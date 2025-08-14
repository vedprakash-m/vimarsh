#!/usr/bin/env python3
"""
Create new containers for the migration
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
    from azure.cosmos import CosmosClient, PartitionKey, ThroughputProperties
    
    def create_container_with_config(database, container_config):
        """Create a container with specified configuration"""
        try:
            container_name = container_config['name']
            
            print(f"📦 Creating container: {container_name}")
            
            # Container properties
            container_properties = {
                'id': container_name,
                'partitionKey': PartitionKey(path=container_config['partition_key'])
            }
            
            # Add TTL if specified
            if container_config.get('ttl'):
                container_properties['defaultTtl'] = container_config['ttl']
            
            # Add vector embedding policy if specified
            if container_config.get('vector_embedding_policy'):
                container_properties['vectorEmbeddingPolicy'] = container_config['vector_embedding_policy']
            
            # Throughput properties
            throughput = ThroughputProperties(
                max_throughput=container_config.get('max_throughput', 4000),
                auto_scale_increment_percentage=10
            )
            
            # Create container
            container = database.create_container(
                body=container_properties,
                offer_throughput=throughput
            )
            
            print(f"✅ Created container: {container_name}")
            print(f"   Partition Key: {container_config['partition_key']}")
            print(f"   Max RU/s: {container_config.get('max_throughput', 4000)}")
            if container_config.get('ttl'):
                print(f"   TTL: {container_config['ttl']} seconds")
            
            return container
            
        except Exception as e:
            print(f"❌ Error creating container {container_config['name']}: {e}")
            return None
    
    def main():
        """Create all new containers for migration"""
        print("🏗️ CREATING NEW CONTAINERS FOR MIGRATION")
        print("=" * 60)
        
        # Get connection
        connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
        if not connection_string:
            print("❌ AZURE_COSMOS_CONNECTION_STRING not found in environment")
            return False
        
        client = CosmosClient.from_connection_string(connection_string)
        database_name = os.getenv('AZURE_COSMOS_DATABASE_NAME', 'vimarsh-multi-personality')
        database = client.get_database_client(database_name)
        
        # Container configurations based on db_design.md
        containers_to_create = [
            # Core Operational Containers
            {
                'name': 'user_sessions',
                'partition_key': '/user_id',
                'max_throughput': 2000,
                'ttl': 7776000  # 90 days
            },
            {
                'name': 'user_interactions',
                'partition_key': '/user_id',
                'max_throughput': 4000,
                'ttl': 15552000  # 180 days
            },
            {
                'name': 'personalities',
                'partition_key': '/personality_id',
                'max_throughput': 1000,
                'ttl': None  # Permanent
            },
            {
                'name': 'personality_vectors',
                'partition_key': '/partition_key',  # Hierarchical key
                'max_throughput': 4000,
                'ttl': None,  # Permanent
                'vector_embedding_policy': {
                    'vectorEmbeddings': [{
                        'path': '/embedding',
                        'dataType': 'float32',
                        'dimensions': 768,
                        'distanceFunction': 'cosine'
                    }]
                }
            },
            
            # Analytics Containers
            {
                'name': 'user_analytics',
                'partition_key': '/user_id',
                'max_throughput': 1000,
                'ttl': None
            },
            {
                'name': 'content_analytics',
                'partition_key': '/source',
                'max_throughput': 1000,
                'ttl': None
            },
            {
                'name': 'daily_metrics',
                'partition_key': '/date',
                'max_throughput': 1000,
                'ttl': 2592000  # 30 days
            },
            {
                'name': 'abuse_incidents',
                'partition_key': '/user_id',
                'max_throughput': 1000,
                'ttl': None
            },
            
            # Materialized Views
            {
                'name': 'engagement_summary',
                'partition_key': '/engagement_tier',
                'max_throughput': 1000,
                'ttl': None
            },
            {
                'name': 'content_popularity',
                'partition_key': '/time_period',
                'max_throughput': 1000,
                'ttl': 2592000  # 30 days
            },
            {
                'name': 'incidents_by_content',
                'partition_key': '/source',
                'max_throughput': 1000,
                'ttl': None
            }
        ]
        
        # Create containers
        created_count = 0
        failed_count = 0
        
        for container_config in containers_to_create:
            # Check if container already exists
            try:
                existing = database.get_container_client(container_config['name'])
                existing.read()  # This will throw if container doesn't exist
                print(f"⚠️ Container {container_config['name']} already exists, skipping")
                continue
            except:
                # Container doesn't exist, create it
                pass
            
            container = create_container_with_config(database, container_config)
            if container:
                created_count += 1
            else:
                failed_count += 1
            
            print()  # Empty line for readability
        
        # Summary
        print("🎉 CONTAINER CREATION COMPLETED")
        print("=" * 40)
        print(f"✅ Created: {created_count} containers")
        print(f"❌ Failed: {failed_count} containers")
        print(f"📊 Total expected: {len(containers_to_create)} containers")
        
        if failed_count == 0:
            print("\n🚀 All containers created successfully!")
            print("Ready for data migration phase.")
        else:
            print(f"\n⚠️ {failed_count} containers failed to create.")
            print("Please review errors above before proceeding.")
        
        return failed_count == 0

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
