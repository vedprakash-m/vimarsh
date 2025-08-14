#!/usr/bin/env python3
"""
PROPER IDEMPOTENT PERSONALITY_ID FIX
Modifies existing records in-place without creating duplicates
"""
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent / 'backend'))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from azure.cosmos import CosmosClient

def proper_personality_id_fix(dry_run=True):
    """Properly add personality_id field by modifying existing records in-place"""
    connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
    if not connection_string:
        print("❌ AZURE_COSMOS_CONNECTION_STRING not set")
        return False
    
    database_name = os.getenv('AZURE_COSMOS_DATABASE_NAME', 'vimarsh-multi-personality')
    
    try:
        client = CosmosClient.from_connection_string(connection_string)
        database = client.get_database_client(database_name)
        container = database.get_container_client('personalities')
        
        print(f"🔧 {'DRY RUN: ' if dry_run else ''}PROPER PERSONALITY_ID FIX")
        print("=" * 60)
        
        # Get all personalities - fresh query each time
        query = "SELECT * FROM c"
        items = list(container.query_items(query=query, enable_cross_partition_query=True))
        
        print(f"📊 Found {len(items)} total records")
        
        fixed_count = 0
        already_good_count = 0
        
        for item in items:
            cosmos_id = item.get('id')  # The Cosmos DB document ID
            has_personality_id = 'personality_id' in item and item.get('personality_id') is not None
            
            if has_personality_id:
                print(f"✅ {cosmos_id}: Already has personality_id='{item.get('personality_id')}'")
                already_good_count += 1
            else:
                print(f"🔧 {cosmos_id}: Missing personality_id field, adding it")
                
                if not dry_run:
                    # CRITICAL: Modify the existing item dictionary directly
                    # Add the personality_id field to match the id
                    item['personality_id'] = cosmos_id
                    
                    # Use upsert_item - this will UPDATE the existing document
                    # because the id and partition key match
                    try:
                        result = container.upsert_item(body=item)
                        print(f"  ✅ Successfully added personality_id to {cosmos_id}")
                        fixed_count += 1
                    except Exception as e:
                        print(f"  ❌ Failed to update {cosmos_id}: {e}")
                        # Continue with other records even if one fails
                        continue
                else:
                    fixed_count += 1
        
        print(f"\n📊 SUMMARY:")
        print(f"  Records already good: {already_good_count}")
        print(f"  Records needing fix: {fixed_count}")
        print(f"  Total records: {already_good_count + fixed_count}")
        
        if dry_run:
            print(f"\n⚠️  This was a DRY RUN - no actual changes made")
            print(f"   Run with --execute to perform actual fixes")
        else:
            print(f"\n✅ PERSONALITY_ID FIX COMPLETED!")
            
            # VERIFICATION: Fresh query to check results
            print(f"\n🔍 VERIFICATION (fresh query):")
            verification_items = list(container.query_items(query=query, enable_cross_partition_query=True))
            
            missing_personality_id = 0
            has_personality_id = 0
            
            for item in verification_items:
                if 'personality_id' in item and item.get('personality_id') is not None:
                    has_personality_id += 1
                else:
                    missing_personality_id += 1
                    print(f"  ❌ {item.get('id', 'NO_ID')}: Still missing personality_id")
            
            print(f"  Total records: {len(verification_items)}")
            print(f"  Records with personality_id: {has_personality_id}")
            print(f"  Records missing personality_id: {missing_personality_id}")
            
            if missing_personality_id == 0:
                print(f"  🎉 SUCCESS: ALL RECORDS NOW HAVE PERSONALITY_ID FIELD!")
            else:
                print(f"  ⚠️  WARNING: {missing_personality_id} records still missing personality_id")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during personality_id fix: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Proper personality_id field fix')
    parser.add_argument('--execute', action='store_true', help='Actually perform fixes (default: dry run)')
    
    args = parser.parse_args()
    
    proper_personality_id_fix(dry_run=not args.execute)
