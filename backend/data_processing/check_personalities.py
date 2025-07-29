#!/usr/bin/env python3
"""Check for new personality entries in Cosmos DB"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
root_env_path = Path(__file__).parent.parent.parent / '.env'
if root_env_path.exists():
    load_dotenv(root_env_path)

try:
    from azure.cosmos import CosmosClient
    
    # Connect to Cosmos DB
    connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
    client = CosmosClient.from_connection_string(connection_string)
    database = client.get_database_client('vimarsh-multi-personality')
    container = database.get_container_client('personality-vectors')
    
    # Check for different personalities
    personalities = ['Buddha', 'Einstein', 'Newton', 'Rumi', 'Marcus Aurelius', 'Lao Tzu', 'Lincoln', 'Confucius']
    
    print("🔍 Checking for new personality entries:")
    print("=" * 50)
    
    for personality in personalities:
        query = f"SELECT c.id FROM c WHERE c.personality = '{personality}'"
        items = list(container.query_items(query=query, enable_cross_partition_query=True))
        count = len(items)
        print(f"  {personality}: {count} entries")
    
    # Check for Krishna entries with different embedding models
    print("\n🔍 Krishna entries by embedding model:")
    print("=" * 50)
    
    query = "SELECT c.embedding_model FROM c WHERE c.personality = 'Krishna'"
    items = list(container.query_items(query=query, enable_cross_partition_query=True))
    
    model_counts = {}
    for item in items:
        model = item.get('embedding_model', 'None')
        model_counts[model] = model_counts.get(model, 0) + 1
    
    for model, count in model_counts.items():
        print(f"  {model}: {count} entries")
    
    # Sample a few new entries to verify they're from the content sourcing
    print("\n📝 Sample entries from new personalities:")
    print("=" * 50)
    
    query = """
    SELECT c.id, c.personality, c.source, c.integration_date, c.has_embedding
    FROM c 
    WHERE c.personality != 'Krishna'
    """
    items = list(container.query_items(query=query, enable_cross_partition_query=True))
    for i, item in enumerate(items[:3]):  # Limit to first 3
        print(f"  ID: {item['id']}")
        print(f"  Personality: {item['personality']}")
        print(f"  Source: {item.get('source', 'N/A')}")
        print(f"  Integration Date: {item.get('integration_date', 'N/A')}")
        print(f"  Has Embedding: {item.get('has_embedding', False)}")
        print()
    
    total_non_krishna = len(items)
    print(f"Total non-Krishna entries: {total_non_krishna}")

except Exception as e:
    print(f"❌ Error: {e}")
