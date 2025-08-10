"""
Enhanced Azure Functions application for Vimarsh - Modular Architecture
Incorporates optimized services while maintaining reliable function registration.
"""

import azure.functions as func
import json
import logging
from datetime import datetime, timezone, timedelta
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
conversation_memory_service = None
personality_models_available = False
personality_service_available = False
memory_service_available = False

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
    from services.conversation_memory_service import ConversationMemoryService
    conversation_memory_service = ConversationMemoryService()
    memory_service_available = True
    logger.info("✅ Conversation memory service initialized")
except ImportError as e:
    logger.warning(f"⚠️ Conversation memory service not available: {e}")

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
async def admin_role_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Optimized admin role endpoint with caching for faster response"""
    try:
        # Import working auth service (from backup version)
        from auth.unified_auth_service import UnifiedAuthService
        from services.admin_service import AdminService
        
        # Add cache for role responses (5 minute TTL)
        cache_key = None
        cached_response = None
        
        logger.info("🔐 Admin role endpoint called")
        
        auth_service = UnifiedAuthService()
        authenticated_user = await auth_service.extract_user_from_request(req)
        
        if not authenticated_user:
            logger.warning("🚫 No authenticated user found")
            return func.HttpResponse(
                json.dumps({
                    "error": "Authentication required",
                    "message": "Valid access token must be provided",
                    "code": "UNAUTHORIZED"
                }),
                status_code=401,
                headers=get_cors_headers()
            )
        
        # Check cache first for faster response
        cache_key = f"admin_role_{authenticated_user.email}"
        try:
            import time
            # Simple in-memory cache (would use Redis in production)
            if not hasattr(admin_role_endpoint, '_cache'):
                admin_role_endpoint._cache = {}
            
            if cache_key in admin_role_endpoint._cache:
                cached_data, timestamp = admin_role_endpoint._cache[cache_key]
                # Use cache if less than 3 minutes old
                if time.time() - timestamp < 180:
                    logger.info(f"⚡ Using cached admin role for {authenticated_user.email}")
                    return func.HttpResponse(
                        json.dumps(cached_data),
                        status_code=200,
                        headers=get_cors_headers()
                    )
        except Exception as cache_error:
            logger.warning(f"Cache error: {cache_error}")
        
        logger.info(f"🔐 Admin role check for user: {authenticated_user.email}")
        
        # Use admin service if available, otherwise fallback to basic role check
        if admin_service:
            try:
                response_data = admin_service.get_user_role(user_email=authenticated_user.email)
                logger.info(f"✅ AdminService returned: {response_data}")
                # Add service status information
                response_data["service_status"] = {
                    "personality_models": personality_models_available,
                    "personality_service": personality_service_available,
                    "admin_service": True,
                    "architecture": "modular"
                }
                # Add authentication context
                response_data["auth_context"] = {
                    "source": "unified_auth_service",
                    "email": authenticated_user.email,
                    "authenticated": True,
                    "auth_mode": str(auth_service.mode),
                    "auth_enabled": auth_service.is_enabled
                }
                
                # Cache the successful response
                if cache_key:
                    try:
                        admin_role_endpoint._cache[cache_key] = (response_data, time.time())
                        logger.info(f"💾 Cached admin role for {authenticated_user.email}")
                    except Exception as cache_error:
                        logger.warning(f"Failed to cache: {cache_error}")
                        
            except Exception as admin_error:
                logger.error(f"❌ AdminService error: {admin_error}")
                # Fall back to environment variable check
                import os
                admin_emails = os.getenv('ADMIN_EMAILS', 'vedprakash.m@outlook.com').split(',')
                is_admin = authenticated_user.email.strip().lower() in [email.strip().lower() for email in admin_emails]
                
                response_data = {
                    "role": "admin" if is_admin else "user",
                    "permissions": ["read", "write", "admin"] if is_admin else ["read"],
                    "user_email": authenticated_user.email,
                    "user_id": authenticated_user.id,
                    "service_status": {
                        "personality_models": personality_models_available,
                        "personality_service": personality_service_available,
                        "admin_service": False,
                        "architecture": "modular"
                    },
                    "auth_context": {
                        "source": "unified_auth_service",
                        "email": authenticated_user.email,
                        "authenticated": True,
                        "auth_mode": str(auth_service.mode),
                        "auth_enabled": auth_service.is_enabled
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "warning": f"AdminService error: {admin_error} - using environment variable check"
                }
                logger.info(f"🔄 Fallback admin check result: {response_data}")
        else:
            # Fallback without admin service - check environment variables directly
            import os
            admin_emails = os.getenv('ADMIN_EMAILS', 'vedprakash.m@outlook.com').split(',')
            is_admin = authenticated_user.email.strip().lower() in [email.strip().lower() for email in admin_emails]
            
            logger.info(f"🔍 Environment variable admin check: admin_emails={admin_emails}, user_email={authenticated_user.email}, is_admin={is_admin}")
            
            response_data = {
                "role": "admin" if is_admin else "user",
                "permissions": ["read", "write", "admin"] if is_admin else ["read"],
                "user_email": authenticated_user.email,
                "user_id": authenticated_user.id,
                "service_status": {
                    "personality_models": personality_models_available,
                    "personality_service": personality_service_available,
                    "admin_service": False,
                    "architecture": "modular"
                },
                "auth_context": {
                    "source": "unified_auth_service",
                    "email": authenticated_user.email,
                    "authenticated": True,
                    "auth_mode": str(auth_service.mode),
                    "auth_enabled": auth_service.is_enabled
                },
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "warning": "Admin service unavailable - using environment variable check"
            }
            logger.info(f"🔄 Environment variable admin check result: {response_data}")
        
        # Cache the final response
        if cache_key and response_data:
            try:
                import time
                admin_role_endpoint._cache[cache_key] = (response_data, time.time())
                logger.info(f"💾 Cached admin role for {authenticated_user.email}")
            except Exception as cache_error:
                logger.warning(f"Failed to cache: {cache_error}")
        
        return func.HttpResponse(
            json.dumps(response_data),
            status_code=200,
            headers=get_cors_headers()
        )
    except Exception as e:
        logger.error(f"❌ Admin role error: {e}")
        logger.error(f"❌ Error details: {str(e)}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to get admin role", "details": str(e)}),
            status_code=500,
            headers=get_cors_headers()
        )

@app.route(route="vimarsh-admin/monitoring", methods=["GET"])
async def admin_monitoring_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Admin monitoring endpoint for system health and usage data"""
    try:
        from auth.unified_auth_service import UnifiedAuthService
        
        logger.info("📊 Admin monitoring endpoint called")
        
        auth_service = UnifiedAuthService()
        authenticated_user = await auth_service.extract_user_from_request(req)
        
        if not authenticated_user:
            return func.HttpResponse(
                json.dumps({"error": "Authentication required"}),
                status_code=401,
                headers=get_cors_headers()
            )
        
        # Use admin service if available
        if admin_service:
            monitoring_data = admin_service.get_usage_monitoring()
        else:
            # Fallback monitoring data
            monitoring_data = {
                "current_status": "healthy",
                "active_sessions": 0,
                "rate_limits": {
                    "requests_per_hour": 1000,
                    "current_usage": 0,
                    "percentage_used": 0.0
                },
                "performance": {
                    "avg_response_time_ms": 250,
                    "system_load": "low",
                    "memory_usage": "normal"
                },
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "service_version": "fallback_v1.0"
            }
        
        return func.HttpResponse(
            json.dumps(monitoring_data),
            status_code=200,
            headers=get_cors_headers()
        )
        
    except Exception as e:
        logger.error(f"❌ Admin monitoring error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to get monitoring data", "details": str(e)}),
            status_code=500,
            headers=get_cors_headers()
        )

@app.route(route="vimarsh-admin/dashboard", methods=["GET"])
async def admin_dashboard_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Admin dashboard endpoint for system statistics and analytics"""
    try:
        from auth.unified_auth_service import UnifiedAuthService
        
        logger.info("📊 Admin dashboard endpoint called")
        
        auth_service = UnifiedAuthService()
        authenticated_user = await auth_service.extract_user_from_request(req)
        
        if not authenticated_user:
            return func.HttpResponse(
                json.dumps({"error": "Authentication required"}),
                status_code=401,
                headers=get_cors_headers()
            )
        
        # Use admin service if available
        if admin_service:
            analytics_data = admin_service.get_admin_analytics(days=30)
        else:
            # Fallback analytics data with correct personality count
            analytics_data = {
                "period": {
                    "days": 30,
                    "start_date": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                    "end_date": datetime.now(timezone.utc).isoformat()
                },
                "user_metrics": {
                    "total_users": 0,  # Frontend expects total_users
                    "active_users": 0,  # Frontend expects active_users
                    "new_users": 0,
                    "returning_users": 0
                },
                "usage_metrics": {
                    "estimated_cost": 0.0,  # Frontend expects usage_metrics.estimated_cost
                    "total_tokens": 0,       # Frontend expects usage_metrics.total_tokens
                    "total_requests": 0      # Frontend expects usage_metrics.total_requests
                },
                "personality_metrics": {
                    "most_popular": "krishna",
                    "total_interactions": 0,
                    "avg_response_time": 0.0
                },
                "system_metrics": {
                    "total_requests": 0,
                    "error_rate": 0.0,
                    "uptime": "99.9%"
                },
                # Fix: Use correct personality count from FALLBACK_PERSONALITIES
                "content_metrics": {
                    "personalities": len(FALLBACK_PERSONALITIES),  # 12 personalities
                    "spiritual_texts": 343,
                    "total_content_chunks": 789
                },
                "status": "operational",  # Frontend checks this for system health
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "service_version": "fallback_v1.0"
            }
        
        return func.HttpResponse(
            json.dumps(analytics_data),
            status_code=200,
            headers=get_cors_headers()
        )
        
    except Exception as e:
        logger.error(f"❌ Admin dashboard error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to get dashboard data", "details": str(e)}),
            status_code=500,
            headers=get_cors_headers()
        )

@app.route(route="vimarsh-admin/cost-dashboard", methods=["GET"])
async def admin_cost_dashboard_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Admin cost dashboard endpoint (alias for dashboard with cost focus)"""
    try:
        from auth.unified_auth_service import UnifiedAuthService
        
        logger.info("💰 Admin cost dashboard endpoint called")
        
        auth_service = UnifiedAuthService()
        authenticated_user = await auth_service.extract_user_from_request(req)
        
        if not authenticated_user:
            return func.HttpResponse(
                json.dumps({"error": "Authentication required"}),
                status_code=401,
                headers=get_cors_headers()
            )
        
        # Use admin service if available
        if admin_service:
            analytics_data = admin_service.get_admin_analytics(days=30)
        else:
            # Fallback analytics data with cost focus
            analytics_data = {
                "period": {
                    "days": 30,
                    "start_date": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                    "end_date": datetime.now(timezone.utc).isoformat()
                },
                "cost_metrics": {
                    "total_cost_usd": 0.0,
                    "llm_cost_usd": 0.0,
                    "infrastructure_cost_usd": 0.0,
                    "cost_per_request": 0.0
                },
                "usage_metrics": {
                    "total_requests": 0,
                    "llm_requests": 0,
                    "template_requests": 0
                },
                "efficiency_metrics": {
                    "cost_efficiency": 100.0,
                    "cache_hit_rate": 0.0
                },
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "service_version": "fallback_v1.0"
            }
        
        return func.HttpResponse(
            json.dumps(analytics_data),
            status_code=200,
            headers=get_cors_headers()
        )
        
    except Exception as e:
        logger.error(f"❌ Admin cost dashboard error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to get cost dashboard data", "details": str(e)}),
            status_code=500,
            headers=get_cors_headers()
        )

@app.route(route="vimarsh-admin/users", methods=["GET"])
async def admin_users_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Admin users endpoint for user management data"""
    try:
        from auth.unified_auth_service import UnifiedAuthService
        
        logger.info("👥 Admin users endpoint called")
        
        auth_service = UnifiedAuthService()
        authenticated_user = await auth_service.extract_user_from_request(req)
        
        if not authenticated_user:
            return func.HttpResponse(
                json.dumps({"error": "Authentication required"}),
                status_code=401,
                headers=get_cors_headers()
            )
        
        # Fallback user data (would be populated from database in production)
        users_data = {
            "users": [
                {
                    "id": authenticated_user.id,
                    "email": authenticated_user.email,
                    "name": authenticated_user.name or "Admin User",
                    "role": "admin",
                    "last_login": datetime.now(timezone.utc).isoformat(),
                    "status": "active",
                    "total_conversations": 0
                }
            ],
            "total_users": 1,
            "active_users": 1,
            "admin_users": 1,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service_version": "fallback_v1.0"
        }
        
        return func.HttpResponse(
            json.dumps(users_data),
            status_code=200,
            headers=get_cors_headers()
        )
        
    except Exception as e:
        logger.error(f"❌ Admin users error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to get users data", "details": str(e)}),
            status_code=500,
            headers=get_cors_headers()
        )

# Import admin endpoints from dedicated modules
try:
    from admin.admin_endpoints import admin_cost_dashboard
    from admin.personality_endpoints import admin_personalities_management
    from admin.content_endpoints import admin_content_sources
    logger.info("✅ Admin endpoints imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Admin endpoints not available: {e}")

# Register admin endpoints
@app.route(route="vimarsh-admin/personalities", methods=["GET"])
async def admin_personalities_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Admin personality management endpoint - delegates to dedicated admin module"""
    try:
        # Delegate to the dedicated admin module
        if 'admin_personalities_management' in globals():
            return await admin_personalities_management(req)
        else:
            # Fallback implementation
            from auth.unified_auth_service import UnifiedAuthService
            
            auth_service = UnifiedAuthService()
            authenticated_user = await auth_service.extract_user_from_request(req)
            
            if not authenticated_user:
                return func.HttpResponse(
                    json.dumps({"error": "Authentication required"}),
                    status_code=401,
                    headers=get_cors_headers()
                )
            
            # Return all 12 personalities with management data
            detailed_personalities = []
            for pid, info in FALLBACK_PERSONALITIES.items():
                detailed_personalities.append({
                    "id": pid,
                    "name": info["name"],
                    "domain": info["domain"],
                    "description": info["description"],
                    "status": "active",
                    "last_updated": datetime.now(timezone.utc).isoformat(),
                    "usage_count": 0,
                    "content_sources": 1,
                    "response_quality": 85.0
                })
            
            personalities_data = {
                "personalities": detailed_personalities,
                "total_personalities": len(detailed_personalities),
                "active_personalities": len(detailed_personalities),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "service_version": "fallback_v1.0"
            }
            
            return func.HttpResponse(
                json.dumps(personalities_data),
                status_code=200,
                headers=get_cors_headers()
            )
            
    except Exception as e:
        logger.error(f"❌ Admin personalities error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to get personalities data", "details": str(e)}),
            status_code=500,
            headers=get_cors_headers()
        )

@app.route(route="vimarsh-admin/content-sources", methods=["GET"])
async def admin_content_sources_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Admin content sources endpoint - delegates to dedicated admin module"""
    try:
        # Delegate to the dedicated admin module
        if 'admin_content_sources' in globals():
            return await admin_content_sources(req)
        else:
            # Fallback implementation
            from auth.unified_auth_service import UnifiedAuthService
            
            auth_service = UnifiedAuthService()
            authenticated_user = await auth_service.extract_user_from_request(req)
            
            if not authenticated_user:
                return func.HttpResponse(
                    json.dumps({"error": "Authentication required"}),
                    status_code=401,
                    headers=get_cors_headers()
                )
            
            # Return content sources data matching the 12 personalities
            content_sources = []
            personality_content_map = {
                "krishna": {"name": "Bhagavad Gita", "chunks": 18, "size_mb": 2.5},
                "einstein": {"name": "Einstein's Relativity Papers", "chunks": 45, "size_mb": 8.2},
                "lincoln": {"name": "Lincoln's Speeches & Letters", "chunks": 32, "size_mb": 3.8},
                "marcus_aurelius": {"name": "Meditations", "chunks": 28, "size_mb": 1.9},
                "buddha": {"name": "Buddhist Sutras Collection", "chunks": 67, "size_mb": 12.4},
                "jesus": {"name": "The Four Gospels", "chunks": 52, "size_mb": 4.6},
                "rumi": {"name": "Rumi's Poetry Collection", "chunks": 89, "size_mb": 6.7},
                "lao_tzu": {"name": "Tao Te Ching", "chunks": 21, "size_mb": 1.2},
                "chanakya": {"name": "Chanakya's Arthashastra", "chunks": 78, "size_mb": 9.3},
                "confucius": {"name": "The Analects", "chunks": 35, "size_mb": 2.8},
                "newton": {"name": "Newton's Principia", "chunks": 156, "size_mb": 18.5},
                "tesla": {"name": "Tesla's Patents", "chunks": 203, "size_mb": 25.6}
            }
            
            for pid, content in personality_content_map.items():
                content_sources.append({
                    "id": f"{pid}_source",
                    "name": content["name"],
                    "personality_associations": [pid],
                    "chunks": content["chunks"],
                    "size_mb": content["size_mb"],
                    "status": "processed",
                    "last_updated": datetime.now(timezone.utc).isoformat()
                })
            
            content_data = {
                "content_sources": content_sources,
                "total_sources": len(content_sources),
                "total_chunks": sum(s["chunks"] for s in content_sources),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "service_version": "fallback_v1.0"
            }
            
            return func.HttpResponse(
                json.dumps(content_data),
                status_code=200,
                headers=get_cors_headers()
            )
            
    except Exception as e:
        logger.error(f"❌ Admin content sources error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to get content sources data", "details": str(e)}),
            status_code=500,
            headers=get_cors_headers()
        )

@app.route(route="vimarsh-admin/settings", methods=["GET"])
async def admin_settings_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Admin settings endpoint with real admin user information"""
    try:
        from auth.unified_auth_service import UnifiedAuthService
        
        logger.info("⚙️ Admin settings endpoint called")
        
        auth_service = UnifiedAuthService()
        authenticated_user = await auth_service.extract_user_from_request(req)
        
        if not authenticated_user:
            return func.HttpResponse(
                json.dumps({"error": "Authentication required"}),
                status_code=401,
                headers=get_cors_headers()
            )
        
        # Get real admin information
        admin_info = {
            "name": authenticated_user.name or "System Administrator",
            "email": authenticated_user.email,  # Real logged-in admin email
            "role": "super_admin",
            "permissions": ["User Management", "Content Management", "System Configuration", "Analytics"],
            "last_login": datetime.now(timezone.utc).isoformat(),
            "account_created": "2024-01-01T00:00:00Z",
            "two_factor_enabled": False
        }
        
        settings_data = {
            "administrator": admin_info,
            "system_configuration": {
                "application_name": "Vimarsh",
                "version": "2.0.0",
                "environment": "production",
                "total_personalities": len(FALLBACK_PERSONALITIES)
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service_version": "admin_v1.0"
        }
        
        return func.HttpResponse(
            json.dumps(settings_data),
            status_code=200,
            headers=get_cors_headers()
        )
        
    except Exception as e:
        logger.error(f"❌ Admin settings error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to get settings data", "details": str(e)}),
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
        user_id = query_data.get('user_id', 'anonymous')  # Add user_id for memory
        
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
        
        # Enhanced response generation with conversation memory
        conversation_context = ""
        conversation_id = None
        if memory_service_available:
            try:
                # Get or start conversation
                import asyncio
                loop = asyncio.new_event_loop()
                try:
                    asyncio.set_event_loop(loop)
                    conversation_id = loop.run_until_complete(
                        conversation_memory_service.start_conversation(
                            user_id=user_id,
                            personality_id=personality_id
                        )
                    )
                    
                    # Get conversation context
                    context_data = loop.run_until_complete(
                        conversation_memory_service.get_conversation_context(
                            conversation_id=conversation_id
                        )
                    )
                    
                    # Format recent messages as context
                    if hasattr(context_data, 'recent_messages') and context_data.recent_messages:
                        from models.conversation_models import MessageType
                        recent_msgs = []
                        for msg in context_data.recent_messages[-3:]:  # Last 3 messages for context
                            if msg.message_type == MessageType.USER_QUERY:
                                recent_msgs.append(f"Previous question: {msg.content}")
                            elif msg.message_type == MessageType.PERSONALITY_RESPONSE:
                                recent_msgs.append(f"My previous response: {msg.content[:200]}...")
                        conversation_context = "\n".join(recent_msgs)
                    
                    logger.info(f"🧠 Retrieved conversation context: {len(conversation_context)} chars")
                finally:
                    loop.close()
                    
            except Exception as memory_error:
                logger.warning(f"⚠️ Failed to retrieve conversation context: {memory_error}")
        
        # Generate response using available service with context
        if personality_service_available:
            # Enhance the user query with conversation context for better follow-up responses
            enhanced_query = user_query
            if conversation_context:
                enhanced_query = f"Previous conversation context:\n{conversation_context}\n\nCurrent question: {user_query}"
                logger.info(f"🔍 Enhanced query with context for better follow-up response")
            
            service_response = optimized_personality_service.generate_response(enhanced_query, personality_id, language)
            response_text = service_response["content"]
            response_metadata = service_response["metadata"]
            response_metadata["memory_enhanced"] = bool(conversation_context)
        else:
            # Fallback response generation
            fallback_responses = {
                "krishna": "Beloved devotee, in the Bhagavad Gita 2.47, I teach: \"You have the right to perform your prescribed duty, but not to the fruits of action.\" This timeless wisdom guides us to act with devotion while surrendering attachment to outcomes. Focus on righteous action with love and dedication. May you find peace in dharmic living. 🙏"
            }
            response_text = fallback_responses.get(personality_id, fallback_responses["krishna"])
            response_metadata = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "service_version": "fallback_v1.0",
                "response_source": "hardcoded_fallback",
                "memory_enhanced": False
            }
        
        # Store conversation in memory
        if memory_service_available and conversation_id:
            try:
                import asyncio
                loop = asyncio.new_event_loop()
                try:
                    asyncio.set_event_loop(loop)
                    # Store user message
                    loop.run_until_complete(
                        conversation_memory_service.add_message(
                            conversation_id=conversation_id,
                            user_id=user_id,
                            personality_id=personality_id,
                            message_type="user_query",
                            content=user_query
                        )
                    )
                    # Store personality response
                    loop.run_until_complete(
                        conversation_memory_service.add_message(
                            conversation_id=conversation_id,
                            user_id=user_id,
                            personality_id=personality_id,
                            message_type="personality_response",
                            content=response_text
                        )
                    )
                    logger.info(f"💾 Stored conversation exchange in memory")
                finally:
                    loop.close()
                    
            except Exception as store_error:
                logger.warning(f"⚠️ Failed to store conversation: {store_error}")
        
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
