#!/usr/bin/env python3
"""Check what's actually in the Cosmos DB"""

import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../../.env')

try:
    from azure.cosmos import CosmosClient
    
    # Get connection string
    connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
    client = CosmosClient.from_connection_string(connection_string)
    
    # Get database and container
    database = client.get_database_client('vimarsh-multi-personality')
    container = database.get_container_client('personality-vectors')
    
    # Query for all entries to check distribution
    all_entries_query = "SELECT c.personality, c.integration_date FROM c"
    
    print("🔍 Analyzing personality distribution by date:")
    print("=" * 80)
    
    personality_counts = {}
    date_counts = {}
    total_entries = 0
    
    for item in container.query_items(query=all_entries_query, enable_cross_partition_query=True):
        personality = item.get('personality', 'Unknown')
        integration_date = item.get('integration_date', 'Unknown')
        
        # Count by personality
        personality_counts[personality] = personality_counts.get(personality, 0) + 1
        
        # Count by date
        date_counts[integration_date] = date_counts.get(integration_date, 0) + 1
        
        total_entries += 1
    
    print("By Integration Date:")
    for date, count in sorted(date_counts.items()):
        print(f"  {date}: {count} entries")
    
    print("\nBy Personality:")
    for personality, count in sorted(personality_counts.items()):
        print(f"  {personality}: {count} entries")
    
    print(f"\nTotal entries: {total_entries}")
    
    # Check specific entry from today with details
    sample_today_query = "SELECT c.id, c.personality, c.source, c.keywords, c.has_embedding, c.integration_date FROM c WHERE c.integration_date = '2025-07-28' OFFSET 0 LIMIT 3"
    
    print("\n📋 Sample entries from today (2025-07-28):")
    print("=" * 60)
    
    sample_items = list(container.query_items(query=sample_today_query, enable_cross_partition_query=True))
    if sample_items:
        for i, item in enumerate(sample_items, 1):
            print(f"Entry {i}:")
            print(f"  ID: {item.get('id', 'N/A')}")
            print(f"  Personality: {item.get('personality', 'N/A')}")
            print(f"  Source: {item.get('source', 'N/A')[:30]}...")
            print(f"  Keywords: {item.get('keywords', 'N/A')}")
            print(f"  Has embedding: {item.get('has_embedding', 'N/A')}")
            print()
    else:
        print("No entries found for today")
    
except Exception as e:
    print(f"❌ Error: {e}")
