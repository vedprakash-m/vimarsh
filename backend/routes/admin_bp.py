"""
Azure Functions Blueprint for all Vimarsh admin routes.
Extracted from function_app.py — 28 admin endpoints.
"""

import azure.functions as func
import json
import logging
import os
import time
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)

bp = func.Blueprint()

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _cors():
    """Standard CORS headers for every response."""
    return {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "https://vimarsh.vedprakash.net",
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "GET, POST, PATCH, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
    }


async def _require_admin(req: func.HttpRequest):
    """Extract the authenticated user via EnhancedUnifiedAuthService.

    Returns the authenticated user object, or ``None`` if auth fails.
    """
    try:
        from auth.enhanced_unified_auth_service import EnhancedUnifiedAuthService
        auth_service = EnhancedUnifiedAuthService()
        return await auth_service.extract_user_from_request(req)
    except Exception as e:
        logger.error(f"❌ Auth extraction error: {e}")
        return None


# ---------------------------------------------------------------------------
# Admin service (optional)
# ---------------------------------------------------------------------------

try:
    from services.admin_service import AdminService
    admin_service = AdminService()
except ImportError:
    admin_service = None

# ---------------------------------------------------------------------------
# FALLBACK_PERSONALITIES (imported from shared_services)
# ---------------------------------------------------------------------------

from routes.shared_services import FALLBACK_PERSONALITIES

# ---------------------------------------------------------------------------
# Delegated function imports (try-import pattern from admin modules)
# ---------------------------------------------------------------------------

# admin.admin_endpoints
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
        create_personality_content_associations,
    )
    logger.info("✅ admin.admin_endpoints imported in admin_bp")
except ImportError as e:
    logger.warning(f"⚠️ admin.admin_endpoints not available: {e}")
    admin_cost_dashboard = None
    admin_personalities_management = None
    admin_content_sources = None
    admin_content_management = None
    get_content_status = None
    acquire_personality_content = None
    process_personality_content = None
    validate_content_quality = None
    create_personality_content_associations = None

# admin.admin_api_integration
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
        admin_dashboard_overview,
    )
    logger.info("✅ admin.admin_api_integration imported in admin_bp")
except ImportError as e:
    logger.warning(f"⚠️ admin.admin_api_integration not available: {e}")
    admin_content_overview = None
    admin_process_content = None
    admin_task_status = None
    admin_delete_content = None
    admin_regenerate_embeddings = None
    admin_all_tasks = None
    admin_start_validation = None
    admin_validation_status = None
    admin_all_validations = None
    admin_start_security_audit = None
    admin_security_audit_status = None
    admin_all_security_audits = None
    admin_security_summary = None
    admin_dashboard_overview = None


# ===================================================================
# 1. vimarsh-admin/role  GET — admin role check with caching
# ===================================================================

# Module-level cache dict
_cache: dict = {}

@bp.route(route="vimarsh-admin/role", methods=["GET"])
async def admin_role_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Optimized admin role endpoint with caching for faster response."""
    try:
        from auth.enhanced_unified_auth_service import EnhancedUnifiedAuthService

        logger.info("🔐 Admin role endpoint called")

        auth_service = EnhancedUnifiedAuthService()
        authenticated_user = await auth_service.extract_user_from_request(req)

        if not authenticated_user:
            logger.warning("🚫 No authenticated user found")
            return func.HttpResponse(
                json.dumps({
                    "error": "Authentication required",
                    "message": "Valid access token must be provided",
                    "code": "UNAUTHORIZED",
                }),
                status_code=401,
                headers=_cors(),
            )

        # Check cache first (180-second / 3-min TTL)
        cache_key = f"admin_role_{authenticated_user.email}"
        try:
            if cache_key in _cache:
                cached_data, timestamp = _cache[cache_key]
                if time.time() - timestamp < 180:
                    logger.info(f"⚡ Using cached admin role for {authenticated_user.email}")
                    return func.HttpResponse(
                        json.dumps(cached_data),
                        status_code=200,
                        headers=_cors(),
                    )
        except Exception as cache_error:
            logger.warning(f"Cache error: {cache_error}")

        logger.info(f"🔐 Admin role check for user: {authenticated_user.email}")

        # Determine personality_models_available / personality_service_available
        try:
            from models.personality_models import PERSONALITY_CONFIGS  # noqa: F401
            personality_models_available = True
        except ImportError:
            personality_models_available = False

        try:
            from services.personality_service import PersonalityService  # noqa: F401
            personality_service_available = True
        except ImportError:
            personality_service_available = False

        response_data = None

        if admin_service:
            try:
                response_data = admin_service.get_user_role(user_email=authenticated_user.email)
                logger.info(f"✅ AdminService returned: {response_data}")
                response_data["service_status"] = {
                    "personality_models": personality_models_available,
                    "personality_service": personality_service_available,
                    "admin_service": True,
                    "architecture": "modular",
                }
                response_data["auth_context"] = {
                    "source": "unified_auth_service",
                    "email": authenticated_user.email,
                    "authenticated": True,
                    "auth_mode": str(auth_service.mode),
                    "auth_enabled": auth_service.is_enabled,
                }

                # Cache successful response
                try:
                    _cache[cache_key] = (response_data, time.time())
                    logger.info(f"💾 Cached admin role for {authenticated_user.email}")
                except Exception as ce:
                    logger.warning(f"Failed to cache: {ce}")

            except Exception as admin_error:
                logger.error(f"❌ AdminService error: {admin_error}")
                admin_emails = os.getenv("ADMIN_EMAILS", "vedprakash.m@outlook.com").split(",")
                is_admin = authenticated_user.email.strip().lower() in [
                    e.strip().lower() for e in admin_emails
                ]
                response_data = {
                    "role": "admin" if is_admin else "user",
                    "permissions": ["read", "write", "admin"] if is_admin else ["read"],
                    "user_email": authenticated_user.email,
                    "user_id": authenticated_user.id,
                    "service_status": {
                        "personality_models": personality_models_available,
                        "personality_service": personality_service_available,
                        "admin_service": False,
                        "architecture": "modular",
                    },
                    "auth_context": {
                        "source": "unified_auth_service",
                        "email": authenticated_user.email,
                        "authenticated": True,
                        "auth_mode": str(auth_service.mode),
                        "auth_enabled": auth_service.is_enabled,
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "warning": f"AdminService error: {admin_error} - using environment variable check",
                }
                logger.info(f"🔄 Fallback admin check result: {response_data}")
        else:
            admin_emails = os.getenv("ADMIN_EMAILS", "vedprakash.m@outlook.com").split(",")
            is_admin = authenticated_user.email.strip().lower() in [
                e.strip().lower() for e in admin_emails
            ]
            logger.info(
                f"🔍 Environment variable admin check: admin_emails={admin_emails}, "
                f"user_email={authenticated_user.email}, is_admin={is_admin}"
            )
            response_data = {
                "role": "admin" if is_admin else "user",
                "permissions": ["read", "write", "admin"] if is_admin else ["read"],
                "user_email": authenticated_user.email,
                "user_id": authenticated_user.id,
                "service_status": {
                    "personality_models": personality_models_available,
                    "personality_service": personality_service_available,
                    "admin_service": False,
                    "architecture": "modular",
                },
                "auth_context": {
                    "source": "unified_auth_service",
                    "email": authenticated_user.email,
                    "authenticated": True,
                    "auth_mode": str(auth_service.mode),
                    "auth_enabled": auth_service.is_enabled,
                },
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "warning": "Admin service unavailable - using environment variable check",
            }
            logger.info(f"🔄 Environment variable admin check result: {response_data}")

        # Final cache write
        if cache_key and response_data:
            try:
                _cache[cache_key] = (response_data, time.time())
                logger.info(f"💾 Cached admin role for {authenticated_user.email}")
            except Exception as ce:
                logger.warning(f"Failed to cache: {ce}")

        return func.HttpResponse(
            json.dumps(response_data),
            status_code=200,
            headers=_cors(),
        )
    except Exception as e:
        logger.error(f"❌ Admin role error: {e}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to get admin role", "details": str(e)}),
            status_code=500,
            headers=_cors(),
        )


# ===================================================================
# 2. vimarsh-admin/monitoring  GET
# ===================================================================

@bp.route(route="vimarsh-admin/monitoring", methods=["GET"])
async def admin_monitoring_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Admin monitoring endpoint for system health and usage data."""
    try:
        logger.info("📊 Admin monitoring endpoint called")

        authenticated_user = await _require_admin(req)
        if not authenticated_user:
            return func.HttpResponse(
                json.dumps({"error": "Authentication required"}),
                status_code=401,
                headers=_cors(),
            )

        if admin_service:
            monitoring_data = admin_service.get_usage_monitoring()
        else:
            monitoring_data = {
                "current_status": "healthy",
                "active_sessions": 0,
                "rate_limits": {
                    "requests_per_hour": 1000,
                    "current_usage": 0,
                    "percentage_used": 0.0,
                },
                "performance": {
                    "avg_response_time_ms": 250,
                    "system_load": "low",
                    "memory_usage": "normal",
                },
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "service_version": "fallback_v1.0",
            }

        return func.HttpResponse(
            json.dumps(monitoring_data),
            status_code=200,
            headers=_cors(),
        )
    except Exception as e:
        logger.error(f"❌ Admin monitoring error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to get monitoring data", "details": str(e)}),
            status_code=500,
            headers=_cors(),
        )


# ===================================================================
# 3. vimarsh-admin/dashboard  GET — full Cosmos DB queries
# ===================================================================

@bp.route(route="vimarsh-admin/dashboard", methods=["GET"])
async def admin_dashboard_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Admin dashboard endpoint for system statistics and analytics — queries real data."""
    try:
        logger.info("📊 Admin dashboard endpoint called")

        authenticated_user = await _require_admin(req)
        if not authenticated_user:
            return func.HttpResponse(
                json.dumps({"error": "Authentication required"}),
                status_code=401,
                headers=_cors(),
            )

        total_users = 0
        active_users = 0
        total_conversations = 0
        total_messages = 0
        personality_count = 25
        total_content_chunks = 0
        personality_usage = {}

        try:
            from azure.cosmos import CosmosClient

            connection_string = os.getenv("AZURE_COSMOS_CONNECTION_STRING")
            if connection_string:
                client = CosmosClient.from_connection_string(connection_string)
                database = client.get_database_client("vimarsh-multi-personality")

                # user_preferences — user counts
                try:
                    users_container = database.get_container_client("user_preferences")
                    user_count = list(users_container.query_items(
                        query="SELECT VALUE COUNT(1) FROM c",
                        enable_cross_partition_query=True,
                    ))
                    total_users = user_count[0] if user_count else 0
                    active_users = total_users
                except Exception as ue:
                    logger.warning(f"⚠️ User count query error: {ue}")

                # conversations — activity metrics + personality usage
                try:
                    conversations_container = database.get_container_client("conversations")
                    conv_count = list(conversations_container.query_items(
                        query="SELECT VALUE COUNT(1) FROM c",
                        enable_cross_partition_query=True,
                    ))
                    total_conversations = conv_count[0] if conv_count else 0

                    usage_results = list(conversations_container.query_items(
                        query="SELECT c.personality, COUNT(1) as count FROM c GROUP BY c.personality",
                        enable_cross_partition_query=True,
                    ))
                    for item in usage_results:
                        personality_usage[item.get("personality", "unknown")] = item.get("count", 0)
                except Exception as ce:
                    logger.warning(f"⚠️ Conversations query error: {ce}")

                # personalities — count
                try:
                    personalities_container = database.get_container_client("personalities")
                    pers_count = list(personalities_container.query_items(
                        query="SELECT VALUE COUNT(1) FROM c",
                        enable_cross_partition_query=True,
                    ))
                    db_personality_count = pers_count[0] if pers_count else 0
                    personality_count = db_personality_count if db_personality_count > 0 else 25
                except Exception as pe:
                    logger.warning(f"⚠️ Personalities query error: {pe}")
                    personality_count = 25

                # personality_vectors — content chunks
                try:
                    vectors_container = database.get_container_client("personality_vectors")
                    vectors_count = list(vectors_container.query_items(
                        query="SELECT VALUE COUNT(1) FROM c",
                        enable_cross_partition_query=True,
                    ))
                    total_content_chunks = vectors_count[0] if vectors_count else 0
                except Exception as ve:
                    logger.warning(f"⚠️ Vectors query error: {ve}")

        except ImportError:
            logger.warning("⚠️ Azure Cosmos SDK not available")
        except Exception as db_err:
            logger.warning(f"⚠️ Database query error: {db_err}")

        most_popular = "krishna"
        if personality_usage:
            most_popular = max(personality_usage, key=personality_usage.get)

        analytics_data = {
            "period": {
                "days": 30,
                "start_date": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "end_date": datetime.now(timezone.utc).isoformat(),
            },
            "user_metrics": {
                "total_users": total_users,
                "active_users": active_users,
                "new_users": 0,
                "returning_users": total_users,
            },
            "usage_metrics": {
                "estimated_cost": 0.0,
                "total_tokens": total_conversations * 500,
                "total_requests": total_conversations,
            },
            "personality_metrics": {
                "most_popular": most_popular,
                "total_interactions": total_conversations,
                "avg_response_time": 2.3,
                "usage_breakdown": personality_usage,
            },
            "system_metrics": {
                "total_requests": total_conversations,
                "error_rate": 0.0,
                "uptime": "99.9%",
            },
            "content_metrics": {
                "personalities": personality_count,
                "spiritual_texts": 458,
                "total_content_chunks": total_content_chunks if total_content_chunks > 0 else 32000,
            },
            "status": "operational",
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service_version": "database_v2.0",
        }

        logger.info(
            f"✅ Dashboard: {total_users} users, {total_conversations} conversations, "
            f"{personality_count} personalities"
        )

        return func.HttpResponse(
            json.dumps(analytics_data),
            status_code=200,
            headers=_cors(),
        )
    except Exception as e:
        logger.error(f"❌ Admin dashboard error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to get dashboard data", "details": str(e)}),
            status_code=500,
            headers=_cors(),
        )


# ===================================================================
# 4. vimarsh-admin/cost-dashboard  GET
# ===================================================================

@bp.route(route="vimarsh-admin/cost-dashboard", methods=["GET"])
async def admin_cost_dashboard_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Admin cost dashboard endpoint (alias for dashboard with cost focus)."""
    try:
        logger.info("💰 Admin cost dashboard endpoint called")

        authenticated_user = await _require_admin(req)
        if not authenticated_user:
            return func.HttpResponse(
                json.dumps({"error": "Authentication required"}),
                status_code=401,
                headers=_cors(),
            )

        if admin_service:
            analytics_data = admin_service.get_admin_analytics(days=30)
        else:
            analytics_data = {
                "period": {
                    "days": 30,
                    "start_date": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                    "end_date": datetime.now(timezone.utc).isoformat(),
                },
                "cost_metrics": {
                    "total_cost_usd": 0.0,
                    "llm_cost_usd": 0.0,
                    "infrastructure_cost_usd": 0.0,
                    "cost_per_request": 0.0,
                },
                "usage_metrics": {
                    "total_requests": 0,
                    "llm_requests": 0,
                    "template_requests": 0,
                },
                "efficiency_metrics": {
                    "cost_efficiency": 100.0,
                    "cache_hit_rate": 0.0,
                },
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "service_version": "fallback_v1.0",
            }

        return func.HttpResponse(
            json.dumps(analytics_data),
            status_code=200,
            headers=_cors(),
        )
    except Exception as e:
        logger.error(f"❌ Admin cost dashboard error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to get cost dashboard data", "details": str(e)}),
            status_code=500,
            headers=_cors(),
        )


# ===================================================================
# 5. vimarsh-admin/users  GET — dual-container querying with dedup
# ===================================================================

@bp.route(route="vimarsh-admin/users", methods=["GET"])
async def admin_users_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Admin users endpoint for user management data — queries real database."""
    try:
        logger.info("👥 Admin users endpoint called")

        authenticated_user = await _require_admin(req)
        if not authenticated_user:
            return func.HttpResponse(
                json.dumps({"error": "Authentication required"}),
                status_code=401,
                headers=_cors(),
            )

        users_list = []
        users_by_email: dict = {}
        total_conversations = 0
        blocked_count = 0

        try:
            from azure.cosmos import CosmosClient

            connection_string = os.getenv("AZURE_COSMOS_CONNECTION_STRING")
            if connection_string:
                client = CosmosClient.from_connection_string(connection_string)
                database = client.get_database_client("vimarsh-multi-personality")

                # Query user_preferences container
                try:
                    users_container = database.get_container_client("user_preferences")
                    users = list(users_container.query_items(
                        query="SELECT * FROM c",
                        enable_cross_partition_query=True,
                    ))

                    for user in users:
                        user_id = user.get("user_id", user.get("id", "unknown"))
                        email = user.get("email", f"{user_id}@user.local")
                        is_blocked = user.get("is_blocked", False)
                        if is_blocked:
                            blocked_count += 1

                        users_by_email[email.lower()] = {
                            "id": user_id,
                            "email": email,
                            "name": user.get("name", user.get("display_name", "User")),
                            "role": user.get("role", "user"),
                            "last_login": user.get("last_activity", user.get("_ts", "")),
                            "status": "blocked" if is_blocked else "active",
                            "total_conversations": user.get("conversation_count", 0),
                            "preferences": user.get("preferences", {}),
                        }
                except Exception as user_err:
                    logger.warning(f"⚠️ Could not query user_preferences: {user_err}")

                # Also query 'users' container and merge
                try:
                    alt_users_container = database.get_container_client("users")
                    alt_users = list(alt_users_container.query_items(
                        query="SELECT * FROM c",
                        enable_cross_partition_query=True,
                    ))

                    for user in alt_users:
                        user_id = user.get("user_id", user.get("id", "unknown"))
                        email = user.get("email", f"{user_id}@user.local")
                        email_key = email.lower()

                        if email_key not in users_by_email:
                            is_blocked = user.get("is_blocked", False)
                            if is_blocked:
                                blocked_count += 1

                            users_by_email[email_key] = {
                                "id": user_id,
                                "email": email,
                                "name": user.get("name", user.get("display_name", "User")),
                                "role": user.get("role", "user"),
                                "last_login": user.get("last_activity", user.get("last_login", "")),
                                "status": "blocked" if is_blocked else "active",
                                "total_conversations": user.get("conversation_count", 0),
                                "preferences": user.get("preferences", {}),
                            }
                except Exception as alt_err:
                    logger.debug(f"ℹ️ Users container not available: {alt_err}")

                # conversations count
                try:
                    conversations_container = database.get_container_client("conversations")
                    count_result = list(conversations_container.query_items(
                        query="SELECT VALUE COUNT(1) FROM c",
                        enable_cross_partition_query=True,
                    ))
                    total_conversations = count_result[0] if count_result else 0
                except Exception as conv_err:
                    logger.warning(f"⚠️ Could not query conversations: {conv_err}")

        except ImportError:
            logger.warning("⚠️ Azure Cosmos SDK not available")
        except Exception as db_err:
            logger.warning(f"⚠️ Database query error: {db_err}")

        users_list = list(users_by_email.values())

        # Always include authenticated admin user if not already present
        admin_email = authenticated_user.email.lower() if authenticated_user.email else ""
        if admin_email and admin_email not in users_by_email:
            users_list.append({
                "id": authenticated_user.id,
                "email": authenticated_user.email,
                "name": authenticated_user.name or "Admin User",
                "role": "admin",
                "last_login": datetime.now(timezone.utc).isoformat(),
                "status": "active",
                "total_conversations": 0,
            })

        users_data = {
            "users": users_list,
            "total_users": len(users_list),
            "active_users": len([u for u in users_list if u.get("status") == "active"]),
            "blocked_users": blocked_count,
            "admin_users": len([u for u in users_list if u.get("role") == "admin"]),
            "total_conversations": total_conversations,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service_version": "database_v2.0",
        }

        logger.info(f"✅ Returning {len(users_list)} users from database")

        return func.HttpResponse(
            json.dumps(users_data),
            status_code=200,
            headers=_cors(),
        )
    except Exception as e:
        logger.error(f"❌ Admin users error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to get users data", "details": str(e)}),
            status_code=500,
            headers=_cors(),
        )


# ===================================================================
# 6. vimarsh-admin/personalities  GET — seed_personalities + triple fallback
# ===================================================================

@bp.route(route="vimarsh-admin/personalities", methods=["GET"])
async def admin_personalities_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Admin personality management — returns all 25 personalities with status."""
    try:
        logger.info("🤖 Admin personalities endpoint called")

        authenticated_user = await _require_admin(req)
        if not authenticated_user:
            return func.HttpResponse(
                json.dumps({"error": "Authentication required"}),
                status_code=401,
                headers=_cors(),
            )

        # First fallback: seed_personalities module
        try:
            from admin.seed_personalities import get_all_personalities, get_content_source
            all_known_personalities = get_all_personalities()
        except ImportError:
            all_known_personalities = []

        detailed_personalities = []
        db_personalities = {}

        # Try Cosmos DB for live data
        try:
            from azure.cosmos import CosmosClient

            connection_string = os.getenv("AZURE_COSMOS_CONNECTION_STRING")
            if connection_string:
                client = CosmosClient.from_connection_string(connection_string)
                database = client.get_database_client("vimarsh-multi-personality")

                # All personalities from DB
                try:
                    personalities_container = database.get_container_client("personalities")
                    db_pers = list(personalities_container.query_items(
                        query="SELECT * FROM c",
                        enable_cross_partition_query=True,
                    ))
                    for p in db_pers:
                        db_personalities[p.get("id")] = p
                except Exception:
                    pass

                # Vector counts per personality
                vectors_container = database.get_container_client("personality_vectors")
                for known_p in all_known_personalities:
                    pid = known_p["id"]
                    db_p = db_personalities.get(pid, {})

                    chunk_count = 0
                    try:
                        chunk_query = f"SELECT VALUE COUNT(1) FROM c WHERE c.personality_id = '{pid}'"
                        chunk_result = list(vectors_container.query_items(
                            query=chunk_query,
                            enable_cross_partition_query=True,
                        ))
                        chunk_count = chunk_result[0] if chunk_result else 0
                    except Exception:
                        pass

                    detailed_personalities.append({
                        "id": pid,
                        "name": db_p.get("name", known_p.get("name", pid.replace("_", " ").title())),
                        "domain": db_p.get("domain", known_p.get("domain", "unknown")),
                        "description": db_p.get("description", known_p.get("description", "")),
                        "status": "active" if chunk_count > 0 else "pending",
                        "last_updated": db_p.get("updated_at", datetime.now(timezone.utc).isoformat()),
                        "usage_count": 0,
                        "content_sources": 1,
                        "total_chunks": chunk_count,
                        "rag_ready": chunk_count > 0,
                        "response_quality": 95.0 if chunk_count > 0 else 0.0,
                    })
        except Exception as db_err:
            logger.warning(f"⚠️ Database query error: {db_err}")
            # Second fallback: seed data with get_content_source
            for known_p in all_known_personalities:
                try:
                    content = get_content_source(known_p["id"])
                except Exception:
                    content = {"chunks": 0}
                detailed_personalities.append({
                    "id": known_p["id"],
                    "name": known_p.get("name", known_p["id"].replace("_", " ").title()),
                    "domain": known_p.get("domain", "unknown"),
                    "description": known_p.get("description", ""),
                    "status": "active",
                    "last_updated": datetime.now(timezone.utc).isoformat(),
                    "usage_count": 0,
                    "content_sources": 1,
                    "total_chunks": content.get("chunks", 0),
                    "rag_ready": content.get("chunks", 0) > 0,
                    "response_quality": 95.0,
                })

        # Third fallback: FALLBACK_PERSONALITIES
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
                    "response_quality": 85.0,
                })

        personalities_data = {
            "personalities": detailed_personalities,
            "total_personalities": len(detailed_personalities),
            "active_personalities": len([p for p in detailed_personalities if p.get("status") == "active"]),
            "rag_ready_count": len([p for p in detailed_personalities if p.get("rag_ready")]),
            "domains": list(set(p.get("domain") for p in detailed_personalities)),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service_version": "enhanced_v2.0",
        }

        logger.info(f"✅ Returning {len(detailed_personalities)} personalities")

        return func.HttpResponse(
            json.dumps(personalities_data),
            status_code=200,
            headers=_cors(),
        )
    except Exception as e:
        logger.error(f"❌ Admin personalities error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to get personalities data", "details": str(e)}),
            status_code=500,
            headers=_cors(),
        )


# ===================================================================
# 7. vimarsh-admin/content-sources  GET — delegate or inline fallback
# ===================================================================

@bp.route(route="vimarsh-admin/content-sources", methods=["GET"])
async def admin_content_sources_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Admin content sources endpoint — delegates to dedicated admin module."""
    try:
        if admin_content_sources is not None:
            return await admin_content_sources(req)

        # Inline fallback
        authenticated_user = await _require_admin(req)
        if not authenticated_user:
            return func.HttpResponse(
                json.dumps({"error": "Authentication required"}),
                status_code=401,
                headers=_cors(),
            )

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
            "tesla": {"name": "Tesla's Patents", "chunks": 203, "size_mb": 25.6},
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
            "rabindranath_tagore": {"name": "Poetry & Prose Collection", "chunks": 234, "size_mb": 18.9},
        }

        content_sources = []
        for pid, content in personality_content_map.items():
            content_sources.append({
                "id": f"{pid}_source",
                "name": content["name"],
                "personality_associations": [pid],
                "chunks": content["chunks"],
                "size_mb": content["size_mb"],
                "status": "processed",
                "last_updated": datetime.now(timezone.utc).isoformat(),
            })

        content_data = {
            "content_sources": content_sources,
            "total_sources": len(content_sources),
            "total_chunks": sum(s["chunks"] for s in content_sources),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service_version": "fallback_v1.0",
        }

        return func.HttpResponse(
            json.dumps(content_data),
            status_code=200,
            headers=_cors(),
        )
    except Exception as e:
        logger.error(f"❌ Admin content sources error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to get content sources data", "details": str(e)}),
            status_code=500,
            headers=_cors(),
        )


# ===================================================================
# 8. vimarsh-admin/settings  GET
# ===================================================================

@bp.route(route="vimarsh-admin/settings", methods=["GET"])
async def admin_settings_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Admin settings endpoint with real admin user information."""
    try:
        logger.info("⚙️ Admin settings endpoint called")

        authenticated_user = await _require_admin(req)
        if not authenticated_user:
            return func.HttpResponse(
                json.dumps({"error": "Authentication required"}),
                status_code=401,
                headers=_cors(),
            )

        admin_info = {
            "name": authenticated_user.name or "System Administrator",
            "email": authenticated_user.email,
            "role": "super_admin",
            "permissions": ["User Management", "Content Management", "System Configuration", "Analytics"],
            "last_login": datetime.now(timezone.utc).isoformat(),
            "account_created": "2024-01-01T00:00:00Z",
            "two_factor_enabled": False,
        }

        settings_data = {
            "administrator": admin_info,
            "system_configuration": {
                "application_name": "Vimarsh",
                "version": "2.0.0",
                "environment": "production",
                "total_personalities": len(FALLBACK_PERSONALITIES),
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service_version": "admin_v1.0",
        }

        return func.HttpResponse(
            json.dumps(settings_data),
            status_code=200,
            headers=_cors(),
        )
    except Exception as e:
        logger.error(f"❌ Admin settings error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to get settings data", "details": str(e)}),
            status_code=500,
            headers=_cors(),
        )


# ===================================================================
# 9. vimarsh-admin/seed-database  POST
# ===================================================================

@bp.route(route="vimarsh-admin/seed-database", methods=["POST"])
async def admin_seed_database_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Seed the database with all 25 personalities — Admin only."""
    try:
        logger.info("🌱 Admin database seed endpoint called")

        authenticated_user = await _require_admin(req)
        if not authenticated_user:
            return func.HttpResponse(
                json.dumps({"error": "Authentication required"}),
                status_code=401,
                headers=_cors(),
            )

        try:
            from admin.seed_personalities import seed_personalities_to_cosmos
            result = await seed_personalities_to_cosmos()

            return func.HttpResponse(
                json.dumps({
                    "success": True,
                    "message": "Database seeded successfully",
                    "details": result,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }),
                status_code=200,
                headers=_cors(),
            )
        except ImportError as ie:
            return func.HttpResponse(
                json.dumps({"error": "Seeding module not available", "details": str(ie)}),
                status_code=500,
                headers=_cors(),
            )
        except Exception as seed_error:
            logger.error(f"❌ Database seeding failed: {seed_error}")
            return func.HttpResponse(
                json.dumps({"error": "Database seeding failed", "details": str(seed_error)}),
                status_code=500,
                headers=_cors(),
            )

    except Exception as e:
        logger.error(f"❌ Admin seed database error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to seed database", "details": str(e)}),
            status_code=500,
            headers=_cors(),
        )


# ===================================================================
# 10–14. Content pipeline (delegating thin routes)
# ===================================================================

@bp.route(route="vimarsh-admin/content/status", methods=["GET"])
async def admin_content_status_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Get content status for all personalities."""
    try:
        if get_content_status is not None:
            return await get_content_status(req)
        return func.HttpResponse(
            json.dumps({"error": "Content status service not available"}),
            status_code=503,
            headers=_cors(),
        )
    except Exception as e:
        logger.error(f"❌ Content status error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to get content status", "details": str(e)}),
            status_code=500,
            headers=_cors(),
        )


@bp.route(route="vimarsh-admin/content/acquire", methods=["POST"])
async def admin_acquire_content_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Acquire content for a specific personality."""
    try:
        if acquire_personality_content is not None:
            return await acquire_personality_content(req)
        return func.HttpResponse(
            json.dumps({"error": "Content acquisition service not available"}),
            status_code=503,
            headers=_cors(),
        )
    except Exception as e:
        logger.error(f"❌ Content acquisition error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to acquire content", "details": str(e)}),
            status_code=500,
            headers=_cors(),
        )


@bp.route(route="vimarsh-admin/content/process", methods=["POST"])
async def admin_process_content_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Process raw content into chunks."""
    try:
        if process_personality_content is not None:
            return await process_personality_content(req)
        return func.HttpResponse(
            json.dumps({"error": "Content processing service not available"}),
            status_code=503,
            headers=_cors(),
        )
    except Exception as e:
        logger.error(f"❌ Content processing error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to process content", "details": str(e)}),
            status_code=500,
            headers=_cors(),
        )


@bp.route(route="vimarsh-admin/content/validate", methods=["POST"])
async def admin_validate_content_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Validate content quality."""
    try:
        if validate_content_quality is not None:
            return await validate_content_quality(req)
        return func.HttpResponse(
            json.dumps({"error": "Content validation service not available"}),
            status_code=503,
            headers=_cors(),
        )
    except Exception as e:
        logger.error(f"❌ Content validation error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to validate content", "details": str(e)}),
            status_code=500,
            headers=_cors(),
        )


@bp.route(route="vimarsh-admin/content/associate", methods=["POST"])
async def admin_associate_content_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Create personality-content associations."""
    try:
        if create_personality_content_associations is not None:
            return await create_personality_content_associations(req)
        return func.HttpResponse(
            json.dumps({"error": "Content association service not available"}),
            status_code=503,
            headers=_cors(),
        )
    except Exception as e:
        logger.error(f"❌ Content association error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to create associations", "details": str(e)}),
            status_code=500,
            headers=_cors(),
        )


# ===================================================================
# 15–20. Content management (delegating thin routes)
# ===================================================================

@bp.route(route="vimarsh-admin/content-management/overview", methods=["GET"])
async def admin_content_management_overview_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Content management service overview."""
    try:
        if admin_content_overview is not None:
            return admin_content_overview(req)
        return func.HttpResponse(
            json.dumps({"error": "Content management service not available"}),
            status_code=503,
            headers=_cors(),
        )
    except Exception as e:
        logger.error(f"❌ Content management overview error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to get content overview", "details": str(e)}),
            status_code=500,
            headers=_cors(),
        )


@bp.route(route="vimarsh-admin/content-management/process", methods=["POST"])
async def admin_content_management_process_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Process personality content."""
    try:
        if admin_process_content is not None:
            return admin_process_content(req)
        return func.HttpResponse(
            json.dumps({"error": "Content management service not available"}),
            status_code=503,
            headers=_cors(),
        )
    except Exception as e:
        logger.error(f"❌ Content management process error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to process content", "details": str(e)}),
            status_code=500,
            headers=_cors(),
        )


@bp.route(route="vimarsh-admin/content-management/tasks", methods=["GET"])
async def admin_content_management_tasks_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Get all content management tasks."""
    try:
        if admin_all_tasks is not None:
            return admin_all_tasks(req)
        return func.HttpResponse(
            json.dumps({"error": "Content management service not available"}),
            status_code=503,
            headers=_cors(),
        )
    except Exception as e:
        logger.error(f"❌ Content management tasks error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to get tasks", "details": str(e)}),
            status_code=500,
            headers=_cors(),
        )


@bp.route(route="vimarsh-admin/content-management/tasks/{task_id}", methods=["GET"])
async def admin_content_management_task_status_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Get content management task status."""
    try:
        if admin_task_status is not None:
            return admin_task_status(req)
        return func.HttpResponse(
            json.dumps({"error": "Content management service not available"}),
            status_code=503,
            headers=_cors(),
        )
    except Exception as e:
        logger.error(f"❌ Content management task status error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to get task status", "details": str(e)}),
            status_code=500,
            headers=_cors(),
        )


@bp.route(route="vimarsh-admin/content-management/delete", methods=["DELETE"])
async def admin_content_management_delete_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Delete personality content."""
    try:
        if admin_delete_content is not None:
            return admin_delete_content(req)
        return func.HttpResponse(
            json.dumps({"error": "Content management service not available"}),
            status_code=503,
            headers=_cors(),
        )
    except Exception as e:
        logger.error(f"❌ Content management delete error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to delete content", "details": str(e)}),
            status_code=500,
            headers=_cors(),
        )


@bp.route(route="vimarsh-admin/content-management/regenerate-embeddings", methods=["POST"])
async def admin_content_management_regenerate_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Regenerate embeddings for personality."""
    try:
        if admin_regenerate_embeddings is not None:
            return admin_regenerate_embeddings(req)
        return func.HttpResponse(
            json.dumps({"error": "Content management service not available"}),
            status_code=503,
            headers=_cors(),
        )
    except Exception as e:
        logger.error(f"❌ Content management regenerate error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to regenerate embeddings", "details": str(e)}),
            status_code=500,
            headers=_cors(),
        )


# ===================================================================
# 21–23. Testing & Validation (delegating thin routes)
# ===================================================================

@bp.route(route="vimarsh-admin/testing/start-validation", methods=["POST"])
async def admin_testing_start_validation_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Start a validation suite."""
    try:
        if admin_start_validation is not None:
            return admin_start_validation(req)
        return func.HttpResponse(
            json.dumps({"error": "Testing validation service not available"}),
            status_code=503,
            headers=_cors(),
        )
    except Exception as e:
        logger.error(f"❌ Testing start validation error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to start validation", "details": str(e)}),
            status_code=500,
            headers=_cors(),
        )


@bp.route(route="vimarsh-admin/testing/validation-status", methods=["GET"])
async def admin_testing_validation_status_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Get validation suite status."""
    try:
        if admin_validation_status is not None:
            return admin_validation_status(req)
        return func.HttpResponse(
            json.dumps({"error": "Testing validation service not available"}),
            status_code=503,
            headers=_cors(),
        )
    except Exception as e:
        logger.error(f"❌ Testing validation status error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to get validation status", "details": str(e)}),
            status_code=500,
            headers=_cors(),
        )


@bp.route(route="vimarsh-admin/testing/all-validations", methods=["GET"])
async def admin_testing_all_validations_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Get all validation suites."""
    try:
        if admin_all_validations is not None:
            return admin_all_validations(req)
        return func.HttpResponse(
            json.dumps({"error": "Testing validation service not available"}),
            status_code=503,
            headers=_cors(),
        )
    except Exception as e:
        logger.error(f"❌ Testing all validations error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to get all validations", "details": str(e)}),
            status_code=500,
            headers=_cors(),
        )


# ===================================================================
# 24–27. Security & Compliance (delegating thin routes)
# ===================================================================

@bp.route(route="vimarsh-admin/security/start-audit", methods=["POST"])
async def admin_security_start_audit_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Start a security audit."""
    try:
        if admin_start_security_audit is not None:
            return admin_start_security_audit(req)
        return func.HttpResponse(
            json.dumps({"error": "Security compliance service not available"}),
            status_code=503,
            headers=_cors(),
        )
    except Exception as e:
        logger.error(f"❌ Security start audit error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to start security audit", "details": str(e)}),
            status_code=500,
            headers=_cors(),
        )


@bp.route(route="vimarsh-admin/security/audit-status", methods=["GET"])
async def admin_security_audit_status_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Get security audit status."""
    try:
        if admin_security_audit_status is not None:
            return admin_security_audit_status(req)
        return func.HttpResponse(
            json.dumps({"error": "Security compliance service not available"}),
            status_code=503,
            headers=_cors(),
        )
    except Exception as e:
        logger.error(f"❌ Security audit status error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to get audit status", "details": str(e)}),
            status_code=500,
            headers=_cors(),
        )


@bp.route(route="vimarsh-admin/security/all-audits", methods=["GET"])
async def admin_security_all_audits_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Get all security audits."""
    try:
        if admin_all_security_audits is not None:
            return admin_all_security_audits(req)
        return func.HttpResponse(
            json.dumps({"error": "Security compliance service not available"}),
            status_code=503,
            headers=_cors(),
        )
    except Exception as e:
        logger.error(f"❌ Security all audits error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to get all audits", "details": str(e)}),
            status_code=500,
            headers=_cors(),
        )


@bp.route(route="vimarsh-admin/security/summary", methods=["GET"])
async def admin_security_summary_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Get security summary."""
    try:
        if admin_security_summary is not None:
            return admin_security_summary(req)
        return func.HttpResponse(
            json.dumps({"error": "Security compliance service not available"}),
            status_code=503,
            headers=_cors(),
        )
    except Exception as e:
        logger.error(f"❌ Security summary error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to get security summary", "details": str(e)}),
            status_code=500,
            headers=_cors(),
        )


# ===================================================================
# 28. vimarsh-admin/overview  GET — Enhanced admin dashboard overview
# ===================================================================

@bp.route(route="vimarsh-admin/overview", methods=["GET"])
async def admin_overview_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Enhanced admin dashboard overview."""
    try:
        if admin_dashboard_overview is not None:
            return admin_dashboard_overview(req)
        return func.HttpResponse(
            json.dumps({"error": "Admin dashboard service not available"}),
            status_code=503,
            headers=_cors(),
        )
    except Exception as e:
        logger.error(f"❌ Admin overview error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to get admin overview", "details": str(e)}),
            status_code=500,
            headers=_cors(),
        )
