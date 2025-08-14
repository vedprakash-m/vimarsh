#!/usr/bin/env python3
"""
Simple check for embedding count without environment issues
"""

import sys
import os

# Add the parent directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.cosmos_client import CosmosManager
    
    print("🔍 Checking embedding status using CosmosManager...")
    
    # Initialize CosmosManager
    cosmos_manager = CosmosManager()
    
    # Get container
    container = cosmos_manager.get_container('personality-vectors')
    
    # Query for entries without embeddings
    query_no_embeddings = """
    SELECT COUNT(1) as count
    FROM c 
    WHERE c.has_embedding = false OR IS_NULL(c.has_embedding) OR NOT IS_DEFINED(c.has_embedding)
    """
    
    no_embed_result = list(container.query_items(
        query=query_no_embeddings,
        enable_cross_partition_query=True
    ))
    
    # Query for entries with embeddings  
    query_with_embeddings = """
    SELECT COUNT(1) as count
    FROM c 
    WHERE c.has_embedding = true
    """
    
    with_embed_result = list(container.query_items(
        query=query_with_embeddings,
        enable_cross_partition_query=True
    ))
    
    # Query for total entries
    query_total = """
    SELECT COUNT(1) as count
    FROM c 
    """
    
    total_result = list(container.query_items(
        query=query_total,
        enable_cross_partition_query=True
    ))
    
    no_embeddings = no_embed_result[0]['count'] if no_embed_result else 0
    with_embeddings = with_embed_result[0]['count'] if with_embed_result else 0
    total_entries = total_result[0]['count'] if total_result else 0
    
    print("=" * 60)
    print("📊 Embedding Status Summary:")
    print("=" * 60)
    print(f"  Total entries: {total_entries}")
    print(f"  Need embeddings: {no_embeddings}")
    print(f"  Have embeddings: {with_embeddings}")
    
    if total_entries > 0:
        progress = (with_embeddings / total_entries) * 100
        print(f"  Overall progress: {progress:.1f}%")
    
    if no_embeddings > 0:
        print(f"\n🚀 Next step: Generate embeddings for {no_embeddings} entries")
        print("   Use: python generate_embeddings.py")
    else:
        print("\n✅ All entries have embeddings!")

except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
