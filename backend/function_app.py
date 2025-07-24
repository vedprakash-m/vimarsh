"""
Main Azure Functions application entry point for Vimarsh spiritual guidance API.

This module implements the core Azure Functions HTTP triggers for the spiritual
guidance system, providing endpoints for user queries and spiritual guidance
through Lord Krishna's persona with authentic Sanskrit terminology support.

Features:
- Sanskrit pronunciation optimization in voice responses
- Sanskrit verse citations with proper transliteration
- Multi-language support (English, Hindi) with Sanskrit terms
"""

import azure.functions as func
import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
import asyncio

# Import unified configuration system
try:
    from config.unified_config import get_config, is_development_mode, is_production_mode
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

# Import centralized logging and health checks
try:
    from backend.core.logging import get_logger, LogContext, PerformanceMetrics
    from backend.core.health import get_health_checker
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup structured logging if available
if MONITORING_AVAILABLE:
    structured_logger = get_logger("vimarsh.api")
    health_checker = get_health_checker()
else:
    structured_logger = None
    health_checker = None

# Import personality management endpoints
try:
    from admin.personality_endpoints import (
        create_personality, get_personality, update_personality, delete_personality,
        search_personalities, get_personalities_by_domain, validate_personality,
        associate_knowledge_base, discover_personalities, get_active_personalities
    )
    PERSONALITY_ENDPOINTS_AVAILABLE = True
except ImportError:
    PERSONALITY_ENDPOINTS_AVAILABLE = False

# Import content management endpoints
try:
    from admin.content_endpoints import (
        get_content, create_content, update_content, delete_content,
        associate_content_personalities, validate_content_quality,
        approve_content, reject_content
    )
    CONTENT_ENDPOINTS_AVAILABLE = True
except ImportError:
    CONTENT_ENDPOINTS_AVAILABLE = False

# Import expert review endpoints
try:
    from admin.expert_review_endpoints import (
        get_review_items, get_experts, get_review_queues,
        assign_review, submit_feedback, get_review_analytics,
        submit_for_review
    )
    EXPERT_REVIEW_ENDPOINTS_AVAILABLE = True
except ImportError:
    EXPERT_REVIEW_ENDPOINTS_AVAILABLE = False

# Import performance monitoring endpoints
try:
    from admin.performance_endpoints import (
        get_cache_metrics, get_performance_metrics, get_performance_report,
        get_performance_alerts, resolve_alert, get_optimization_recommendations,
        warm_cache, invalidate_cache, optimize_cache
    )
    PERFORMANCE_ENDPOINTS_AVAILABLE = True
except ImportError:
    PERFORMANCE_ENDPOINTS_AVAILABLE = False

# Import authentication middleware
try:
    from auth.unified_auth_service import auth_service, require_auth, require_admin, AuthenticatedUser
    from auth.models import AuthenticatedUser
    AUTHENTICATION_ENABLED = True
    logger.info("✅ Unified authentication service loaded successfully")
except ImportError as e:
    AUTHENTICATION_ENABLED = False
    logger.warning(f"⚠️ Authentication modules not available, running without auth: {e}")

# Initialize Azure Functions app
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


async def health_check_impl(req: func.HttpRequest) -> func.HttpResponse:
    """
    Health check endpoint for monitoring service availability.
    
    Returns:
        HTTP 200: Service is healthy
        HTTP 500: Service has issues
    """
    try:
        # Use comprehensive health checker if available
        if MONITORING_AVAILABLE and health_checker:
            health_summary = health_checker.perform_full_health_check()
            
            # Determine HTTP status based on health
            if health_summary.overall_status.value in ["healthy", "degraded"]:
                status_code = 200
            else:
                status_code = 500
            
            return func.HttpResponse(
                json.dumps(health_summary.to_dict()),
                mimetype="application/json",
                status_code=status_code
            )
        else:
            # Fallback to simple health check
            config = get_config() if CONFIG_AVAILABLE else None
            environment = config.environment.value if config else "unknown"
            
            health_status = {
                "status": "healthy",
                "service": "vimarsh-spiritual-guidance",
                "version": "1.0.0",
                "timestamp": datetime.utcnow().isoformat(),
                "environment": environment,
                "monitoring": "basic"
            }
            
            return func.HttpResponse(
                json.dumps(health_status),
                mimetype="application/json",
                status_code=200
            )
    
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        
        error_response = {
            "status": "critical",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return func.HttpResponse(
            json.dumps(error_response),
            mimetype="application/json",
            status_code=500
        )
        
        logger.info("Health check successful")
        return func.HttpResponse(
            json.dumps(health_status),
            mimetype="application/json",
            status_code=200
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "status": "unhealthy", 
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }),
            mimetype="application/json",
            status_code=500
        )


@app.route(route="health", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
async def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """Azure Functions wrapper for health check."""
    return await health_check_impl(req)


@app.route(route="health/quick", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
async def quick_health_check(req: func.HttpRequest) -> func.HttpResponse:
    """Quick health check for load balancers."""
    try:
        if MONITORING_AVAILABLE and health_checker:
            status = health_checker.get_quick_health_status()
        else:
            status = {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "uptime": True
            }
        
        return func.HttpResponse(
            json.dumps(status),
            mimetype="application/json",
            status_code=200
        )
    
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"status": "error", "message": str(e)}),
            mimetype="application/json",
            status_code=500
        )


@app.route(route="health/detailed", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
async def detailed_health_check(req: func.HttpRequest) -> func.HttpResponse:
    """Detailed health check with full component analysis."""
    try:
        if MONITORING_AVAILABLE and health_checker:
            # Force fresh health check
            health_summary = health_checker.perform_full_health_check(use_cache=False)
            
            status_code = 200 if health_summary.overall_status.value in ["healthy", "degraded"] else 500
            
            return func.HttpResponse(
                json.dumps(health_summary.to_dict()),
                mimetype="application/json",
                status_code=status_code
            )
        else:
            return func.HttpResponse(
                json.dumps({"error": "Detailed health monitoring not available"}),
                mimetype="application/json",
                status_code=503
            )
    
    except Exception as e:
        logger.error(f"Detailed health check failed: {str(e)}")
        return func.HttpResponse(
            json.dumps({"status": "critical", "error": str(e)}),
            mimetype="application/json",
            status_code=500
        )


async def spiritual_guidance_impl(req: func.HttpRequest) -> func.HttpResponse:
    """
    Main spiritual guidance endpoint providing Lord Krishna's wisdom.
    
    Accepts user queries and returns spiritually grounded responses based on
    sacred texts using RAG pipeline and Gemini Pro API with budget controls.
    
    Authentication: Optional - Can be enabled by setting ENABLE_AUTH environment variable
    
    Request Body:
        {
            "query": "User's spiritual question",
            "language": "English" | "Hindi" (optional, default: "English"),
            "include_citations": boolean (optional, default: true),
            "voice_enabled": boolean (optional, default: false),
            "personality_id": "krishna" | "einstein" | "lincoln" | "marcus_aurelius" (optional, default: "krishna")
        }
    
    Returns:
        {
            "response": "Lord Krishna's guidance",
            "citations": [...],
            "metadata": {...},
            "audio_url": "..." (if voice_enabled=true)
        }
    """
    try:
        # Optional authentication check with admin role detection
        user_context = None
        user_id = None
        user_email = None
        session_id = None
        
        if AUTHENTICATION_ENABLED and os.getenv("ENABLE_AUTH", "false").lower() == "true":
            try:
                # Extract user from JWT token
                auth_header = req.headers.get('Authorization', '')
                if auth_header.startswith('Bearer '):
                    token = auth_header[7:]
                    # Use auth middleware to extract user
                    user = auth_middleware.extract_user_from_request(req)
                    if user:
                        user_context = {"authenticated": True, "role": str(user.role)}
                        user_id = user.id
                        user_email = user.email
                        session_id = req.headers.get('x-session-id', f"session_{user.id}")
                        logger.info(f"🔐 Authenticated request from {user.email} (Role: {user.role})")
                    else:
                        logger.warning("Invalid authentication token")
                else:
                    logger.warning("Missing authentication token")
            except Exception as auth_error:
                logger.warning(f"Authentication failed: {auth_error}")
                # Continue without auth for graceful degradation
        
        # Generate placeholder user context for development
        if not user_context:
            user_id = req.headers.get('x-user-id', 'dev_user_1')
            user_email = req.headers.get('x-user-email', 'dev@example.com')
            session_id = req.headers.get('x-session-id', f"session_{user_id}")
            user_context = {"authenticated": False, "role": "user"}
        
        # Parse and validate request
        if not req.get_body():
            raise ValueError("Request body is required")
            
        query_data = req.get_json()
        if not query_data:
            raise ValueError("Invalid JSON in request body")
        
        # Extract request parameters
        user_query = query_data.get('query', '').strip()
        language = query_data.get('language', 'English')
        include_citations = query_data.get('include_citations', True)
        voice_enabled = query_data.get('voice_enabled', False)
        conversation_context = query_data.get('conversation_context', [])
        personality_id = query_data.get('personality_id', 'krishna')  # Default to Krishna for backward compatibility
        
        # Validate required parameters
        if not user_query:
            raise ValueError("Query parameter is required and cannot be empty")
        
        if language not in ['English', 'Hindi']:
            raise ValueError("Language must be 'English' or 'Hindi'")
        
        logger.info(f"Processing spiritual guidance request from {user_email}: {user_query[:100]}...")
        
        # Generate response with budget-aware LLM service
        response_data = await _generate_spiritual_response_with_budget(
            user_query, language, include_citations, voice_enabled, conversation_context,
            user_id, user_email, session_id, personality_id
        )
        
        # Add authentication metadata if available
        if user_context:
            response_data["metadata"]["authenticated"] = user_context["authenticated"]
            response_data["metadata"]["user_role"] = user_context["role"]
            response_data["metadata"]["user_id"] = user_id
        
        logger.info("Spiritual guidance response generated successfully")
        return func.HttpResponse(
            json.dumps(response_data, ensure_ascii=False),
            mimetype="application/json",
            status_code=200,
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Access-Control-Allow-Origin": "https://vimarsh.vedprakash.net",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization, x-user-id, x-user-email, x-session-id",
                "Access-Control-Allow-Credentials": "true"
            }
        )
        
    except ValueError as e:
        logger.warning(f"Invalid request: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "error": "Invalid request",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }),
            mimetype="application/json",
            status_code=400
        )
        
    except Exception as e:
        logger.error(f"Spiritual guidance processing failed: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "error": "Internal server error",
                "message": "Unable to process spiritual guidance request",
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": req.headers.get('x-request-id', 'unknown')
            }),
            mimetype="application/json",
            status_code=500
        )


@app.route(route="spiritual_guidance", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
async def spiritual_guidance(req: func.HttpRequest) -> func.HttpResponse:
    """Azure Functions wrapper for spiritual guidance."""
    return await spiritual_guidance_impl(req)


async def supported_languages_impl(req: func.HttpRequest) -> func.HttpResponse:
    """
    Returns list of supported languages for spiritual guidance.
    
    Returns:
        {
            "languages": [
                {"code": "English", "name": "English", "native_name": "English"},
                {"code": "Hindi", "name": "Hindi", "native_name": "हिन्दी"}
            ]
        }
    """
    try:
        languages_data = {
            "languages": [
                {
                    "code": "English",
                    "name": "English", 
                    "native_name": "English",
                    "supported_features": ["text", "voice", "citations"]
                },
                {
                    "code": "Hindi",
                    "name": "Hindi",
                    "native_name": "हिन्दी", 
                    "supported_features": ["text", "voice", "citations"]
                }
            ],
            "default_language": "English"
        }
        
        return func.HttpResponse(
            json.dumps(languages_data, ensure_ascii=False),
            mimetype="application/json",
            status_code=200,
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Access-Control-Allow-Origin": "*"
            }
        )
        
    except Exception as e:
        logger.error(f"Languages endpoint failed: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )


@app.route(route="languages", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
async def supported_languages(req: func.HttpRequest) -> func.HttpResponse:
    """Azure Functions wrapper for supported languages."""
    return await supported_languages_impl(req)


async def get_active_personalities_impl(req: func.HttpRequest) -> func.HttpResponse:
    """
    Get active personalities for user selection.
    
    Query Parameters:
        - domain: Filter by domain (spiritual, scientific, historical, philosophical)
        - q: Search query
        - active_only: Only return active personalities (default: true)
    
    Returns:
        {
            "personalities": [
                {
                    "id": "krishna",
                    "name": "Krishna",
                    "display_name": "Lord Krishna",
                    "domain": "spiritual",
                    "description": "Divine teacher and guide...",
                    "expertise_areas": ["dharma", "karma", ...],
                    "quality_score": 95.0,
                    "usage_count": 1000,
                    "is_active": true
                }
            ]
        }
    """
    try:
        # Parse query parameters
        domain = req.params.get('domain')
        search_query = req.params.get('q')
        active_only = req.params.get('active_only', 'true').lower() == 'true'
        
        # Import personality service
        from services.personality_service import personality_service, PersonalitySearchFilter
        
        # Create search filter
        filters = PersonalitySearchFilter(
            domain=None if not domain or domain == 'all' else personality_service.PersonalityDomain(domain),
            is_active=active_only,
            search_query=search_query
        )
        
        # Search personalities
        personalities = await personality_service.search_personalities(filters, limit=50)
        
        # Convert to API format
        personality_data = []
        for personality in personalities:
            personality_data.append({
                "id": personality.id,
                "name": personality.name,
                "display_name": personality.display_name,
                "domain": personality.domain.value,
                "time_period": personality.time_period,
                "description": personality.description,
                "expertise_areas": personality.expertise_areas,
                "cultural_context": personality.cultural_context,
                "quality_score": personality.quality_score,
                "usage_count": personality.usage_count,
                "is_active": personality.is_active,
                "tags": personality.tags
            })
        
        return func.HttpResponse(
            json.dumps({
                "personalities": personality_data,
                "total": len(personality_data)
            }),
            mimetype="application/json",
            status_code=200,
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to get active personalities: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "error": "Failed to load personalities",
                "message": str(e),
                "personalities": []
            }),
            mimetype="application/json",
            status_code=500
        )


@app.route(route="personalities/active", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
async def get_active_personalities(req: func.HttpRequest) -> func.HttpResponse:
    """Azure Functions wrapper for getting active personalities."""
    return await get_active_personalities_impl(req)


async def _generate_spiritual_response_with_budget(
    query: str, 
    language: str, 
    include_citations: bool,
    voice_enabled: bool,
    conversation_context: List[Dict[str, str]] = None,
    user_id: str = None,
    user_email: str = None,
    session_id: str = None,
    personality_id: str = "krishna"
) -> Dict[str, Any]:
    """
    Generate spiritual guidance response using budget-aware LLM service.
    
    Args:
        query: User's spiritual question
        language: Response language (English/Hindi)
        include_citations: Whether to include source citations
        voice_enabled: Whether to generate audio response
        conversation_context: Previous conversation context
        user_id: User ID for budget tracking
        user_email: User email for budget tracking
        session_id: Session ID for usage tracking
        personality_id: ID of the personality to use for response generation
    
    Returns:
        Structured response with guidance, citations, and metadata
    """
    try:
        # Use budget-aware LLM service
        from services.llm_service import llm_service
        from services.llm_service import SpiritualContext
        
        # Get spiritual guidance with personality support
        spiritual_response = await llm_service.get_spiritual_guidance(
            query=query,
            context="guidance",
            conversation_context=conversation_context,
            personality_id=personality_id
        )
        
        # Structure the response
        response_data = {
            "response": spiritual_response.content,
            "citations": [],  # Don't include separate citations since they're inline
            "metadata": {
                "language": language,
                "confidence": spiritual_response.confidence,
                "processing_time_ms": int(spiritual_response.response_time * 1000),
                "voice_enabled": voice_enabled,
                "service_version": "enhanced_budget_aware_v1.0",
                "spiritual_context": spiritual_response.spiritual_context.value if spiritual_response.spiritual_context else "general",
                "safety_passed": spiritual_response.safety_passed,
                "safety_score": spiritual_response.safety_score,
                "token_usage": {
                    "input_tokens": spiritual_response.token_usage.input_tokens,
                    "output_tokens": spiritual_response.token_usage.output_tokens,
                    "total_tokens": spiritual_response.token_usage.total_tokens,
                    "estimated_cost": spiritual_response.token_usage.estimated_cost
                } if spiritual_response.token_usage else None,
                **spiritual_response.metadata
            }
        }
        
        # Add audio URL if voice enabled (placeholder for now)
        if voice_enabled:
            response_data["audio_url"] = None  # TODO: Implement TTS
        
        logger.info("✅ Generated response using budget-aware LLM service")
        return response_data
        
    except Exception as e:
        logger.error(f"Budget-aware LLM service failed: {e}")
        # Return fallback to original function
        return await _generate_spiritual_response(
            query, language, include_citations, voice_enabled, conversation_context,
            user_id, user_email, session_id, personality_id
        )


async def _generate_spiritual_response(
    query: str, 
    language: str, 
    include_citations: bool,
    voice_enabled: bool,
    conversation_context: List[Dict[str, str]] = None,
    user_id: str = None,
    user_email: str = None,
    session_id: str = None,
    personality_id: str = "krishna"
) -> Dict[str, Any]:
    """
    Generate spiritual guidance response using simplified LLM service.
    
    Args:
        query: User's spiritual question
        language: Response language (English/Hindi)
        include_citations: Whether to include source citations
        voice_enabled: Whether to generate audio response
        conversation_context: Previous conversation context
        user_id: User ID for conversation tracking
        user_email: User email for conversation tracking
        session_id: Session ID for conversation tracking
        personality_id: ID of the personality to use for response generation
    
    Returns:
        Structured response with guidance, citations, and metadata
    """
    try:
        # Use simplified LLM service
        from services.llm_service import llm_service
        
        # Get spiritual guidance with conversation context
        spiritual_response = await llm_service.get_spiritual_guidance(
            query, context="general", conversation_context=conversation_context, personality_id=personality_id
        )
        
        # Structure the response
        response_data = {
            "response": spiritual_response.content,
            "citations": [],  # Don't include separate citations since they're inline
            "metadata": {
                "language": language,
                "confidence": spiritual_response.confidence,
                "processing_time_ms": 150,  # Simulated
                "voice_enabled": voice_enabled,
                "service_version": "simplified_v1.0",
                **spiritual_response.metadata
            }
        }
        
        # Save conversation to database for audit and improvement
        if user_id and user_email:
            try:
                from services.database_service import db_service, Conversation
                
                conversation = Conversation(
                    id=f"conv_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                    userId=user_id,
                    userEmail=user_email,
                    sessionId=session_id or f"session_{user_id}",
                    timestamp=datetime.utcnow().isoformat(),
                    question=query,
                    response=spiritual_response.content,
                    citations=spiritual_response.citations,
                    personality="krishna",  # Default personality
                    metadata={
                        "language": language,
                        "confidence": spiritual_response.confidence,
                        "model": spiritual_response.metadata.get("model", "gemini-2.5-flash"),
                        "tokens": spiritual_response.metadata.get("total_tokens", 0),
                        "cost": spiritual_response.metadata.get("estimated_cost", 0.0),
                        "responseTime": spiritual_response.metadata.get("response_time", 0.0),
                        "voiceEnabled": voice_enabled,
                        "includeCitations": include_citations
                    }
                )
                
                # Save conversation asynchronously
                await db_service.save_conversation(conversation)
                logger.info(f"💾 Conversation saved for user {user_email}")
                
            except Exception as db_error:
                logger.error(f"Failed to save conversation: {db_error}")
                # Don't fail the request if database save fails
        
        # Add audio URL if voice enabled (placeholder for now)
        if voice_enabled:
            response_data["audio_url"] = None  # TODO: Implement TTS
        
        logger.info("✅ Generated response using simplified LLM service")
        return response_data
        
    except Exception as e:
        logger.error(f"LLM service failed: {e}")
        # Return basic fallback
        return {
            "response": "🙏 The spiritual guidance service is experiencing technical difficulties. Our divine wisdom is temporarily unavailable. Please try again in a moment, dear soul. (Backend Error)",
            "citations": [],
            "metadata": {
                "language": language,
                "confidence": 0.3,
                "processing_time_ms": 50,
                "voice_enabled": voice_enabled,
                "service_version": "backend_fallback_v1.0",
                "error": str(e)
            }
        }

async def handle_options_impl(req: func.HttpRequest) -> func.HttpResponse:
    """Handle CORS preflight requests for all routes."""
    return func.HttpResponse(
        "",
        status_code=204,
        headers={
            "Access-Control-Allow-Origin": "https://vimarsh.vedprakash.net",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, x-request-id, x-user-id, x-user-email, x-session-id",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Max-Age": "86400"
        }
    )


# CORS handling for browser requests
@app.function_name("options_handler")
@app.route(route="{*route}", methods=["OPTIONS"], auth_level=func.AuthLevel.ANONYMOUS)
async def handle_options(req: func.HttpRequest) -> func.HttpResponse:
    """Azure Functions wrapper for CORS preflight requests."""
    return await handle_options_impl(req)

# Feedback API imports
try:
    from feedback_api import (
        collect_feedback_endpoint,
        get_feedback_analytics,
        get_improvement_metrics,
        export_feedback_report
    )
    FEEDBACK_API_AVAILABLE = True
    logger.info("Feedback API module loaded successfully")
except ImportError as e:
    FEEDBACK_API_AVAILABLE = False
    logger.warning(f"Feedback API not available: {e}")


async def collect_feedback_impl(req: func.HttpRequest) -> func.HttpResponse:
    """
    Collects feedback from users regarding the spiritual guidance received.
    
    Request Body:
        {
            "request_id": "unique-request-identifier",
            "user_id": "optional-user-identifier",
            "feedback": "User's feedback on the guidance",
            "rating": 1-5 (optional, default: 3),
            "language": "English" | "Hindi" (optional, default: "English")
        }
    
    Returns:
        {
            "status": "success",
            "message": "Feedback collected successfully",
            "feedback_id": "unique-feedback-identifier"
        }
    """
    try:
        # Parse and validate request
        if not req.get_body():
            raise ValueError("Request body is required")
            
        feedback_data = req.get_json()
        if not feedback_data:
            raise ValueError("Invalid JSON in request body")
        
        # Extract request parameters
        request_id = feedback_data.get('request_id', '').strip()
        user_id = feedback_data.get('user_id', '').strip()
        feedback = feedback_data.get('feedback', '').strip()
        rating = feedback_data.get('rating', 3)
        language = feedback_data.get('language', 'English')
        
        # Validate required parameters
        if not request_id:
            raise ValueError("Request ID is required and cannot be empty")
        
        if not feedback:
            raise ValueError("Feedback parameter is required and cannot be empty")
        
        if language not in ['English', 'Hindi']:
            raise ValueError("Language must be 'English' or 'Hindi'")
        
        logger.info(f"Collecting feedback for request ID {request_id}...")
        
        # For MVP, simulate feedback collection
        # This will be enhanced with actual data storage and processing
        feedback_id = f"fb-{hash(request_id)}"
        logger.info(f"Feedback collected: {feedback_id}")
        
        return func.HttpResponse(
            json.dumps({
                "status": "success",
                "message": "Feedback collected successfully",
                "feedback_id": feedback_id
            }),
            mimetype="application/json",
            status_code=200,
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )
        
    except ValueError as e:
        logger.warning(f"Invalid feedback submission: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "error": "Invalid feedback submission",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }),
            mimetype="application/json",
            status_code=400
        )
        
    except Exception as e:
        logger.error(f"Feedback collection failed: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "error": "Internal server error",
                "message": "Unable to collect feedback",
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": req.headers.get('x-request-id', 'unknown')
            }),
            mimetype="application/json",
            status_code=500
        )


@app.route(route="feedback/collect", methods=["POST"])
async def collect_feedback(req: func.HttpRequest) -> func.HttpResponse:
    """Azure Functions wrapper for feedback collection."""
    return await collect_feedback_impl(req)


async def get_feedback_analytics_impl(req: func.HttpRequest) -> func.HttpResponse:
    """
    Retrieves feedback analytics for the spiritual guidance provided.
    
    Query Parameters:
        - start_date: "YYYY-MM-DD" (optional, default: 30 days ago)
        - end_date: "YYYY-MM-DD" (optional, default: today)
        - granularity: "daily" | "weekly" | "monthly" (optional, default: "daily")
        - language: "English" | "Hindi" (optional, default: "English")
    
    Returns:
        {
            "analytics": {
                "total_feedback": 100,
                "average_rating": 4.2,
                "feedback_trends": [...]
            }
        }
    """
    try:
        # Parse query parameters
        start_date = req.params.get('start_date')
        end_date = req.params.get('end_date')
        granularity = req.params.get('granularity', 'daily')
        language = req.params.get('language', 'English')
        
        logger.info(f"Retrieving feedback analytics from {start_date} to {end_date}...")
        
        # For MVP, return simulated analytics data
        # This will be enhanced with actual analytics computation
        analytics_data = {
            "total_feedback": 100,
            "average_rating": 4.2,
            "feedback_trends": [
                {"date": "2023-10-01", "positive": 30, "negative": 5},
                {"date": "2023-10-02", "positive": 25, "negative": 10},
                {"date": "2023-10-03", "positive": 35, "negative": 8}
            ]
        }
        
        return func.HttpResponse(
            json.dumps({
                "analytics": analytics_data
            }),
            mimetype="application/json",
            status_code=200,
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Access-Control-Allow-Origin": "*"
            }
        )
        
    except Exception as e:
        logger.error(f"Feedback analytics retrieval failed: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )


@app.route(route="feedback/analytics", methods=["GET"])
async def get_feedback_analytics(req: func.HttpRequest) -> func.HttpResponse:
    """Azure Functions wrapper for feedback analytics retrieval."""
    return await get_feedback_analytics_impl(req)


async def get_improvement_metrics_impl(req: func.HttpRequest) -> func.HttpResponse:
    """
    Retrieves system performance and improvement metrics based on user feedback.
    
    Query Parameters:
        - metric_type: "response_time" | "accuracy" | "user_satisfaction" (optional, default: "response_time")
        - time_period: "daily" | "weekly" | "monthly" (optional, default: "weekly")
    
    Returns:
        {
            "metrics": {
                "response_time": [...],
                "accuracy": [...],
                "user_satisfaction": [...]
            }
        }
    """
    try:
        # Parse query parameters
        metric_type = req.params.get('metric_type', 'response_time')
        time_period = req.params.get('time_period', 'weekly')
        
        logger.info(f"Retrieving improvement metrics for {metric_type} over {time_period}...")
        
        # For MVP, return simulated metrics data
        # This will be enhanced with actual metrics computation
        metrics_data = {
            "response_time": [120, 115, 130, 110, 105],
            "accuracy": [0.85, 0.87, 0.86, 0.88, 0.84],
            "user_satisfaction": [4.2, 4.3, 4.1, 4.5, 4.0]
        }
        
        return func.HttpResponse(
            json.dumps({
                "metrics": metrics_data
            }),
            mimetype="application/json",
            status_code=200,
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Access-Control-Allow-Origin": "*"
            }
        )
        
    except Exception as e:
        logger.error(f"Improvement metrics retrieval failed: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )


@app.route(route="feedback/improvement_metrics", methods=["GET"])
async def get_improvement_metrics(req: func.HttpRequest) -> func.HttpResponse:
    """Azure Functions wrapper for improvement metrics retrieval."""
    return await get_improvement_metrics_impl(req)


async def export_feedback_report_impl(req: func.HttpRequest) -> func.HttpResponse:
    """
    Exports feedback data report for administrators.
    
    Query Parameters:
        - format: "csv" | "json" (optional, default: "csv")
        - start_date: "YYYY-MM-DD" (optional, default: 30 days ago)
        - end_date: "YYYY-MM-DD" (optional, default: today)
    
    Returns:
        {
            "status": "success",
            "message": "Report generated successfully",
            "report_url": "https://example.com/report.csv"
        }
    """
    try:
        # Parse query parameters
        report_format = req.params.get('format', 'csv')
        start_date = req.params.get('start_date')
        end_date = req.params.get('end_date')
        
        logger.info(f"Exporting feedback report from {start_date} to {end_date} in {report_format} format...")
        
        # For MVP, simulate report generation
        # This will be enhanced with actual report generation and storage
        report_url = f"https://example.com/report-{hash(datetime.utcnow())}.{report_format}"
        
        return func.HttpResponse(
            json.dumps({
                "status": "success",
                "message": "Report generated successfully",
                "report_url": report_url
            }),
            mimetype="application/json",
            status_code=200,
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )
        
    except Exception as e:
        logger.error(f"Feedback report export failed: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "error": "Internal server error",
                "message": "Unable to export feedback report",
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": req.headers.get('x-request-id', 'unknown')
            }),
            mimetype="application/json",
            status_code=500
        )


@app.route(route="feedback/export_report", methods=["POST"])
async def export_feedback_report_basic(req: func.HttpRequest) -> func.HttpResponse:
    """Azure Functions wrapper for feedback report export."""
    return await export_feedback_report_impl(req)

# Feedback API endpoints (if available)
if FEEDBACK_API_AVAILABLE:
    @app.function_name("feedback_collect")
    @app.route(route="feedback/collect", methods=["POST"])
    async def feedback_collect(req: func.HttpRequest) -> func.HttpResponse:
        """Collect user feedback endpoint."""
        try:
            return await collect_feedback_endpoint(req)
        except Exception as e:
            logger.error(f"Error in feedback collection: {e}")
            return func.HttpResponse(
                json.dumps({"error": "Feedback collection service unavailable"}),
                status_code=503,
                mimetype="application/json"
            )

    @app.function_name("feedback_analytics")
    @app.route(route="feedback/analytics", methods=["GET"])
    async def feedback_analytics(req: func.HttpRequest) -> func.HttpResponse:
        """Get feedback analytics endpoint."""
        try:
            return await get_feedback_analytics(req)
        except Exception as e:
            logger.error(f"Error in feedback analytics: {e}")
            return func.HttpResponse(
                json.dumps({"error": "Analytics service unavailable"}),
                status_code=503,
                mimetype="application/json"
            )

    @app.function_name("improvement_metrics")
    @app.route(route="feedback/improvement-metrics", methods=["GET"])
    async def improvement_metrics(req: func.HttpRequest) -> func.HttpResponse:
        """Get improvement metrics endpoint."""
        try:
            return await get_improvement_metrics(req)
        except Exception as e:
            logger.error(f"Error in improvement metrics: {e}")
            return func.HttpResponse(
                json.dumps({"error": "Improvement metrics service unavailable"}),
                status_code=503,
                mimetype="application/json"
            )

    @app.function_name("export_feedback_report")
    @app.route(route="feedback/export-report", methods=["GET"])
    async def export_report_conditional(req: func.HttpRequest) -> func.HttpResponse:
        """Export feedback report endpoint."""
        try:
            return await export_feedback_report_impl(req)
        except Exception as e:
            logger.error(f"Error in report export: {e}")
            return func.HttpResponse(
                json.dumps({"error": "Report export service unavailable"}),
                status_code=503,
                mimetype="application/json"
            )

    @app.function_name("feedback_health")
    @app.route(route="feedback/health", methods=["GET"])
    async def feedback_health(req: func.HttpRequest) -> func.HttpResponse:
        """Health check for feedback service."""
        return func.HttpResponse(
            json.dumps({
                "status": "healthy",
                "service": "vimarsh-feedback-api",
                "timestamp": datetime.utcnow().isoformat(),
                "features": {
                    "collection": True,
                    "analytics": True,
                    "improvement_metrics": True,
                    "export": True
                }
            }),
            status_code=200,
            mimetype="application/json"
        )
else:
    @app.function_name("feedback_unavailable")
    @app.route(route="feedback/{*route}", methods=["GET", "POST"])
    async def feedback_unavailable(req: func.HttpRequest) -> func.HttpResponse:
        """Fallback for when feedback API is unavailable."""
        return func.HttpResponse(
            json.dumps({
                "error": "Feedback API is not available in this deployment",
                "message": "Please check system configuration"
            }),
            status_code=503,
            mimetype="application/json"
        )

# Admin endpoints for cost management and user administration
try:
    from admin import (
        admin_cost_dashboard,
        admin_user_management,
        admin_budget_management,
        super_admin_role_management,
        admin_system_health,
        admin_get_user_role,
        admin_metrics_dashboard,
        admin_performance_report,
        admin_real_time_metrics,
        admin_alerts_dashboard
    )
    ADMIN_AVAILABLE = True
    logger.info("✅ Admin endpoints loaded successfully")
except ImportError as e:
    logger.error(f"❌ Admin endpoints not available: {e}")
    ADMIN_AVAILABLE = False

# Register admin endpoints if available
if ADMIN_AVAILABLE:
    @app.function_name("admin_cost_dashboard")
    @app.route(route="vimarsh-admin/cost-dashboard", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
    @require_admin
    async def admin_cost_dashboard_endpoint(req: func.HttpRequest) -> func.HttpResponse:
        """Admin cost dashboard endpoint - Requires admin authentication."""
        try:
            return await admin_cost_dashboard(req)
        except Exception as e:
            logger.error(f"Error in admin cost dashboard: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return func.HttpResponse(
                json.dumps({"error": "Cost dashboard service unavailable", "debug": str(e)}),
                status_code=503,
                mimetype="application/json"
            )

    @app.function_name("admin_user_list")
    @app.route(route="vimarsh-admin/users", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
    @require_admin
    async def admin_user_list_endpoint(req: func.HttpRequest) -> func.HttpResponse:
        """Admin user list endpoint - Requires admin authentication."""
        try:
            return await admin_user_management(req)
        except Exception as e:
            logger.error(f"Error in admin user list: {e}")
            return func.HttpResponse(
                json.dumps({"error": "User list service unavailable"}),
                status_code=503,
                mimetype="application/json"
            )

    @app.function_name("admin_user_block")
    @app.route(route="vimarsh-admin/users/{user_id}/block", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
    @require_admin
    async def admin_user_block_endpoint(req: func.HttpRequest) -> func.HttpResponse:
        """Admin user block endpoint - Requires admin authentication."""
        try:
            return await admin_user_management(req)
        except Exception as e:
            logger.error(f"Error in admin user block: {e}")
            return func.HttpResponse(
                json.dumps({"error": "User block service unavailable"}),
                status_code=503,
                mimetype="application/json"
            )

    @app.function_name("admin_user_unblock")
    @app.route(route="vimarsh-admin/users/{user_id}/unblock", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
    @require_admin
    async def admin_user_unblock_endpoint(req: func.HttpRequest) -> func.HttpResponse:
        """Admin user unblock endpoint - Requires admin authentication."""
        try:
            return await admin_user_management(req)
        except Exception as e:
            logger.error(f"Error in admin user unblock: {e}")
            return func.HttpResponse(
                json.dumps({"error": "User unblock service unavailable"}),
                status_code=503,
                mimetype="application/json"
            )

    @app.function_name("admin_budget_list")
    @app.route(route="vimarsh-admin/budgets", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
    @require_admin
    async def admin_budget_list_endpoint(req: func.HttpRequest) -> func.HttpResponse:
        """Admin budget list endpoint - Requires admin authentication."""
        try:
            return await admin_budget_management(req)
        except Exception as e:
            logger.error(f"Error in admin budget list: {e}")
            return func.HttpResponse(
                json.dumps({"error": "Budget list service unavailable"}),
                status_code=503,
                mimetype="application/json"
            )

    @app.function_name("admin_budget_create")
    @app.route(route="vimarsh-admin/budgets", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
    @require_admin
    async def admin_budget_create_endpoint(req: func.HttpRequest) -> func.HttpResponse:
        """Admin budget create endpoint - Requires admin authentication."""
        try:
            return await admin_budget_management(req)
        except Exception as e:
            logger.error(f"Error in admin budget create: {e}")
            return func.HttpResponse(
                json.dumps({"error": "Budget create service unavailable"}),
                status_code=503,
                mimetype="application/json"
            )

    @app.function_name("admin_budget_override")
    @app.route(route="vimarsh-admin/budgets/{user_id}/override", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
    @require_admin
    async def admin_budget_override_endpoint(req: func.HttpRequest) -> func.HttpResponse:
        """Admin budget override endpoint - Requires admin authentication."""
        try:
            return await admin_budget_management(req)
        except Exception as e:
            logger.error(f"Error in admin budget override: {e}")
            return func.HttpResponse(
                json.dumps({"error": "Budget override service unavailable"}),
                status_code=503,
                mimetype="application/json"
            )

    @app.function_name("super_admin_role_list")
    @app.route(route="vimarsh-admin/roles", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
    @require_admin
    async def super_admin_role_list_endpoint(req: func.HttpRequest) -> func.HttpResponse:
        """Super admin role list endpoint - Requires admin authentication."""
        try:
            return await super_admin_role_management(req)
        except Exception as e:
            logger.error(f"Error in super admin role list: {e}")
            return func.HttpResponse(
                json.dumps({"error": "Role list service unavailable"}),
                status_code=503,
                mimetype="application/json"
            )

    @app.function_name("super_admin_role_create")
    @app.route(route="vimarsh-admin/roles", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
    @require_admin
    async def super_admin_role_create_endpoint(req: func.HttpRequest) -> func.HttpResponse:
        """Super admin role create endpoint - Requires admin authentication."""
        try:
            return await super_admin_role_management(req)
        except Exception as e:
            logger.error(f"Error in super admin role create: {e}")
            return func.HttpResponse(
                json.dumps({"error": "Role create service unavailable"}),
                status_code=503,
                mimetype="application/json"
            )

    @app.function_name("admin_system_health")
    @app.route(route="vimarsh-admin/health", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
    @require_admin
    async def admin_system_health_endpoint(req: func.HttpRequest) -> func.HttpResponse:
        """Admin system health endpoint - Requires admin authentication."""
        try:
            return await admin_system_health(req)
        except Exception as e:
            logger.error(f"Error in admin system health: {e}")
            return func.HttpResponse(
                json.dumps({"error": "System health service unavailable"}),
                status_code=503,
                mimetype="application/json"
            )

    @app.function_name("admin_get_role")
    @app.route(route="vimarsh-admin/role", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
    @require_admin
    async def admin_get_role_endpoint(req: func.HttpRequest) -> func.HttpResponse:
        """Admin get user role endpoint - Requires admin authentication."""
        try:
            return await admin_get_user_role(req)
        except Exception as e:
            logger.error(f"Error in admin get role: {e}")
            return func.HttpResponse(
                json.dumps({"error": "Role service unavailable"}),
                status_code=503,
                mimetype="application/json",
                headers={
                    "Access-Control-Allow-Origin": "https://vimarsh.vedprakash.net",
                    "Access-Control-Allow-Credentials": "true",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization, x-request-id, x-user-id, x-user-email, x-session-id"
                }
            )

    @app.function_name("admin_dev_token")
    @app.route(route="vimarsh-admin/dev-token", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
    async def admin_dev_token_endpoint(req: func.HttpRequest) -> func.HttpResponse:
        """Generate development token for specific user - Development mode only."""
        try:
            # Only allow in development mode
            if os.getenv('ENVIRONMENT', 'production') != 'development':
                return func.HttpResponse(
                    json.dumps({"error": "Development tokens only available in development mode"}),
                    status_code=403,
                    mimetype="application/json",
                    headers={"Access-Control-Allow-Origin": "*"}
                )
            
            # Parse request body
            try:
                req_body = req.get_json()
                user_email = req_body.get('email')
                if not user_email:
                    return func.HttpResponse(
                        json.dumps({"error": "Email is required"}),
                        status_code=400,
                        mimetype="application/json",
                        headers={"Access-Control-Allow-Origin": "*"}
                    )
            except Exception:
                return func.HttpResponse(
                    json.dumps({"error": "Invalid JSON body"}),
                    status_code=400,
                    mimetype="application/json",
                    headers={"Access-Control-Allow-Origin": "*"}
                )
            
            # Use simple dev token format: dev:email:timestamp:signature
            import hashlib
            import hmac
            from datetime import datetime
            
            dev_secret = os.getenv('DEV_AUTH_SECRET', 'dev-secret-change-in-production')
            timestamp = str(int(datetime.utcnow().timestamp()))
            payload = f"{user_email}:{timestamp}"
            signature = hmac.new(
                dev_secret.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            
            dev_token = f"dev:{user_email}:{timestamp}:{signature}"
            
            logger.info(f"🔑 Generated development token for user: {user_email}")
            
            return func.HttpResponse(
                json.dumps({
                    "token": dev_token,
                    "email": user_email,
                    "expires_in": "24h"
                }),
                status_code=200,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
            )
            
        except Exception as e:
            logger.error(f"Error generating development token: {e}")
            return func.HttpResponse(
                json.dumps({"error": f"Token generation failed: {str(e)}"}),
                status_code=500,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
            )
    @app.function_name("admin_real_time_metrics")
    @app.route(route="vimarsh-admin/real-time-metrics", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
    @require_admin
    async def admin_real_time_metrics_endpoint(req: func.HttpRequest) -> func.HttpResponse:
        """Admin real-time metrics endpoint - Requires admin authentication."""
        try:
            return await admin_real_time_metrics(req)
        except Exception as e:
            logger.error(f"Error in admin real-time metrics: {e}")
            return func.HttpResponse(
                json.dumps({"error": "Real-time metrics service unavailable"}),
                status_code=503,
                mimetype="application/json"
            )

    @app.function_name("admin_alerts_dashboard")
    @app.route(route="vimarsh-admin/alerts", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
    @require_admin
    async def admin_alerts_dashboard_endpoint(req: func.HttpRequest) -> func.HttpResponse:
        """Admin alerts dashboard endpoint - Requires admin authentication."""
        try:
            return await admin_alerts_dashboard(req)
        except Exception as e:
            logger.error(f"Error in admin alerts dashboard: {e}")
            return func.HttpResponse(
                json.dumps({"error": "Alerts dashboard service unavailable"}),
                status_code=503,
                mimetype="application/json"
            )

    # Simple test endpoint without complex decorators
    @app.function_name("admin_test")
    @app.route(route="vimarsh-admin/test", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
    async def admin_test_endpoint(req: func.HttpRequest) -> func.HttpResponse:
        """Simple admin test endpoint."""
        try:
            # Check if user is authenticated
            if AUTHENTICATION_ENABLED:
                user = auth_service.authenticate_request(req)
                if not user:
                    return func.HttpResponse(
                        json.dumps({"error": "Authentication required"}),
                        status_code=401,
                        mimetype="application/json",
                        headers={
                            "Access-Control-Allow-Origin": "https://vimarsh.vedprakash.net",
                            "Access-Control-Allow-Credentials": "true",
                            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                            "Access-Control-Allow-Headers": "Content-Type, Authorization, x-request-id, x-user-id, x-user-email, x-session-id"
                        }
                    )
                
                # Check admin role
                from core.user_roles import admin_role_manager
                user_role = admin_role_manager.get_user_role(user.email)
                is_admin = admin_role_manager.is_admin(user.email)
                
                return func.HttpResponse(
                    json.dumps({
                        "message": "Admin test successful",
                        "user_email": user.email,
                        "user_role": str(user_role),
                        "is_admin": is_admin,
                        "timestamp": datetime.utcnow().isoformat()
                    }),
                    mimetype="application/json",
                    status_code=200,
                    headers={
                        "Access-Control-Allow-Origin": "https://vimarsh.vedprakash.net",
                        "Access-Control-Allow-Credentials": "true",
                        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                        "Access-Control-Allow-Headers": "Content-Type, Authorization, x-request-id, x-user-id, x-user-email, x-session-id"
                    }
                )
            else:
                return func.HttpResponse(
                    json.dumps({"message": "Authentication disabled"}),
                    mimetype="application/json",
                    status_code=200
                )
        except Exception as e:
            logger.error(f"Admin test error: {e}")
            return func.HttpResponse(
                json.dumps({"error": str(e)}),
                status_code=500,
                mimetype="application/json",
                headers={
                    "Access-Control-Allow-Origin": "https://vimarsh.vedprakash.net",
                    "Access-Control-Allow-Credentials": "true",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization, x-request-id, x-user-id, x-user-email, x-session-id"
                }
            )

else:
    @app.function_name("admin_unavailable")
    @app.route(route="vimarsh-admin/{*route}", methods=["GET", "POST"])
    async def admin_unavailable(req: func.HttpRequest) -> func.HttpResponse:
        """Fallback for when admin API is unavailable."""
        return func.HttpResponse(
            json.dumps({
                "error": "Admin API is not available in this deployment",
                "message": "Please check system configuration and admin permissions"
            }),
            status_code=503,
            mimetype="application/json"
        )

@app.route(route="user/budget", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
async def user_budget_status(req: func.HttpRequest) -> func.HttpResponse:
    """User endpoint to view their own budget status and usage."""
    try:
        # Get user context (similar to spiritual guidance)
        user_id = req.headers.get('x-user-id', 'dev_user_1')
        user_email = req.headers.get('x-user-email', 'dev@example.com')
        
        # Optional authentication check
        if AUTHENTICATION_ENABLED and os.getenv("ENABLE_AUTH", "false").lower() == "true":
            try:
                user = auth_middleware.extract_user_from_request(req)
                if user:
                    user_id = user.id
                    user_email = user.email
                    logger.info(f"🔐 Budget request from authenticated user: {user.email}")
                else:
                    return func.HttpResponse(
                        json.dumps({
                            "error": "Authentication required",
                            "message": "Valid access token must be provided to view budget status"
                        }),
                        status_code=401,
                        mimetype="application/json",
                        headers={"Access-Control-Allow-Origin": "*"}
                    )
            except Exception as e:
                logger.warning(f"Authentication failed: {e}")
                return func.HttpResponse(
                    json.dumps({
                        "error": "Authentication failed",
                        "message": str(e)
                    }),
                    status_code=401,
                    mimetype="application/json",
                    headers={"Access-Control-Allow-Origin": "*"}
                )
        
        # Get budget status and usage
        if TOKEN_TRACKING_AVAILABLE:
            from backend.core.token_tracker import token_tracker
            from backend.core.budget_validator import budget_validator
            
            budget_status = budget_validator.get_user_budget_status(user_id)
            user_stats = token_tracker.get_user_usage(user_id)
            forecast = token_tracker.get_cost_forecast(user_id)
            
            response_data = {
                "user_id": user_id,
                "user_email": user_email,
                "budget_status": budget_status,
                "usage_stats": user_stats.to_dict() if user_stats else None,
                "cost_forecast": forecast,
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            response_data = {
                "user_id": user_id,
                "user_email": user_email,
                "budget_status": {"status": "tracking_not_available"},
                "usage_stats": None,
                "cost_forecast": None,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        return func.HttpResponse(
            json.dumps(response_data),
            mimetype="application/json",
            status_code=200,
            headers={"Access-Control-Allow-Origin": "*"}
        )
        
    except Exception as e:
        logger.error(f"User budget status error: {e}")
        return func.HttpResponse(
            json.dumps({
                "error": "Failed to retrieve budget status",
                "message": str(e)
            }),
            status_code=500,
            mimetype="application/json",
            headers={"Access-Control-Allow-Origin": "*"}
        )

# Personality Management Endpoints
if PERSONALITY_ENDPOINTS_AVAILABLE:
    @app.function_name("admin_create_personality")
    @app.route(route="admin/personalities", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
    async def admin_create_personality_endpoint(req: func.HttpRequest) -> func.HttpResponse:
        """Create new personality endpoint."""
        return await create_personality(req)

    @app.function_name("admin_get_personality")
    @app.route(route="admin/personalities/{personality_id}", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
    async def admin_get_personality_endpoint(req: func.HttpRequest) -> func.HttpResponse:
        """Get personality by ID endpoint."""
        return await get_personality(req)

    @app.function_name("admin_update_personality")
    @app.route(route="admin/personalities/{personality_id}", methods=["PUT"], auth_level=func.AuthLevel.ANONYMOUS)
    async def admin_update_personality_endpoint(req: func.HttpRequest) -> func.HttpResponse:
        """Update personality endpoint."""
        return await update_personality(req)

    @app.function_name("admin_delete_personality")
    @app.route(route="admin/personalities/{personality_id}", methods=["DELETE"], auth_level=func.AuthLevel.ANONYMOUS)
    async def admin_delete_personality_endpoint(req: func.HttpRequest) -> func.HttpResponse:
        """Delete personality endpoint."""
        return await delete_personality(req)

    @app.function_name("admin_search_personalities")
    @app.route(route="admin/personalities", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
    async def admin_search_personalities_endpoint(req: func.HttpRequest) -> func.HttpResponse:
        """Search personalities endpoint."""
        return await search_personalities(req)

    @app.function_name("admin_personalities_by_domain")
    @app.route(route="admin/personalities/domain/{domain}", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
    async def admin_personalities_by_domain_endpoint(req: func.HttpRequest) -> func.HttpResponse:
        """Get personalities by domain endpoint."""
        return await get_personalities_by_domain(req)

    @app.function_name("discover_personalities")
    @app.route(route="personalities/discover", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
    async def discover_personalities_endpoint(req: func.HttpRequest) -> func.HttpResponse:
        """Discover personalities endpoint."""
        return await discover_personalities(req)

    @app.function_name("get_active_personalities")
    @app.route(route="personalities/active", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
    async def get_active_personalities_endpoint(req: func.HttpRequest) -> func.HttpResponse:
        """Get active personalities endpoint."""
        return await get_active_personalities(req)

    @app.function_name("generate_personality_response")
    @app.route(route="personalities/{personality_id}/chat", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
    async def generate_personality_response_endpoint(req: func.HttpRequest) -> func.HttpResponse:
        """Generate personality response endpoint."""
        try:
            from services.llm_service import EnhancedLLMService
            
            # Get personality ID from route
            personality_id = req.route_params.get('personality_id')
            if not personality_id:
                return func.HttpResponse(
                    json.dumps({"error": "Personality ID is required"}),
                    status_code=400,
                    headers={"Content-Type": "application/json"}
                )
            
            # Parse request body
            try:
                body = req.get_json()
            except ValueError:
                return func.HttpResponse(
                    json.dumps({"error": "Invalid JSON in request body"}),
                    status_code=400,
                    headers={"Content-Type": "application/json"}
                )
            
            if not body or 'query' not in body:
                return func.HttpResponse(
                    json.dumps({"error": "Query is required"}),
                    status_code=400,
                    headers={"Content-Type": "application/json"}
                )
            
            # Generate response
            llm_service = EnhancedLLMService()
            response = await llm_service.generate_personality_response(
                query=body['query'],
                personality_id=personality_id,
                context_chunks=body.get('context_chunks', []),
                conversation_history=body.get('conversation_history', []),
                language=body.get('language', 'English'),
                user_id=body.get('user_id'),
                session_id=body.get('session_id')
            )
            
            return func.HttpResponse(
                json.dumps({
                    "success": True,
                    "response": {
                        "content": response.content,
                        "citations": response.citations,
                        "confidence": response.confidence,
                        "language": response.language,
                        "metadata": response.metadata,
                        "safety_passed": response.safety_passed
                    }
                }),
                status_code=200,
                headers={"Content-Type": "application/json"}
            )
            
        except Exception as e:
            logger.error(f"Failed to generate personality response: {str(e)}")
            return func.HttpResponse(
                json.dumps({"error": "Failed to generate response"}),
                status_code=500,
                headers={"Content-Type": "application/json"}
            )
else:
    @app.function_name("personality_endpoints_unavailable")
    @app.route(route="admin/personalities/{*route}", methods=["GET", "POST", "PUT", "DELETE"])
    @app.route(route="personalities/{*route}", methods=["GET", "POST"])
    async def personality_endpoints_unavailable(req: func.HttpRequest) -> func.HttpResponse:
        """Fallback for when personality endpoints are unavailable."""
        return func.HttpResponse(
            json.dumps({
                "error": "Personality management not available",
                "message": "Personality management functionality is currently unavailable"
            }),
            status_code=503,
            headers={"Content-Type": "application/json"}
        )

# Content Management Endpoints
if CONTENT_ENDPOINTS_AVAILABLE:
    @app.function_name("admin_get_content")
    @app.route(route="admin/content", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
    async def admin_get_content_endpoint(req: func.HttpRequest) -> func.HttpResponse:
        """Get content with filtering and search capabilities."""
        return await get_content(req)

    @app.function_name("admin_create_content")
    @app.route(route="admin/content", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
    async def admin_create_content_endpoint(req: func.HttpRequest) -> func.HttpResponse:
        """Create new content item."""
        return await create_content(req)

    @app.function_name("admin_update_content")
    @app.route(route="admin/content/{content_id}", methods=["PUT"], auth_level=func.AuthLevel.ANONYMOUS)
    async def admin_update_content_endpoint(req: func.HttpRequest) -> func.HttpResponse:
        """Update existing content item."""
        return await update_content(req)

    @app.function_name("admin_delete_content")
    @app.route(route="admin/content/{content_id}", methods=["DELETE"], auth_level=func.AuthLevel.ANONYMOUS)
    async def admin_delete_content_endpoint(req: func.HttpRequest) -> func.HttpResponse:
        """Delete content item."""
        return await delete_content(req)

    @app.function_name("admin_associate_content")
    @app.route(route="admin/content/{content_id}/associate", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
    async def admin_associate_content_endpoint(req: func.HttpRequest) -> func.HttpResponse:
        """Associate content with personalities."""
        return await associate_content_personalities(req)

    @app.function_name("admin_validate_content")
    @app.route(route="admin/content/{content_id}/validate", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
    async def admin_validate_content_endpoint(req: func.HttpRequest) -> func.HttpResponse:
        """Validate content quality."""
        return await validate_content_quality(req)

    @app.function_name("admin_approve_content")
    @app.route(route="admin/content/{content_id}/approve", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
    async def admin_approve_content_endpoint(req: func.HttpRequest) -> func.HttpResponse:
        """Approve content item."""
        return await approve_content(req)

    @app.function_name("admin_reject_content")
    @app.route(route="admin/content/{content_id}/reject", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
    async def admin_reject_content_endpoint(req: func.HttpRequest) -> func.HttpResponse:
        """Reject content item."""
        return await reject_content(req)

else:
    @app.function_name("content_endpoints_unavailable")
    @app.route(route="admin/content/{*route}", methods=["GET", "POST", "PUT", "DELETE"])
    async def content_endpoints_unavailable(req: func.HttpRequest) -> func.HttpResponse:
        """Fallback for when content endpoints are unavailable."""
        return func.HttpResponse(
            json.dumps({
                "error": "Content management not available",
                "message": "Content management functionality is currently unavailable"
            }),
            status_code=503,
            headers={"Content-Type": "application/json"}
        )

# Expert Review Endpoints
if EXPERT_REVIEW_ENDPOINTS_AVAILABLE:
    @app.function_name("admin_get_review_items")
    @app.route(route="admin/expert-review/items", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
    async def admin_get_review_items_endpoint(req: func.HttpRequest) -> func.HttpResponse:
        """Get review items with filtering capabilities."""
        return await get_review_items(req)

    @app.function_name("admin_get_experts")
    @app.route(route="admin/expert-review/experts", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
    async def admin_get_experts_endpoint(req: func.HttpRequest) -> func.HttpResponse:
        """Get expert profiles."""
        return await get_experts(req)

    @app.function_name("admin_get_review_queues")
    @app.route(route="admin/expert-review/queues", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
    async def admin_get_review_queues_endpoint(req: func.HttpRequest) -> func.HttpResponse:
        """Get review queue status for all domains."""
        return await get_review_queues(req)

    @app.function_name("admin_assign_review")
    @app.route(route="admin/expert-review/assign", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
    async def admin_assign_review_endpoint(req: func.HttpRequest) -> func.HttpResponse:
        """Assign a review to an expert."""
        return await assign_review(req)

    @app.function_name("admin_submit_feedback")
    @app.route(route="admin/expert-review/feedback", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
    async def admin_submit_feedback_endpoint(req: func.HttpRequest) -> func.HttpResponse:
        """Submit expert feedback for a review."""
        return await submit_feedback(req)

    @app.function_name("admin_get_review_analytics")
    @app.route(route="admin/expert-review/analytics", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
    async def admin_get_review_analytics_endpoint(req: func.HttpRequest) -> func.HttpResponse:
        """Get comprehensive review analytics."""
        return await get_review_analytics(req)

    @app.function_name("admin_submit_for_review")
    @app.route(route="admin/expert-review/submit", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
    async def admin_submit_for_review_endpoint(req: func.HttpRequest) -> func.HttpResponse:
        """Submit content for expert review."""
        return await submit_for_review(req)

else:
    @app.function_name("expert_review_endpoints_unavailable")
    @app.route(route="admin/expert-review/{*route}", methods=["GET", "POST", "PUT", "DELETE"])
    async def expert_review_endpoints_unavailable(req: func.HttpRequest) -> func.HttpResponse:
        """Fallback for when expert review endpoints are unavailable."""
        return func.HttpResponse(
            json.dumps({
                "error": "Expert review not available",
                "message": "Expert review functionality is currently unavailable"
            }),
            status_code=503,
            headers={"Content-Type": "application/json"}
        )

# Performance Monitoring Endpoints
if PERFORMANCE_ENDPOINTS_AVAILABLE:
    @app.function_name("admin_get_cache_metrics")
    @app.route(route="admin/performance/cache-metrics", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
    async def admin_get_cache_metrics_endpoint(req: func.HttpRequest) -> func.HttpResponse:
        """Get cache performance metrics."""
        return await get_cache_metrics(req)

    @app.function_name("admin_get_performance_metrics")
    @app.route(route="admin/performance/metrics", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
    async def admin_get_performance_metrics_endpoint(req: func.HttpRequest) -> func.HttpResponse:
        """Get performance metrics."""
        return await get_performance_metrics(req)

    @app.function_name("admin_get_performance_report")
    @app.route(route="admin/performance/report", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
    async def admin_get_performance_report_endpoint(req: func.HttpRequest) -> func.HttpResponse:
        """Get comprehensive performance report."""
        return await get_performance_report(req)

    @app.function_name("admin_get_performance_alerts")
    @app.route(route="admin/performance/alerts", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
    async def admin_get_performance_alerts_endpoint(req: func.HttpRequest) -> func.HttpResponse:
        """Get active performance alerts."""
        return await get_performance_alerts(req)

    @app.function_name("admin_resolve_alert")
    @app.route(route="admin/performance/alerts/resolve", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
    async def admin_resolve_alert_endpoint(req: func.HttpRequest) -> func.HttpResponse:
        """Resolve a performance alert."""
        return await resolve_alert(req)

    @app.function_name("admin_get_optimization_recommendations")
    @app.route(route="admin/performance/recommendations", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
    async def admin_get_optimization_recommendations_endpoint(req: func.HttpRequest) -> func.HttpResponse:
        """Get performance optimization recommendations."""
        return await get_optimization_recommendations(req)

    @app.function_name("admin_warm_cache")
    @app.route(route="admin/performance/cache/warm", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
    async def admin_warm_cache_endpoint(req: func.HttpRequest) -> func.HttpResponse:
        """Warm cache for specific personality."""
        return await warm_cache(req)

    @app.function_name("admin_invalidate_cache")
    @app.route(route="admin/performance/cache/invalidate", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
    async def admin_invalidate_cache_endpoint(req: func.HttpRequest) -> func.HttpResponse:
        """Invalidate cache entries."""
        return await invalidate_cache(req)

    @app.function_name("admin_optimize_cache")
    @app.route(route="admin/performance/cache/optimize", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
    async def admin_optimize_cache_endpoint(req: func.HttpRequest) -> func.HttpResponse:
        """Optimize cache performance and cleanup."""
        return await optimize_cache(req)

else:
    @app.function_name("performance_endpoints_unavailable")
    @app.route(route="admin/performance/{*route}", methods=["GET", "POST", "PUT", "DELETE"])
    async def performance_endpoints_unavailable(req: func.HttpRequest) -> func.HttpResponse:
        """Fallback for when performance endpoints are unavailable."""
        return func.HttpResponse(
            json.dumps({
                "error": "Performance monitoring not available",
                "message": "Performance monitoring functionality is currently unavailable"
            }),
            status_code=503,
            headers={"Content-Type": "application/json"}
        )