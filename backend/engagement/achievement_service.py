"""
Achievement Service for Vimarsh
Manages achievement unlocking, progress tracking, and points/levels.
"""

import logging
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import threading
import time

from azure.cosmos import CosmosClient, PartitionKey, exceptions

from .achievement_definitions import (
    ACHIEVEMENT_DEFINITIONS, 
    get_achievement_by_id,
    calculate_level
)

logger = logging.getLogger(__name__)


class AchievementCache:
    """Simple TTL cache for achievement data"""
    
    def __init__(self, default_ttl: int = 60):
        self._cache: Dict[str, tuple] = {}
        self._lock = threading.Lock()
        self._default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            if key in self._cache:
                value, expiry = self._cache[key]
                if time.time() < expiry:
                    return value
                del self._cache[key]
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        with self._lock:
            expiry = time.time() + (ttl or self._default_ttl)
            self._cache[key] = (value, expiry)
    
    def delete(self, key: str) -> None:
        with self._lock:
            if key in self._cache:
                del self._cache[key]


class AchievementService:
    """Service for managing user achievements and gamification"""
    
    CONTAINER_NAME = "achievements"
    CACHE_TTL_SECONDS = 60  # 1 minute cache
    
    def __init__(self):
        """Initialize achievement service with Cosmos DB connection"""
        self.container = None
        self._cache = AchievementCache(default_ttl=self.CACHE_TTL_SECONDS)
        self._init_cosmos_db()
    
    def _init_cosmos_db(self):
        """Initialize Cosmos DB connection"""
        try:
            cosmos_endpoint = os.environ.get("COSMOS_ENDPOINT") or os.environ.get("COSMOS_DB_ENDPOINT")
            cosmos_key = os.environ.get("COSMOS_KEY") or os.environ.get("COSMOS_DB_KEY")
            cosmos_database = os.environ.get("COSMOS_DATABASE", "vimarsh-db")
            
            if not cosmos_endpoint or not cosmos_key:
                logger.warning("⚠️ Cosmos DB credentials not found, achievements will use in-memory storage")
                self.container = None
                self._memory_store: Dict[str, Dict] = {}
                return
            
            client = CosmosClient(cosmos_endpoint, cosmos_key)
            database = client.get_database_client(cosmos_database)
            
            # Create container if it doesn't exist
            try:
                self.container = database.create_container_if_not_exists(
                    id=self.CONTAINER_NAME,
                    partition_key=PartitionKey(path="/user_id"),
                    offer_throughput=400
                )
                logger.info(f"✅ Achievements container '{self.CONTAINER_NAME}' ready")
            except exceptions.CosmosResourceExistsError:
                self.container = database.get_container_client(self.CONTAINER_NAME)
                logger.info(f"✅ Connected to existing achievements container")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize Cosmos DB for achievements: {e}")
            self.container = None
            self._memory_store = {}
    
    def _generate_id(self, user_id: str) -> str:
        """Generate document ID from user_id"""
        return f"achievements_{user_id}"
    
    async def get_achievement_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get achievement data for a user with caching"""
        try:
            cache_key = f"achievements_{user_id}"
            
            # Check cache first
            cached = self._cache.get(cache_key)
            if cached is not None:
                logger.debug(f"📦 Cache hit for achievement data: {user_id}")
                return cached
            
            doc_id = self._generate_id(user_id)
            
            if self.container:
                try:
                    item = self.container.read_item(item=doc_id, partition_key=user_id)
                    self._cache.set(cache_key, item, self.CACHE_TTL_SECONDS)
                    return item
                except exceptions.CosmosResourceNotFoundError:
                    return None
            else:
                return self._memory_store.get(doc_id)
                
        except Exception as e:
            logger.error(f"❌ Error getting achievement data: {e}")
            return None
    
    async def _create_achievement_data(self, user_id: str) -> Dict[str, Any]:
        """Create initial achievement data for a user"""
        doc_id = self._generate_id(user_id)
        now = datetime.now(timezone.utc).isoformat()
        
        # Initialize progress for all achievements
        achievement_progress = {}
        for aid, achievement in ACHIEVEMENT_DEFINITIONS.items():
            criteria = achievement.get("criteria", {})
            achievement_progress[aid] = {
                "current_value": 0,
                "threshold": criteria.get("threshold", 0) if isinstance(criteria.get("threshold"), int) else None,
                "progress_percentage": 0.0
            }
        
        data = {
            "id": doc_id,
            "user_id": user_id,
            "unlocked_achievements": [],
            "achievement_progress": achievement_progress,
            "total_points": 0,
            "level": 1,
            "level_progress": 0.0,
            "recent_unlocks": [],  # Last 10 unlocked achievements
            "created_at": now,
            "updated_at": now
        }
        
        # Save
        if self.container:
            self.container.create_item(body=data)
        else:
            self._memory_store[doc_id] = data
        
        return data
    
    async def get_all_achievements(self, user_id: str) -> Dict[str, Any]:
        """Get all achievements with user's progress"""
        try:
            data = await self.get_achievement_data(user_id)
            if not data:
                data = await self._create_achievement_data(user_id)
            
            unlocked_ids = set(data.get("unlocked_achievements", []))
            progress = data.get("achievement_progress", {})
            
            achievements = []
            for aid, achievement in ACHIEVEMENT_DEFINITIONS.items():
                is_unlocked = aid in unlocked_ids
                prog = progress.get(aid, {})
                
                achievements.append({
                    "id": aid,
                    "name": achievement["name"],
                    "description": achievement["description"],
                    "icon": achievement["icon"],
                    "points": achievement["points"],
                    "category": achievement["category"],
                    "tier": achievement["tier"],
                    "unlocked": is_unlocked,
                    "unlocked_at": prog.get("unlocked_at") if is_unlocked else None,
                    "progress": {
                        "current": prog.get("current_value", 0),
                        "target": prog.get("threshold"),
                        "percentage": prog.get("progress_percentage", 0)
                    }
                })
            
            # Calculate level info
            level, level_progress = calculate_level(data.get("total_points", 0))
            
            return {
                "achievements": sorted(achievements, key=lambda a: (not a["unlocked"], a["category"])),
                "summary": {
                    "total": len(ACHIEVEMENT_DEFINITIONS),
                    "unlocked": len(unlocked_ids),
                    "total_points": data.get("total_points", 0),
                    "level": level,
                    "level_progress": level_progress
                },
                "recent_unlocks": data.get("recent_unlocks", [])
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting achievements: {e}")
            raise
    
    async def check_and_unlock_achievements(
        self, 
        user_id: str, 
        metrics: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Check if any achievements should be unlocked based on current metrics.
        
        Args:
            user_id: User ID
            metrics: Dict with keys like 'streak', 'conversations', 'personalities_met', etc.
            
        Returns:
            List of newly unlocked achievements
        """
        try:
            data = await self.get_achievement_data(user_id)
            if not data:
                data = await self._create_achievement_data(user_id)
            
            unlocked_ids = set(data.get("unlocked_achievements", []))
            progress = data.get("achievement_progress", {})
            newly_unlocked = []
            now = datetime.now(timezone.utc).isoformat()
            
            for aid, achievement in ACHIEVEMENT_DEFINITIONS.items():
                # Skip already unlocked
                if aid in unlocked_ids:
                    continue
                
                criteria = achievement.get("criteria", {})
                criteria_type = criteria.get("type")
                threshold = criteria.get("threshold")
                
                # Get current value based on criteria type
                current_value = 0
                should_unlock = False
                
                if criteria_type == "streak":
                    current_value = metrics.get("streak", 0)
                    should_unlock = current_value >= threshold
                    
                elif criteria_type == "conversations":
                    current_value = metrics.get("total_conversations", 0)
                    should_unlock = current_value >= threshold
                    
                elif criteria_type == "personalities_met":
                    personalities = metrics.get("personalities_met", [])
                    current_value = len(personalities) if isinstance(personalities, list) else 0
                    should_unlock = current_value >= threshold
                    
                elif criteria_type == "domains_explored":
                    domains = metrics.get("domains_explored", [])
                    current_value = len(domains) if isinstance(domains, list) else 0
                    should_unlock = current_value >= threshold
                    
                elif criteria_type == "insights_saved":
                    current_value = metrics.get("total_insights_saved", 0)
                    should_unlock = current_value >= threshold
                    
                elif criteria_type == "shares":
                    current_value = metrics.get("total_shares", 0)
                    should_unlock = current_value >= threshold
                    
                elif criteria_type == "onboarding":
                    should_unlock = metrics.get("onboarding_complete", False)
                    current_value = 1 if should_unlock else 0
                    
                elif criteria_type == "feature_used":
                    feature = criteria.get("feature")
                    features_used = metrics.get("features_used", [])
                    should_unlock = feature in features_used
                    current_value = 1 if should_unlock else 0
                    
                elif criteria_type == "feature_enabled":
                    feature = criteria.get("feature")
                    features_enabled = metrics.get("features_enabled", [])
                    should_unlock = feature in features_enabled
                    current_value = 1 if should_unlock else 0
                    
                elif criteria_type == "conversation_length":
                    current_value = metrics.get("max_conversation_length", 0)
                    should_unlock = current_value >= threshold
                    
                elif criteria_type == "relationship_level":
                    should_unlock = metrics.get("has_kindred_spirit", False)
                    current_value = 1 if should_unlock else 0
                    
                elif criteria_type == "time_based":
                    condition = criteria.get("condition")
                    current_hour = datetime.now(timezone.utc).hour
                    if condition == "after_midnight":
                        should_unlock = metrics.get("conversation_after_midnight", False)
                    elif condition == "before_6am":
                        should_unlock = metrics.get("conversation_before_6am", False)
                    current_value = 1 if should_unlock else 0
                
                # Update progress
                if aid not in progress:
                    progress[aid] = {}
                    
                progress[aid]["current_value"] = current_value
                if isinstance(threshold, int) and threshold > 0:
                    progress[aid]["threshold"] = threshold
                    progress[aid]["progress_percentage"] = min(100, (current_value / threshold) * 100)
                
                # Unlock if criteria met
                if should_unlock:
                    unlocked_ids.add(aid)
                    progress[aid]["unlocked_at"] = now
                    progress[aid]["progress_percentage"] = 100
                    
                    unlocked_achievement = {
                        "id": aid,
                        "name": achievement["name"],
                        "description": achievement["description"],
                        "icon": achievement["icon"],
                        "points": achievement["points"],
                        "category": achievement["category"],
                        "tier": achievement["tier"],
                        "celebration_message": achievement.get("celebration_message", "Congratulations!"),
                        "unlocked_at": now
                    }
                    newly_unlocked.append(unlocked_achievement)
                    
                    logger.info(f"🏆 Achievement unlocked for {user_id}: {aid}")
            
            # Update data if changes
            if newly_unlocked:
                # Add points
                points_earned = sum(a["points"] for a in newly_unlocked)
                data["total_points"] = data.get("total_points", 0) + points_earned
                
                # Recalculate level
                level, level_progress = calculate_level(data["total_points"])
                data["level"] = level
                data["level_progress"] = level_progress
                
                data["unlocked_achievements"] = list(unlocked_ids)
                data["achievement_progress"] = progress
                
                # Update recent unlocks (keep last 10)
                recent = data.get("recent_unlocks", [])
                for unlock in newly_unlocked:
                    recent.insert(0, {
                        "id": unlock["id"],
                        "name": unlock["name"],
                        "icon": unlock["icon"],
                        "unlocked_at": unlock["unlocked_at"]
                    })
                data["recent_unlocks"] = recent[:10]
                
                data["updated_at"] = now
                await self._save_data(data)
            else:
                # Still save progress updates
                data["achievement_progress"] = progress
                data["updated_at"] = now
                await self._save_data(data)
            
            return newly_unlocked
            
        except Exception as e:
            logger.error(f"❌ Error checking achievements: {e}")
            raise
    
    async def unlock_achievement(self, user_id: str, achievement_id: str) -> Optional[Dict[str, Any]]:
        """Manually unlock a specific achievement"""
        try:
            achievement = get_achievement_by_id(achievement_id)
            if not achievement:
                return None
            
            data = await self.get_achievement_data(user_id)
            if not data:
                data = await self._create_achievement_data(user_id)
            
            unlocked_ids = set(data.get("unlocked_achievements", []))
            
            # Already unlocked
            if achievement_id in unlocked_ids:
                return None
            
            now = datetime.now(timezone.utc).isoformat()
            
            # Unlock
            unlocked_ids.add(achievement_id)
            data["unlocked_achievements"] = list(unlocked_ids)
            
            # Add points
            data["total_points"] = data.get("total_points", 0) + achievement["points"]
            
            # Update level
            level, level_progress = calculate_level(data["total_points"])
            data["level"] = level
            data["level_progress"] = level_progress
            
            # Update progress
            progress = data.get("achievement_progress", {})
            if achievement_id not in progress:
                progress[achievement_id] = {}
            progress[achievement_id]["unlocked_at"] = now
            progress[achievement_id]["progress_percentage"] = 100
            data["achievement_progress"] = progress
            
            # Update recent unlocks
            recent = data.get("recent_unlocks", [])
            recent.insert(0, {
                "id": achievement_id,
                "name": achievement["name"],
                "icon": achievement["icon"],
                "unlocked_at": now
            })
            data["recent_unlocks"] = recent[:10]
            
            data["updated_at"] = now
            await self._save_data(data)
            
            logger.info(f"🏆 Achievement manually unlocked for {user_id}: {achievement_id}")
            
            return {
                "id": achievement_id,
                "name": achievement["name"],
                "description": achievement["description"],
                "icon": achievement["icon"],
                "points": achievement["points"],
                "celebration_message": achievement.get("celebration_message", "Congratulations!"),
                "unlocked_at": now
            }
            
        except Exception as e:
            logger.error(f"❌ Error unlocking achievement: {e}")
            raise
    
    async def _save_data(self, data: Dict[str, Any]) -> None:
        """Save achievement data to database and invalidate cache"""
        try:
            if self.container:
                self.container.upsert_item(body=data)
            else:
                self._memory_store[data["id"]] = data
            
            # Invalidate cache after save
            user_id = data.get("userId")
            if user_id:
                cache_key = f"achievements_{user_id}"
                self._cache.invalidate(cache_key)
                logger.debug(f"🗑️ Invalidated achievement cache: {user_id}")
        except Exception as e:
            logger.error(f"❌ Error saving achievement data: {e}")
            raise


# Singleton instance
_achievement_service = None

def get_achievement_service() -> AchievementService:
    """Get singleton achievement service instance"""
    global _achievement_service
    if _achievement_service is None:
        _achievement_service = AchievementService()
    return _achievement_service
