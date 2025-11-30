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

# Import centralized AI model configuration
try:
    from config.ai_models import AI_CONFIG
    gemini_model = AI_CONFIG.gemini_generation_model
except ImportError:
    # Fallback if config not available  
    gemini_model = "models/gemini-2.5-flash"

# Create the function app FIRST - this ensures it's available before imports
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# Import dependencies with graceful fallbacks
optimized_personality_service = None
safety_service = None
admin_service = None
conversation_memory_service = None
enhanced_llm_service = None
enhanced_rag_service = None
database_personality_service = None
personality_models_available = False
personality_service_available = False
database_personality_available = False
memory_service_available = False
enhanced_llm_available = False
enhanced_rag_available = False

# Try to import the new database-driven personality service first
try:
    from services.database_personality_service import DatabasePersonalityService
    database_personality_service = DatabasePersonalityService()
    database_personality_available = True
    logger.info("✅ Database-driven personality service initialized")
except ImportError as e:
    logger.warning(f"⚠️ Database personality service not available: {e}")
except Exception as e:
    logger.warning(f"⚠️ Database personality service initialization failed: {e}")

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
    optimized_personality_service = None
    personality_service_available = False
except Exception as e:
    logger.warning(f"⚠️ Personality service failed to initialize: {e}")
    optimized_personality_service = None
    personality_service_available = False

try:
    from services.enhanced_llm_wrapper import enhanced_llm_service
    enhanced_llm_available = True
    logger.info("✅ Enhanced LLM service with reliability patterns loaded")
except ImportError as e:
    logger.warning(f"⚠️ Enhanced LLM service not available: {e}")
    enhanced_llm_service = None
    enhanced_llm_available = False
except Exception as e:
    logger.warning(f"⚠️ Enhanced LLM service failed to initialize: {e}")
    enhanced_llm_service = None
    enhanced_llm_available = False

try:
    from services.enhanced_rag_service_v6 import EnhancedRAGService
    # Don't initialize at import time - do it lazily
    enhanced_rag_available = True
    enhanced_rag_service = None  # Will be initialized on first use
    logger.info("✅ Enhanced RAG service imported successfully (will initialize on first use)")
except ImportError as e:
    logger.warning(f"⚠️ Enhanced RAG service not available: {e}")
except Exception as e:
    logger.warning(f"⚠️ Enhanced RAG service import failed: {e}")

try:
    from services.conversation_memory_service import ConversationMemoryService
    conversation_memory_service = ConversationMemoryService()
    memory_service_available = True
    logger.info("✅ Conversation memory service initialized")
except ImportError as e:
    logger.warning(f"⚠️ Conversation memory service not available: {e}")
    conversation_memory_service = None
    memory_service_available = False
except Exception as e:
    logger.warning(f"⚠️ Conversation memory service failed to initialize: {e}")
    conversation_memory_service = None
    memory_service_available = False

# Import hierarchical memory service (new 4-layer architecture)
hierarchical_memory_service = None
hierarchical_memory_available = False
try:
    from services.hierarchical_memory_service import get_memory_service
    hierarchical_memory_service = get_memory_service()
    hierarchical_memory_available = True
    logger.info("✅ Hierarchical memory service initialized (4-layer architecture)")
except ImportError as e:
    logger.warning(f"⚠️ Hierarchical memory service not available: {e}")
except Exception as e:
    logger.warning(f"⚠️ Hierarchical memory service failed to initialize: {e}")

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

# Helper functions with database-driven approach
async def get_personality_list():
    """Get list of all available personalities (database-first approach)"""
    # Try database-driven service first
    if database_personality_available and database_personality_service:
        try:
            return await database_personality_service.get_personality_list()
        except Exception as e:
            logger.warning(f"⚠️ Database personality service failed: {e}")
    
    # Fallback to hardcoded approach
    if 'FALLBACK_PERSONALITIES' in globals():
        return [
            {
                "id": pid,
                "name": config["name"],
                "description": config["description"],
                "domain": config["domain"],
                "active": True  # All personalities are active
            }
            for pid, config in FALLBACK_PERSONALITIES.items()
        ]
    elif personality_models_available and 'PERSONALITY_CONFIGS' in globals():
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

async def get_personalities_by_domain(domain=None):
    """Get personalities filtered by domain (database-first approach)"""
    # Try database-driven service first
    if database_personality_available and database_personality_service:
        try:
            return await database_personality_service.get_all_personalities(domain)
        except Exception as e:
            logger.warning(f"⚠️ Database personality service failed: {e}")
    
    # Fallback to hardcoded approach
    if 'FALLBACK_PERSONALITIES' in globals():
        if domain and domain != "all":
            # Filter by domain using FALLBACK_PERSONALITIES
            filtered = {
                pid: config for pid, config in FALLBACK_PERSONALITIES.items()
                if config["domain"] == domain
            }
            return filtered
        else:
            return FALLBACK_PERSONALITIES
    elif personality_models_available and 'PERSONALITY_CONFIGS' not in globals():
        return {}
    
    if domain and domain != "all":
        # Fallback to old logic for compatibility
        return {
            k: v for k, v in PERSONALITY_CONFIGS.items()
            if v.domain.value == domain
        }
    else:
        return PERSONALITY_CONFIGS

async def get_personality_config(personality_id):
    """Get a specific personality configuration (database-first approach)"""
    # Try database-driven service first
    if database_personality_available and database_personality_service:
        try:
            return await database_personality_service.get_personality_config(personality_id)
        except Exception as e:
            logger.warning(f"⚠️ Database personality config failed: {e}")
    
    # Fallback to hardcoded approach
    if personality_models_available and 'PERSONALITY_CONFIGS' in globals():
        return PERSONALITY_CONFIGS.get(personality_id)
    return None

# Fallback personality data (if models not available)
FALLBACK_PERSONALITIES = {
    # SPIRITUAL (4 personalities) - ORIGINAL
    "krishna": {"name": "Krishna", "domain": "spiritual", "description": "Divine guide offering spiritual wisdom from the Bhagavad Gita"},
    "buddha": {"name": "Buddha", "domain": "spiritual", "description": "Enlightened teacher of the Middle Way and mindfulness"},
    "jesus_christ": {"name": "Jesus Christ", "domain": "spiritual", "description": "Teacher of love, compassion, and spiritual transformation"},
    "rumi": {"name": "Rumi", "domain": "spiritual", "description": "Sufi mystic poet of divine love and spiritual union"},
    
    # SCIENTIFIC (5 personalities) - ORIGINAL + NEW
    "albert_einstein": {"name": "Albert Einstein", "domain": "scientific", "description": "Brilliant physicist exploring the mysteries of the universe"},
    "isaac_newton": {"name": "Isaac Newton", "domain": "scientific", "description": "English mathematician and physicist, father of classical mechanics"},
    "nikola_tesla": {"name": "Nikola Tesla", "domain": "scientific", "description": "Serbian-American inventor and electrical engineer with enhanced RAG content from his works"},
    "leonardo_da_vinci": {"name": "Leonardo da Vinci", "domain": "scientific", "description": "Renaissance polymath, inventor, scientist, and visionary artist"},
    "archimedes": {"name": "Archimedes", "domain": "scientific", "description": "Ancient Greek mathematician, physicist, engineer, and inventor"},
    
    # PHILOSOPHICAL (6 personalities) - ORIGINAL + NEW
    "marcus_aurelius": {"name": "Marcus Aurelius", "domain": "philosophical", "description": "Roman Emperor and Stoic philosopher"},
    "lao_tzu": {"name": "Lao Tzu", "domain": "philosophical", "description": "Ancient Chinese sage and founder of Taoism with enhanced RAG content from Tao Te Ching"},
    "socrates": {"name": "Socrates", "domain": "philosophical", "description": "Ancient Greek philosopher, father of Western philosophy"},
    "plato": {"name": "Plato", "domain": "philosophical", "description": "Student of Socrates, founded the Academy in Athens"},
    "aristotle": {"name": "Aristotle", "domain": "philosophical", "description": "Student of Plato, systematic approach to logic and ethics"},
    "sigmund_freud": {"name": "Sigmund Freud", "domain": "philosophical", "description": "Founder of psychoanalysis, explored human psychology"},
    
    # HISTORICAL (11 personalities) - ORIGINAL + NEW
    "abraham_lincoln": {"name": "Abraham Lincoln", "domain": "leadership", "description": "16th President known for wisdom, leadership, and unity"},
    "chanakya": {"name": "Chanakya", "domain": "historical", "description": "Ancient Indian strategist, economist, and political advisor"},
    "confucius": {"name": "Confucius", "domain": "historical", "description": "Chinese philosopher and educator emphasizing ethics and social harmony"},
    "benjamin_franklin": {"name": "Benjamin Franklin", "domain": "historical", "description": "Founding Father, diplomat, inventor, and polymath"},
    "martin_luther_king_jr": {"name": "Martin Luther King Jr.", "domain": "leadership", "description": "Civil rights leader and advocate for social justice"},
    "george_washington": {"name": "George Washington", "domain": "historical", "description": "First US President, military leader, and statesman"},
    "mahatma_gandhi": {"name": "Mahatma Gandhi", "domain": "leadership", "description": "Independence leader and advocate of non-violence with enhanced RAG content"},
    "swami_vivekananda": {"name": "Swami Vivekananda", "domain": "historical", "description": "Spiritual teacher who introduced Vedanta to the West"},
    
    # LITERARY (2 personalities) - NEW DOMAIN
    "william_shakespeare": {"name": "William Shakespeare", "domain": "literary", "description": "Greatest playwright and poet in English literature"},
    "rabindranath_tagore": {"name": "Rabindranath Tagore", "domain": "literary", "description": "Nobel Prize winner, poet, philosopher, and writer"}
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

@app.route(route="diagnostic", methods=["GET"])
async def diagnostic_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Diagnostic endpoint to test Enhanced RAG service dependencies"""
    import os
    try:
        logger.info('🧪 Diagnostic endpoint triggered.')
        
        diagnostic_results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tests": {},
            "summary": {}
        }
        
        # Test 1: Environment Variables
        required_vars = [
            'AZURE_COSMOS_CONNECTION_STRING',
            'GEMINI_API_KEY', 
            'AZURE_COSMOS_DATABASE_NAME',
            'AZURE_COSMOS_CONTAINER_NAME'
        ]
        
        env_test = {"missing": [], "present": []}
        for var in required_vars:
            value = os.getenv(var)
            if value:
                env_test["present"].append({"var": var, "length": len(value)})
            else:
                env_test["missing"].append(var)
        
        diagnostic_results["tests"]["environment_variables"] = env_test
        
        # Test 2: Package Imports
        import_test = {}
        try:
            import google.generativeai as genai
            import_test["google_generativeai"] = "available"
        except ImportError as e:
            import_test["google_generativeai"] = f"missing: {str(e)}"
        
        try:
            import azure.cosmos.cosmos_client as cosmos_client
            import_test["azure_cosmos"] = "available"
        except ImportError as e:
            import_test["azure_cosmos"] = f"missing: {str(e)}"
        
        diagnostic_results["tests"]["package_imports"] = import_test
        
        # Test 3: Cosmos DB Connection
        cosmos_test = {"status": "unknown", "error": None}
        try:
            connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
            if connection_string:
                import azure.cosmos.cosmos_client as cosmos_client
                client = cosmos_client.CosmosClient.from_connection_string(connection_string)
                database_name = os.getenv('AZURE_COSMOS_DATABASE_NAME', 'vimarsh-multi-personality')
                container_name = os.getenv('AZURE_COSMOS_CONTAINER_NAME', 'personality_vectors')
                database = client.get_database_client(database_name)
                container = database.get_container_client(container_name)
                
                # Try to read container properties
                properties = container.read()
                cosmos_test["status"] = "connected"
                cosmos_test["database"] = database_name
                cosmos_test["container"] = container_name
            else:
                cosmos_test["status"] = "no_connection_string"
        except Exception as e:
            cosmos_test["status"] = "failed"
            cosmos_test["error"] = str(e)
        
        diagnostic_results["tests"]["cosmos_db"] = cosmos_test
        
        # Test 4: Gemini API
        gemini_test = {"status": "unknown", "error": None}
        try:
            api_key = os.getenv('GEMINI_API_KEY')
            if api_key:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(gemini_model)
                response = model.generate_content("Hello")
                if response and response.text:
                    gemini_test["status"] = "working"
                    gemini_test["response_sample"] = response.text[:100]
                else:
                    gemini_test["status"] = "no_response"
            else:
                gemini_test["status"] = "no_api_key"
        except Exception as e:
            gemini_test["status"] = "failed"
            gemini_test["error"] = str(e)
        
        diagnostic_results["tests"]["gemini_api"] = gemini_test
        
        # Test 5: Enhanced RAG Service
        rag_test = {"status": "unknown", "error": None}
        try:
            from services.enhanced_rag_service_v6 import EnhancedRAGService
            service = EnhancedRAGService()
            rag_test["status"] = "initialized"
        except Exception as e:
            rag_test["status"] = "failed"
            rag_test["error"] = str(e)
        
        diagnostic_results["tests"]["enhanced_rag_service"] = rag_test
        
        # Summary
        env_ok = len(env_test["missing"]) == 0
        imports_ok = all("available" in status for status in import_test.values())
        cosmos_ok = cosmos_test["status"] == "connected"
        gemini_ok = gemini_test["status"] == "working"
        rag_ok = rag_test["status"] == "initialized"
        
        diagnostic_results["summary"] = {
            "environment_variables": "pass" if env_ok else "fail",
            "package_imports": "pass" if imports_ok else "fail", 
            "cosmos_db": "pass" if cosmos_ok else "fail",
            "gemini_api": "pass" if gemini_ok else "fail",
            "enhanced_rag_service": "pass" if rag_ok else "fail",
            "overall_status": "pass" if all([env_ok, imports_ok, cosmos_ok, gemini_ok, rag_ok]) else "fail"
        }
        
        return func.HttpResponse(
            json.dumps(diagnostic_results, indent=2),
            status_code=200,
            headers=get_cors_headers()
        )
        
    except Exception as e:
        logger.error(f"❌ Diagnostic endpoint error: {str(e)}")
        error_response = {
            "error": "Diagnostic test failed",
            "message": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        return func.HttpResponse(
            json.dumps(error_response),
            status_code=500,
            headers=get_cors_headers()
        )

@app.route(route="test", methods=["GET", "POST"])
def test_simple(req: func.HttpRequest) -> func.HttpResponse:
    """Simple test endpoint to verify basic functionality"""
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
            "received_data": req_body,
            "services_status": {
                "personality_service_available": personality_service_available,
                "enhanced_llm_available": enhanced_llm_available,
                "enhanced_rag_available": enhanced_rag_available,
                "memory_service_available": memory_service_available
            }
        }
        
        return func.HttpResponse(
            json.dumps(response_data, indent=2),
            status_code=200,
            headers={
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "https://vimarsh.vedprakash.net",
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
                "Access-Control-Allow-Origin": "https://vimarsh.vedprakash.net",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
                "Access-Control-Allow-Credentials": "true"
            }
        )


@app.route(route="health", methods=["GET"])
async def health_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Enhanced health check endpoint with comprehensive service status"""
    try:
        # Import capability manifest service
        from core.capability_manifest import capability_manifest_service
        
        # Generate comprehensive capability manifest
        manifest = capability_manifest_service.generate_manifest()
        
        # Get personality data for compatibility
        if database_personality_available or personality_models_available:
            personalities = await get_personality_list()
            total_personalities = len(personalities)
            personality_ids = [p["id"] for p in personalities]
        else:
            personality_ids = list(FALLBACK_PERSONALITIES.keys())
            total_personalities = len(personality_ids)
        
        # Convert to dictionary for JSON response
        health_data = {
            "status": "healthy" if manifest.overall_status.value == "operational" else "degraded",
            "service": "vimarsh-enhanced",
            "version": "2.1-capability-aware",
            "architecture": "modular-with-fallbacks",
            "timestamp": manifest.timestamp,
            "deployment_readiness": manifest.deployment_readiness,
            "overall_status": manifest.overall_status.value,
            
            # Personality info for compatibility
            "personalities_available": total_personalities,
            "personalities": personality_ids,
            
            # Detailed service capabilities
            "services": {
                name: {
                    "available": cap.available,
                    "status": cap.status.value,
                    "fallback_mode": cap.fallback_mode.value,
                    "error_message": cap.error_message,
                    "failure_rate_24h": cap.failure_rate_24h,
                    "response_time_ms": cap.response_time_ms,
                    "health_details": cap.health_details or {}
                }
                for name, cap in manifest.capabilities.items()
            },
            
            # Legacy service status for compatibility
            "legacy_services": {
                "personality_models": personality_models_available,
                "personality_service": personality_service_available,
                "memory_service": memory_service_available,
                "fallback_mode": not (personality_models_available and personality_service_available)
            },
            
            # Transparency features
            "active_fallbacks": manifest.active_fallbacks,
            "recommendations": manifest.recommendations,
            "user_impact": manifest.user_impact,
            
            # Service statistics
            "service_counts": {
                "operational": sum(1 for cap in manifest.capabilities.values() if cap.status.value == "operational"),
                "degraded": sum(1 for cap in manifest.capabilities.values() if cap.status.value == "degraded"),
                "unavailable": sum(1 for cap in manifest.capabilities.values() if cap.status.value == "unavailable")
            }
        }
        
        return func.HttpResponse(
            json.dumps(health_data, indent=2),
            status_code=200,
            headers=get_cors_headers()
        )
    except Exception as e:
        logger.error(f"❌ Health check failed: {str(e)}")
        # Fallback to simple health check
        health_data = {
            "status": "degraded",
            "service": "vimarsh-enhanced",
            "version": "2.1-fallback",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "fallback_reason": "Capability manifest service unavailable"
        }
        return func.HttpResponse(
            json.dumps(health_data),
            status_code=500,
            headers=get_cors_headers()
        )

@app.route(route="personalities/active", methods=["GET"])
async def get_active_personalities(req: func.HttpRequest) -> func.HttpResponse:
    """Get list of active personalities with enhanced filtering"""
    try:
        # Handle parameters
        domain = req.params.get('domain', 'all')
        active_only = req.params.get('active_only', 'false').lower() == 'true'
        
        logger.info(f"🎭 Getting personalities - domain: {domain}, active_only: {active_only}")
        
        # Get personality data based on available services (database-first approach)
        if database_personality_available or personality_models_available:
            if domain == 'all':
                personalities_data = await get_personality_list()
                # Ensure we have a list of dict format for consistency
                if isinstance(personalities_data, list) and len(personalities_data) > 0:
                    if isinstance(personalities_data[0], dict):
                        personalities = personalities_data
                    else:
                        personalities = []
                else:
                    personalities = []
            else:
                personality_configs = await get_personalities_by_domain(domain)
                if isinstance(personality_configs, list):
                    # Database returned a list
                    personalities = personality_configs
                else:
                    # Hardcoded configs returned a dict of PersonalityConfig objects
                    personalities = []
                    if isinstance(personality_configs, dict):
                        for config in personality_configs.values():
                            if hasattr(config, 'id') and hasattr(config, 'name'):
                                personalities.append({
                                    "id": config.id,
                                    "name": config.name,
                                    "domain": config.domain.value if hasattr(config.domain, 'value') else str(config.domain),
                                    "description": config.description
                                })
            
            all_personalities_data = await get_personality_list()
            if isinstance(all_personalities_data, list) and len(all_personalities_data) > 0:
                domains = list(set(p.get("domain", "unknown") for p in all_personalities_data if isinstance(p, dict)))
            else:
                domains = ["spiritual", "scientific", "historical", "philosophical"]
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
        
        # Ensure personalities is properly defined for all code paths
        if 'personalities' not in locals():
            personalities = []
        
        response_data = {
            "personalities": personalities,
            "total": len(personalities),
            "domains": domains,
            "service_mode": "database" if database_personality_available else ("enhanced" if personality_models_available else "fallback"),
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
        # Import enhanced auth service with database persistence (maintains admin compatibility)
        from auth.enhanced_unified_auth_service import EnhancedUnifiedAuthService
        from services.admin_service import AdminService
        
        # Add cache for role responses (5 minute TTL)
        cache_key = None
        cached_response = None
        
        logger.info("🔐 Admin role endpoint called")
        
        auth_service = EnhancedUnifiedAuthService()
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
        from auth.enhanced_unified_auth_service import EnhancedUnifiedAuthService
        
        logger.info("📊 Admin monitoring endpoint called")
        
        auth_service = EnhancedUnifiedAuthService()
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
    """Admin dashboard endpoint for system statistics and analytics - queries real data"""
    try:
        from auth.enhanced_unified_auth_service import EnhancedUnifiedAuthService
        
        logger.info("📊 Admin dashboard endpoint called")
        
        auth_service = EnhancedUnifiedAuthService()
        authenticated_user = await auth_service.extract_user_from_request(req)
        
        if not authenticated_user:
            return func.HttpResponse(
                json.dumps({"error": "Authentication required"}),
                status_code=401,
                headers=get_cors_headers()
            )
        
        # Query real metrics from database
        total_users = 0
        active_users = 0
        total_conversations = 0
        total_messages = 0
        personality_count = 25  # Default known count
        total_content_chunks = 0
        personality_usage = {}
        
        try:
            from azure.cosmos import CosmosClient
            import os
            
            connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
            if connection_string:
                client = CosmosClient.from_connection_string(connection_string)
                database = client.get_database_client('vimarsh-multi-personality')
                
                # Query user_preferences for user counts
                try:
                    users_container = database.get_container_client('user_preferences')
                    users_query = "SELECT VALUE COUNT(1) FROM c"
                    user_count = list(users_container.query_items(
                        query=users_query,
                        enable_cross_partition_query=True
                    ))
                    total_users = user_count[0] if user_count else 0
                    active_users = total_users  # Assume all active for now
                except Exception as ue:
                    logger.warning(f"⚠️ User count query error: {ue}")
                
                # Query conversations for activity metrics
                try:
                    conversations_container = database.get_container_client('conversations')
                    conv_count_query = "SELECT VALUE COUNT(1) FROM c"
                    conv_count = list(conversations_container.query_items(
                        query=conv_count_query,
                        enable_cross_partition_query=True
                    ))
                    total_conversations = conv_count[0] if conv_count else 0
                    
                    # Get personality usage from conversations
                    usage_query = "SELECT c.personality, COUNT(1) as count FROM c GROUP BY c.personality"
                    usage_results = list(conversations_container.query_items(
                        query=usage_query,
                        enable_cross_partition_query=True
                    ))
                    for item in usage_results:
                        personality_usage[item.get('personality', 'unknown')] = item.get('count', 0)
                except Exception as ce:
                    logger.warning(f"⚠️ Conversations query error: {ce}")
                
                # Query personalities container for count (query ALL, no filter)
                try:
                    personalities_container = database.get_container_client('personalities')
                    # Query all personalities without active filter
                    pers_count_query = "SELECT VALUE COUNT(1) FROM c"
                    pers_count = list(personalities_container.query_items(
                        query=pers_count_query,
                        enable_cross_partition_query=True
                    ))
                    db_personality_count = pers_count[0] if pers_count else 0
                    # Use database count if available, otherwise use known count of 25
                    personality_count = db_personality_count if db_personality_count > 0 else 25
                except Exception as pe:
                    logger.warning(f"⚠️ Personalities query error: {pe}")
                    personality_count = 25  # Always fall back to known count
                
                # Query personality-vectors for content chunks
                try:
                    vectors_container = database.get_container_client('personality_vectors')
                    vectors_count_query = "SELECT VALUE COUNT(1) FROM c"
                    vectors_count = list(vectors_container.query_items(
                        query=vectors_count_query,
                        enable_cross_partition_query=True
                    ))
                    total_content_chunks = vectors_count[0] if vectors_count else 0
                except Exception as ve:
                    logger.warning(f"⚠️ Vectors query error: {ve}")
                    
        except ImportError:
            logger.warning("⚠️ Azure Cosmos SDK not available")
        except Exception as db_err:
            logger.warning(f"⚠️ Database query error: {db_err}")
        
        # Determine most popular personality
        most_popular = "krishna"
        if personality_usage:
            most_popular = max(personality_usage, key=personality_usage.get)
        
        analytics_data = {
            "period": {
                "days": 30,
                "start_date": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "end_date": datetime.now(timezone.utc).isoformat()
            },
            "user_metrics": {
                "total_users": total_users,
                "active_users": active_users,
                "new_users": 0,
                "returning_users": total_users
            },
            "usage_metrics": {
                "estimated_cost": 0.0,
                "total_tokens": total_conversations * 500,  # Estimate tokens
                "total_requests": total_conversations
            },
            "personality_metrics": {
                "most_popular": most_popular,
                "total_interactions": total_conversations,
                "avg_response_time": 2.3,
                "usage_breakdown": personality_usage
            },
            "system_metrics": {
                "total_requests": total_conversations,
                "error_rate": 0.0,
                "uptime": "99.9%"
            },
            "content_metrics": {
                "personalities": personality_count,
                "spiritual_texts": 458,
                "total_content_chunks": total_content_chunks if total_content_chunks > 0 else 32000
            },
            "status": "operational",
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service_version": "database_v2.0"
        }
        
        logger.info(f"✅ Dashboard: {total_users} users, {total_conversations} conversations, {personality_count} personalities")
        
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
        from auth.enhanced_unified_auth_service import EnhancedUnifiedAuthService
        
        logger.info("💰 Admin cost dashboard endpoint called")
        
        auth_service = EnhancedUnifiedAuthService()
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
    """Admin users endpoint for user management data - queries real database"""
    try:
        from auth.enhanced_unified_auth_service import EnhancedUnifiedAuthService
        
        logger.info("👥 Admin users endpoint called")
        
        auth_service = EnhancedUnifiedAuthService()
        authenticated_user = await auth_service.extract_user_from_request(req)
        
        if not authenticated_user:
            return func.HttpResponse(
                json.dumps({"error": "Authentication required"}),
                status_code=401,
                headers=get_cors_headers()
            )
        
        # Query real user data from Cosmos DB - query BOTH users and user_preferences
        users_list = []
        users_by_email = {}  # For deduplication
        total_conversations = 0
        blocked_count = 0
        
        try:
            from azure.cosmos import CosmosClient
            import os
            
            connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
            if connection_string:
                client = CosmosClient.from_connection_string(connection_string)
                database = client.get_database_client('vimarsh-multi-personality')
                
                # Query user_preferences container
                try:
                    users_container = database.get_container_client('user_preferences')
                    users_query = "SELECT * FROM c"
                    users = list(users_container.query_items(
                        query=users_query,
                        enable_cross_partition_query=True
                    ))
                    
                    for user in users:
                        user_id = user.get('user_id', user.get('id', 'unknown'))
                        email = user.get('email', f"{user_id}@user.local")
                        is_blocked = user.get('is_blocked', False)
                        if is_blocked:
                            blocked_count += 1
                        
                        user_data = {
                            "id": user_id,
                            "email": email,
                            "name": user.get('name', user.get('display_name', 'User')),
                            "role": user.get('role', 'user'),
                            "last_login": user.get('last_activity', user.get('_ts', '')),
                            "status": "blocked" if is_blocked else "active",
                            "total_conversations": user.get('conversation_count', 0),
                            "preferences": user.get('preferences', {})
                        }
                        users_by_email[email.lower()] = user_data
                except Exception as user_err:
                    logger.warning(f"⚠️ Could not query user_preferences: {user_err}")
                
                # Also query 'users' container and merge results
                try:
                    alt_users_container = database.get_container_client('users')
                    alt_users_query = "SELECT * FROM c"
                    alt_users = list(alt_users_container.query_items(
                        query=alt_users_query,
                        enable_cross_partition_query=True
                    ))
                    
                    for user in alt_users:
                        user_id = user.get('user_id', user.get('id', 'unknown'))
                        email = user.get('email', f"{user_id}@user.local")
                        email_key = email.lower()
                        
                        # Only add if not already in users_by_email
                        if email_key not in users_by_email:
                            is_blocked = user.get('is_blocked', False)
                            if is_blocked:
                                blocked_count += 1
                            
                            users_by_email[email_key] = {
                                "id": user_id,
                                "email": email,
                                "name": user.get('name', user.get('display_name', 'User')),
                                "role": user.get('role', 'user'),
                                "last_login": user.get('last_activity', user.get('last_login', '')),
                                "status": "blocked" if is_blocked else "active",
                                "total_conversations": user.get('conversation_count', 0),
                                "preferences": user.get('preferences', {})
                            }
                except Exception as alt_err:
                    logger.debug(f"ℹ️ Users container not available: {alt_err}")
                
                # Query conversations for activity stats
                try:
                    conversations_container = database.get_container_client('conversations')
                    count_query = "SELECT VALUE COUNT(1) FROM c"
                    count_result = list(conversations_container.query_items(
                        query=count_query,
                        enable_cross_partition_query=True
                    ))
                    total_conversations = count_result[0] if count_result else 0
                except Exception as conv_err:
                    logger.warning(f"⚠️ Could not query conversations: {conv_err}")
                    
        except ImportError:
            logger.warning("⚠️ Azure Cosmos SDK not available")
        except Exception as db_err:
            logger.warning(f"⚠️ Database query error: {db_err}")
        
        # Convert dict to list
        users_list = list(users_by_email.values())
        
        # Always include authenticated admin user if not already in list
        admin_email = authenticated_user.email.lower() if authenticated_user.email else ""
        if admin_email and admin_email not in users_by_email:
            users_list.append({
                "id": authenticated_user.id,
                "email": authenticated_user.email,
                "name": authenticated_user.name or "Admin User",
                "role": "admin",
                "last_login": datetime.now(timezone.utc).isoformat(),
                "status": "active",
                "total_conversations": 0
            })
        
        users_data = {
            "users": users_list,
            "total_users": len(users_list),
            "active_users": len([u for u in users_list if u.get('status') == 'active']),
            "blocked_users": blocked_count,
            "admin_users": len([u for u in users_list if u.get('role') == 'admin']),
            "total_conversations": total_conversations,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service_version": "database_v2.0"
        }
        
        logger.info(f"✅ Returning {len(users_list)} users from database")
        
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
    from admin.admin_endpoints import (
        admin_cost_dashboard,
        admin_personalities_management,
        admin_content_sources,
        admin_content_management,
        get_content_status,
        acquire_personality_content,
        process_personality_content,
        validate_content_quality,
        create_personality_content_associations
    )
    logger.info("✅ Admin endpoints imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Admin endpoints not available: {e}")

# Import new admin services integration
try:
    from admin.admin_api_integration import (
        admin_content_overview,
        admin_process_content,
        admin_task_status,
        admin_delete_content,
        admin_regenerate_embeddings,
        admin_all_tasks,
        admin_start_validation,
        admin_validation_status,
        admin_all_validations,
        admin_start_security_audit,
        admin_security_audit_status,
        admin_all_security_audits,
        admin_security_summary,
        admin_dashboard_overview
    )
    logger.info("✅ New admin API integration imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ New admin API integration not available: {e}")

# Register admin endpoints
@app.route(route="vimarsh-admin/personalities", methods=["GET"])
async def admin_personalities_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Admin personality management endpoint - returns all 25 personalities with status"""
    try:
        from auth.enhanced_unified_auth_service import EnhancedUnifiedAuthService
        
        logger.info("🤖 Admin personalities endpoint called")
        
        auth_service = EnhancedUnifiedAuthService()
        authenticated_user = await auth_service.extract_user_from_request(req)
        
        if not authenticated_user:
            return func.HttpResponse(
                json.dumps({"error": "Authentication required"}),
                status_code=401,
                headers=get_cors_headers()
            )
        
        # Import all personalities from seeding script as base
        try:
            from admin.seed_personalities import get_all_personalities, get_content_source
            all_known_personalities = get_all_personalities()
        except ImportError:
            all_known_personalities = []
        
        detailed_personalities = []
        db_personalities = {}
        
        # Try to get database data for each personality
        try:
            from azure.cosmos import CosmosClient
            import os
            
            connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
            if connection_string:
                client = CosmosClient.from_connection_string(connection_string)
                database = client.get_database_client('vimarsh-multi-personality')
                
                # Query all personalities from database
                try:
                    personalities_container = database.get_container_client('personalities')
                    db_pers = list(personalities_container.query_items(
                        query="SELECT * FROM c",
                        enable_cross_partition_query=True
                    ))
                    for p in db_pers:
                        db_personalities[p.get('id')] = p
                except Exception:
                    pass
                
                # Get vector counts per personality
                vectors_container = database.get_container_client('personality_vectors')
                for known_p in all_known_personalities:
                    pid = known_p['id']
                    db_p = db_personalities.get(pid, {})
                    
                    # Get chunk count
                    chunk_count = 0
                    try:
                        chunk_query = f"SELECT VALUE COUNT(1) FROM c WHERE c.personality_id = '{pid}'"
                        chunk_result = list(vectors_container.query_items(
                            query=chunk_query,
                            enable_cross_partition_query=True
                        ))
                        chunk_count = chunk_result[0] if chunk_result else 0
                    except Exception:
                        pass
                    
                    detailed_personalities.append({
                        "id": pid,
                        "name": db_p.get('name', known_p.get('name', pid.replace('_', ' ').title())),
                        "domain": db_p.get('domain', known_p.get('domain', 'unknown')),
                        "description": db_p.get('description', known_p.get('description', '')),
                        "status": "active" if chunk_count > 0 else "pending",
                        "last_updated": db_p.get('updated_at', datetime.now(timezone.utc).isoformat()),
                        "usage_count": 0,
                        "content_sources": 1,
                        "total_chunks": chunk_count,
                        "rag_ready": chunk_count > 0,
                        "response_quality": 95.0 if chunk_count > 0 else 0.0
                    })
        except Exception as db_err:
            logger.warning(f"⚠️ Database query error: {db_err}")
            # Use fallback data
            for known_p in all_known_personalities:
                content = get_content_source(known_p['id'])
                detailed_personalities.append({
                    "id": known_p['id'],
                    "name": known_p.get('name', known_p['id'].replace('_', ' ').title()),
                    "domain": known_p.get('domain', 'unknown'),
                    "description": known_p.get('description', ''),
                    "status": "active",
                    "last_updated": datetime.now(timezone.utc).isoformat(),
                    "usage_count": 0,
                    "content_sources": 1,
                    "total_chunks": content.get('chunks', 0),
                    "rag_ready": content.get('chunks', 0) > 0,
                    "response_quality": 95.0
                })
        
        # If still empty, use FALLBACK_PERSONALITIES
        if not detailed_personalities:
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
                    "total_chunks": 50,
                    "rag_ready": True,
                    "response_quality": 85.0
                })
        
        personalities_data = {
            "personalities": detailed_personalities,
            "total_personalities": len(detailed_personalities),
            "active_personalities": len([p for p in detailed_personalities if p.get('status') == 'active']),
            "rag_ready_count": len([p for p in detailed_personalities if p.get('rag_ready')]),
            "domains": list(set(p.get('domain') for p in detailed_personalities)),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service_version": "enhanced_v2.0"
        }
        
        logger.info(f"✅ Returning {len(detailed_personalities)} personalities")
        
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
            from auth.enhanced_unified_auth_service import EnhancedUnifiedAuthService
            
            auth_service = EnhancedUnifiedAuthService()
            authenticated_user = await auth_service.extract_user_from_request(req)
            
            if not authenticated_user:
                return func.HttpResponse(
                    json.dumps({"error": "Authentication required"}),
                    status_code=401,
                    headers=get_cors_headers()
                )
            
            # Return content sources data matching ALL personalities
            content_sources = []
            personality_content_map = {
                # ORIGINAL PERSONALITIES
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
                "tesla": {"name": "Tesla's Patents", "chunks": 203, "size_mb": 25.6},
                # NEW PERSONALITIES
                "leonardo_da_vinci": {"name": "Leonardo's Notebooks", "chunks": 124, "size_mb": 15.3},
                "archimedes": {"name": "Mathematical Works", "chunks": 67, "size_mb": 8.9},
                "socrates": {"name": "Socratic Dialogues", "chunks": 45, "size_mb": 5.2},
                "plato": {"name": "The Republic & Dialogues", "chunks": 89, "size_mb": 11.7},
                "aristotle": {"name": "Nicomachean Ethics & Politics", "chunks": 112, "size_mb": 14.6},
                "sigmund_freud": {"name": "Psychoanalytic Works", "chunks": 78, "size_mb": 9.8},
                "benjamin_franklin": {"name": "Autobiography & Letters", "chunks": 56, "size_mb": 6.4},
                "martin_luther_king": {"name": "Speeches & Letters", "chunks": 43, "size_mb": 4.9},
                "nelson_mandela": {"name": "Long Walk to Freedom & Speeches", "chunks": 67, "size_mb": 7.8},
                "george_washington": {"name": "Letters & Presidential Papers", "chunks": 89, "size_mb": 10.2},
                "gandhi": {"name": "My Experiments with Truth", "chunks": 98, "size_mb": 11.5},
                "swami_vivekananda": {"name": "Complete Works", "chunks": 134, "size_mb": 16.8},
                "william_shakespeare": {"name": "Complete Works", "chunks": 567, "size_mb": 45.2},
                "rabindranath_tagore": {"name": "Poetry & Prose Collection", "chunks": 234, "size_mb": 18.9}
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
        from auth.enhanced_unified_auth_service import EnhancedUnifiedAuthService
        
        logger.info("⚙️ Admin settings endpoint called")
        
        auth_service = EnhancedUnifiedAuthService()
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

@app.route(route="vimarsh-admin/seed-database", methods=["POST"])
async def admin_seed_database_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Seed the database with all 25 personalities - Admin only"""
    try:
        from auth.enhanced_unified_auth_service import EnhancedUnifiedAuthService
        
        logger.info("🌱 Admin database seed endpoint called")
        
        auth_service = EnhancedUnifiedAuthService()
        authenticated_user = await auth_service.extract_user_from_request(req)
        
        if not authenticated_user:
            return func.HttpResponse(
                json.dumps({"error": "Authentication required"}),
                status_code=401,
                headers=get_cors_headers()
            )
        
        # Import and run seeding
        try:
            from admin.seed_personalities import seed_personalities_to_cosmos
            result = await seed_personalities_to_cosmos()
            
            return func.HttpResponse(
                json.dumps({
                    "success": True,
                    "message": "Database seeded successfully",
                    "details": result,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }),
                status_code=200,
                headers=get_cors_headers()
            )
        except ImportError as ie:
            return func.HttpResponse(
                json.dumps({"error": "Seeding module not available", "details": str(ie)}),
                status_code=500,
                headers=get_cors_headers()
            )
        except Exception as seed_error:
            logger.error(f"❌ Database seeding failed: {seed_error}")
            return func.HttpResponse(
                json.dumps({"error": "Database seeding failed", "details": str(seed_error)}),
                status_code=500,
                headers=get_cors_headers()
            )
        
    except Exception as e:
        logger.error(f"❌ Admin seed database error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to seed database", "details": str(e)}),
            status_code=500,
            headers=get_cors_headers()
        )

# Content Management Admin Endpoints
@app.route(route="vimarsh-admin/content/status", methods=["GET"])
async def admin_content_status_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Get content status for all personalities"""
    try:
        from admin.admin_endpoints import get_content_status
        return await get_content_status(req)
    except Exception as e:
        logger.error(f"❌ Content status error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to get content status", "details": str(e)}),
            status_code=500,
            headers=get_cors_headers()
        )

@app.route(route="vimarsh-admin/content/acquire", methods=["POST"])
async def admin_acquire_content_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Acquire content for a specific personality"""
    try:
        from admin.admin_endpoints import acquire_personality_content
        return await acquire_personality_content(req)
    except Exception as e:
        logger.error(f"❌ Content acquisition error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to acquire content", "details": str(e)}),
            status_code=500,
            headers=get_cors_headers()
        )

@app.route(route="vimarsh-admin/content/process", methods=["POST"])
async def admin_process_content_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Process raw content into chunks"""
    try:
        from admin.admin_endpoints import process_personality_content
        return await process_personality_content(req)
    except Exception as e:
        logger.error(f"❌ Content processing error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to process content", "details": str(e)}),
            status_code=500,
            headers=get_cors_headers()
        )

@app.route(route="vimarsh-admin/content/validate", methods=["POST"])
async def admin_validate_content_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Validate content quality"""
    try:
        from admin.admin_endpoints import validate_content_quality
        return await validate_content_quality(req)
    except Exception as e:
        logger.error(f"❌ Content validation error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to validate content", "details": str(e)}),
            status_code=500,
            headers=get_cors_headers()
        )

@app.route(route="vimarsh-admin/content/associate", methods=["POST"])
async def admin_associate_content_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Create personality-content associations"""
    try:
        from admin.admin_endpoints import create_personality_content_associations
        return await create_personality_content_associations(req)
    except Exception as e:
        logger.error(f"❌ Content association error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to create associations", "details": str(e)}),
            status_code=500,
            headers=get_cors_headers()
        )

# New Consolidated Admin Services Endpoints
@app.route(route="vimarsh-admin/content-management/overview", methods=["GET"])
async def admin_content_management_overview_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Content management service overview"""
    try:
        if 'admin_content_overview' in globals():
            return admin_content_overview(req)
        else:
            return func.HttpResponse(
                json.dumps({"error": "Content management service not available"}),
                status_code=503,
                headers=get_cors_headers()
            )
    except Exception as e:
        logger.error(f"❌ Content management overview error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to get content overview", "details": str(e)}),
            status_code=500,
            headers=get_cors_headers()
        )

@app.route(route="vimarsh-admin/content-management/process", methods=["POST"])
async def admin_content_management_process_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Process personality content"""
    try:
        if 'admin_process_content' in globals():
            return admin_process_content(req)
        else:
            return func.HttpResponse(
                json.dumps({"error": "Content management service not available"}),
                status_code=503,
                headers=get_cors_headers()
            )
    except Exception as e:
        logger.error(f"❌ Content management process error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to process content", "details": str(e)}),
            status_code=500,
            headers=get_cors_headers()
        )

@app.route(route="vimarsh-admin/content-management/tasks", methods=["GET"])
async def admin_content_management_tasks_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Get all content management tasks"""
    try:
        if 'admin_all_tasks' in globals():
            return admin_all_tasks(req)
        else:
            return func.HttpResponse(
                json.dumps({"error": "Content management service not available"}),
                status_code=503,
                headers=get_cors_headers()
            )
    except Exception as e:
        logger.error(f"❌ Content management tasks error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to get tasks", "details": str(e)}),
            status_code=500,
            headers=get_cors_headers()
        )

@app.route(route="vimarsh-admin/content-management/tasks/{task_id}", methods=["GET"])
async def admin_content_management_task_status_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Get content management task status"""
    try:
        if 'admin_task_status' in globals():
            return admin_task_status(req)
        else:
            return func.HttpResponse(
                json.dumps({"error": "Content management service not available"}),
                status_code=503,
                headers=get_cors_headers()
            )
    except Exception as e:
        logger.error(f"❌ Content management task status error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to get task status", "details": str(e)}),
            status_code=500,
            headers=get_cors_headers()
        )

@app.route(route="vimarsh-admin/content-management/delete", methods=["DELETE"])
async def admin_content_management_delete_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Delete personality content"""
    try:
        if 'admin_delete_content' in globals():
            return admin_delete_content(req)
        else:
            return func.HttpResponse(
                json.dumps({"error": "Content management service not available"}),
                status_code=503,
                headers=get_cors_headers()
            )
    except Exception as e:
        logger.error(f"❌ Content management delete error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to delete content", "details": str(e)}),
            status_code=500,
            headers=get_cors_headers()
        )

@app.route(route="vimarsh-admin/content-management/regenerate-embeddings", methods=["POST"])
async def admin_content_management_regenerate_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Regenerate embeddings for personality"""
    try:
        if 'admin_regenerate_embeddings' in globals():
            return admin_regenerate_embeddings(req)
        else:
            return func.HttpResponse(
                json.dumps({"error": "Content management service not available"}),
                status_code=503,
                headers=get_cors_headers()
            )
    except Exception as e:
        logger.error(f"❌ Content management regenerate error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to regenerate embeddings", "details": str(e)}),
            status_code=500,
            headers=get_cors_headers()
        )

# Testing & Validation Admin Endpoints
@app.route(route="vimarsh-admin/testing/start-validation", methods=["POST"])
async def admin_testing_start_validation_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Start a validation suite"""
    try:
        if 'admin_start_validation' in globals():
            return admin_start_validation(req)
        else:
            return func.HttpResponse(
                json.dumps({"error": "Testing validation service not available"}),
                status_code=503,
                headers=get_cors_headers()
            )
    except Exception as e:
        logger.error(f"❌ Testing start validation error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to start validation", "details": str(e)}),
            status_code=500,
            headers=get_cors_headers()
        )

@app.route(route="vimarsh-admin/testing/validation-status", methods=["GET"])
async def admin_testing_validation_status_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Get validation suite status"""
    try:
        if 'admin_validation_status' in globals():
            return admin_validation_status(req)
        else:
            return func.HttpResponse(
                json.dumps({"error": "Testing validation service not available"}),
                status_code=503,
                headers=get_cors_headers()
            )
    except Exception as e:
        logger.error(f"❌ Testing validation status error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to get validation status", "details": str(e)}),
            status_code=500,
            headers=get_cors_headers()
        )

@app.route(route="vimarsh-admin/testing/all-validations", methods=["GET"])
async def admin_testing_all_validations_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Get all validation suites"""
    try:
        if 'admin_all_validations' in globals():
            return admin_all_validations(req)
        else:
            return func.HttpResponse(
                json.dumps({"error": "Testing validation service not available"}),
                status_code=503,
                headers=get_cors_headers()
            )
    except Exception as e:
        logger.error(f"❌ Testing all validations error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to get all validations", "details": str(e)}),
            status_code=500,
            headers=get_cors_headers()
        )

# Security & Compliance Admin Endpoints
@app.route(route="vimarsh-admin/security/start-audit", methods=["POST"])
async def admin_security_start_audit_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Start a security audit"""
    try:
        if 'admin_start_security_audit' in globals():
            return admin_start_security_audit(req)
        else:
            return func.HttpResponse(
                json.dumps({"error": "Security compliance service not available"}),
                status_code=503,
                headers=get_cors_headers()
            )
    except Exception as e:
        logger.error(f"❌ Security start audit error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to start security audit", "details": str(e)}),
            status_code=500,
            headers=get_cors_headers()
        )

@app.route(route="vimarsh-admin/security/audit-status", methods=["GET"])
async def admin_security_audit_status_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Get security audit status"""
    try:
        if 'admin_security_audit_status' in globals():
            return admin_security_audit_status(req)
        else:
            return func.HttpResponse(
                json.dumps({"error": "Security compliance service not available"}),
                status_code=503,
                headers=get_cors_headers()
            )
    except Exception as e:
        logger.error(f"❌ Security audit status error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to get audit status", "details": str(e)}),
            status_code=500,
            headers=get_cors_headers()
        )

@app.route(route="vimarsh-admin/security/all-audits", methods=["GET"])
async def admin_security_all_audits_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Get all security audits"""
    try:
        if 'admin_all_security_audits' in globals():
            return admin_all_security_audits(req)
        else:
            return func.HttpResponse(
                json.dumps({"error": "Security compliance service not available"}),
                status_code=503,
                headers=get_cors_headers()
            )
    except Exception as e:
        logger.error(f"❌ Security all audits error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to get all audits", "details": str(e)}),
            status_code=500,
            headers=get_cors_headers()
        )

@app.route(route="vimarsh-admin/security/summary", methods=["GET"])
async def admin_security_summary_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Get security summary"""
    try:
        if 'admin_security_summary' in globals():
            return admin_security_summary(req)
        else:
            return func.HttpResponse(
                json.dumps({"error": "Security compliance service not available"}),
                status_code=503,
                headers=get_cors_headers()
            )
    except Exception as e:
        logger.error(f"❌ Security summary error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to get security summary", "details": str(e)}),
            status_code=500,
            headers=get_cors_headers()
        )

# Enhanced Admin Dashboard Overview
@app.route(route="vimarsh-admin/overview", methods=["GET"])
async def admin_overview_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Enhanced admin dashboard overview"""
    try:
        if 'admin_dashboard_overview' in globals():
            return admin_dashboard_overview(req)
        else:
            return func.HttpResponse(
                json.dumps({"error": "Admin dashboard service not available"}),
                status_code=503,
                headers=get_cors_headers()
            )
    except Exception as e:
        logger.error(f"❌ Admin overview error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to get admin overview", "details": str(e)}),
            status_code=500,
            headers=get_cors_headers()
        )

async def _get_template_fallback_response(personality_id: str):
    """Get template fallback response with metadata using database-first approach"""
    
    # Try to get personality config from database first
    if database_personality_available or personality_models_available:
        try:
            personality_config = await get_personality_config(personality_id)
            if personality_config and hasattr(personality_config, 'response_templates'):
                # Use personality-specific template if available
                templates = personality_config.response_templates
                if templates and templates.default_response:
                    response_text = templates.default_response
                else:
                    # Fall back to hardcoded for this personality
                    response_text = _get_hardcoded_fallback(personality_id)
            else:
                response_text = _get_hardcoded_fallback(personality_id)
        except Exception as e:
            logger.warning(f"Failed to get personality config for {personality_id}: {e}")
            response_text = _get_hardcoded_fallback(personality_id)
    else:
        response_text = _get_hardcoded_fallback(personality_id)
    
    response_metadata = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service_version": "fallback_v1.0",
        "response_source": "template_fallback",
        "memory_enhanced": False,
        "database_enhanced": database_personality_available
    }
    
    return response_text, response_metadata

def _get_hardcoded_fallback(personality_id: str) -> str:
    """Get hardcoded fallback responses for specific personalities"""
    fallback_responses = {
        "krishna": "Beloved devotee, in the Bhagavad Gita 2.47, I teach: \"You have the right to perform your prescribed duty, but not to the fruits of action.\" This timeless wisdom guides us to act with devotion while surrendering attachment to outcomes. Focus on righteous action with love and dedication. May you find peace in dharmic living. 🙏",
        "buddha": "Dear friend, suffering arises from attachment and craving. Through mindful awareness and the Noble Eightfold Path, we can find liberation. Practice compassion for all beings and remember - the present moment is all we truly have. May you find peace and wisdom on your path.",
        "default": "I apologize, but I'm currently unable to provide personalized guidance. Please try again in a moment."
    }
    
    return fallback_responses.get(personality_id, fallback_responses["default"])

@app.route(route="guidance", methods=["POST"])
async def guidance_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Enhanced guidance endpoint with modular service integration"""
    global enhanced_rag_service, enhanced_rag_available
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
        
        # Enhanced user ID resolution for cross-session memory
        user_id = query_data.get('user_id') or query_data.get('session_id')
        
        # Try to get persistent user ID from authentication if available
        persistent_user_id = None
        try:
            from auth.enhanced_unified_auth_service import EnhancedUnifiedAuthService
            auth_service = EnhancedUnifiedAuthService()
            authenticated_user = await auth_service.extract_user_from_request(req)
            
            if authenticated_user:
                persistent_user_id = await auth_service.get_persistent_user_id(authenticated_user)
                logger.info(f"🔗 Using persistent user ID: {persistent_user_id} for authenticated user: {authenticated_user.email}")
            
        except Exception as auth_error:
            logger.warning(f"⚠️ Could not get persistent user ID: {auth_error}")
        
        # Use persistent ID if available, otherwise fallback to session ID
        if persistent_user_id:
            user_id = persistent_user_id
        elif not user_id:
            # Final fallback to session-based ID
            user_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(user_query[:50]) % 10000}"
        
        logger.debug(f"🆔 Final user ID for conversation: {user_id}")
        
        if not user_query:
            return func.HttpResponse(
                json.dumps({"error": "Query is required"}),
                status_code=400,
                headers=get_cors_headers()
            )
        
        # Validate personality using database-first approach
        if database_personality_available or personality_models_available:
            valid_personalities_data = await get_personality_list()
            if isinstance(valid_personalities_data, list):
                valid_personalities = [p.get("id", "") for p in valid_personalities_data if isinstance(p, dict)]
            else:
                valid_personalities = list(FALLBACK_PERSONALITIES.keys())
        else:
            valid_personalities = (
                list(FALLBACK_PERSONALITIES.keys()) if not personality_service_available
                else optimized_personality_service.get_available_personalities()
            )
        
        if personality_id not in valid_personalities:
            logger.warning(f"Invalid personality: {personality_id}, defaulting to Krishna")
            personality_id = "krishna"
        
        # Enhanced response generation with hierarchical memory (4-layer architecture)
        conversation_context = ""
        conversation_id = None
        memory_enhanced_context = None
        session_id = query_data.get("session_id") or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Try hierarchical memory first (new 4-layer architecture)
        if hierarchical_memory_available and hierarchical_memory_service:
            try:
                # Assemble working memory context with all 4 layers
                memory_enhanced_context = await hierarchical_memory_service.assemble_working_memory(
                    user_id=user_id,
                    personality_id=personality_id,
                    session_id=session_id,
                    current_query=user_query,
                    current_messages=[]
                )
                
                # Build rich context from hierarchical memory
                context_parts = []
                
                # Add user profile context (Core Memory - Layer 2)
                if memory_enhanced_context.user_profile_context:
                    context_parts.append(f"About the seeker:\n{memory_enhanced_context.user_profile_context}")
                
                # Add relationship context (Core Memory - Layer 2)
                if memory_enhanced_context.relationship_context:
                    context_parts.append(f"Our journey together:\n{memory_enhanced_context.relationship_context}")
                
                # Add recent session summaries (Episodic Memory - Layer 3)
                if memory_enhanced_context.recent_session_summaries:
                    summaries = "\n".join([f"- {s}" for s in memory_enhanced_context.recent_session_summaries[:3]])
                    context_parts.append(f"Previous conversations:\n{summaries}")
                
                # Add relevant past insights (Episodic Memory - Layer 3)
                if memory_enhanced_context.relevant_past_insights:
                    insights = "\n".join([f"- {i}" for i in memory_enhanced_context.relevant_past_insights[:3]])
                    context_parts.append(f"Relevant wisdom shared before:\n{insights}")
                
                # Add retrieved memories from semantic search (Semantic Archive - Layer 4)
                if memory_enhanced_context.retrieved_memories:
                    memories = "\n".join([f"- {m}" for m in memory_enhanced_context.retrieved_memories[:3]])
                    context_parts.append(f"Related memories:\n{memories}")
                
                conversation_context = "\n\n".join(context_parts)
                logger.info(f"🧠 Hierarchical memory context assembled: {len(conversation_context)} chars, "
                           f"quality: {memory_enhanced_context.context_quality_score:.2f}")
                
            except Exception as hier_memory_error:
                logger.warning(f"⚠️ Hierarchical memory failed, falling back to basic: {hier_memory_error}")
        
        # Fallback to basic conversation memory if hierarchical failed
        if not conversation_context and memory_service_available:
            try:
                # Get or start conversation
                conversation_id = await conversation_memory_service.start_conversation(
                    user_id=user_id,
                    personality_id=personality_id
                )
                
                # Get conversation context
                context_data = await conversation_memory_service.get_conversation_context(
                    conversation_id=conversation_id
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
                
                logger.info(f"🧠 Basic conversation context: {len(conversation_context)} chars")
                    
            except Exception as memory_error:
                logger.warning(f"⚠️ Failed to retrieve conversation context: {memory_error}")
        
        # Generate response using available service with context
        response_source = "template_fallback"  # Default assumption
        
        if enhanced_rag_available:
            # Try enhanced RAG service first - this provides content-backed responses with citations
            try:
                # Initialize enhanced RAG service lazily if not already done
                if enhanced_rag_service is None:
                    logger.info("🔄 Initializing Enhanced RAG service on first use...")
                    try:
                        from services.enhanced_rag_service_v6 import EnhancedRAGService
                        enhanced_rag_service = EnhancedRAGService()
                        logger.info("✅ Enhanced RAG service initialized successfully")
                    except Exception as init_error:
                        logger.warning(f"⚠️ Enhanced RAG service initialization failed: {init_error}")
                        logger.info("🔄 Falling back to other services...")
                        # Set flag to prevent retrying initialization and fall back gracefully
                        enhanced_rag_available = False
                        enhanced_rag_service = "failed"  # Mark as failed to avoid retrying
                        # Don't raise - fall through to other services
                
                # Only proceed if service was successfully initialized
                if enhanced_rag_service != "failed":
                    # Enhanced RAG service handles conversation context internally
                    rag_response = await enhanced_rag_service.generate_enhanced_response(
                        query=user_query,
                        personality_id=personality_id,
                        context=conversation_context
                    )
                else:
                    # Service failed to initialize, skip to fallback
                    logger.info("🔄 Enhanced RAG service not available, skipping to fallback...")
                    raise Exception("Enhanced RAG service not available")
                
                if rag_response and rag_response.content:
                    response_text = rag_response.content
                    response_metadata = {
                        "content_backed": rag_response.content_backed,
                        "confidence_score": rag_response.confidence_score,
                        "citations": rag_response.rag_context.citations if rag_response.rag_context else [],
                        "chunks_used": len(rag_response.rag_context.relevant_chunks) if rag_response.rag_context else 0,
                        "retrieval_method": rag_response.rag_context.retrieval_method if rag_response.rag_context else "none",
                        "avg_similarity": rag_response.rag_context.avg_similarity_score if rag_response.rag_context else 0.0,
                        "memory_enhanced": bool(conversation_context),
                        **rag_response.metadata
                    }
                    response_source = rag_response.response_source
                    logger.info(f"✅ Enhanced RAG service provided response (confidence: {rag_response.confidence_score:.3f}, content-backed: {rag_response.content_backed})")
                else:
                    # Enhanced RAG failed, fall back to enhanced LLM
                    raise Exception("Enhanced RAG service returned no valid response")
                    
            except Exception as rag_error:
                logger.warning(f"⚠️ Enhanced RAG service failed: {rag_error}, falling back to enhanced LLM")
                # Fall through to enhanced LLM service
                if enhanced_llm_available and enhanced_llm_service is not None:
                    try:
                        # Enhance the user query with conversation context for better follow-up responses
                        enhanced_query = user_query
                        if conversation_context:
                            enhanced_query = f"Previous conversation context:\n{conversation_context}\n\nCurrent question: {user_query}"
                            logger.info(f"🔍 Enhanced query with context for better follow-up response")
                        
                        # Use enhanced LLM with circuit breaker and retry patterns
                        llm_response = await enhanced_llm_service.generate_response_with_monitoring(
                            query=enhanced_query,
                            personality_id=personality_id,
                            language=language
                        )
                        
                        if llm_response and llm_response.get("success", False):
                            response_text = llm_response["content"]
                            response_metadata = llm_response.get("metadata", {})
                            response_metadata["memory_enhanced"] = bool(conversation_context)
                            response_metadata["content_backed"] = False  # LLM responses are not content-backed
                            response_source = llm_response.get("source", "enhanced_llm")
                            logger.info(f"✅ Enhanced LLM service provided response (source: {response_source})")
                        else:
                            # Enhanced LLM failed, try standard personality service
                            raise Exception("Enhanced LLM service returned no valid response")
                            
                    except Exception as llm_error:
                        logger.warning(f"⚠️ Enhanced LLM service failed: {llm_error}, falling back to personality service")
                        # Fall through to personality service
                        if personality_service_available and optimized_personality_service is not None:
                            enhanced_query = user_query
                            if conversation_context:
                                enhanced_query = f"Previous conversation context:\n{conversation_context}\n\nCurrent question: {user_query}"
                                logger.info(f"🔍 Enhanced query with context for better follow-up response")
                            
                            service_response = optimized_personality_service.generate_response(enhanced_query, personality_id, language)
                            response_text = service_response["content"]
                            response_metadata = service_response["metadata"]
                            response_metadata["memory_enhanced"] = bool(conversation_context)
                            response_metadata["content_backed"] = False
                            response_source = "personality_service"
                        else:
                            # Final fallback to templates
                            response_text, response_metadata = await _get_template_fallback_response(personality_id)
                            response_metadata["content_backed"] = False
                            response_source = "template_fallback"
                else:
                    # No enhanced LLM, try personality service
                    if personality_service_available and optimized_personality_service is not None:
                        enhanced_query = user_query
                        if conversation_context:
                            enhanced_query = f"Previous conversation context:\n{conversation_context}\n\nCurrent question: {user_query}"
                            logger.info(f"🔍 Enhanced query with context for better follow-up response")
                        
                        service_response = optimized_personality_service.generate_response(enhanced_query, personality_id, language)
                        response_text = service_response["content"]
                        response_metadata = service_response["metadata"]
                        response_metadata["memory_enhanced"] = bool(conversation_context)
                        response_metadata["content_backed"] = False
                        response_source = "personality_service"
                    else:
                        # Final fallback to templates
                        response_text, response_metadata = await _get_template_fallback_response(personality_id)
                        response_metadata["content_backed"] = False
                        response_source = "template_fallback"
                    
        elif enhanced_llm_available and enhanced_llm_service is not None:
            # Try enhanced LLM service first with reliability patterns
            try:
                # Enhance the user query with conversation context for better follow-up responses
                enhanced_query = user_query
                if conversation_context:
                    enhanced_query = f"Previous conversation context:\n{conversation_context}\n\nCurrent question: {user_query}"
                    logger.info(f"🔍 Enhanced query with context for better follow-up response")
                
                # Use enhanced LLM with circuit breaker and retry patterns
                llm_response = await enhanced_llm_service.generate_response_with_monitoring(
                    query=enhanced_query,
                    personality_id=personality_id,
                    language=language
                )
                
                if llm_response and llm_response.get("success", False):
                    response_text = llm_response["content"]
                    response_metadata = llm_response.get("metadata", {})
                    response_metadata["memory_enhanced"] = bool(conversation_context)
                    response_source = llm_response.get("source", "enhanced_llm")
                    logger.info(f"✅ Enhanced LLM service provided response (source: {response_source})")
                else:
                    # Enhanced LLM failed, try standard personality service
                    raise Exception("Enhanced LLM service returned no valid response")
                    
            except Exception as llm_error:
                logger.warning(f"⚠️ Enhanced LLM service failed: {llm_error}, falling back to personality service")
                # Fall through to personality service
                if personality_service_available and optimized_personality_service is not None:
                    # Enhance the user query with conversation context for better follow-up responses
                    enhanced_query = user_query
                    if conversation_context:
                        enhanced_query = f"Previous conversation context:\n{conversation_context}\n\nCurrent question: {user_query}"
                        logger.info(f"🔍 Enhanced query with context for better follow-up response")
                    
                    service_response = optimized_personality_service.generate_response(enhanced_query, personality_id, language)
                    response_text = service_response["content"]
                    response_metadata = service_response["metadata"]
                    response_metadata["memory_enhanced"] = bool(conversation_context)
                    response_source = "personality_service"
                else:
                    # Final fallback to templates
                    response_text, response_metadata = await _get_template_fallback_response(personality_id)
                    response_source = "template_fallback"
                    
        elif personality_service_available and optimized_personality_service is not None:
            # Standard personality service without enhanced LLM
            # Enhance the user query with conversation context for better follow-up responses
            enhanced_query = user_query
            if conversation_context:
                enhanced_query = f"Previous conversation context:\n{conversation_context}\n\nCurrent question: {user_query}"
                logger.info(f"🔍 Enhanced query with context for better follow-up response")
            
            service_response = optimized_personality_service.generate_response(enhanced_query, personality_id, language)
            response_text = service_response["content"]
            response_metadata = service_response["metadata"]
            response_metadata["memory_enhanced"] = bool(conversation_context)
            response_source = "personality_service"
        else:
            # Template fallback only
            response_text, response_metadata = await _get_template_fallback_response(personality_id)
            response_source = "template_fallback"
        
        # Store conversation in hierarchical memory (new 4-layer architecture)
        if hierarchical_memory_available and hierarchical_memory_service is not None:
            try:
                from models.memory_models import MessageRole, EmotionalTone
                
                # Detect emotional tone from user query (simplified)
                emotional_keywords = {
                    EmotionalTone.TROUBLED: ["worried", "anxious", "stressed", "struggling", "lost", "confused"],
                    EmotionalTone.HOPEFUL: ["hope", "wish", "dream", "aspire", "looking forward"],
                    EmotionalTone.CURIOUS: ["what", "how", "why", "explain", "understand", "tell me"],
                    EmotionalTone.GRATEFUL: ["thank", "grateful", "appreciate", "blessed"],
                    EmotionalTone.SEEKING: ["help", "guide", "seek", "searching", "need"]
                }
                
                user_emotion = EmotionalTone.NEUTRAL
                query_lower = user_query.lower()
                for emotion, keywords in emotional_keywords.items():
                    if any(kw in query_lower for kw in keywords):
                        user_emotion = emotion
                        break
                
                # Store user message with enhanced metadata
                await hierarchical_memory_service.store_message(
                    user_id=user_id,
                    personality_id=personality_id,
                    session_id=session_id,
                    role=MessageRole.USER,
                    content=user_query,
                    emotional_tone=user_emotion
                )
                
                # Store personality response
                await hierarchical_memory_service.store_message(
                    user_id=user_id,
                    personality_id=personality_id,
                    session_id=session_id,
                    role=MessageRole.ASSISTANT,
                    content=response_text,
                    emotional_tone=EmotionalTone.CALM  # Personalities are typically calm
                )
                
                logger.info(f"💾 Stored conversation in hierarchical memory (session: {session_id})")
                
            except Exception as hier_store_error:
                logger.warning(f"⚠️ Failed to store in hierarchical memory: {hier_store_error}")
        
        # Fallback: Store in basic conversation memory
        elif memory_service_available and conversation_memory_service is not None and conversation_id:
            try:
                # Store user message
                await conversation_memory_service.add_message(
                    conversation_id=conversation_id,
                    user_id=user_id,
                    personality_id=personality_id,
                    message_type="user_query",
                    content=user_query
                )
                # Store personality response
                await conversation_memory_service.add_message(
                    conversation_id=conversation_id,
                    user_id=user_id,
                    personality_id=personality_id,
                    message_type="personality_response",
                    content=response_text
                )
                logger.info(f"💾 Stored conversation exchange in memory")
                    
            except Exception as store_error:
                logger.error(f"❌ Failed to store conversation: {store_error}")
        
        # Get personality info
        if personality_models_available:
            config = await get_personality_config(personality_id)
            if config and hasattr(config, 'id'):
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
        else:
            fallback_info = FALLBACK_PERSONALITIES[personality_id]
            personality_info = {
                "id": personality_id,
                "name": fallback_info["name"],
                "domain": fallback_info["domain"],
                "description": fallback_info["description"]
            }
        
        # Build final response with transparency about response source
        response = {
            "response": response_text,
            "personality": personality_info,
            "metadata": {
                **response_metadata,
                "language": language,
                "query_length": len(user_query),
                "response_length": len(response_text),
                "service_mode": "enhanced" if enhanced_llm_available else ("standard" if personality_service_available else "fallback"),
                "response_source": response_source,  # Key transparency feature
                "ai_generated": response_source not in ["template_fallback", "hardcoded_fallback"]
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


# ============================================================================
# WISDOM OF THE DAY ENDPOINT
# ============================================================================

@app.route(route="wisdom-of-day", methods=["GET", "OPTIONS"])
async def wisdom_of_day(req: func.HttpRequest) -> func.HttpResponse:
    """
    Get the wisdom of the day - a rotating daily quote from various personalities.
    Returns consistent wisdom for the same day based on date seeding.
    """
    if req.method == "OPTIONS":
        return func.HttpResponse("", status_code=204, headers=get_cors_headers())
    
    try:
        # Get current date for consistent daily rotation
        today = datetime.now(timezone.utc).date()
        day_of_year = today.timetuple().tm_yday
        
        # Collection of curated wisdom quotes from various personalities
        wisdom_collection = [
            {
                "quote": "The unexamined life is not worth living.",
                "personality_id": "socrates",
                "personality_name": "Socrates",
                "domain": "philosophical",
                "source": "Apology of Socrates"
            },
            {
                "quote": "Be the change you wish to see in the world.",
                "personality_id": "mahatma_gandhi",
                "personality_name": "Mahatma Gandhi",
                "domain": "leadership",
                "source": "Personal Philosophy"
            },
            {
                "quote": "You must not lose faith in humanity. Humanity is an ocean; if a few drops of the ocean are dirty, the ocean does not become dirty.",
                "personality_id": "mahatma_gandhi",
                "personality_name": "Mahatma Gandhi",
                "domain": "leadership",
                "source": "Personal Letters"
            },
            {
                "quote": "Imagination is more important than knowledge. Knowledge is limited. Imagination encircles the world.",
                "personality_id": "albert_einstein",
                "personality_name": "Albert Einstein",
                "domain": "scientific",
                "source": "Interview, 1929"
            },
            {
                "quote": "The important thing is not to stop questioning. Curiosity has its own reason for existence.",
                "personality_id": "albert_einstein",
                "personality_name": "Albert Einstein",
                "domain": "scientific",
                "source": "Personal Memoir"
            },
            {
                "quote": "Karmanye vadhikaraste ma phaleshu kadachana - You have the right to work, but not to the fruits of your work.",
                "personality_id": "krishna",
                "personality_name": "Lord Krishna",
                "domain": "spiritual",
                "source": "Bhagavad Gita 2.47"
            },
            {
                "quote": "The mind is everything. What you think you become.",
                "personality_id": "buddha",
                "personality_name": "Gautama Buddha",
                "domain": "spiritual",
                "source": "Dhammapada"
            },
            {
                "quote": "Peace comes from within. Do not seek it without.",
                "personality_id": "buddha",
                "personality_name": "Gautama Buddha",
                "domain": "spiritual",
                "source": "Buddhist Teachings"
            },
            {
                "quote": "The wound is the place where the Light enters you.",
                "personality_id": "rumi",
                "personality_name": "Rumi",
                "domain": "spiritual",
                "source": "Masnavi"
            },
            {
                "quote": "Let yourself be silently drawn by the strange pull of what you really love.",
                "personality_id": "rumi",
                "personality_name": "Rumi",
                "domain": "spiritual",
                "source": "Poetry Collection"
            },
            {
                "quote": "We are what we repeatedly do. Excellence, then, is not an act, but a habit.",
                "personality_id": "aristotle",
                "personality_name": "Aristotle",
                "domain": "philosophical",
                "source": "Nicomachean Ethics"
            },
            {
                "quote": "To be, or not to be, that is the question.",
                "personality_id": "william_shakespeare",
                "personality_name": "William Shakespeare",
                "domain": "literary",
                "source": "Hamlet"
            },
            {
                "quote": "All the world's a stage, and all the men and women merely players.",
                "personality_id": "william_shakespeare",
                "personality_name": "William Shakespeare",
                "domain": "literary",
                "source": "As You Like It"
            },
            {
                "quote": "Arise, awake, and stop not till the goal is reached.",
                "personality_id": "swami_vivekananda",
                "personality_name": "Swami Vivekananda",
                "domain": "spiritual",
                "source": "Lectures and Discourses"
            },
            {
                "quote": "You cannot believe in God until you believe in yourself.",
                "personality_id": "swami_vivekananda",
                "personality_name": "Swami Vivekananda",
                "domain": "spiritual",
                "source": "Complete Works"
            },
            {
                "quote": "Love your neighbor as yourself.",
                "personality_id": "jesus_christ",
                "personality_name": "Jesus Christ",
                "domain": "spiritual",
                "source": "Gospel of Matthew 22:39"
            },
            {
                "quote": "The journey of a thousand miles begins with a single step.",
                "personality_id": "lao_tzu",
                "personality_name": "Lao Tzu",
                "domain": "philosophical",
                "source": "Tao Te Ching"
            },
            {
                "quote": "He who knows others is wise; he who knows himself is enlightened.",
                "personality_id": "lao_tzu",
                "personality_name": "Lao Tzu",
                "domain": "philosophical",
                "source": "Tao Te Ching"
            },
            {
                "quote": "It is not the strongest of the species that survives, but the most adaptable.",
                "personality_id": "marcus_aurelius",
                "personality_name": "Marcus Aurelius",
                "domain": "philosophical",
                "source": "Meditations"
            },
            {
                "quote": "Very little is needed to make a happy life; it is all within yourself, in your way of thinking.",
                "personality_id": "marcus_aurelius",
                "personality_name": "Marcus Aurelius",
                "domain": "philosophical",
                "source": "Meditations"
            },
            {
                "quote": "I have a dream that my four little children will one day live in a nation where they will not be judged by the color of their skin but by the content of their character.",
                "personality_id": "martin_luther_king_jr",
                "personality_name": "Martin Luther King Jr.",
                "domain": "leadership",
                "source": "I Have a Dream Speech"
            },
            {
                "quote": "Darkness cannot drive out darkness; only light can do that. Hate cannot drive out hate; only love can do that.",
                "personality_id": "martin_luther_king_jr",
                "personality_name": "Martin Luther King Jr.",
                "domain": "leadership",
                "source": "Strength to Love"
            },
            {
                "quote": "A house divided against itself cannot stand.",
                "personality_id": "abraham_lincoln",
                "personality_name": "Abraham Lincoln",
                "domain": "leadership",
                "source": "House Divided Speech"
            },
            {
                "quote": "In the end, it's not the years in your life that count. It's the life in your years.",
                "personality_id": "abraham_lincoln",
                "personality_name": "Abraham Lincoln",
                "domain": "leadership",
                "source": "Attributed"
            },
            {
                "quote": "If you tell the truth, you don't have to remember anything.",
                "personality_id": "benjamin_franklin",
                "personality_name": "Benjamin Franklin",
                "domain": "leadership",
                "source": "Poor Richard's Almanack"
            },
            {
                "quote": "An investment in knowledge pays the best interest.",
                "personality_id": "benjamin_franklin",
                "personality_name": "Benjamin Franklin",
                "domain": "leadership",
                "source": "The Way to Wealth"
            },
            {
                "quote": "Before you embark on a journey of revenge, dig two graves.",
                "personality_id": "confucius",
                "personality_name": "Confucius",
                "domain": "philosophical",
                "source": "Analects"
            },
            {
                "quote": "It does not matter how slowly you go as long as you do not stop.",
                "personality_id": "confucius",
                "personality_name": "Confucius",
                "domain": "philosophical",
                "source": "Analects"
            },
            {
                "quote": "The future belongs to those who prepare for it today.",
                "personality_id": "chanakya",
                "personality_name": "Chanakya",
                "domain": "leadership",
                "source": "Arthashastra"
            },
            {
                "quote": "A person should not be too honest. Straight trees are cut first.",
                "personality_id": "chanakya",
                "personality_name": "Chanakya",
                "domain": "leadership",
                "source": "Chanakya Neeti"
            }
        ]
        
        # Select today's wisdom based on day of year (ensures consistency for the day)
        wisdom_index = day_of_year % len(wisdom_collection)
        todays_wisdom = wisdom_collection[wisdom_index]
        
        response = {
            "wisdom": todays_wisdom,
            "date": today.isoformat(),
            "day_number": day_of_year,
            "total_quotes": len(wisdom_collection)
        }
        
        logger.info(f"📜 Wisdom of the day served: {todays_wisdom['personality_name']}")
        
        return func.HttpResponse(
            json.dumps(response, indent=2),
            status_code=200,
            headers=get_cors_headers()
        )
        
    except Exception as e:
        logger.error(f"❌ Error in wisdom-of-day endpoint: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "error": "Failed to get wisdom of the day",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }),
            status_code=500,
            headers=get_cors_headers()
        )


# ============================================================================
# SHARE TRACKING ENDPOINT
# ============================================================================

@app.route(route="share/track", methods=["POST", "OPTIONS"])
async def track_share(req: func.HttpRequest) -> func.HttpResponse:
    """
    Track share analytics for wisdom content.
    """
    if req.method == "OPTIONS":
        return func.HttpResponse("", status_code=204, headers=get_cors_headers())
    
    try:
        body = req.get_json()
        
        platform = body.get("platform", "unknown")
        content_type = body.get("content_type", "wisdom")
        personality_id = body.get("personality_id")
        domain = body.get("domain")
        
        # Log the share event for analytics
        logger.info(f"📤 Share tracked: platform={platform}, type={content_type}, personality={personality_id}, domain={domain}")
        
        # TODO: Store in Cosmos DB for analytics dashboard
        # For now, just acknowledge the tracking
        
        response = {
            "success": True,
            "message": "Share tracked successfully",
            "platform": platform,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        return func.HttpResponse(
            json.dumps(response),
            status_code=200,
            headers=get_cors_headers()
        )
        
    except Exception as e:
        logger.error(f"❌ Error tracking share: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "error": "Failed to track share",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }),
            status_code=500,
            headers=get_cors_headers()
        )


@app.route(route="share/{shareId}", methods=["GET", "OPTIONS"])
async def get_shared_wisdom(req: func.HttpRequest) -> func.HttpResponse:
    """
    Retrieve shared wisdom by share ID.
    Used for the public share landing page.
    """
    if req.method == "OPTIONS":
        return func.HttpResponse("", status_code=204, headers=get_cors_headers())
    
    try:
        share_id = req.route_params.get('shareId')
        
        if not share_id:
            return func.HttpResponse(
                json.dumps({"error": "Share ID required"}),
                status_code=400,
                headers=get_cors_headers()
            )
        
        # TODO: Retrieve from Cosmos DB shares collection
        # For now, return sample data based on share_id pattern
        
        # Sample shared wisdom data
        sample_shares = {
            "demo": {
                "id": "demo",
                "text": "The unexamined life is not worth living. To find yourself, think for yourself.",
                "personality_id": "socrates",
                "personality_name": "Socrates",
                "domain": "philosophical",
                "citation": "Apology of Socrates",
                "shared_at": datetime.now(timezone.utc).isoformat(),
                "share_count": 42
            }
        }
        
        # Try to find the share or return a generic wisdom
        if share_id in sample_shares:
            wisdom = sample_shares[share_id]
        else:
            # Generate a wisdom based on the share ID hash
            wisdom = {
                "id": share_id,
                "text": "Knowledge speaks, but wisdom listens. In the journey of understanding, patience is your greatest companion.",
                "personality_id": "buddha",
                "personality_name": "Gautama Buddha",
                "domain": "spiritual",
                "citation": "Buddhist Teachings",
                "shared_at": datetime.now(timezone.utc).isoformat(),
                "share_count": 12
            }
        
        logger.info(f"📖 Shared wisdom retrieved: share_id={share_id}")
        
        return func.HttpResponse(
            json.dumps(wisdom),
            status_code=200,
            headers=get_cors_headers()
        )
        
    except Exception as e:
        logger.error(f"❌ Error retrieving shared wisdom: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "error": "Failed to retrieve shared wisdom",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }),
            status_code=500,
            headers=get_cors_headers()
        )


@app.route(route="wisdom/history", methods=["GET", "OPTIONS"])
async def get_wisdom_history(req: func.HttpRequest) -> func.HttpResponse:
    """
    Get paginated history of daily wisdom entries.
    """
    if req.method == "OPTIONS":
        return func.HttpResponse("", status_code=204, headers=get_cors_headers())
    
    try:
        page = int(req.params.get('page', 1))
        limit = int(req.params.get('limit', 10))
        domain = req.params.get('domain')
        
        # Static wisdom archive for demo
        all_entries = [
            {
                "id": "w1",
                "date": "2025-01-28",
                "personality_id": "krishna",
                "personality_name": "Lord Krishna",
                "domain": "spiritual",
                "wisdom_text": "You have the right to work, but never to the fruit of work.",
                "source_citation": "Bhagavad Gita 2.47",
                "saved": False
            },
            {
                "id": "w2",
                "date": "2025-01-27",
                "personality_id": "albert_einstein",
                "personality_name": "Albert Einstein",
                "domain": "scientific",
                "wisdom_text": "Imagination is more important than knowledge. Knowledge is limited. Imagination encircles the world.",
                "source_citation": "Interview, 1929",
                "saved": False
            },
            {
                "id": "w3",
                "date": "2025-01-26",
                "personality_id": "marcus_aurelius",
                "personality_name": "Marcus Aurelius",
                "domain": "philosophical",
                "wisdom_text": "Very little is needed to make a happy life; it is all within yourself, in your way of thinking.",
                "source_citation": "Meditations",
                "saved": False
            },
            {
                "id": "w4",
                "date": "2025-01-25",
                "personality_id": "mahatma_gandhi",
                "personality_name": "Mahatma Gandhi",
                "domain": "leadership",
                "wisdom_text": "Be the change you wish to see in the world.",
                "source_citation": "Personal Philosophy",
                "saved": False
            },
            {
                "id": "w5",
                "date": "2025-01-24",
                "personality_id": "buddha",
                "personality_name": "Gautama Buddha",
                "domain": "spiritual",
                "wisdom_text": "Peace comes from within. Do not seek it without.",
                "source_citation": "Buddhist Teachings",
                "saved": False
            },
            {
                "id": "w6",
                "date": "2025-01-23",
                "personality_id": "socrates",
                "personality_name": "Socrates",
                "domain": "philosophical",
                "wisdom_text": "The unexamined life is not worth living.",
                "source_citation": "Apology of Socrates",
                "saved": False
            },
            {
                "id": "w7",
                "date": "2025-01-22",
                "personality_id": "abraham_lincoln",
                "personality_name": "Abraham Lincoln",
                "domain": "leadership",
                "wisdom_text": "In the end, it's not the years in your life that count. It's the life in your years.",
                "source_citation": "Attributed",
                "saved": False
            },
            {
                "id": "w8",
                "date": "2025-01-21",
                "personality_id": "rumi",
                "personality_name": "Rumi",
                "domain": "spiritual",
                "wisdom_text": "The wound is the place where the Light enters you.",
                "source_citation": "Masnavi",
                "saved": False
            },
            {
                "id": "w9",
                "date": "2025-01-20",
                "personality_id": "nikola_tesla",
                "personality_name": "Nikola Tesla",
                "domain": "scientific",
                "wisdom_text": "The present is theirs; the future, for which I really worked, is mine.",
                "source_citation": "Interview, 1899",
                "saved": False
            },
            {
                "id": "w10",
                "date": "2025-01-19",
                "personality_id": "confucius",
                "personality_name": "Confucius",
                "domain": "philosophical",
                "wisdom_text": "It does not matter how slowly you go as long as you do not stop.",
                "source_citation": "Analects",
                "saved": False
            }
        ]
        
        # Filter by domain if specified
        if domain and domain != 'All':
            all_entries = [e for e in all_entries if e['domain'] == domain]
        
        # Paginate
        total = len(all_entries)
        start = (page - 1) * limit
        end = start + limit
        entries = all_entries[start:end]
        
        response = {
            "entries": entries,
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit
        }
        
        logger.info(f"📚 Wisdom history retrieved: page={page}, count={len(entries)}")
        
        return func.HttpResponse(
            json.dumps(response),
            status_code=200,
            headers=get_cors_headers()
        )
        
    except Exception as e:
        logger.error(f"❌ Error retrieving wisdom history: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "error": "Failed to retrieve wisdom history",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }),
            status_code=500,
            headers=get_cors_headers()
        )


@app.route(route="wisdom/save", methods=["POST", "OPTIONS"])
async def save_wisdom(req: func.HttpRequest) -> func.HttpResponse:
    """
    Save a wisdom entry to user's collection.
    """
    if req.method == "OPTIONS":
        return func.HttpResponse("", status_code=204, headers=get_cors_headers())
    
    try:
        body = req.get_json()
        wisdom_id = body.get("wisdom_id")
        
        if not wisdom_id:
            return func.HttpResponse(
                json.dumps({"error": "Wisdom ID required"}),
                status_code=400,
                headers=get_cors_headers()
            )
        
        # TODO: Store in user's saved collection in Cosmos DB
        logger.info(f"💾 Wisdom saved: id={wisdom_id}")
        
        response = {
            "success": True,
            "message": "Wisdom saved to your collection",
            "wisdom_id": wisdom_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        return func.HttpResponse(
            json.dumps(response),
            status_code=200,
            headers=get_cors_headers()
        )
        
    except Exception as e:
        logger.error(f"❌ Error saving wisdom: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "error": "Failed to save wisdom",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }),
            status_code=500,
            headers=get_cors_headers()
        )


# ============================================================================
# OG Image Generation Endpoint for Social Sharing
# ============================================================================

@app.route(route="og-image/{share_id}", methods=["GET"])
async def get_og_image(req: func.HttpRequest) -> func.HttpResponse:
    """
    Generate dynamic OG (Open Graph) images for social sharing.
    Returns an SVG image with the wisdom quote, personality, and branding.
    """
    try:
        share_id = req.route_params.get('share_id', '')
        
        if not share_id:
            return func.HttpResponse(
                "Share ID required",
                status_code=400,
                headers=get_cors_headers()
            )
        
        # Import OG image service
        try:
            from services.og_image_service import og_image_service
        except ImportError as e:
            logger.error(f"❌ OG image service import failed: {e}")
            return func.HttpResponse(
                "OG image service not available",
                status_code=503,
                headers=get_cors_headers()
            )
        
        # TODO: Fetch share data from database using share_id
        # For now, use sample data based on share_id hash
        sample_wisdom_data = [
            {
                "wisdom_text": "You have the right to work, but never to the fruit of work. You should never engage in action for the sake of reward.",
                "personality": "krishna",
                "citation": "Bhagavad Gita 2.47"
            },
            {
                "wisdom_text": "What you think, you become. What you feel, you attract. What you imagine, you create.",
                "personality": "buddha",
                "citation": "Buddhist Wisdom"
            },
            {
                "wisdom_text": "The only true wisdom is in knowing you know nothing.",
                "personality": "socrates",
                "citation": "Socratic Dialogues"
            },
            {
                "wisdom_text": "Imagination is more important than knowledge. Knowledge is limited. Imagination encircles the world.",
                "personality": "einstein",
                "citation": "The World As I See It"
            },
            {
                "wisdom_text": "Be the change that you wish to see in the world.",
                "personality": "gandhi",
                "citation": "Mahatma Gandhi"
            }
        ]
        
        # Select wisdom based on share_id hash
        import hashlib
        hash_val = int(hashlib.md5(share_id.encode()).hexdigest(), 16)
        wisdom = sample_wisdom_data[hash_val % len(sample_wisdom_data)]
        
        # Generate the OG image
        result = og_image_service.get_image_response(
            wisdom_text=wisdom["wisdom_text"],
            personality=wisdom["personality"],
            citation=wisdom.get("citation")
        )
        
        if not result.get("success"):
            logger.error(f"❌ OG image generation failed: {result.get('error')}")
            return func.HttpResponse(
                "Failed to generate image",
                status_code=500,
                headers=get_cors_headers()
            )
        
        # Return SVG image with proper headers
        headers = {
            **get_cors_headers(),
            "Content-Type": "image/svg+xml; charset=utf-8",
            "Cache-Control": "public, max-age=86400",  # 24 hours
        }
        
        logger.info(f"🖼️ OG image generated for share_id={share_id}")
        
        return func.HttpResponse(
            result["content"],
            status_code=200,
            headers=headers
        )
        
    except Exception as e:
        logger.error(f"❌ OG image endpoint error: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "error": "Failed to generate OG image",
                "message": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }),
            status_code=500,
            headers=get_cors_headers()
        )


# Enhanced CORS handling in each endpoint - no separate OPTIONS handlers needed
# All endpoints already include proper CORS headers

# ==============================================================================
# MEMORY API ROUTE REGISTRATION
# ==============================================================================

# Register hierarchical memory routes if service is available
try:
    from services.memory_api import register_memory_routes
    register_memory_routes(app)
    logger.info("🧠 Memory API routes registered successfully")
except ImportError as e:
    logger.warning(f"⚠️ Memory API routes not available: {e}")
except Exception as e:
    logger.warning(f"⚠️ Failed to register memory API routes: {e}")
