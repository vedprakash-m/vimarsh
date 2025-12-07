"""
Create user_preferences Cosmos DB container
Sets up container with proper partition key and indexing policy
"""

import os
import logging
from azure.cosmos import CosmosClient, PartitionKey, exceptions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_user_preferences_container():
    """
    Create user_preferences container in Cosmos DB
    
    Container Schema:
    - id: "prefs_{user_id}" (string, unique document identifier)
    - user_id: (string, partition key)
    - experience_preferences: (object)
    - notification_preferences: (object)
    - memory_preferences: (object)
    - created_at: (ISO 8601 timestamp)
    - updated_at: (ISO 8601 timestamp)
    """
    try:
        # Get Cosmos DB credentials
        cosmos_endpoint = os.environ.get("COSMOS_ENDPOINT") or os.environ.get("COSMOS_DB_ENDPOINT")
        cosmos_key = os.environ.get("COSMOS_KEY") or os.environ.get("COSMOS_DB_KEY")
        cosmos_database = os.environ.get("COSMOS_DATABASE", "vimarsh-db")
        
        if not cosmos_endpoint or not cosmos_key:
            logger.error("❌ Cosmos DB credentials not found in environment")
            return False
        
        logger.info(f"🔗 Connecting to Cosmos DB: {cosmos_endpoint}")
        client = CosmosClient(cosmos_endpoint, cosmos_key)
        database = client.get_database_client(cosmos_database)
        
        # Container configuration
        container_name = "user_preferences"
        partition_key_path = "/user_id"
        
        # Check if container already exists
        try:
            existing_container = database.get_container_client(container_name)
            existing_container.read()
            logger.warning(f"⚠️ Container '{container_name}' already exists")
            return True
        except exceptions.CosmosResourceNotFoundError:
            pass  # Container doesn't exist, proceed with creation
        
        # Indexing policy for optimal query performance
        indexing_policy = {
            "indexingMode": "consistent",
            "automatic": True,
            "includedPaths": [
                {"path": "/*"}
            ],
            "excludedPaths": [
                {"path": '/"_etag"/?'}
            ]
        }
        
        # Create container
        logger.info(f"📦 Creating container '{container_name}' with partition key '{partition_key_path}'")
        container = database.create_container(
            id=container_name,
            partition_key=PartitionKey(path=partition_key_path),
            indexing_policy=indexing_policy,
            offer_throughput=400  # 400 RU/s for cost optimization
        )
        
        logger.info(f"✅ Container '{container_name}' created successfully")
        logger.info(f"📊 Throughput: 400 RU/s")
        logger.info(f"🔑 Partition key: {partition_key_path}")
        
        # Verify container properties
        properties = container.read()
        logger.info(f"✅ Container verification successful")
        logger.info(f"   - ID: {properties['id']}")
        logger.info(f"   - Partition Key: {properties['partitionKey']['paths']}")
        
        return True
        
    except exceptions.CosmosHttpResponseError as e:
        logger.error(f"❌ Cosmos DB error: {e.status_code} - {e.message}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error creating container: {e}")
        return False


if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("🚀 Starting user_preferences container creation")
    logger.info("=" * 80)
    
    success = create_user_preferences_container()
    
    if success:
        logger.info("=" * 80)
        logger.info("✅ Container creation completed successfully")
        logger.info("=" * 80)
    else:
        logger.info("=" * 80)
        logger.error("❌ Container creation failed")
        logger.info("=" * 80)
        exit(1)
