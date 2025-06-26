#!/usr/bin/env python3
"""
Azure Cosmos DB (MongoDB vCore) Integration for Vimarsh
Handles embeddings generation and upload to vector database
"""

import json
import os
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import logging
from dataclasses import dataclass, asdict
import hashlib

# Third-party imports
import openai
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
import numpy as np
from tenacity import retry, stop_after_attempt, wait_exponential

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class EmbeddingChunk:
    """Represents a chunk with its embedding for Cosmos DB storage."""
    id: str
    scripture: str
    chapter: int
    verse: str
    content_type: str
    content: str
    embedding: List[float]
    metadata: Dict[str, Any]
    scripture_id: str
    created_at: str
    hash: str

class CosmosDBVectorStore:
    """Manages vector embeddings in Azure Cosmos DB for MongoDB vCore."""
    
    def __init__(self, connection_string: str, database_name: str = "vimarsh", 
                 collection_name: str = "spiritual_embeddings"):
        """
        Initialize Cosmos DB connection.
        
        Args:
            connection_string: Azure Cosmos DB connection string
            database_name: Database name
            collection_name: Collection name for embeddings
        """
        self.connection_string = connection_string
        self.database_name = database_name
        self.collection_name = collection_name
        self.client: Optional[MongoClient] = None
        self.db: Optional[Database] = None
        self.collection: Optional[Collection] = None
        
    def connect(self):
        """Establish connection to Cosmos DB."""
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client[self.database_name]
            self.collection = self.db[self.collection_name]
            
            # Test connection
            self.client.admin.command('ping')
            logger.info(f"✅ Connected to Cosmos DB: {self.database_name}.{self.collection_name}")
            
            # Create vector search index if it doesn't exist
            self._ensure_vector_index()
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Cosmos DB: {e}")
            raise
    
    def _ensure_vector_index(self):
        """Create vector search index for embeddings."""
        try:
            # Check if index exists
            indexes = list(self.collection.list_indexes())
            vector_index_exists = any(
                idx.get('name') == 'vector_index' for idx in indexes
            )
            
            if not vector_index_exists:
                # Create vector search index
                index_definition = {
                    "embedding": "cosmosSearch"
                }
                
                self.collection.create_index(
                    [("embedding", "cosmosSearch")],
                    name="vector_index",
                    cosmosSearchOptions={
                        "kind": "vector-ivf",
                        "numLists": 1,
                        "similarity": "cosine",
                        "dimensions": 1536  # OpenAI ada-002 embedding dimension
                    }
                )
                logger.info("✅ Created vector search index")
            else:
                logger.info("✅ Vector search index already exists")
                
        except Exception as e:
            logger.warning(f"⚠️ Could not create vector index: {e}")
    
    def close(self):
        """Close database connection."""
        if self.client:
            self.client.close()
            logger.info("✅ Closed Cosmos DB connection")
    
    def insert_embeddings(self, embeddings: List[EmbeddingChunk]) -> int:
        """
        Insert embeddings into Cosmos DB.
        
        Args:
            embeddings: List of embedding chunks to insert
            
        Returns:
            Number of successfully inserted documents
        """
        if not self.collection:
            raise ValueError("Not connected to database")
        
        documents = [asdict(chunk) for chunk in embeddings]
        
        try:
            result = self.collection.insert_many(documents)
            inserted_count = len(result.inserted_ids)
            logger.info(f"✅ Inserted {inserted_count} embeddings to Cosmos DB")
            return inserted_count
            
        except Exception as e:
            logger.error(f"❌ Failed to insert embeddings: {e}")
            raise
    
    def search_similar(self, query_embedding: List[float], top_k: int = 5, 
                      scripture_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for similar embeddings using vector search.
        
        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            scripture_filter: Optional filter by scripture_id
            
        Returns:
            List of similar documents with scores
        """
        if not self.collection:
            raise ValueError("Not connected to database")
        
        # Build aggregation pipeline for vector search
        pipeline = [
            {
                "$search": {
                    "cosmosSearch": {
                        "vector": query_embedding,
                        "path": "embedding",
                        "k": top_k
                    }
                }
            }
        ]
        
        # Add scripture filter if specified
        if scripture_filter:
            pipeline.append({
                "$match": {"scripture_id": scripture_filter}
            })
        
        # Add score and limit
        pipeline.extend([
            {"$addFields": {"score": {"$meta": "searchScore"}}},
            {"$limit": top_k}
        ])
        
        try:
            results = list(self.collection.aggregate(pipeline))
            logger.info(f"✅ Found {len(results)} similar embeddings")
            return results
            
        except Exception as e:
            logger.error(f"❌ Vector search failed: {e}")
            raise
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the embeddings collection."""
        if not self.collection:
            raise ValueError("Not connected to database")
        
        try:
            stats = self.db.command("collStats", self.collection_name)
            
            # Get book distribution
            book_distribution = list(self.collection.aggregate([
                {"$group": {"_id": "$scripture_id", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]))
            
            # Get content type distribution
            content_type_dist = list(self.collection.aggregate([
                {"$group": {"_id": "$content_type", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]))
            
            return {
                "total_documents": stats.get("count", 0),
                "storage_size": stats.get("storageSize", 0),
                "index_size": stats.get("totalIndexSize", 0),
                "book_distribution": book_distribution,
                "content_type_distribution": content_type_dist
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get collection stats: {e}")
            raise

class OpenAIEmbeddings:
    """Handles OpenAI embeddings generation."""
    
    def __init__(self, api_key: str, model: str = "text-embedding-ada-002"):
        """
        Initialize OpenAI embeddings.
        
        Args:
            api_key: OpenAI API key
            model: Embedding model to use
        """
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.max_tokens = 8192  # Max tokens for ada-002
        
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text with retry logic.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        try:
            # Truncate text if too long
            if len(text) > self.max_tokens * 4:  # Rough estimate
                text = text[:self.max_tokens * 4]
            
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"❌ Failed to generate embedding: {e}")
            raise
    
    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batches.
        
        Args:
            texts: List of texts to embed
            batch_size: Number of texts per batch
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            try:
                response = self.client.embeddings.create(
                    model=self.model,
                    input=batch
                )
                
                batch_embeddings = [data.embedding for data in response.data]
                embeddings.extend(batch_embeddings)
                
                logger.info(f"✅ Generated embeddings for batch {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size}")
                
            except Exception as e:
                logger.error(f"❌ Failed to generate embeddings for batch: {e}")
                raise
        
        return embeddings

class SpiritualBooksVectorizer:
    """Main class for processing spiritual books and uploading to vector database."""
    
    def __init__(self, base_dir: str, openai_api_key: str, cosmos_connection_string: str):
        """
        Initialize the vectorizer.
        
        Args:
            base_dir: Base directory path
            openai_api_key: OpenAI API key
            cosmos_connection_string: Cosmos DB connection string
        """
        self.base_dir = Path(base_dir)
        self.sources_dir = self.base_dir / "data" / "sources"
        self.registry_file = self.sources_dir / "scriptures_registry.json"
        
        # Initialize services
        self.embeddings = OpenAIEmbeddings(openai_api_key)
        self.vector_store = CosmosDBVectorStore(cosmos_connection_string)
        
    def load_registry(self) -> Dict[str, Any]:
        """Load the books registry."""
        if not self.registry_file.exists():
            raise FileNotFoundError(f"Registry file not found: {self.registry_file}")
        
        with open(self.registry_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_registry(self, registry: Dict[str, Any]):
        """Save the books registry."""
        registry["last_updated"] = datetime.now().isoformat()
        with open(self.registry_file, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)
    
    def load_processed_chunks(self, scripture_id: str) -> List[Dict[str, Any]]:
        """Load processed chunks from JSONL file."""
        registry = self.load_registry()
        scripture_info = registry["scriptures"].get(scripture_id)
        
        if not scripture_info:
            raise ValueError(f"Scripture {scripture_id} not found in registry")
        
        output_file = scripture_info.get("output_file")
        if not output_file:
            raise ValueError(f"No output file found for scripture {scripture_id}")
        
        chunks = []
        with open(output_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    chunks.append(json.loads(line))
        
        logger.info(f"✅ Loaded {len(chunks)} chunks for {scripture_id}")
        return chunks
    
    def create_embedding_chunk(self, chunk: Dict[str, Any], scripture_id: str, 
                              embedding: List[float]) -> EmbeddingChunk:
        """Create an EmbeddingChunk from processed chunk data."""
        # Create a hash for deduplication
        content_hash = hashlib.sha256(chunk["content"].encode('utf-8')).hexdigest()[:16]
        
        return EmbeddingChunk(
            id=chunk["id"],
            scripture=chunk["scripture"],
            chapter=chunk["chapter"],
            verse=chunk["verse"],
            content_type=chunk["content_type"],
            content=chunk["content"],
            embedding=embedding,
            metadata=chunk["metadata"],
            scripture_id=scripture_id,
            created_at=datetime.now().isoformat(),
            hash=content_hash
        )
    
    def process_scripture_embeddings(self, scripture_id: str) -> Tuple[int, int]:
        """
        Process embeddings for a single scripture.
        
        Args:
            scripture_id: Scripture identifier
            
        Returns:
            Tuple of (processed_count, uploaded_count)
        """
        logger.info(f"🔄 Processing embeddings for {scripture_id}")
        
        # Load chunks
        chunks = self.load_processed_chunks(scripture_id)
        
        if not chunks:
            logger.warning(f"No chunks found for {scripture_id}")
            return 0, 0
        
        # Generate embeddings
        texts = [chunk["content"] for chunk in chunks]
        embeddings = self.embeddings.generate_embeddings_batch(texts)
        
        # Create embedding chunks
        embedding_chunks = []
        for chunk, embedding in zip(chunks, embeddings):
            embedding_chunk = self.create_embedding_chunk(chunk, scripture_id, embedding)
            embedding_chunks.append(embedding_chunk)
        
        # Upload to Cosmos DB
        uploaded_count = self.vector_store.insert_embeddings(embedding_chunks)
        
        return len(chunks), uploaded_count
    
    def process_all_scriptures(self) -> Dict[str, Any]:
        """Process embeddings for all scriptures in the registry."""
        logger.info("🚀 Starting vector embeddings processing...")
        
        # Connect to Cosmos DB
        self.vector_store.connect()
        
        try:
            registry = self.load_registry()
            results = {}
            total_processed = 0
            total_uploaded = 0
            
            for scripture_id, scripture_info in registry["scriptures"].items():
                if scripture_info.get("status") != "success":
                    logger.warning(f"⚠️ Skipping {scripture_id}: status is {scripture_info.get('status')}")
                    continue
                
                try:
                    processed, uploaded = self.process_scripture_embeddings(scripture_id)
                    results[scripture_id] = {
                        "status": "success",
                        "processed": processed,
                        "uploaded": uploaded,
                        "timestamp": datetime.now().isoformat()
                    }
                    total_processed += processed
                    total_uploaded += uploaded
                    
                    # Update registry
                    registry["books"][book_id]["embeddings_generated"] = True
                    registry["books"][book_id]["embeddings_uploaded"] = True
                    registry["books"][book_id]["vectors_count"] = uploaded
                    registry["books"][book_id]["vectorized_date"] = datetime.now().isoformat()
                    
                    logger.info(f"✅ {book_id}: {processed} processed, {uploaded} uploaded")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to process {book_id}: {e}")
                    results[book_id] = {
                        "status": "error",
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    }
            
            # Save updated registry
            self.save_registry(registry)
            
            # Get collection stats
            stats = self.vector_store.get_collection_stats()
            
            return {
                "total_books_processed": len([r for r in results.values() if r["status"] == "success"]),
                "total_chunks_processed": total_processed,
                "total_vectors_uploaded": total_uploaded,
                "collection_stats": stats,
                "book_results": results,
                "registry_updated": True
            }
            
        finally:
            self.vector_store.close()
    
    def search_similar_content(self, query: str, top_k: int = 5, 
                             book_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for similar content using vector search.
        
        Args:
            query: Search query
            top_k: Number of results to return
            book_filter: Optional filter by book_id
            
        Returns:
            List of similar content with scores
        """
        # Generate query embedding
        query_embedding = self.embeddings.generate_embedding(query)
        
        # Connect and search
        self.vector_store.connect()
        
        try:
            results = self.vector_store.search_similar(
                query_embedding, top_k, book_filter
            )
            return results
            
        finally:
            self.vector_store.close()

def main():
    """Main entry point for vector processing."""
    # Configuration
    base_dir = "/Users/vedprakashmishra/vimarsh"
    
    # Get API keys from environment
    openai_api_key = os.getenv("OPENAI_API_KEY")
    cosmos_connection_string = os.getenv("COSMOS_DB_CONNECTION_STRING")
    
    if not openai_api_key:
        logger.error("❌ OPENAI_API_KEY environment variable not set")
        return
    
    if not cosmos_connection_string:
        logger.error("❌ COSMOS_DB_CONNECTION_STRING environment variable not set")
        return
    
    # Initialize vectorizer
    vectorizer = SpiritualBooksVectorizer(
        base_dir=base_dir,
        openai_api_key=openai_api_key,
        cosmos_connection_string=cosmos_connection_string
    )
    
    try:
        # Process all books
        results = vectorizer.process_all_books()
        
        # Print summary
        print("\n" + "="*60)
        print("🎯 VECTOR PROCESSING SUMMARY")
        print("="*60)
        print(f"Books processed: {results['total_books_processed']}")
        print(f"Chunks processed: {results['total_chunks_processed']}")
        print(f"Vectors uploaded: {results['total_vectors_uploaded']}")
        print(f"Total documents in DB: {results['collection_stats']['total_documents']}")
        
        print("\nBook Results:")
        for book_id, result in results['book_results'].items():
            if result['status'] == 'success':
                print(f"  ✅ {book_id}: {result['processed']} chunks → {result['uploaded']} vectors")
            else:
                print(f"  ❌ {book_id}: {result['error']}")
        
        print("\nCollection Stats:")
        stats = results['collection_stats']
        print(f"  Storage size: {stats['storage_size']} bytes")
        print(f"  Index size: {stats['index_size']} bytes")
        
        print("\nBook Distribution:")
        for book_dist in stats['book_distribution']:
            print(f"  {book_dist['_id']}: {book_dist['count']} vectors")
        
        print("\n🎉 Vector processing complete!")
        print("📝 Next steps:")
        print("   1. Test vector search functionality")
        print("   2. Integrate with RAG pipeline")
        print("   3. Set up admin UI for book registry management")
        
    except Exception as e:
        logger.error(f"❌ Vector processing failed: {e}")
        raise

if __name__ == "__main__":
    main()
