#!/usr/bin/env python3
"""
Create new containers for the migration - Serverless version
Based on db_design.md specifications
"""

import os
import sys
from dotenv import load_dotenv

# Add the parent directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Load environment variables from root .env
load_dotenv('../../.env')

try:
    from azure.cosmos import CosmosClient, PartitionKey
    
    def main():
        """Create all new containers for migration"""
        print("🏗️ CREATING NEW CONTAINERS FOR MIGRATION (SERVERLESS)")
        print("=" * 60)
        
        # Get connection
        connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
        if not connection_string:
            print("❌ AZURE_COSMOS_CONNECTION_STRING not found in environment")
            return False
        
        client = CosmosClient.from_connection_string(connection_string)
        database_name = os.getenv('AZURE_COSMOS_DATABASE_NAME', 'vimarsh-multi-personality')
        database = client.get_database_client(database_name)
        
        # Container configurations - no throughput for serverless
        containers_to_create = [
            # Core Operational Containers
            {
                'id': 'user_sessions',
                'partition_key': PartitionKey(path='/user_id'),
                'description': 'User session data with 90-day TTL'
            },
            {
                'id': 'user_interactions',
                'partition_key': PartitionKey(path='/user_id'),
                'description': 'User interaction history with 180-day TTL'
            },
            {
                'id': 'personalities',
                'partition_key': PartitionKey(path='/personality_id'),
                'description': 'Personality configuration data'
            },
            {
                'id': 'personality_vectors',
                'partition_key': PartitionKey(path='/partition_key'),
                'description': 'Personality vectors with hierarchical partitioning'
            },
            # Analytics Containers
            {
                'id': 'user_analytics',
                'partition_key': PartitionKey(path='/user_id'),
                'description': 'Aggregated user analytics'
            },
            {
                'id': 'content_analytics',
                'partition_key': PartitionKey(path='/source'),
                'description': 'Content performance analytics'
            },
            {
                'id': 'daily_metrics',
                'partition_key': PartitionKey(path='/date'),
                'description': 'Daily system metrics'
            },
            {
                'id': 'abuse_incidents',
                'partition_key': PartitionKey(path='/user_id'),
                'description': 'Content moderation incidents'
            },
            # Materialized View Containers
            {
                'id': 'engagement_summary',
                'partition_key': PartitionKey(path='/engagement_tier'),
                'description': 'User engagement summaries'
            },
            {
                'id': 'content_popularity',
                'partition_key': PartitionKey(path='/time_period'),
                'description': 'Content popularity metrics'
            },
            {
                'id': 'incidents_by_content',
                'partition_key': PartitionKey(path='/source'),
                'description': 'Incidents grouped by content source'
            }
        ]
        
        created_count = 0
        failed_count = 0
        skipped_count = 0
        
        for container_config in containers_to_create:
            container_name = container_config['id']
            
            try:
                print(f"📦 Creating container: {container_name}")
                
                # Check if container already exists
                try:
                    existing_container = database.get_container_client(container_name)
                    existing_container.read()
                    print(f"ℹ️ Container {container_name} already exists, skipping")
                    skipped_count += 1
                    continue
                except:
                    pass  # Container doesn't exist, continue with creation
                
                # Create container (no throughput for serverless)
                container = database.create_container(
                    id=container_config['id'],
                    partition_key=container_config['partition_key']
                )
                
                print(f"✅ Created container: {container_name}")
                print(f"   Partition Key: {container_config['partition_key'].path}")
                print(f"   Description: {container_config['description']}")
                created_count += 1
                
            except Exception as e:
                print(f"❌ Error creating container {container_name}: {e}")
                failed_count += 1
        
        print(f"\n🎉 CONTAINER CREATION COMPLETED")
        print("=" * 40)
        print(f"✅ Created: {created_count} containers")
        print(f"ℹ️ Skipped (already exist): {skipped_count} containers") 
        print(f"❌ Failed: {failed_count} containers")
        print(f"📊 Total expected: {len(containers_to_create)} containers")
        
        if failed_count > 0:
            print(f"\n⚠️ {failed_count} containers failed to create.")
            print("Please review errors above before proceeding.")
            return False
        else:
            print(f"\n🎉 All new containers created successfully!")
            print("💡 Note: Using serverless Cosmos DB - no throughput settings applied")
            return True

    if __name__ == "__main__":
        success = main()
        if not success:
            sys.exit(1)

except ImportError:
    print("❌ Error: azure-cosmos package not installed")
    print("Run: pip install azure-cosmos")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
