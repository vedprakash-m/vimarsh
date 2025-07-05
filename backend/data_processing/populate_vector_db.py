"""
Vector Database Population Script for Vimarsh
Populates Cosmos DB with sacred text embeddings and sets up vector search.
"""

import asyncio
import json
import logging
import os
import sys
from typing import List, Dict, Any, Optional
from pathlib import Path
import numpy as np
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VectorDatabasePopulator:
    """Populates vector database with sacred text embeddings."""
    
    def __init__(self):
        self.embedding_model = None
        self.cosmos_client = None
        self.database = None
        self.container = None
        
    def initialize_embedding_model(self):
        """Initialize the embedding model."""
        try:
            from sentence_transformers import SentenceTransformer
            model_name = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
            
            logger.info(f"Loading embedding model: {model_name}")
            self.embedding_model = SentenceTransformer(model_name)
            logger.info("✅ Embedding model loaded successfully")
            
        except ImportError:
            logger.error("❌ sentence-transformers not installed. Run: pip install sentence-transformers")
            sys.exit(1)
        except Exception as e:
            logger.error(f"❌ Failed to load embedding model: {e}")
            sys.exit(1)
    
    def initialize_cosmos_db(self):
        """Initialize Cosmos DB connection."""
        try:
            from azure.cosmos import CosmosClient, exceptions
            
            connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
            if not connection_string:
                logger.warning("⚠️ Cosmos DB connection string not set. Using local storage fallback.")
                return False
            
            self.cosmos_client = CosmosClient.from_connection_string(connection_string)
            
            # Get database and container
            database_name = os.getenv('AZURE_COSMOS_DATABASE_NAME', 'vimarsh')
            container_name = os.getenv('AZURE_COSMOS_CONTAINER_NAME', 'spiritual_texts')
            
            try:
                self.database = self.cosmos_client.get_database_client(database_name)
                self.container = self.database.get_container_client(container_name)
                logger.info("✅ Connected to Cosmos DB")
                return True
                
            except exceptions.CosmosResourceNotFoundError:
                logger.info("Creating database and container...")
                
                # Create database
                self.database = self.cosmos_client.create_database_if_not_exists(database_name)
                
                # Create container with vector indexing
                container_definition = {
                    'id': container_name,
                    'partitionKey': {'paths': ['/source'], 'kind': 'Hash'},
                    'vectorEmbeddingPolicy': {
                        'vectorEmbeddings': [
                            {
                                'path': '/embedding',
                                'dataType': 'float32',
                                'dimensions': int(os.getenv('VECTOR_DIMENSION', 384)),
                                'distanceFunction': 'cosine'
                            }
                        ]
                    },
                    'indexingPolicy': {
                        'vectorIndexes': [
                            {
                                'path': '/embedding',
                                'type': 'quantizedFlat'
                            }
                        ]
                    }
                }
                
                self.container = self.database.create_container_if_not_exists(
                    body=container_definition,
                    offer_throughput=400
                )
                
                logger.info("✅ Created Cosmos DB database and container with vector indexing")
                return True
                
        except ImportError:
            logger.warning("⚠️ Azure Cosmos DB SDK not installed. Run: pip install azure-cosmos")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to connect to Cosmos DB: {e}")
            return False
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a list of texts."""
        if not self.embedding_model:
            raise RuntimeError("Embedding model not initialized")
        
        logger.info(f"Generating embeddings for {len(texts)} texts...")
        embeddings = self.embedding_model.encode(texts, convert_to_numpy=True)
        logger.info(f"✅ Generated embeddings: {embeddings.shape}")
        return embeddings
    
    def load_sacred_texts(self) -> List[Dict[str, Any]]:
        """Load sacred texts from JSON file."""
        data_file = Path(__file__).parent / "data" / "sacred_texts_data.json"
        
        if not data_file.exists():
            logger.info("Sacred texts data file not found. Creating it...")
            # Import and run the sacred text loader
            from .sacred_text_loader import SacredTextDataLoader
            loader = SacredTextDataLoader()
            loader.load_all_sacred_texts()
            loader.save_to_json()
        
        logger.info(f"Loading sacred texts from: {data_file}")
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        texts = data.get('texts', [])
        logger.info(f"✅ Loaded {len(texts)} sacred text entries")
        return texts
    
    async def populate_cosmos_db(self, texts: List[Dict[str, Any]]) -> bool:
        """Populate Cosmos DB with texts and embeddings."""
        if not self.container:
            logger.error("❌ Cosmos DB container not available")
            return False
        
        logger.info("Populating Cosmos DB with sacred texts and embeddings...")
        
        # Prepare texts for embedding
        text_contents = [text['text'] for text in texts]
        
        # Generate embeddings in batches
        batch_size = 10
        all_embeddings = []
        
        for i in range(0, len(text_contents), batch_size):
            batch = text_contents[i:i + batch_size]
            batch_embeddings = self.generate_embeddings(batch)
            all_embeddings.extend(batch_embeddings.tolist())
            logger.info(f"Processed embeddings for batch {i//batch_size + 1}/{(len(text_contents) + batch_size - 1)//batch_size}")
        
        # Insert texts with embeddings into Cosmos DB
        successful_inserts = 0
        failed_inserts = 0
        
        for text, embedding in zip(texts, all_embeddings):
            try:
                # Prepare document for Cosmos DB
                document = {
                    **text,
                    'embedding': embedding,
                    'embedding_model': os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2'),
                    'populated_at': datetime.utcnow().isoformat(),
                    'ttl': -1  # Never expire
                }
                
                # Insert or upsert document
                self.container.upsert_item(body=document)
                successful_inserts += 1
                
                if successful_inserts % 5 == 0:
                    logger.info(f"Inserted {successful_inserts}/{len(texts)} documents...")
                    
            except Exception as e:
                logger.error(f"Failed to insert document {text.get('id', 'unknown')}: {e}")
                failed_inserts += 1
        
        logger.info(f"✅ Cosmos DB population completed: {successful_inserts} successful, {failed_inserts} failed")
        return failed_inserts == 0
    
    def save_to_local_storage(self, texts: List[Dict[str, Any]]) -> bool:
        """Save texts and embeddings to local storage as fallback."""
        logger.info("Saving to local vector storage (FAISS)...")
        
        try:
            import faiss
            import pickle
            
            # Prepare texts for embedding
            text_contents = [text['text'] for text in texts]
            embeddings = self.generate_embeddings(text_contents)
            
            # Create FAISS index
            dimension = embeddings.shape[1]
            index = faiss.IndexFlatIP(dimension)  # Inner product (cosine similarity)
            
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings)
            index.add(embeddings)
            
            # Save to local storage
            storage_dir = Path(__file__).parent / "vector_storage"
            storage_dir.mkdir(exist_ok=True)
            
            # Save FAISS index
            faiss.write_index(index, str(storage_dir / "sacred_texts.index"))
            
            # Save metadata
            metadata = {
                'texts': texts,
                'embeddings_shape': embeddings.shape,
                'model': os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2'),
                'created_at': datetime.utcnow().isoformat()
            }
            
            with open(storage_dir / "metadata.pkl", 'wb') as f:
                pickle.dump(metadata, f)
            
            logger.info(f"✅ Local vector storage saved: {len(texts)} texts, {embeddings.shape} embeddings")
            return True
            
        except ImportError:
            logger.error("❌ FAISS not installed. Run: pip install faiss-cpu")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to save to local storage: {e}")
            return False
    
    async def test_vector_search(self) -> bool:
        """Test vector search functionality."""
        logger.info("Testing vector search functionality...")
        
        test_query = "What is dharma and duty?"
        
        if self.container:
            # Test Cosmos DB vector search
            try:
                query_embedding = self.generate_embeddings([test_query])[0].tolist()
                
                # Cosmos DB vector search query
                query = """
                SELECT TOP 3 c.id, c.text, c.source, c.spiritual_theme,
                       VectorDistance(c.embedding, @query_vector) AS similarity_score
                FROM c
                WHERE c.content_type = 'sacred_text'
                ORDER BY VectorDistance(c.embedding, @query_vector)
                """
                
                results = list(self.container.query_items(
                    query=query,
                    parameters=[{"name": "@query_vector", "value": query_embedding}],
                    enable_cross_partition_query=True
                ))
                
                if results:
                    logger.info(f"✅ Cosmos DB vector search working: {len(results)} results")
                    for result in results[:2]:
                        logger.info(f"   - {result['source']}: {result['text'][:60]}... (score: {result['similarity_score']:.3f})")
                    return True
                else:
                    logger.warning("⚠️ Cosmos DB vector search returned no results")
                    return False
                    
            except Exception as e:
                logger.error(f"❌ Cosmos DB vector search failed: {e}")
                return False
        else:
            # Test local FAISS search
            try:
                import faiss
                import pickle
                
                storage_dir = Path(__file__).parent / "vector_storage"
                
                if not (storage_dir / "sacred_texts.index").exists():
                    logger.error("❌ Local vector index not found")
                    return False
                
                # Load index and metadata
                index = faiss.read_index(str(storage_dir / "sacred_texts.index"))
                
                with open(storage_dir / "metadata.pkl", 'rb') as f:
                    metadata = pickle.load(f)
                
                # Search
                query_embedding = self.generate_embeddings([test_query])
                faiss.normalize_L2(query_embedding)
                
                scores, indices = index.search(query_embedding, 3)
                
                if len(indices[0]) > 0:
                    logger.info(f"✅ Local vector search working: {len(indices[0])} results")
                    for i, idx in enumerate(indices[0][:2]):
                        if idx < len(metadata['texts']):
                            text = metadata['texts'][idx]
                            logger.info(f"   - {text['source']}: {text['text'][:60]}... (score: {scores[0][i]:.3f})")
                    return True
                else:
                    logger.warning("⚠️ Local vector search returned no results")
                    return False
                    
            except Exception as e:
                logger.error(f"❌ Local vector search failed: {e}")
                return False
    
    async def run_population(self) -> bool:
        """Run the complete vector database population process."""
        logger.info("🕉️ Starting Vector Database Population for Vimarsh")
        logger.info("=" * 60)
        
        # Initialize components
        self.initialize_embedding_model()
        cosmos_available = self.initialize_cosmos_db()
        
        # Load sacred texts
        texts = self.load_sacred_texts()
        if not texts:
            logger.error("❌ No sacred texts to process")
            return False
        
        # Populate database
        success = False
        
        if cosmos_available:
            logger.info("📊 Using Cosmos DB for vector storage")
            success = await self.populate_cosmos_db(texts)
        else:
            logger.info("💾 Using local FAISS storage")
            success = self.save_to_local_storage(texts)
        
        if not success:
            logger.error("❌ Database population failed")
            return False
        
        # Test vector search
        test_success = await self.test_vector_search()
        
        if test_success:
            logger.info("=" * 60)
            logger.info("✅ Vector Database Population Completed Successfully!")
            logger.info(f"📊 Populated {len(texts)} sacred text entries")
            logger.info("🔍 Vector search functionality verified")
            logger.info("🕉️ Ready for spiritual guidance queries")
            return True
        else:
            logger.error("❌ Vector search test failed")
            return False

async def main():
    """Main function for vector database population."""
    populator = VectorDatabasePopulator()
    success = await populator.run_population()
    
    if success:
        print("\n🎉 Vector database population completed successfully!")
        print("🕉️ Your spiritual guidance system is now ready with:")
        print("   ✓ Sacred text embeddings")
        print("   ✓ Vector similarity search")
        print("   ✓ Real-time context retrieval")
        sys.exit(0)
    else:
        print("\n❌ Vector database population failed!")
        print("Please check the logs and resolve any issues.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
