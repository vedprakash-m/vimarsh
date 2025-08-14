#!/usr/bin/env python3
"""
Schema Analysis and Fix Script
Analyzes personality records and fixes schema inconsistencies
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

def analyze_schema():
    """Analyze schema differences between personality records"""
    connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
    if not connection_string:
        print("❌ AZURE_COSMOS_CONNECTION_STRING not set")
        return
    
    database_name = os.getenv('AZURE_COSMOS_DATABASE_NAME', 'vimarsh-multi-personality')
    
    try:
        client = CosmosClient.from_connection_string(connection_string)
        database = client.get_database_client(database_name)
        container = database.get_container_client('personalities')
        
        # Get all personalities
        query = "SELECT * FROM c"
        items = list(container.query_items(query=query, enable_cross_partition_query=True))
        
        print(f"🔍 SCHEMA ANALYSIS - Found {len(items)} total records")
        print("=" * 60)
        
        # Analyze schema patterns
        schema_groups = defaultdict(list)
        
        for item in items:
            # Create schema signature
            fields = set(item.keys())
            has_personality_id = 'personality_id' in fields
            has_extensive_fields = 'llm_config' in fields or 'content_filters' in fields
            
            schema_type = "unknown"
            if has_personality_id and not has_extensive_fields:
                schema_type = "old_simple"
            elif not has_personality_id and has_extensive_fields:
                schema_type = "new_extensive"
            elif has_personality_id and has_extensive_fields:
                schema_type = "complete"
            else:
                schema_type = "minimal"
            
            schema_groups[schema_type].append(item)
        
        # Report findings
        for schema_type, records in schema_groups.items():
            print(f"\n📋 {schema_type.upper()} SCHEMA ({len(records)} records):")
            
            if records:
                sample = records[0]
                field_count = len(sample.keys())
                print(f"  Sample fields ({field_count}): {', '.join(sorted(sample.keys())[:10])}...")
                
                for i, record in enumerate(records[:3]):
                    personality_id = record.get('personality_id') or record.get('id')
                    name = record.get('name', 'NO_NAME')
                    print(f"    Record {i+1}: {personality_id} ({name})")
        
        # Show specific issues
        print(f"\n🚨 SCHEMA ISSUES:")
        
        old_simple = schema_groups.get('old_simple', [])
        new_extensive = schema_groups.get('new_extensive', [])
        
        if old_simple:
            print(f"  ❌ {len(old_simple)} records have personality_id but lack extensive fields")
        
        if new_extensive:
            print(f"  ❌ {len(new_extensive)} records have extensive fields but lack personality_id")
        
        return schema_groups
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {}

def fix_schema(dry_run=True):
    """Fix schema inconsistencies"""
    connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
    if not connection_string:
        print("❌ AZURE_COSMOS_CONNECTION_STRING not set")
        return False
    
    database_name = os.getenv('AZURE_COSMOS_DATABASE_NAME', 'vimarsh-multi-personality')
    
    try:
        client = CosmosClient.from_connection_string(connection_string)
        database = client.get_database_client(database_name)
        container = database.get_container_client('personalities')
        
        print(f"🔧 {'DRY RUN: ' if dry_run else ''}SCHEMA FIX STARTING")
        print("=" * 60)
        
        # Get all personalities
        query = "SELECT * FROM c"
        items = list(container.query_items(query=query, enable_cross_partition_query=True))
        
        fix_count = 0
        
        for item in items:
            personality_id = item.get('personality_id') or item.get('id')
            has_personality_id = 'personality_id' in item
            has_extensive_fields = 'llm_config' in item or 'content_filters' in item
            
            needs_fix = False
            
            # Case 1: Extensive fields but missing personality_id
            if has_extensive_fields and not has_personality_id:
                print(f"🔧 {personality_id}: Adding missing personality_id field")
                if not dry_run:
                    item['personality_id'] = personality_id
                    container.upsert_item(item)
                needs_fix = True
            
            # Case 2: Has personality_id but lacks extensive fields (less critical)
            # We'll leave these as-is since they might be intentionally simple
            
            if needs_fix:
                fix_count += 1
        
        print(f"\n📊 SCHEMA FIX SUMMARY:")
        print(f"  Records needing fixes: {fix_count}")
        
        if dry_run:
            print(f"⚠️  This was a DRY RUN - no actual changes made")
            print(f"   Run with --execute to perform actual fixes")
        else:
            print(f"✅ SCHEMA FIXES COMPLETED")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during schema fix: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Schema analysis and fix')
    parser.add_argument('--execute', action='store_true', help='Actually perform fixes (default: dry run)')
    parser.add_argument('--analyze-only', action='store_true', help='Only analyze schema, no fixes')
    
    args = parser.parse_args()
    
    if args.analyze_only:
        analyze_schema()
    else:
        analyze_schema()
        print()
        fix_schema(dry_run=not args.execute)
