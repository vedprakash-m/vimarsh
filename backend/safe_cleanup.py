#!/usr/bin/env python3
"""
Safe cleanup script - ONLY deletes the 2 old containers after migration
- personality-vectors (migrated to personality_vectors)
- user_activity (split into user_sessions + user_interactions)
"""
import os
import sys
import json
from azure.cosmos import CosmosClient

def parse_connection_string(connection_string):
    """Parse Cosmos DB connection string"""
    parts = {}
    for part in connection_string.split(';'):
        if '=' in part:
            key, value = part.split('=', 1)
            parts[key] = value
    return parts

def main():
    # Containers to clean up (ONLY these 2)
    OLD_CONTAINERS_TO_DELETE = ['personality-vectors', 'user_activity']
    
    try:
        # Load local settings
        with open('local.settings.json', 'r') as f:
            settings = json.load(f)
        
        # Get connection details
        connection_string = settings['Values']['AZURE_COSMOS_CONNECTION_STRING']
        database_name = settings['Values']['AZURE_COSMOS_DATABASE_NAME']
        
        # Parse connection string
        conn_parts = parse_connection_string(connection_string)
        endpoint = conn_parts.get('AccountEndpoint')
        key = conn_parts.get('AccountKey')
        
        if not endpoint or not key:
            print('❌ Could not parse connection string')
            return
        
        # Connect to Cosmos DB
        print(f'🔗 Connecting to database: {database_name}')
        client = CosmosClient(endpoint, key)
        database = client.get_database_client(database_name)
        
        # List all containers first
        print('\n📋 Current containers:')
        all_containers = list(database.list_containers())
        for container in all_containers:
            print(f'  - {container["id"]}')
        
        # Find old containers that exist
        existing_old_containers = []
        for container in all_containers:
            if container['id'] in OLD_CONTAINERS_TO_DELETE:
                existing_old_containers.append(container['id'])
        
        if not existing_old_containers:
            print('\n✅ No old containers found - cleanup already completed!')
            return
        
        print(f'\n⚠️  Found {len(existing_old_containers)} old containers to clean up:')
        for container_name in existing_old_containers:
            print(f'    - {container_name}')
        
        # Ask for confirmation
        print(f'\n🚨 This will DELETE {len(existing_old_containers)} containers:')
        for container_name in existing_old_containers:
            print(f'    - {container_name}')
        
        print(f'\\n📋 The following {len(all_containers) - len(existing_old_containers)} containers will be PRESERVED:')
        for container in all_containers:
            if container['id'] not in OLD_CONTAINERS_TO_DELETE:
                print(f'    - {container["id"]}')
        
        response = input('\\nAre you sure you want to proceed? (type "yes" to confirm): ')
        
        if response.lower() != 'yes':
            print('❌ Cleanup cancelled')
            return
        
        # Delete old containers
        print('\\n🗑️  Starting cleanup...')
        for container_name in existing_old_containers:
            try:
                print(f'  Deleting {container_name}...')
                container = database.get_container_client(container_name)
                database.delete_container(container)
                print(f'  ✅ Deleted {container_name}')
            except Exception as e:
                print(f'  ❌ Failed to delete {container_name}: {str(e)}')
        
        print('\\n🎉 Cleanup completed!')
        
        # Show final state
        print('\\n📋 Remaining containers:')
        remaining_containers = list(database.list_containers())
        for container in remaining_containers:
            print(f'  - {container["id"]}')
        
        print(f'\\nFinal count: {len(remaining_containers)} containers')
        
    except Exception as e:
        print(f'❌ Error: {str(e)}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
