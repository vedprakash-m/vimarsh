#!/usr/bin/env python3
"""Check what containers exist in the Cosmos DB"""

import os
import sys
from dotenv import load_dotenv

# Add the parent directory to sys.path to import from backend
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Load environment variables from root .env
load_dotenv('../../.env')

try:
    from azure.cosmos import CosmosClient
    
    # Get connection string
    connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
    if not connection_string:
        print("❌ No AZURE_COSMOS_CONNECTION_STRING found in environment")
        sys.exit(1)
    
    client = CosmosClient.from_connection_string(connection_string)
    
    # Get database
    database_name = os.getenv('AZURE_COSMOS_DATABASE_NAME', 'vimarsh-multi-personality')
    database = client.get_database_client(database_name)
    
    print(f"🗄️ Checking containers in database: {database_name}")
    print("=" * 80)
    
    # List all containers
    containers = list(database.list_containers())
    
    if not containers:
        print("No containers found in the database")
    else:
        print(f"Found {len(containers)} containers:")
        print()
        
        for container_info in containers:
            container_id = container_info['id']
            partition_key = container_info.get('partitionKey', {}).get('paths', ['Unknown'])
            
            print(f"📦 Container: {container_id}")
            print(f"   Partition Key: {partition_key}")
            
            # Get container client to check document count
            try:
                container = database.get_container_client(container_id)
                
                # Try to get some sample documents and count
                query = "SELECT VALUE COUNT(1) FROM c"
                try:
                    count_result = list(container.query_items(query=query, enable_cross_partition_query=True))
                    doc_count = count_result[0] if count_result else 0
                except:
                    doc_count = "Unable to count"
                
                print(f"   Document Count: {doc_count}")
                
                # Get sample document to show schema
                try:
                    sample_query = "SELECT TOP 1 * FROM c"
                    sample_docs = list(container.query_items(query=sample_query, enable_cross_partition_query=True))
                    if sample_docs:
                        sample_doc = sample_docs[0]
                        print(f"   Sample fields: {list(sample_doc.keys())}")
                    else:
                        print("   Sample fields: No documents found")
                except Exception as e:
                    print(f"   Sample fields: Error getting sample - {e}")
                
            except Exception as e:
                print(f"   Error accessing container: {e}")
            
            print()
    
    print("\n🔍 Current Database Architecture Summary:")
    print("=" * 50)
    print("Current containers:")
    for container_info in containers:
        print(f"  - {container_info['id']}")
    
    print("\nExpected containers per new design:")
    expected_containers = [
        "users", "user_sessions", "user_interactions", 
        "personalities", "personality_vectors",
        "user_analytics", "content_analytics", "daily_metrics",
        "abuse_incidents", "incidents_by_content", "content_popularity"
    ]
    for container in expected_containers:
        print(f"  - {container}")
    
    current_names = [c['id'] for c in containers]
    missing = [c for c in expected_containers if c not in current_names]
    extra = [c for c in current_names if c not in expected_containers]
    
    if missing:
        print(f"\n⚠️ Missing containers: {missing}")
    if extra:
        print(f"\n📋 Extra containers: {extra}")
    
except Exception as e:
    print(f"❌ Error: {e}")
