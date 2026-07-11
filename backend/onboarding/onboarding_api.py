"""
Onboarding API endpoints for Vimarsh
Provides REST API for personalized onboarding flow.
"""

import azure.functions as func
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any

logger = logging.getLogger(__name__)


def get_cors_headers() -> Dict[str, str]:
    """Get standard CORS headers for all responses"""
    return {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "https://vimarsh.vedmishra.com",
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "GET, POST, PUT, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization"
    }


def register_onboarding_routes(app: func.FunctionApp):
    """Register all onboarding API routes with the function app"""
    
    @app.route(route="onboarding/quiz/questions", methods=["GET"])
    async def get_quiz_questions(req: func.HttpRequest) -> func.HttpResponse:
        """Get all quiz questions for the onboarding flow"""
        try:
            from onboarding import get_quiz_service
            quiz_service = get_quiz_service()
            
            questions = quiz_service.get_all_questions()
            
            return func.HttpResponse(
                json.dumps({
                    "success": True,
                    "questions": questions,
                    "total_questions": len(questions),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }),
                status_code=200,
                headers=get_cors_headers()
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to get quiz questions: {e}")
            return func.HttpResponse(
                json.dumps({"error": "Failed to load quiz questions", "details": str(e)}),
                status_code=500,
                headers=get_cors_headers()
            )
    
    @app.route(route="onboarding/quiz/process", methods=["POST"])
    async def process_quiz_responses(req: func.HttpRequest) -> func.HttpResponse:
        """Process quiz responses and return personality recommendations"""
        try:
            # Parse request
            try:
                body = req.get_json()
            except ValueError:
                return func.HttpResponse(
                    json.dumps({"error": "Invalid JSON in request body"}),
                    status_code=400,
                    headers=get_cors_headers()
                )
            
            responses = body.get("responses", [])
            user_id = body.get("user_id")
            
            if not responses:
                return func.HttpResponse(
                    json.dumps({"error": "Quiz responses are required"}),
                    status_code=400,
                    headers=get_cors_headers()
                )
            
            from onboarding import get_quiz_service
            quiz_service = get_quiz_service()
            
            # Process responses
            result = quiz_service.process_quiz_responses(responses)
            
            return func.HttpResponse(
                json.dumps({
                    "success": True,
                    "result": result,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }),
                status_code=200,
                headers=get_cors_headers()
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to process quiz: {e}")
            return func.HttpResponse(
                json.dumps({"error": "Failed to process quiz responses", "details": str(e)}),
                status_code=500,
                headers=get_cors_headers()
            )
    
    @app.route(route="onboarding/state", methods=["GET"])
    async def get_onboarding_state(req: func.HttpRequest) -> func.HttpResponse:
        """Get current onboarding state for a user"""
        try:
            user_id = req.params.get("user_id")
            
            if not user_id:
                return func.HttpResponse(
                    json.dumps({"error": "user_id parameter is required"}),
                    status_code=400,
                    headers=get_cors_headers()
                )
            
            from onboarding import get_onboarding_service
            onboarding_service = get_onboarding_service()
            
            state = await onboarding_service.get_or_create_state(user_id)
            
            return func.HttpResponse(
                json.dumps({
                    "success": True,
                    "state": state,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }),
                status_code=200,
                headers=get_cors_headers()
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to get onboarding state: {e}")
            return func.HttpResponse(
                json.dumps({"error": "Failed to get onboarding state", "details": str(e)}),
                status_code=500,
                headers=get_cors_headers()
            )
    
    @app.route(route="onboarding/state/advance", methods=["POST"])
    async def advance_onboarding_step(req: func.HttpRequest) -> func.HttpResponse:
        """Advance to the next onboarding step"""
        try:
            try:
                body = req.get_json()
            except ValueError:
                return func.HttpResponse(
                    json.dumps({"error": "Invalid JSON in request body"}),
                    status_code=400,
                    headers=get_cors_headers()
                )
            
            user_id = body.get("user_id")
            
            if not user_id:
                return func.HttpResponse(
                    json.dumps({"error": "user_id is required"}),
                    status_code=400,
                    headers=get_cors_headers()
                )
            
            from onboarding import get_onboarding_service
            onboarding_service = get_onboarding_service()
            
            state = await onboarding_service.advance_step(user_id)
            
            return func.HttpResponse(
                json.dumps({
                    "success": True,
                    "state": state,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }),
                status_code=200,
                headers=get_cors_headers()
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to advance onboarding step: {e}")
            return func.HttpResponse(
                json.dumps({"error": "Failed to advance step", "details": str(e)}),
                status_code=500,
                headers=get_cors_headers()
            )
    
    @app.route(route="onboarding/quiz/response", methods=["POST"])
    async def record_quiz_response(req: func.HttpRequest) -> func.HttpResponse:
        """Record a single quiz response"""
        try:
            try:
                body = req.get_json()
            except ValueError:
                return func.HttpResponse(
                    json.dumps({"error": "Invalid JSON in request body"}),
                    status_code=400,
                    headers=get_cors_headers()
                )
            
            user_id = body.get("user_id")
            question_id = body.get("question_id")
            selected_option_id = body.get("selected_option_id")
            
            if not all([user_id, question_id, selected_option_id]):
                return func.HttpResponse(
                    json.dumps({"error": "user_id, question_id, and selected_option_id are required"}),
                    status_code=400,
                    headers=get_cors_headers()
                )
            
            from onboarding import get_onboarding_service
            onboarding_service = get_onboarding_service()
            
            state = await onboarding_service.record_quiz_response(
                user_id, question_id, selected_option_id
            )
            
            return func.HttpResponse(
                json.dumps({
                    "success": True,
                    "state": state,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }),
                status_code=200,
                headers=get_cors_headers()
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to record quiz response: {e}")
            return func.HttpResponse(
                json.dumps({"error": "Failed to record response", "details": str(e)}),
                status_code=500,
                headers=get_cors_headers()
            )
    
    @app.route(route="onboarding/complete", methods=["POST"])
    async def complete_onboarding(req: func.HttpRequest) -> func.HttpResponse:
        """Mark onboarding as complete"""
        try:
            try:
                body = req.get_json()
            except ValueError:
                return func.HttpResponse(
                    json.dumps({"error": "Invalid JSON in request body"}),
                    status_code=400,
                    headers=get_cors_headers()
                )
            
            user_id = body.get("user_id")
            
            if not user_id:
                return func.HttpResponse(
                    json.dumps({"error": "user_id is required"}),
                    status_code=400,
                    headers=get_cors_headers()
                )
            
            from onboarding import get_onboarding_service
            onboarding_service = get_onboarding_service()
            
            state = await onboarding_service.complete_onboarding(user_id)
            
            return func.HttpResponse(
                json.dumps({
                    "success": True,
                    "state": state,
                    "message": "🎉 Onboarding completed successfully!",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }),
                status_code=200,
                headers=get_cors_headers()
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to complete onboarding: {e}")
            return func.HttpResponse(
                json.dumps({"error": "Failed to complete onboarding", "details": str(e)}),
                status_code=500,
                headers=get_cors_headers()
            )
    
    @app.route(route="onboarding/skip", methods=["POST"])
    async def skip_onboarding(req: func.HttpRequest) -> func.HttpResponse:
        """Skip the onboarding flow"""
        try:
            try:
                body = req.get_json()
            except ValueError:
                return func.HttpResponse(
                    json.dumps({"error": "Invalid JSON in request body"}),
                    status_code=400,
                    headers=get_cors_headers()
                )
            
            user_id = body.get("user_id")
            
            if not user_id:
                return func.HttpResponse(
                    json.dumps({"error": "user_id is required"}),
                    status_code=400,
                    headers=get_cors_headers()
                )
            
            from onboarding import get_onboarding_service
            onboarding_service = get_onboarding_service()
            
            state = await onboarding_service.skip_onboarding(user_id)
            
            return func.HttpResponse(
                json.dumps({
                    "success": True,
                    "state": state,
                    "message": "Onboarding skipped. You can always restart it from settings.",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }),
                status_code=200,
                headers=get_cors_headers()
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to skip onboarding: {e}")
            return func.HttpResponse(
                json.dumps({"error": "Failed to skip onboarding", "details": str(e)}),
                status_code=500,
                headers=get_cors_headers()
            )
    
    logger.info("✅ Onboarding API routes registered successfully")
