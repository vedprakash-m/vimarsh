#!/usr/bin/env python3
"""
Quick embedding status check - based on working repair_entries.py
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Any
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv('../../.env')

def check_embedding_status():
    """Check embedding status using the same approach as repair_entries.py"""
    try:
        from azure.cosmos import CosmosClient
        
        # Debug environment loading
        print("🔍 Loading environment variables...")
        env_path = '../../.env'
        print(f"   Looking for .env at: {os.path.abspath(env_path)}")
        print(f"   .env exists: {os.path.exists(env_path)}")
        
        # Get connection string (same as repair script)
        connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
        
        print(f"   AZURE_COSMOS_CONNECTION_STRING loaded: {'Yes' if connection_string else 'No'}")
        
        if not connection_string:
            print("❌ Missing required environment variable: AZURE_COSMOS_CONNECTION_STRING")
            return
            
        logger.info("Connecting to Cosmos DB...")
        
        client = CosmosClient.from_connection_string(connection_string)
        database_name = 'vimarsh-multi-personality'
        container_name = 'personality-vectors'
        
        database = client.get_database_client(database_name)
        container = database.get_container_client(container_name)
        
        print("\n🔍 Checking Embedding Status")
        print("=" * 80)
        
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
        
        print(f"📊 Embedding Status Summary:")
        print(f"  Total entries: {total_entries}")
        print(f"  Need embeddings: {no_embeddings}")
        print(f"  Have embeddings: {with_embeddings}")
        
        if total_entries > 0:
            progress = (with_embeddings / total_entries) * 100
            print(f"  Overall progress: {progress:.1f}%")
        
        # Breakdown by personality
        query_by_personality = """
        SELECT c.personality, 
               SUM(CASE WHEN c.has_embedding = true THEN 1 ELSE 0 END) as with_embeddings,
               SUM(CASE WHEN c.has_embedding = false OR IS_NULL(c.has_embedding) OR NOT IS_DEFINED(c.has_embedding) THEN 1 ELSE 0 END) as without_embeddings,
               COUNT(1) as total
        FROM c 
        GROUP BY c.personality
        ORDER BY c.personality
        """
        
        personality_results = list(container.query_items(
            query=query_by_personality,
            enable_cross_partition_query=True
        ))
        
        print(f"\n👥 Breakdown by Personality:")
        print("=" * 60)
        for result in personality_results:
            personality = result['personality']
            total = result['total']
            with_embed = result['with_embeddings']
            without_embed = result['without_embeddings']
            progress = (with_embed / total * 100) if total > 0 else 0
            
            print(f"  {personality}:")
            print(f"    Total: {total}")
            print(f"    Have embeddings: {with_embed}")
            print(f"    Need embeddings: {without_embed}")
            print(f"    Progress: {progress:.1f}%")
            print()
        
        if no_embeddings > 0:
            print(f"🚀 Next step: Generate embeddings for {no_embeddings} entries")
            print("   All repaired entries are ready for embedding generation!")
        else:
            print("✅ All entries have embeddings!")
            
    except Exception as e:
        logger.error(f"Error checking embedding status: {str(e)}")
        raise

if __name__ == "__main__":
    check_embedding_status()
