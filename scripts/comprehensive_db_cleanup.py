#!/usr/bin/env python3
"""
COMPREHENSIVE IDEMPOTENT DATABASE CLEANUP
1. Fixes schema issues (adds missing personality_id fields)
2. Removes duplicate personalities 
3. Ensures clean, consistent database state
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

def comprehensive_cleanup(dry_run=True):
    """
    Comprehensive idempotent cleanup:
    1. Fix schema issues (add missing personality_id)
    2. Remove duplicates
    3. Verify final state
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
        
        print(f"🧹 {'DRY RUN: ' if dry_run else ''}COMPREHENSIVE CLEANUP STARTING")
        print("=" * 70)
        
        # STEP 1: Get all personalities
        query = "SELECT * FROM c"
        items = list(container.query_items(query=query, enable_cross_partition_query=True))
        print(f"📊 Found {len(items)} total records")
        
        # STEP 2: Fix schema issues first
        print(f"\n🔧 STEP 1: FIXING SCHEMA ISSUES")
        print("-" * 40)
        
        schema_fix_count = 0
        for item in items:
            personality_id = item.get('personality_id') or item.get('id')
            has_personality_id = 'personality_id' in item
            has_extensive_fields = 'llm_config' in item or 'content_filters' in item
            
            # Fix: Add missing personality_id field
            if has_extensive_fields and not has_personality_id:
                print(f"  🔧 {personality_id}: Adding missing personality_id field")
                if not dry_run:
                    item['personality_id'] = personality_id
                    container.upsert_item(item)
                schema_fix_count += 1
        
        print(f"  📊 Schema fixes needed: {schema_fix_count}")
        
        # STEP 3: Re-fetch data after schema fixes (if not dry run)
        if not dry_run and schema_fix_count > 0:
            print(f"  🔄 Re-fetching data after schema fixes...")
            items = list(container.query_items(query=query, enable_cross_partition_query=True))
        
        # STEP 4: Handle duplicates
        print(f"\n🗑️  STEP 2: REMOVING DUPLICATES")
        print("-" * 40)
        
        # Group by personality_id (now all records should have it)
        personality_groups = defaultdict(list)
        for item in items:
            personality_id = item.get('personality_id') or item.get('id')
            personality_groups[personality_id].append(item)
        
        duplicate_deletions = 0
        unique_kept = 0
        
        for personality_id, records in personality_groups.items():
            if len(records) > 1:
                # Choose the best record to keep (prefer one with most fields)
                best_record = max(records, key=lambda r: len(r.keys()))
                delete_records = [r for r in records if r != best_record]
                
                print(f"  🔧 {personality_id}: Keeping best of {len(records)}, deleting {len(delete_records)}")
                print(f"    ✅ KEEP: Cosmos ID={best_record.get('id')} ({len(best_record.keys())} fields)")
                
                for record in delete_records:
                    cosmos_id = record.get('id')
                    field_count = len(record.keys())
                    print(f"    🗑️  DELETE: Cosmos ID={cosmos_id} ({field_count} fields)")
                    
                    if not dry_run:
                        try:
                            container.delete_item(item=cosmos_id, partition_key=cosmos_id)
                            print(f"      ✅ Deleted successfully")
                        except Exception as e:
                            print(f"      ❌ Delete failed: {e}")
                            return False
                
                duplicate_deletions += len(delete_records)
                unique_kept += 1
            else:
                unique_kept += 1
        
        print(f"  📊 Duplicates removed: {duplicate_deletions}")
        
        # STEP 5: Final verification
        print(f"\n✅ STEP 3: FINAL VERIFICATION")
        print("-" * 40)
        
        if not dry_run:
            # Re-fetch final state
            final_items = list(container.query_items(query=query, enable_cross_partition_query=True))
            
            # Check for remaining issues
            final_personality_ids = []
            schema_issues = 0
            
            for item in final_items:
                personality_id = item.get('personality_id') or item.get('id')
                final_personality_ids.append(personality_id)
                
                if not item.get('personality_id'):
                    schema_issues += 1
            
            final_unique = len(set(final_personality_ids))
            final_total = len(final_personality_ids)
            final_duplicates = final_total - final_unique
            
            print(f"  📊 Final state:")
            print(f"    Total records: {final_total}")
            print(f"    Unique personalities: {final_unique}")
            print(f"    Remaining duplicates: {final_duplicates}")
            print(f"    Schema issues: {schema_issues}")
            
            if final_duplicates == 0 and schema_issues == 0:
                print(f"  🎉 DATABASE IS NOW CLEAN AND CONSISTENT!")
            else:
                print(f"  ⚠️  Issues remain - may need manual intervention")
        
        # Summary
        print(f"\n📊 COMPREHENSIVE CLEANUP SUMMARY:")
        print(f"  Schema fixes: {schema_fix_count}")
        print(f"  Duplicates removed: {duplicate_deletions}")
        print(f"  Final unique personalities: {unique_kept}")
        print(f"  Original records: {len(items)}")
        print(f"  Final records: {unique_kept} (saved {len(items) - unique_kept} records)")
        
        if dry_run:
            print(f"\n⚠️  This was a DRY RUN - no actual changes made")
            print(f"   Run with --execute to perform actual cleanup")
        else:
            print(f"\n✅ COMPREHENSIVE CLEANUP COMPLETED!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during comprehensive cleanup: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Comprehensive idempotent database cleanup')
    parser.add_argument('--execute', action='store_true', help='Actually perform changes (default: dry run)')
    
    args = parser.parse_args()
    
    comprehensive_cleanup(dry_run=not args.execute)
