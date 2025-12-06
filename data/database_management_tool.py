#!/usr/bin/env python3
"""
Combined Database Management Tool for Vimarsh
- Cleanup old entries without proper integration_date
- Generate Azure OpenAI embeddings for new personality entries
- Comprehensive database health management
"""

import os
import sys
import logging
import asyncio
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
import time

# Add backend to path for service imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('database_management.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv('../../.env')

class DatabaseManager:
    """Comprehensive database management for cleanup and embedding generation."""
    
    def __init__(self):
        self.client = None
        self.database = None
        self.container = None
        
        # Initialize Azure OpenAI embedding service
        try:
            from services.azure_openai_embedding_service import AzureOpenAIEmbeddingService
            self.embedding_service = AzureOpenAIEmbeddingService()
            self.use_azure = True
            logger.info("✅ Azure OpenAI embedding service initialized")
        except Exception as e:
            logger.warning(f"Azure OpenAI unavailable, using Gemini fallback: {e}")
            self.api_key = os.getenv('GOOGLE_API_KEY')
            if not self.api_key:
                raise ValueError("Neither Azure OpenAI nor GOOGLE_API_KEY available")
            self.use_azure = False
        
        # Rate limiting for embeddings
        self.requests_per_minute = 50
        self.request_interval = 60.0 / self.requests_per_minute
        self.last_request_time = 0
        
        self._setup_cosmos_db()
    
    def _setup_cosmos_db(self):
        """Initialize Cosmos DB connection."""
        try:
            from azure.cosmos import CosmosClient
            
            connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
            if not connection_string:
                raise ValueError("AZURE_COSMOS_CONNECTION_STRING not found in environment variables")
            
            self.client = CosmosClient.from_connection_string(connection_string)
            self.database = self.client.get_database_client('vimarsh-multi-personality')
            self.container = self.database.get_container_client('personality-vectors')
            
            logger.info("✅ Cosmos DB connection established")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Cosmos DB: {str(e)}")
            raise
    
    async def analyze_database_state(self) -> Dict[str, Any]:
        """Analyze current database state for both cleanup and embedding needs."""
        try:
            logger.info("🔍 Analyzing database state...")
            
            analysis = {
                'total_entries': 0,
                'personality_distribution': {},
                'integration_dates': {},
                'embedding_status': {},
                'cleanup_candidates': 0,
                'embedding_candidates': 0
            }
            
            # Query all entries for comprehensive analysis
            all_entries_query = """
            SELECT c.personality, c.integration_date, c.has_embedding, c.id
            FROM c
            """
            
            for item in self.container.query_items(query=all_entries_query, enable_cross_partition_query=True):
                analysis['total_entries'] += 1
                
                personality = item.get('personality', 'Unknown')
                integration_date = item.get('integration_date', 'Unknown')
                has_embedding = item.get('has_embedding', False)
                
                # Count by personality
                analysis['personality_distribution'][personality] = analysis['personality_distribution'].get(personality, 0) + 1
                
                # Count by integration date
                analysis['integration_dates'][integration_date] = analysis['integration_dates'].get(integration_date, 0) + 1
                
                # Count embedding status by personality
                if personality not in analysis['embedding_status']:
                    analysis['embedding_status'][personality] = {'with_embeddings': 0, 'without_embeddings': 0}
                
                if has_embedding:
                    analysis['embedding_status'][personality]['with_embeddings'] += 1
                else:
                    analysis['embedding_status'][personality]['without_embeddings'] += 1
                    analysis['embedding_candidates'] += 1
                
                # Count cleanup candidates (old entries without proper date)
                if integration_date in ['Unknown', None] or not integration_date:
                    analysis['cleanup_candidates'] += 1
            
            logger.info("📊 Database analysis complete")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Database analysis failed: {str(e)}")
            return {'error': str(e)}
    
    def print_analysis_report(self, analysis: Dict[str, Any]):
        """Print a comprehensive analysis report."""
        if 'error' in analysis:
            print(f"❌ Analysis failed: {analysis['error']}")
            return
        
        print("\n" + "="*70)
        print("📊 VIMARSH DATABASE ANALYSIS REPORT")
        print("="*70)
        
        print(f"\n🎯 OVERVIEW:")
        print(f"  Total entries: {analysis['total_entries']}")
        print(f"  Cleanup candidates: {analysis['cleanup_candidates']}")
        print(f"  Embedding candidates: {analysis['embedding_candidates']}")
        
        print(f"\n👥 PERSONALITY DISTRIBUTION:")
        for personality, count in sorted(analysis['personality_distribution'].items()):
            print(f"  {personality:<15}: {count:>4} entries")
        
        print(f"\n📅 INTEGRATION DATES:")
        for date, count in sorted(analysis['integration_dates'].items()):
            print(f"  {date:<15}: {count:>4} entries")
        
        print(f"\n🧠 EMBEDDING STATUS:")
        for personality, status in sorted(analysis['embedding_status'].items()):
            total = status['with_embeddings'] + status['without_embeddings']
            completion_rate = (status['with_embeddings'] / total * 100) if total > 0 else 0
            print(f"  {personality:<12}: {status['with_embeddings']:>3}/{total:<3} ({completion_rate:>5.1f}%)")
    
    async def cleanup_old_entries(self, dry_run: bool = True) -> Dict[str, Any]:
        """Clean up old entries without proper integration_date."""
        try:
            logger.info(f"🧹 Starting cleanup {'(DRY RUN)' if dry_run else '(ACTUAL CLEANUP)'}")
            
            # Query for old entries
            old_entries_query = """
            SELECT c.id, c.personality, c.integration_date, c.source
            FROM c 
            WHERE c.integration_date = 'Unknown' OR IS_NULL(c.integration_date)
            """
            
            entries_to_cleanup = list(self.container.query_items(query=old_entries_query, enable_cross_partition_query=True))
            
            cleanup_stats = {
                'total_found': len(entries_to_cleanup),
                'deleted': 0,
                'errors': [],
                'dry_run': dry_run
            }
            
            logger.info(f"Found {len(entries_to_cleanup)} entries to cleanup")
            
            if not dry_run and entries_to_cleanup:
                # Perform actual cleanup
                from azure.cosmos.exceptions import CosmosResourceNotFoundError
                
                for entry in entries_to_cleanup:
                    try:
                        self.container.delete_item(
                            item=entry['id'],
                            partition_key=entry['personality']
                        )
                        cleanup_stats['deleted'] += 1
                        
                        if cleanup_stats['deleted'] % 50 == 0:
                            logger.info(f"  Deleted {cleanup_stats['deleted']} entries...")
                            
                    except CosmosResourceNotFoundError:
                        logger.warning(f"Entry {entry['id']} already deleted")
                    except Exception as e:
                        error_msg = f"Failed to delete {entry['id']}: {str(e)}"
                        cleanup_stats['errors'].append(error_msg)
                        logger.error(error_msg)
                
                logger.info(f"✅ Cleanup complete: {cleanup_stats['deleted']} entries deleted")
            
            return cleanup_stats
            
        except Exception as e:
            error_msg = f"❌ Cleanup failed: {str(e)}"
            logger.error(error_msg)
            return {'error': error_msg, 'dry_run': dry_run}
    
    async def generate_embedding(self, text: str, retries: int = 0) -> Optional[List[float]]:
        """Generate embedding using Gemini API with rate limiting."""
        try:
            import google.generativeai as genai
            
            if not self.api_key:
                raise ValueError("GOOGLE_API_KEY not found")
            
            genai.configure(api_key=self.api_key)
            
            # Rate limiting
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            if time_since_last < self.request_interval:
                sleep_time = self.request_interval - time_since_last
                await asyncio.sleep(sleep_time)
            
            self.last_request_time = time.time()
            
            # Generate embedding using gemini-embedding-001 with MRL
            result = genai.embed_content(
                model="models/gemini-embedding-001",
                content=text,
                task_type="retrieval_document",
                output_dimensionality=768  # MRL dimension for Cosmos DB compatibility
            )
            
            embedding = result['embedding']
            
            if not embedding or len(embedding) == 0:
                raise ValueError("Empty embedding received")
            
            return embedding
            
        except Exception as e:
            if retries < 3:
                logger.warning(f"⚠️ Embedding generation failed (attempt {retries + 1}/4): {str(e)}")
                await asyncio.sleep(2.0 * (retries + 1))
                return await self.generate_embedding(text, retries + 1)
            else:
                logger.error(f"❌ Failed to generate embedding after 4 attempts: {str(e)}")
                return None
    
    def _prepare_text_for_embedding(self, entry: Dict[str, Any]) -> str:
        """Prepare text content for embedding generation."""
        text_parts = []
        
        # Add main content
        if entry.get('content'):
            text_parts.append(entry['content'])
        elif entry.get('text'):
            text_parts.append(entry['text'])
        
        # Add context
        if entry.get('source'):
            text_parts.append(f"Source: {entry['source']}")
        
        if entry.get('personality'):
            text_parts.append(f"Personality: {entry['personality']}")
        
        if entry.get('keywords'):
            keywords_str = ', '.join(entry['keywords']) if isinstance(entry['keywords'], list) else str(entry['keywords'])
            text_parts.append(f"Keywords: {keywords_str}")
        
        full_text = ' | '.join(text_parts).strip()
        full_text = ' '.join(full_text.split())  # Normalize whitespace
        
        # Truncate if too long
        max_length = 30000
        if len(full_text) > max_length:
            full_text = full_text[:max_length] + "..."
        
        return full_text
    
    async def generate_embeddings(self, personality_filter: Optional[str] = None, batch_size: int = 10) -> Dict[str, Any]:
        """Generate embeddings for entries that don't have them."""
        try:
            logger.info(f"🤖 Starting embedding generation for {'all personalities' if not personality_filter else personality_filter}")
            
            # Query for entries without embeddings
            base_query = "SELECT * FROM c WHERE c.has_embedding = false OR IS_NULL(c.has_embedding)"
            
            if personality_filter:
                base_query += f" AND c.personality = '{personality_filter}'"
            
            entries_to_process = list(self.container.query_items(query=base_query, enable_cross_partition_query=True))
            
            embedding_stats = {
                'total_entries': len(entries_to_process),
                'processed': 0,
                'successful': 0,
                'failed': 0,
                'errors': []
            }
            
            logger.info(f"Found {len(entries_to_process)} entries needing embeddings")
            
            if not entries_to_process:
                return embedding_stats
            
            # Process in batches
            for i in range(0, len(entries_to_process), batch_size):
                batch = entries_to_process[i:i + batch_size]
                batch_num = (i // batch_size) + 1
                total_batches = (len(entries_to_process) + batch_size - 1) // batch_size
                
                logger.info(f"🔄 Processing batch {batch_num}/{total_batches} ({len(batch)} entries)")
                
                for entry in batch:
                    try:
                        # Prepare text
                        content_text = self._prepare_text_for_embedding(entry)
                        
                        if not content_text:
                            logger.warning(f"⚠️ Skipping entry {entry.get('id', 'unknown')} - no content")
                            embedding_stats['failed'] += 1
                            continue
                        
                        # Generate embedding
                        embedding = await self.generate_embedding(content_text)
                        
                        if embedding:
                            # Update entry
                            entry['embedding'] = embedding
                            entry['has_embedding'] = True
                            entry['embedding_model'] = 'gemini-embedding-001'
                            entry['embedding_generated_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
                            
                            # Update in database
                            self.container.upsert_item(entry)
                            embedding_stats['successful'] += 1
                            
                            logger.info(f"✅ Generated embedding for {entry.get('personality', 'unknown')} entry")
                        else:
                            embedding_stats['failed'] += 1
                            error_msg = f"Failed to generate embedding for entry {entry.get('id', 'unknown')}"
                            embedding_stats['errors'].append(error_msg)
                        
                        embedding_stats['processed'] += 1
                        
                    except Exception as e:
                        error_msg = f"Error processing entry {entry.get('id', 'unknown')}: {str(e)}"
                        embedding_stats['errors'].append(error_msg)
                        embedding_stats['failed'] += 1
                        logger.error(error_msg)
                
                # Small delay between batches
                if i + batch_size < len(entries_to_process):
                    await asyncio.sleep(2.0)
            
            logger.info("🎉 Embedding generation complete")
            return embedding_stats
            
        except Exception as e:
            error_msg = f"❌ Embedding generation failed: {str(e)}"
            logger.error(error_msg)
            return {'error': error_msg}

async def main():
    """Main interactive function."""
    print("🔧 VIMARSH DATABASE MANAGEMENT TOOL")
    print("="*50)
    
    try:
        db_manager = DatabaseManager()
        
        while True:
            print("\n📋 AVAILABLE OPERATIONS:")
            print("1. Analyze database state")
            print("2. Cleanup old entries (dry run)")
            print("3. Cleanup old entries (actual)")
            print("4. Generate embeddings for all personalities")
            print("5. Generate embeddings for specific personality")
            print("6. Do both cleanup and embedding generation")
            print("7. Exit")
            
            choice = input("\nSelect operation (1-7): ").strip()
            
            if choice == "1":
                # Analyze database
                analysis = await db_manager.analyze_database_state()
                db_manager.print_analysis_report(analysis)
                
            elif choice == "2":
                # Dry run cleanup
                results = await db_manager.cleanup_old_entries(dry_run=True)
                print(f"\n🔍 DRY RUN RESULTS:")
                print(f"  Entries found for cleanup: {results.get('total_found', 0)}")
                print("  No actual deletion performed")
                
            elif choice == "3":
                # Actual cleanup
                confirm = input("\n⚠️  WARNING: This will permanently delete old entries. Continue? (yes/no): ").strip().lower()
                if confirm in ['yes', 'y']:
                    results = await db_manager.cleanup_old_entries(dry_run=False)
                    print(f"\n✅ CLEANUP COMPLETE:")
                    print(f"  Entries deleted: {results.get('deleted', 0)}")
                    if results.get('errors'):
                        print(f"  Errors: {len(results['errors'])}")
                else:
                    print("❌ Cleanup cancelled")
                
            elif choice == "4":
                # Generate embeddings for all
                results = await db_manager.generate_embeddings()
                print(f"\n🤖 EMBEDDING GENERATION COMPLETE:")
                print(f"  Total entries: {results.get('total_entries', 0)}")
                print(f"  Successful: {results.get('successful', 0)}")
                print(f"  Failed: {results.get('failed', 0)}")
                
            elif choice == "5":
                # Generate embeddings for specific personality
                personality = input("Enter personality name (Buddha, Einstein, Newton, Rumi, etc.): ").strip()
                results = await db_manager.generate_embeddings(personality_filter=personality)
                print(f"\n🤖 EMBEDDING GENERATION FOR {personality.upper()}:")
                print(f"  Total entries: {results.get('total_entries', 0)}")
                print(f"  Successful: {results.get('successful', 0)}")
                print(f"  Failed: {results.get('failed', 0)}")
                
            elif choice == "6":
                # Do both operations
                print("\n🚀 PERFORMING COMPREHENSIVE DATABASE MANAGEMENT")
                
                # First, analyze
                print("\n📊 Step 1: Analyzing database...")
                analysis = await db_manager.analyze_database_state()
                db_manager.print_analysis_report(analysis)
                
                # Cleanup confirmation
                if analysis.get('cleanup_candidates', 0) > 0:
                    confirm_cleanup = input(f"\n🧹 Found {analysis['cleanup_candidates']} entries to cleanup. Proceed? (yes/no): ").strip().lower()
                    if confirm_cleanup in ['yes', 'y']:
                        cleanup_results = await db_manager.cleanup_old_entries(dry_run=False)
                        print(f"  ✅ Cleanup: {cleanup_results.get('deleted', 0)} entries deleted")
                
                # Embedding generation
                if analysis.get('embedding_candidates', 0) > 0:
                    confirm_embeddings = input(f"\n🤖 Found {analysis['embedding_candidates']} entries needing embeddings. Proceed? (yes/no): ").strip().lower()
                    if confirm_embeddings in ['yes', 'y']:
                        embedding_results = await db_manager.generate_embeddings()
                        print(f"  ✅ Embeddings: {embedding_results.get('successful', 0)} generated successfully")
                
                print("\n🎉 Comprehensive database management complete!")
                
            elif choice == "7":
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please select 1-7.")
    
    except Exception as e:
        print(f"❌ Tool failed: {str(e)}")
        logger.error(f"Tool failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
