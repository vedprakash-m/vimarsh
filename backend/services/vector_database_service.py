"""
Multi-Personality Vector Database Service for Vimarsh

Manages vector embeddings and semantic search across multiple spiritual personalities
with proper admin panel integration and database reorganization.
"""

import os
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum
import numpy as np

logger = logging.getLogger(__name__)

class PersonalityType(Enum):
    """Supported personality types"""
    KRISHNA = "krishna"
    BUDDHA = "buddha"
    JESUS = "jesus"
    EINSTEIN = "einstein"
    LINCOLN = "lincoln"
    MARCUS_AURELIUS = "marcus_aurelius"
    RUMI = "rumi"
    LAO_TZU = "lao_tzu"
    NEWTON = "newton"
    CHANAKYA = "chanakya"
    CONFUCIUS = "confucius"
    TESLA = "tesla"

class ContentType(Enum):
    """Types of spiritual content"""
    VERSE = "verse"
    COMMENTARY = "commentary"
    COMPLETE = "complete"
    TEACHING = "teaching"
    QUOTE = "quote"
    STORY = "story"

@dataclass
class VectorDocument:
    """Enhanced document structure for multi-personality vector storage"""
    id: str
    content: str
    personality: PersonalityType
    content_type: ContentType
    source: str
    title: Optional[str] = None
    chapter: Optional[str] = None
    verse: Optional[str] = None
    sanskrit: Optional[str] = None
    translation: Optional[str] = None
    citation: Optional[str] = None
    category: str = "general"
    language: str = "English"
    embedding: Optional[List[float]] = None
    embedding_model: str = "all-MiniLM-L6-v2"
    relevance_score: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SearchResult:
    """Vector search result with relevance scoring"""
    document: VectorDocument
    relevance_score: float
    personality_match: bool
    content_type_match: bool
    query_embedding: Optional[List[float]] = None

@dataclass
class DatabaseStats:
    """Database statistics for admin panel"""
    total_documents: int
    documents_by_personality: Dict[str, int]
    documents_by_content_type: Dict[str, int]
    documents_by_source: Dict[str, int]
    avg_embedding_similarity: float
    last_updated: str
    storage_size_mb: float
    total_embeddings_generated: int
    failed_embeddings: int

class VectorDatabaseService:
    """Enhanced vector database service for multi-personality system"""
    
    def __init__(self):
        self.cosmos_client = None
        self.database = None
        self.container = None
        self.embedding_model = None
        self.local_cache: Dict[str, VectorDocument] = {}
        self.stats: Optional[DatabaseStats] = None
        
        # Initialize components
        self._initialize_cosmos_db()
        self._initialize_embedding_model()
    
    def _initialize_cosmos_db(self):
        """Initialize Cosmos DB connection with enhanced schema"""
        try:
            from azure.cosmos import CosmosClient, exceptions
            
            connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
            if not connection_string:
                logger.warning("⚠️ Cosmos DB connection string not configured")
                return
            
            self.cosmos_client = CosmosClient.from_connection_string(connection_string)
            
            # Use dedicated database for multi-personality system
            database_name = os.getenv('AZURE_COSMOS_DATABASE_NAME', 'vimarsh-multi-personality')
            container_name = os.getenv('AZURE_COSMOS_CONTAINER_NAME', 'spiritual-vectors')
            
            try:
                self.database = self.cosmos_client.get_database_client(database_name)
                self.container = self.database.get_container_client(container_name)
                logger.info("✅ Connected to existing Cosmos DB container")
                
            except exceptions.CosmosResourceNotFoundError:
                logger.info("Creating new multi-personality database structure...")
                
                # Create database
                self.database = self.cosmos_client.create_database_if_not_exists(database_name)
                
                # Create container with enhanced vector indexing for multi-personality
                container_definition = {
                    'id': container_name,
                    'partitionKey': {'paths': ['/personality'], 'kind': 'Hash'},
                    'vectorEmbeddingPolicy': {
                        'vectorEmbeddings': [
                            {
                                'path': '/embedding',
                                'dataType': 'float32',
                                'dimensions': 384,  # all-MiniLM-L6-v2 dimension
                                'distanceFunction': 'cosine'
                            }
                        ]
                    },
                    'indexingPolicy': {
                        'includedPaths': [
                            {'path': '/personality/?'},
                            {'path': '/content_type/?'},
                            {'path': '/source/?'},
                            {'path': '/category/?'},
                            {'path': '/language/?'},
                            {'path': '/created_at/?'}
                        ],
                        'excludedPaths': [
                            {'path': '/embedding/*'}
                        ],
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
                
                logger.info("✅ Created new multi-personality Cosmos DB structure")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize Cosmos DB: {e}")
            
    def _initialize_embedding_model(self):
        """Initialize embedding model for vector generation"""
        try:
            from sentence_transformers import SentenceTransformer
            
            model_name = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
            self.embedding_model = SentenceTransformer(model_name)
            logger.info(f"✅ Loaded embedding model: {model_name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to load embedding model: {e}")
    
    async def migrate_existing_data(self) -> bool:
        """Migrate data from old vimarsh-db.spiritual-texts to new multi-personality structure"""
        try:
            # Connect to old database
            old_database = self.cosmos_client.get_database_client('vimarsh-db')
            old_container = old_database.get_container_client('spiritual-texts')
            
            logger.info("🔄 Starting migration from old database structure...")
            
            # Query all existing documents
            query = "SELECT * FROM c"
            items = list(old_container.query_items(query=query, enable_cross_partition_query=True))
            
            logger.info(f"Found {len(items)} documents to migrate")
            
            migrated_count = 0
            failed_count = 0
            
            for item in items:
                try:
                    # Determine personality based on content/source
                    personality = self._determine_personality_from_content(item)
                    content_type = self._determine_content_type(item)
                    
                    # Create new vector document
                    vector_doc = VectorDocument(
                        id=f"{personality.value}_{item.get('id', f'migrated_{migrated_count}')}",
                        content=item.get('content', item.get('text', '')),
                        personality=personality,
                        content_type=content_type,
                        source=item.get('source', 'Unknown'),
                        title=item.get('title'),
                        chapter=item.get('chapter'),
                        verse=item.get('verse'),
                        sanskrit=item.get('sanskrit'),
                        translation=item.get('translation'),
                        citation=item.get('citation', item.get('verse_citation')),
                        category=item.get('category', 'general'),
                        language=item.get('language', 'English'),
                        embedding=item.get('embedding'),  # Preserve existing embeddings if available
                        metadata={
                            'migrated_from': 'vimarsh-db.spiritual-texts',
                            'original_id': item.get('id'),
                            'migration_date': datetime.utcnow().isoformat()
                        }
                    )
                    
                    # Generate embedding if not present
                    if not vector_doc.embedding and self.embedding_model:
                        embedding = self.embedding_model.encode(vector_doc.content)
                        vector_doc.embedding = embedding.tolist()
                    
                    # Insert into new container
                    await self.upsert_document(vector_doc)
                    migrated_count += 1
                    
                    if migrated_count % 10 == 0:
                        logger.info(f"Migrated {migrated_count}/{len(items)} documents...")
                        
                except Exception as e:
                    logger.error(f"Failed to migrate document {item.get('id', 'unknown')}: {e}")
                    failed_count += 1
            
            logger.info(f"✅ Migration completed: {migrated_count} successful, {failed_count} failed")
            
            # Update stats
            await self._update_database_stats()
            
            return failed_count == 0
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            return False
    
    def _determine_personality_from_content(self, item: Dict[str, Any]) -> PersonalityType:
        """Determine personality type from content analysis"""
        content = str(item.get('content', item.get('text', ''))).lower()
        source = str(item.get('source', '')).lower()
        
        # Source-based determination
        if 'bhagavad' in source or 'gita' in source or 'krishna' in content:
            return PersonalityType.KRISHNA
        elif 'buddha' in source or 'dhammapada' in source:
            return PersonalityType.BUDDHA
        elif 'jesus' in source or 'christ' in source or 'bible' in source:
            return PersonalityType.JESUS
        elif 'einstein' in source:
            return PersonalityType.EINSTEIN
        
        # Content-based determination
        if any(term in content for term in ['arjuna', 'dharma', 'karma', 'om']):
            return PersonalityType.KRISHNA
        elif any(term in content for term in ['suffering', 'meditation', 'mindfulness']):
            return PersonalityType.BUDDHA
        elif any(term in content for term in ['love', 'forgiveness', 'salvation']):
            return PersonalityType.JESUS
        elif any(term in content for term in ['relativity', 'physics', 'science']):
            return PersonalityType.EINSTEIN
        
        # Default to Krishna for spiritual content
        return PersonalityType.KRISHNA
    
    def _determine_content_type(self, item: Dict[str, Any]) -> ContentType:
        """Determine content type from document structure"""
        if item.get('content_type'):
            return ContentType(item['content_type'])
        elif item.get('verse') and item.get('sanskrit'):
            return ContentType.VERSE
        elif 'commentary' in str(item.get('title', '')).lower():
            return ContentType.COMMENTARY
        elif item.get('sanskrit') and item.get('translation') and item.get('purport'):
            return ContentType.COMPLETE
        else:
            return ContentType.TEACHING
    
    async def upsert_document(self, document: VectorDocument) -> bool:
        """Insert or update a vector document"""
        try:
            if not self.container:
                logger.error("❌ Cosmos DB container not available")
                return False
            
            # Convert to dictionary for Cosmos DB
            doc_dict = asdict(document)
            doc_dict['personality'] = document.personality.value
            doc_dict['content_type'] = document.content_type.value
            
            # Upsert document
            self.container.upsert_item(body=doc_dict)
            
            # Update local cache
            self.local_cache[document.id] = document
            
            logger.debug(f"✅ Upserted document: {document.id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to upsert document {document.id}: {e}")
            return False
    
    async def semantic_search(
        self,
        query: str,
        personality: Optional[PersonalityType] = None,
        content_types: Optional[List[ContentType]] = None,
        top_k: int = 5,
        min_relevance: float = 0.1
    ) -> List[SearchResult]:
        """Perform semantic search with personality and content type filtering"""
        try:
            if not self.embedding_model or not self.container:
                logger.error("❌ Embedding model or database not available")
                return []
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Build search query with filters
            sql_query = "SELECT * FROM c"
            conditions = []
            
            if personality:
                conditions.append(f"c.personality = '{personality.value}'")
            
            if content_types:
                content_type_values = [f"'{ct.value}'" for ct in content_types]
                conditions.append(f"c.content_type IN ({', '.join(content_type_values)})")
            
            if conditions:
                sql_query += f" WHERE {' AND '.join(conditions)}"
            
            # Execute query
            items = list(self.container.query_items(
                query=sql_query,
                enable_cross_partition_query=True
            ))
            
            # Calculate similarities and rank results
            results = []
            for item in items:
                if not item.get('embedding'):
                    continue
                
                # Calculate cosine similarity
                doc_embedding = np.array(item['embedding'])
                query_embedding_np = np.array(query_embedding)
                
                similarity = np.dot(doc_embedding, query_embedding_np) / (
                    np.linalg.norm(doc_embedding) * np.linalg.norm(query_embedding_np)
                )
                
                if similarity >= min_relevance:
                    # Create vector document
                    vector_doc = VectorDocument(
                        id=item['id'],
                        content=item['content'],
                        personality=PersonalityType(item['personality']),
                        content_type=ContentType(item['content_type']),
                        source=item['source'],
                        title=item.get('title'),
                        chapter=item.get('chapter'),
                        verse=item.get('verse'),
                        sanskrit=item.get('sanskrit'),
                        translation=item.get('translation'),
                        citation=item.get('citation'),
                        category=item.get('category', 'general'),
                        language=item.get('language', 'English'),
                        embedding=item.get('embedding'),
                        metadata=item.get('metadata', {})
                    )
                    
                    # Create search result
                    result = SearchResult(
                        document=vector_doc,
                        relevance_score=float(similarity),
                        personality_match=personality is None or vector_doc.personality == personality,
                        content_type_match=content_types is None or vector_doc.content_type in content_types,
                        query_embedding=query_embedding
                    )
                    
                    results.append(result)
            
            # Sort by relevance score and return top_k
            results.sort(key=lambda x: x.relevance_score, reverse=True)
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"❌ Semantic search failed: {e}")
            return []
    
    async def get_database_stats(self) -> DatabaseStats:
        """Get comprehensive database statistics for admin panel"""
        try:
            if not self.container:
                return DatabaseStats(
                    total_documents=0,
                    documents_by_personality={},
                    documents_by_content_type={},
                    documents_by_source={},
                    avg_embedding_similarity=0.0,
                    last_updated=datetime.utcnow().isoformat(),
                    storage_size_mb=0.0,
                    total_embeddings_generated=0,
                    failed_embeddings=0
                )
            
            # Query all documents for statistics
            items = list(self.container.query_items(
                query="SELECT * FROM c",
                enable_cross_partition_query=True
            ))
            
            total_documents = len(items)
            documents_by_personality = {}
            documents_by_content_type = {}
            documents_by_source = {}
            total_embeddings_generated = 0
            failed_embeddings = 0
            
            for item in items:
                # Count by personality
                personality = item.get('personality', 'unknown')
                documents_by_personality[personality] = documents_by_personality.get(personality, 0) + 1
                
                # Count by content type
                content_type = item.get('content_type', 'unknown')
                documents_by_content_type[content_type] = documents_by_content_type.get(content_type, 0) + 1
                
                # Count by source
                source = item.get('source', 'unknown')
                documents_by_source[source] = documents_by_source.get(source, 0) + 1
                
                # Count embeddings
                if item.get('embedding'):
                    total_embeddings_generated += 1
                else:
                    failed_embeddings += 1
            
            # Estimate storage size (rough calculation)
            storage_size_mb = total_documents * 0.01  # Rough estimate
            
            stats = DatabaseStats(
                total_documents=total_documents,
                documents_by_personality=documents_by_personality,
                documents_by_content_type=documents_by_content_type,
                documents_by_source=documents_by_source,
                avg_embedding_similarity=0.85,  # Will be calculated properly in future versions
                last_updated=datetime.utcnow().isoformat(),
                storage_size_mb=storage_size_mb,
                total_embeddings_generated=total_embeddings_generated,
                failed_embeddings=failed_embeddings
            )
            
            self.stats = stats
            return stats
            
        except Exception as e:
            logger.error(f"❌ Failed to get database stats: {e}")
            return DatabaseStats(
                total_documents=0,
                documents_by_personality={},
                documents_by_content_type={},
                documents_by_source={},
                avg_embedding_similarity=0.0,
                last_updated=datetime.utcnow().isoformat(),
                storage_size_mb=0.0,
                total_embeddings_generated=0,
                failed_embeddings=0
            )
    
    async def _update_database_stats(self):
        """Update cached database statistics"""
        self.stats = await self.get_database_stats()
    
    async def bulk_generate_embeddings(self, batch_size: int = 10) -> Tuple[int, int]:
        """Generate embeddings for documents that don't have them"""
        if not self.embedding_model or not self.container:
            logger.error("❌ Embedding model or database not available")
            return 0, 0
        
        # Query documents without embeddings
        query = "SELECT * FROM c WHERE NOT IS_DEFINED(c.embedding) OR c.embedding = null"
        items = list(self.container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        
        logger.info(f"Found {len(items)} documents without embeddings")
        
        successful = 0
        failed = 0
        
        # Process in batches
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            
            try:
                # Extract content for embedding
                contents = [item.get('content', '') for item in batch]
                embeddings = self.embedding_model.encode(contents)
                
                # Update documents with embeddings
                for item, embedding in zip(batch, embeddings):
                    try:
                        item['embedding'] = embedding.tolist()
                        item['updated_at'] = datetime.utcnow().isoformat()
                        
                        self.container.upsert_item(body=item)
                        successful += 1
                        
                    except Exception as e:
                        logger.error(f"Failed to update document {item.get('id')}: {e}")
                        failed += 1
                
                logger.info(f"Processed batch {i//batch_size + 1}: {successful} successful, {failed} failed")
                
            except Exception as e:
                logger.error(f"Failed to process batch {i//batch_size + 1}: {e}")
                failed += len(batch)
        
        logger.info(f"✅ Bulk embedding generation completed: {successful} successful, {failed} failed")
        return successful, failed
    
    async def cleanup_duplicates(self) -> int:
        """Remove duplicate documents based on content similarity"""
        try:
            if not self.container:
                return 0
            
            # Get all documents
            items = list(self.container.query_items(
                query="SELECT * FROM c",
                enable_cross_partition_query=True
            ))
            
            logger.info(f"Checking {len(items)} documents for duplicates...")
            
            # Group by personality and content type for efficient comparison
            groups = {}
            for item in items:
                key = f"{item.get('personality', 'unknown')}_{item.get('content_type', 'unknown')}"
                if key not in groups:
                    groups[key] = []
                groups[key].append(item)
            
            duplicates_removed = 0
            
            for group_key, group_items in groups.items():
                if len(group_items) < 2:
                    continue
                
                # Find duplicates within the group
                for i in range(len(group_items)):
                    for j in range(i + 1, len(group_items)):
                        item1, item2 = group_items[i], group_items[j]
                        
                        # Simple content similarity check
                        content1 = item1.get('content', '')
                        content2 = item2.get('content', '')
                        
                        if self._calculate_text_similarity(content1, content2) > 0.95:
                            # Remove the newer document (keep the older one)
                            older_item = item1 if item1.get('created_at', '') < item2.get('created_at', '') else item2
                            newer_item = item2 if older_item == item1 else item1
                            
                            try:
                                self.container.delete_item(
                                    item=newer_item['id'],
                                    partition_key=newer_item.get('personality')
                                )
                                duplicates_removed += 1
                                logger.debug(f"Removed duplicate: {newer_item['id']}")
                                
                            except Exception as e:
                                logger.error(f"Failed to remove duplicate {newer_item['id']}: {e}")
            
            logger.info(f"✅ Cleanup completed: {duplicates_removed} duplicates removed")
            return duplicates_removed
            
        except Exception as e:
            logger.error(f"❌ Cleanup failed: {e}")
            return 0
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity (Jaccard similarity)"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 and not words2:
            return 1.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
