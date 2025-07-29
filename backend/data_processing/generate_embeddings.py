#!/usr/bin/env python3
"""
Generate vector embeddings for personality entries in Cosmos DB using Google Gemini.
This script processes entries that don't have embeddings and generates them using the Gemini API.
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('generate_embeddings.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv('../../.env')

class EmbeddingGenerator:
    """Generate embeddings for entries missing them"""
    
    def __init__(self):
        self.client = None
        self.database = None
        self.container = None
        self.embedding_service = None
        
    def setup_services(self):
        """Setup Cosmos DB and embedding service"""
        try:
            # Setup Cosmos DB
            connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
            if not connection_string:
                logger.error("❌ AZURE_COSMOS_CONNECTION_STRING not found")
                return False
                
            self.client = CosmosClient.from_connection_string(connection_string)
            self.database = self.client.get_database_client('vimarsh-multi-personality')
            self.container = self.database.get_container_client('personality-vectors')
            logger.info("✅ Cosmos DB connected")
            
            # Setup embedding service
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                logger.error("❌ GEMINI_API_KEY not found")
                return False
                
            self.embedding_service = get_gemini_embedding_service()
            logger.info("✅ Gemini embedding service initialized")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error setting up services: {e}")
            return False
    
    def get_entries_without_embeddings(self, limit=100):
        """Get entries that don't have embeddings yet"""
        try:
            query = """
            SELECT c.id, c.personality, c.content, c.text
            FROM c 
            WHERE (NOT IS_DEFINED(c.has_embedding) OR c.has_embedding = false)
            AND c.personality != 'Krishna'
            """
            
            items = list(self.container.query_items(
                query=query, 
                enable_cross_partition_query=True,
                max_item_count=limit
            ))
            
            logger.info(f"🔍 Found {len(items)} entries without embeddings")
            return items
            
        except Exception as e:
            logger.error(f"❌ Error querying entries: {e}")
            return []
    
    def generate_embedding_for_entry(self, entry):
        """Generate embedding for a single entry"""
        try:
            # Get content
            content = entry.get('content') or entry.get('text', '')
            if not content or len(content) < 50:
                logger.debug(f"⚠️ Skipping {entry['id']} - insufficient content")
                return False
            
            # Truncate very long content for embedding model limits
            if len(content) > 7000:
                content = content[:7000]
                logger.debug(f"⚠️ Truncated content for {entry['id']}")
            
            # Generate embedding
            result = self.embedding_service.generate_embedding(
                content, 
                task_type="RETRIEVAL_DOCUMENT"
            )
            
            if result.success and result.embedding:
                # Update the entry with embedding
                entry['embedding'] = result.embedding
                entry['embedding_model'] = 'gemini-text-embedding-004'
                entry['embedding_dimensions'] = len(result.embedding)
                entry['has_embedding'] = True
                
                # Update in Cosmos DB
                self.container.upsert_item(entry)
                return True
            else:
                logger.debug(f"⚠️ Failed to generate embedding for {entry['id']}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error generating embedding for {entry['id']}: {e}")
            return False
    
    def generate_embeddings_batch(self, batch_size=10, max_entries=None):
        """Generate embeddings in batches"""
        logger.info("🧠 Starting embedding generation for entries without embeddings")
        
        total_processed = 0
        total_successful = 0
        
        while True:
            # Get batch of entries without embeddings
            entries = self.get_entries_without_embeddings(limit=batch_size)
            
            if not entries:
                logger.info("✅ No more entries without embeddings found")
                break
            
            if max_entries and total_processed >= max_entries:
                logger.info(f"🛑 Reached maximum entries limit: {max_entries}")
                break
            
            logger.info(f"📦 Processing batch of {len(entries)} entries")
            
            batch_successful = 0
            for i, entry in enumerate(entries):
                try:
                    if self.generate_embedding_for_entry(entry):
                        batch_successful += 1
                        total_successful += 1
                    
                    total_processed += 1
                    
                    # Progress update every 10 entries
                    if total_processed % 10 == 0:
                        logger.info(f"   Progress: {total_processed} processed, {total_successful} successful")
                    
                    # Small delay to avoid rate limiting
                    time.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"❌ Error processing entry {entry.get('id', i)}: {e}")
                    continue
            
            logger.info(f"✅ Batch complete: {batch_successful}/{len(entries)} successful")
            
            # Break if we got fewer entries than requested (likely end of data)
            if len(entries) < batch_size:
                break
        
        logger.info(f"🎉 Embedding generation complete!")
        logger.info(f"   Total processed: {total_processed}")
        logger.info(f"   Total successful: {total_successful}")
        logger.info(f"   Success rate: {(total_successful/total_processed*100):.1f}%")
        
        return total_successful > 0

def main():
    """Main function"""
    print("🧠 EMBEDDING GENERATION FOR EXISTING ENTRIES")
    print("=" * 50)
    
    if not SERVICES_AVAILABLE:
        print("❌ Required services not available")
        return False
    
    generator = EmbeddingGenerator()
    
    if not generator.setup_services():
        print("❌ Failed to setup services")
        return False
    
    # Generate embeddings for entries that don't have them
    success = generator.generate_embeddings_batch(
        batch_size=10,  # Process 10 entries at a time
        max_entries=100  # Limit to 100 entries for testing
    )
    
    if success:
        print("\n✅ EMBEDDING GENERATION SUCCESSFUL!")
        print("   Entries now have vector embeddings for semantic search")
        print("   🔍 RAG system ready for multi-personality queries")
    else:
        print("\n❌ EMBEDDING GENERATION FAILED!")
        print("   Check logs and configuration")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
