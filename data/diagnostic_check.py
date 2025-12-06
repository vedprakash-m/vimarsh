#!/usr/bin/env python3
"""Quick diagnostic to see what personalities are in the database"""

import os
import sys
sys.path.insert(0, '../backend')

from azure.cosmos import CosmosClient

cs = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
if not cs:
    print("❌ AZURE_COSMOS_CONNECTION_STRING not set")
    sys.exit(1)

client = CosmosClient.from_connection_string(cs)
db = client.get_database_client('vimarsh-multi-personality')
c = db.get_container_client('personality_vectors')

# Get sample documents
query = "SELECT c.personality, COUNT(1) as cnt FROM c GROUP BY c.personality"
try:
    results = list(c.query_items(query, enable_cross_partition_query=True))
    print("Personalities in database (from GROUP BY):")
    for r in results:
        print(f"  {r}")
except Exception as e:
    print(f"GROUP BY failed: {e}")
    print("\nTrying alternative query...")
    
    # Alternative: get personalities from sample
    query2 = "SELECT c.personality FROM c OFFSET 0 LIMIT 20"
    results = list(c.query_items(query2, enable_cross_partition_query=True))
    personalities = set()
    for r in results:
        p = r.get('personality')
        if p:
            personalities.add(p)
    
    print(f"Sample personalities found: {personalities}")
