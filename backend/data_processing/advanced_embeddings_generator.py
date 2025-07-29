#!/usr/bin/env python3
"""
Advanced vector embeddings generator for personality entries in Cosmos DB using Google Gemini.
This script processes entries that don't have embeddings and generates them using the Gemini API
with proper rate limiting, error handling, and batch processing.
"""

import os
import logging
import asyncio
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
import time

# Configure logging with proper Unicode handling
import sys

# Create handlers with proper encoding
file_handler = logging.FileHandler('advanced_embeddings.log', encoding='utf-8')
console_handler = logging.StreamHandler(sys.stdout)

# Set up console handler for Windows compatibility
if sys.platform.startswith('win'):
    # Use UTF-8 encoding for console on Windows
    console_handler.stream = open(sys.stdout.fileno(), 'w', encoding='utf-8', buffering=1)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[file_handler, console_handler]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv('../../.env')

def safe_log(logger_func, message: str):
    """Safe logging function that handles Unicode encoding issues on Windows."""
    try:
        logger_func(message)
    except UnicodeEncodeError:
        # Remove emojis and special characters if encoding fails
        safe_message = message.encode('ascii', 'ignore').decode('ascii')
        logger_func(f"[EMOJI_REMOVED] {safe_message}")
    except Exception as e:
        # Fallback to basic logging
        print(f"Logging error: {str(e)}")
        print(f"Message: {message}")

class AdvancedEmbeddingGenerator:
    """Handles embedding generation using Google Gemini API with proper error handling and rate limiting."""
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # Rate limiting configuration - More optimal for production
        self.requests_per_minute = 50  # Back to more aggressive rate limit
        self.request_interval = 60.0 / self.requests_per_minute  # 1.2 seconds between requests
        self.last_request_time = 0
        
        # Batch processing configuration - Larger batches for efficiency
        self.batch_size = 10  # More efficient batch size
        self.max_retries = 3  # Reasonable retry count
        self.retry_delay = 2.0  # Standard delay between retries
        
        safe_log(logger.info, f"🤖 Embedding generator initialized with {self.requests_per_minute} requests/minute")
    
    async def generate_embedding(self, text: str, retries: int = 0) -> Optional[List[float]]:
        """
        Generate embedding for a single text using Gemini API with rate limiting and retry logic.
        
        Args:
            text: Text to generate embedding for
            retries: Current retry count
            
        Returns:
            List of embedding values or None if failed
        """
        try:
            import google.generativeai as genai
            
            # Configure Gemini
            genai.configure(api_key=self.api_key)
            
            # Rate limiting
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            if time_since_last < self.request_interval:
                sleep_time = self.request_interval - time_since_last
                await asyncio.sleep(sleep_time)
            
            self.last_request_time = time.time()
            
            # Generate embedding using text-embedding-004 model
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_document"
            )
            
            embedding = result['embedding']
            
            # Validate embedding
            if not embedding or len(embedding) == 0:
                raise ValueError("Empty embedding received")
            
            logger.debug(f"✅ Generated embedding with {len(embedding)} dimensions")
            return embedding
            
        except Exception as e:
            error_str = str(e).lower()
            
            # Handle specific API errors
            if "quota" in error_str or "limit" in error_str:
                logger.error(f"🚫 API quota/limit reached: {str(e)}")
                if retries < self.max_retries:
                    logger.warning("   Waiting 60 seconds before retry...")
                    await asyncio.sleep(60)  # Wait longer for quota issues
                    return await self.generate_embedding(text, retries + 1)
            elif "rate" in error_str:
                logger.warning(f"⚠️ Rate limit hit: {str(e)}")
                if retries < self.max_retries:
                    await asyncio.sleep(self.retry_delay * (retries + 1))  # Standard exponential backoff
                    return await self.generate_embedding(text, retries + 1)
            else:
                # General retry logic
                if retries < self.max_retries:
                    logger.warning(f"⚠️ Embedding generation failed (attempt {retries + 1}/{self.max_retries + 1}): {str(e)}")
                    await asyncio.sleep(self.retry_delay * (retries + 1))  # Exponential backoff
                    return await self.generate_embedding(text, retries + 1)
            
            logger.error(f"❌ Failed to generate embedding after {self.max_retries + 1} attempts: {str(e)}")
            return None
    
    async def generate_batch_embeddings(self, entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate embeddings for a batch of entries with progress tracking.
        
        Args:
            entries: List of database entries to process
            
        Returns:
            Dictionary with processing results and statistics
        """
        results = {
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'updated_entries': [],
            'errors': []
        }
        
        logger.info(f"🔄 Processing batch of {len(entries)} entries...")
        
        for i, entry in enumerate(entries, 1):
            try:
                # Extract text content for embedding
                content_text = self._prepare_text_for_embedding(entry)
                
                if not content_text:
                    logger.warning(f"⚠️ Skipping entry {entry.get('id', 'unknown')} - no content")
                    results['failed'] += 1
                    continue
                
                # Generate embedding
                embedding = await self.generate_embedding(content_text)
                
                if embedding:
                    # Update entry with embedding
                    entry['embedding'] = embedding
                    entry['has_embedding'] = True
                    entry['embedding_model'] = 'text-embedding-004'
                    entry['embedding_generated_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
                    
                    results['updated_entries'].append(entry)
                    results['successful'] += 1
                    
                    safe_log(logger.info, f"✅ Generated embedding for entry {i}/{len(entries)} - {entry.get('personality', 'unknown')}")
                else:
                    results['failed'] += 1
                    error_msg = f"Failed to generate embedding for entry {entry.get('id', 'unknown')}"
                    results['errors'].append(error_msg)
                    logger.error(f"❌ {error_msg}")
                
                results['processed'] += 1
                
                # Progress update every 5 entries
                if i % 5 == 0:
                    logger.info(f"📊 Progress: {i}/{len(entries)} entries processed ({results['successful']} successful)")
                
            except Exception as e:
                error_msg = f"Error processing entry {entry.get('id', 'unknown')}: {str(e)}"
                results['errors'].append(error_msg)
                results['failed'] += 1
                logger.error(f"❌ {error_msg}")
        
        return results
    
    def _prepare_text_for_embedding(self, entry: Dict[str, Any]) -> str:
        """
        Prepare text content from database entry for embedding generation.
        
        Args:
            entry: Database entry dictionary
            
        Returns:
            Cleaned text content suitable for embedding
        """
        # Combine relevant text fields
        text_parts = []
        
        # Add main content
        if entry.get('content'):
            text_parts.append(entry['content'])
        elif entry.get('text'):  # fallback to 'text' field
            text_parts.append(entry['text'])
        
        # Add source information if available
        if entry.get('source'):
            text_parts.append(f"Source: {entry['source']}")
        
        # Add personality context
        if entry.get('personality'):
            text_parts.append(f"Personality: {entry['personality']}")
        
        # Add keywords context
        if entry.get('keywords'):
            keywords_str = ', '.join(entry['keywords']) if isinstance(entry['keywords'], list) else str(entry['keywords'])
            text_parts.append(f"Keywords: {keywords_str}")
        
        # Join and clean text
        full_text = ' | '.join(text_parts)
        
        # Basic text cleaning
        full_text = full_text.strip()
        full_text = ' '.join(full_text.split())  # Normalize whitespace
        
        # Truncate if too long (Gemini has token limits) - More conservative
        max_length = 15000  # Much more conservative limit
        if len(full_text) > max_length:
            full_text = full_text[:max_length] + "..."
            logger.warning(f"⚠️ Text truncated to {max_length} characters for entry {entry.get('id', 'unknown')}")
        
        return full_text

async def generate_embeddings_for_database(batch_size: int = 10, personality_filter: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate embeddings for all entries in Cosmos DB that don't have embeddings.
    
    Args:
        batch_size: Number of entries to process in each batch
        personality_filter: Optional personality filter (e.g., 'Buddha', 'Einstein')
        
    Returns:
        Dictionary with generation statistics and results
    """
    try:
        from azure.cosmos import CosmosClient
        
        # Get connection string
        connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
        if not connection_string:
            raise ValueError("AZURE_COSMOS_CONNECTION_STRING not found in environment variables")
        
        client = CosmosClient.from_connection_string(connection_string)
        database = client.get_database_client('vimarsh-multi-personality')
        container = database.get_container_client('personality-vectors')
        
        # Initialize embedding generator
        generator = AdvancedEmbeddingGenerator()
        
        # Build query for entries without embeddings
        base_query = "SELECT * FROM c WHERE c.has_embedding = false OR IS_NULL(c.has_embedding)"
        
        if personality_filter:
            base_query += f" AND c.personality = '{personality_filter}'"
        
        logger.info("🔍 Querying entries without embeddings...")
        
        # Get entries to process
        entries_to_process = list(container.query_items(query=base_query, enable_cross_partition_query=True))
        
        total_entries = len(entries_to_process)
        logger.info(f"📊 Found {total_entries} entries to process")
        
        if total_entries == 0:
            return {
                'total_entries': 0,
                'processed': 0,
                'successful': 0,
                'failed': 0,
                'message': 'No entries found that need embeddings'
            }
        
        # Process entries in batches
        overall_stats = {
            'total_entries': total_entries,
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'batches_completed': 0,
            'errors': []
        }
        
        for i in range(0, total_entries, batch_size):
            batch = entries_to_process[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total_entries + batch_size - 1) // batch_size
            
            logger.info(f"🔄 Processing batch {batch_num}/{total_batches} ({len(batch)} entries)")
            
            # Generate embeddings for batch
            batch_results = await generator.generate_batch_embeddings(batch)
            
            # Update database with new embeddings
            if batch_results['updated_entries']:
                await _update_database_batch(container, batch_results['updated_entries'])
            
            # Update overall statistics
            overall_stats['processed'] += batch_results['processed']
            overall_stats['successful'] += batch_results['successful']
            overall_stats['failed'] += batch_results['failed']
            overall_stats['batches_completed'] += 1
            overall_stats['errors'].extend(batch_results['errors'])
            
            logger.info(f"✅ Batch {batch_num} complete: {batch_results['successful']}/{len(batch)} successful")
            
            # Small delay between batches to be respectful to API
            if i + batch_size < total_entries:
                await asyncio.sleep(2.0)  # Shorter delay between batches
        
        logger.info("🎉 Embedding generation complete!")
        logger.info("📈 Final statistics:")
        logger.info(f"  Total entries: {overall_stats['total_entries']}")
        logger.info(f"  Successfully processed: {overall_stats['successful']}")
        logger.info(f"  Failed: {overall_stats['failed']}")
        logger.info(f"  Success rate: {(overall_stats['successful'] / overall_stats['total_entries'] * 100):.1f}%")
        
        return overall_stats
        
    except Exception as e:
        error_msg = f"❌ Embedding generation failed: {str(e)}"
        logger.error(error_msg)
        return {
            'error': error_msg,
            'total_entries': 0,
            'processed': 0,
            'successful': 0,
            'failed': 0
        }

async def _update_database_batch(container, entries: List[Dict[str, Any]]):
    """Update database entries with new embeddings in batch."""
    safe_log(logger.info, f"💾 Updating {len(entries)} entries in database...")
    
    successful_updates = 0
    failed_updates = 0
    
    for entry in entries:
        try:
            # Update the entry in Cosmos DB
            container.upsert_item(entry)
            successful_updates += 1
            
        except Exception as e:
            logger.error(f"❌ Failed to update entry {entry.get('id', 'unknown')}: {str(e)}")
            failed_updates += 1
    
    safe_log(logger.info, f"💾 Database update complete: {successful_updates} successful, {failed_updates} failed")

def main():
    """Main execution function with interactive options."""
    print("🤖 Advanced Vimarsh Embedding Generation Tool")
    print("=" * 50)
    
    # Get user preferences
    print("\n🎯 Generation Options:")
    print("1. Generate embeddings for all personalities")
    print("2. Generate embeddings for specific personality")
    print("3. Show statistics only (no generation)")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    personality_filter = None
    if choice == "2":
        personality_filter = input("Enter personality name (Buddha, Einstein, Newton, Rumi, etc.): ").strip()
    elif choice == "3":
        # Just show statistics
        asyncio.run(_show_statistics_only())
        return
    
    batch_size = 10  # More efficient default
    try:
        batch_input = input(f"\nBatch size (default {batch_size}, recommended: 10-20): ").strip()
        if batch_input:
            batch_size = int(batch_input)
            if batch_size > 30:
                print("⚠️  Warning: Batch sizes > 30 may cause API errors. Recommended: 10-20")
    except ValueError:
        logger.warning("Invalid batch size, using default")
    
    print("\n🚀 Starting embedding generation...")
    print(f"  Personality filter: {'All' if not personality_filter else personality_filter}")
    print(f"  Batch size: {batch_size}")
    
    # Run embedding generation
    results = asyncio.run(generate_embeddings_for_database(batch_size, personality_filter))
    
    if 'error' in results:
        print(f"❌ Generation failed: {results['error']}")
    else:
        print("\n🎉 Generation completed!")
        print(f"  Total entries processed: {results['processed']}")
        print(f"  Successful: {results['successful']}")
        print(f"  Failed: {results['failed']}")
        
        if results['errors']:
            print(f"\n⚠️ {len(results['errors'])} errors occurred. Check advanced_embeddings.log for details.")

async def _show_statistics_only():
    """Show embedding statistics without generating new ones."""
    try:
        from azure.cosmos import CosmosClient
        
        connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
        client = CosmosClient.from_connection_string(connection_string)
        database = client.get_database_client('vimarsh-multi-personality')
        container = database.get_container_client('personality-vectors')
        
        # Query embedding statistics
        stats_query = """
        SELECT 
            c.personality,
            COUNT(1) as total_entries,
            SUM(CASE WHEN c.has_embedding = true THEN 1 ELSE 0 END) as with_embeddings,
            SUM(CASE WHEN c.has_embedding = false OR IS_NULL(c.has_embedding) THEN 1 ELSE 0 END) as without_embeddings
        FROM c 
        GROUP BY c.personality
        """
        
        print("\n📊 Embedding Statistics by Personality:")
        print("=" * 70)
        
        total_entries = 0
        total_with_embeddings = 0
        total_without_embeddings = 0
        
        for item in container.query_items(query=stats_query, enable_cross_partition_query=True):
            personality = item['personality']
            total = item['total_entries']
            with_emb = item['with_embeddings']
            without_emb = item['without_embeddings']
            
            completion_rate = (with_emb / total * 100) if total > 0 else 0
            
            print(f"{personality:<12} | Total: {total:>4} | With: {with_emb:>4} | Without: {without_emb:>4} | {completion_rate:>5.1f}%")
            
            total_entries += total
            total_with_embeddings += with_emb
            total_without_embeddings += without_emb
        
        overall_completion = (total_with_embeddings / total_entries * 100) if total_entries > 0 else 0
        
        print("-" * 70)
        print(f"{'TOTAL':<12} | Total: {total_entries:>4} | With: {total_with_embeddings:>4} | Without: {total_without_embeddings:>4} | {overall_completion:>5.1f}%")
        
    except Exception as e:
        print(f"❌ Failed to get statistics: {str(e)}")

if __name__ == "__main__":
    main()
