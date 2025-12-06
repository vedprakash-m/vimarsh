#!/usr/bin/env python3
"""Check sample document structure"""

import os
import sys
import json
sys.path.insert(0, 'backend')

from dotenv import load_dotenv
from azure.cosmos import CosmosClient

load_dotenv('.env')

cs = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
if not cs:
    print("❌ No connection string")
    sys.exit(1)

client = CosmosClient.from_connection_string(cs)
db = client.get_database_client('vimarsh-multi-personality')
c = db.get_container_client('personality_vectors')

# Get 5 sample documents
query = "SELECT TOP 5 * FROM c"
try:
    results = list(c.query_items(query, enable_cross_partition_query=True))
    print(f"Retrieved {len(results)} sample documents\n")
    
    for i, doc in enumerate(results):
        print(f"\n=== Document {i+1} ===")
        print(f"Keys in document: {list(doc.keys())}")
        
        # Print key fields
        for key in ['id', 'personality', 'content', 'embedding', 'embedding_model', 'domain', 'source', 'chunk_index']:
            if key in doc:
                val = doc[key]
                if isinstance(val, list):
                    if len(val) > 0 and isinstance(val[0], (int, float)):
                        print(f"  {key}: <list of {len(val)} numbers, first={val[0]:.4f}>")
                    else:
                        print(f"  {key}: <list of {len(val)} items>")
                elif isinstance(val, dict):
                    print(f"  {key}: <dict with keys {list(val.keys())}>")
                elif isinstance(val, str):
                    if len(val) > 80:
                        print(f"  {key}: {val[:80]}...")
                    else:
                        print(f"  {key}: {val}")
                else:
                    print(f"  {key}: {val}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
