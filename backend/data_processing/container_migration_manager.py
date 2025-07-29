"""
Container Migration & Verification Script for Vimarsh Multi-Personality Database
Helps resolve container naming issues and ensures proper migration to personality-vectors.
"""

import os
import asyncio
import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class ContainerMigrationManager:
    """Manages container migration and verification for the multi-personality system"""
    
    def __init__(self):
        self.cosmos_client = None
        self.database = None
        self.old_container = None  # spiritual-vectors
        self.new_container = None  # personality-vectors
        self.migration_stats = {
            'documents_found': 0,
            'documents_migrated': 0,
            'migration_errors': 0
        }
        
        self._initialize_cosmos_db()
    
    def _initialize_cosmos_db(self):
        """Initialize Cosmos DB connections"""
        try:
            from azure.cosmos import CosmosClient
            
            connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
            if not connection_string:
                logger.error("❌ AZURE_COSMOS_CONNECTION_STRING not found in environment")
                return
            
            self.cosmos_client = CosmosClient.from_connection_string(connection_string)
            
            # Database name
            database_name = os.getenv('AZURE_COSMOS_DATABASE_NAME', 'vimarsh-multi-personality')
            self.database = self.cosmos_client.get_database_client(database_name)
            
            logger.info(f"✅ Connected to database: {database_name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Cosmos DB: {str(e)}")
    
    async def check_container_status(self) -> Dict[str, Any]:
        """Check the current status of containers in the database"""
        try:
            containers = list(self.database.list_containers())
            container_info = {}
            
            for container in containers:
                container_name = container['id']
                container_client = self.database.get_container_client(container_name)
                
                # Count documents
                try:
                    doc_count = 0
                    for item in container_client.query_items(
                        query="SELECT VALUE COUNT(1) FROM c",
                        enable_cross_partition_query=True
                    ):
                        doc_count = item
                        break
                    
                    # Get sample document to understand structure
                    sample_doc = None
                    for item in container_client.query_items(
                        query="SELECT TOP 1 * FROM c",
                        enable_cross_partition_query=True
                    ):
                        sample_doc = item
                        break
                    
                    container_info[container_name] = {
                        'document_count': doc_count,
                        'has_personality_field': sample_doc and 'personality' in sample_doc if sample_doc else False,
                        'has_embedding_field': sample_doc and 'embedding' in sample_doc if sample_doc else False,
                        'sample_id': sample_doc.get('id') if sample_doc else None,
                        'partition_key': container['partitionKey']['paths'][0] if 'partitionKey' in container else None
                    }
                    
                except Exception as e:
                    container_info[container_name] = {
                        'error': str(e),
                        'document_count': 0
                    }
            
            return {
                'database_name': self.database.id,
                'containers': container_info,
                'total_containers': len(containers),
                'recommended_action': self._get_migration_recommendation(container_info)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to check container status: {str(e)}")
            return {'error': str(e)}
    
    def _get_migration_recommendation(self, container_info: Dict[str, Any]) -> str:
        """Analyze container info and recommend migration strategy"""
        has_spiritual_vectors = 'spiritual-vectors' in container_info
        has_personality_vectors = 'personality-vectors' in container_info
        
        spiritual_count = container_info.get('spiritual-vectors', {}).get('document_count', 0)
        personality_count = container_info.get('personality-vectors', {}).get('document_count', 0)
        
        if has_spiritual_vectors and spiritual_count > 0:
            if has_personality_vectors and personality_count > 0:
                return f"BOTH_EXIST: spiritual-vectors ({spiritual_count} docs) and personality-vectors ({personality_count} docs). Recommend consolidation."
            else:
                return f"MIGRATE_NEEDED: spiritual-vectors has {spiritual_count} documents. Need to migrate/rename to personality-vectors."
        elif has_personality_vectors and personality_count > 0:
            return f"MIGRATION_COMPLETE: personality-vectors has {personality_count} documents. Ready to use."
        else:
            return "NO_DATA: No vector containers found with data. Need to populate."
    
    async def migrate_container_data(self, from_container: str = 'spiritual-vectors', to_container: str = 'personality-vectors'):
        """Migrate data from old container to new container with enhanced metadata"""
        try:
            # Get source and destination containers
            source_container = self.database.get_container_client(from_container)
            
            # Create destination container if it doesn't exist
            try:
                dest_container = self.database.get_container_client(to_container)
            except Exception as e:
                logger.info(f"Creating new container: {to_container} (Error: {str(e)})")
                container_definition = {
                    'id': to_container,
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
                dest_container = self.database.create_container(container_definition)
            
            # Migrate documents
            logger.info(f"🚀 Starting migration from {from_container} to {to_container}")
            
            for item in source_container.query_items(
                query="SELECT * FROM c",
                enable_cross_partition_query=True
            ):
                try:
                    # Enhance document with proper structure
                    enhanced_doc = self._enhance_document_metadata(item)
                    
                    # Insert into new container
                    dest_container.create_item(enhanced_doc)
                    self.migration_stats['documents_migrated'] += 1
                    
                    if self.migration_stats['documents_migrated'] % 100 == 0:
                        logger.info(f"✅ Migrated {self.migration_stats['documents_migrated']} documents")
                
                except Exception as e:
                    logger.error(f"❌ Failed to migrate document {item.get('id', 'unknown')}: {str(e)}")
                    self.migration_stats['migration_errors'] += 1
                
                self.migration_stats['documents_found'] += 1
            
            logger.info(f"🎉 Migration complete: {self.migration_stats}")
            return self.migration_stats
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {str(e)}")
            return {'error': str(e)}
    
    def _enhance_document_metadata(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance existing document with proper metadata structure"""
        enhanced = doc.copy()
        
        # Ensure personality field exists (default to krishna for existing data)
        if 'personality' not in enhanced:
            # Try to infer personality from source or content
            source = doc.get('source', '').lower()
            if 'gita' in source or 'bhagavad' in source:
                enhanced['personality'] = 'krishna'
            elif 'isopanishad' in source or 'upanishad' in source:
                enhanced['personality'] = 'krishna'
            else:
                enhanced['personality'] = 'krishna'  # Default for existing data
        
        # Ensure content_type exists
        if 'content_type' not in enhanced:
            if doc.get('verse'):
                enhanced['content_type'] = 'verse'
            else:
                enhanced['content_type'] = 'teaching'
        
        # Ensure proper metadata structure
        if 'metadata' not in enhanced:
            enhanced['metadata'] = {}
        
        # Add migration metadata
        enhanced['metadata'].update({
            'migrated_from': 'spiritual-vectors',
            'migration_date': datetime.utcnow().isoformat(),
            'migration_version': '1.0',
            'original_container': 'spiritual-vectors'
        })
        
        # Ensure category exists
        if 'category' not in enhanced:
            enhanced['category'] = 'spiritual'
        
        # Ensure timestamps
        if 'created_at' not in enhanced:
            enhanced['created_at'] = datetime.utcnow().isoformat()
        
        enhanced['updated_at'] = datetime.utcnow().isoformat()
        
        return enhanced
    
    async def verify_migration(self, container_name: str = 'personality-vectors') -> Dict[str, Any]:
        """Verify the migration was successful"""
        try:
            container = self.database.get_container_client(container_name)
            
            # Count total documents
            total_docs = 0
            for item in container.query_items(
                query="SELECT VALUE COUNT(1) FROM c",
                enable_cross_partition_query=True
            ):
                total_docs = item
                break
            
            # Count by personality
            personality_counts = {}
            for item in container.query_items(
                query="SELECT c.personality, COUNT(1) as count FROM c GROUP BY c.personality",
                enable_cross_partition_query=True
            ):
                personality_counts[item['personality']] = item['count']
            
            # Check data quality
            sample_docs = list(container.query_items(
                query="SELECT TOP 5 * FROM c",
                enable_cross_partition_query=True
            ))
            
            required_fields = ['id', 'content', 'personality', 'embedding']
            quality_check = {
                'has_all_required_fields': all(
                    all(field in doc for field in required_fields) 
                    for doc in sample_docs
                ),
                'sample_personalities': [doc.get('personality') for doc in sample_docs],
                'sample_sources': [doc.get('source') for doc in sample_docs]
            }
            
            return {
                'container_name': container_name,
                'total_documents': total_docs,
                'personality_distribution': personality_counts,
                'quality_check': quality_check,
                'migration_status': 'SUCCESS' if total_docs > 0 else 'NO_DATA'
            }
            
        except Exception as e:
            return {
                'container_name': container_name,
                'error': str(e),
                'migration_status': 'FAILED'
            }
    
    def generate_migration_report(self, status_info: Dict[str, Any]) -> str:
        """Generate a human-readable migration report"""
        report = []
        report.append("=" * 60)
        report.append("🔍 VIMARSH CONTAINER MIGRATION REPORT")
        report.append("=" * 60)
        
        if 'error' in status_info:
            report.append(f"❌ ERROR: {status_info['error']}")
            return "\n".join(report)
        
        report.append(f"Database: {status_info.get('database_name', 'Unknown')}")
        report.append(f"Total Containers: {status_info.get('total_containers', 0)}")
        report.append("")
        
        containers = status_info.get('containers', {})
        for container_name, info in containers.items():
            report.append(f"📦 Container: {container_name}")
            if 'error' in info:
                report.append(f"   ❌ Error: {info['error']}")
            else:
                report.append(f"   📊 Documents: {info.get('document_count', 0)}")
                report.append(f"   🔑 Partition Key: {info.get('partition_key', 'Unknown')}")
                report.append(f"   👤 Has Personality Field: {info.get('has_personality_field', False)}")
                report.append(f"   🧠 Has Embedding Field: {info.get('has_embedding_field', False)}")
                if info.get('sample_id'):
                    report.append(f"   📄 Sample ID: {info['sample_id']}")
            report.append("")
        
        report.append("🎯 RECOMMENDATION:")
        report.append(f"   {status_info.get('recommended_action', 'No specific action needed')}")
        report.append("=" * 60)
        
        return "\n".join(report)

# Usage functions
async def check_current_status():
    """Check current container status"""
    manager = ContainerMigrationManager()
    status = await manager.check_container_status()
    report = manager.generate_migration_report(status)
    print(report)
    return status

async def migrate_if_needed():
    """Migrate data if needed"""
    manager = ContainerMigrationManager()
    
    # Check status first
    status = await manager.check_container_status()
    containers = status.get('containers', {})
    
    spiritual_count = containers.get('spiritual-vectors', {}).get('document_count', 0)
    personality_count = containers.get('personality-vectors', {}).get('document_count', 0)
    
    if spiritual_count > 0 and personality_count == 0:
        print("🚀 Migration needed. Starting migration...")
        result = await manager.migrate_container_data()
        print(f"✅ Migration result: {result}")
        
        # Verify migration
        verification = await manager.verify_migration()
        print(f"🔍 Verification result: {verification}")
        
    elif personality_count > 0:
        print("✅ personality-vectors container already has data. Migration complete.")
        verification = await manager.verify_migration()
        print(f"🔍 Current status: {verification}")
    else:
        print("⚠️ No data found in either container.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("Checking current container status...")
    asyncio.run(check_current_status())
    
    print("\nRunning migration if needed...")
    asyncio.run(migrate_if_needed())
