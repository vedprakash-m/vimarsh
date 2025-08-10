#!/usr/bin/env python3
"""
Create Phase 2 Containers for Memory System and Personalization
==============================================================

Creates Cosmos DB containers for:
- Conversation sessions and messages (memory system)
- Wisdom journal entries
- User preferences and personalization
- Advanced analytics containers
"""

import os
import sys
from dotenv import load_dotenv
import json

# Add the parent directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Load environment variables
load_dotenv('../.env')

try:
    from azure.cosmos import CosmosClient, PartitionKey, ThroughputProperties
    from azure.cosmos.exceptions import CosmosResourceExistsError
    
    def create_container_with_indexing(database, container_config):
        """Create a container with specified configuration and indexing policy"""
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
            
            # Add indexing policy if specified
            if container_config.get('indexing_policy'):
                container_properties['indexingPolicy'] = container_config['indexing_policy']
            
            # Add vector embedding policy if specified
            if container_config.get('vector_embedding_policy'):
                container_properties['vectorEmbeddingPolicy'] = container_config['vector_embedding_policy']
            
            # Throughput properties (autoscale)
            throughput = ThroughputProperties(
                max_throughput=container_config.get('max_throughput', 4000),
                auto_scale_increment_percentage=10
            )
            
            # Create container with proper API
            if container_config.get('ttl'):
                container = database.create_container(
                    id=container_name,
                    partition_key=PartitionKey(path=container_config['partition_key']),
                    default_ttl=container_config['ttl'],
                    offer_throughput=throughput
                )
            else:
                container = database.create_container(
                    id=container_name,
                    partition_key=PartitionKey(path=container_config['partition_key']),
                    offer_throughput=throughput
                )
            
            print(f"✅ Created container: {container_name}")
            print(f"   Partition Key: {container_config['partition_key']}")
            print(f"   Max RU/s: {container_config.get('max_throughput', 4000)}")
            if container_config.get('ttl'):
                print(f"   TTL: {container_config['ttl']} seconds")
            if container_config.get('indexing_policy'):
                print(f"   Custom indexing: {len(container_config['indexing_policy']['includedPaths'])} paths")
            
            return container
            
        except CosmosResourceExistsError:
            print(f"⚠️ Container {container_name} already exists, skipping")
            return database.get_container_client(container_name)
        except Exception as e:
            print(f"❌ Error creating container {container_config['name']}: {e}")
            return None
    
    def main():
        """Create all Phase 2 containers"""
        print("🏗️ CREATING PHASE 2 CONTAINERS FOR MEMORY & PERSONALIZATION")
        print("=" * 70)
        
        # Get connection
        connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
        if not connection_string:
            print("❌ AZURE_COSMOS_CONNECTION_STRING not found in environment")
            print("Make sure .env file is properly configured")
            return False
        
        client = CosmosClient.from_connection_string(connection_string)
        database_name = os.getenv('AZURE_COSMOS_DATABASE_NAME', 'vimarsh-multi-personality')
        
        try:
            database = client.get_database_client(database_name)
            print(f"📊 Connected to database: {database_name}")
        except Exception as e:
            print(f"❌ Failed to connect to database {database_name}: {e}")
            return False
        
        # Phase 2 Container configurations based on conversation_models.py
        phase2_containers = [
            # Conversation Memory System
            {
                'name': 'conversation-sessions',
                'partition_key': '/partition_key',  # user_id|personality_id
                'max_throughput': 2000,
                'ttl': None,  # Keep conversations indefinitely
                'indexing_policy': {
                    'indexingMode': 'consistent',
                    'automatic': True,
                    'includedPaths': [
                        {'path': '/user_id/?'},
                        {'path': '/personality_id/?'},
                        {'path': '/status/?'},
                        {'path': '/created_at/?'},
                        {'path': '/updated_at/?'},
                        {'path': '/tags/*'}
                    ],
                    'excludedPaths': [
                        {'path': '/context/*'},
                        {'path': '/_etag/?'}
                    ]
                }
            },
            {
                'name': 'conversation-messages',
                'partition_key': '/partition_key',  # user_id|personality_id
                'max_throughput': 4000,
                'ttl': None,  # Keep messages indefinitely
                'indexing_policy': {
                    'indexingMode': 'consistent',
                    'automatic': True,
                    'includedPaths': [
                        {'path': '/session_id/?'},
                        {'path': '/user_id/?'},
                        {'path': '/personality_id/?'},
                        {'path': '/message_type/?'},
                        {'path': '/timestamp/?'},
                        {'path': '/response_time/?'}
                    ],
                    'excludedPaths': [
                        {'path': '/content/?'},  # Full text content - expensive to index
                        {'path': '/metadata/*'},
                        {'path': '/_etag/?'}
                    ]
                }
            },
            
            # Wisdom Journal System
            {
                'name': 'wisdom-journal',
                'partition_key': '/partition_key',  # user_id
                'max_throughput': 1000,
                'ttl': None,  # Keep journal entries indefinitely
                'indexing_policy': {
                    'indexingMode': 'consistent',
                    'automatic': True,
                    'includedPaths': [
                        {'path': '/user_id/?'},
                        {'path': '/personality_id/?'},
                        {'path': '/entry_type/?'},
                        {'path': '/created_at/?'},
                        {'path': '/updated_at/?'},
                        {'path': '/is_favorite/?'},
                        {'path': '/tags/*'},
                        {'path': '/source_session_id/?'}
                    ],
                    'excludedPaths': [
                        {'path': '/content/?'},  # Full text content
                        {'path': '/metadata/*'},
                        {'path': '/_etag/?'}
                    ]
                }
            },
            
            # User Preferences & Personalization
            {
                'name': 'user-preferences',
                'partition_key': '/partition_key',  # user_id
                'max_throughput': 1000,
                'ttl': None,  # Keep preferences indefinitely
                'indexing_policy': {
                    'indexingMode': 'consistent',
                    'automatic': True,
                    'includedPaths': [
                        {'path': '/user_id/?'},
                        {'path': '/preferred_personalities/*'},
                        {'path': '/conversation_style/?'},
                        {'path': '/language_preference/?'},
                        {'path': '/updated_at/?'}
                    ],
                    'excludedPaths': [
                        {'path': '/notification_settings/*'},
                        {'path': '/privacy_settings/*'},
                        {'path': '/ui_preferences/*'},
                        {'path': '/_etag/?'}
                    ]
                }
            },
            
            # Advanced Analytics for Phase 2
            {
                'name': 'conversation-analytics',
                'partition_key': '/user_id',
                'max_throughput': 1000,
                'ttl': 7776000,  # 90 days
                'indexing_policy': {
                    'indexingMode': 'consistent',
                    'automatic': True,
                    'includedPaths': [
                        {'path': '/user_id/?'},
                        {'path': '/personality_id/?'},
                        {'path': '/date/?'},
                        {'path': '/conversation_count/?'},
                        {'path': '/avg_session_duration/?'},
                        {'path': '/engagement_score/?'}
                    ]
                }
            },
            
            # Personalization Insights
            {
                'name': 'personalization-insights',
                'partition_key': '/user_id',
                'max_throughput': 1000,
                'ttl': None,  # Keep insights indefinitely for learning
                'indexing_policy': {
                    'indexingMode': 'consistent',
                    'automatic': True,
                    'includedPaths': [
                        {'path': '/user_id/?'},
                        {'path': '/insight_type/?'},
                        {'path': '/personality_affinity/?'},
                        {'path': '/interaction_patterns/?'},
                        {'path': '/created_at/?'}
                    ]
                }
            }
        ]
        
        # Create containers
        created_count = 0
        skipped_count = 0
        failed_count = 0
        
        for container_config in phase2_containers:
            container = create_container_with_indexing(database, container_config)
            if container:
                if "already exists" in str(container):
                    skipped_count += 1
                else:
                    created_count += 1
            else:
                failed_count += 1
            
            print()  # Empty line for readability
        
        # Summary
        print("🎉 PHASE 2 CONTAINER CREATION COMPLETED")
        print("=" * 50)
        print(f"✅ Created: {created_count} containers")
        print(f"⚠️ Skipped (already exist): {skipped_count} containers")
        print(f"❌ Failed: {failed_count} containers")
        print(f"📊 Total processed: {len(phase2_containers)} containers")
        
        if failed_count == 0:
            print("\n🚀 All Phase 2 containers are ready!")
            print("📝 Next steps:")
            print("  1. Update database service integration")
            print("  2. Migrate in-memory services to Cosmos DB")
            print("  3. Test memory system with production containers")
        else:
            print(f"\n⚠️ {failed_count} containers failed to create.")
            print("Please review errors above before proceeding.")
        
        return failed_count == 0

    if __name__ == "__main__":
        success = main()
        if not success:
            sys.exit(1)

except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Required packages:")
    print("  pip install azure-cosmos python-dotenv")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
