#!/usr/bin/env python3
"""
Simple direct fix for adding personality_id field
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

def fix_personality_id_field(dry_run=True):
    """Simple fix to add missing personality_id field"""
    connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
    if not connection_string:
        print("❌ AZURE_COSMOS_CONNECTION_STRING not set")
        return False
    
    database_name = os.getenv('AZURE_COSMOS_DATABASE_NAME', 'vimarsh-multi-personality')
    
    try:
        client = CosmosClient.from_connection_string(connection_string)
        database = client.get_database_client(database_name)
        container = database.get_container_client('personalities')
        
        print(f"🔧 {'DRY RUN: ' if dry_run else ''}FIXING PERSONALITY_ID FIELD")
        print("=" * 50)
        
        # Get all personalities
        query = "SELECT * FROM c"
        items = list(container.query_items(query=query, enable_cross_partition_query=True))
        
        print(f"📊 Found {len(items)} total records")
        
        fix_count = 0
        
        for item in items:
            personality_id_value = item.get('id')  # Use the 'id' field as personality_id
            has_personality_id = 'personality_id' in item
            
            if not has_personality_id and personality_id_value:
                print(f"🔧 Adding personality_id='{personality_id_value}' to record {personality_id_value}")
                
                if not dry_run:
                    # Add the personality_id field
                    item['personality_id'] = personality_id_value
                    
                    # Use upsert_item which will insert or update
                    try:
                        container.upsert_item(body=item)
                        print(f"  ✅ Successfully updated record {personality_id_value}")
                        fix_count += 1
                    except Exception as e:
                        print(f"  ❌ Failed to update record {personality_id_value}: {e}")
                        return False
                else:
                    fix_count += 1
            elif has_personality_id:
                print(f"✅ Record {personality_id_value} already has personality_id field")
        
        print(f"\n📊 SUMMARY:")
        print(f"  Records needing personality_id fix: {fix_count}")
        
        if dry_run:
            print(f"⚠️  This was a DRY RUN - no actual changes made")
            print(f"   Run with --execute to perform actual fixes")
        else:
            print(f"✅ PERSONALITY_ID FIXES COMPLETED!")
            
            # Verify the fix worked
            print(f"\n🔍 VERIFICATION:")
            updated_items = list(container.query_items(query=query, enable_cross_partition_query=True))
            missing_personality_id = 0
            
            for item in updated_items:
                if 'personality_id' not in item:
                    missing_personality_id += 1
            
            print(f"  Total records: {len(updated_items)}")
            print(f"  Records missing personality_id: {missing_personality_id}")
            
            if missing_personality_id == 0:
                print(f"  🎉 ALL RECORDS NOW HAVE PERSONALITY_ID FIELD!")
            else:
                print(f"  ⚠️  {missing_personality_id} records still missing personality_id")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during personality_id fix: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Fix missing personality_id fields')
    parser.add_argument('--execute', action='store_true', help='Actually perform fixes (default: dry run)')
    
    args = parser.parse_args()
    
    fix_personality_id_field(dry_run=not args.execute)
