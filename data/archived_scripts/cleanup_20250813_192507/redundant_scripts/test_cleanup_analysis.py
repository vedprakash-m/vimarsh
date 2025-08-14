#!/usr/bin/env python3
"""
TEST SCRIPT: Analyze Orphaned Embeddings for Jesus Christ and Chanakya
Performs detailed analysis of what would be deleted WITHOUT actually deleting anything.
Use this to verify the cleanup script logic before running the real cleanup.
"""

import os
import sys
from dotenv import load_dotenv
from azure.cosmos import CosmosClient

# Load environment variables
load_dotenv('.env')

def analyze_orphaned_embeddings():
    """Analyze orphaned embeddings without deleting anything"""
    
    print("🔍 ANALYZING ORPHANED EMBEDDINGS (NO DELETION)")
    print("=" * 60)
    
    try:
        # Connect to Cosmos DB
        connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
        if not connection_string:
            print("❌ Missing AZURE_COSMOS_CONNECTION_STRING")
            return False
            
        client = CosmosClient.from_connection_string(connection_string)
        db = client.get_database_client('vimarsh-multi-personality')
        container = db.get_container_client('personality_vectors')
        
        # SAFETY RESTRICTION: Only allow analysis of these specific personalities
        ALLOWED_PERSONALITIES = ['Jesus Christ', 'Chanakya']
        personalities_to_analyze = ['Jesus Christ', 'Chanakya']
        
        # Verify we're only analyzing allowed personalities
        for personality in personalities_to_analyze:
            if personality not in ALLOWED_PERSONALITIES:
                raise ValueError(f"SAFETY ERROR: {personality} not in allowed list {ALLOWED_PERSONALITIES}")
        
        print(f"🔒 SAFETY RESTRICTION: Only analyzing {ALLOWED_PERSONALITIES}")
        print(f"📊 Analyzing {len(personalities_to_analyze)} personalities")
        
        for personality in personalities_to_analyze:
            print(f"\n📊 ANALYZING {personality.upper()}:")
            print("-" * 40)
            
            # Total documents for this personality
            total_query = f'SELECT VALUE COUNT(1) FROM c WHERE c.personality_id = "{personality}"'
            total_docs = list(container.query_items(total_query, enable_cross_partition_query=True))[0]
            
            # Documents with embeddings
            embedding_query = f'''
            SELECT VALUE COUNT(1) FROM c 
            WHERE c.personality_id = "{personality}" 
            AND IS_DEFINED(c.embedding) AND c.embedding != null
            '''
            docs_with_embeddings = list(container.query_items(embedding_query, enable_cross_partition_query=True))[0]
            
            # Documents with content field
            content_query = f'''
            SELECT VALUE COUNT(1) FROM c 
            WHERE c.personality_id = "{personality}" 
            AND IS_DEFINED(c.content) AND LENGTH(c.content) > 0
            '''
            docs_with_content = list(container.query_items(content_query, enable_cross_partition_query=True))[0]
            
            # Documents with chunk_text field
            chunk_text_query = f'''
            SELECT VALUE COUNT(1) FROM c 
            WHERE c.personality_id = "{personality}" 
            AND IS_DEFINED(c.chunk_text) AND LENGTH(c.chunk_text) > 0
            '''
            docs_with_chunk_text = list(container.query_items(chunk_text_query, enable_cross_partition_query=True))[0]
            
            # ORPHANED: Embeddings with NO content AND NO chunk_text
            orphaned_query = f'''
            SELECT VALUE COUNT(1) FROM c 
            WHERE c.personality_id = "{personality}" 
            AND IS_DEFINED(c.embedding) AND c.embedding != null
            AND (NOT IS_DEFINED(c.content) OR LENGTH(c.content) = 0)
            AND (NOT IS_DEFINED(c.chunk_text) OR LENGTH(c.chunk_text) = 0)
            '''
            orphaned_count = list(container.query_items(orphaned_query, enable_cross_partition_query=True))[0]
            
            # GOOD DATA: Embeddings with content OR chunk_text
            good_data_query = f'''
            SELECT VALUE COUNT(1) FROM c 
            WHERE c.personality_id = "{personality}" 
            AND IS_DEFINED(c.embedding) AND c.embedding != null
            AND ((IS_DEFINED(c.content) AND LENGTH(c.content) > 0) OR 
                 (IS_DEFINED(c.chunk_text) AND LENGTH(c.chunk_text) > 0))
            '''
            good_data_count = list(container.query_items(good_data_query, enable_cross_partition_query=True))[0]
            
            print(f"  📈 Total Documents: {total_docs:,}")
            print(f"  🔗 With Embeddings: {docs_with_embeddings:,}")
            print(f"  📄 With Content Field: {docs_with_content:,}")
            print(f"  📝 With Chunk_Text Field: {docs_with_chunk_text:,}")
            print(f"  ✅ GOOD DATA (embeddings + text): {good_data_count:,}")
            print(f"  ⚠️ ORPHANED (embeddings only): {orphaned_count:,}")
            
            # Safety check
            if good_data_count > 0:
                print(f"  🚨 WARNING: {good_data_count:,} documents have good data!")
                print(f"     These should NOT be deleted!")
            
            # Show sample documents to verify logic
            print(f"\n  🔍 SAMPLE DOCUMENTS FOR VERIFICATION:")
            
            # Sample of what WOULD BE DELETED (orphaned)
            orphaned_sample_query = f'''
            SELECT TOP 3 c.id, c.personality_id, 
                   IS_DEFINED(c.embedding) as has_embedding,
                   LENGTH(c.content) as content_length,
                   LENGTH(c.chunk_text) as chunk_text_length,
                   c.source
            FROM c 
            WHERE c.personality_id = "{personality}" 
            AND IS_DEFINED(c.embedding) AND c.embedding != null
            AND (NOT IS_DEFINED(c.content) OR LENGTH(c.content) = 0)
            AND (NOT IS_DEFINED(c.chunk_text) OR LENGTH(c.chunk_text) = 0)
            '''
            
            orphaned_samples = list(container.query_items(orphaned_sample_query, enable_cross_partition_query=True))
            
            if orphaned_samples:
                print(f"    🗑️ WOULD DELETE (sample of {len(orphaned_samples)}):")
                for sample in orphaned_samples:
                    print(f"      • ID: {sample['id']}")
                    print(f"        Embedding: {sample.get('has_embedding', False)}")
                    print(f"        Content: {sample.get('content_length', 0)} chars")
                    print(f"        Chunk_text: {sample.get('chunk_text_length', 0)} chars")
                    print(f"        Source: {sample.get('source', 'N/A')}")
            else:
                print(f"    ✅ No orphaned documents found - nothing to delete!")
            
            # Sample of what WOULD BE KEPT (good data)
            good_sample_query = f'''
            SELECT TOP 3 c.id, c.personality_id, 
                   IS_DEFINED(c.embedding) as has_embedding,
                   LENGTH(c.content) as content_length,
                   LENGTH(c.chunk_text) as chunk_text_length,
                   c.source
            FROM c 
            WHERE c.personality_id = "{personality}" 
            AND IS_DEFINED(c.embedding) AND c.embedding != null
            AND ((IS_DEFINED(c.content) AND LENGTH(c.content) > 0) OR 
                 (IS_DEFINED(c.chunk_text) AND LENGTH(c.chunk_text) > 0))
            '''
            
            good_samples = list(container.query_items(good_sample_query, enable_cross_partition_query=True))
            
            if good_samples:
                print(f"    ✅ WOULD KEEP (sample of {len(good_samples)}):")
                for sample in good_samples:
                    print(f"      • ID: {sample['id']}")
                    print(f"        Embedding: {sample.get('has_embedding', False)}")
                    print(f"        Content: {sample.get('content_length', 0)} chars")
                    print(f"        Chunk_text: {sample.get('chunk_text_length', 0)} chars")
                    print(f"        Source: {sample.get('source', 'N/A')}")
        
        print(f"\n🎯 SAFETY ANALYSIS SUMMARY:")
        print("=" * 40)
        
        total_would_delete = 0
        total_would_keep = 0
        
        for personality in personalities_to_analyze:
            # Recalculate for summary
            orphaned_query = f'''
            SELECT VALUE COUNT(1) FROM c 
            WHERE c.personality_id = "{personality}" 
            AND IS_DEFINED(c.embedding) AND c.embedding != null
            AND (NOT IS_DEFINED(c.content) OR LENGTH(c.content) = 0)
            AND (NOT IS_DEFINED(c.chunk_text) OR LENGTH(c.chunk_text) = 0)
            '''
            orphaned = list(container.query_items(orphaned_query, enable_cross_partition_query=True))[0]
            
            good_query = f'''
            SELECT VALUE COUNT(1) FROM c 
            WHERE c.personality_id = "{personality}" 
            AND IS_DEFINED(c.embedding) AND c.embedding != null
            AND ((IS_DEFINED(c.content) AND LENGTH(c.content) > 0) OR 
                 (IS_DEFINED(c.chunk_text) AND LENGTH(c.chunk_text) > 0))
            '''
            good = list(container.query_items(good_query, enable_cross_partition_query=True))[0]
            
            total_would_delete += orphaned
            total_would_keep += good
            
            print(f"  {personality}:")
            print(f"    🗑️ Would delete: {orphaned:,} orphaned embeddings")
            print(f"    ✅ Would keep: {good:,} good documents")
        
        print(f"\n🏆 FINAL RECOMMENDATION:")
        if total_would_keep > 0:
            print(f"  ⚠️ CAUTION: {total_would_keep:,} good documents would be preserved")
            print(f"  🗑️ Safe to delete: {total_would_delete:,} orphaned embeddings")
            print(f"  ✅ CLEANUP SCRIPT LOGIC LOOKS SAFE")
        else:
            print(f"  🗑️ Would delete: {total_would_delete:,} orphaned embeddings")
            print(f"  ✅ No good data at risk - SAFE TO PROCEED")
        
        return True
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return False

if __name__ == "__main__":
    success = analyze_orphaned_embeddings()
    if success:
        print(f"\n📋 NEXT STEPS:")
        print(f"  1. Review the analysis above")
        print(f"  2. If safe, run: python3 data/cleanup_orphaned_embeddings.py")
        print(f"  3. Upload fresh content for Jesus Christ and Chanakya")
        print(f"  4. Generate new embeddings for the fresh content")
    
    sys.exit(0 if success else 1)
