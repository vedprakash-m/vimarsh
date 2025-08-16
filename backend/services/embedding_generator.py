#!/usr/bin/env python3
"""
Vector Embedding Generation Service
Generates embeddings for personality chunks using Google's text-embedding-004 model
"""

import os
import json
import logging
import asyncio
import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class EmbeddingJob:
    """Data structure for embedding generation job"""
    chunk_id: str
    personality_id: str
    chunk_text: str
    token_count: int
    retry_count: int = 0
    max_retries: int = 3
    
class EmbeddingGenerator:
    """Service for generating embeddings for personality chunks"""
    
    def __init__(self):
        # Initialize environment variables - use standardized connection string only
        self.cosmos_connection_string = os.getenv("AZURE_COSMOS_CONNECTION_STRING")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        
        if not self.gemini_api_key:
            raise ValueError("Required environment variable not set: GEMINI_API_KEY")
            
        # Check Cosmos DB credentials
        if not self.cosmos_connection_string:
            raise ValueError("Cosmos DB credentials not set. Please set AZURE_COSMOS_CONNECTION_STRING")
        
        # Configure Gemini AI
        genai.configure(api_key=self.gemini_api_key)
        self.embedding_model = "models/text-embedding-004"
        
        # Initialize Cosmos DB client
        self.cosmos_client = CosmosClient.from_connection_string(cosmos_connection_string)
        self.database_name = database_name
        self.container_name = os.getenv("AZURE_COSMOS_CONTAINER_NAME", "personality-vectors")  # Fixed: use hyphen like production
        self.database = self.cosmos_client.get_database_client(database_name)
        self.container = self.database.get_container_client(self.container_name)
        
        # Processing configuration
        self.batch_size = 10  # Process 10 chunks at a time
        self.rate_limit_delay = 1.0  # 1 second between API calls
        self.max_concurrent_requests = 5
        
        # Statistics tracking
        self.stats = {
            "total_chunks": 0,
            "processed_chunks": 0,
            "failed_chunks": 0,
            "skipped_chunks": 0,
            "start_time": None,
            "end_time": None,
            "personalities_processed": set(),
            "api_calls_made": 0,
            "total_tokens_processed": 0
        }
    
    async def generate_embeddings_for_all_chunks(self) -> Dict[str, Any]:
        """Generate embeddings for all chunks with embedding_status = 'pending'"""
        logger.info("🚀 Starting embedding generation for all pending chunks")
        
        self.stats["start_time"] = datetime.now(timezone.utc)
        
        try:
            # Get all pending chunks
            pending_chunks = await self.get_pending_chunks()
            self.stats["total_chunks"] = len(pending_chunks)
            
            logger.info(f"📊 Found {len(pending_chunks):,} chunks pending embedding generation")
            
            if not pending_chunks:
                logger.info("✅ No pending chunks found - all embeddings up to date!")
                return self._generate_summary()
            
            # Convert to EmbeddingJob objects
            jobs = []
            for chunk in pending_chunks:
                try:
                    # Support both 'content' and 'chunk_text' field names
                    chunk_content = chunk.get('content') or chunk.get('chunk_text', '')
                    if not chunk_content:
                        logger.warning(f"⚠️ Skipping chunk due to missing content: {chunk.get('id', 'unknown')}")
                        continue
                    
                    job = EmbeddingJob(
                        chunk_id=chunk['id'],
                        personality_id=chunk['personality_id'],
                        chunk_text=chunk_content,
                        token_count=len(chunk_content.split())  # Simple token estimate
                    )
                    jobs.append(job)
                except KeyError as e:
                    logger.warning(f"⚠️ Skipping chunk due to missing field {e}: {chunk.get('id', 'unknown')}")
                    continue
            
            if not jobs:
                logger.error("❌ No valid jobs created from chunks")
                return {"status": "error", "message": "No valid chunks to process"}
            
            logger.info(f"📊 Processing {len(jobs)} embedding jobs")
            
            # Process chunks in batches
            await self.process_chunks_in_batches(jobs)
            
            self.stats["end_time"] = datetime.now(timezone.utc)
            return self._generate_summary()
            
        except Exception as e:
            logger.error(f"❌ Embedding generation failed: {e}")
            self.stats["end_time"] = datetime.now(timezone.utc)
            raise
    
    async def get_pending_chunks(self) -> List[Dict[str, Any]]:
        """Get all chunks that need embeddings generated."""
        try:
            # First, update existing chunks that have embeddings to mark them as complete
            await self._update_existing_embedding_status()
            
            # Now query for chunks that truly need embeddings
            query = """
            SELECT * FROM c 
            WHERE (NOT IS_DEFINED(c.embedding_status) OR c.embedding_status = 'pending')
            AND (NOT IS_DEFINED(c.embedding) OR c.embedding = null OR ARRAY_LENGTH(c.embedding) = 0)
            AND (IS_DEFINED(c.content) OR IS_DEFINED(c.chunk_text))
            """
            
            logger.info(f"🔍 Querying for chunks that need embeddings...")
            items = list(self.container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            
            logger.info(f"✅ Found {len(items)} chunks that need embeddings")
            return items
            
        except Exception as e:
            logger.error(f"❌ Failed to retrieve pending chunks: {e}")
            raise
    
    async def _update_existing_embedding_status(self):
        """Update chunks that already have embeddings to mark them as complete"""
        try:
            logger.info("🔄 Updating embedding status for chunks that already have embeddings...")
            
            # Query for chunks that have embeddings but no status
            query = """
            SELECT c.id, c.personality_id FROM c 
            WHERE IS_DEFINED(c.embedding) 
            AND IS_ARRAY(c.embedding) 
            AND ARRAY_LENGTH(c.embedding) > 0
            AND (NOT IS_DEFINED(c.embedding_status) OR c.embedding_status != 'complete')
            """
            
            items = list(self.container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            
            logger.info(f"📊 Found {len(items)} chunks with embeddings to update status")
            
            # Update in batches to avoid overwhelming the database
            batch_size = 100
            updated_count = 0
            
            for i in range(0, len(items), batch_size):
                batch = items[i:i + batch_size]
                
                for item in batch:
                    try:
                        # Read the full chunk
                        chunk = self.container.read_item(
                            item=item['id'],
                            partition_key=item['personality_id']
                        )
                        
                        # Update the status
                        chunk["embedding_status"] = "complete"
                        chunk["embedding_model"] = self.embedding_model
                        if "embedding_generated_at" not in chunk:
                            chunk["embedding_generated_at"] = datetime.now(timezone.utc).isoformat()
                        
                        # Save the updated chunk
                        self.container.upsert_item(chunk)
                        updated_count += 1
                        
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to update status for chunk {item['id']}: {e}")
                        continue
                
                # Rate limiting between batches
                if i + batch_size < len(items):
                    await asyncio.sleep(0.1)
            
            logger.info(f"✅ Updated embedding status for {updated_count:,} chunks")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to update existing embedding status: {e}")
            # Don't raise - this is a cleanup operation
    
    async def process_chunks_in_batches(self, chunks: List[EmbeddingJob]):
        """Process chunks in batches with rate limiting"""
        
        total_batches = (len(chunks) + self.batch_size - 1) // self.batch_size
        
        for batch_idx in range(0, len(chunks), self.batch_size):
            batch = chunks[batch_idx:batch_idx + self.batch_size]
            batch_num = (batch_idx // self.batch_size) + 1
            
            logger.info(f"📦 Processing batch {batch_num}/{total_batches} ({len(batch)} chunks)")
            
            try:
                await self.process_batch(batch)
                
                # Rate limiting between batches
                if batch_num < total_batches:
                    await asyncio.sleep(self.rate_limit_delay)
                    
            except Exception as e:
                logger.error(f"❌ Failed to process batch {batch_num}: {e}")
                # Continue with next batch
                continue
            
            # Progress reporting
            if batch_num % 10 == 0:
                self._log_progress(batch_num, total_batches)
    
    async def process_batch(self, batch: List[EmbeddingJob]):
        """Process a single batch of chunks"""
        
        # Generate embeddings for all chunks in batch
        embedding_results = await self.generate_batch_embeddings(batch)
        
        # Update chunks in Cosmos DB
        for job, embedding in zip(batch, embedding_results):
            if embedding is not None:
                await self.update_chunk_with_embedding(job, embedding)
                self.stats["processed_chunks"] += 1
                self.stats["total_tokens_processed"] += job.token_count
            else:
                await self.handle_failed_chunk(job)
                self.stats["failed_chunks"] += 1
    
    async def generate_batch_embeddings(self, batch: List[EmbeddingJob]) -> List[Optional[List[float]]]:
        """Generate embeddings for a batch of chunks using Gemini API"""
        
        embeddings = []
        
        for job in batch:
            try:
                # Generate embedding using Gemini
                result = genai.embed_content(
                    model=self.embedding_model,
                    content=job.chunk_text,
                    task_type="retrieval_document"
                )
                
                embedding = result['embedding']
                embeddings.append(embedding)
                
                self.stats["api_calls_made"] += 1
                
                # Rate limiting between individual API calls
                await asyncio.sleep(0.1)  # 100ms between calls
                
            except Exception as e:
                logger.error(f"❌ Failed to generate embedding for chunk {job.chunk_id}: {e}")
                embeddings.append(None)
                
                # Exponential backoff for rate limit errors
                if "quota" in str(e).lower() or "rate" in str(e).lower():
                    await asyncio.sleep(5.0)
        
        return embeddings
    
    async def update_chunk_with_embedding(self, job: EmbeddingJob, embedding: List[float]):
        """Update chunk in Cosmos DB with generated embedding"""
        
        try:
            # Read current chunk
            chunk = self.container.read_item(
                item=job.chunk_id,
                partition_key=job.personality_id
            )
            
            # Update with embedding
            chunk["embedding"] = embedding
            chunk["embedding_status"] = "complete"
            chunk["embedding_model"] = self.embedding_model
            chunk["embedding_generated_at"] = datetime.now(timezone.utc).isoformat()
            
            # Save updated chunk
            self.container.upsert_item(chunk)
            
            logger.debug(f"✅ Updated chunk {job.chunk_id} with embedding ({len(embedding)} dimensions)")
            
        except Exception as e:
            logger.error(f"❌ Failed to update chunk {job.chunk_id}: {e}")
            raise
    
    async def handle_failed_chunk(self, job: EmbeddingJob):
        """Handle chunks that failed embedding generation"""
        
        try:
            # Read current chunk
            chunk = self.container.read_item(
                item=job.chunk_id,
                partition_key=job.personality_id
            )
            
            # Update failure status
            chunk["embedding_status"] = "failed"
            chunk["embedding_error"] = f"Failed after {job.max_retries} retries"
            chunk["embedding_failed_at"] = datetime.now(timezone.utc).isoformat()
            
            # Save updated chunk
            self.container.upsert_item(chunk)
            
            logger.warning(f"⚠️ Marked chunk {job.chunk_id} as failed")
            
        except Exception as e:
            logger.error(f"❌ Failed to update failed chunk {job.chunk_id}: {e}")
    
    def _log_progress(self, current_batch: int, total_batches: int):
        """Log progress statistics"""
        
        elapsed = datetime.now(timezone.utc) - self.stats["start_time"]
        elapsed_seconds = elapsed.total_seconds()
        
        processed = self.stats["processed_chunks"]
        failed = self.stats["failed_chunks"]
        total = self.stats["total_chunks"]
        
        rate = processed / elapsed_seconds if elapsed_seconds > 0 else 0
        eta_seconds = (total - processed - failed) / rate if rate > 0 else 0
        eta_minutes = eta_seconds / 60
        
        logger.info(f"""
        📈 Progress Update:
        - Batches: {current_batch}/{total_batches}
        - Chunks: {processed:,} processed, {failed:,} failed, {total:,} total
        - Rate: {rate:.1f} chunks/second
        - ETA: {eta_minutes:.1f} minutes
        - API Calls: {self.stats['api_calls_made']:,}
        - Tokens: {self.stats['total_tokens_processed']:,}
        """)
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate processing summary"""
        
        if self.stats["start_time"] and self.stats["end_time"]:
            processing_time = (self.stats["end_time"] - self.stats["start_time"]).total_seconds()
        else:
            processing_time = 0
        
        success_rate = (
            self.stats["processed_chunks"] / 
            max(self.stats["total_chunks"], 1) * 100
        )
        
        return {
            "embedding_generation_completed": True,
            "processing_time_seconds": processing_time,
            "statistics": {
                "total_chunks": self.stats["total_chunks"],
                "processed_chunks": self.stats["processed_chunks"],
                "failed_chunks": self.stats["failed_chunks"],
                "skipped_chunks": self.stats["skipped_chunks"],
                "api_calls_made": self.stats["api_calls_made"],
                "total_tokens_processed": self.stats["total_tokens_processed"],
                "personalities_count": len(self.stats["personalities_processed"])
            },
            "personalities_processed": list(self.stats["personalities_processed"]),
            "success_rate": success_rate,
            "processing_rate": self.stats["processed_chunks"] / processing_time if processing_time > 0 else 0
        }
    
    async def get_embedding_status(self) -> Dict[str, Any]:
        """Get current embedding generation status"""
        
        try:
            # Count chunks by status
            status_counts = {"pending": 0, "complete": 0, "failed": 0}
            
            # Count pending chunks (including those without embedding_status)
            pending_query = """
            SELECT VALUE COUNT(1) FROM c 
            WHERE (c.embedding_status = 'pending' OR NOT IS_DEFINED(c.embedding_status))
            """
            pending_result = list(self.container.query_items(
                query=pending_query,
                enable_cross_partition_query=True
            ))
            status_counts["pending"] = pending_result[0] if pending_result else 0
            
            # Count complete chunks
            complete_query = "SELECT VALUE COUNT(1) FROM c WHERE c.embedding_status = 'complete'"
            complete_result = list(self.container.query_items(
                query=complete_query,
                enable_cross_partition_query=True
            ))
            status_counts["complete"] = complete_result[0] if complete_result else 0
            
            # Count failed chunks
            failed_query = "SELECT VALUE COUNT(1) FROM c WHERE c.embedding_status = 'failed'"
            failed_result = list(self.container.query_items(
                query=failed_query,
                enable_cross_partition_query=True
            ))
            status_counts["failed"] = failed_result[0] if failed_result else 0
            
            # Get personality breakdown
            personality_stats = {}
            personalities_query = "SELECT DISTINCT VALUE c.personality_id FROM c"
            personalities = list(self.container.query_items(
                query=personalities_query,
                enable_cross_partition_query=True
            ))
            
            for personality_id in personalities:
                
                # Count pending for this personality
                pending_query = f"""
                SELECT VALUE COUNT(1) FROM c 
                WHERE c.personality_id = '{personality_id}' 
                AND (c.embedding_status = 'pending' OR NOT IS_DEFINED(c.embedding_status))
                """
                pending_count = list(self.container.query_items(
                    query=pending_query, 
                    enable_cross_partition_query=False,
                    partition_key=personality_id
                ))
                
                # Count complete for this personality
                complete_query = f"""
                SELECT VALUE COUNT(1) FROM c 
                WHERE c.personality_id = '{personality_id}' 
                AND c.embedding_status = 'complete'
                """
                complete_count = list(self.container.query_items(
                    query=complete_query, 
                    enable_cross_partition_query=False,
                    partition_key=personality_id
                ))
                
                personality_stats[personality_id] = {
                    "pending": pending_count[0] if pending_count else 0,
                    "complete": complete_count[0] if complete_count else 0
                }
            
            total_chunks = sum(status_counts.values())
            completion_percentage = (
                status_counts.get("complete", 0) / max(total_chunks, 1) * 100
            ) if total_chunks > 0 else 0
            
            return {
                "overall_status": status_counts,
                "personality_breakdown": personality_stats,
                "total_chunks": total_chunks,
                "completion_percentage": completion_percentage,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get embedding status: {e}")
            return {
                "error": str(e),
                "overall_status": {"pending": 0, "complete": 0, "failed": 0},
                "personality_breakdown": {},
                "total_chunks": 0,
                "completion_percentage": 0,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

# CLI interface for standalone execution
async def main():
    """Main function for CLI execution"""
    
    print("🚀 Vector Embedding Generator")
    print("=" * 50)
    
    generator = EmbeddingGenerator()
    
    try:
        # Check current status first
        status = await generator.get_embedding_status()
        print(f"\n📊 Current Status:")
        print(f"Total chunks: {status['total_chunks']:,}")
        print(f"Pending: {status['overall_status'].get('pending', 0):,}")
        print(f"Complete: {status['overall_status'].get('complete', 0):,}")
        print(f"Failed: {status['overall_status'].get('failed', 0):,}")
        print(f"Completion: {status['completion_percentage']:.1f}%")
        
        if status['overall_status'].get('pending', 0) == 0:
            print("\n✅ All embeddings already generated!")
            return
        
        print(f"\n🔄 Starting embedding generation...")
        
        # Generate embeddings
        summary = await generator.generate_embeddings_for_all_chunks()
        
        print("\n✅ Embedding Generation Complete!")
        print(f"Total chunks: {summary['statistics']['total_chunks']:,}")
        print(f"Successfully processed: {summary['statistics']['processed_chunks']:,}")
        print(f"Failed: {summary['statistics']['failed_chunks']:,}")
        print(f"Success rate: {summary['success_rate']:.1f}%")
        print(f"Processing time: {summary['processing_time_seconds']:.2f} seconds")
        print(f"Processing rate: {summary['processing_rate']:.1f} chunks/second")
        print(f"API calls made: {summary['statistics']['api_calls_made']:,}")
        print(f"Total tokens processed: {summary['statistics']['total_tokens_processed']:,}")
        
        print(f"\n📊 Personalities processed: {summary['statistics']['personalities_count']}")
        for personality in sorted(summary['personalities_processed']):
            print(f"  - {personality}")
    
    except Exception as e:
        print(f"❌ Embedding generation failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
