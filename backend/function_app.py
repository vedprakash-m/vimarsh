"""
Vimarsh — Azure Functions Application Entry Point

Slim orchestrator that creates the FunctionApp and registers:
  • 7 Blueprint modules (routes/ package)   — 48 inline routes
  • 4 external route packages               — engagement, onboarding, memory, notifications
  • 3 timer triggers                        — notification timers

All route logic lives in backend/routes/*.py.
Shared services live in backend/routes/shared_services.py.
Original monolith backed up as function_app.py.bak.
"""

import azure.functions as func
import logging

# ── logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── create app ───────────────────────────────────────────────────────────────
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# ── register blueprint modules ──────────────────────────────────────────────
try:
    from routes import ALL_BLUEPRINTS
    for bp in ALL_BLUEPRINTS:
        app.register_functions(bp)
    logger.info(f"✅ Registered {len(ALL_BLUEPRINTS)} route blueprints")
except Exception as e:
    logger.critical(f"❌ Failed to register blueprints: {e}")
    raise

# ── register legacy route packages (already extracted before blueprints) ────

# Memory API
try:
    from services.memory_api import register_memory_routes
    register_memory_routes(app)
    logger.info("🧠 Memory API routes registered")
except ImportError as e:
    logger.warning(f"⚠️ Memory API routes not available: {e}")
except Exception as e:
    logger.warning(f"⚠️ Failed to register memory API routes: {e}")

# Onboarding API
try:
    from onboarding.onboarding_api import register_onboarding_routes
    register_onboarding_routes(app)
    logger.info("🎯 Onboarding API routes registered")
except ImportError as e:
    logger.warning(f"⚠️ Onboarding API routes not available: {e}")
except Exception as e:
    logger.warning(f"⚠️ Failed to register onboarding API routes: {e}")

# Engagement API
try:
    from engagement.engagement_api import register_engagement_routes
    register_engagement_routes(app)
    logger.info("🏆 Engagement API routes registered")
except ImportError as e:
    logger.warning(f"⚠️ Engagement API routes not available: {e}")
except Exception as e:
    logger.warning(f"⚠️ Failed to register engagement API routes: {e}")

# Notification API + timer triggers
try:
    from notifications.notification_api import register_notification_routes
    register_notification_routes(app)
    logger.info("🔔 Notification API routes registered")
except ImportError as e:
    logger.warning(f"⚠️ Notification API routes not available: {e}")
except Exception as e:
    logger.warning(f"⚠️ Failed to register notification API routes: {e}")

try:
    from notifications.notification_trigger import register_notification_timers
    register_notification_timers(app)
    logger.info("⏰ Notification timer triggers registered")
except ImportError as e:
    logger.warning(f"⚠️ Notification timer triggers not available: {e}")
except Exception as e:
    logger.warning(f"⚠️ Failed to register notification timer triggers: {e}")

logger.info("🚀 Vimarsh function app initialized")

# ── backward-compatible exports for tests ────────────────────────────────────
# These re-export symbols that tests expect to find in function_app.py
# After refactoring, they live in blueprint modules but tests may still import here

try:
    from routes.shared_services import get_cors_headers, FALLBACK_PERSONALITIES
    from routes.shared_services import get_personality_list as get_active_personalities
    from routes.shared_services import (
        database_personality_available,
        personality_service_available,
        personality_models_available,
        enhanced_llm_available,
        enhanced_rag_available,
        memory_service_available,
        hierarchical_memory_available,
        engagement_available,
        database_personality_service,
        optimized_personality_service as personality_service,
        PersonalityService,
    )
except ImportError:
    pass

try:
    from routes.guidance_bp import guidance_endpoint
except ImportError:
    pass

try:
    from routes.diagnostics_bp import health_endpoint
except ImportError:
    pass

try:
    from routes.admin_bp import admin_role_endpoint
except ImportError:
    pass

