import azure.functions as func
import json
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

def main(req: func.HttpRequest) -> func.HttpResponse:
    """Simple test endpoint to isolate issues"""
    try:
        logger.info('🧪 Simple test endpoint triggered.')
        
        # Basic request parsing
        try:
            req_body = req.get_json()
            if not req_body:
                req_body = {}
        except Exception as e:
            logger.warning(f"⚠️ Failed to parse request body: {e}")
            req_body = {}
        
        # Simple response
        response_data = {
            "status": "success",
            "message": "Simple test endpoint working",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "received_data": req_body
        }
        
        return func.HttpResponse(
            json.dumps(response_data, indent=2),
            status_code=200,
            headers={
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "https://vimarsh.vedmishra.com",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
                "Access-Control-Allow-Credentials": "true"
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Simple test endpoint error: {str(e)}")
        error_response = {
            "error": "Simple test error",
            "message": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        return func.HttpResponse(
            json.dumps(error_response),
            status_code=500,
            headers={
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "https://vimarsh.vedmishra.com",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
                "Access-Control-Allow-Credentials": "true"
            }
        )
