#!/usr/bin/env python3
"""
Cosmos DB Chunk Uploader Service
Uploads processed personality chunks to Cosmos DB before embedding generation
"""

import os
import json
import logging
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CosmosChunk:
    """Data structure for Cosmos DB chunk storage"""
    id: str
    personality_id: str
    source_id: str
    chunk_text: str
    chunk_index: int
    metadata: Dict[str, Any]
    quality_score: float
    relevance_score: float
    token_count: int
    embedding: Optional[List[float]] = None
    embedding_status: str = "pending"
    embedding_model: Optional[str] = None
    created_at: str = ""
    uploaded_at: str = ""
    embedding_generated_at: Optional[str] = None

    def to_cosmos_item(self) -> Dict[str, Any]:
        """Convert to Cosmos DB item format"""
        item = asdict(self)
        # Ensure required Cosmos DB fields
        item["id"] = self.id
        item["partition_key"] = self.personality_id  # Use personality as partition key (existing schema uses partition_key)
        if not item["created_at"]:
            item["created_at"] = datetime.now(timezone.utc).isoformat()
        if not item["uploaded_at"]:
            item["uploaded_at"] = datetime.now(timezone.utc).isoformat()
        return item

class CosmosChunkUploader:
    """Service for uploading processed chunks to Cosmos DB"""
    
    def __init__(self):
        self.cosmos_endpoint = os.getenv("COSMOS_ENDPOINT")
        self.cosmos_key = os.getenv("COSMOS_KEY") 
        self.database_name = "vimarsh-multi-personality"
        self.container_name = "personality_vectors"
        
        if not self.cosmos_endpoint or not self.cosmos_key:
            raise ValueError("COSMOS_ENDPOINT and COSMOS_KEY environment variables must be set")
        
        # Initialize Cosmos client
        self.client = cosmos_client.CosmosClient(
            self.cosmos_endpoint, 
            self.cosmos_key
        )
        self.database = self.client.get_database_client(self.database_name)
        
        # Ensure container exists
        self._ensure_container_exists()
        self.container = self.database.get_container_client(self.container_name)
        
        # Processing stats
        self.upload_stats = {
            "total_chunks": 0,
            "successful_uploads": 0,
            "failed_uploads": 0,
            "duplicate_skips": 0,
            "start_time": None,
            "end_time": None
        }
    
    def _ensure_container_exists(self):
        """Ensure the personality_vectors container exists, create if not"""
        try:
            # Try to get the container
            container_properties = self.database.get_container_client(self.container_name).read()
            logger.info(f"✅ Container '{self.container_name}' already exists")
        except exceptions.CosmosResourceNotFoundError:
            # Container doesn't exist, create it
            logger.info(f"📦 Creating container '{self.container_name}'...")
            
            # Define container properties
            container_definition = {
                'id': self.container_name,
                'partitionKey': {
                    'paths': ['/partitionKey'],
                    'kind': 'Hash'
                },
                'indexingPolicy': {
                    'indexingMode': 'consistent',
                    'automatic': True,
                    'includedPaths': [
                        {'path': '/*'}
                    ],
                    'excludedPaths': [
                        {'path': '/embedding/*'}  # Exclude embedding vectors from indexing
                    ]
                }
            }
            
            # Create container
            created_container = self.database.create_container(
                id=self.container_name,
                partition_key={'paths': ['/partition_key'], 'kind': 'Hash'}
                # No offer_throughput for serverless accounts
            )
            logger.info(f"✅ Created container '{self.container_name}' successfully")
        except Exception as e:
            logger.error(f"❌ Failed to ensure container exists: {e}")
            raise
    
    async def upload_all_personality_chunks(self) -> Dict[str, Any]:
        """Upload all processed personality chunks to Cosmos DB"""
        logger.info("🚀 Starting bulk upload of personality chunks to Cosmos DB")
        
        # Get processed chunks directory
        chunks_dir = os.path.join(
            os.path.dirname(__file__), "..", "..", "data", "sources", "processed_chunks"
        )
        
        if not os.path.exists(chunks_dir):
            raise FileNotFoundError(f"Processed chunks directory not found: {chunks_dir}")
        
        self.upload_stats["start_time"] = datetime.now(timezone.utc)
        
        # Process each personality chunk file
        chunk_files = [f for f in os.listdir(chunks_dir) if f.endswith("_chunks.json")]
        
        for chunk_file in chunk_files:
            personality_id = chunk_file.replace("_chunks.json", "")
            file_path = os.path.join(chunks_dir, chunk_file)
            
            logger.info(f"📚 Processing {personality_id} chunks from {chunk_file}")
            
            try:
                await self.upload_personality_chunks(personality_id, file_path)
            except Exception as e:
                logger.error(f"❌ Failed to upload {personality_id} chunks: {e}")
                self.upload_stats["failed_uploads"] += 1
        
        self.upload_stats["end_time"] = datetime.now(timezone.utc)
        processing_time = (self.upload_stats["end_time"] - self.upload_stats["start_time"]).total_seconds()
        
        # Generate summary report
        summary = {
            "upload_completed": True,
            "processing_time_seconds": processing_time,
            "statistics": self.upload_stats,
            "personalities_processed": len(chunk_files),
            "success_rate": (
                self.upload_stats["successful_uploads"] / 
                max(self.upload_stats["total_chunks"], 1) * 100
            )
        }
        
        logger.info(f"""
        ✅ Cosmos DB Upload Complete!
        - Total chunks: {self.upload_stats['total_chunks']:,}
        - Successfully uploaded: {self.upload_stats['successful_uploads']:,}
        - Failed uploads: {self.upload_stats['failed_uploads']:,}
        - Duplicates skipped: {self.upload_stats['duplicate_skips']:,}
        - Processing time: {processing_time:.2f}s
        - Success rate: {summary['success_rate']:.1f}%
        """)
        
        return summary
    
    async def upload_personality_chunks(self, personality_id: str, file_path: str):
        """Upload chunks for a specific personality"""
        
        # Load processed chunks
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        chunks = data.get("chunks", [])
        logger.info(f"📊 Found {len(chunks)} chunks for {personality_id}")
        
        # Upload chunks in batches
        batch_size = 25  # Cosmos DB batch size limit
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            await self.upload_batch(batch, personality_id)
    
    async def upload_batch(self, chunks_batch: List[Dict], personality_id: str):
        """Upload a batch of chunks to Cosmos DB"""
        
        for chunk_data in chunks_batch:
            try:
                # Convert to CosmosChunk
                cosmos_chunk = CosmosChunk(
                    id=chunk_data["id"],
                    personality_id=chunk_data["personality_id"],
                    source_id=chunk_data["source_id"],
                    chunk_text=chunk_data["chunk_text"],
                    chunk_index=chunk_data["chunk_index"],
                    metadata=chunk_data["metadata"],
                    quality_score=chunk_data["quality_score"],
                    relevance_score=chunk_data["relevance_score"],
                    token_count=chunk_data["token_count"],
                    created_at=chunk_data["created_at"]
                )
                
                # Upload to Cosmos DB
                cosmos_item = cosmos_chunk.to_cosmos_item()
                
                # Check if chunk already exists
                if await self.chunk_exists(cosmos_chunk.id, personality_id):
                    logger.debug(f"⏭️ Chunk {cosmos_chunk.id} already exists, skipping")
                    self.upload_stats["duplicate_skips"] += 1
                    continue
                
                # Upload to Cosmos DB
                self.container.create_item(body=cosmos_item)
                self.upload_stats["successful_uploads"] += 1
                
                if self.upload_stats["successful_uploads"] % 1000 == 0:
                    logger.info(f"📈 Uploaded {self.upload_stats['successful_uploads']:,} chunks so far...")
                
            except Exception as e:
                logger.error(f"❌ Failed to upload chunk {chunk_data.get('id', 'unknown')}: {e}")
                self.upload_stats["failed_uploads"] += 1
            
            self.upload_stats["total_chunks"] += 1
    
    async def chunk_exists(self, chunk_id: str, personality_id: str) -> bool:
        """Check if a chunk already exists in Cosmos DB"""
        try:
            query = f"SELECT c.id FROM c WHERE c.id = '{chunk_id}' AND c.partition_key = '{personality_id}'"
            items = list(self.container.query_items(
                query=query,
                enable_cross_partition_query=False
            ))
            return len(items) > 0
        except Exception:
            return False
    
    async def get_upload_status(self) -> Dict[str, Any]:
        """Get current upload status and statistics"""
        
        # Query chunk counts by personality
        personality_stats = {}
        
        try:
            # Get unique personalities
            query = "SELECT DISTINCT c.personality_id FROM c"
            personalities = list(self.container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            
            for personality in personalities:
                personality_id = personality["personality_id"]
                
                # Count chunks for this personality
                count_query = f"SELECT VALUE COUNT(1) FROM c WHERE c.personality_id = '{personality_id}'"
                count_result = list(self.container.query_items(
                    query=count_query,
                    enable_cross_partition_query=False
                ))
                
                chunk_count = count_result[0] if count_result else 0
                
                # Count pending embeddings
                pending_query = f"SELECT VALUE COUNT(1) FROM c WHERE c.personality_id = '{personality_id}' AND c.embedding_status = 'pending'"
                pending_result = list(self.container.query_items(
                    query=pending_query,
                    enable_cross_partition_query=False
                ))
                
                pending_count = pending_result[0] if pending_result else 0
                
                personality_stats[personality_id] = {
                    "total_chunks": chunk_count,
                    "embeddings_pending": pending_count,
                    "embeddings_complete": chunk_count - pending_count
                }
        
        except Exception as e:
            logger.error(f"Error getting upload status: {e}")
            personality_stats = {}
        
        return {
            "upload_statistics": self.upload_stats,
            "personality_breakdown": personality_stats,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

# CLI interface for standalone execution
async def main():
    """Main function for CLI execution"""
    
    print("🚀 Cosmos DB Chunk Uploader")
    print("=" * 50)
    
    uploader = CosmosChunkUploader()
    
    try:
        # Upload all chunks
        summary = await uploader.upload_all_personality_chunks()
        
        print("\n✅ Upload Summary:")
        print(f"Total personalities: {summary['personalities_processed']}")
        print(f"Total chunks: {summary['statistics']['total_chunks']:,}")
        print(f"Successfully uploaded: {summary['statistics']['successful_uploads']:,}")
        print(f"Failed uploads: {summary['statistics']['failed_uploads']:,}")
        print(f"Success rate: {summary['success_rate']:.1f}%")
        print(f"Processing time: {summary['processing_time_seconds']:.2f} seconds")
        
        # Get final status
        status = await uploader.get_upload_status()
        print(f"\n📊 Cosmos DB Status:")
        for personality_id, stats in status["personality_breakdown"].items():
            print(f"  {personality_id}: {stats['total_chunks']} chunks ({stats['embeddings_pending']} pending embeddings)")
    
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
