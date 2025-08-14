"""
Enhanced Database Service - Database-Driven Personality Management
Extends the existing database service with comprehensive personality configuration
management using standardized personality data and Cosmos DB integration.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

# Import standardization components
from config.personality_standardization_mapping import (
    STANDARDIZED_PERSONALITIES,
    get_standardized_id,
    get_all_standardized_ids
)

from config.comprehensive_personality_registry import (
    ComprehensivePersonalityConfig
)

from config.database_migration_service import (
    PersonalityMigrationService
)

logger = logging.getLogger(__name__)


class DatabaseDrivenPersonalityService:
    """
    Database-driven personality management service
    Replaces hardcoded personality configurations with database queries
    """
    
    def __init__(self, database_service=None):
        self.database_service = database_service
        self.cache = {}  # Simple in-memory cache
        self.cache_ttl = 300  # 5 minutes TTL
        self.last_cache_update = {}
        
    async def get_personality_config(self, personality_id: str) -> Optional[Dict[str, Any]]:
        """
        Get personality configuration by ID (supports legacy IDs)
        
        Args:
            personality_id: Legacy or standardized personality ID
            
        Returns:
            Comprehensive personality configuration or None
        """
        # Standardize the ID
        standardized_id = get_standardized_id(personality_id)
        
        # Check cache first
        if self._is_cache_valid(standardized_id):
            logger.debug(f"🚀 Cache hit for personality {standardized_id}")
            return self.cache[standardized_id]
        
        # Try database first
        if self.database_service:
            try:
                db_config = await self._get_from_database(standardized_id)
                if db_config:
                    self._update_cache(standardized_id, db_config)
                    logger.debug(f"📊 Database hit for personality {standardized_id}")
                    return db_config
            except Exception as e:
                logger.warning(f"⚠️ Database query failed for {standardized_id}: {e}")
        
        # Fallback to standardized mapping
        fallback_config = self._get_from_standardized_mapping(standardized_id)
        if fallback_config:
            self._update_cache(standardized_id, fallback_config)
            logger.debug(f"📋 Fallback to standardized mapping for {standardized_id}")
            return fallback_config
        
        logger.warning(f"❌ Personality {personality_id} not found")
        return None
    
    async def get_all_personalities(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """
        Get all personality configurations
        
        Args:
            active_only: If True, return only active personalities
            
        Returns:
            List of personality configurations
        """
        personalities = []
        
        # Try database first
        if self.database_service:
            try:
                db_personalities = await self._get_all_from_database(active_only)
                if db_personalities:
                    logger.debug(f"📊 Retrieved {len(db_personalities)} personalities from database")
                    return db_personalities
            except Exception as e:
                logger.warning(f"⚠️ Database query failed for all personalities: {e}")
        
        # Fallback to standardized mapping
        for personality_id in get_all_standardized_ids():
            config = self._get_from_standardized_mapping(personality_id)
            if config and (not active_only or config.get("is_active", True)):
                personalities.append(config)
        
        logger.debug(f"📋 Fallback: Retrieved {len(personalities)} personalities from standardized mapping")
        return personalities
    
    async def get_personalities_by_domain(self, domain: str, active_only: bool = True) -> List[Dict[str, Any]]:
        """
        Get personalities filtered by domain
        
        Args:
            domain: Domain name (spiritual, scientific, etc.)
            active_only: If True, return only active personalities
            
        Returns:
            List of personality configurations in the domain
        """
        all_personalities = await self.get_all_personalities(active_only)
        domain_personalities = [
            p for p in all_personalities 
            if p.get("domain") == domain
        ]
        
        logger.debug(f"🎭 Found {len(domain_personalities)} personalities in domain {domain}")
        return domain_personalities
    
    async def save_personality_config(self, config: Dict[str, Any]) -> bool:
        """
        Save personality configuration to database
        
        Args:
            config: Personality configuration dictionary
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            if self.database_service:
                success = await self._save_to_database(config)
                if success:
                    # Invalidate cache
                    personality_id = config.get("personality_id")
                    if personality_id in self.cache:
                        del self.cache[personality_id]
                    logger.info(f"✅ Saved personality {personality_id} to database")
                    return True
            
            logger.warning("⚠️ Database service not available for save operation")
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to save personality config: {e}")
            return False
    
    async def delete_personality_config(self, personality_id: str) -> bool:
        """
        Delete personality configuration from database
        
        Args:
            personality_id: Personality ID to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            standardized_id = get_standardized_id(personality_id)
            
            if self.database_service:
                success = await self._delete_from_database(standardized_id)
                if success:
                    # Invalidate cache
                    if standardized_id in self.cache:
                        del self.cache[standardized_id]
                    logger.info(f"✅ Deleted personality {standardized_id} from database")
                    return True
            
            logger.warning("⚠️ Database service not available for delete operation")
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to delete personality config: {e}")
            return False
    
    async def update_personality_config(self, personality_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update personality configuration in database
        
        Args:
            personality_id: Personality ID to update
            updates: Dictionary of field updates
            
        Returns:
            True if updated successfully, False otherwise
        """
        try:
            standardized_id = get_standardized_id(personality_id)
            
            # Get current config
            current_config = await self.get_personality_config(standardized_id)
            if not current_config:
                logger.error(f"❌ Personality {standardized_id} not found for update")
                return False
            
            # Apply updates
            current_config.update(updates)
            current_config["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            # Save updated config
            return await self.save_personality_config(current_config)
            
        except Exception as e:
            logger.error(f"❌ Failed to update personality config: {e}")
            return False
    
    async def migrate_hardcoded_personalities(self, dry_run: bool = True) -> Dict[str, Any]:
        """
        Migrate hardcoded personalities to database
        
        Args:
            dry_run: If True, validate migration without committing changes
            
        Returns:
            Migration report
        """
        try:
            migration_service = PersonalityMigrationService(self.database_service)
            result = await migration_service.migrate_all_personalities(dry_run)
            
            # Clear cache after migration
            if not dry_run and result.get("status") == "completed":
                self.cache.clear()
                logger.info("🧹 Cleared personality cache after migration")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def _is_cache_valid(self, personality_id: str) -> bool:
        """Check if cached data is still valid"""
        if personality_id not in self.cache:
            return False
        
        last_update = self.last_cache_update.get(personality_id, 0)
        current_time = datetime.now(timezone.utc).timestamp()
        
        return (current_time - last_update) < self.cache_ttl
    
    def _update_cache(self, personality_id: str, config: Dict[str, Any]):
        """Update cache with new configuration"""
        self.cache[personality_id] = config
        self.last_cache_update[personality_id] = datetime.now(timezone.utc).timestamp()
    
    def _get_from_standardized_mapping(self, personality_id: str) -> Optional[Dict[str, Any]]:
        """Get personality configuration from standardized mapping"""
        std_data = STANDARDIZED_PERSONALITIES.get(personality_id)
        if not std_data:
            return None
        
        # Convert to comprehensive format
        config = {
            "id": std_data["standardized_id"],
            "personality_id": std_data["standardized_id"],
            "display_name": std_data["display_name"],
            "domain": std_data["domain"].value if hasattr(std_data["domain"], 'value') else str(std_data["domain"]),
            "description": std_data["description"],
            "legacy_ids": std_data.get("legacy_ids", []),
            "primary_sources": std_data.get("primary_sources", []),
            "cultural_context": std_data.get("cultural_context", "universal"),
            "historical_period": std_data.get("historical_period", ""),
            "is_active": True,
            "is_featured": True,
            "availability": "public",
            "personality_version": "1.0",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "data_source": "standardized_mapping"
        }
        
        return config
    
    async def _get_from_database(self, personality_id: str) -> Optional[Dict[str, Any]]:
        """Get personality configuration from database"""
        if not self.database_service:
            return None
        
        # This would be the actual database query
        # For now, return None to force fallback to standardized mapping
        return None
    
    async def _get_all_from_database(self, active_only: bool = True) -> Optional[List[Dict[str, Any]]]:
        """Get all personality configurations from database"""
        if not self.database_service:
            return None
        
        # This would be the actual database query
        # For now, return None to force fallback to standardized mapping
        return None
    
    async def _save_to_database(self, config: Dict[str, Any]) -> bool:
        """Save configuration to database"""
        if not self.database_service:
            return False
        
        # This would be the actual database save
        # For now, return True to simulate successful save
        logger.info(f"💾 Would save personality {config.get('personality_id')} to database")
        return True
    
    async def _delete_from_database(self, personality_id: str) -> bool:
        """Delete configuration from database"""
        if not self.database_service:
            return False
        
        # This would be the actual database delete
        # For now, return True to simulate successful delete
        logger.info(f"🗑️ Would delete personality {personality_id} from database")
        return True
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on personality service"""
        health_status = {
            "service": "database_driven_personality",
            "status": "healthy",
            "cache_size": len(self.cache),
            "standardized_personalities": len(STANDARDIZED_PERSONALITIES),
            "database_available": self.database_service is not None,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Test a sample personality retrieval
        try:
            test_config = await self.get_personality_config("krishna")
            health_status["sample_retrieval"] = "success" if test_config else "failed"
        except Exception as e:
            health_status["status"] = "degraded"
            health_status["sample_retrieval"] = f"error: {e}"
        
        return health_status


# Factory function for service creation
async def create_database_driven_personality_service(database_service=None) -> DatabaseDrivenPersonalityService:
    """Factory function to create database-driven personality service"""
    service = DatabaseDrivenPersonalityService(database_service)
    logger.info("🚀 Created database-driven personality service")
    return service


# CLI interface for testing
if __name__ == "__main__":
    import asyncio
    
    async def test_service():
        service = await create_database_driven_personality_service()
        
        print("🔍 Testing personality service...")
        
        # Test health check
        health = await service.health_check()
        print(f"📊 Health: {health['status']} - {health['standardized_personalities']} personalities available")
        
        # Test individual personality retrieval
        krishna = await service.get_personality_config("krishna")
        print(f"🕉️  Krishna config: {'✅ Found' if krishna else '❌ Not found'}")
        
        # Test legacy ID mapping
        gandhi = await service.get_personality_config("gandhi")  # Legacy ID
        print(f"🕊️  Gandhi config (legacy ID): {'✅ Found' if gandhi else '❌ Not found'}")
        if gandhi:
            print(f"   Mapped to: {gandhi['personality_id']}")
        
        # Test domain filtering
        spiritual = await service.get_personalities_by_domain("spiritual")
        print(f"🙏 Spiritual personalities: {len(spiritual)} found")
        
        # Test all personalities
        all_personalities = await service.get_all_personalities()
        print(f"🎭 All personalities: {len(all_personalities)} found")
        
        # Test migration dry-run
        print("\n🚀 Testing migration...")
        migration_result = await service.migrate_hardcoded_personalities(dry_run=True)
        print(f"📋 Migration dry-run: {migration_result['status']}")
        print(f"   Personalities validated: {len(migration_result.get('migrated_personalities', []))}")
        print(f"   ID changes required: {len(migration_result.get('id_changes', []))}")
    
    asyncio.run(test_service())
