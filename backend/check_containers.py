#!/usr/bin/env python3
"""
Safe script to check current Cosmos DB containers before cleanup
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
        
        # List containers
        print('\n📋 Current containers in database:')
        containers = list(database.list_containers())
        
        old_containers = []
        new_containers = []
        
        for container in containers:
            container_name = container['id']
            print(f'  - {container_name}')
            
            # Categorize containers
            if container_name in ['personality-vectors', 'user_activity']:
                old_containers.append(container_name)
            else:
                new_containers.append(container_name)
        
        print(f'\n📊 Summary:')
        print(f'  Total containers: {len(containers)}')
        print(f'  Old containers (should be cleaned up): {len(old_containers)}')
        for container in old_containers:
            print(f'    - {container}')
        print(f'  New containers (keep): {len(new_containers)}')
        for container in new_containers:
            print(f'    - {container}')
        
        if len(old_containers) == 0:
            print('\n✅ No old containers found - cleanup already completed!')
        else:
            print(f'\n⚠️  Found {len(old_containers)} old containers that should be cleaned up')
        
    except Exception as e:
        print(f'❌ Error: {str(e)}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
