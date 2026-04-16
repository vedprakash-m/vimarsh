"""
Engagement Service for Vimarsh
Manages user streaks, daily activity tracking, and engagement metrics.
"""

import logging
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta, date
from collections import defaultdict
from functools import lru_cache
import threading
import time

from azure.cosmos import CosmosClient, PartitionKey, exceptions

logger = logging.getLogger(__name__)


class TTLCache:
    """Simple TTL cache for engagement data"""
    
    def __init__(self, default_ttl: int = 60):
        self._cache: Dict[str, tuple] = {}  # {key: (value, expiry_time)}
        self._lock = threading.Lock()
        self._default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        with self._lock:
            if key in self._cache:
                value, expiry = self._cache[key]
                if time.time() < expiry:
                    return value
                else:
                    del self._cache[key]
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL"""
        with self._lock:
            expiry = time.time() + (ttl or self._default_ttl)
            self._cache[key] = (value, expiry)
    
    def delete(self, key: str) -> None:
        """Delete value from cache"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
    
    def clear(self) -> None:
        """Clear all cached values"""
        with self._lock:
            self._cache.clear()
    
    def cleanup(self) -> int:
        """Remove expired entries and return count removed"""
        with self._lock:
            now = time.time()
            expired = [k for k, (_, exp) in self._cache.items() if exp <= now]
            for k in expired:
                del self._cache[k]
            return len(expired)


class EngagementService:
    """Service for tracking user engagement, streaks, and daily activity"""
    
    CONTAINER_NAME = "engagement_tracking"
    
    # Grace period for streak (hours before streak breaks)
    STREAK_GRACE_HOURS = 36  # 1.5 days grace period
    
    # Max streak freezes per month
    MAX_FREEZES_PER_MONTH = 2
    
    # Cache TTL in seconds
    CACHE_TTL_SECONDS = 60  # 1 minute cache for engagement data
    STREAK_CACHE_TTL_SECONDS = 30  # 30 seconds for streak info (more volatile)
    
    def __init__(self):
        """Initialize engagement service with Cosmos DB connection"""
        self.container = None
        self._cache = TTLCache(default_ttl=self.CACHE_TTL_SECONDS)
        self._init_cosmos_db()
    
    def _init_cosmos_db(self):
        """Initialize Cosmos DB connection"""
        try:
            cosmos_endpoint = os.environ.get("COSMOS_ENDPOINT") or os.environ.get("COSMOS_DB_ENDPOINT")
            cosmos_key = os.environ.get("COSMOS_KEY") or os.environ.get("COSMOS_DB_KEY")
            cosmos_database = os.environ.get("COSMOS_DATABASE", "vimarsh-db")
            
            if not cosmos_endpoint or not cosmos_key:
                logger.warning("⚠️ Cosmos DB credentials not found, engagement will use in-memory storage")
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
                logger.info(f"✅ Engagement container '{self.CONTAINER_NAME}' ready")
            except exceptions.CosmosResourceExistsError:
                self.container = database.get_container_client(self.CONTAINER_NAME)
                logger.info(f"✅ Connected to existing engagement container")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize Cosmos DB for engagement: {e}")
            self.container = None
            self._memory_store = {}
    
    def _generate_id(self, user_id: str) -> str:
        """Generate document ID from user_id"""
        return f"engagement_{user_id}"
    
    def _get_today_str(self) -> str:
        """Get today's date as ISO string"""
        return datetime.now(timezone.utc).date().isoformat()
    
    async def get_engagement_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get engagement data for a user with caching"""
        try:
            cache_key = f"engagement_{user_id}"
            
            # Check cache first
            cached = self._cache.get(cache_key)
            if cached is not None:
                logger.debug(f"📦 Cache hit for engagement data: {user_id}")
                return cached
            
            doc_id = self._generate_id(user_id)
            
            if self.container:
                try:
                    item = self.container.read_item(item=doc_id, partition_key=user_id)
                    # Cache the result
                    self._cache.set(cache_key, item, self.CACHE_TTL_SECONDS)
                    return item
                except exceptions.CosmosResourceNotFoundError:
                    return None
            else:
                data = self._memory_store.get(doc_id)
                if data:
                    self._cache.set(cache_key, data, self.CACHE_TTL_SECONDS)
                return data
                
        except Exception as e:
            logger.error(f"❌ Error getting engagement data: {e}")
            return None
    
    async def _create_engagement_data(self, user_id: str) -> Dict[str, Any]:
        """Create initial engagement data for a user"""
        doc_id = self._generate_id(user_id)
        now = datetime.now(timezone.utc)
        today = now.date().isoformat()
        
        data = {
            "id": doc_id,
            "user_id": user_id,
            "streaks": {
                "current_streak": 0,
                "longest_streak": 0,
                "streak_start_date": None,
                "last_activity_date": None,
                "streak_history": [],
                "grace_period_used": False,
                "freeze_count": 0,
                "freeze_used_dates": []
            },
            "daily_activity": {},
            "weekly_summary": {
                "week_of": self._get_week_start(now).isoformat(),
                "total_conversations": 0,
                "unique_personalities": [],
                "domains_explored": [],
                "insights_saved": 0,
                "total_time_minutes": 0
            },
            "milestones": {
                "first_conversation": {"achieved": False, "date": None},
                "streak_3_days": {"achieved": False, "date": None},
                "streak_7_days": {"achieved": False, "date": None},
                "streak_30_days": {"achieved": False, "date": None},
                "all_domains_explored": {"achieved": False, "date": None}
            },
            "stats": {
                "total_conversations": 0,
                "total_insights_saved": 0,
                "total_shares": 0,
                "personalities_met": [],
                "domains_explored": []
            },
            "notification_schedule": {
                "daily_reminder_time": "08:00",
                "timezone": "UTC",
                "enabled": False,
                "last_sent": None
            },
            "created_at": now.isoformat(),
            "updated_at": now.isoformat()
        }
        
        # Save
        if self.container:
            self.container.create_item(body=data)
        else:
            self._memory_store[doc_id] = data
        
        return data
    
    def _get_week_start(self, dt: datetime) -> date:
        """Get the Monday of the week for a given date"""
        return (dt.date() - timedelta(days=dt.weekday()))
    
    async def record_check_in(self, user_id: str) -> Dict[str, Any]:
        """Record a daily check-in and update streak"""
        try:
            data = await self.get_engagement_data(user_id)
            if not data:
                data = await self._create_engagement_data(user_id)
            
            now = datetime.now(timezone.utc)
            today = now.date().isoformat()
            streaks = data.get("streaks", {})
            
            last_activity = streaks.get("last_activity_date")
            current_streak = streaks.get("current_streak", 0)
            
            # Check if already checked in today
            if last_activity == today:
                return {
                    "success": True,
                    "already_checked_in": True,
                    "current_streak": current_streak,
                    "message": "Already checked in today"
                }
            
            # Calculate streak
            if last_activity:
                last_date = datetime.fromisoformat(last_activity).date()
                today_date = now.date()
                days_diff = (today_date - last_date).days
                
                if days_diff == 1:
                    # Perfect continuation
                    current_streak += 1
                    streaks["grace_period_used"] = False
                elif days_diff == 2 and not streaks.get("grace_period_used"):
                    # Grace period (missed one day)
                    current_streak += 1
                    streaks["grace_period_used"] = True
                    logger.info(f"🔥 Grace period used for {user_id}")
                elif days_diff > 2 or (days_diff == 2 and streaks.get("grace_period_used")):
                    # Streak broken
                    if current_streak > 0:
                        # Save to history
                        streaks.setdefault("streak_history", []).append({
                            "start": streaks.get("streak_start_date"),
                            "end": last_activity,
                            "length": current_streak
                        })
                    # Reset
                    current_streak = 1
                    streaks["streak_start_date"] = today
                    streaks["grace_period_used"] = False
                else:
                    # Same day or unexpected case
                    pass
            else:
                # First activity ever
                current_streak = 1
                streaks["streak_start_date"] = today
            
            # Update streak data
            streaks["current_streak"] = current_streak
            streaks["last_activity_date"] = today
            
            # Update longest streak
            if current_streak > streaks.get("longest_streak", 0):
                streaks["longest_streak"] = current_streak
            
            data["streaks"] = streaks
            data["updated_at"] = now.isoformat()
            
            # Initialize daily activity for today
            if today not in data.get("daily_activity", {}):
                data["daily_activity"][today] = {
                    "conversations": 0,
                    "personalities_engaged": [],
                    "insights_saved": 0,
                    "time_spent_minutes": 0,
                    "first_activity_at": now.isoformat()
                }
            
            await self._save_data(data)
            
            # Check for streak milestones
            milestone_achieved = None
            if current_streak == 3 and not data.get("milestones", {}).get("streak_3_days", {}).get("achieved"):
                milestone_achieved = "streak_3_days"
            elif current_streak == 7 and not data.get("milestones", {}).get("streak_7_days", {}).get("achieved"):
                milestone_achieved = "streak_7_days"
            elif current_streak == 30 and not data.get("milestones", {}).get("streak_30_days", {}).get("achieved"):
                milestone_achieved = "streak_30_days"
            
            if milestone_achieved:
                data["milestones"][milestone_achieved] = {
                    "achieved": True,
                    "date": today
                }
                await self._save_data(data)
            
            logger.info(f"🔥 Check-in recorded for {user_id}: streak={current_streak}")
            
            return {
                "success": True,
                "already_checked_in": False,
                "current_streak": current_streak,
                "longest_streak": streaks["longest_streak"],
                "milestone_achieved": milestone_achieved,
                "grace_period_used": streaks["grace_period_used"]
            }
            
        except Exception as e:
            logger.error(f"❌ Error recording check-in: {e}")
            raise
    
    async def record_activity(
        self, 
        user_id: str, 
        activity_type: str, 
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Record a user activity.
        
        activity_type: 'conversation', 'insight_saved', 'share', 'voice_used', etc.
        metadata: Additional data like personality_id, duration, etc.
        """
        try:
            data = await self.get_engagement_data(user_id)
            if not data:
                data = await self._create_engagement_data(user_id)
            
            now = datetime.now(timezone.utc)
            today = now.date().isoformat()
            metadata = metadata or {}
            
            # Ensure daily activity exists
            if today not in data.get("daily_activity", {}):
                data["daily_activity"][today] = {
                    "conversations": 0,
                    "personalities_engaged": [],
                    "insights_saved": 0,
                    "time_spent_minutes": 0,
                    "first_activity_at": now.isoformat()
                }
            
            daily = data["daily_activity"][today]
            stats = data.get("stats", {})
            
            # Process by activity type
            if activity_type == "conversation":
                daily["conversations"] = daily.get("conversations", 0) + 1
                stats["total_conversations"] = stats.get("total_conversations", 0) + 1
                
                personality = metadata.get("personality_id")
                if personality:
                    if personality not in daily.get("personalities_engaged", []):
                        daily.setdefault("personalities_engaged", []).append(personality)
                    if personality not in stats.get("personalities_met", []):
                        stats.setdefault("personalities_met", []).append(personality)
                
                domain = metadata.get("domain")
                if domain and domain not in stats.get("domains_explored", []):
                    stats.setdefault("domains_explored", []).append(domain)
                
                # Check first conversation milestone
                if stats["total_conversations"] == 1:
                    data.setdefault("milestones", {})["first_conversation"] = {
                        "achieved": True,
                        "date": today
                    }
                    
            elif activity_type == "insight_saved":
                daily["insights_saved"] = daily.get("insights_saved", 0) + 1
                stats["total_insights_saved"] = stats.get("total_insights_saved", 0) + 1
                
            elif activity_type == "share":
                stats["total_shares"] = stats.get("total_shares", 0) + 1
                
            elif activity_type == "time_spent":
                minutes = metadata.get("minutes", 0)
                daily["time_spent_minutes"] = daily.get("time_spent_minutes", 0) + minutes
            
            data["daily_activity"][today] = daily
            data["stats"] = stats
            data["updated_at"] = now.isoformat()
            
            # Update weekly summary
            await self._update_weekly_summary(data, now)
            
            await self._save_data(data)
            
            return {
                "success": True,
                "activity_type": activity_type,
                "daily_stats": daily,
                "total_stats": stats
            }
            
        except Exception as e:
            logger.error(f"❌ Error recording activity: {e}")
            raise
    
    async def _update_weekly_summary(self, data: Dict, now: datetime):
        """Update weekly summary in engagement data"""
        week_start = self._get_week_start(now).isoformat()
        weekly = data.get("weekly_summary", {})
        
        # Reset if new week
        if weekly.get("week_of") != week_start:
            weekly = {
                "week_of": week_start,
                "total_conversations": 0,
                "unique_personalities": [],
                "domains_explored": [],
                "insights_saved": 0,
                "total_time_minutes": 0
            }
        
        # Aggregate from daily activity for this week
        total_convos = 0
        all_personalities = set()
        all_domains = set()
        total_insights = 0
        total_time = 0
        
        week_start_date = datetime.fromisoformat(week_start).date()
        for day_str, day_data in data.get("daily_activity", {}).items():
            try:
                day_date = datetime.fromisoformat(day_str).date()
                if day_date >= week_start_date:
                    total_convos += day_data.get("conversations", 0)
                    all_personalities.update(day_data.get("personalities_engaged", []))
                    total_insights += day_data.get("insights_saved", 0)
                    total_time += day_data.get("time_spent_minutes", 0)
            except:
                pass
        
        weekly["total_conversations"] = total_convos
        weekly["unique_personalities"] = list(all_personalities)
        weekly["domains_explored"] = list(all_domains)
        weekly["insights_saved"] = total_insights
        weekly["total_time_minutes"] = total_time
        
        data["weekly_summary"] = weekly
    
    async def get_streak_info(self, user_id: str) -> Dict[str, Any]:
        """Get current streak information for a user"""
        try:
            data = await self.get_engagement_data(user_id)
            if not data:
                return {
                    "current_streak": 0,
                    "longest_streak": 0,
                    "streak_start_date": None,
                    "last_activity_date": None,
                    "is_active_today": False,
                    "streak_at_risk": False
                }
            
            streaks = data.get("streaks", {})
            today = self._get_today_str()
            
            # Check if streak is at risk
            last_activity = streaks.get("last_activity_date")
            streak_at_risk = False
            if last_activity and last_activity != today:
                last_date = datetime.fromisoformat(last_activity).date()
                today_date = datetime.now(timezone.utc).date()
                days_diff = (today_date - last_date).days
                if days_diff >= 1:
                    streak_at_risk = True
            
            return {
                "current_streak": streaks.get("current_streak", 0),
                "longest_streak": streaks.get("longest_streak", 0),
                "streak_start_date": streaks.get("streak_start_date"),
                "last_activity_date": last_activity,
                "is_active_today": last_activity == today,
                "streak_at_risk": streak_at_risk,
                "grace_period_used": streaks.get("grace_period_used", False),
                "freeze_count": streaks.get("freeze_count", 0)
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting streak info: {e}")
            return {"current_streak": 0, "longest_streak": 0}
    
    async def get_user_streak(self, user_id: str) -> int:
        """Get current streak count for a user"""
        info = await self.get_streak_info(user_id)
        return info.get("current_streak", 0)

    async def get_progress_summary(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive progress summary for dashboard"""
        try:
            data = await self.get_engagement_data(user_id)
            if not data:
                return {
                    "streak": {"current_streak": 0, "longest_streak": 0},
                    "stats": {},
                    "weekly_activity": [],
                    "milestones": {}
                }
            
            # Build weekly activity for last 7 days
            weekly_activity = []
            today = datetime.now(timezone.utc).date()
            for i in range(7):
                day = today - timedelta(days=6-i)
                day_str = day.isoformat()
                day_data = data.get("daily_activity", {}).get(day_str, {})
                weekly_activity.append({
                    "date": day_str,
                    "day_name": day.strftime("%a"),
                    "conversations": day_data.get("conversations", 0),
                    "time_spent_minutes": day_data.get("time_spent_minutes", 0),
                    "insights_saved": day_data.get("insights_saved", 0),
                    "active": day_data.get("conversations", 0) > 0
                })
            
            return {
                "streak": data.get("streaks", {}),
                "stats": data.get("stats", {}),
                "weekly_activity": weekly_activity,
                "weekly_summary": data.get("weekly_summary", {}),
                "milestones": data.get("milestones", {}),
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting progress summary: {e}")
            raise
    
    async def freeze_streak(self, user_id: str) -> Dict[str, Any]:
        """Use a streak freeze to prevent streak loss"""
        try:
            data = await self.get_engagement_data(user_id)
            if not data:
                return {"success": False, "error": "No engagement data found"}
            
            streaks = data.get("streaks", {})
            now = datetime.now(timezone.utc)
            today = now.date().isoformat()
            
            # Check if already used max freezes this month
            current_month = now.strftime("%Y-%m")
            freeze_dates = streaks.get("freeze_used_dates", [])
            month_freezes = [d for d in freeze_dates if d.startswith(current_month)]
            
            if len(month_freezes) >= self.MAX_FREEZES_PER_MONTH:
                return {
                    "success": False,
                    "error": f"Maximum {self.MAX_FREEZES_PER_MONTH} freezes per month reached"
                }
            
            # Apply freeze
            freeze_dates.append(today)
            streaks["freeze_used_dates"] = freeze_dates
            streaks["freeze_count"] = len(freeze_dates)
            streaks["last_activity_date"] = today  # Extend the streak
            
            data["streaks"] = streaks
            data["updated_at"] = now.isoformat()
            
            await self._save_data(data)
            
            return {
                "success": True,
                "freezes_remaining": self.MAX_FREEZES_PER_MONTH - len(month_freezes) - 1,
                "current_streak": streaks.get("current_streak", 0)
            }
            
        except Exception as e:
            logger.error(f"❌ Error freezing streak: {e}")
            raise
    
    async def _save_data(self, data: Dict[str, Any]) -> None:
        """Save engagement data to database and invalidate cache"""
        try:
            user_id = data.get("user_id")
            
            if self.container:
                self.container.upsert_item(body=data)
            else:
                self._memory_store[data["id"]] = data
            
            # Invalidate cache for this user
            if user_id:
                cache_key = f"engagement_{user_id}"
                self._cache.delete(cache_key)
                logger.debug(f"🗑️ Cache invalidated for: {user_id}")
                
        except Exception as e:
            logger.error(f"❌ Error saving engagement data: {e}")
            raise
    
    def get_journey_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive journey statistics for user (synchronous).

        Args:
            user_id: User identifier

        Returns:
            Dictionary with journey stats including streak, conversations, achievements, etc.
        """
        try:
            # Read streak data synchronously from in-memory store (Cosmos path is async)
            doc_id = self._generate_id(user_id)
            data: Dict = {}

            if self.container:
                try:
                    data = self.container.read_item(item=doc_id, partition_key=user_id)
                except Exception:
                    data = {}
            else:
                data = getattr(self, "_memory_store", {}).get(doc_id, {})

            streaks = data.get("streaks", {})
            stats = data.get("stats", {})

            # Get conversation count
            conversation_count = self._get_conversation_count(user_id)

            # Calculate wisdom level based on activity
            wisdom_level = self._calculate_wisdom_level(conversation_count)

            # Get domain exploration breakdown
            domain_exploration = self._get_domain_exploration(user_id)

            result = {
                "current_streak": streaks.get("current_streak", 0),
                "longest_streak": streaks.get("longest_streak", 0),
                "total_conversations": conversation_count,
                "achievements_unlocked": 0,
                "wisdom_level": wisdom_level,
                "domain_exploration": domain_exploration,
            }

            logger.info(f"📊 Retrieved journey stats for user {user_id}")
            return result

        except Exception as e:
            logger.error(f"❌ Error getting journey stats for user {user_id}: {e}")
            return {
                "current_streak": 0,
                "longest_streak": 0,
                "total_conversations": 0,
                "achievements_unlocked": 0,
                "wisdom_level": "Seeker",
                "domain_exploration": {},
            }

    
    def _get_conversation_count(self, user_id: str) -> int:
        """Get total conversation count for user"""
        try:
            if self.container:
                # Query for all activity records
                query = "SELECT VALUE COUNT(1) FROM c WHERE c.user_id = @user_id"
                parameters = [{"name": "@user_id", "value": user_id}]
                
                result = list(self.container.query_items(
                    query=query,
                    parameters=parameters,
                    enable_cross_partition_query=True
                ))
                
                return result[0] if result else 0
            else:
                # Count from memory store
                return len([
                    item for item in self._memory_store.values()
                    if item.get("user_id") == user_id
                ])
                
        except Exception as e:
            logger.error(f"❌ Error getting conversation count: {e}")
            return 0
    
    def _calculate_wisdom_level(self, conversation_count: int) -> str:
        """Calculate wisdom level based on conversation count"""
        if conversation_count < 5:
            return "Seeker"
        elif conversation_count < 20:
            return "Student"
        elif conversation_count < 50:
            return "Practitioner"
        elif conversation_count < 100:
            return "Scholar"
        elif conversation_count < 200:
            return "Sage"
        else:
            return "Master"
    
    def _get_domain_exploration(self, user_id: str) -> Dict[str, int]:
        """Get conversation breakdown by domain"""
        try:
            # Initialize domain counts
            domains = {
                "spiritual": 0,
                "philosophical": 0,
                "leadership": 0,
                "scientific": 0,
                "literary": 0,
                "psychology": 0
            }
            
            if self.container:
                # Query for personality usage (assuming personality field contains personality_id)
                query = "SELECT c.personality FROM c WHERE c.user_id = @user_id"
                parameters = [{"name": "@user_id", "value": user_id}]
                
                items = list(self.container.query_items(
                    query=query,
                    parameters=parameters,
                    enable_cross_partition_query=True
                ))
                
                # Map personalities to domains (this is a simplified mapping)
                personality_domain_map = {
                    "krishna": "spiritual",
                    "buddha": "spiritual",
                    "jesus": "spiritual",
                    "rumi": "spiritual",
                    "vivekananda": "spiritual",
                    "marcus": "philosophical",
                    "laotzu": "philosophical",
                    "confucius": "philosophical",
                    "aristotle": "philosophical",
                    "plato": "philosophical",
                    "socrates": "philosophical",
                    "chanakya": "leadership",
                    "lincoln": "leadership",
                    "franklin": "leadership",
                    "washington": "leadership",
                    "gandhi": "leadership",
                    "mlk": "leadership",
                    "einstein": "scientific",
                    "newton": "scientific",
                    "tesla": "scientific",
                    "archimedes": "scientific",
                    "davinci": "scientific",
                    "tagore": "literary",
                    "shakespeare": "literary",
                    "freud": "psychology"
                }
                
                # Count domain usage
                for item in items:
                    personality = item.get("personality", "").lower()
                    domain = personality_domain_map.get(personality, "philosophical")
                    if domain in domains:
                        domains[domain] += 1
            else:
                # Use memory store
                for item in self._memory_store.values():
                    if item.get("user_id") == user_id:
                        personality = item.get("personality", "").lower()
                        # Simple domain detection (can be enhanced)
                        if personality:
                            domains["philosophical"] += 1
            
            return domains
            
        except Exception as e:
            logger.error(f"❌ Error getting domain exploration: {e}")
            return {
                "spiritual": 0,
                "philosophical": 0,
                "leadership": 0,
                "scientific": 0,
                "literary": 0,
                "psychology": 0
            }


# Singleton instance
_engagement_service = None

def get_engagement_service() -> EngagementService:
    """Get singleton engagement service instance"""
    global _engagement_service
    if _engagement_service is None:
        _engagement_service = EngagementService()
    return _engagement_service
