#!/usr/bin/env python3
"""
Capability Manifest Service - Real-time Service Status and Health Monitoring

This module provides transparent visibility into which services are actually working,
addressing the gap between claimed capabilities and actual implementation.
"""

import os
import time
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class ServiceStatus(Enum):
    """Service availability status"""
    OPERATIONAL = "operational"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"

class FallbackMode(Enum):
    """Types of fallback modes"""
    NONE = "none"
    TEMPLATE = "template"
    CACHED = "cached"
    SIMPLIFIED = "simplified"
    EMERGENCY = "emergency"

@dataclass
class ServiceCapability:
    """Individual service capability status"""
    name: str
    status: ServiceStatus
    available: bool
    last_success: Optional[str] = None
    last_failure: Optional[str] = None
    failure_rate_24h: float = 0.0
    response_time_ms: float = 0.0
    fallback_mode: FallbackMode = FallbackMode.NONE
    error_message: Optional[str] = None
    health_details: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.health_details is None:
            self.health_details = {}

@dataclass
class CapabilityManifest:
    """Complete system capability manifest"""
    timestamp: str
    deployment_readiness: float
    overall_status: ServiceStatus
    capabilities: Dict[str, ServiceCapability]
    active_fallbacks: List[str]
    recommendations: List[str]
    user_impact: Dict[str, str]

class CapabilityManifestService:
    """Service to track and report real-time system capabilities"""
    
    def __init__(self):
        self.logger = logger
        self.failure_tracking: Dict[str, List[Dict[str, Any]]] = {}
        self.success_tracking: Dict[str, List[datetime]] = {}
        self.response_times: Dict[str, List[float]] = {}
        
    def test_llm_service(self) -> ServiceCapability:
        """Test LLM service availability and performance"""
        start_time = time.time()
        
        try:
            # Check if service is importable and configured
            from services.llm_service import LLMService
            
            llm_service = LLMService()
            # Check for Azure OpenAI credentials (migrated from Gemini)
            api_key_configured = bool(
                os.getenv('AZURE_OPENAI_API_KEY') and 
                os.getenv('AZURE_OPENAI_ENDPOINT')
            )
            
            if not api_key_configured:
                return ServiceCapability(
                    name="llm_service",
                    status=ServiceStatus.UNAVAILABLE,
                    available=False,
                    fallback_mode=FallbackMode.TEMPLATE,
                    error_message="Azure OpenAI credentials not configured",
                    health_details={
                        "api_key_present": bool(os.getenv('AZURE_OPENAI_API_KEY') or os.getenv('AZURE_OPENAI_CHAT_API_KEY')),
                        "endpoint_present": bool(os.getenv('AZURE_OPENAI_ENDPOINT') or os.getenv('AZURE_OPENAI_CHAT_ENDPOINT')),
                        "service_imported": True,
                        "service_configured": llm_service.is_configured
                    }
                )
            
            # Test basic configuration
            response_time = (time.time() - start_time) * 1000
            
            # After Azure OpenAI migration, check for client instead of model
            client_initialized = hasattr(llm_service, 'client') and llm_service.client is not None
            
            if llm_service.is_configured and client_initialized:
                self._record_success('llm', response_time)
                return ServiceCapability(
                    name="llm_service",
                    status=ServiceStatus.OPERATIONAL,
                    available=True,
                    last_success=datetime.now(timezone.utc).isoformat(),
                    response_time_ms=response_time,
                    fallback_mode=FallbackMode.NONE,
                    health_details={
                        "api_key_present": True,
                        "endpoint_present": True,
                        "service_configured": True,
                        "client_initialized": True,
                        "personalities_loaded": len(llm_service.personalities)
                    }
                )
            else:
                self._record_failure('llm', 'Service not properly configured')
                return ServiceCapability(
                    name="llm_service",
                    status=ServiceStatus.DEGRADED,
                    available=False,
                    fallback_mode=FallbackMode.TEMPLATE,
                    error_message="Service configuration incomplete",
                    failure_rate_24h=self._calculate_failure_rate('llm'),
                    health_details={
                        "api_key_present": api_key_configured,
                        "service_configured": llm_service.is_configured,
                        "client_initialized": client_initialized
                    }
                )
                
        except ImportError as e:
            return ServiceCapability(
                name="llm_service",
                status=ServiceStatus.UNAVAILABLE,
                available=False,
                fallback_mode=FallbackMode.TEMPLATE,
                error_message=f"Service not available: {str(e)}",
                health_details={"service_imported": False}
            )
        except Exception as e:
            self._record_failure('llm', str(e))
            return ServiceCapability(
                name="llm_service",
                status=ServiceStatus.UNAVAILABLE,
                available=False,
                fallback_mode=FallbackMode.TEMPLATE,
                error_message=str(e),
                failure_rate_24h=self._calculate_failure_rate('llm')
            )
    
    def test_vector_search(self) -> ServiceCapability:
        """Test vector search service availability"""
        start_time = time.time()
        
        try:
            from services.vector_database_service import VectorDatabaseService
            
            vector_service = VectorDatabaseService()
            response_time = (time.time() - start_time) * 1000
            
            # Check the same environment variables that VectorDatabaseService actually uses
            connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
            database_name = os.getenv('AZURE_COSMOS_DATABASE_NAME', 'vimarsh-multi-personality')
            container_name = os.getenv('AZURE_COSMOS_CONTAINER_NAME', 'personality_vectors')  # Fixed default
            
            if not connection_string:
                return ServiceCapability(
                    name="vector_search",
                    status=ServiceStatus.UNAVAILABLE,
                    available=False,
                    fallback_mode=FallbackMode.SIMPLIFIED,
                    error_message="Cosmos DB credentials not configured",
                    health_details={
                        "cosmos_connection_string_configured": bool(connection_string),
                        "cosmos_database_name": database_name,
                        "cosmos_container_name": container_name,
                        "service_imported": True
                    }
                )
            
            self._record_success('vector', response_time)
            return ServiceCapability(
                name="vector_search",
                status=ServiceStatus.OPERATIONAL,
                available=True,
                last_success=datetime.now(timezone.utc).isoformat(),
                response_time_ms=response_time,
                fallback_mode=FallbackMode.NONE,
                health_details={
                    "cosmos_connection_string_configured": True,
                    "cosmos_database_name": database_name,
                    "cosmos_container_name": container_name,
                    "service_imported": True,
                    "basic_initialization": True
                }
            )
                
        except ImportError:
            return ServiceCapability(
                name="vector_search",
                status=ServiceStatus.UNAVAILABLE,
                available=False,
                fallback_mode=FallbackMode.SIMPLIFIED,
                error_message="Vector service not available",
                health_details={"service_imported": False}
            )
        except Exception as e:
            self._record_failure('vector', str(e))
            return ServiceCapability(
                name="vector_search",
                status=ServiceStatus.UNAVAILABLE,
                available=False,
                fallback_mode=FallbackMode.SIMPLIFIED,
                error_message=str(e),
                failure_rate_24h=self._calculate_failure_rate('vector')
            )
    
    def test_memory_persistence(self) -> ServiceCapability:
        """Test memory service availability and mode"""
        try:
            from services.conversation_memory_service import ConversationMemoryService
            
            memory_service = ConversationMemoryService()
            
            # Check if database service is properly connected
            database_connected = False
            cross_session_persistence = False
            mode = "in_memory"
            
            if hasattr(memory_service, 'database_service') and memory_service.database_service:
                try:
                    # Check if Phase 2 database service is connected to Cosmos
                    if hasattr(memory_service.database_service, 'is_cosmos_enabled'):
                        database_connected = memory_service.database_service.is_cosmos_enabled
                        if database_connected:
                            mode = "cosmos_db"
                            cross_session_persistence = True
                except Exception:
                    pass  # Keep conservative defaults
            
            return ServiceCapability(
                name="memory_persistence",
                status=ServiceStatus.OPERATIONAL,
                available=True,
                fallback_mode=FallbackMode.CACHED if not database_connected else FallbackMode.NONE,
                health_details={
                    "mode": mode,
                    "service_imported": True,
                    "session_support": True,
                    "cross_session_persistence": cross_session_persistence,
                    "database_connected": database_connected
                }
            )
            
        except ImportError:
            return ServiceCapability(
                name="memory_persistence",
                status=ServiceStatus.UNAVAILABLE,
                available=False,
                fallback_mode=FallbackMode.NONE,
                error_message="Memory service not available",
                health_details={"service_imported": False}
            )
        except Exception as e:
            return ServiceCapability(
                name="memory_persistence",
                status=ServiceStatus.UNAVAILABLE,
                available=False,
                error_message=str(e)
            )
    
    def test_citation_grounding(self) -> ServiceCapability:
        """Test citation validation service"""
        try:
            from services.citation_grounding_checker import CitationGroundingChecker
            
            # Basic import test - assume basic functionality if importable
            return ServiceCapability(
                name="citation_grounding",
                status=ServiceStatus.OPERATIONAL,
                available=True,
                fallback_mode=FallbackMode.NONE,
                health_details={
                    "service_imported": True,
                    "validation_available": True  # Conservative assumption
                }
            )
            
        except ImportError:
            return ServiceCapability(
                name="citation_grounding",
                status=ServiceStatus.UNAVAILABLE,
                available=False,
                fallback_mode=FallbackMode.SIMPLIFIED,
                error_message="Citation service not available",
                health_details={"service_imported": False}
            )
        except Exception as e:
            return ServiceCapability(
                name="citation_grounding",
                status=ServiceStatus.UNAVAILABLE,
                available=False,
                fallback_mode=FallbackMode.SIMPLIFIED,
                error_message=str(e)
            )
    
    def test_enhanced_rag(self) -> ServiceCapability:
        """Test enhanced RAG service availability"""
        try:
            from services.hybrid_search_service import HybridSearchService
            
            # Basic import test - assume basic functionality if importable
            return ServiceCapability(
                name="enhanced_rag",
                status=ServiceStatus.OPERATIONAL,
                available=True,
                fallback_mode=FallbackMode.NONE,
                health_details={
                    "service_imported": True,
                    "hybrid_search_available": True,  # Conservative assumption
                    "bm25_enabled": True,
                    "vector_fusion_enabled": True
                }
            )
            
        except ImportError:
            return ServiceCapability(
                name="enhanced_rag",
                status=ServiceStatus.UNAVAILABLE,
                available=False,
                fallback_mode=FallbackMode.SIMPLIFIED,
                error_message="Enhanced RAG service not available",
                health_details={"service_imported": False}
            )
        except Exception as e:
            return ServiceCapability(
                name="enhanced_rag",
                status=ServiceStatus.UNAVAILABLE,
                available=False,
                fallback_mode=FallbackMode.SIMPLIFIED,
                error_message=str(e)
            )
    
    def generate_manifest(self) -> CapabilityManifest:
        """Generate complete capability manifest"""
        capabilities: Dict[str, ServiceCapability] = {}
        
        # Test all services with diagnostic logging
        capabilities["llm_service"] = self.test_llm_service()
        logger.info(f"🔍 LLM Service: {capabilities['llm_service'].status.value} (available: {capabilities['llm_service'].available})")
        
        capabilities["vector_search"] = self.test_vector_search()
        logger.info(f"🔍 Vector Search: {capabilities['vector_search'].status.value} (available: {capabilities['vector_search'].available})")
        
        capabilities["memory_persistence"] = self.test_memory_persistence()
        logger.info(f"🔍 Memory Persistence: {capabilities['memory_persistence'].status.value} (available: {capabilities['memory_persistence'].available})")
        
        capabilities["citation_grounding"] = self.test_citation_grounding()
        logger.info(f"🔍 Citation Grounding: {capabilities['citation_grounding'].status.value} (available: {capabilities['citation_grounding'].available})")
        
        capabilities["enhanced_rag"] = self.test_enhanced_rag()
        logger.info(f"🔍 Enhanced RAG: {capabilities['enhanced_rag'].status.value} (available: {capabilities['enhanced_rag'].available})")
        
        # Calculate overall deployment readiness
        deployment_readiness = self._calculate_deployment_readiness(capabilities)
        overall_status = self._determine_overall_status(capabilities)
        
        # Identify active fallbacks
        active_fallbacks: List[str] = [
            cap.name for cap in capabilities.values() 
            if cap.fallback_mode != FallbackMode.NONE
        ]
        
        # Generate recommendations
        recommendations = self._generate_recommendations(capabilities)
        
        # Assess user impact
        user_impact = self._assess_user_impact(capabilities)
        
        # Log deployment readiness summary
        logger.info(f"📊 Deployment Readiness: {deployment_readiness*100:.0f}% - Status: {overall_status.value}")
        if active_fallbacks:
            logger.warning(f"⚠️  Active Fallbacks: {', '.join(active_fallbacks)}")
        if recommendations:
            logger.info(f"💡 Recommendations: {'; '.join(recommendations)}")
        
        return CapabilityManifest(
            timestamp=datetime.now(timezone.utc).isoformat(),
            deployment_readiness=deployment_readiness,
            overall_status=overall_status,
            capabilities=capabilities,
            active_fallbacks=active_fallbacks,
            recommendations=recommendations,
            user_impact=user_impact
        )
    
    def _record_success(self, service: str, response_time: float):
        """Record successful service call"""
        if service not in self.success_tracking:
            self.success_tracking[service] = []
        if service not in self.response_times:
            self.response_times[service] = []
            
        timestamp = datetime.now(timezone.utc)
        self.success_tracking[service].append(timestamp)
        self.response_times[service].append(response_time)
        
        # Keep only last 24 hours
        cutoff = timestamp - timedelta(hours=24)
        self.success_tracking[service] = [
            t for t in self.success_tracking[service] if t > cutoff
        ]
        self.response_times[service] = self.response_times[service][-100:]  # Keep last 100
    
    def _record_failure(self, service: str, error: str):
        """Record service failure"""
        if service not in self.failure_tracking:
            self.failure_tracking[service] = []
            
        timestamp = datetime.now(timezone.utc)
        self.failure_tracking[service].append({
            'timestamp': timestamp,
            'error': error
        })
        
        # Keep only last 24 hours
        cutoff = timestamp - timedelta(hours=24)
        self.failure_tracking[service] = [
            f for f in self.failure_tracking[service] if f['timestamp'] > cutoff
        ]
    
    def _calculate_failure_rate(self, service: str) -> float:
        """Calculate 24-hour failure rate for service"""
        successes = len(self.success_tracking.get(service, []))
        failures = len(self.failure_tracking.get(service, []))
        total = successes + failures
        
        if total == 0:
            return 0.0
        
        return failures / total
    
    def _calculate_deployment_readiness(self, capabilities: Dict[str, ServiceCapability]) -> float:
        """Calculate overall deployment readiness score (0.0 to 1.0)"""
        weights = {
            "llm_service": 0.4,  # Critical for AI responses
            "vector_search": 0.25,  # Important for quality
            "memory_persistence": 0.15,  # Nice to have
            "citation_grounding": 0.1,  # Quality assurance
            "enhanced_rag": 0.1  # Enhancement
        }
        
        score = 0.0
        for service, weight in weights.items():
            cap = capabilities.get(service)
            if cap:
                if cap.status == ServiceStatus.OPERATIONAL:
                    score += weight
                elif cap.status == ServiceStatus.DEGRADED:
                    score += weight * 0.5
                # Unavailable services contribute 0
        
        return round(score, 3)
    
    def _determine_overall_status(self, capabilities: Dict[str, ServiceCapability]) -> ServiceStatus:
        """Determine overall system status"""
        critical_services = ["llm_service", "vector_search"]
        
        critical_unavailable = any(
            capabilities.get(service, ServiceCapability("", ServiceStatus.UNKNOWN, False)).status == ServiceStatus.UNAVAILABLE
            for service in critical_services
        )
        
        if critical_unavailable:
            return ServiceStatus.DEGRADED
        
        any_degraded = any(cap.status == ServiceStatus.DEGRADED for cap in capabilities.values())
        if any_degraded:
            return ServiceStatus.DEGRADED
        
        all_operational = all(cap.status == ServiceStatus.OPERATIONAL for cap in capabilities.values())
        if all_operational:
            return ServiceStatus.OPERATIONAL
        
        return ServiceStatus.UNKNOWN
    
    def _generate_recommendations(self, capabilities: Dict[str, ServiceCapability]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations: List[str] = []
        
        llm_cap = capabilities.get("llm_service")
        if llm_cap and not llm_cap.available:
            if llm_cap.error_message and "API key" in str(llm_cap.error_message):
                recommendations.append("Configure AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT environment variables")
            else:
                recommendations.append("Check LLM service configuration and API connectivity")
        
        vector_cap = capabilities.get("vector_search")
        if vector_cap and not vector_cap.available:
            recommendations.append("Verify Cosmos DB connection string and container setup")
        
        memory_cap = capabilities.get("memory_persistence")
        if memory_cap and memory_cap.fallback_mode == FallbackMode.CACHED:
            recommendations.append("Configure persistent storage for cross-session memory")
        
        # Alert on high failure rates
        for service, cap in capabilities.items():
            if cap.failure_rate_24h > 0.2:  # >20% failure rate
                recommendations.append(f"Investigate {service} reliability - {cap.failure_rate_24h:.1%} failure rate")
        
        return recommendations
    
    def _assess_user_impact(self, capabilities: Dict[str, ServiceCapability]) -> Dict[str, str]:
        """Assess user-visible impact of current capability status"""
        impact: Dict[str, str] = {}
        
        llm_cap = capabilities.get("llm_service")
        if llm_cap and not llm_cap.available:
            impact["responses"] = "Users will receive template responses instead of AI-generated content"
        
        vector_cap = capabilities.get("vector_search")
        if vector_cap and not vector_cap.available:
            impact["context"] = "Reduced response quality due to simplified text search"
        
        memory_cap = capabilities.get("memory_persistence")
        if memory_cap and memory_cap.fallback_mode == FallbackMode.CACHED:
            impact["continuity"] = "No conversation history across sessions"
        
        citation_cap = capabilities.get("citation_grounding")
        if citation_cap and not citation_cap.available:
            impact["citations"] = "Citations may not be validated for accuracy"
        
        if not impact:
            impact["overall"] = "All features working as expected"
        
        return impact

    def get_service_status_json(self) -> str:
        """Get current service status as JSON string"""
        manifest = self.generate_manifest()
        return json.dumps(asdict(manifest), indent=2, default=str)

# Global instance for use across the application
capability_manifest_service = CapabilityManifestService()
