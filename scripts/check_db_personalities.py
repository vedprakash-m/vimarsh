#!/usr/bin/env python3
"""
Quick script to check personalities in the database
"""
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent / 'backend'))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from azure.cosmos import CosmosClient

def check_db_personalities():
    """Check personalities currently in database"""
    connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
    if not connection_string:
        print("❌ AZURE_COSMOS_CONNECTION_STRING not set")
        return
    
    database_name = os.getenv('AZURE_COSMOS_DATABASE_NAME', 'vimarsh-multi-personality')
    
    try:
        client = CosmosClient.from_connection_string(connection_string)
        database = client.get_database_client(database_name)
        container = database.get_container_client('personalities')
        
        # Query all personalities
        query = "SELECT c.id, c.name, c.personality_id FROM c"
        items = list(container.query_items(query=query, enable_cross_partition_query=True))
        
        print(f"🔍 Found {len(items)} personalities in database:")
        print()
        
        personalities = []
        for item in items:
            personality_id = item.get('personality_id') or item.get('id')
            name = item.get('name', 'Unknown')
            personalities.append(personality_id)
            print(f"  - {personality_id}: {name}")
        
        print()
        print(f"📋 Personality IDs: {sorted(personalities)}")
        return personalities
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

if __name__ == "__main__":
    check_db_personalities()
