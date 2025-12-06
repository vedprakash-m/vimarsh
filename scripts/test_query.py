#!/usr/bin/env python3
"""Test query with STARTSWITH"""

import os
import sys
sys.path.insert(0, 'backend')

from dotenv import load_dotenv
from azure.cosmos import CosmosClient

load_dotenv('.env')

cs = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
client = CosmosClient.from_connection_string(cs)
db = client.get_database_client('vimarsh-multi-personality')
c = db.get_container_client('personality_vectors')

# Test STARTSWITH query
query = "SELECT * FROM c WHERE STARTSWITH(c.personality_id, 'krishna_') OFFSET 0 LIMIT 3"
try:
    results = list(c.query_items(query, enable_cross_partition_query=True))
    print(f"Found {len(results)} documents starting with 'krishna_'")
    for doc in results:
        print(f"  - {doc.get('id')}: {doc.get('personality_id')}")
except Exception as e:
    print(f"Query failed: {e}")
    
    # Try alternative query
    print("\nTrying alternative query...")
    query2 = "SELECT c.id, c.personality_id FROM c WHERE c.personality_id LIKE 'krishna_%' OFFSET 0 LIMIT 3"
    try:
        results2 = list(c.query_items(query2, enable_cross_partition_query=True))
        print(f"Found {len(results2)} documents")
    except Exception as e2:
        print(f"LIKE also failed: {e2}")
        
        # Try substring
        print("\nTrying SUBSTRING...")
        query3 = "SELECT c.id, c.personality_id FROM c WHERE SUBSTRING(c.personality_id, 0, 9) = 'krishna_' OFFSET 0 LIMIT 3"
        try:
            results3 = list(c.query_items(query3, enable_cross_partition_query=True))
            print(f"Found {len(results3)} documents")
        except Exception as e3:
            print(f"SUBSTRING failed: {e3}")
