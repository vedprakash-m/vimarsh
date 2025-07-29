"""
Container Migration Checker - Fixes container naming issues
Checks current containers and migrates data to correct container structure.
"""

import os
import sys
import logging
from typing import List, Dict, Any
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from azure.cosmos import CosmosClient, exceptions

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContainerMigrationChecker:
    """Checks and fixes Cosmos DB container naming issues"""
    
    def __init__(self):
        self.connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING') or os.getenv('COSMOSDB_CONNECTION_STRING')
        if not self.connection_string:
            raise ValueError("❌ No Cosmos DB connection string found in environment variables")
        
        self.client = CosmosClient.from_connection_string(self.connection_string)
        logger.info("✅ Connected to Cosmos DB")
    
    def list_all_databases(self) -> List[Dict[str, Any]]:
        """List all databases in the Cosmos account"""
        try:
            databases = list(self.client.list_databases())
            logger.info(f"📊 Found {len(databases)} databases:")
            for db in databases:
                logger.info(f"  - {db['id']}")
            return databases
        except Exception as e:
            logger.error(f"❌ Error listing databases: {str(e)}")
            return []
    
    def list_containers_in_database(self, database_name: str) -> List[Dict[str, Any]]:
        """List all containers in a specific database"""
        try:
            database = self.client.get_database_client(database_name)
            containers = list(database.list_containers())
            logger.info(f"📦 Containers in '{database_name}':")
            for container in containers:
                logger.info(f"  - {container['id']}")
            return containers
        except exceptions.CosmosResourceNotFoundError:
            logger.warning(f"⚠️ Database '{database_name}' not found")
            return []
        except Exception as e:
            logger.error(f"❌ Error listing containers in '{database_name}': {str(e)}")
            return []
    
    def check_container_contents(self, database_name: str, container_name: str) -> Dict[str, Any]:
        """Check contents of a specific container"""
        try:
            database = self.client.get_database_client(database_name)
            container = database.get_container_client(container_name)
            
            # Count documents
            query = "SELECT VALUE COUNT(1) FROM c"
            count_result = list(container.query_items(query=query, enable_cross_partition_query=True))
            total_count = count_result[0] if count_result else 0
            
            # Sample documents
            sample_query = "SELECT TOP 3 c.id, c.personality, c.source, c.content_type FROM c"
            sample_docs = list(container.query_items(query=sample_query, enable_cross_partition_query=True))
            
            logger.info(f"📄 Container '{container_name}' in '{database_name}':")
            logger.info(f"  - Total documents: {total_count}")
            logger.info(f"  - Sample documents:")
            for doc in sample_docs:
                personality = doc.get('personality', 'N/A')
                source = doc.get('source', 'N/A')
                content_type = doc.get('content_type', 'N/A')
                logger.info(f"    • ID: {doc['id']} | Personality: {personality} | Source: {source} | Type: {content_type}")
            
            return {
                'total_count': total_count,
                'sample_docs': sample_docs,
                'exists': True
            }
            
        except exceptions.CosmosResourceNotFoundError:
            logger.warning(f"⚠️ Container '{container_name}' not found in '{database_name}'")
            return {'exists': False, 'total_count': 0}
        except Exception as e:
            logger.error(f"❌ Error checking container '{container_name}': {str(e)}")
            return {'exists': False, 'total_count': 0, 'error': str(e)}
    
    def migrate_container_data(self, source_db: str, source_container: str, 
                              target_db: str, target_container: str) -> bool:
        """Migrate data from one container to another"""
        try:
            logger.info(f"🚀 Starting migration from {source_db}.{source_container} to {target_db}.{target_container}")
            
            # Get source container
            source_database = self.client.get_database_client(source_db)
            source_cont = source_database.get_container_client(source_container)
            
            # Create target database and container if needed
            target_database = self.client.create_database_if_not_exists(target_db)
            
            # Create target container with proper configuration
            container_definition = {
                'id': target_container,
                'partitionKey': {'paths': ['/personality'], 'kind': 'Hash'},
                'vectorEmbeddingPolicy': {
                    'vectorEmbeddings': [
                        {
                            'path': '/embedding',
                            'dataType': 'float32',
                            'dimensions': 768,
                            'distanceFunction': 'cosine'
                        }
                    ]
                }
            }
            
            target_cont = target_database.create_container_if_not_exists(
                id=target_container,
                partition_key={'paths': ['/personality'], 'kind': 'Hash'}
                # No offer_throughput for serverless accounts
            )
            
            # Query all documents from source
            all_docs_query = "SELECT * FROM c"
            all_docs = list(source_cont.query_items(query=all_docs_query, enable_cross_partition_query=True))
            
            logger.info(f"📊 Found {len(all_docs)} documents to migrate")
            
            # Migrate documents
            migrated_count = 0
            for doc in all_docs:
                try:
                    # Ensure personality field exists for partitioning
                    if 'personality' not in doc:
                        doc['personality'] = 'krishna'  # Default for existing Krishna content
                    
                    target_cont.create_item(body=doc)
                    migrated_count += 1
                    
                    if migrated_count % 10 == 0:
                        logger.info(f"✅ Migrated {migrated_count}/{len(all_docs)} documents")
                        
                except Exception as e:
                    logger.error(f"❌ Failed to migrate document {doc.get('id', 'unknown')}: {str(e)}")
            
            logger.info(f"🎉 Migration complete! Migrated {migrated_count}/{len(all_docs)} documents")
            return True
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {str(e)}")
            return False
    
    def run_complete_check(self):
        """Run complete check of container situation"""
        logger.info("🔍 Starting complete container check...")
        
        # 1. List all databases
        databases = self.list_all_databases()
        
        # 2. Check for relevant databases
        relevant_dbs = ['vimarsh-db', 'vimarsh-multi-personality']
        
        container_status = {}
        
        for db_name in relevant_dbs:
            if any(db['id'] == db_name for db in databases):
                containers = self.list_containers_in_database(db_name)
                container_status[db_name] = {}
                
                # Check relevant containers
                relevant_containers = ['spiritual-texts', 'spiritual-vectors', 'personality-vectors']
                
                for container_name in relevant_containers:
                    if any(c['id'] == container_name for c in containers):
                        container_status[db_name][container_name] = self.check_container_contents(db_name, container_name)
                    else:
                        container_status[db_name][container_name] = {'exists': False, 'total_count': 0}
            else:
                logger.warning(f"⚠️ Database '{db_name}' not found")
                container_status[db_name] = {}
        
        # 3. Analyze situation and recommend action
        self.analyze_and_recommend(container_status)
        
        return container_status
    
    def analyze_and_recommend(self, container_status: Dict[str, Any]):
        """Analyze container status and recommend actions"""
        logger.info("\n" + "="*60)
        logger.info("📊 CONTAINER STATUS ANALYSIS")
        logger.info("="*60)
        
        # Check if data exists in wrong container
        old_container_data = 0
        new_container_data = 0
        
        if 'vimarsh-multi-personality' in container_status:
            if 'spiritual-vectors' in container_status['vimarsh-multi-personality']:
                old_container_data = container_status['vimarsh-multi-personality']['spiritual-vectors'].get('total_count', 0)
            
            if 'personality-vectors' in container_status['vimarsh-multi-personality']:
                new_container_data = container_status['vimarsh-multi-personality']['personality-vectors'].get('total_count', 0)
        
        logger.info(f"📊 Data distribution:")
        logger.info(f"  - spiritual-vectors (old): {old_container_data} documents")
        logger.info(f"  - personality-vectors (new): {new_container_data} documents")
        
        if old_container_data > 0 and new_container_data == 0:
            logger.info("🔧 RECOMMENDATION: Migrate data from spiritual-vectors to personality-vectors")
            response = input("\nDo you want to migrate the data now? (y/n): ")
            if response.lower() == 'y':
                success = self.migrate_container_data(
                    'vimarsh-multi-personality', 'spiritual-vectors',
                    'vimarsh-multi-personality', 'personality-vectors'
                )
                if success:
                    logger.info("✅ Migration completed successfully!")
                else:
                    logger.error("❌ Migration failed!")
        
        elif new_container_data > 0:
            logger.info("✅ Data is correctly in personality-vectors container")
        
        else:
            logger.warning("⚠️ No data found in either container!")
        
        logger.info("="*60)

def main():
    """Main function"""
    try:
        checker = ContainerMigrationChecker()
        checker.run_complete_check()
        
    except Exception as e:
        logger.error(f"❌ Fatal error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
