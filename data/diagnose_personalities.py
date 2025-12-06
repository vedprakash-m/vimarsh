#!/usr/bin/env python3
"""Diagnostic to find actual personality values in database"""

import os
import sys
sys.path.insert(0, '../backend')

from azure.cosmos import CosmosClient

try:
    cs = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
    if not cs:
        # Try using Azure credentials
        from azure.identity import DefaultAzureCredential
        import json
        
        # Try reading from local Cosmos emulator or Azure
        # Get connection URL and key from somewhere
        url = "https://vimarsh-db-westus2.documents.azure.com:443/"
        # This won't work without credentials, but DefaultAzureCredential should handle it
        creds = DefaultAzureCredential()
        client = CosmosClient(url=url, credential=creds)
    else:
        client = CosmosClient.from_connection_string(cs)
    
    db = client.get_database_client('vimarsh-multi-personality')
    c = db.get_container_client('personality_vectors')
    
    # Get distinct personalities
    query = "SELECT DISTINCT c.personality FROM c"
    results = list(c.query_items(query, enable_cross_partition_query=True))
    
    personalities = set()
    for r in results:
        p = r.get('personality')
        if p:
            personalities.add(p)
    
    print(f"Found {len(personalities)} unique personalities:")
    for p in sorted(personalities):
        print(f"  - {p}")
        
    # Now count by personality
    print("\nCounts by personality:")
    for p in sorted(personalities):
        query2 = f"SELECT VALUE COUNT(1) FROM c WHERE c.personality = '{p}'"
        count_result = list(c.query_items(query2, enable_cross_partition_query=True))
        count = count_result[0] if count_result else 0
        print(f"  {p}: {count}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
