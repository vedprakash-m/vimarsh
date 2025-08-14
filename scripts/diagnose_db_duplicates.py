#!/usr/bin/env python3
"""
Diagnose duplicate personalities in the database
"""
import os
import sys
from pathlib import Path
from collections import defaultdict, Counter

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent / 'backend'))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from azure.cosmos import CosmosClient

def diagnose_duplicates():
    """Analyze duplicate personalities and their structure"""
    connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
    if not connection_string:
        print("❌ AZURE_COSMOS_CONNECTION_STRING not set")
        return
    
    database_name = os.getenv('AZURE_COSMOS_DATABASE_NAME', 'vimarsh-multi-personality')
    
    try:
        client = CosmosClient.from_connection_string(connection_string)
        database = client.get_database_client(database_name)
        container = database.get_container_client('personalities')
        
        # Query all personalities with full structure
        query = "SELECT * FROM c"
        items = list(container.query_items(query=query, enable_cross_partition_query=True))
        
        print(f"🔍 DUPLICATE ANALYSIS - Found {len(items)} total records")
        print("=" * 60)
        
        # Group by personality_id
        personality_groups = defaultdict(list)
        for item in items:
            personality_id = item.get('personality_id') or item.get('id')
            personality_groups[personality_id].append(item)
        
        # Count duplicates
        duplicate_count = 0
        unique_count = 0
        
        for personality_id, records in personality_groups.items():
            if len(records) > 1:
                duplicate_count += len(records)
                print(f"\n🚨 DUPLICATE: {personality_id} ({len(records)} copies)")
                for i, record in enumerate(records):
                    cosmos_id = record.get('id', 'NO_ID')
                    name = record.get('name', 'NO_NAME')
                    domain = record.get('domain', 'NO_DOMAIN')
                    print(f"  Copy {i+1}: Cosmos ID={cosmos_id}, Name={name}, Domain={domain}")
            else:
                unique_count += 1
        
        print(f"\n📊 SUMMARY:")
        print(f"  Unique personalities: {len(personality_groups)}")
        print(f"  Total records: {len(items)}")
        print(f"  Duplicate records: {duplicate_count}")
        print(f"  Clean records: {unique_count}")
        print(f"  Waste ratio: {duplicate_count}/{len(items)} = {duplicate_count/len(items)*100:.1f}%")
        
        # Show Cosmos ID patterns
        cosmos_ids = [item.get('id') for item in items]
        cosmos_id_counter = Counter(cosmos_ids)
        
        print(f"\n🔑 COSMOS ID ANALYSIS:")
        for cosmos_id, count in cosmos_id_counter.most_common():
            if count > 1:
                print(f"  Cosmos ID '{cosmos_id}' appears {count} times")
        
        return personality_groups
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {}

if __name__ == "__main__":
    diagnose_duplicates()
