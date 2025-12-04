"""
Migration Script: Initialize Engagement Data for Existing Users
Vimarsh Engagement System - Phase 4 Integration

This script initializes engagement data (streaks, achievements, activity tracking)
for all existing users in the Vimarsh database.

Usage:
    python data/migrate_engagement_data.py [--dry-run] [--user-id USER_ID]

Options:
    --dry-run       Show what would be migrated without making changes
    --user-id       Migrate only a specific user (for testing)
"""

import asyncio
import argparse
import logging
import os
import sys
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from azure.cosmos import CosmosClient, PartitionKey, exceptions

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EngagementMigration:
    """Migration utility to initialize engagement data for existing users"""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.client = None
        self.database = None
        self.users_migrated = 0
        self.users_skipped = 0
        self.errors = []
        
        self._init_cosmos_db()
    
    def _init_cosmos_db(self):
        """Initialize Cosmos DB connection"""
        cosmos_endpoint = os.environ.get("COSMOS_ENDPOINT") or os.environ.get("COSMOS_DB_ENDPOINT")
        cosmos_key = os.environ.get("COSMOS_KEY") or os.environ.get("COSMOS_DB_KEY")
        cosmos_database = os.environ.get("COSMOS_DATABASE", "vimarsh-db")
        
        if not cosmos_endpoint or not cosmos_key:
            raise ValueError("COSMOS_ENDPOINT and COSMOS_KEY environment variables are required")
        
        self.client = CosmosClient(cosmos_endpoint, cosmos_key)
        self.database = self.client.get_database_client(cosmos_database)
        logger.info(f"✅ Connected to Cosmos DB database: {cosmos_database}")
    
    def _get_or_create_container(self, container_name: str, partition_key: str = "/user_id") -> Any:
        """Get or create a container"""
        try:
            container = self.database.create_container_if_not_exists(
                id=container_name,
                partition_key=PartitionKey(path=partition_key),
                offer_throughput=400
            )
            return container
        except exceptions.CosmosResourceExistsError:
            return self.database.get_container_client(container_name)
    
    async def get_existing_users(self) -> List[str]:
        """Get list of all existing user IDs from conversation memory"""
        user_ids = set()
        
        # Check conversation_memory container
        try:
            memory_container = self.database.get_container_client("conversation_memory")
            query = "SELECT DISTINCT c.user_id FROM c WHERE IS_DEFINED(c.user_id)"
            items = list(memory_container.query_items(query=query, enable_cross_partition_query=True))
            for item in items:
                if item.get("user_id") and item["user_id"] != "anonymous":
                    user_ids.add(item["user_id"])
            logger.info(f"📚 Found {len(user_ids)} users in conversation_memory")
        except exceptions.CosmosResourceNotFoundError:
            logger.warning("⚠️ conversation_memory container not found")
        except Exception as e:
            logger.warning(f"⚠️ Error reading conversation_memory: {e}")
        
        # Check user_profiles container (if exists)
        try:
            profiles_container = self.database.get_container_client("user_profiles")
            query = "SELECT c.user_id FROM c WHERE IS_DEFINED(c.user_id)"
            items = list(profiles_container.query_items(query=query, enable_cross_partition_query=True))
            for item in items:
                if item.get("user_id") and item["user_id"] != "anonymous":
                    user_ids.add(item["user_id"])
            logger.info(f"👤 Found additional users in user_profiles")
        except exceptions.CosmosResourceNotFoundError:
            logger.warning("⚠️ user_profiles container not found")
        except Exception as e:
            logger.warning(f"⚠️ Error reading user_profiles: {e}")
        
        # Check onboarding_state container (if exists)
        try:
            onboarding_container = self.database.get_container_client("onboarding_state")
            query = "SELECT c.user_id FROM c WHERE IS_DEFINED(c.user_id)"
            items = list(onboarding_container.query_items(query=query, enable_cross_partition_query=True))
            for item in items:
                if item.get("user_id") and item["user_id"] != "anonymous":
                    user_ids.add(item["user_id"])
            logger.info(f"🎓 Found additional users in onboarding_state")
        except exceptions.CosmosResourceNotFoundError:
            pass  # Container may not exist yet
        except Exception as e:
            logger.warning(f"⚠️ Error reading onboarding_state: {e}")
        
        return list(user_ids)
    
    async def get_user_activity_stats(self, user_id: str) -> Dict[str, Any]:
        """Get existing activity statistics for a user from conversation history"""
        stats = {
            "total_conversations": 0,
            "personalities_met": [],
            "domains_explored": [],
            "first_conversation_date": None,
            "last_conversation_date": None
        }
        
        try:
            memory_container = self.database.get_container_client("conversation_memory")
            query = f"SELECT * FROM c WHERE c.user_id = '{user_id}'"
            items = list(memory_container.query_items(query=query, enable_cross_partition_query=True))
            
            personalities = set()
            domains = set()
            earliest_date = None
            latest_date = None
            
            for item in items:
                stats["total_conversations"] += 1
                
                personality_id = item.get("personality_id")
                if personality_id:
                    personalities.add(personality_id)
                    # Map personality to domain
                    domain = self._get_domain_for_personality(personality_id)
                    if domain:
                        domains.add(domain)
                
                timestamp = item.get("created_at") or item.get("timestamp")
                if timestamp:
                    try:
                        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                        if earliest_date is None or dt < earliest_date:
                            earliest_date = dt
                        if latest_date is None or dt > latest_date:
                            latest_date = dt
                    except:
                        pass
            
            stats["personalities_met"] = list(personalities)
            stats["domains_explored"] = list(domains)
            stats["first_conversation_date"] = earliest_date.isoformat() if earliest_date else None
            stats["last_conversation_date"] = latest_date.isoformat() if latest_date else None
            
        except Exception as e:
            logger.warning(f"⚠️ Error getting activity stats for {user_id}: {e}")
        
        return stats
    
    def _get_domain_for_personality(self, personality_id: str) -> Optional[str]:
        """Map personality ID to domain"""
        domain_map = {
            # Spiritual domain
            "krishna": "spiritual",
            "buddha": "spiritual",
            "jesus": "spiritual",
            "rumi": "spiritual",
            "vivekananda": "spiritual",
            # Philosophical domain
            "marcus_aurelius": "philosophical",
            "lao_tzu": "philosophical",
            "confucius": "philosophical",
            "aristotle": "philosophical",
            "plato": "philosophical",
            "socrates": "philosophical",
            # Leadership domain
            "chanakya": "leadership",
            "lincoln": "leadership",
            "franklin": "leadership",
            "washington": "leadership",
            "gandhi": "leadership",
            "mlk": "leadership",
            # Scientific domain
            "einstein": "scientific",
            "newton": "scientific",
            "tesla": "scientific",
            "archimedes": "scientific",
            "davinci": "scientific",
            # Literary domain
            "tagore": "literary",
            "shakespeare": "literary",
            # Psychology domain
            "freud": "psychology"
        }
        return domain_map.get(personality_id.lower())
    
    async def migrate_user(self, user_id: str) -> bool:
        """Migrate a single user to the engagement system"""
        try:
            # Get containers
            engagement_container = self._get_or_create_container("engagement_tracking")
            achievements_container = self._get_or_create_container("achievements")
            
            now = datetime.now(timezone.utc)
            
            # Check if user already has engagement data
            engagement_doc_id = f"engagement_{user_id}"
            try:
                existing = engagement_container.read_item(
                    item=engagement_doc_id,
                    partition_key=user_id
                )
                logger.info(f"⏭️ Skipping {user_id} - engagement data already exists")
                self.users_skipped += 1
                return True
            except exceptions.CosmosResourceNotFoundError:
                pass  # No existing data, proceed with migration
            
            # Get user's historical activity
            stats = await self.get_user_activity_stats(user_id)
            
            # Calculate initial streak based on last activity
            current_streak = 0
            if stats["last_conversation_date"]:
                try:
                    last_date = datetime.fromisoformat(stats["last_conversation_date"])
                    days_since = (now - last_date).days
                    if days_since <= 1:
                        current_streak = 1  # Active today or yesterday
                except:
                    pass
            
            # Create engagement data
            engagement_data = {
                "id": engagement_doc_id,
                "user_id": user_id,
                "streaks": {
                    "current_streak": current_streak,
                    "longest_streak": current_streak,
                    "streak_start_date": now.date().isoformat() if current_streak > 0 else None,
                    "last_activity_date": stats["last_conversation_date"][:10] if stats["last_conversation_date"] else None,
                    "streak_history": [],
                    "grace_period_used": False,
                    "freeze_count": 0,
                    "freeze_used_dates": []
                },
                "daily_activity": {},
                "weekly_summary": {
                    "week_of": (now.date() - timedelta(days=now.weekday())).isoformat(),
                    "total_conversations": 0,
                    "unique_personalities": [],
                    "domains_explored": [],
                    "insights_saved": 0,
                    "total_time_minutes": 0
                },
                "milestones": {
                    "first_conversation": {
                        "achieved": stats["total_conversations"] > 0,
                        "date": stats["first_conversation_date"][:10] if stats["first_conversation_date"] else None
                    },
                    "streak_3_days": {"achieved": False, "date": None},
                    "streak_7_days": {"achieved": False, "date": None},
                    "streak_30_days": {"achieved": False, "date": None},
                    "all_domains_explored": {
                        "achieved": len(stats["domains_explored"]) >= 6,
                        "date": None
                    }
                },
                "stats": {
                    "total_conversations": stats["total_conversations"],
                    "total_insights_saved": 0,
                    "total_shares": 0,
                    "personalities_met": stats["personalities_met"],
                    "domains_explored": stats["domains_explored"]
                },
                "notification_schedule": {
                    "daily_reminder_time": "08:00",
                    "timezone": "UTC",
                    "enabled": False,
                    "last_sent": None
                },
                "created_at": now.isoformat(),
                "updated_at": now.isoformat(),
                "migrated_at": now.isoformat(),
                "migration_version": "1.0"
            }
            
            # Create achievements data
            achievements_doc_id = f"achievements_{user_id}"
            
            # Initialize achievement progress
            achievement_progress = {}
            unlocked_achievements = []
            total_points = 0
            
            # Check for auto-unlockable achievements based on stats
            if stats["total_conversations"] > 0:
                # First Steps achievement
                achievement_progress["first_steps"] = {
                    "current_value": 1,
                    "threshold": 1,
                    "progress_percentage": 100,
                    "unlocked_at": stats["first_conversation_date"]
                }
                unlocked_achievements.append("first_steps")
                total_points += 10
            
            if stats["total_conversations"] >= 10:
                achievement_progress["seeker_10"] = {
                    "current_value": stats["total_conversations"],
                    "threshold": 10,
                    "progress_percentage": 100,
                    "unlocked_at": now.isoformat()
                }
                unlocked_achievements.append("seeker_10")
                total_points += 25
            
            if stats["total_conversations"] >= 50:
                achievement_progress["seeker_50"] = {
                    "current_value": stats["total_conversations"],
                    "threshold": 50,
                    "progress_percentage": 100,
                    "unlocked_at": now.isoformat()
                }
                unlocked_achievements.append("seeker_50")
                total_points += 50
            
            if len(stats["personalities_met"]) >= 5:
                achievement_progress["social_5"] = {
                    "current_value": len(stats["personalities_met"]),
                    "threshold": 5,
                    "progress_percentage": 100,
                    "unlocked_at": now.isoformat()
                }
                unlocked_achievements.append("social_5")
                total_points += 30
            
            if len(stats["domains_explored"]) >= 3:
                achievement_progress["explorer_3"] = {
                    "current_value": len(stats["domains_explored"]),
                    "threshold": 3,
                    "progress_percentage": 100,
                    "unlocked_at": now.isoformat()
                }
                unlocked_achievements.append("explorer_3")
                total_points += 30
            
            if len(stats["domains_explored"]) >= 6:
                achievement_progress["explorer_6"] = {
                    "current_value": 6,
                    "threshold": 6,
                    "progress_percentage": 100,
                    "unlocked_at": now.isoformat()
                }
                unlocked_achievements.append("explorer_6")
                total_points += 100
            
            # Calculate level from points
            level = 1
            level_progress = 0.0
            points_for_level = [0, 100, 250, 500, 1000, 2000]
            for i, threshold in enumerate(points_for_level):
                if total_points >= threshold:
                    level = i + 1
                    if i + 1 < len(points_for_level):
                        next_threshold = points_for_level[i + 1]
                        level_progress = (total_points - threshold) / (next_threshold - threshold) * 100
            
            achievements_data = {
                "id": achievements_doc_id,
                "user_id": user_id,
                "unlocked_achievements": unlocked_achievements,
                "achievement_progress": achievement_progress,
                "total_points": total_points,
                "level": level,
                "level_progress": level_progress,
                "recent_unlocks": [
                    {"id": aid, "unlocked_at": now.isoformat()}
                    for aid in unlocked_achievements[:10]
                ],
                "created_at": now.isoformat(),
                "updated_at": now.isoformat(),
                "migrated_at": now.isoformat(),
                "migration_version": "1.0"
            }
            
            # Save to database (if not dry run)
            if not self.dry_run:
                engagement_container.create_item(body=engagement_data)
                achievements_container.create_item(body=achievements_data)
                logger.info(f"✅ Migrated user {user_id}: {stats['total_conversations']} convos, {len(unlocked_achievements)} achievements")
            else:
                logger.info(f"🔍 [DRY RUN] Would migrate user {user_id}: {stats['total_conversations']} convos, {len(unlocked_achievements)} achievements")
            
            self.users_migrated += 1
            return True
            
        except Exception as e:
            logger.error(f"❌ Error migrating user {user_id}: {e}")
            self.errors.append({"user_id": user_id, "error": str(e)})
            return False
    
    async def run_migration(self, specific_user: Optional[str] = None):
        """Run the migration for all users or a specific user"""
        logger.info("=" * 60)
        logger.info("🚀 Starting Engagement Data Migration")
        logger.info(f"   Dry Run: {self.dry_run}")
        logger.info("=" * 60)
        
        if specific_user:
            users = [specific_user]
            logger.info(f"📋 Migrating specific user: {specific_user}")
        else:
            users = await self.get_existing_users()
            logger.info(f"📋 Found {len(users)} existing users to migrate")
        
        if not users:
            logger.info("✨ No users to migrate")
            return
        
        # Process users
        for i, user_id in enumerate(users, 1):
            logger.info(f"[{i}/{len(users)}] Processing user: {user_id}")
            await self.migrate_user(user_id)
        
        # Summary
        logger.info("=" * 60)
        logger.info("📊 Migration Summary")
        logger.info(f"   Users migrated: {self.users_migrated}")
        logger.info(f"   Users skipped: {self.users_skipped}")
        logger.info(f"   Errors: {len(self.errors)}")
        
        if self.errors:
            logger.info("   Failed users:")
            for err in self.errors:
                logger.info(f"     - {err['user_id']}: {err['error']}")
        
        logger.info("=" * 60)
        
        if self.dry_run:
            logger.info("🔍 This was a DRY RUN. No data was modified.")
            logger.info("   Run without --dry-run to apply changes.")


async def main():
    parser = argparse.ArgumentParser(description="Migrate engagement data for existing users")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be migrated without making changes")
    parser.add_argument("--user-id", type=str, help="Migrate only a specific user")
    args = parser.parse_args()
    
    migration = EngagementMigration(dry_run=args.dry_run)
    await migration.run_migration(specific_user=args.user_id)


if __name__ == "__main__":
    asyncio.run(main())
