"""
Notification Timer Trigger
Azure Functions timer trigger for scheduled push notifications.
Handles daily wisdom, streak reminders, and weekly digest notifications.
"""

import azure.functions as func
import logging
import json
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Create blueprint for timer triggers
notification_timer_bp = func.Blueprint()


def get_cosmos_client():
    """Get Cosmos DB client for notification subscriptions."""
    try:
        import os
        from azure.cosmos import CosmosClient
        
        endpoint = os.environ.get("COSMOS_ENDPOINT") or os.environ.get("COSMOSDB_ENDPOINT")
        key = os.environ.get("COSMOS_KEY") or os.environ.get("COSMOSDB_KEY")
        
        if not endpoint or not key:
            logger.warning("Cosmos DB credentials not configured")
            return None, None
            
        client = CosmosClient(endpoint, key)
        database = client.get_database_client(
            os.environ.get("COSMOS_DATABASE", "vimarsh-db")
        )
        
        return client, database
    except Exception as e:
        logger.error(f"Failed to get Cosmos client: {e}")
        return None, None


def get_notification_service():
    """Get notification service instance with preferences integration."""
    try:
        from notifications.notification_service import NotificationService
        from services.preferences_service import PreferencesService
        
        preferences_service = PreferencesService()
        return NotificationService(preferences_service=preferences_service)
    except Exception as e:
        logger.error(f"Failed to get notification service: {e}")
        return None


def get_users_for_notification(
    database,
    notification_type: str,
    current_hour: int,
    timezone_str: str = "UTC"
) -> List[Dict[str, Any]]:
    """
    Get users who should receive notifications at this time.
    
    Args:
        database: Cosmos DB database client
        notification_type: Type of notification to send
        current_hour: Current hour (0-23)
        timezone_str: Timezone string
        
    Returns:
        List of user subscriptions with their preferences
    """
    try:
        container = database.get_container_client("notification_subscriptions")
        
        # Query for active subscriptions where:
        # 1. User has notifications enabled
        # 2. User has this specific notification type enabled
        # 3. User's preferred time matches current hour
        # 4. Current time is not in quiet hours
        
        notification_field_map = {
            "daily_wisdom": "daily_wisdom_enabled",
            "streak_reminder": "streak_reminders_enabled",
            "achievement_unlocked": "achievement_notifications_enabled",
            "weekly_digest": "weekly_summary_enabled"
        }
        
        preference_field = notification_field_map.get(notification_type, "enabled")
        
        query = f"""
            SELECT * FROM c 
            WHERE c.active = true 
            AND c.preferences.enabled = true
            AND c.preferences.{preference_field} = true
            AND c.preferences.preferred_time_hour = @hour
        """
        
        parameters = [{"name": "@hour", "value": current_hour}]
        
        items = list(container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True
        ))
        
        # Filter out users in quiet hours
        filtered_items = []
        for item in items:
            prefs = item.get("preferences", {})
            quiet_start = prefs.get("quiet_hours_start", 22)
            quiet_end = prefs.get("quiet_hours_end", 7)
            
            # Check if current hour is in quiet hours
            if quiet_start > quiet_end:
                # Quiet hours span midnight (e.g., 22:00 - 07:00)
                if current_hour >= quiet_start or current_hour < quiet_end:
                    continue
            else:
                # Quiet hours don't span midnight
                if quiet_start <= current_hour < quiet_end:
                    continue
            
            filtered_items.append(item)
        
        return filtered_items
        
    except Exception as e:
        logger.error(f"Failed to get users for notification: {e}")
        return []


def get_users_with_at_risk_streaks(database) -> List[Dict[str, Any]]:
    """
    Get users whose streaks are at risk (haven't engaged today and it's getting late).
    """
    try:
        # Get user activity container
        activity_container = database.get_container_client("user_activity")
        subscriptions_container = database.get_container_client("notification_subscriptions")
        
        # Get today's date
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Get users with active streaks who haven't engaged today
        # This would need to be refined based on actual data schema
        query = """
            SELECT c.user_id, c.current_streak, c.last_activity_date
            FROM c 
            WHERE c.current_streak > 0
            AND c.last_activity_date = @yesterday
        """
        
        parameters = [{"name": "@yesterday", "value": yesterday}]
        
        at_risk_users = list(activity_container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True
        ))
        
        # Get subscriptions for these users
        result = []
        for user in at_risk_users:
            user_id = user.get("user_id")
            try:
                sub_query = "SELECT * FROM c WHERE c.user_id = @user_id AND c.active = true"
                sub_params = [{"name": "@user_id", "value": user_id}]
                
                subscriptions = list(subscriptions_container.query_items(
                    query=sub_query,
                    parameters=sub_params,
                    enable_cross_partition_query=True
                ))
                
                for sub in subscriptions:
                    if sub.get("preferences", {}).get("streak_reminders_enabled", True):
                        result.append({
                            **sub,
                            "current_streak": user.get("current_streak", 0),
                            "last_activity_date": user.get("last_activity_date")
                        })
                        
            except Exception as e:
                logger.warning(f"Failed to get subscription for user {user_id}: {e}")
                continue
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to get at-risk streak users: {e}")
        return []


@notification_timer_bp.timer_trigger(
    schedule="0 0 * * * *",  # Run every hour at minute 0
    arg_name="timer",
    run_on_startup=False
)
async def daily_wisdom_trigger(timer: func.TimerRequest) -> None:
    """
    Timer trigger for daily wisdom notifications.
    Runs every hour to send notifications to users whose preferred time matches.
    """
    logger.info("🕐 Daily wisdom trigger fired")
    
    if timer.past_due:
        logger.warning("Timer is past due")
    
    try:
        _, database = get_cosmos_client()
        notification_service = get_notification_service()
        
        if not database or not notification_service:
            logger.error("Required services not available")
            return
        
        # Get current hour in UTC
        current_hour = datetime.now(timezone.utc).hour
        
        # Get users who should receive daily wisdom at this hour
        users = get_users_for_notification(
            database,
            "daily_wisdom",
            current_hour
        )
        
        logger.info(f"Found {len(users)} users for daily wisdom at hour {current_hour}")
        
        # Send notifications
        from notifications.content_service import ContentService
        content_service = ContentService()
        
        success_count = 0
        failure_count = 0
        
        for user in users:
            try:
                user_id = user.get("user_id")
                
                # Get user's favorite personality or default
                favorite_personality = user.get("favorite_personality", "krishna")
                
                # Generate personalized content
                content = await content_service.generate_daily_wisdom(
                    personality=favorite_personality
                )
                
                # Send notification
                result = await notification_service.send_notification(
                    user_id=user_id,
                    title=content.get("title", "Daily Wisdom"),
                    body=content.get("body", "Your daily wisdom awaits"),
                    data={
                        "category": "daily_wisdom",
                        "personality": favorite_personality,
                        "url": "/"
                    }
                )
                
                if result.get("success"):
                    success_count += 1
                else:
                    failure_count += 1
                    
            except Exception as e:
                logger.error(f"Failed to send daily wisdom to user: {e}")
                failure_count += 1
        
        logger.info(f"✅ Daily wisdom: {success_count} sent, {failure_count} failed")
        
    except Exception as e:
        logger.error(f"❌ Daily wisdom trigger error: {e}")


@notification_timer_bp.timer_trigger(
    schedule="0 0 18 * * *",  # Run at 6 PM UTC daily
    arg_name="timer",
    run_on_startup=False
)
async def streak_reminder_trigger(timer: func.TimerRequest) -> None:
    """
    Timer trigger for streak reminders.
    Sends reminders to users whose streaks are at risk.
    """
    logger.info("🔥 Streak reminder trigger fired")
    
    if timer.past_due:
        logger.warning("Timer is past due")
    
    try:
        _, database = get_cosmos_client()
        notification_service = get_notification_service()
        
        if not database or not notification_service:
            logger.error("Required services not available")
            return
        
        # Get users with at-risk streaks
        at_risk_users = get_users_with_at_risk_streaks(database)
        
        logger.info(f"Found {len(at_risk_users)} users with at-risk streaks")
        
        # Send notifications
        from notifications.content_service import ContentService
        content_service = ContentService()
        
        success_count = 0
        failure_count = 0
        
        for user in at_risk_users:
            try:
                user_id = user.get("user_id")
                current_streak = user.get("current_streak", 0)
                
                # Generate streak reminder content
                content = await content_service.generate_streak_reminder(
                    streak_count=current_streak,
                    at_risk=True
                )
                
                # Send notification
                result = await notification_service.send_notification(
                    user_id=user_id,
                    title=content.get("title", "Your streak is at risk!"),
                    body=content.get("body", f"Keep your {current_streak}-day streak alive!"),
                    data={
                        "category": "streak_at_risk",
                        "current_streak": current_streak,
                        "url": "/"
                    }
                )
                
                if result.get("success"):
                    success_count += 1
                else:
                    failure_count += 1
                    
            except Exception as e:
                logger.error(f"Failed to send streak reminder to user: {e}")
                failure_count += 1
        
        logger.info(f"✅ Streak reminders: {success_count} sent, {failure_count} failed")
        
    except Exception as e:
        logger.error(f"❌ Streak reminder trigger error: {e}")


@notification_timer_bp.timer_trigger(
    schedule="0 0 10 * * 0",  # Run at 10 AM UTC every Sunday
    arg_name="timer",
    run_on_startup=False
)
async def weekly_digest_trigger(timer: func.TimerRequest) -> None:
    """
    Timer trigger for weekly digest notifications.
    Sends weekly summary to users every Sunday.
    """
    logger.info("📊 Weekly digest trigger fired")
    
    if timer.past_due:
        logger.warning("Timer is past due")
    
    try:
        _, database = get_cosmos_client()
        notification_service = get_notification_service()
        
        if not database or not notification_service:
            logger.error("Required services not available")
            return
        
        # Get current hour
        current_hour = 10  # 10 AM UTC
        
        # Get users who want weekly summary
        users = get_users_for_notification(
            database,
            "weekly_digest",
            current_hour
        )
        
        logger.info(f"Found {len(users)} users for weekly digest")
        
        success_count = 0
        failure_count = 0
        
        for user in users:
            try:
                user_id = user.get("user_id")
                
                # Get user stats for the week
                # This would need to be implemented based on actual data
                conversations_count = 7  # Placeholder
                streak_days = 5  # Placeholder
                
                # Send notification
                result = await notification_service.send_notification(
                    user_id=user_id,
                    title="📊 Your Weekly Wisdom Summary",
                    body=f"This week: {conversations_count} conversations, {streak_days} day streak!",
                    data={
                        "category": "weekly_digest",
                        "url": "/profile"
                    }
                )
                
                if result.get("success"):
                    success_count += 1
                else:
                    failure_count += 1
                    
            except Exception as e:
                logger.error(f"Failed to send weekly digest to user: {e}")
                failure_count += 1
        
        logger.info(f"✅ Weekly digest: {success_count} sent, {failure_count} failed")
        
    except Exception as e:
        logger.error(f"❌ Weekly digest trigger error: {e}")


def register_notification_timers(app: func.FunctionApp) -> None:
    """Register notification timer triggers with the function app."""
    try:
        app.register_functions(notification_timer_bp)
        logger.info("✅ Notification timer triggers registered")
    except Exception as e:
        logger.error(f"Failed to register notification timers: {e}")
