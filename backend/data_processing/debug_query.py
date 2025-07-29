#!/usr/bin/env python3
"""
Debug script to check the exact values in the database entries
"""

import os
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
    
    print("🔍 Checking exact values in Krishna entries:")
    print("=" * 60)
    
    # Query for Krishna entries specifically
    krishna_query = "SELECT c.id, c.personality, c.integration_date, c.has_embedding FROM c WHERE c.personality = 'krishna' OFFSET 0 LIMIT 5"
    
    krishna_items = list(container.query_items(query=krishna_query, enable_cross_partition_query=True))
    
    if krishna_items:
        for i, item in enumerate(krishna_items, 1):
            print(f"Entry {i}:")
            print(f"  ID: {item.get('id')}")
            print(f"  Personality: '{item.get('personality')}' (type: {type(item.get('personality'))})")
            print(f"  Integration Date: '{item.get('integration_date')}' (type: {type(item.get('integration_date'))})")
            print(f"  Has Embedding: '{item.get('has_embedding')}' (type: {type(item.get('has_embedding'))})")
            print()
    
    # Test different query variations
    print("\n🧪 Testing different query variations:")
    print("=" * 60)
    
    # Test query 1: Exact match
    query1 = "SELECT COUNT(1) as count FROM c WHERE c.integration_date = 'Unknown'"
    result1 = list(container.query_items(query=query1, enable_cross_partition_query=True))[0]
    print(f"Query 'integration_date = \"Unknown\"': {result1['count']} entries")
    
    # Test query 2: IS_NULL
    query2 = "SELECT COUNT(1) as count FROM c WHERE IS_NULL(c.integration_date)"
    result2 = list(container.query_items(query=query2, enable_cross_partition_query=True))[0]
    print(f"Query 'IS_NULL(integration_date)': {result2['count']} entries")
    
    # Test query 3: Combined
    query3 = "SELECT COUNT(1) as count FROM c WHERE c.integration_date = 'Unknown' OR IS_NULL(c.integration_date)"
    result3 = list(container.query_items(query=query3, enable_cross_partition_query=True))[0]
    print(f"Query 'integration_date = \"Unknown\" OR IS_NULL': {result3['count']} entries")
    
    # Test query 4: Krishna personality with Unknown date
    query4 = "SELECT COUNT(1) as count FROM c WHERE c.personality = 'krishna' AND c.integration_date = 'Unknown'"
    result4 = list(container.query_items(query=query4, enable_cross_partition_query=True))[0]
    print(f"Query 'personality = \"krishna\" AND integration_date = \"Unknown\"': {result4['count']} entries")
    
except Exception as e:
    print(f"❌ Error: {e}")
