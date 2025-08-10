#!/usr/bin/env python3
"""
Simple test script to create one Phase 2 container
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../.env')

try:
    from azure.cosmos import CosmosClient, PartitionKey
    
    def main():
        print("🧪 Testing container creation...")
        
        # Get connection
        connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
        client = CosmosClient.from_connection_string(connection_string)
        database_name = 'vimarsh-multi-personality'
        database = client.get_database_client(database_name)
        
        print(f"📊 Connected to database: {database_name}")
        
        # Try to create a simple container
        try:
            container_name = 'test-conversation-sessions'
            print(f"📦 Creating test container: {container_name}")
            
            # Use the older API format first
            container = database.create_container(
                id=container_name,
                partition_key=PartitionKey(path='/partition_key')
            )
            
            print(f"✅ Created container: {container_name}")
            
            # Clean up - delete the test container
            database.delete_container(container_name)
            print(f"🗑️ Cleaned up test container")
            
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            print(f"Error type: {type(e)}")
            return False

    if __name__ == "__main__":
        success = main()
        if success:
            print("🎉 Container creation API works!")
        else:
            print("❌ Container creation failed")
            sys.exit(1)

except ImportError as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)
