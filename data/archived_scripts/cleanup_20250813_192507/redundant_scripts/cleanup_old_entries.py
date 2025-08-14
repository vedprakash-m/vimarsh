#!/usr/bin/env python3
"""
Cleanup old Krishna entries from Cosmos DB that don't have proper integration_date metadata.
This script safely removes old entries while preserving the new properly-assigned personality entries.
"""

import os
import logging
from typing import Dict, List, Any
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cleanup_old_entries.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv('../../.env')

def cleanup_old_entries(dry_run: bool = True) -> Dict[str, Any]:
    """
    Clean up old Krishna entries that don't have proper integration_date metadata.
    
    Args:
        dry_run: If True, only analyze what would be deleted without actually deleting
    
    Returns:
        Dictionary with cleanup statistics and results
    """
    try:
        from azure.cosmos import CosmosClient
        from azure.cosmos.exceptions import CosmosResourceNotFoundError
        
        # Get connection string with proper error handling
        connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
        if not connection_string:
            raise ValueError("AZURE_COSMOS_CONNECTION_STRING not found in environment variables")
        
        client = CosmosClient.from_connection_string(connection_string)
        database = client.get_database_client('vimarsh-multi-personality')
        container = database.get_container_client('personality-vectors')
        
        logger.info("🔍 Starting cleanup analysis...")
        
        # Query for old entries without proper integration_date
        old_entries_query = """
        SELECT c.id, c.personality, c.integration_date, c.source 
        FROM c 
        WHERE c.integration_date = 'Unknown' OR IS_NULL(c.integration_date)
        """
        
        cleanup_stats = {
            'total_analyzed': 0,
            'krishna_entries': 0,
            'other_old_entries': 0,
            'entries_to_cleanup': [],
            'cleanup_performed': not dry_run,
            'errors': []
        }
        
        entries_to_cleanup = []
        
        # Analyze old entries
        logger.info("📊 Analyzing old entries...")
        for item in container.query_items(query=old_entries_query, enable_cross_partition_query=True):
            cleanup_stats['total_analyzed'] += 1
            
            entry_info = {
                'id': item.get('id'),
                'personality': item.get('personality'),
                'integration_date': item.get('integration_date'),
                'source_preview': item.get('source', '')[:50] if item.get('source') else 'N/A'
            }
            
            # Count by personality
            if item.get('personality', '').lower() == 'krishna':
                cleanup_stats['krishna_entries'] += 1
            else:
                cleanup_stats['other_old_entries'] += 1
            
            entries_to_cleanup.append(entry_info)
        
        cleanup_stats['entries_to_cleanup'] = entries_to_cleanup[:10]  # Store first 10 for reporting
        
        logger.info(f"📈 Analysis complete:")
        logger.info(f"  Total old entries: {cleanup_stats['total_analyzed']}")
        logger.info(f"  Krishna entries: {cleanup_stats['krishna_entries']}")
        logger.info(f"  Other old entries: {cleanup_stats['other_old_entries']}")
        
        if dry_run:
            logger.info("🔍 DRY RUN MODE - No entries will be deleted")
            logger.info("💡 Run with dry_run=False to perform actual cleanup")
        else:
            # Perform actual cleanup
            logger.info("🗑️ Starting cleanup operation...")
            deleted_count = 0
            error_count = 0
            
            # Delete entries in batches for better performance
            batch_size = 100
            batch = []
            
            for item in container.query_items(query=old_entries_query, enable_cross_partition_query=True):
                batch.append(item)
                
                if len(batch) >= batch_size:
                    deleted_batch, errors_batch = _delete_batch(container, batch)
                    deleted_count += deleted_batch
                    error_count += errors_batch
                    cleanup_stats['errors'].extend(errors_batch) if errors_batch else None
                    batch = []
            
            # Process remaining items
            if batch:
                deleted_batch, errors_batch = _delete_batch(container, batch)
                deleted_count += deleted_batch
                error_count += errors_batch
                cleanup_stats['errors'].extend(errors_batch) if errors_batch else None
            
            cleanup_stats['deleted_count'] = deleted_count
            cleanup_stats['error_count'] = error_count
            
            logger.info(f"✅ Cleanup complete:")
            logger.info(f"  Entries deleted: {deleted_count}")
            logger.info(f"  Errors encountered: {error_count}")
        
        return cleanup_stats
        
    except Exception as e:
        error_msg = f"❌ Cleanup operation failed: {str(e)}"
        logger.error(error_msg)
        return {
            'error': error_msg,
            'cleanup_performed': False
        }

def _delete_batch(container, batch: List[Dict[str, Any]]) -> tuple[int, List[str]]:
    """
    Delete a batch of items from Cosmos DB with error handling.
    
    Returns:
        Tuple of (deleted_count, errors_list)
    """
    from azure.cosmos.exceptions import CosmosResourceNotFoundError
    
    deleted_count = 0
    errors = []
    
    for item in batch:
        try:
            container.delete_item(
                item=item['id'],
                partition_key=item['personality']
            )
            deleted_count += 1
            
            if deleted_count % 50 == 0:
                logger.info(f"  Deleted {deleted_count} items...")
                
        except CosmosResourceNotFoundError:
            logger.warning(f"  Item {item['id']} not found (already deleted?)")
        except Exception as e:
            error_msg = f"Failed to delete item {item['id']}: {str(e)}"
            errors.append(error_msg)
            logger.error(f"  {error_msg}")
    
    return deleted_count, errors

def main():
    """Main execution function with interactive confirmation."""
    print("🧹 Vimarsh Database Cleanup Tool")
    print("=" * 50)
    
    # First, run in dry-run mode
    print("\n🔍 Step 1: Analyzing database (dry run)")
    dry_run_results = cleanup_old_entries(dry_run=True)
    
    if 'error' in dry_run_results:
        print(f"❌ Analysis failed: {dry_run_results['error']}")
        return
    
    print(f"\n📊 Analysis Results:")
    print(f"  Total old entries found: {dry_run_results['total_analyzed']}")
    print(f"  Krishna entries: {dry_run_results['krishna_entries']}")
    print(f"  Other old entries: {dry_run_results['other_old_entries']}")
    
    if dry_run_results['total_analyzed'] == 0:
        print("✨ No old entries found. Database is clean!")
        return
    
    # Show sample entries
    print(f"\n📋 Sample entries to be cleaned:")
    for i, entry in enumerate(dry_run_results['entries_to_cleanup'][:5], 1):
        print(f"  {i}. ID: {entry['id'][:20]}... | Personality: {entry['personality']} | Date: {entry['integration_date']}")
    
    # Ask for confirmation
    print(f"\n⚠️  WARNING: This will permanently delete {dry_run_results['total_analyzed']} entries!")
    response = input("Do you want to proceed with cleanup? (yes/no): ").strip().lower()
    
    if response in ['yes', 'y']:
        print("\n🗑️ Step 2: Performing cleanup...")
        cleanup_results = cleanup_old_entries(dry_run=False)
        
        if 'error' in cleanup_results:
            print(f"❌ Cleanup failed: {cleanup_results['error']}")
        else:
            print(f"✅ Cleanup completed successfully!")
            print(f"  Entries deleted: {cleanup_results.get('deleted_count', 0)}")
            if cleanup_results.get('error_count', 0) > 0:
                print(f"  ⚠️  Errors encountered: {cleanup_results['error_count']}")
                print("  Check cleanup_old_entries.log for details")
    else:
        print("❌ Cleanup cancelled by user")

if __name__ == "__main__":
    main()
