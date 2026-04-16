"""
User blueprint — profile, preferences, usage, export, account deletion.

Extracted from function_app.py (lines 3720-4058).
"""

import azure.functions as func
import json
import logging

logger = logging.getLogger(__name__)

bp = func.Blueprint()

# ── service imports (soft) ───────────────────────────────────────────────────
_services_ready = False
preferences_service = None
data_export_service = None
analytics_service = None
_get_engagement_service = None
_verify_token = None
_get_user_from_token = None

try:
    from services.preferences_service import preferences_service as _prefs
    from services.data_export_service import data_export_service as _export
    from engagement.engagement_service import get_engagement_service
    from services.analytics_service import analytics_service as _analytics
    from services.hierarchical_memory_service import HierarchicalMemoryService
    from auth import verify_token, get_user_from_token

    preferences_service = _prefs
    data_export_service = _export
    analytics_service = _analytics
    _get_engagement_service = get_engagement_service
    _verify_token = verify_token
    _get_user_from_token = get_user_from_token
    _memory_service = HierarchicalMemoryService()
    _services_ready = True
    logger.info("✅ User blueprint services imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ User blueprint services not available: {e}")
    _memory_service = None

    def _verify_token(token):
        return None

    def _get_user_from_token(token):
        return None

    def _get_engagement_service():
        return None


# ── helpers ──────────────────────────────────────────────────────────────────

def _cors() -> dict:
    return {
        "Access-Control-Allow-Origin": "https://vimarsh.vedprakash.net",
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "GET, POST, PATCH, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
    }

def _extract_user(req: func.HttpRequest):
    """Return (user_info, user_id) or (None, error_response)."""
    auth_header = req.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None, func.HttpResponse(
            json.dumps({"error": "Missing or invalid authorization header"}),
            status_code=401,
            mimetype="application/json",
            headers=_cors(),
        )
    token = auth_header.replace("Bearer ", "")
    user_info = _get_user_from_token(token)
    if not user_info:
        return None, func.HttpResponse(
            json.dumps({"error": "Invalid or expired token"}),
            status_code=401,
            mimetype="application/json",
            headers=_cors(),
        )
    user_id = user_info.get("sub") or user_info.get("oid")
    if not user_id:
        return None, func.HttpResponse(
            json.dumps({"error": "Could not extract user ID from token"}),
            status_code=400,
            mimetype="application/json",
            headers=_cors(),
        )
    return (user_info, user_id), None


# ── routes ───────────────────────────────────────────────────────────────────

@bp.route(route="user/profile", methods=["GET", "OPTIONS"])
async def get_user_profile(req: func.HttpRequest) -> func.HttpResponse:
    """GET /api/user/profile — complete user profile"""
    if req.method == "OPTIONS":
        return func.HttpResponse(status_code=204, headers=_cors())
    try:
        result, err = _extract_user(req)
        if err:
            return err
        user_info, user_id = result

        prefs = preferences_service.get_preferences(user_id)
        engagement_service = _get_engagement_service()
        journey_stats = engagement_service.get_journey_stats(user_id) if engagement_service else {}
        ai_usage = await analytics_service.get_ai_usage_summary(user_id) if analytics_service else {}

        profile = {
            "user_id": user_id,
            "email": user_info.get("preferred_username") or user_info.get("email"),
            "name": user_info.get("name"),
            "preferences": {
                "experience_preferences": prefs.get("experience_preferences"),
                "notification_preferences": prefs.get("notification_preferences"),
                "memory_preferences": prefs.get("memory_preferences"),
            },
            "journey_stats": journey_stats,
            "ai_usage": ai_usage,
            "member_since": prefs.get("created_at"),
            "last_updated": prefs.get("updated_at"),
        }

        logger.info(f"👤 Retrieved profile for user {user_id}")
        headers = {"Content-Type": "application/json", **_cors()}
        return func.HttpResponse(json.dumps(profile), status_code=200, headers=headers)

    except Exception as e:
        logger.error(f"❌ Error getting user profile: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error", "details": str(e)}),
            status_code=500,
            mimetype="application/json",
            headers=_cors(),
        )


@bp.route(route="user/preferences", methods=["PATCH"])
async def update_user_preferences(req: func.HttpRequest) -> func.HttpResponse:
    """PATCH /api/user/preferences — update user preferences"""
    try:
        result, err = _extract_user(req)
        if err:
            return err
        user_info, user_id = result

        try:
            req_body = req.get_json()
        except ValueError:
            return func.HttpResponse(
                json.dumps({"error": "Invalid JSON in request body"}),
                status_code=400,
                mimetype="application/json",
            )

        try:
            updated_prefs = preferences_service.update_preferences(
                user_id=user_id, updates=req_body, validate=True
            )
            logger.info(f"✅ Updated preferences for user {user_id}")
            return func.HttpResponse(
                json.dumps(
                    {
                        "success": True,
                        "preferences": {
                            "experience_preferences": updated_prefs.get("experience_preferences"),
                            "notification_preferences": updated_prefs.get("notification_preferences"),
                            "memory_preferences": updated_prefs.get("memory_preferences"),
                        },
                        "updated_at": updated_prefs.get("updated_at"),
                    }
                ),
                status_code=200,
                mimetype="application/json",
            )
        except ValueError as e:
            return func.HttpResponse(
                json.dumps({"error": "Validation error", "details": str(e)}),
                status_code=400,
                mimetype="application/json",
            )

    except Exception as e:
        logger.error(f"❌ Error updating user preferences: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error", "details": str(e)}),
            status_code=500,
            mimetype="application/json",
        )


@bp.route(route="user/usage-summary", methods=["GET"])
async def get_usage_summary(req: func.HttpRequest) -> func.HttpResponse:
    """GET /api/user/usage-summary — AI usage and cost summary"""
    try:
        result, err = _extract_user(req)
        if err:
            return err
        user_info, user_id = result

        usage_summary = await analytics_service.get_ai_usage_summary(user_id)
        logger.info(f"💰 Retrieved usage summary for user {user_id}")
        return func.HttpResponse(json.dumps(usage_summary), status_code=200, mimetype="application/json")

    except Exception as e:
        logger.error(f"❌ Error getting usage summary: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error", "details": str(e)}),
            status_code=500,
            mimetype="application/json",
        )


@bp.route(route="user/export", methods=["POST"])
async def export_user_data(req: func.HttpRequest) -> func.HttpResponse:
    """POST /api/user/export — GDPR-compliant data export"""
    try:
        result, err = _extract_user(req)
        if err:
            return err
        user_info, user_id = result

        export_data = await data_export_service.export_user_data(user_id=user_id, include_metadata=True)
        logger.info(f"📦 Exported data for user {user_id}")

        return func.HttpResponse(
            json.dumps(export_data),
            status_code=200,
            mimetype="application/json",
            headers={"Content-Disposition": f"attachment; filename=vimarsh_data_export_{user_id}.json"},
        )

    except Exception as e:
        logger.error(f"❌ Error exporting user data: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error", "details": str(e)}),
            status_code=500,
            mimetype="application/json",
        )


@bp.route(route="user/account", methods=["DELETE"])
async def delete_user_account(req: func.HttpRequest) -> func.HttpResponse:
    """DELETE /api/user/account — delete account and all associated data"""
    try:
        result, err = _extract_user(req)
        if err:
            return err
        user_info, user_id = result

        deletion_summary = await data_export_service.delete_user_data(user_id)
        logger.info(f"🗑️ Deleted account for user {user_id}")

        return func.HttpResponse(
            json.dumps(
                {
                    "success": True,
                    "message": "Account and all associated data deleted successfully",
                    "deletion_summary": deletion_summary,
                }
            ),
            status_code=200,
            mimetype="application/json",
        )

    except Exception as e:
        logger.error(f"❌ Error deleting user account: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error", "details": str(e)}),
            status_code=500,
            mimetype="application/json",
        )


@bp.route(route="conversations", methods=["GET"])
async def get_conversations(req: func.HttpRequest) -> func.HttpResponse:
    """GET /api/conversations — get user's conversation history"""
    try:
        result, err = _extract_user(req)
        if err:
            return err
        user_info, user_id = result

        # Parse query parameters
        limit = int(req.params.get("limit", "50"))
        personality_id = req.params.get("personality_id")
        
        # Cap limit to prevent excessive data retrieval
        limit = min(limit, 100)

        if not _memory_service:
            logger.warning("⚠️ Memory service not available for conversation history")
            return func.HttpResponse(
                json.dumps({"conversations": []}),
                status_code=200,
                mimetype="application/json",
            )

        # Get recent sessions from hierarchical memory service
        sessions = await _memory_service.get_recent_sessions(
            user_id=user_id,
            personality_id=personality_id,
            limit=limit
        )

        # Transform sessions to conversation format expected by frontend
        conversations = []
        for session in sessions:
            conversation = {
                "sessionId": session.session_id,
                "personalityId": session.personality_id,
                "messages": [],  # Session summaries don't include full messages
                "summary": session.summary or "",
                "keyTopics": session.key_topics or [],
                "emotionalJourney": session.emotional_journey or [],
                "createdAt": session.start_time.isoformat() if session.start_time else "",
                "endedAt": session.end_time.isoformat() if session.end_time else "",
                "turnCount": session.turn_count or 0,
            }
            conversations.append(conversation)

        logger.info(f"📜 Retrieved {len(conversations)} conversations for user {user_id}")
        return func.HttpResponse(
            json.dumps({"conversations": conversations}),
            status_code=200,
            mimetype="application/json",
        )

    except ValueError as e:
        return func.HttpResponse(
            json.dumps({"error": "Invalid parameter", "details": str(e)}),
            status_code=400,
            mimetype="application/json",
        )
    except Exception as e:
        logger.error(f"❌ Error getting conversations: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error", "details": str(e)}),
            status_code=500,
            mimetype="application/json",
        )
