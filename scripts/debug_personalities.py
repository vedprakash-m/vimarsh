#!/usr/bin/env python3
"""Debug script to check personality values in database"""

import os
import sys
sys.path.insert(0, 'backend')

from dotenv import load_dotenv
from azure.cosmos import CosmosClient

# Load .env
load_dotenv('.env')

cs = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
if not cs:
    print("❌ No connection string")
    sys.exit(1)

client = CosmosClient.from_connection_string(cs)
db = client.get_database_client('vimarsh-multi-personality')
c = db.get_container_client('personality_vectors')

# Get DISTINCT personalities
query = "SELECT DISTINCT c.personality FROM c"
try:
    results = list(c.query_items(query, enable_cross_partition_query=True))
    print(f"Distinct personalities in database:")
    personalities = set()
    for r in results:
        p = r.get('personality')
        if p:
            personalities.add(p)
            print(f"  - {p}")
    
    print(f"\nTotal unique: {len(personalities)}")
    
    # Compare with expected
    expected = {
        'spiritual': ['krishna', 'buddha', 'jesus', 'rumi', 'vivekananda'],
        'philosophical': ['marcus_aurelius', 'lao_tzu', 'confucius', 'aristotle', 'plato', 'socrates'],
    }
    
    print(f"\nExpected personalities (from script):")
    all_expected = []
    for domain, names in expected.items():
        for name in names:
            all_expected.append(name)
            print(f"  - {name}")
    
    print(f"\nMatches:")
    for p in personalities:
        if p.lower() in all_expected:
            print(f"  ✅ {p} matches")
        else:
            print(f"  ❌ {p} does NOT match")
            
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
