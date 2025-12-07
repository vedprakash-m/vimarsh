"""
Data Export Service for Vimarsh
GDPR-compliant user data export functionality
"""

import logging
import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import asyncio

from azure.cosmos import CosmosClient, exceptions

logger = logging.getLogger(__name__)


class DataExportService:
    """Service for exporting user data in GDPR-compliant format"""
    
    # Cosmos DB containers to export from
    CONTAINERS_TO_EXPORT = [
        "user_preferences",
        "engagement_tracking",
        "conversation_memory",
        "user_activity",
        "bookmarks"
    ]
    
    # Export format version
    EXPORT_VERSION = "1.0"
    
    def __init__(self):
        """Initialize data export service"""
        self.cosmos_client = None
        self.database = None
        self._init_cosmos_db()
    
    def _init_cosmos_db(self):
        """Initialize Cosmos DB connection"""
        try:
            cosmos_endpoint = os.environ.get("COSMOS_ENDPOINT") or os.environ.get("COSMOS_DB_ENDPOINT")
            cosmos_key = os.environ.get("COSMOS_KEY") or os.environ.get("COSMOS_DB_KEY")
            cosmos_database = os.environ.get("COSMOS_DATABASE", "vimarsh-db")
            
            if not cosmos_endpoint or not cosmos_key:
                logger.warning("⚠️ Cosmos DB credentials not found, data export will be limited")
                return
            
            self.cosmos_client = CosmosClient(cosmos_endpoint, cosmos_key)
            self.database = self.cosmos_client.get_database_client(cosmos_database)
            logger.info("✅ Data Export Service connected to Cosmos DB")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Cosmos DB: {e}")
    
    async def export_user_data(
        self,
        user_id: str,
        include_metadata: bool = True
    ) -> Dict[str, Any]:
        """
        Export all user data in GDPR-compliant format
        
        Args:
            user_id: User identifier
            include_metadata: Whether to include export metadata
            
        Returns:
            Complete user data export dictionary
        """
        logger.info(f"📦 Starting data export for user {user_id}")
        
        export_data = {
            "export_version": self.EXPORT_VERSION,
            "user_id": user_id,
            "export_timestamp": datetime.now(timezone.utc).isoformat(),
            "data": {}
        }
        
        try:
            # Export data from each container
            for container_name in self.CONTAINERS_TO_EXPORT:
                try:
                    data = await self._export_from_container(user_id, container_name)
                    export_data["data"][container_name] = data
                    logger.info(f"✅ Exported {len(data)} items from {container_name}")
                except Exception as e:
                    logger.error(f"❌ Error exporting from {container_name}: {e}")
                    export_data["data"][container_name] = {
                        "error": str(e),
                        "items": []
                    }
            
            # Add metadata if requested
            if include_metadata:
                export_data["metadata"] = self._generate_export_metadata(export_data)
            
            logger.info(f"✅ Data export completed for user {user_id}")
            return export_data
            
        except Exception as e:
            logger.error(f"❌ Error during data export for user {user_id}: {e}")
            raise
    
    async def _export_from_container(
        self,
        user_id: str,
        container_name: str
    ) -> List[Dict[str, Any]]:
        """
        Export user data from a specific container
        
        Args:
            user_id: User identifier
            container_name: Name of the container
            
        Returns:
            List of user data items
        """
        if not self.database:
            logger.warning(f"⚠️ No database connection, skipping {container_name}")
            return []
        
        try:
            container = self.database.get_container_client(container_name)
            
            # Query for user's data
            query = "SELECT * FROM c WHERE c.user_id = @user_id"
            parameters = [{"name": "@user_id", "value": user_id}]
            
            items = list(container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True
            ))
            
            # Sanitize items (remove internal fields)
            sanitized_items = [
                self._sanitize_item(item) for item in items
            ]
            
            return sanitized_items
            
        except exceptions.CosmosResourceNotFoundError:
            logger.warning(f"⚠️ Container {container_name} not found")
            return []
        except Exception as e:
            logger.error(f"❌ Error exporting from {container_name}: {e}")
            raise
    
    def _sanitize_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove internal/sensitive fields from exported item
        
        Args:
            item: Item to sanitize
            
        Returns:
            Sanitized item
        """
        # Fields to exclude from export
        exclude_fields = ["_rid", "_self", "_etag", "_attachments", "_ts"]
        
        return {
            key: value for key, value in item.items()
            if key not in exclude_fields
        }
    
    def _generate_export_metadata(self, export_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate metadata about the export
        
        Args:
            export_data: Export data
            
        Returns:
            Metadata dictionary
        """
        metadata = {
            "total_containers": len(self.CONTAINERS_TO_EXPORT),
            "containers_exported": len([
                c for c in export_data["data"].values()
                if not isinstance(c, dict) or "error" not in c
            ]),
            "total_items": 0,
            "item_counts_by_container": {}
        }
        
        for container_name, data in export_data["data"].items():
            if isinstance(data, list):
                count = len(data)
                metadata["total_items"] += count
                metadata["item_counts_by_container"][container_name] = count
            elif isinstance(data, dict) and "items" in data:
                count = len(data.get("items", []))
                metadata["total_items"] += count
                metadata["item_counts_by_container"][container_name] = count
        
        return metadata
    
    def export_to_json_file(
        self,
        export_data: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> str:
        """
        Save export data to JSON file
        
        Args:
            export_data: Export data
            output_path: Optional output path
            
        Returns:
            Path to saved file
        """
        try:
            if not output_path:
                user_id = export_data.get("user_id", "unknown")
                timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
                output_path = f"data/exports/user_{user_id}_{timestamp}.json"
            
            # Create directory if needed
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Write JSON file with pretty formatting
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Export saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Error saving export to file: {e}")
            raise
    
    async def delete_user_data(self, user_id: str) -> Dict[str, Any]:
        """
        Delete all user data (for account deletion)
        
        Args:
            user_id: User identifier
            
        Returns:
            Deletion summary
        """
        logger.info(f"🗑️ Starting data deletion for user {user_id}")
        
        deletion_summary = {
            "user_id": user_id,
            "deletion_timestamp": datetime.now(timezone.utc).isoformat(),
            "containers_processed": {},
            "total_items_deleted": 0
        }
        
        try:
            for container_name in self.CONTAINERS_TO_EXPORT:
                try:
                    count = await self._delete_from_container(user_id, container_name)
                    deletion_summary["containers_processed"][container_name] = {
                        "status": "success",
                        "items_deleted": count
                    }
                    deletion_summary["total_items_deleted"] += count
                    logger.info(f"✅ Deleted {count} items from {container_name}")
                except Exception as e:
                    logger.error(f"❌ Error deleting from {container_name}: {e}")
                    deletion_summary["containers_processed"][container_name] = {
                        "status": "error",
                        "error": str(e)
                    }
            
            logger.info(f"✅ Data deletion completed for user {user_id}")
            return deletion_summary
            
        except Exception as e:
            logger.error(f"❌ Error during data deletion for user {user_id}: {e}")
            raise
    
    async def _delete_from_container(
        self,
        user_id: str,
        container_name: str
    ) -> int:
        """
        Delete user data from a specific container
        
        Args:
            user_id: User identifier
            container_name: Name of the container
            
        Returns:
            Number of items deleted
        """
        if not self.database:
            logger.warning(f"⚠️ No database connection, skipping {container_name}")
            return 0
        
        try:
            container = self.database.get_container_client(container_name)
            
            # Query for user's data
            query = "SELECT c.id, c.user_id FROM c WHERE c.user_id = @user_id"
            parameters = [{"name": "@user_id", "value": user_id}]
            
            items = list(container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True
            ))
            
            # Delete each item
            deleted_count = 0
            for item in items:
                try:
                    container.delete_item(
                        item=item["id"],
                        partition_key=user_id
                    )
                    deleted_count += 1
                except Exception as e:
                    logger.error(f"❌ Error deleting item {item['id']}: {e}")
            
            return deleted_count
            
        except exceptions.CosmosResourceNotFoundError:
            logger.warning(f"⚠️ Container {container_name} not found")
            return 0
        except Exception as e:
            logger.error(f"❌ Error deleting from {container_name}: {e}")
            raise


# Global data export service instance
data_export_service = DataExportService()
