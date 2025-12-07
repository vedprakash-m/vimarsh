"""
Migrate existing users to have default preferences
Creates preference documents for all users who don't have them yet
"""

import os
import logging
from typing import List, Dict, Any
from datetime import datetime, timezone
from azure.cosmos import CosmosClient, exceptions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Default preferences (matches PreferencesService.DEFAULT_PREFERENCES)
DEFAULT_PREFERENCES = {
    "experience_preferences": {
        "conversation_style": "balanced",
        "language": "en",
        "formality": "respectful",
        "favorite_personalities": [],
        "theme": "auto",
        "text_size": "medium",
        "reduce_animations": False
    },
    "notification_preferences": {
        "daily_wisdom_enabled": True,
        "preferred_time": "08:00",
        "timezone": "America/Los_Angeles",
        "quiet_hours_enabled": False,
        "quiet_start": "22:00",
        "quiet_end": "07:00",
        "types": {
            "daily_wisdom": True,
            "streak_reminders": True,
            "achievements": True,
            "weekly_summary": True
        }
    },
    "memory_preferences": {
        "remember_conversations": True,
        "connect_insights": True,
        "track_emotions": True,
        "suggest_topics": True,
        "privacy_mode": "standard",
        "data_retention_days": 90,
        "analytics_consent": True,
        "research_consent": False
    }
}


def get_existing_users(database) -> List[str]:
    """
    Get list of unique user_ids from engagement_tracking container
    
    Args:
        database: Cosmos DB database client
        
    Returns:
        List of unique user IDs
    """
    try:
        container = database.get_container_client("engagement_tracking")
        
        # Query for distinct user_ids
        query = "SELECT DISTINCT c.user_id FROM c"
        items = list(container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        
        user_ids = [item["user_id"] for item in items if item.get("user_id")]
        logger.info(f"📊 Found {len(user_ids)} existing users")
        return user_ids
        
    except exceptions.CosmosResourceNotFoundError:
        logger.warning("⚠️ engagement_tracking container not found")
        return []
    except Exception as e:
        logger.error(f"❌ Error getting existing users: {e}")
        return []


def get_users_with_preferences(preferences_container) -> List[str]:
    """
    Get list of user_ids who already have preferences
    
    Args:
        preferences_container: user_preferences container client
        
    Returns:
        List of user IDs with existing preferences
    """
    try:
        query = "SELECT c.user_id FROM c"
        items = list(preferences_container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        
        user_ids = [item["user_id"] for item in items if item.get("user_id")]
        logger.info(f"📊 Found {len(user_ids)} users with existing preferences")
        return user_ids
        
    except Exception as e:
        logger.error(f"❌ Error getting users with preferences: {e}")
        return []


def create_default_preferences(user_id: str) -> Dict[str, Any]:
    """
    Create default preferences document for user
    
    Args:
        user_id: User identifier
        
    Returns:
        Preferences document
    """
    now = datetime.now(timezone.utc).isoformat()
    
    return {
        "id": f"prefs_{user_id}",
        "user_id": user_id,
        **DEFAULT_PREFERENCES,
        "created_at": now,
        "updated_at": now
    }


def migrate_user_preferences(dry_run: bool = False):
    """
    Migrate existing users to have default preferences
    
    Args:
        dry_run: If True, only report what would be done without making changes
    """
    try:
        # Get Cosmos DB credentials
        cosmos_endpoint = os.environ.get("COSMOS_ENDPOINT") or os.environ.get("COSMOS_DB_ENDPOINT")
        cosmos_key = os.environ.get("COSMOS_KEY") or os.environ.get("COSMOS_DB_KEY")
        cosmos_database = os.environ.get("COSMOS_DATABASE", "vimarsh-db")
        
        if not cosmos_endpoint or not cosmos_key:
            logger.error("❌ Cosmos DB credentials not found in environment")
            return
        
        logger.info(f"🔗 Connecting to Cosmos DB: {cosmos_endpoint}")
        client = CosmosClient(cosmos_endpoint, cosmos_key)
        database = client.get_database_client(cosmos_database)
        
        # Get containers
        try:
            preferences_container = database.get_container_client("user_preferences")
        except exceptions.CosmosResourceNotFoundError:
            logger.error("❌ user_preferences container not found. Run create_user_preferences_container.py first")
            return
        
        # Get existing users
        logger.info("🔍 Finding existing users...")
        all_users = get_existing_users(database)
        
        if not all_users:
            logger.warning("⚠️ No existing users found")
            return
        
        # Get users who already have preferences
        users_with_prefs = get_users_with_preferences(preferences_container)
        
        # Find users who need preferences
        users_without_prefs = [uid for uid in all_users if uid not in users_with_prefs]
        
        logger.info(f"📊 Migration Summary:")
        logger.info(f"   - Total users: {len(all_users)}")
        logger.info(f"   - Users with preferences: {len(users_with_prefs)}")
        logger.info(f"   - Users needing migration: {len(users_without_prefs)}")
        
        if not users_without_prefs:
            logger.info("✅ All users already have preferences")
            return
        
        if dry_run:
            logger.info("🔍 DRY RUN MODE - No changes will be made")
            logger.info(f"📋 Would create preferences for {len(users_without_prefs)} users:")
            for user_id in users_without_prefs[:10]:  # Show first 10
                logger.info(f"   - {user_id}")
            if len(users_without_prefs) > 10:
                logger.info(f"   ... and {len(users_without_prefs) - 10} more")
            return
        
        # Migrate users
        logger.info(f"🚀 Starting migration for {len(users_without_prefs)} users...")
        
        success_count = 0
        error_count = 0
        
        for i, user_id in enumerate(users_without_prefs, 1):
            try:
                prefs = create_default_preferences(user_id)
                preferences_container.create_item(prefs)
                success_count += 1
                
                if i % 10 == 0:
                    logger.info(f"📊 Progress: {i}/{len(users_without_prefs)} ({success_count} success, {error_count} errors)")
                
            except Exception as e:
                error_count += 1
                logger.error(f"❌ Error creating preferences for {user_id}: {e}")
        
        logger.info(f"✅ Migration completed:")
        logger.info(f"   - Successfully created: {success_count}")
        logger.info(f"   - Errors: {error_count}")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        raise


if __name__ == "__main__":
    import sys
    
    logger.info("=" * 80)
    logger.info("🚀 Starting user preferences migration")
    logger.info("=" * 80)
    
    # Check for dry-run flag
    dry_run = "--dry-run" in sys.argv
    
    if dry_run:
        logger.info("🔍 Running in DRY RUN mode")
    
    try:
        migrate_user_preferences(dry_run=dry_run)
        logger.info("=" * 80)
        logger.info("✅ Migration process completed")
        logger.info("=" * 80)
    except Exception as e:
        logger.error("=" * 80)
        logger.error(f"❌ Migration failed: {e}")
        logger.error("=" * 80)
        exit(1)
