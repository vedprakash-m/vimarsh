#!/usr/bin/env python3
"""
Azure Cosmos DB Vector Storage Integration
Handles embedding generation and vector storage for spiritual books
"""

import json
import os
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass
from datetime import datetime

# Azure and OpenAI imports
try:
    import openai
    from azure.cosmos import CosmosClient, PartitionKey
    from azure.cosmos.exceptions import CosmosResourceExistsError, CosmosResourceNotFoundError
    import numpy as np
except ImportError as e:
    print(f"Missing dependencies: {e}")
    print("Install with: pip install azure-cosmos openai numpy")
    exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class EmbeddingConfig:
    """Configuration for embedding generation."""
    model: str = "text-embedding-3-small"
    dimensions: int = 1536
    batch_size: int = 100
    max_tokens: int = 8000

@dataclass
class CosmosConfig:
    """Configuration for Cosmos DB."""
    endpoint: str
    key: str
    database_name: str = "vimarsh"
    container_name: str = "spiritual_texts"
    partition_key: str = "/book_id"

class SpiritualTextsVectorStore:
    """Manages vector storage for spiritual texts in Azure Cosmos DB."""
    
    def __init__(self, cosmos_config: CosmosConfig, embedding_config: EmbeddingConfig):
        self.cosmos_config = cosmos_config
        self.embedding_config = embedding_config
        
        # Initialize Cosmos DB client
        self.cosmos_client = CosmosClient(cosmos_config.endpoint, cosmos_config.key)
        self.database = None
        self.container = None
        
        # Initialize OpenAI client
        openai.api_key = os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
    
    async def initialize_cosmos_db(self):
        """Initialize Cosmos DB database and container."""
        try:
            # Create database
            self.database = self.cosmos_client.create_database_if_not_exists(
                id=self.cosmos_config.database_name
            )
            logger.info(f"Database '{self.cosmos_config.database_name}' ready")
            
            # Create container with vector policy
            container_definition = {
                "id": self.cosmos_config.container_name,
                "partitionKey": PartitionKey(path=self.cosmos_config.partition_key),
                "vectorEmbeddingPolicy": {
                    "vectorEmbeddings": [
                        {
                            "path": "/embedding",
                            "dataType": "float32",
                            "distanceFunction": "cosine",
                            "dimensions": self.embedding_config.dimensions
                        }
                    ]
                },
                "indexingPolicy": {
                    "vectorIndexes": [
                        {
                            "path": "/embedding",
                            "type": "quantizedFlat"
                        }
                    ]
                }
            }
            
            self.container = self.database.create_container_if_not_exists(
                body=container_definition,
                offer_throughput=1000  # Start with 1000 RU/s
            )
            logger.info(f"Container '{self.cosmos_config.container_name}' ready with vector support")
            
        except Exception as e:
            logger.error(f"Error initializing Cosmos DB: {e}")
            raise
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a text using OpenAI."""
        try:
            # Truncate text if too long
            if len(text) > self.embedding_config.max_tokens * 4:  # Rough estimate
                text = text[:self.embedding_config.max_tokens * 4]
            
            response = openai.embeddings.create(
                model=self.embedding_config.model,
                input=text,
                dimensions=self.embedding_config.dimensions
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        embeddings = []
        
        for i in range(0, len(texts), self.embedding_config.batch_size):
            batch = texts[i:i + self.embedding_config.batch_size]
            logger.info(f"Generating embeddings for batch {i//self.embedding_config.batch_size + 1}")
            
            try:
                response = openai.embeddings.create(
                    model=self.embedding_config.model,
                    input=batch,
                    dimensions=self.embedding_config.dimensions
                )
                
                batch_embeddings = [data.embedding for data in response.data]
                embeddings.extend(batch_embeddings)
                
                # Small delay to avoid rate limits
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error in batch embedding generation: {e}")
                # Generate individually as fallback
                for text in batch:
                    try:
                        embedding = self.generate_embedding(text)
                        embeddings.append(embedding)
                    except:
                        logger.warning(f"Failed to generate embedding for text: {text[:100]}...")
                        embeddings.append([0.0] * self.embedding_config.dimensions)
        
        return embeddings
    
    def prepare_document(self, chunk: Dict[str, Any], embedding: List[float]) -> Dict[str, Any]:
        """Prepare a document for Cosmos DB storage."""
        # Extract book_id from chunk id
        book_id = chunk["id"].split("_")[0]
        
        document = {
            "id": chunk["id"],
            "book_id": book_id,
            "book_title": chunk["book"],
            "chapter": chunk.get("chapter"),
            "verse": chunk.get("verse"),
            "content_type": chunk.get("content_type"),
            "content": chunk["content"],
            "embedding": embedding,
            "metadata": {
                **chunk.get("metadata", {}),
                "embedding_model": self.embedding_config.model,
                "embedding_dimensions": self.embedding_config.dimensions,
                "processed_date": datetime.now().isoformat(),
                "has_sanskrit": chunk.get("sanskrit", "") != "",
                "has_translation": chunk.get("translation", "") != "",
                "has_purport": chunk.get("purport", "") != "",
                "has_synonyms": chunk.get("synonyms", "") != ""
            }
        }
        
        # Add optional fields if present
        optional_fields = ["sanskrit", "translation", "purport", "synonyms"]
        for field in optional_fields:
            if field in chunk and chunk[field]:
                document[field] = chunk[field]
        
        return document
    
    async def store_documents(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Store documents in Cosmos DB."""
        stored_count = 0
        failed_count = 0
        
        for doc in documents:
            try:
                self.container.create_item(body=doc)
                stored_count += 1
                
                if stored_count % 100 == 0:
                    logger.info(f"Stored {stored_count} documents...")
                    
            except CosmosResourceExistsError:
                # Document already exists, try to update
                try:
                    self.container.replace_item(item=doc["id"], body=doc)
                    stored_count += 1
                    logger.info(f"Updated existing document: {doc['id']}")
                except Exception as e:
                    logger.error(f"Failed to update document {doc['id']}: {e}")
                    failed_count += 1
                    
            except Exception as e:
                logger.error(f"Failed to store document {doc['id']}: {e}")
                failed_count += 1
        
        logger.info(f"Storage complete: {stored_count} stored, {failed_count} failed")
        return {"stored": stored_count, "failed": failed_count}
    
    async def process_book_file(self, jsonl_file: Path) -> Dict[str, Any]:
        """Process a single JSONL file and store in Cosmos DB."""
        logger.info(f"Processing {jsonl_file.name}...")
        
        # Load chunks
        chunks = []
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    chunks.append(json.loads(line))
        
        logger.info(f"Loaded {len(chunks)} chunks from {jsonl_file.name}")
        
        # Extract texts for embedding
        texts = [chunk["content"] for chunk in chunks]
        
        # Generate embeddings
        logger.info("Generating embeddings...")
        embeddings = await self.generate_embeddings_batch(texts)
        
        # Prepare documents
        documents = []
        for chunk, embedding in zip(chunks, embeddings):
            doc = self.prepare_document(chunk, embedding)
            documents.append(doc)
        
        # Store in Cosmos DB
        logger.info("Storing documents in Cosmos DB...")
        result = await self.store_documents(documents)
        
        return {
            "file": jsonl_file.name,
            "chunks_processed": len(chunks),
            "embeddings_generated": len(embeddings),
            **result
        }
    
    async def vector_search(self, query_text: str, top_k: int = 5, book_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Perform vector similarity search."""
        # Generate query embedding
        query_embedding = self.generate_embedding(query_text)
        
        # Build SQL query
        sql = """
        SELECT TOP @top_k c.id, c.book_title, c.verse, c.content, c.content_type,
               VectorDistance(c.embedding, @query_embedding) AS similarity_score
        FROM c
        """
        
        parameters = [
            {"name": "@top_k", "value": top_k},
            {"name": "@query_embedding", "value": query_embedding}
        ]
        
        if book_filter:
            sql += " WHERE c.book_id = @book_filter"
            parameters.append({"name": "@book_filter", "value": book_filter})
        
        sql += " ORDER BY VectorDistance(c.embedding, @query_embedding)"
        
        # Execute query
        try:
            results = list(self.container.query_items(
                query=sql,
                parameters=parameters,
                enable_cross_partition_query=True
            ))
            
            return results
            
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []

class SpiritualBooksVectorManager:
    """High-level manager for spiritual books vector operations."""
    
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.sources_dir = self.base_dir / "data" / "sources"
        self.registry_file = self.sources_dir / "books_registry.json"
        
        # Load configurations from environment
        cosmos_config = CosmosConfig(
            endpoint=os.getenv("AZURE_COSMOS_ENDPOINT", ""),
            key=os.getenv("AZURE_COSMOS_KEY", "")
        )
        
        embedding_config = EmbeddingConfig()
        
        self.vector_store = SpiritualTextsVectorStore(cosmos_config, embedding_config)
    
    def load_registry(self) -> Dict[str, Any]:
        """Load the books registry."""
        with open(self.registry_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def update_registry_vector_status(self, book_id: str, vector_status: Dict[str, Any]):
        """Update registry with vector storage status."""
        registry = self.load_registry()
        
        if book_id in registry["books"]:
            registry["books"][book_id].update({
                "vector_stored": True,
                "vector_storage_date": datetime.now().isoformat(),
                "embedding_model": self.vector_store.embedding_config.model,
                "cosmos_db_status": vector_status
            })
            
            with open(self.registry_file, 'w', encoding='utf-8') as f:
                json.dump(registry, f, indent=2, ensure_ascii=False)
    
    async def process_all_books(self):
        """Process all books and store in vector database."""
        logger.info("🚀 Starting vector storage pipeline...")
        
        # Initialize Cosmos DB
        await self.vector_store.initialize_cosmos_db()
        
        # Find all JSONL files
        jsonl_files = list(self.sources_dir.glob("*_clean.jsonl"))
        
        if not jsonl_files:
            logger.error("No clean JSONL files found!")
            return
        
        total_results = []
        
        for jsonl_file in jsonl_files:
            try:
                result = await self.vector_store.process_book_file(jsonl_file)
                total_results.append(result)
                
                # Update registry
                book_id = jsonl_file.stem.replace("_clean", "")
                self.update_registry_vector_status(book_id, result)
                
                logger.info(f"✅ {jsonl_file.name} processed successfully")
                
            except Exception as e:
                logger.error(f"❌ Failed to process {jsonl_file.name}: {e}")
        
        # Summary
        total_chunks = sum(r["chunks_processed"] for r in total_results)
        total_stored = sum(r["stored"] for r in total_results)
        
        logger.info(f"\n🎉 Vector storage complete!")
        logger.info(f"📊 Total chunks: {total_chunks}")
        logger.info(f"📊 Successfully stored: {total_stored}")
        logger.info(f"📊 Files processed: {len(total_results)}")

async def main():
    """Main entry point for vector storage."""
    base_dir = "/Users/vedprakashmishra/vimarsh"
    
    # Check environment variables
    required_env = ["AZURE_COSMOS_ENDPOINT", "AZURE_COSMOS_KEY", "OPENAI_API_KEY"]
    missing_env = [var for var in required_env if not os.getenv(var)]
    
    if missing_env:
        logger.error(f"Missing environment variables: {missing_env}")
        logger.info("Please set:")
        for var in missing_env:
            logger.info(f"  export {var}=your_value_here")
        return
    
    manager = SpiritualBooksVectorManager(base_dir)
    await manager.process_all_books()

if __name__ == "__main__":
    asyncio.run(main())
