#!/usr/bin/env python3
"""Get sample documents to see personality field format"""

import os
import sys
sys.path.insert(0, '../backend')

from azure.cosmos import CosmosClient

# Use connection string from environment
cs = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
if cs:
    client = CosmosClient.from_connection_string(cs)
else:
    # Try default credentials - this is what worked for validate_embeddings
    # Actually, let's just try to connect directly and see what error we get
    # which will tell us what's happening
    print("Attempting to use default Azure credentials...")
    from azure.identity import DefaultAzureCredential, ClientSecretCredential
    try:
        # Check if managed identity or service principal
        cred = DefaultAzureCredential()
        client = CosmosClient(url="https://vimarsh-db.documents.azure.com:443/", credential=cred)
    except Exception as e:
        print(f"Failed: {e}")
        # Maybe it needs specific URL  
        import subprocess
        result = subprocess.run(['az', 'cosmosdb', 'keys', 'list', '--name', 'vimarsh-db', '--resource-group', 'vimarsh-rg', '--query', 'primaryConnectionString', '-o', 'tsv'], capture_output=True, text=True)
        if result.returncode == 0:
            cs = result.stdout.strip()
            print(f"Got connection string from az CLI")
            client = CosmosClient.from_connection_string(cs)
        else:
            print(f"az CLI failed: {result.stderr}")
            sys.exit(1)

db = client.get_database_client('vimarsh-multi-personality')
c = db.get_container_client('personality_vectors')

# Get first 5 documents to understand structure
items = list(c.query_items("SELECT c.id, c.personality, c.content FROM c OFFSET 0 LIMIT 5", enable_cross_partition_query=True))

print(f"Retrieved {len(items)} documents\n")
for i, doc in enumerate(items):
    print(f"Doc {i+1}:")
    print(f"  id: {doc.get('id')}")
    print(f"  personality: {doc.get('personality')} (type: {type(doc.get('personality')).__name__})")
    content = doc.get('content', '')
    if len(content) > 80:
        print(f"  content: {content[:80]}...")
    else:
        print(f"  content: {content}")
    print()
