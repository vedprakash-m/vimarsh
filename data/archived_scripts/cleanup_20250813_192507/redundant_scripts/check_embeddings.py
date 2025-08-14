#!/usr/bin/env python3
"""
Check which entries need embeddings generated
"""

import os
import logging
from dotenv import load_dotenv
from azure.cosmos import CosmosClient

# Load environment variables
load_dotenv('../../.env')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_embedding_status():
    """Check how many entries need embeddings"""
    try:
        # Initialize Cosmos client
        endpoint = os.getenv('COSMOS_ENDPOINT')
        key = os.getenv('COSMOS_KEY')
        client = CosmosClient(endpoint, key)
        
        database_name = 'vimarsh-multi-personality'
        container_name = 'personality-vectors'
        
        database = client.get_database_client(database_name)
        container = database.get_container_client(container_name)
        
        print("🔍 Analyzing embedding status:")
        print("=" * 80)
        
        # Query entries without embeddings
        query_no_embeddings = """
        SELECT c.personality, COUNT(1) as count
        FROM c 
        WHERE c.has_embedding = false OR IS_NULL(c.has_embedding) OR NOT IS_DEFINED(c.has_embedding)
        GROUP BY c.personality
        """
        
        no_embeddings = list(container.query_items(
            query=query_no_embeddings,
            enable_cross_partition_query=True
        ))
        
        # Query entries with embeddings
        query_with_embeddings = """
        SELECT c.personality, COUNT(1) as count
        FROM c 
        WHERE c.has_embedding = true
        GROUP BY c.personality
        """
        
        with_embeddings = list(container.query_items(
            query=query_with_embeddings,
            enable_cross_partition_query=True
        ))
        
        # Query total counts
        query_total = """
        SELECT c.personality, COUNT(1) as count
        FROM c 
        GROUP BY c.personality
        """
        
        total_counts = list(container.query_items(
            query=query_total,
            enable_cross_partition_query=True
        ))
        
        print("\n📊 Embedding Status by Personality:")
        print("=" * 60)
        
        # Create lookup dictionaries
        no_embed_dict = {item['personality']: item['count'] for item in no_embeddings}
        with_embed_dict = {item['personality']: item['count'] for item in with_embeddings}
        
        total_no_embeddings = 0
        total_with_embeddings = 0
        total_entries = 0
        
        for personality_data in total_counts:
            personality = personality_data['personality']
            total = personality_data['count']
            no_embed = no_embed_dict.get(personality, 0)
            with_embed = with_embed_dict.get(personality, 0)
            
            total_no_embeddings += no_embed
            total_with_embeddings += with_embed
            total_entries += total
            
            print(f"  {personality}:")
            print(f"    Total: {total}")
            print(f"    Need embeddings: {no_embed}")
            print(f"    Have embeddings: {with_embed}")
            print(f"    Progress: {(with_embed/total*100):.1f}%")
            print()
        
        print("\n🎯 Summary:")
        print("=" * 40)
        print(f"  Total entries: {total_entries}")
        print(f"  Need embeddings: {total_no_embeddings}")
        print(f"  Have embeddings: {total_with_embeddings}")
        print(f"  Overall progress: {(total_with_embeddings/total_entries*100):.1f}%")
        
        if total_no_embeddings > 0:
            print(f"\n🚀 Next step: Generate embeddings for {total_no_embeddings} entries")
        else:
            print(f"\n✅ All entries have embeddings!")
            
    except Exception as e:
        logger.error(f"Error checking embedding status: {str(e)}")
        raise

if __name__ == "__main__":
    check_embedding_status()
