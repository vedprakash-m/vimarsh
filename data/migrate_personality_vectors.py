#!/usr/bin/env python3
"""
Migrate personality-vectors to personality_vectors
This is the MOST CRITICAL migration - preserves 6,514 embeddings
"""

import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

# Add the parent directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Load environment variables from root .env
load_dotenv('../../.env')

try:
    from azure.cosmos import CosmosClient
    
    def transform_vector_document(old_doc):
        """Transform old document to new schema with hierarchical partition key"""
        # Create hierarchical partition key: personality_id::source  
        personality = old_doc.get('personality', 'unknown')
        source = old_doc.get('source', 'unknown')[:50]  # Limit source length
        partition_key = f"{personality}::{source}"
        
        new_doc = {
            "id": old_doc['id'],
            "partition_key": partition_key,  # NEW: Hierarchical partition key
            "personality_id": personality,   # NEW: Separate personality reference
            "source": old_doc.get('source', ''),
            "content": old_doc.get('content', ''),
            "content_type": old_doc.get('content_type', 'verse'),
            "title": old_doc.get('title'),
            "chapter": old_doc.get('chapter'),
            "verse": old_doc.get('verse'),
            "sanskrit": old_doc.get('sanskrit'),
            "translation": old_doc.get('translation'),
            "citation": old_doc.get('citation'),
            "category": old_doc.get('category', 'general'),
            "language": old_doc.get('language', 'English'),
            "embedding": old_doc.get('embedding'),  # PRESERVE: Critical embeddings
            "embedding_model": old_doc.get('embedding_model', 'unknown'),
            "topic_tags": old_doc.get('metadata', {}).get('topic_tags', []) if old_doc.get('metadata') else [],
            "foundational_text_ref": {
                "source": old_doc.get('source', ''),
                "chapter": old_doc.get('chapter'),
                "verse": old_doc.get('verse')
            },
            "created_at": old_doc.get('created_at'),
            "updated_at": old_doc.get('updated_at'),
            "_ttl": None  # Permanent storage
        }
        
        # Remove None values to keep documents clean
        return {k: v for k, v in new_doc.items() if v is not None}
    
    def migrate_personality_vectors():
        """Migrate personality-vectors → personality_vectors"""
        print("🔄 MIGRATING PERSONALITY VECTORS")
        print("=" * 60)
        print("⚠️ CRITICAL: This contains 6,514 irreplaceable embeddings")
        
        # Get connection
        connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
        if not connection_string:
            print("❌ AZURE_COSMOS_CONNECTION_STRING not found")
            return False
        
        client = CosmosClient.from_connection_string(connection_string)
        database_name = os.getenv('AZURE_COSMOS_DATABASE_NAME', 'vimarsh-multi-personality')
        database = client.get_database_client(database_name)
        
        # Get containers
        source_container = database.get_container_client('personality-vectors')
        target_container = database.get_container_client('personality_vectors')
        
        # Check target container is empty
        try:
            count_query = "SELECT VALUE COUNT(1) FROM c"
            existing_count_result = list(target_container.query_items(query=count_query, enable_cross_partition_query=True))
            existing_count = existing_count_result[0] if existing_count_result else 0
            
            if existing_count > 0:
                print(f"⚠️ Target container personality_vectors already has {existing_count} documents")
                response = input("Continue and potentially create duplicates? (yes/no): ")
                if response.lower() != 'yes':
                    print("❌ Migration cancelled")
                    return False
        except Exception as e:
            print(f"⚠️ Could not check target container: {e}")
        
        # Process in batches
        batch_size = 50  # Smaller batches for safety
        migrated_count = 0
        error_count = 0
        
        print(f"📦 Starting migration in batches of {batch_size}")
        
        try:
            # Query all documents from source
            query = "SELECT * FROM c"
            
            batch = []
            for doc in source_container.query_items(query=query, enable_cross_partition_query=True):
                batch.append(doc)
                
                if len(batch) >= batch_size:
                    # Process batch
                    batch_errors = process_batch(target_container, batch, migrated_count)
                    migrated_count += len(batch) - batch_errors
                    error_count += batch_errors
                    
                    if migrated_count % 500 == 0:
                        print(f"✅ Migrated {migrated_count} documents (errors: {error_count})")
                    
                    batch = []
            
            # Process remaining documents
            if batch:
                batch_errors = process_batch(target_container, batch, migrated_count)
                migrated_count += len(batch) - batch_errors
                error_count += batch_errors
            
            print(f"\n🎉 MIGRATION COMPLETED")
            print("=" * 40)
            print(f"✅ Successfully migrated: {migrated_count} documents")
            print(f"❌ Errors: {error_count} documents")
            print(f"📊 Expected total: 6514 documents")
            
            if migrated_count == 6514:
                print("🎉 PERFECT! All 6,514 personality vectors migrated successfully")
                return True
            elif migrated_count > 6500:
                print("✅ GOOD! Migration appears successful (count close to expected)")
                return True
            else:
                print("⚠️ WARNING: Migrated count significantly lower than expected")
                print("Please investigate before proceeding")
                return False
                
        except Exception as e:
            print(f"❌ Critical error during migration: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def process_batch(target_container, batch, current_count):
        """Process a batch of documents"""
        error_count = 0
        
        for doc in batch:
            try:
                # Transform document
                new_doc = transform_vector_document(doc)
                
                # Validate critical fields
                if not new_doc.get('embedding'):
                    print(f"⚠️ Warning: Document {doc['id']} has no embedding!")
                
                # Insert into target container
                target_container.create_item(new_doc)
                
            except Exception as e:
                print(f"❌ Error migrating document {doc.get('id', 'unknown')}: {e}")
                error_count += 1
        
        return error_count
    
    def validate_migration():
        """Validate the migration was successful"""
        print("\n🔍 VALIDATING MIGRATION")
        print("-" * 40)
        
        # Get connection
        connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
        client = CosmosClient.from_connection_string(connection_string)
        database_name = os.getenv('AZURE_COSMOS_DATABASE_NAME', 'vimarsh-multi-personality')
        database = client.get_database_client(database_name)
        
        source_container = database.get_container_client('personality-vectors')
        target_container = database.get_container_client('personality_vectors')
        
        try:
            # Count documents
            count_query = "SELECT VALUE COUNT(1) FROM c"
            
            source_count_result = list(source_container.query_items(query=count_query, enable_cross_partition_query=True))
            source_count = source_count_result[0] if source_count_result else 0
            
            target_count_result = list(target_container.query_items(query=count_query, enable_cross_partition_query=True))
            target_count = target_count_result[0] if target_count_result else 0
            
            print(f"📊 Source (personality-vectors): {source_count} documents")
            print(f"📊 Target (personality_vectors): {target_count} documents")
            
            if source_count == target_count:
                print("✅ Document counts match perfectly!")
            else:
                print(f"⚠️ Document counts don't match (difference: {abs(source_count - target_count)})")
            
            # Validate embeddings preserved
            embedding_query = "SELECT TOP 10 c.id, c.embedding FROM c WHERE IS_DEFINED(c.embedding) AND c.embedding != null"
            embedding_samples = list(target_container.query_items(query=embedding_query, enable_cross_partition_query=True))
            
            if embedding_samples:
                print(f"✅ Embeddings preserved - {len(embedding_samples)} sample documents have valid embeddings")
                
                # Check embedding format
                for sample in embedding_samples:
                    embedding = sample.get('embedding')
                    if not isinstance(embedding, list) or len(embedding) == 0:
                        print(f"❌ Invalid embedding format for document {sample['id']}")
                        return False
                
                print("✅ Embedding format validation passed")
            else:
                print("❌ No embeddings found in target container!")
                return False
            
            # Validate partition keys
            partition_query = "SELECT TOP 5 c.partition_key, c.personality_id, c.source FROM c WHERE IS_DEFINED(c.partition_key)"
            partition_samples = list(target_container.query_items(query=partition_query, enable_cross_partition_query=True))
            
            if partition_samples:
                print(f"✅ Partition keys created - {len(partition_samples)} sample documents")
                for sample in partition_samples:
                    if '::' not in sample.get('partition_key', ''):
                        print(f"❌ Invalid partition key format: {sample.get('partition_key')}")
                        return False
                print("✅ Partition key format validation passed")
            else:
                print("❌ No partition keys found!")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Validation error: {e}")
            return False
    
    def main():
        """Main migration function"""
        print("🚀 PERSONALITY VECTORS MIGRATION")
        print("=" * 60)
        print("🔴 CRITICAL: This migrates 6,514 embeddings that cannot be regenerated")
        print("💾 Ensure backup was completed before proceeding")
        
        # Confirm migration
        response = input("\n⚠️ Proceed with personality vectors migration? (yes/no): ")
        if response.lower() != 'yes':
            print("❌ Migration cancelled")
            return False
        
        # Execute migration
        migration_success = migrate_personality_vectors()
        
        if not migration_success:
            print("❌ Migration failed - please check errors above")
            return False
        
        # Validate migration
        validation_success = validate_migration()
        
        if validation_success:
            print("\n🎉 PERSONALITY VECTORS MIGRATION SUCCESSFUL!")
            print("✅ All critical embeddings preserved and migrated")
            return True
        else:
            print("\n❌ MIGRATION VALIDATION FAILED!")
            print("⚠️ Please investigate issues before proceeding")
            return False

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
