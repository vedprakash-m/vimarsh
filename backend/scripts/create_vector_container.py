#!/usr/bin/env python3
"""
Create the spiritual-vectors container in Cosmos DB for the vector database service
"""

import os
import sys
from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosResourceExistsError

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from dotenv import load_dotenv
    load_dotenv()
    print("[OK] Loaded environment variables")
except ImportError:
    print("[WARNING] python-dotenv not available")

def create_vector_container():
    """Create the spiritual-vectors container with proper configuration"""
    try:
        # Get connection string
        connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
        if not connection_string:
            print("❌ AZURE_COSMOS_CONNECTION_STRING not found in environment")
            return False
        
        # Initialize Cosmos client
        client = CosmosClient.from_connection_string(connection_string)
        print("✅ Connected to Cosmos DB")
        
        # Get or create database
        try:
            database = client.create_database('vimarsh-multi-personality')
            print("✅ Created vimarsh-multi-personality database")
        except CosmosResourceExistsError:
            database = client.get_database_client('vimarsh-multi-personality')
            print("✅ Using existing vimarsh-multi-personality database")
        
        # Container configuration
        from azure.cosmos.partition_key import PartitionKey
        
        # Create container (no throughput for serverless accounts)
        try:
            container = database.create_container(
                id='spiritual-vectors',
                partition_key=PartitionKey(path='/personality')
            )
            print("✅ Created spiritual-vectors container successfully")
            print(f"   Container ID: {container.id}")
            print("   Partition Key: /personality")
            print("   Mode: Serverless")
            return True
            
        except CosmosResourceExistsError:
            print("✅ Container 'spiritual-vectors' already exists")
            return True
            
    except Exception as e:
        print(f"❌ Error creating container: {e}")
        return False

if __name__ == "__main__":
    print("Creating Cosmos DB container for vector database...")
    print("=" * 50)
    
    success = create_vector_container()
    
    if success:
        print("=" * 50)
        print("✅ Container setup completed successfully!")
        print("   You can now run the vector database migration.")
        sys.exit(0)
    else:
        print("=" * 50)
        print("❌ Container setup failed!")
        sys.exit(1)
