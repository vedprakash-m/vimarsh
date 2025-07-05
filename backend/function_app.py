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

# Import centralized configuration
try:
    from backend.core.config import get_config
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

# Import authentication middleware
try:
    from auth.entra_external_id_middleware import auth_required, VedUser
    AUTHENTICATION_ENABLED = True
except ImportError:
    AUTHENTICATION_ENABLED = False
    logger.warning("Authentication modules not available, running without auth")

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
            health_status = {
                "status": "healthy",
                "service": "vimarsh-spiritual-guidance",
                "version": "1.0.0",
                "timestamp": datetime.utcnow().isoformat(),
                "environment": os.getenv("AZURE_FUNCTIONS_ENVIRONMENT", "unknown"),
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
    sacred texts using RAG pipeline and Gemini Pro API.
    
    Authentication: Optional - Can be enabled by setting ENABLE_AUTH environment variable
    
    Request Body:
        {
            "query": "User's spiritual question",
            "language": "English" | "Hindi" (optional, default: "English"),
            "include_citations": boolean (optional, default: true),
            "voice_enabled": boolean (optional, default: false)
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
        # Optional authentication check
        user_context = None
        if AUTHENTICATION_ENABLED and os.getenv("ENABLE_AUTH", "false").lower() == "true":
            try:
                # Extract user from JWT token
                auth_header = req.headers.get('Authorization', '')
                if auth_header.startswith('Bearer '):
                    token = auth_header[7:]
                    # Validate token and extract user (simplified for now)
                    user_context = {"authenticated": True, "token": token}
                    logger.info("🔐 Authenticated request received")
                else:
                    logger.warning("Missing authentication token")
            except Exception as auth_error:
                logger.warning(f"Authentication failed: {auth_error}")
                # Continue without auth for graceful degradation
        
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
        conversation_context = query_data.get('conversation_context', [])  # New parameter
        
        # Validate required parameters
        if not user_query:
            raise ValueError("Query parameter is required and cannot be empty")
        
        if language not in ['English', 'Hindi']:
            raise ValueError("Language must be 'English' or 'Hindi'")
        
        logger.info(f"Processing spiritual guidance request: {user_query[:100]}...")
        
        # Generate response with enhanced API integration
        response_data = await _generate_spiritual_response(
            user_query, language, include_citations, voice_enabled, conversation_context
        )
        
        # Add authentication metadata if available
        if user_context:
            response_data["metadata"]["authenticated"] = True
            response_data["metadata"]["user_context"] = "available"
        
        logger.info("Spiritual guidance response generated successfully")
        return func.HttpResponse(
            json.dumps(response_data, ensure_ascii=False),
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


async def _generate_spiritual_response(
    query: str, 
    language: str, 
    include_citations: bool,
    voice_enabled: bool,
    conversation_context: List[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Generate spiritual guidance response using simplified LLM service.
    
    Args:
        query: User's spiritual question
        language: Response language (English/Hindi)
        include_citations: Whether to include source citations
        voice_enabled: Whether to generate audio response
    
    Returns:
        Structured response with guidance, citations, and metadata
    """
    try:
        # Use simplified LLM service
        from services.llm_service import llm_service
        
        # Get spiritual guidance with conversation context
        spiritual_response = await llm_service.get_spiritual_guidance(
            query, context="general", conversation_context=conversation_context
        )
        
        # Structure the response
        response_data = {
            "response": spiritual_response.content,
            "citations": spiritual_response.citations if include_citations else [],
            "metadata": {
                "language": language,
                "confidence": spiritual_response.confidence,
                "processing_time_ms": 150,  # Simulated
                "voice_enabled": voice_enabled,
                "service_version": "simplified_v1.0",
                **spiritual_response.metadata
            }
        }
        
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
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, x-request-id",
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
