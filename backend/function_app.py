"""
Main Azure Functions application entry point for Vimarsh spiritual guidance API.

This module implements the core Azure Functions HTTP triggers for the spiritual
guidance system, providing endpoints for user queries and spiritual guidance
through Lord Krishna's persona.
"""

import azure.functions as func
import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Azure Functions app
app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


async def health_check_impl(req: func.HttpRequest) -> func.HttpResponse:
    """
    Health check endpoint for monitoring service availability.
    
    Returns:
        HTTP 200: Service is healthy
        HTTP 500: Service has issues
    """
    try:
        health_status = {
            "status": "healthy",
            "service": "vimarsh-spiritual-guidance",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "environment": os.getenv("AZURE_FUNCTIONS_ENVIRONMENT", "unknown")
        }
        
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


@app.route(route="health", methods=["GET"])
async def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """Azure Functions wrapper for health check."""
    return await health_check_impl(req)


async def spiritual_guidance_impl(req: func.HttpRequest) -> func.HttpResponse:
    """
    Main spiritual guidance endpoint providing Lord Krishna's wisdom.
    
    Accepts user queries and returns spiritually grounded responses based on
    sacred texts using RAG pipeline and Gemini Pro API.
    
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
        
        # Validate required parameters
        if not user_query:
            raise ValueError("Query parameter is required and cannot be empty")
        
        if language not in ['English', 'Hindi']:
            raise ValueError("Language must be 'English' or 'Hindi'")
        
        logger.info(f"Processing spiritual guidance request: {user_query[:100]}...")
        
        # For MVP, return a basic structured response
        # This will be enhanced with actual RAG pipeline and LLM integration
        response_data = await _generate_spiritual_response(
            user_query, language, include_citations, voice_enabled
        )
        
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


@app.route(route="spiritual_guidance", methods=["POST"])
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


@app.route(route="languages", methods=["GET"])
async def supported_languages(req: func.HttpRequest) -> func.HttpResponse:
    """Azure Functions wrapper for supported languages."""
    return await supported_languages_impl(req)


async def _generate_spiritual_response(
    query: str, 
    language: str, 
    include_citations: bool,
    voice_enabled: bool
) -> Dict[str, Any]:
    """
    Generate spiritual guidance response (MVP placeholder implementation).
    
    This is a basic implementation that will be enhanced with:
    - RAG pipeline integration
    - Gemini Pro API calls
    - Vector database retrieval
    - Citation extraction
    - Voice synthesis
    
    Args:
        query: User's spiritual question
        language: Response language (English/Hindi)
        include_citations: Whether to include source citations
        voice_enabled: Whether to generate audio response
    
    Returns:
        Structured response with guidance, citations, and metadata
    """
    # MVP placeholder - will be replaced with actual implementation
    base_response = {
        "response": "",
        "citations": [],
        "metadata": {
            "query_processed": query,
            "language": language,
            "processing_time_ms": 150,
            "model_version": "gemini-pro-1.0",
            "persona": "Lord Krishna",
            "confidence_score": 0.85,
            "spiritual_authenticity": "validated"
        }
    }
    
    # Generate basic response based on language
    if language == "Hindi":
        base_response["response"] = (
            "प्रिय भक्त, आपका प्रश्न अत्यंत महत्वपूर्ण है। गीता के अनुसार, "
            "जीवन में आने वाली चुनौतियों का सामना धैर्य और स्थिर बुद्धि से करना चाहिए। "
            "मैं आपको सदैव सत्य के मार्ग पर चलने की प्रेरणा देता हूँ।"
        )
        if include_citations:
            base_response["citations"] = [
                {
                    "source": "भगवद्गीता",
                    "chapter": 2,
                    "verse": 47,
                    "text": "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन",
                    "relevance_score": 0.92
                }
            ]
    else:  # English
        base_response["response"] = (
            "Dear devotee, your question touches the very essence of spiritual wisdom. "
            "As I taught Arjuna on the battlefield of Kurukshetra, life's challenges "
            "are opportunities for spiritual growth. Remember that you have the right "
            "to perform your duties, but never to the fruits of action. Let Me guide "
            "you toward the path of righteousness and inner peace."
        )
        if include_citations:
            base_response["citations"] = [
                {
                    "source": "Bhagavad Gita",
                    "chapter": 2,
                    "verse": 47,
                    "text": "You have a right to perform your prescribed duty, but not to the fruits of action.",
                    "sanskrit": "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।",
                    "relevance_score": 0.92
                }
            ]
    
    # Add voice URL if enabled (placeholder for future implementation)
    if voice_enabled:
        base_response["audio_url"] = f"https://vimarsh-audio.blob.core.windows.net/responses/{hash(query)}.mp3"
    
    return base_response


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
@app.route(route="{*route}", methods=["OPTIONS"])
async def handle_options(req: func.HttpRequest) -> func.HttpResponse:
    """Azure Functions wrapper for CORS preflight requests."""
    return await handle_options_impl(req)
