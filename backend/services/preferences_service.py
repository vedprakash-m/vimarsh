"""
Preferences Service for Vimarsh
Manages user preferences, settings, and configuration
"""

import logging
import os
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from copy import deepcopy

from azure.cosmos import CosmosClient, exceptions

logger = logging.getLogger(__name__)


class PreferencesService:
    """Service for managing user preferences and settings"""
    
    CONTAINER_NAME = "user_preferences"
    
    # Default preference values
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
            "preferred_time": "09:00",
            "timezone": "UTC",
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
    
    # Validation rules
    VALID_CONVERSATION_STYLES = ["brief", "balanced", "detailed"]
    VALID_LANGUAGES = ["en", "hi"]
    VALID_FORMALITY_LEVELS = ["very_formal", "respectful", "friendly", "casual"]
    VALID_THEMES = ["light", "auto", "dark"]
    VALID_TEXT_SIZES = ["small", "medium", "large"]
    VALID_PRIVACY_MODES = ["standard", "private", "minimal"]
    VALID_TIMEZONES = [
        "UTC", "America/Los_Angeles", "America/Denver", "America/Chicago",
        "America/New_York", "Europe/London", "Europe/Paris",
        "Asia/Kolkata", "Asia/Tokyo", "Australia/Sydney"
    ]
    MAX_FAVORITE_PERSONALITIES = 5
    MIN_DATA_RETENTION_DAYS = 30
    MAX_DATA_RETENTION_DAYS = 365
    
    def __init__(self):
        """Initialize preferences service with Cosmos DB connection"""
        self.container = None
        self._memory_store: Dict[str, Dict] = {}
        self._init_cosmos_db()
    
    def _init_cosmos_db(self):
        """Initialize Cosmos DB connection"""
        try:
            cosmos_endpoint = os.environ.get("COSMOS_ENDPOINT") or os.environ.get("COSMOS_DB_ENDPOINT")
            cosmos_key = os.environ.get("COSMOS_KEY") or os.environ.get("COSMOS_DB_KEY")
            cosmos_database = os.environ.get("AZURE_COSMOS_DATABASE_NAME", "vimarsh-multi-personality")
            
            if not cosmos_endpoint or not cosmos_key:
                logger.warning("⚠️ Cosmos DB credentials not found, preferences will use in-memory storage")
                return
            
            client = CosmosClient(cosmos_endpoint, cosmos_key)
            database = client.get_database_client(cosmos_database)
            
            # Get or create container
            try:
                self.container = database.get_container_client(self.CONTAINER_NAME)
                # Test connection
                self.container.read()
                logger.info(f"✅ Connected to Cosmos DB container: {self.CONTAINER_NAME}")
            except exceptions.CosmosResourceNotFoundError:
                logger.warning(f"⚠️ Container {self.CONTAINER_NAME} not found, will be created during migration")
                self.container = None
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Cosmos DB: {e}")
            self.container = None
    
    def get_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Get user preferences, creating defaults if not exists
        
        Args:
            user_id: User identifier
            
        Returns:
            User preferences dictionary
        """
        try:
            if self.container:
                try:
                    # Query for user preferences
                    query = "SELECT * FROM c WHERE c.user_id = @user_id"
                    parameters = [{"name": "@user_id", "value": user_id}]
                    
                    items = list(self.container.query_items(
                        query=query,
                        parameters=parameters,
                        enable_cross_partition_query=True
                    ))
                    
                    if items:
                        prefs = items[0]
                        logger.info(f"📖 Retrieved preferences for user {user_id}")
                        return prefs
                    else:
                        # Create default preferences
                        logger.info(f"🆕 Creating default preferences for user {user_id}")
                        return self._create_default_preferences(user_id)
                        
                except exceptions.CosmosHttpResponseError as e:
                    logger.error(f"❌ Cosmos DB error retrieving preferences: {e}")
                    return self._create_default_preferences(user_id)
            else:
                # Use in-memory store
                if user_id in self._memory_store:
                    logger.info(f"📖 Retrieved preferences from memory for user {user_id}")
                    return self._memory_store[user_id]
                else:
                    logger.info(f"🆕 Creating default preferences in memory for user {user_id}")
                    prefs = self._create_default_preferences(user_id)
                    self._memory_store[user_id] = prefs
                    return prefs
                    
        except Exception as e:
            logger.error(f"❌ Error getting preferences for user {user_id}: {e}")
            return self._create_default_preferences(user_id)
    
    def update_preferences(
        self,
        user_id: str,
        updates: Dict[str, Any],
        validate: bool = True
    ) -> Dict[str, Any]:
        """
        Update user preferences with validation
        
        Args:
            user_id: User identifier
            updates: Partial preferences to update
            validate: Whether to validate updates
            
        Returns:
            Updated preferences dictionary
            
        Raises:
            ValueError: If validation fails
        """
        try:
            # Get current preferences
            current_prefs = self.get_preferences(user_id)
            
            # Validate updates if requested
            if validate:
                self._validate_preferences(updates)
            
            # Deep merge updates into current preferences
            updated_prefs = self._deep_merge_preferences(current_prefs, updates)
            
            # Update timestamp
            updated_prefs["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            # Save to database or memory
            if self.container:
                try:
                    self.container.upsert_item(updated_prefs)
                    logger.info(f"💾 Updated preferences for user {user_id}")
                except exceptions.CosmosHttpResponseError as e:
                    logger.error(f"❌ Cosmos DB error updating preferences: {e}")
                    raise
            else:
                self._memory_store[user_id] = updated_prefs
                logger.info(f"💾 Updated preferences in memory for user {user_id}")
            
            return updated_prefs
            
        except ValueError as e:
            logger.error(f"❌ Validation error updating preferences: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Error updating preferences for user {user_id}: {e}")
            raise
    
    def delete_preferences(self, user_id: str) -> bool:
        """
        Delete user preferences (for account deletion)
        
        Args:
            user_id: User identifier
            
        Returns:
            True if successful
        """
        try:
            if self.container:
                try:
                    # Get item to delete (need id and partition key)
                    prefs = self.get_preferences(user_id)
                    if prefs:
                        self.container.delete_item(
                            item=prefs["id"],
                            partition_key=user_id
                        )
                        logger.info(f"🗑️ Deleted preferences for user {user_id}")
                        return True
                except exceptions.CosmosResourceNotFoundError:
                    logger.warning(f"⚠️ No preferences found to delete for user {user_id}")
                    return True
            else:
                if user_id in self._memory_store:
                    del self._memory_store[user_id]
                    logger.info(f"🗑️ Deleted preferences from memory for user {user_id}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error deleting preferences for user {user_id}: {e}")
            return False
    
    def get_default_preferences(self) -> Dict[str, Any]:
        """Get default preferences template"""
        return deepcopy(self.DEFAULT_PREFERENCES)
    
    def _create_default_preferences(self, user_id: str) -> Dict[str, Any]:
        """Create default preferences document for user"""
        prefs = {
            "id": f"prefs_{user_id}",
            "user_id": user_id,
            **self.get_default_preferences(),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Save to database or memory
        if self.container:
            try:
                self.container.create_item(prefs)
                logger.info(f"✅ Created default preferences for user {user_id}")
            except exceptions.CosmosHttpResponseError as e:
                logger.error(f"❌ Error creating default preferences: {e}")
        else:
            self._memory_store[user_id] = prefs
        
        return prefs
    
    def _validate_preferences(self, updates: Dict[str, Any]) -> None:
        """
        Validate preference updates
        
        Args:
            updates: Preferences to validate
            
        Raises:
            ValueError: If validation fails
        """
        # Validate experience preferences
        if "experience_preferences" in updates:
            exp_prefs = updates["experience_preferences"]
            
            if "conversation_style" in exp_prefs:
                if exp_prefs["conversation_style"] not in self.VALID_CONVERSATION_STYLES:
                    raise ValueError(f"Invalid conversation_style: {exp_prefs['conversation_style']}")
            
            if "language" in exp_prefs:
                if exp_prefs["language"] not in self.VALID_LANGUAGES:
                    raise ValueError(f"Invalid language: {exp_prefs['language']}")
            
            if "formality" in exp_prefs:
                if exp_prefs["formality"] not in self.VALID_FORMALITY_LEVELS:
                    raise ValueError(f"Invalid formality: {exp_prefs['formality']}")
            
            if "favorite_personalities" in exp_prefs:
                favs = exp_prefs["favorite_personalities"]
                if not isinstance(favs, list):
                    raise ValueError("favorite_personalities must be a list")
                if len(favs) > self.MAX_FAVORITE_PERSONALITIES:
                    raise ValueError(f"favorite_personalities: maximum {self.MAX_FAVORITE_PERSONALITIES} allowed")
            
            if "theme" in exp_prefs:
                if exp_prefs["theme"] not in self.VALID_THEMES:
                    raise ValueError(f"Invalid theme: {exp_prefs['theme']}")
            
            if "text_size" in exp_prefs:
                if exp_prefs["text_size"] not in self.VALID_TEXT_SIZES:
                    raise ValueError(f"Invalid text_size: {exp_prefs['text_size']}")
        
        # Validate notification preferences
        if "notification_preferences" in updates:
            notif_prefs = updates["notification_preferences"]
            
            if "timezone" in notif_prefs:
                if notif_prefs["timezone"] not in self.VALID_TIMEZONES:
                    raise ValueError(f"Invalid timezone: {notif_prefs['timezone']}")
            
            # Validate time formats (HH:MM) - skip validation, will use defaults if invalid
            for time_field in ["preferred_time", "quiet_start", "quiet_end"]:
                if time_field in notif_prefs:
                    time_val = notif_prefs[time_field]
                    if not self._is_valid_time_format(time_val):
                        logger.warning(f"⚠️ Invalid time format for {time_field}: {time_val}, will use default")
                        # Don't raise error, just log warning - let notification service handle defaults
        
        # Validate memory preferences
        if "memory_preferences" in updates:
            mem_prefs = updates["memory_preferences"]
            
            if "privacy_mode" in mem_prefs:
                if mem_prefs["privacy_mode"] not in self.VALID_PRIVACY_MODES:
                    raise ValueError(f"Invalid privacy_mode: {mem_prefs['privacy_mode']}")
            
            if "data_retention_days" in mem_prefs:
                days = mem_prefs["data_retention_days"]
                if not isinstance(days, int):
                    raise ValueError("data_retention_days must be an integer")
                if days < self.MIN_DATA_RETENTION_DAYS or days > self.MAX_DATA_RETENTION_DAYS:
                    raise ValueError(
                        f"data_retention_days must be between {self.MIN_DATA_RETENTION_DAYS} "
                        f"and {self.MAX_DATA_RETENTION_DAYS}"
                    )
    
    def _is_valid_time_format(self, time_str: str) -> bool:
        """Validate time format (HH:MM)"""
        try:
            parts = time_str.split(":")
            if len(parts) != 2:
                return False
            hour, minute = int(parts[0]), int(parts[1])
            return 0 <= hour <= 23 and 0 <= minute <= 59
        except (ValueError, AttributeError):
            return False
    
    def _deep_merge_preferences(
        self,
        current: Dict[str, Any],
        updates: Dict[str, Any],
        is_top_level: bool = True
    ) -> Dict[str, Any]:
        """
        Deep merge preference updates into current preferences.
        Only filters invalid sections at top level.
        
        Args:
            current: Current preferences
            updates: Updates to merge
            is_top_level: Whether this is the top-level call (filters sections)
            
        Returns:
            Merged preferences
        """
        result = deepcopy(current)
        
        # List of valid preference sections (only checked at top level)
        valid_sections = {"experience_preferences", "notification_preferences", "memory_preferences"}
        
        for key, value in updates.items():
            # Only filter invalid sections at top level
            if is_top_level:
                # Skip non-preference keys (id, user_id, created_at, updated_at are allowed)
                if key not in valid_sections and key not in ["id", "user_id", "created_at", "updated_at"]:
                    logger.warning(f"⚠️ Ignoring invalid preference section: {key}")
                    continue
                
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # Recursively merge nested dictionaries (not top level anymore)
                result[key] = self._deep_merge_preferences(result[key], value, is_top_level=False)
            else:
                # Overwrite with new value
                result[key] = value
        
        return result


# Global preferences service instance
preferences_service = PreferencesService()
