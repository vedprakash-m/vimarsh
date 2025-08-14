#!/usr/bin/env python3
"""
IDEMPOTENT Database Cleanup Script
Removes duplicate personalities and ensures clean database state
"""
import os
import sys
from pathlib import Path
from collections import defaultdict

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent / 'backend'))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from azure.cosmos import CosmosClient

def cleanup_duplicates(dry_run=True):
    """
    Idempotent cleanup of duplicate personalities
    
    Args:
        dry_run (bool): If True, only shows what would be deleted without actually deleting
    """
    connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
    if not connection_string:
        print("❌ AZURE_COSMOS_CONNECTION_STRING not set")
        return False
    
    database_name = os.getenv('AZURE_COSMOS_DATABASE_NAME', 'vimarsh-multi-personality')
    
    try:
        client = CosmosClient.from_connection_string(connection_string)
        database = client.get_database_client(database_name)
        container = database.get_container_client('personalities')
        
        print(f"🧹 {'DRY RUN: ' if dry_run else ''}IDEMPOTENT CLEANUP STARTING")
        print("=" * 60)
        
        # Get all personalities
        query = "SELECT * FROM c"
        items = list(container.query_items(query=query, enable_cross_partition_query=True))
        
        print(f"📊 Found {len(items)} total records")
        
        # Group by personality_id
        personality_groups = defaultdict(list)
        for item in items:
            personality_id = item.get('personality_id') or item.get('id')
            personality_groups[personality_id].append(item)
        
        # Process duplicates
        total_deletions = 0
        total_kept = 0
        
        for personality_id, records in personality_groups.items():
            if len(records) > 1:
                # Keep the first record, delete the rest
                keep_record = records[0]
                delete_records = records[1:]
                
                print(f"\n🔧 {personality_id}: Keeping 1, deleting {len(delete_records)} duplicates")
                print(f"  ✅ KEEP: Cosmos ID={keep_record.get('id')}")
                
                for record in delete_records:
                    cosmos_id = record.get('id')
                    print(f"  🗑️  DELETE: Cosmos ID={cosmos_id}")
                    
                    if not dry_run:
                        try:
                            container.delete_item(item=cosmos_id, partition_key=cosmos_id)
                            print(f"    ✅ Deleted successfully")
                        except Exception as e:
                            print(f"    ❌ Delete failed: {e}")
                            return False
                
                total_deletions += len(delete_records)
                total_kept += 1
            else:
                # No duplicates
                print(f"✅ {personality_id}: Clean (no duplicates)")
                total_kept += 1
        
        print(f"\n📊 CLEANUP SUMMARY:")
        print(f"  Records to keep: {total_kept}")
        print(f"  Records to delete: {total_deletions}")
        print(f"  Final database size: {total_kept} (from {len(items)})")
        print(f"  Space savings: {total_deletions}/{len(items)} = {total_deletions/len(items)*100:.1f}%")
        
        if dry_run:
            print(f"\n⚠️  This was a DRY RUN - no actual deletions performed")
            print(f"   Run with --execute to perform actual cleanup")
        else:
            print(f"\n✅ CLEANUP COMPLETED - Database is now clean and idempotent")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        return False

def verify_clean_state():
    """Verify that database is in clean state with no duplicates"""
    connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
    if not connection_string:
        print("❌ AZURE_COSMOS_CONNECTION_STRING not set")
        return False
    
    database_name = os.getenv('AZURE_COSMOS_DATABASE_NAME', 'vimarsh-multi-personality')
    
    try:
        client = CosmosClient.from_connection_string(connection_string)
        database = client.get_database_client(database_name)
        container = database.get_container_client('personalities')
        
        # Get all personalities
        query = "SELECT c.id, c.personality_id FROM c"
        items = list(container.query_items(query=query, enable_cross_partition_query=True))
        
        # Check for duplicates
        personality_ids = []
        for item in items:
            personality_id = item.get('personality_id') or item.get('id')
            personality_ids.append(personality_id)
        
        unique_count = len(set(personality_ids))
        total_count = len(personality_ids)
        
        print(f"🔍 VERIFICATION RESULTS:")
        print(f"  Total records: {total_count}")
        print(f"  Unique personalities: {unique_count}")
        print(f"  Duplicates: {total_count - unique_count}")
        
        if unique_count == total_count:
            print(f"✅ DATABASE IS CLEAN - No duplicates found!")
            return True
        else:
            print(f"❌ DATABASE HAS DUPLICATES - Cleanup needed!")
            return False
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Idempotent database cleanup')
    parser.add_argument('--execute', action='store_true', help='Actually perform deletions (default: dry run)')
    parser.add_argument('--verify', action='store_true', help='Only verify database state')
    
    args = parser.parse_args()
    
    if args.verify:
        verify_clean_state()
    else:
        cleanup_duplicates(dry_run=not args.execute)
