#!/usr/bin/env python3
"""
Quick embedding generation for Jesus Christ and Chanakya fresh content
Fixed version to complete the 25/25 personalities operational goal
"""

import os
import json
import logging
import sys
import asyncio
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Add the backend directory to Python path for Google Gemini integration
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class QuickEmbeddingGenerator:
    """Generate embeddings for fresh Jesus Christ and Chanakya content"""
    
    def __init__(self):
        self.generated_count = 0
        self.failed_count = 0
        
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv(Path(__file__).parent.parent / '.env')
        
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.cosmos_connection = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
        
    async def generate_embeddings_for_fresh_content(self):
        """Generate embeddings for fresh content entries"""
        
        print("🔮 QUICK EMBEDDING GENERATION FOR FRESH CONTENT")
        print("=" * 60)
        
        try:
            # Import Google Gemini API
            import google.generativeai as genai
            
            if not self.gemini_api_key:
                raise Exception("Missing GEMINI_API_KEY")
            
            # Configure Gemini
            genai.configure(api_key=self.gemini_api_key)
            print("✅ Google Gemini API configured")
            
            # Connect to Cosmos DB
            from azure.cosmos import CosmosClient
            
            if not self.cosmos_connection:
                raise Exception("Missing AZURE_COSMOS_CONNECTION_STRING")
            
            client = CosmosClient.from_connection_string(self.cosmos_connection)
            db = client.get_database_client('vimarsh-multi-personality')
            container = db.get_container_client('personality_vectors')
            print("✅ Cosmos DB connection established")
            
            # Query for fresh content without embeddings
            query = """
                SELECT * FROM c 
                WHERE c.content_type = 'fresh_upload' 
                AND (c.embedding = null OR NOT IS_DEFINED(c.embedding))
                AND (c.personality_id = 'Jesus Christ' OR c.personality_id = 'Chanakya')
            """
            
            print("🔍 Querying for fresh content without embeddings...")
            items = list(container.query_items(query, enable_cross_partition_query=True))
            
            print(f"📊 Found {len(items)} entries needing embeddings")
            
            if not items:
                print("✅ All fresh content already has embeddings!")
                return True
            
            # Generate embeddings in batches
            batch_size = 5  # Conservative batch size
            batches = [items[i:i + batch_size] for i in range(0, len(items), batch_size)]
            
            for batch_num, batch in enumerate(batches):
                print(f"\\n🔮 Processing batch {batch_num + 1}/{len(batches)} ({len(batch)} entries)")
                
                for item in batch:
                    try:
                        # Generate embedding using Gemini
                        content_text = item.get('content', '') or item.get('chunk_text', '')
                        
                        if not content_text or len(content_text.strip()) < 20:
                            print(f"   ⚠️ Skipping {item['id']} - insufficient content")
                            continue
                        
                        # Use Google Gemini text-embedding-004 model
                        result = genai.embed_content(
                            model="models/text-embedding-004",
                            content=content_text,
                            task_type="retrieval_document"
                        )
                        
                        embedding = result['embedding']
                        
                        if not embedding or len(embedding) == 0:
                            print(f"   ❌ Failed to generate embedding for {item['id']}")
                            self.failed_count += 1
                            continue
                        
                        # Update the item with embedding
                        item['embedding'] = embedding
                        item['embedding_model'] = 'text-embedding-004'
                        item['embedding_generated_at'] = datetime.now().isoformat()
                        item['updated_at'] = datetime.now().isoformat()
                        
                        # Replace the item in Cosmos DB
                        container.replace_item(item['id'], item)
                        
                        self.generated_count += 1
                        personality = item.get('personality_id', 'Unknown')
                        print(f"   ✅ Generated embedding for {personality} - {item['id']}")
                        
                        # Small delay to avoid rate limiting
                        await asyncio.sleep(0.1)
                        
                    except Exception as e:
                        self.failed_count += 1
                        logger.error(f"Failed to generate embedding for {item.get('id', 'unknown')}: {e}")
                        print(f"   ❌ Error for {item.get('id', 'unknown')}: {e}")
                
                # Delay between batches
                if batch_num < len(batches) - 1:
                    print(f"   ⏳ Waiting before next batch...")
                    await asyncio.sleep(1)
            
            # Final report
            print(f"\\n🎯 EMBEDDING GENERATION COMPLETE")
            print(f"   ✅ Successfully generated: {self.generated_count}")
            print(f"   ❌ Failed: {self.failed_count}")
            print(f"   📊 Success rate: {(self.generated_count / len(items)) * 100:.1f}%")
            
            return self.generated_count > 0
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            print(f"❌ Embedding generation failed: {e}")
            return False

async def main():
    """Main execution function"""
    
    print("🚀 QUICK EMBEDDING GENERATION FOR 25/25 PERSONALITIES")
    print("=" * 70)
    print("Target: Generate embeddings for Jesus Christ and Chanakya fresh content")
    print()
    
    generator = QuickEmbeddingGenerator()
    success = await generator.generate_embeddings_for_fresh_content()
    
    if success:
        print(f"\\n🎉 SUCCESS! Embedding generation complete")
        print("🎯 Ready to test 25/25 personalities operational status!")
    else:
        print(f"\\n⚠️ Some issues occurred during embedding generation")
        print("🔧 Check logs for details and retry if needed")
    
    return success

if __name__ == "__main__":
    # Install required packages if missing
    try:
        import google.generativeai as genai
    except ImportError:
        print("📦 Installing Google Generative AI...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "google-generativeai"])
    
    # Run the embedding generation
    asyncio.run(main())
