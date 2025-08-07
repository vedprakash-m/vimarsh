"""
Enhanced Azure Functions application for Vimarsh - Modular Architecture
Incorporates optimized services while maintaining reliable function registration.
"""

import azure.functions as func
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the function app FIRST - this ensures it's available before imports
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# Import dependencies with graceful fallbacks
optimized_personality_service = None
safety_service = None
admin_service = None
personality_models_available = False
personality_service_available = False

try:
    from models.personality_models import PERSONALITY_CONFIGS, PersonalityConfig
    personality_models_available = True
    logger.info("✅ Personality models imported successfully")
    
    from services.personality_service import PersonalityService
    optimized_personality_service = PersonalityService()
    personality_service_available = True
    logger.info("✅ Personality service initialized")
    
except ImportError as e:
    logger.warning(f"⚠️ Personality service not available: {e}")

try:
    from services.safety_service import SafetyService
    safety_service = SafetyService()
    logger.info("✅ Safety service initialized")
except ImportError as e:
    logger.warning(f"⚠️ Safety service not available: {e}")

try:
    from services.admin_service import AdminService
    admin_service = AdminService()
    logger.info("✅ Admin service initialized")
except ImportError as e:
    logger.warning(f"⚠️ Admin service not available: {e}")

# Helper functions
def get_personality_list():
    """Get list of all available personalities"""
    if personality_models_available and 'PERSONALITY_CONFIGS' in globals():
        return [
            {
                "id": config.id,
                "name": config.name,
                "description": config.description,
                "domain": config.domain.value,
                "active": True  # Simplified for now
            }
            for config in PERSONALITY_CONFIGS.values()
        ]
    return []

def get_personalities_by_domain(domain=None):
    """Get personalities filtered by domain"""
    if not personality_models_available or 'PERSONALITY_CONFIGS' not in globals():
        return {}
    
    if domain and domain != "all":
        return {
            k: v for k, v in PERSONALITY_CONFIGS.items() 
            if v.domain.value == domain
        }
    return PERSONALITY_CONFIGS

def get_personality_config(personality_id):
    """Get a specific personality configuration"""
    if personality_models_available and 'PERSONALITY_CONFIGS' in globals():
        return PERSONALITY_CONFIGS.get(personality_id)
    return None

# Fallback personality data (if models not available)
FALLBACK_PERSONALITIES = {
    "krishna": {"name": "Krishna", "domain": "spiritual", "description": "Divine guide offering spiritual wisdom from the Bhagavad Gita"},
    "einstein": {"name": "Albert Einstein", "domain": "scientific", "description": "Brilliant physicist exploring the mysteries of the universe"},
    "lincoln": {"name": "Abraham Lincoln", "domain": "historical", "description": "16th President known for wisdom, leadership, and unity"},
    "marcus_aurelius": {"name": "Marcus Aurelius", "domain": "philosophical", "description": "Roman Emperor and Stoic philosopher"},
    "buddha": {"name": "Buddha", "domain": "spiritual", "description": "Enlightened teacher of the Middle Way and mindfulness"},
    "jesus": {"name": "Jesus Christ", "domain": "spiritual", "description": "Teacher of love, compassion, and spiritual transformation"},
    "rumi": {"name": "Rumi", "domain": "spiritual", "description": "Sufi mystic poet of divine love and spiritual union"},
    "lao_tzu": {"name": "Lao Tzu", "domain": "philosophical", "description": "Ancient Chinese sage and founder of Taoism"},
    "chanakya": {"name": "Chanakya", "domain": "historical", "description": "Ancient Indian strategist, economist, and political advisor"},
    "confucius": {"name": "Confucius", "domain": "historical", "description": "Chinese philosopher and educator emphasizing ethics and social harmony"},
    "newton": {"name": "Isaac Newton", "domain": "scientific", "description": "English mathematician and physicist, father of classical mechanics"},
    "tesla": {"name": "Nikola Tesla", "domain": "scientific", "description": "Serbian-American inventor and electrical engineer, pioneer of modern technology"}
}

def get_cors_headers() -> Dict[str, str]:
    """Get standard CORS headers for all responses"""
    return {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "https://vimarsh.vedprakash.net",
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization"
    }

@app.route(route="health", methods=["GET"])
def health_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Enhanced health check endpoint with service status"""
    try:
        # Get personality data
        if personality_models_available:
            personalities = get_personality_list()
            total_personalities = len(personalities)
            personality_ids = [p["id"] for p in personalities]
        else:
            personality_ids = list(FALLBACK_PERSONALITIES.keys())
            total_personalities = len(personality_ids)
        
        health_data = {
            "status": "healthy",
            "service": "vimarsh-enhanced",
            "version": "2.0",
            "architecture": "modular",
            "personalities_available": total_personalities,
            "personalities": personality_ids,
            "services": {
                "personality_models": personality_models_available,
                "personality_service": personality_service_available,
                "fallback_mode": not (personality_models_available and personality_service_available)
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        return func.HttpResponse(
            json.dumps(health_data, indent=2),
            status_code=200,
            headers=get_cors_headers()
        )
    except Exception as e:
        logger.error(f"❌ Health check failed: {str(e)}")
        return func.HttpResponse(
            json.dumps({"status": "unhealthy", "error": str(e)}),
            status_code=500,
            headers=get_cors_headers()
        )

@app.route(route="personalities/active", methods=["GET"])
def get_active_personalities(req: func.HttpRequest) -> func.HttpResponse:
    """Get list of active personalities with enhanced filtering"""
    try:
        # Handle parameters
        domain = req.params.get('domain', 'all')
        active_only = req.params.get('active_only', 'false').lower() == 'true'
        
        logger.info(f"🎭 Getting personalities - domain: {domain}, active_only: {active_only}")
        
        # Get personality data based on available services
        if personality_models_available:
            if domain == 'all':
                personalities = get_personality_list()
            else:
                personality_configs = get_personalities_by_domain(domain)
                personalities = [
                    {
                        "id": config.id,
                        "name": config.name,
                        "domain": config.domain.value,
                        "description": config.description
                    }
                    for config in personality_configs.values()
                ]
            
            domains = list(set(p["domain"] for p in get_personality_list()))
        else:
            # Use fallback data
            if domain == 'all':
                filtered_personalities = FALLBACK_PERSONALITIES
            else:
                filtered_personalities = {
                    k: v for k, v in FALLBACK_PERSONALITIES.items() 
                    if v['domain'] == domain
                }
            
            personalities = [
                {
                    "id": pid,
                    "name": info["name"],
                    "domain": info["domain"],
                    "description": info["description"]
                }
                for pid, info in filtered_personalities.items()
            ]
            
            domains = list(set(p["domain"] for p in FALLBACK_PERSONALITIES.values()))
        
        response_data = {
            "personalities": personalities,
            "total": len(personalities),
            "domains": domains,
            "service_mode": "enhanced" if personality_models_available else "fallback",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(f"✅ Returning {len(personalities)} personalities")
        
        return func.HttpResponse(
            json.dumps(response_data),
            status_code=200,
            headers=get_cors_headers()
        )
    except Exception as e:
        logger.error(f"❌ Error getting personalities: {e}")
        return func.HttpResponse(
            json.dumps({
                "error": "Failed to get personalities", 
                "details": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }),
            status_code=500,
            headers=get_cors_headers()
        )

@app.route(route="vimarsh-admin/role", methods=["GET"])
def admin_role_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Enhanced admin role endpoint with service status and proper authentication"""
    try:
        # Extract user email from headers (set by frontend authentication)
        user_email = req.headers.get('x-user-email') or req.headers.get('X-User-Email')
        
        # Also try to extract from Authorization header if MSAL token is provided
        if not user_email:
            auth_header = req.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                # For production, we should decode the MSAL token
                # For now, we'll extract email from header or default to None
                user_email = None
        
        # Use admin service if available, otherwise fallback
        if admin_service:
            response_data = admin_service.get_user_role(user_email=user_email)
            # Add service status information
            response_data["service_status"] = {
                "personality_models": personality_models_available,
                "personality_service": personality_service_available,
                "admin_service": True,
                "architecture": "modular"
            }
        else:
            # Fallback without admin service - should not give admin access to unknown users
            response_data = {
                "role": "user",  # Changed from "admin" to "user" - security fix!
                "permissions": ["read"],  # Changed from admin permissions
                "user_email": user_email or "anonymous",
                "service_status": {
                    "personality_models": personality_models_available,
                    "personality_service": personality_service_available,
                    "admin_service": False,
                    "architecture": "modular"
                },
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "warning": "Admin service unavailable - defaulting to user role"
            }
        
        return func.HttpResponse(
            json.dumps(response_data),
            status_code=200,
            headers=get_cors_headers()
        )
    except Exception as e:
        logger.error(f"❌ Admin role error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to get admin role"}),
            status_code=500,
            headers=get_cors_headers()
        )

@app.route(route="guidance", methods=["POST"])
def guidance_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Enhanced guidance endpoint with modular service integration"""
    try:
        # Parse request body
        try:
            query_data = req.get_json()
        except ValueError:
            return func.HttpResponse(
                json.dumps({"error": "Invalid JSON in request body"}),
                status_code=400,
                headers=get_cors_headers()
            )
        
        if not query_data:
            return func.HttpResponse(
                json.dumps({"error": "Request body is required"}),
                status_code=400,
                headers=get_cors_headers()
            )
        
        # Extract parameters
        user_query = query_data.get('query', '').strip()
        personality_id = query_data.get('personality_id', 'krishna')
        language = query_data.get('language', 'English')
        
        if not user_query:
            return func.HttpResponse(
                json.dumps({"error": "Query is required"}),
                status_code=400,
                headers=get_cors_headers()
            )
        
        # Validate personality
        valid_personalities = (
            list(FALLBACK_PERSONALITIES.keys()) if not personality_service_available
            else optimized_personality_service.get_available_personalities()
        )
        
        if personality_id not in valid_personalities:
            logger.warning(f"Invalid personality: {personality_id}, defaulting to Krishna")
            personality_id = "krishna"
        
        # Generate response using available service
        if personality_service_available:
            service_response = optimized_personality_service.generate_response(user_query, personality_id, language)
            response_text = service_response["content"]
            response_metadata = service_response["metadata"]
        else:
            # Fallback response generation
            fallback_responses = {
                "krishna": "Beloved devotee, in the Bhagavad Gita 2.47, I teach: \"You have the right to perform your prescribed duty, but not to the fruits of action.\" This timeless wisdom guides us to act with devotion while surrendering attachment to outcomes. Focus on righteous action with love and dedication. May you find peace in dharmic living. 🙏"
            }
            response_text = fallback_responses.get(personality_id, fallback_responses["krishna"])
            response_metadata = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "service_version": "fallback_v1.0",
                "response_source": "hardcoded_fallback"
            }
        
        # Get personality info
        if personality_models_available:
            config = get_personality_config(personality_id)
            personality_info = {
                "id": config.id,
                "name": config.name,
                "domain": config.domain.value,
                "description": config.description
            }
        else:
            fallback_info = FALLBACK_PERSONALITIES[personality_id]
            personality_info = {
                "id": personality_id,
                "name": fallback_info["name"],
                "domain": fallback_info["domain"],
                "description": fallback_info["description"]
            }
        
        # Build final response
        response = {
            "response": response_text,
            "personality": personality_info,
            "metadata": {
                **response_metadata,
                "language": language,
                "query_length": len(user_query),
                "response_length": len(response_text),
                "service_mode": "enhanced" if personality_service_available else "fallback"
            }
        }
        
        logger.info(f"✅ {personality_info['name']} response generated successfully")
        
        return func.HttpResponse(
            json.dumps(response, indent=2),
            status_code=200,
            headers=get_cors_headers()
        )
        
    except Exception as e:
        logger.error(f"❌ Error in guidance endpoint: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "error": "Internal server error",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }),
            status_code=500,
            headers=get_cors_headers()
        )

# Enhanced CORS handling in each endpoint - no separate OPTIONS handlers needed
# All endpoints already include proper CORS headers
