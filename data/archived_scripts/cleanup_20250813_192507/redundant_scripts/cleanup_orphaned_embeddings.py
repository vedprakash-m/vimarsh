#!/usr/bin/env python3
"""
Cleanup Orphaned Embeddings for Jesus Christ and Chanakya
Removes embeddings that have no associated content before fresh content upload.
"""

import os
import sys
from dotenv import load_dotenv
from azure.cosmos import CosmosClient

# Load environment variables
load_dotenv('.env')

def cleanup_orphaned_embeddings():
    """Remove orphaned embeddings for Jesus Christ and Chanakya"""
    
    print("🧹 CLEANUP ORPHANED EMBEDDINGS")
    print("=" * 50)
    
    try:
        # Connect to Cosmos DB
        connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
        if not connection_string:
            print("❌ Missing AZURE_COSMOS_CONNECTION_STRING")
            return False
            
        client = CosmosClient.from_connection_string(connection_string)
        db = client.get_database_client('vimarsh-multi-personality')
        container = db.get_container_client('personality_vectors')
        
        # SAFETY RESTRICTION: Only allow deletion for these specific personalities
        ALLOWED_PERSONALITIES = ['Jesus Christ', 'Chanakya']
        personalities_to_clean = ['Jesus Christ', 'Chanakya']
        
        # Verify we're only cleaning allowed personalities
        for personality in personalities_to_clean:
            if personality not in ALLOWED_PERSONALITIES:
                raise ValueError(f"SAFETY ERROR: {personality} not in allowed list {ALLOWED_PERSONALITIES}")
        
        print(f"🔒 SAFETY RESTRICTION: Only cleaning {ALLOWED_PERSONALITIES}")
        print(f"⚠️ NO OTHER PERSONALITIES WILL BE AFFECTED")
        print(f"🗑️ Will clean {len(personalities_to_clean)} personalities")
        
        # Additional confirmation prompt
        user_confirmation = input(f"\n⚠️ CONFIRM: Delete orphaned embeddings for {personalities_to_clean}? (yes/no): ")
        if user_confirmation.lower() not in ['yes', 'y']:
            print("❌ Operation cancelled by user")
            return False
        
        personalities_to_clean = ['Jesus Christ', 'Chanakya']
        
        for personality in personalities_to_clean:
            print(f"\n🎯 CLEANING {personality.upper()}:")
            
            # First, count what we're about to delete
            count_query = f'''
            SELECT VALUE COUNT(1) FROM c 
            WHERE c.personality_id = "{personality}" 
            AND IS_DEFINED(c.embedding) AND c.embedding != null
            AND (NOT IS_DEFINED(c.content) OR LENGTH(c.content) = 0)
            AND (NOT IS_DEFINED(c.chunk_text) OR LENGTH(c.chunk_text) = 0)
            '''
            
            orphaned_count = list(container.query_items(count_query, enable_cross_partition_query=True))[0]
            print(f"  📊 Orphaned embeddings found: {orphaned_count:,}")
            
            if orphaned_count == 0:
                print(f"  ✅ No orphaned embeddings found for {personality}")
                continue
            
            # Get all orphaned documents to delete
            orphaned_query = f'''
            SELECT c.id, c.personality_id FROM c 
            WHERE c.personality_id = "{personality}" 
            AND IS_DEFINED(c.embedding) AND c.embedding != null
            AND (NOT IS_DEFINED(c.content) OR LENGTH(c.content) = 0)
            AND (NOT IS_DEFINED(c.chunk_text) OR LENGTH(c.chunk_text) = 0)
            '''
            
            orphaned_docs = list(container.query_items(orphaned_query, enable_cross_partition_query=True))
            
            # Delete orphaned documents
            deleted_count = 0
            failed_count = 0
            
            for doc in orphaned_docs:
                try:
                    # FINAL SAFETY CHECK: Verify personality_id before deletion
                    if doc['personality_id'] not in ALLOWED_PERSONALITIES:
                        print(f"    🚨 SAFETY ABORT: Attempted to delete from {doc['personality_id']} - NOT ALLOWED!")
                        failed_count += 1
                        continue
                    
                    container.delete_item(
                        item=doc['id'],
                        partition_key=doc['personality_id']
                    )
                    deleted_count += 1
                    
                    if deleted_count % 100 == 0:
                        print(f"    🗑️ Deleted {deleted_count}/{orphaned_count} documents...")
                        
                except Exception as e:
                    failed_count += 1
                    if failed_count <= 5:  # Only show first 5 errors
                        print(f"    ⚠️ Failed to delete {doc['id']}: {e}")
            
            print(f"  ✅ Cleanup complete for {personality}:")
            print(f"    • Deleted: {deleted_count:,} orphaned embeddings")
            if failed_count > 0:
                print(f"    • Failed: {failed_count:,} deletions")
        
        # Final verification
        print(f"\n🔍 POST-CLEANUP VERIFICATION:")
        for personality in personalities_to_clean:
            remaining_query = f'''
            SELECT VALUE COUNT(1) FROM c 
            WHERE c.personality_id = "{personality}"
            '''
            remaining_docs = list(container.query_items(remaining_query, enable_cross_partition_query=True))[0]
            print(f"  {personality}: {remaining_docs:,} documents remaining")
        
        print(f"\n🎉 CLEANUP COMPLETED SUCCESSFULLY!")
        print(f"Ready for fresh content upload for Jesus Christ and Chanakya.")
        return True
        
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        return False

if __name__ == "__main__":
    success = cleanup_orphaned_embeddings()
    sys.exit(0 if success else 1)
