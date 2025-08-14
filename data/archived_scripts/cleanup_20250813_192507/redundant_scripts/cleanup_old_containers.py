#!/usr/bin/env python3
"""
Cosmos DB Container Cleanup Script
Safely delete old/unused containers while preserving personality-vectors.
"""

import asyncio
import logging
import os
import re
from pathlib import Path
from typing import List, Dict

from azure.cosmos.aio import CosmosClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ContainerCleanup:
    """Clean up old Cosmos DB containers"""
    
    def __init__(self):
        self.cosmos_client = None
        
    async def initialize_cosmos_connection(self):
        """Initialize Cosmos DB connection"""
        try:
            # Load environment variables
            from dotenv import load_dotenv
            env_path = Path(__file__).parent.parent.parent / '.env'
            load_dotenv(env_path)
            
            # Get connection string
            cosmos_connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING') or os.getenv('COSMOSDB_CONNECTION_STRING')
            
            if not cosmos_connection_string:
                raise ValueError("No Cosmos DB connection string found")
            
            # Parse connection string
            endpoint_match = re.search(r'AccountEndpoint=([^;]+)', cosmos_connection_string)
            key_match = re.search(r'AccountKey=([^;]+)', cosmos_connection_string)
            
            if not endpoint_match or not key_match:
                raise ValueError("Invalid connection string format")
                
            cosmos_endpoint = endpoint_match.group(1)
            cosmos_key = key_match.group(1)
            
            self.cosmos_client = CosmosClient(cosmos_endpoint, cosmos_key)
            logger.info("✅ Connected to Cosmos DB")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Cosmos DB: {e}")
            raise
            
    async def list_all_containers(self) -> List[Dict[str, str]]:
        """List all containers across all databases"""
        try:
            all_containers = []
            
            # Get all databases
            databases = self.cosmos_client.list_databases()
            
            async for database in databases:
                db_name = database['id']
                logger.info(f"📊 Scanning database: {db_name}")
                
                db_client = self.cosmos_client.get_database_client(db_name)
                containers = db_client.list_containers()
                
                async for container in containers:
                    container_info = {
                        'database': db_name,
                        'container': container['id'],
                        'full_path': f"{db_name}.{container['id']}"
                    }
                    all_containers.append(container_info)
                    logger.info(f"  📦 Found container: {container_info['full_path']}")
            
            return all_containers
            
        except Exception as e:
            logger.error(f"❌ Failed to list containers: {e}")
            raise
            
    def identify_containers_to_delete(self, all_containers: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Identify which containers should be deleted"""
        containers_to_keep = [
            'vimarsh-multi-personality.personality-vectors'  # The only container we want to keep
        ]
        
        containers_to_delete = []
        containers_to_keep_found = []
        
        for container in all_containers:
            full_path = container['full_path']
            
            if full_path in containers_to_keep:
                containers_to_keep_found.append(container)
                logger.info(f"✅ KEEPING: {full_path}")
            else:
                containers_to_delete.append(container)
                logger.info(f"🗑️  WILL DELETE: {full_path}")
        
        # Verify we found the container we want to keep
        if not containers_to_keep_found:
            raise ValueError("❌ CRITICAL: personality-vectors container not found! Aborting cleanup.")
        
        return containers_to_delete
        
    async def delete_container(self, database_name: str, container_name: str) -> bool:
        """Delete a single container"""
        try:
            db_client = self.cosmos_client.get_database_client(database_name)
            await db_client.delete_container(container_name)
            logger.info(f"✅ DELETED: {database_name}.{container_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to delete {database_name}.{container_name}: {e}")
            return False
            
    async def cleanup_containers(self, dry_run: bool = True):
        """Main cleanup function"""
        try:
            logger.info("🚀 Starting container cleanup process...")
            
            # List all containers
            all_containers = await self.list_all_containers()
            
            if not all_containers:
                logger.info("ℹ️  No containers found")
                return
            
            # Identify containers to delete
            containers_to_delete = self.identify_containers_to_delete(all_containers)
            
            if not containers_to_delete:
                logger.info("ℹ️  No containers need to be deleted")
                return
            
            # Show cleanup plan
            print("\n" + "="*70)
            print("🗑️  CONTAINER CLEANUP PLAN")
            print("="*70)
            print(f"Containers to DELETE ({len(containers_to_delete)}):")
            for container in containers_to_delete:
                print(f"  ❌ {container['full_path']}")
            
            print("\nContainers to KEEP (1):")
            print("  ✅ vimarsh-multi-personality.personality-vectors")
            print("="*70)
            
            if dry_run:
                print("\n🔍 DRY RUN MODE: No containers will actually be deleted")
                print("Run with dry_run=False to perform actual deletion")
                return
            
            # Ask for confirmation
            print(f"\n⚠️  WARNING: This will permanently delete {len(containers_to_delete)} containers!")
            confirmation = input("Type 'DELETE' to confirm: ")
            
            if confirmation != 'DELETE':
                print("❌ Cleanup cancelled")
                return
            
            # Perform deletions
            logger.info("🗑️  Starting container deletions...")
            deleted_count = 0
            failed_count = 0
            
            for container in containers_to_delete:
                success = await self.delete_container(container['database'], container['container'])
                if success:
                    deleted_count += 1
                else:
                    failed_count += 1
            
            # Summary
            print("\n" + "="*70)
            print("🎉 CLEANUP SUMMARY")
            print("="*70)
            print(f"✅ Successfully deleted: {deleted_count} containers")
            print(f"❌ Failed to delete: {failed_count} containers")
            print("✅ Containers remaining: 1 (personality-vectors)")
            print("="*70)
            
            if failed_count == 0:
                logger.info("🎉 Container cleanup completed successfully!")
            else:
                logger.warning(f"⚠️  Cleanup completed with {failed_count} failures")
                
        except Exception as e:
            logger.error(f"❌ Container cleanup failed: {e}")
            raise
            
    async def cleanup(self):
        """Clean up resources"""
        if self.cosmos_client:
            await self.cosmos_client.close()

async def main():
    """Main function"""
    cleanup_manager = ContainerCleanup()
    
    try:
        await cleanup_manager.initialize_cosmos_connection()
        
        # First run in dry-run mode to show what will be deleted
        await cleanup_manager.cleanup_containers(dry_run=True)
        
        # Ask if user wants to proceed with actual deletion
        print("\n" + "="*70)
        proceed = input("Do you want to proceed with actual deletion? (y/N): ")
        
        if proceed.lower() in ['y', 'yes']:
            await cleanup_manager.cleanup_containers(dry_run=False)
        else:
            print("❌ Cleanup cancelled by user")
            
    except Exception as e:
        logger.error(f"❌ Cleanup process failed: {e}")
        raise
    finally:
        await cleanup_manager.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
