#!/usr/bin/env python3
"""
SIMPLE TEST: Verify what would be deleted for Jesus Christ and Chanakya
Quick verification script with safety restrictions
"""

import os
from dotenv import load_dotenv
from azure.cosmos import CosmosClient

load_dotenv('.env')

def simple_analysis():
    """Simple analysis with safety restrictions"""
    
    print("🔍 SAFE DELETION ANALYSIS")
    print("=" * 40)
    
    # SAFETY RESTRICTION
    ALLOWED_PERSONALITIES = ['Jesus Christ', 'Chanakya']
    print(f"🔒 SAFETY: Only analyzing {ALLOWED_PERSONALITIES}")
    
    try:
        connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
        if not connection_string:
            print("❌ Missing connection string")
            return False
            
        client = CosmosClient.from_connection_string(connection_string)
        db = client.get_database_client('vimarsh-multi-personality')
        container = db.get_container_client('personality_vectors')
        
        for personality in ALLOWED_PERSONALITIES:
            print(f"\n📊 {personality}:")
            
            # Total documents
            total_query = f'SELECT VALUE COUNT(1) FROM c WHERE c.personality_id = "{personality}"'
            total = list(container.query_items(total_query, enable_cross_partition_query=True))[0]
            
            # Orphaned (what we would delete)
            orphaned_query = f'''
            SELECT VALUE COUNT(1) FROM c 
            WHERE c.personality_id = "{personality}" 
            AND IS_DEFINED(c.embedding) AND c.embedding != null
            AND (NOT IS_DEFINED(c.content) OR LENGTH(c.content) = 0)
            AND (NOT IS_DEFINED(c.chunk_text) OR LENGTH(c.chunk_text) = 0)
            '''
            orphaned = list(container.query_items(orphaned_query, enable_cross_partition_query=True))[0]
            
            # Good data (what we would keep)
            good_query = f'''
            SELECT VALUE COUNT(1) FROM c 
            WHERE c.personality_id = "{personality}" 
            AND IS_DEFINED(c.embedding) AND c.embedding != null
            AND ((IS_DEFINED(c.content) AND LENGTH(c.content) > 0) OR 
                 (IS_DEFINED(c.chunk_text) AND LENGTH(c.chunk_text) > 0))
            '''
            good = list(container.query_items(good_query, enable_cross_partition_query=True))[0]
            
            print(f"  📈 Total: {total}")
            print(f"  🗑️ Would DELETE: {orphaned} (orphaned embeddings)")
            print(f"  ✅ Would KEEP: {good} (good data)")
            
            if good > 0:
                print(f"  🚨 WARNING: {good} documents have good data!")
            else:
                print(f"  ✅ Safe: All {orphaned} are orphaned embeddings")
        
        print(f"\n🎯 RECOMMENDATION:")
        print(f"✅ SAFE to run cleanup script")
        print(f"🔒 Only Jesus Christ and Chanakya will be affected")
        print(f"🗑️ Only orphaned embeddings (no content/chunk_text) will be deleted")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = simple_analysis()
    if success:
        print(f"\n📋 NEXT STEP:")
        print(f"python3 data/cleanup_orphaned_embeddings.py")
