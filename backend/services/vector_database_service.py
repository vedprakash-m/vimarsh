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
            container_name = os.getenv('AZURE_COSMOS_CONTAINER_NAME', 'personality-vectors')
            
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
                                'dimensions': 768,  # Gemini text-embedding-004 dimension
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
            # Use Gemini API for embeddings instead of sentence-transformers
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from gemini_embedding_service import GeminiTransformer
            
            # Create Gemini-based transformer for drop-in compatibility
            self.embedding_model = GeminiTransformer('gemini-embedding')
            logger.info(f"✅ Loaded Gemini embedding service (dimension: {self.embedding_model.service.dimension})")
            
        except Exception as e:
            logger.error(f"❌ Failed to load Gemini embedding service: {e}")
            logger.warning("⚠️ Falling back to mock embedding model")
            self.embedding_model = None
    
    async def migrate_existing_data(self) -> bool:
        """
        DEPRECATED: Migration from old vimarsh-db.spiritual-texts to new multi-personality structure
        This migration has been completed. Old containers have been deleted.
        """
        logger.warning("❌ Migration method called but is no longer needed - migration completed")
        logger.info("✅ All data is now in vimarsh-multi-personality.personality-vectors container")
        return True  # Return success to prevent errors in calling code
    
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
            query_embedding = self.embedding_model.encode(query)
            # Ensure it's a list (Gemini service already returns a list)
            if hasattr(query_embedding, 'tolist'):
                query_embedding = query_embedding.tolist()
            elif not isinstance(query_embedding, list):
                query_embedding = list(query_embedding)
            
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

    async def add_content(self, content: str, personality_id: str, metadata: Dict[str, Any] = None) -> bool:
        """Add new content to the vector database with proper chunking and embedding generation"""
        try:
            if not self.container or not self.embedding_model:
                logger.error("❌ Database or embedding service not available")
                return False
            
            # Parse personality
            try:
                personality = PersonalityType(personality_id.lower())
            except ValueError:
                logger.error(f"❌ Invalid personality: {personality_id}")
                return False
            
            metadata = metadata or {}
            
            # Determine content type from metadata or content analysis
            content_type = ContentType.TEACHING
            if metadata.get('content_type'):
                try:
                    content_type = ContentType(metadata['content_type'])
                except ValueError:
                    pass
            elif 'verse' in metadata or 'sanskrit' in metadata:
                content_type = ContentType.VERSE
            elif 'commentary' in content.lower():
                content_type = ContentType.COMMENTARY
            
            # Generate embedding
            try:
                embedding = self.embedding_model.encode(content)
                embedding_list = embedding.tolist() if hasattr(embedding, 'tolist') else list(embedding)
            except Exception as e:
                logger.error(f"❌ Failed to generate embedding: {e}")
                return False
            
            # Create document ID
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            doc_id = f"{personality_id}_{timestamp}_{hash(content[:100]) % 1000:03d}"
            
            # Create vector document
            vector_doc = VectorDocument(
                id=doc_id,
                content=content,
                personality=personality,
                content_type=content_type,
                source=metadata.get('source', 'Added via API'),
                title=metadata.get('title'),
                chapter=metadata.get('chapter'),
                verse=metadata.get('verse'),
                sanskrit=metadata.get('sanskrit'),
                translation=metadata.get('translation'),
                citation=metadata.get('citation'),
                category=metadata.get('category', 'general'),
                language=metadata.get('language', 'English'),
                embedding=embedding_list,
                metadata=metadata
            )
            
            # Store in database
            success = await self.upsert_document(vector_doc)
            
            if success:
                logger.info(f"✅ Added content to {personality_id}: {doc_id}")
                # Update stats if cached
                if self.stats:
                    await self._update_database_stats()
            else:
                logger.error(f"❌ Failed to store document: {doc_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Failed to add content: {e}")
            return False

    async def get_personality_stats(self, personality_id: Optional[str] = None) -> Dict[str, Any]:
        """Get detailed statistics for a specific personality or all personalities"""
        try:
            if not self.container:
                logger.error("❌ Database not available")
                return {}
            
            # Build query based on personality filter
            if personality_id:
                query = f"SELECT * FROM c WHERE c.personality = '{personality_id.lower()}'"
            else:
                query = "SELECT * FROM c"
            
            items = list(self.container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            
            if personality_id:
                # Stats for specific personality
                personality_docs = items
                total_docs = len(personality_docs)
                
                content_types = {}
                sources = {}
                languages = {}
                with_embeddings = 0
                avg_content_length = 0
                
                for item in personality_docs:
                    # Content types
                    ct = item.get('content_type', 'unknown')
                    content_types[ct] = content_types.get(ct, 0) + 1
                    
                    # Sources
                    source = item.get('source', 'unknown')
                    sources[source] = sources.get(source, 0) + 1
                    
                    # Languages
                    lang = item.get('language', 'unknown')
                    languages[lang] = languages.get(lang, 0) + 1
                    
                    # Embeddings
                    if item.get('embedding'):
                        with_embeddings += 1
                    
                    # Content length
                    content_length = len(item.get('content', ''))
                    avg_content_length += content_length
                
                avg_content_length = avg_content_length / total_docs if total_docs > 0 else 0
                
                return {
                    'personality': personality_id,
                    'total_documents': total_docs,
                    'content_types': content_types,
                    'sources': sources,
                    'languages': languages,
                    'embeddings_generated': with_embeddings,
                    'missing_embeddings': total_docs - with_embeddings,
                    'avg_content_length': avg_content_length,
                    'last_updated': datetime.utcnow().isoformat()
                }
            else:
                # Stats for all personalities
                personalities = {}
                
                for item in items:
                    personality = item.get('personality', 'unknown')
                    if personality not in personalities:
                        personalities[personality] = {
                            'documents': 0,
                            'content_types': {},
                            'sources': set(),
                            'with_embeddings': 0
                        }
                    
                    personalities[personality]['documents'] += 1
                    
                    ct = item.get('content_type', 'unknown')
                    personalities[personality]['content_types'][ct] = personalities[personality]['content_types'].get(ct, 0) + 1
                    
                    personalities[personality]['sources'].add(item.get('source', 'unknown'))
                    
                    if item.get('embedding'):
                        personalities[personality]['with_embeddings'] += 1
                
                # Convert sets to counts
                for p_id, stats in personalities.items():
                    stats['unique_sources'] = len(stats['sources'])
                    del stats['sources']  # Remove set, keep count
                
                return {
                    'total_personalities': len(personalities),
                    'personalities': personalities,
                    'last_updated': datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to get personality stats: {e}")
            return {}

    async def export_database(self, personality_filter: Optional[str] = None) -> Dict[str, Any]:
        """Export database contents for backup or migration"""
        try:
            if not self.container:
                logger.error("❌ Database not available")
                return {}
            
            # Build query
            if personality_filter:
                query = f"SELECT * FROM c WHERE c.personality = '{personality_filter.lower()}'"
            else:
                query = "SELECT * FROM c"
            
            items = list(self.container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            
            # Get database stats
            stats = await self.get_database_stats()
            
            export_data = {
                'export_metadata': {
                    'timestamp': datetime.utcnow().isoformat(),
                    'personality_filter': personality_filter,
                    'total_documents': len(items),
                    'export_version': '1.0'
                },
                'database_stats': asdict(stats),
                'documents': items
            }
            
            logger.info(f"✅ Exported {len(items)} documents" + 
                       (f" for personality {personality_filter}" if personality_filter else ""))
            
            return export_data
            
        except Exception as e:
            logger.error(f"❌ Failed to export database: {e}")
            return {}

    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check for the vector database service"""
        health_status = {
            'timestamp': datetime.utcnow().isoformat(),
            'overall_status': 'healthy',
            'components': {},
            'performance_metrics': {}
        }
        
        try:
            # Check Cosmos DB connection
            if self.cosmos_client and self.container:
                try:
                    # Simple query to test connection
                    list(self.container.query_items(
                        query="SELECT TOP 1 c.id FROM c",
                        enable_cross_partition_query=True
                    ))
                    health_status['components']['cosmos_db'] = 'healthy'
                except Exception as e:
                    health_status['components']['cosmos_db'] = f'unhealthy: {str(e)}'
                    health_status['overall_status'] = 'degraded'
            else:
                health_status['components']['cosmos_db'] = 'unhealthy: not initialized'
                health_status['overall_status'] = 'unhealthy'
            
            # Check embedding service
            if self.embedding_model:
                try:
                    # Test embedding generation
                    test_embedding = self.embedding_model.encode("test")
                    if test_embedding is not None and len(test_embedding) > 0:
                        health_status['components']['embedding_service'] = 'healthy'
                    else:
                        health_status['components']['embedding_service'] = 'unhealthy: invalid response'
                        health_status['overall_status'] = 'degraded'
                except Exception as e:
                    health_status['components']['embedding_service'] = f'unhealthy: {str(e)}'
                    health_status['overall_status'] = 'degraded'
            else:
                health_status['components']['embedding_service'] = 'unhealthy: not initialized'
                health_status['overall_status'] = 'degraded'
            
            # Performance metrics
            if health_status['components'].get('cosmos_db') == 'healthy':
                try:
                    import time
                    start_time = time.time()
                    
                    # Test query performance
                    list(self.container.query_items(
                        query="SELECT TOP 5 c.id, c.personality FROM c",
                        enable_cross_partition_query=True  
                    ))
                    
                    query_time = (time.time() - start_time) * 1000
                    health_status['performance_metrics']['query_time_ms'] = round(query_time, 2)
                    
                    # Get document count
                    stats = await self.get_database_stats()
                    health_status['performance_metrics']['total_documents'] = stats.total_documents
                    health_status['performance_metrics']['total_embeddings'] = stats.total_embeddings_generated
                    
                except Exception as e:
                    health_status['performance_metrics']['error'] = str(e)
            
            return health_status
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'overall_status': 'unhealthy',
                'error': str(e)
            }
