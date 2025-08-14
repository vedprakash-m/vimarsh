#!/usr/bin/env python3
"""
Check the exact field structure in the database
"""

import os
import azure.cosmos.cosmos_client as cosmos_client

def check_field_structure():
    """Check the field structure of documents in the database"""
    
    # Get connection details from local.settings.json environment
    cosmos_connection_string = os.getenv(
        'COSMOSDB_CONNECTION_STRING', 
        'AccountEndpoint=https://vimarsh-db.documents.azure.com:443/;AccountKey=dFPfklJEMgzjimnjmN9v4m3Yh9UWSKzQUDGNm7MhRBL7c3q0NZiUuqFLQB3mI32Um5NLDDlzaX9dACDbWHkZ2w==;'
    )
    
    # Initialize Cosmos client
    client = cosmos_client.CosmosClient.from_connection_string(cosmos_connection_string)
    database = client.get_database_client('vimarsh-multi-personality')
    container = database.get_container_client('personality_vectors')
    
    print("🔍 Checking field structure for Gandhi documents...")
    
    try:
        # Get a few Gandhi documents to check field structure
        query = "SELECT TOP 2 * FROM c WHERE c.personality = 'gandhi'"
        items = list(container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        
        if items:
            print(f"✅ Found {len(items)} Gandhi documents")
            print("📋 Field structure of first document:")
            for key, value in items[0].items():
                if isinstance(value, str) and len(value) > 100:
                    print(f"   - {key}: {value[:100]}... (truncated)")
                else:
                    print(f"   - {key}: {value}")
        else:
            print("❌ No Gandhi documents found")
            
    except Exception as e:
        print(f"❌ Error checking field structure: {str(e)}")

if __name__ == "__main__":
    check_field_structure()
