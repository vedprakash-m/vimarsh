"""
Engagement API endpoints for Vimarsh
Provides REST API for streaks, achievements, and gamification.
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
        "Access-Control-Allow-Origin": "https://vimarsh.vedprakash.net",
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "GET, POST, PUT, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization"
    }


def register_engagement_routes(app: func.FunctionApp):
    """Register all engagement API routes with the function app"""
    
    # =========================================================================
    # STREAK ENDPOINTS
    # =========================================================================
    
    @app.route(route="engagement/streaks", methods=["GET"])
    async def get_streak_data(req: func.HttpRequest) -> func.HttpResponse:
        """Get streak data for a user"""
        try:
            user_id = req.params.get("user_id")
            
            if not user_id:
                return func.HttpResponse(
                    json.dumps({"error": "user_id parameter is required"}),
                    status_code=400,
                    headers=get_cors_headers()
                )
            
            from engagement import get_engagement_service
            engagement_service = get_engagement_service()
            
            streak_data = await engagement_service.get_or_create_streak_data(user_id)
            
            return func.HttpResponse(
                json.dumps({
                    "success": True,
                    "data": streak_data,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }),
                status_code=200,
                headers=get_cors_headers()
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to get streak data: {e}")
            return func.HttpResponse(
                json.dumps({"error": "Failed to get streak data", "details": str(e)}),
                status_code=500,
                headers=get_cors_headers()
            )
    
    @app.route(route="engagement/activity", methods=["POST"])
    async def record_activity(req: func.HttpRequest) -> func.HttpResponse:
        """Record user activity for streak tracking"""
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
            activity_type = body.get("activity_type", "conversation")
            personality_id = body.get("personality_id")
            domain = body.get("domain")
            metadata = body.get("metadata", {})
            
            if not user_id:
                return func.HttpResponse(
                    json.dumps({"error": "user_id is required"}),
                    status_code=400,
                    headers=get_cors_headers()
                )
            
            from engagement import get_engagement_service
            engagement_service = get_engagement_service()
            
            result = await engagement_service.record_daily_activity(
                user_id=user_id,
                activity_type=activity_type,
                personality_id=personality_id,
                domain=domain,
                metadata=metadata
            )
            
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
            logger.error(f"❌ Failed to record activity: {e}")
            return func.HttpResponse(
                json.dumps({"error": "Failed to record activity", "details": str(e)}),
                status_code=500,
                headers=get_cors_headers()
            )
    
    @app.route(route="engagement/streaks/freeze", methods=["POST"])
    async def use_streak_freeze(req: func.HttpRequest) -> func.HttpResponse:
        """Use a streak freeze to protect the streak"""
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
            
            from engagement import get_engagement_service
            engagement_service = get_engagement_service()
            
            result = await engagement_service.use_streak_freeze(user_id)
            
            return func.HttpResponse(
                json.dumps({
                    "success": result.get("success", False),
                    "result": result,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }),
                status_code=200 if result.get("success") else 400,
                headers=get_cors_headers()
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to use streak freeze: {e}")
            return func.HttpResponse(
                json.dumps({"error": "Failed to use streak freeze", "details": str(e)}),
                status_code=500,
                headers=get_cors_headers()
            )
    
    @app.route(route="engagement/summary", methods=["GET"])
    async def get_weekly_summary(req: func.HttpRequest) -> func.HttpResponse:
        """Get weekly engagement summary for a user"""
        try:
            user_id = req.params.get("user_id")
            
            if not user_id:
                return func.HttpResponse(
                    json.dumps({"error": "user_id parameter is required"}),
                    status_code=400,
                    headers=get_cors_headers()
                )
            
            from engagement import get_engagement_service
            engagement_service = get_engagement_service()
            
            summary = await engagement_service.get_weekly_summary(user_id)
            
            return func.HttpResponse(
                json.dumps({
                    "success": True,
                    "summary": summary,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }),
                status_code=200,
                headers=get_cors_headers()
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to get weekly summary: {e}")
            return func.HttpResponse(
                json.dumps({"error": "Failed to get weekly summary", "details": str(e)}),
                status_code=500,
                headers=get_cors_headers()
            )
    
    # =========================================================================
    # ACHIEVEMENT ENDPOINTS
    # =========================================================================
    
    @app.route(route="engagement/achievements", methods=["GET"])
    async def get_achievements(req: func.HttpRequest) -> func.HttpResponse:
        """Get all achievements with user progress"""
        try:
            user_id = req.params.get("user_id")
            
            if not user_id:
                return func.HttpResponse(
                    json.dumps({"error": "user_id parameter is required"}),
                    status_code=400,
                    headers=get_cors_headers()
                )
            
            from engagement import get_achievement_service
            achievement_service = get_achievement_service()
            
            achievements = await achievement_service.get_all_achievements(user_id)
            
            return func.HttpResponse(
                json.dumps({
                    "success": True,
                    "data": achievements,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }),
                status_code=200,
                headers=get_cors_headers()
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to get achievements: {e}")
            return func.HttpResponse(
                json.dumps({"error": "Failed to get achievements", "details": str(e)}),
                status_code=500,
                headers=get_cors_headers()
            )
    
    @app.route(route="engagement/achievements/check", methods=["POST"])
    async def check_achievements(req: func.HttpRequest) -> func.HttpResponse:
        """Check if any achievements should be unlocked based on metrics"""
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
            metrics = body.get("metrics", {})
            
            if not user_id:
                return func.HttpResponse(
                    json.dumps({"error": "user_id is required"}),
                    status_code=400,
                    headers=get_cors_headers()
                )
            
            from engagement import get_achievement_service
            achievement_service = get_achievement_service()
            
            newly_unlocked = await achievement_service.check_and_unlock_achievements(
                user_id=user_id,
                metrics=metrics
            )
            
            return func.HttpResponse(
                json.dumps({
                    "success": True,
                    "newly_unlocked": newly_unlocked,
                    "unlocked_count": len(newly_unlocked),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }),
                status_code=200,
                headers=get_cors_headers()
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to check achievements: {e}")
            return func.HttpResponse(
                json.dumps({"error": "Failed to check achievements", "details": str(e)}),
                status_code=500,
                headers=get_cors_headers()
            )
    
    @app.route(route="engagement/achievements/unlock", methods=["POST"])
    async def unlock_achievement(req: func.HttpRequest) -> func.HttpResponse:
        """Manually unlock a specific achievement"""
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
            achievement_id = body.get("achievement_id")
            
            if not user_id or not achievement_id:
                return func.HttpResponse(
                    json.dumps({"error": "user_id and achievement_id are required"}),
                    status_code=400,
                    headers=get_cors_headers()
                )
            
            from engagement import get_achievement_service
            achievement_service = get_achievement_service()
            
            unlocked = await achievement_service.unlock_achievement(user_id, achievement_id)
            
            if unlocked:
                return func.HttpResponse(
                    json.dumps({
                        "success": True,
                        "achievement": unlocked,
                        "message": f"🏆 Achievement '{unlocked['name']}' unlocked!",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }),
                    status_code=200,
                    headers=get_cors_headers()
                )
            else:
                return func.HttpResponse(
                    json.dumps({
                        "success": False,
                        "message": "Achievement not found or already unlocked",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }),
                    status_code=400,
                    headers=get_cors_headers()
                )
            
        except Exception as e:
            logger.error(f"❌ Failed to unlock achievement: {e}")
            return func.HttpResponse(
                json.dumps({"error": "Failed to unlock achievement", "details": str(e)}),
                status_code=500,
                headers=get_cors_headers()
            )
    
    # =========================================================================
    # COMBINED ENGAGEMENT DASHBOARD
    # =========================================================================
    
    @app.route(route="engagement/dashboard", methods=["GET"])
    async def get_engagement_dashboard(req: func.HttpRequest) -> func.HttpResponse:
        """Get combined engagement dashboard data (streaks + achievements + stats)"""
        try:
            user_id = req.params.get("user_id")
            
            if not user_id:
                return func.HttpResponse(
                    json.dumps({"error": "user_id parameter is required"}),
                    status_code=400,
                    headers=get_cors_headers()
                )
            
            from engagement import get_engagement_service, get_achievement_service
            engagement_service = get_engagement_service()
            achievement_service = get_achievement_service()
            
            # Gather all data
            streak_data = await engagement_service.get_or_create_streak_data(user_id)
            achievements = await achievement_service.get_all_achievements(user_id)
            weekly_summary = await engagement_service.get_weekly_summary(user_id)
            
            dashboard = {
                "streaks": {
                    "current_streak": streak_data.get("current_streak", 0),
                    "longest_streak": streak_data.get("longest_streak", 0),
                    "streak_freezes_available": streak_data.get("streak_freezes_available", 0),
                    "last_active_date": streak_data.get("last_active_date"),
                    "streak_at_risk": streak_data.get("streak_at_risk", False)
                },
                "achievements": {
                    "total": achievements["summary"]["total"],
                    "unlocked": achievements["summary"]["unlocked"],
                    "total_points": achievements["summary"]["total_points"],
                    "level": achievements["summary"]["level"],
                    "level_progress": achievements["summary"]["level_progress"],
                    "recent_unlocks": achievements.get("recent_unlocks", [])[:5]
                },
                "weekly_activity": weekly_summary,
                "engagement_score": _calculate_engagement_score(streak_data, achievements)
            }
            
            return func.HttpResponse(
                json.dumps({
                    "success": True,
                    "dashboard": dashboard,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }),
                status_code=200,
                headers=get_cors_headers()
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to get engagement dashboard: {e}")
            return func.HttpResponse(
                json.dumps({"error": "Failed to get dashboard", "details": str(e)}),
                status_code=500,
                headers=get_cors_headers()
            )
    
    logger.info("✅ Engagement API routes registered successfully")


def _calculate_engagement_score(streak_data: Dict[str, Any], achievements: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate an overall engagement score"""
    # Base score from streak
    streak_score = min(streak_data.get("current_streak", 0) * 10, 100)
    
    # Bonus from achievements
    total_achievements = achievements["summary"]["total"]
    unlocked = achievements["summary"]["unlocked"]
    achievement_percentage = (unlocked / total_achievements * 100) if total_achievements > 0 else 0
    
    # Combined score
    overall_score = (streak_score + achievement_percentage) / 2
    
    # Determine tier
    if overall_score >= 80:
        tier = "legendary"
        tier_label = "🌟 Legendary Seeker"
    elif overall_score >= 60:
        tier = "master"
        tier_label = "✨ Master Seeker"
    elif overall_score >= 40:
        tier = "dedicated"
        tier_label = "🔥 Dedicated Seeker"
    elif overall_score >= 20:
        tier = "active"
        tier_label = "💫 Active Seeker"
    else:
        tier = "beginner"
        tier_label = "🌱 Beginning Seeker"
    
    return {
        "score": round(overall_score, 1),
        "tier": tier,
        "tier_label": tier_label,
        "streak_contribution": round(streak_score, 1),
        "achievement_contribution": round(achievement_percentage, 1)
    }
