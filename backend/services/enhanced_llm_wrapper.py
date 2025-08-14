#!/usr/bin/env python3
"""
Enhanced LLM Service with Reliability Patterns

This module wraps the existing LLM service with circuit breaker, retry logic,
and comprehensive fallback tracking to reduce template usage and improve reliability.
"""

import os
import time
import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from core.service_reliability import (
    circuit_breaker, 
    fallback_tracker, 
    recovery_manager,
    ExponentialBackoffRetry
)

logger = logging.getLogger(__name__)

class EnhancedLLMService:
    """Enhanced LLM service with reliability patterns"""
    
    def __init__(self):
        self.logger = logger
        self.retry_policy = ExponentialBackoffRetry(max_attempts=3)
        self.base_service = None
        
        # Initialize database personality service
        self.database_personality_service = None
        self.database_available = False
        self._initialize_database_service()
        
        self._initialize_base_service()
        
        # Template responses for fallback (will be updated from database if available)
        self.fallback_templates = self._get_fallback_templates()
    
    def _initialize_database_service(self):
        """Initialize database personality service"""
        try:
            from services.database_personality_service import DatabasePersonalityService
            self.database_personality_service = DatabasePersonalityService()
            self.database_available = True
            self.logger.info("✅ Database personality service initialized in Enhanced LLM wrapper")
        except ImportError as e:
            self.logger.warning(f"⚠️ Database personality service not available in Enhanced LLM wrapper: {e}")
        except Exception as e:
            self.logger.warning(f"⚠️ Database personality service initialization failed in Enhanced LLM wrapper: {e}")
    
    def _get_fallback_templates(self) -> Dict[str, str]:
        """Get fallback templates from database or use hardcoded ones"""
        if self.database_available and self.database_personality_service:
            try:
                # Try to get templates from database
                import asyncio
                loop = asyncio.new_event_loop()
                try:
                    asyncio.set_event_loop(loop)
                    database_personalities = loop.run_until_complete(
                        self.database_personality_service.get_all_personalities()
                    )
                finally:
                    loop.close()
                
                if database_personalities:
                    templates = {}
                    for personality in database_personalities:
                        if isinstance(personality, dict) and 'id' in personality:
                            # Try to get default response from personality config
                            response_templates = personality.get('response_templates', {})
                            default_response = response_templates.get('default_response', '')
                            
                            if default_response:
                                templates[personality['id']] = default_response
                            else:
                                # Use description as fallback template
                                description = personality.get('description', 'I am here to provide guidance.')
                                templates[personality['id']] = f"{description[:200]}..."
                    
                    if templates:
                        self.logger.info(f"✅ Loaded {len(templates)} fallback templates from database")
                        return templates
                        
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to load fallback templates from database: {e}")
        
        # Use hardcoded fallback templates
        self.logger.info("📋 Using hardcoded fallback templates")
        return {
            "krishna": "Beloved devotee, in the Bhagavad Gita 2.47, I teach: \"You have the right to perform your prescribed duty, but not to the fruits of action.\" Focus on righteous action with love and dedication. 🙏",
            "buddha": "Dear friend, suffering arises from attachment. Practice mindfulness and compassion. The Middle Way leads to peace and liberation from all forms of suffering.",
            "jesus": "Beloved child, love is the greatest commandment. \"Love your neighbor as yourself\" (Matthew 22:39). Let God's love guide your heart and actions.",
            "rumi": "Beloved, you are not just a drop in the ocean, but the entire ocean in each drop. Let love be your bridge to the divine mystery within.",
            "einstein": "The important thing is not to stop questioning. Curiosity has its own reason for existing. Wonder at the mysteries of the universe.",
            "lincoln": "A house divided against itself cannot stand. Let us choose unity over division, and work together for the common good of all.",
            "marcus_aurelius": "You have power over your mind - not outside events. Realize this, and you will find strength. Focus on what you can control.",
            "confucius": "The man who moves a mountain begins by carrying away small stones. Cultivate virtue through small, consistent actions."
        }
    
    def _initialize_base_service(self):
        """Initialize the base LLM service with error handling"""
        try:
            from services.llm_service import LLMService
            self.base_service = LLMService()
            
            if self.base_service.is_configured:
                self.logger.info("✅ Enhanced LLM service initialized with base service")
            else:
                self.logger.warning("⚠️ Base LLM service not configured, will use templates")
                
        except ImportError as e:
            self.logger.error(f"❌ Failed to import base LLM service: {e}")
            self.base_service = None
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize base LLM service: {e}")
            self.base_service = None
    
    async def generate_response_with_monitoring(self, query: str, personality_id: str, language: str = "English") -> Dict[str, Any]:
        """Generate response with comprehensive monitoring and fallback"""
        start_time = time.time()
        
        try:
            # Circuit breaker check
            if circuit_breaker.is_open():
                fallback_tracker.record_fallback('circuit_breaker_open')
                return self._get_template_response(personality_id, "Circuit breaker is open")
            
            # Check if base service is available
            if not self.base_service or not self.base_service.is_configured:
                fallback_tracker.record_fallback('base_service_unavailable')
                return self._get_template_response(personality_id, "Base service not configured")
            
            # Attempt to get AI response with retry
            try:
                ai_response = await self.retry_policy.execute(
                    lambda: self._call_base_service(query, personality_id, language)
                )
                
                # Record success
                response_time = time.time() - start_time
                circuit_breaker.record_success()
                fallback_tracker.record_success()
                fallback_tracker.record_response_time(response_time * 1000)  # Convert to ms
                
                # Enhance response with metadata
                if isinstance(ai_response, dict):
                    ai_response["metadata"]["response_source"] = "gemini_ai"
                    ai_response["metadata"]["generation_time_ms"] = response_time * 1000
                    ai_response["metadata"]["circuit_breaker_status"] = circuit_breaker.get_status()
                    ai_response["metadata"]["reliability_stats"] = fallback_tracker.get_stats()
                    
                    return ai_response
                else:
                    # Handle unexpected response format
                    fallback_tracker.record_fallback("unexpected_response_format")
                    return self._get_template_response(personality_id, "Unexpected response format")
                
            except Exception as e:
                circuit_breaker.record_failure()
                fallback_tracker.record_fallback(str(e))
                
                self.logger.warning(f"🔄 LLM failed after retries, using template for {personality_id}: {e}")
                return self._get_template_response(personality_id, str(e))
                
        except Exception as e:
            self.logger.error(f"❌ Critical error in enhanced LLM service: {e}")
            fallback_tracker.record_fallback(f"critical_error: {e}")
            return self._get_template_response(personality_id, f"Critical error: {e}")
    
    async def _call_base_service(self, query: str, personality_id: str, language: str) -> Dict[str, Any]:
        """Call the base LLM service with timeout"""
        try:
            # Call base service async method
            response = await self.base_service.generate_personality_response(
                query=query,
                context="guidance",
                personality_id=personality_id
            )
            
            # Convert response to expected format
            return {
                "content": response.content,
                "metadata": {
                    "source": response.source,
                    "character_count": response.character_count,
                    "personality_id": response.personality_id,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
            
        except asyncio.TimeoutError:
            raise Exception("LLM service timeout")
        except Exception as e:
            raise Exception(f"LLM service error: {e}")
    
    def _get_template_response(self, personality_id: str, fallback_reason: str) -> Dict[str, Any]:
        """Get template response with metadata"""
        template = self.fallback_templates.get(
            personality_id, 
            self.fallback_templates.get("krishna", "I apologize, but I'm unable to provide guidance at this moment. Please try again.")
        )
        
        return {
            "content": template,
            "metadata": {
                "source": "template_fallback",
                "response_source": "template_fallback",
                "fallback_reason": fallback_reason,
                "personality_id": personality_id,
                "character_count": len(template),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "generation_time_ms": 50,  # Templates are fast
                "circuit_breaker_status": circuit_breaker.get_status(),
                "reliability_stats": fallback_tracker.get_stats()
            }
        }
    
    def get_available_personalities(self) -> list:
        """Get available personalities"""
        if self.base_service:
            try:
                return self.base_service.get_available_personalities()
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to get personalities from base service: {e}")
        
        # Fallback personality list
        return [
            {"id": "krishna", "name": "Krishna", "domain": "spiritual"},
            {"id": "buddha", "name": "Buddha", "domain": "spiritual"},
            {"id": "jesus", "name": "Jesus Christ", "domain": "spiritual"},
            {"id": "rumi", "name": "Rumi", "domain": "spiritual"},
            {"id": "einstein", "name": "Albert Einstein", "domain": "scientific"},
            {"id": "lincoln", "name": "Abraham Lincoln", "domain": "historical"},
            {"id": "marcus_aurelius", "name": "Marcus Aurelius", "domain": "philosophical"},
            {"id": "confucius", "name": "Confucius", "domain": "philosophical"}
        ]
    
    async def attempt_service_recovery(self) -> bool:
        """Attempt to recover the LLM service"""
        try:
            # Reinitialize the base service
            self._initialize_base_service()
            
            if self.base_service and self.base_service.is_configured:
                # Test with a simple query
                test_response = await self._call_base_service(
                    "Test query", "krishna", "English"
                )
                
                if test_response and test_response.get("content"):
                    self.logger.info("✅ LLM service recovery successful")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ LLM service recovery failed: {e}")
            return False
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get comprehensive service status"""
        base_service_status = {
            "available": self.base_service is not None,
            "configured": self.base_service.is_configured if self.base_service else False,
            "api_key_present": bool(os.getenv('GEMINI_API_KEY'))
        }
        
        return {
            "enhanced_service": True,
            "base_service": base_service_status,
            "circuit_breaker": circuit_breaker.get_status(),
            "reliability_stats": fallback_tracker.get_stats(),
            "recovery_status": recovery_manager.get_recovery_status("llm_service"),
            "fallback_templates_loaded": len(self.fallback_templates),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def start_recovery_monitor(self):
        """Start background recovery monitoring"""
        try:
            if recovery_manager.should_attempt_recovery("llm_service"):
                recovery_success = await recovery_manager.attempt_recovery(
                    "llm_service", 
                    self.attempt_service_recovery
                )
                
                if recovery_success:
                    self.logger.info("✅ LLM service automatically recovered")
                else:
                    self.logger.info("⚠️ LLM service recovery attempt failed")
                    
        except Exception as e:
            self.logger.error(f"❌ Recovery monitor error: {e}")

# Global enhanced service instance
enhanced_llm_service = EnhancedLLMService()
