"""
Enhanced Multi-Personality Metadata Management for Vimarsh
Integrates with existing vector database service and content sourcing pipeline.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum
from pathlib import Path
import hashlib

from services.vector_database_service import (
    PersonalityType, ContentType, VectorDocument, VectorDatabaseService
)

logger = logging.getLogger(__name__)

class SourceType(Enum):
    """Types of content sources"""
    SACRED_TEXT = "sacred_text"
    SCIENTIFIC_PAPER = "scientific_paper"
    HISTORICAL_DOCUMENT = "historical_document"
    PHILOSOPHICAL_WORK = "philosophical_work"
    PATENT = "patent"
    SPEECH = "speech"
    LETTER = "letter"
    AUTOBIOGRAPHY = "autobiography"

@dataclass
class BookMetadata:
    """Comprehensive metadata for books and papers from Gemini's research report"""
    source_id: str
    personality: PersonalityType
    domain: str  # spiritual, scientific, historical, philosophical
    work_title: str
    edition_translation: str
    translator: Optional[str] = None
    original_author: Optional[str] = None
    original_language: Optional[str] = None
    publication_year: Optional[int] = None
    repository: str = ""
    download_url: str = ""
    format_type: str = ""  # pdf, html, text
    authenticity_notes: str = ""
    public_domain: bool = True
    copyright_status: str = "public_domain"
    source_type: SourceType = SourceType.SACRED_TEXT
    
    # Processing metadata
    content_length: Optional[int] = None
    chunk_count: Optional[int] = None
    processing_date: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    quality_score: float = 0.0
    
    # Citation information
    recommended_citation: str = ""
    scholarly_notes: str = ""
    
    @property
    def unique_id(self) -> str:
        """Generate unique identifier for this book/paper"""
        content = f"{self.personality.value}_{self.work_title}_{self.edition_translation}"
        return hashlib.md5(content.encode()).hexdigest()[:16]

@dataclass 
class PersonalitySourceMapping:
    """Maps personalities to their authentic source materials"""
    personality: PersonalityType
    primary_sources: List[BookMetadata] = field(default_factory=list)
    secondary_sources: List[BookMetadata] = field(default_factory=list)
    total_chunks: int = 0
    vector_count: int = 0
    last_updated: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def add_source(self, book_metadata: BookMetadata, is_primary: bool = True):
        """Add a source to this personality's collection"""
        if is_primary:
            self.primary_sources.append(book_metadata)
        else:
            self.secondary_sources.append(book_metadata)
        
        self.last_updated = datetime.utcnow().isoformat()

class MetadataManager:
    """Manages metadata for all personalities and their source materials"""
    
    def __init__(self, metadata_storage_path: str = "metadata_storage"):
        self.storage_path = Path(metadata_storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        # Storage files
        self.books_metadata_file = self.storage_path / "books_metadata.json"
        self.personality_mappings_file = self.storage_path / "personality_mappings.json"
        self.vector_mappings_file = self.storage_path / "vector_mappings.json"
        
        # In-memory caches
        self.books_metadata: Dict[str, BookMetadata] = {}
        self.personality_mappings: Dict[str, PersonalitySourceMapping] = {}
        self.vector_to_source_mapping: Dict[str, str] = {}  # vector_id -> source_id
        
        # Load existing data
        self.load_metadata()
    
    def create_book_metadata_from_source(self, content_source) -> BookMetadata:
        """Create BookMetadata from ContentSource (from content_sourcing_pipeline)"""
        # Map personality strings to PersonalityType enum
        personality_mapping = {
            "Krishna": PersonalityType.KRISHNA,
            "Buddha": PersonalityType.BUDDHA,
            "Jesus Christ": PersonalityType.JESUS,
            "Einstein": PersonalityType.EINSTEIN,
            "Newton": PersonalityType.NEWTON,
            "Tesla": PersonalityType.TESLA,
            "Lincoln": PersonalityType.LINCOLN,
            "Chanakya": PersonalityType.CHANAKYA,
            "Confucius": PersonalityType.CONFUCIUS,
            "Marcus Aurelius": PersonalityType.MARCUS_AURELIUS,
            "Lao Tzu": PersonalityType.LAO_TZU,
            "Rumi": PersonalityType.RUMI,
        }
        
        # Map domain to source type
        source_type_mapping = {
            "spiritual": SourceType.SACRED_TEXT,
            "scientific": SourceType.SCIENTIFIC_PAPER,
            "historical": SourceType.HISTORICAL_DOCUMENT,
            "philosophical": SourceType.PHILOSOPHICAL_WORK,
        }
        
        personality = personality_mapping.get(content_source.personality, PersonalityType.KRISHNA)
        source_type = source_type_mapping.get(content_source.domain, SourceType.SACRED_TEXT)
        
        # Extract translator/author from edition_translation
        translator = None
        if "trans." in content_source.edition_translation:
            translator = content_source.edition_translation.split("(trans.)")[0].strip()
        elif "," in content_source.edition_translation:
            translator = content_source.edition_translation.split(",")[0].strip()
        
        return BookMetadata(
            source_id=content_source.source_id,
            personality=personality,
            domain=content_source.domain,
            work_title=content_source.work_title,
            edition_translation=content_source.edition_translation,
            translator=translator,
            repository=content_source.repository,
            download_url=content_source.download_url,
            format_type=content_source.format_type,
            authenticity_notes=content_source.authenticity_notes,
            public_domain=content_source.public_domain,
            source_type=source_type,
            recommended_citation=f"{content_source.edition_translation}. {content_source.work_title}. {content_source.repository}.",
            scholarly_notes=content_source.authenticity_notes
        )
    
    def register_book(self, book_metadata: BookMetadata, is_primary_source: bool = True):
        """Register a book/paper and map it to personality"""
        # Store book metadata
        self.books_metadata[book_metadata.unique_id] = book_metadata
        
        # Update personality mapping
        personality_key = book_metadata.personality.value
        if personality_key not in self.personality_mappings:
            self.personality_mappings[personality_key] = PersonalitySourceMapping(
                personality=book_metadata.personality
            )
        
        self.personality_mappings[personality_key].add_source(book_metadata, is_primary_source)
        
        logger.info(f"📚 Registered {book_metadata.work_title} for {book_metadata.personality.value}")
    
    def create_vector_document(self, 
                              book_metadata: BookMetadata, 
                              content: str, 
                              chunk_index: int,
                              chapter: Optional[str] = None,
                              verse: Optional[str] = None,
                              additional_metadata: Optional[Dict[str, Any]] = None) -> VectorDocument:
        """Create a VectorDocument with proper metadata linking"""
        
        # Generate unique vector document ID
        vector_id = f"{book_metadata.unique_id}_chunk_{chunk_index:04d}"
        
        # Map domain to content type
        content_type_mapping = {
            "spiritual": ContentType.VERSE if verse else ContentType.TEACHING,
            "scientific": ContentType.QUOTE,
            "historical": ContentType.QUOTE,
            "philosophical": ContentType.QUOTE,
        }
        
        content_type = content_type_mapping.get(book_metadata.domain, ContentType.TEACHING)
        
        # Create citation
        citation_parts = [book_metadata.work_title]
        if chapter:
            citation_parts.append(f"Chapter {chapter}")
        if verse:
            citation_parts.append(f"Verse {verse}")
        citation_parts.append(f"({book_metadata.edition_translation})")
        citation = ", ".join(citation_parts)
        
        # Combine metadata
        metadata = {
            "source_id": book_metadata.source_id,
            "unique_id": book_metadata.unique_id,
            "domain": book_metadata.domain,
            "translator": book_metadata.translator,
            "repository": book_metadata.repository,
            "authenticity_notes": book_metadata.authenticity_notes,
            "chunk_index": chunk_index,
            "public_domain": book_metadata.public_domain,
            "copyright_status": book_metadata.copyright_status,
            "source_type": book_metadata.source_type.value,
        }
        
        if additional_metadata:
            metadata.update(additional_metadata)
        
        # Track vector to source mapping
        self.vector_to_source_mapping[vector_id] = book_metadata.unique_id
        
        return VectorDocument(
            id=vector_id,
            content=content,
            personality=book_metadata.personality,
            content_type=content_type,
            source=book_metadata.work_title,
            title=f"{book_metadata.work_title} - Chunk {chunk_index}",
            chapter=chapter,
            verse=verse,
            citation=citation,
            category=book_metadata.domain,
            language="English",  # Most sources are English translations
            metadata=metadata
        )
    
    def get_sources_for_personality(self, personality: Union[str, PersonalityType]) -> Optional[PersonalitySourceMapping]:
        """Get all sources for a specific personality"""
        if isinstance(personality, PersonalityType):
            personality = personality.value
        
        return self.personality_mappings.get(personality)
    
    def get_book_metadata(self, source_id: str) -> Optional[BookMetadata]:
        """Get book metadata by source ID"""
        return self.books_metadata.get(source_id)
    
    def get_source_from_vector(self, vector_id: str) -> Optional[BookMetadata]:
        """Get the source book metadata from a vector document ID"""
        source_id = self.vector_to_source_mapping.get(vector_id)
        if source_id:
            return self.books_metadata.get(source_id)
        return None
    
    def update_processing_stats(self, source_id: str, content_length: int, chunk_count: int, quality_score: float = 0.0):
        """Update processing statistics for a book"""
        if source_id in self.books_metadata:
            book = self.books_metadata[source_id]
            book.content_length = content_length
            book.chunk_count = chunk_count
            book.quality_score = quality_score
            book.processing_date = datetime.utcnow().isoformat()
            
            # Update personality mapping totals
            personality_key = book.personality.value
            if personality_key in self.personality_mappings:
                mapping = self.personality_mappings[personality_key]
                mapping.total_chunks += chunk_count
                mapping.last_updated = datetime.utcnow().isoformat()
    
    def get_personality_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get comprehensive statistics for all personalities"""
        stats = {}
        
        for personality_key, mapping in self.personality_mappings.items():
            stats[personality_key] = {
                "personality": personality_key,
                "primary_sources_count": len(mapping.primary_sources),
                "secondary_sources_count": len(mapping.secondary_sources),
                "total_sources": len(mapping.primary_sources) + len(mapping.secondary_sources),
                "total_chunks": mapping.total_chunks,
                "vector_count": mapping.vector_count,
                "last_updated": mapping.last_updated,
                "primary_works": [source.work_title for source in mapping.primary_sources],
                "domains": list(set([source.domain for source in mapping.primary_sources + mapping.secondary_sources]))
            }
        
        return stats
    
    def save_metadata(self):
        """Save all metadata to disk"""
        try:
            # Convert dataclasses to dictionaries for JSON serialization
            books_data = {
                source_id: asdict(book_metadata) 
                for source_id, book_metadata in self.books_metadata.items()
            }
            
            personality_data = {}
            for personality_key, mapping in self.personality_mappings.items():
                mapping_dict = asdict(mapping)
                # Convert PersonalityType enum to string
                mapping_dict['personality'] = mapping.personality.value
                personality_data[personality_key] = mapping_dict
            
            # Save to files
            with open(self.books_metadata_file, 'w', encoding='utf-8') as f:
                json.dump(books_data, f, indent=2, ensure_ascii=False, default=str)
            
            with open(self.personality_mappings_file, 'w', encoding='utf-8') as f:
                json.dump(personality_data, f, indent=2, ensure_ascii=False, default=str)
            
            with open(self.vector_mappings_file, 'w', encoding='utf-8') as f:
                json.dump(self.vector_to_source_mapping, f, indent=2, ensure_ascii=False)
            
            logger.info("✅ Metadata saved successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to save metadata: {str(e)}")
    
    def load_metadata(self):
        """Load metadata from disk"""
        try:
            # Load books metadata
            if self.books_metadata_file.exists():
                with open(self.books_metadata_file, 'r', encoding='utf-8') as f:
                    books_data = json.load(f)
                
                for source_id, book_dict in books_data.items():
                    # Convert back to dataclass
                    # Handle enum conversion
                    if 'personality' in book_dict:
                        book_dict['personality'] = PersonalityType(book_dict['personality'])
                    if 'source_type' in book_dict:
                        book_dict['source_type'] = SourceType(book_dict['source_type'])
                    
                    self.books_metadata[source_id] = BookMetadata(**book_dict)
            
            # Load personality mappings
            if self.personality_mappings_file.exists():
                with open(self.personality_mappings_file, 'r', encoding='utf-8') as f:
                    personality_data = json.load(f)
                
                for personality_key, mapping_dict in personality_data.items():
                    # Convert personality back to enum
                    mapping_dict['personality'] = PersonalityType(mapping_dict['personality'])
                    
                    # Convert source lists back to BookMetadata objects
                    primary_sources = []
                    for source_dict in mapping_dict.get('primary_sources', []):
                        if 'personality' in source_dict:
                            source_dict['personality'] = PersonalityType(source_dict['personality'])
                        if 'source_type' in source_dict:
                            source_dict['source_type'] = SourceType(source_dict['source_type'])
                        primary_sources.append(BookMetadata(**source_dict))
                    
                    secondary_sources = []
                    for source_dict in mapping_dict.get('secondary_sources', []):
                        if 'personality' in source_dict:
                            source_dict['personality'] = PersonalityType(source_dict['personality'])
                        if 'source_type' in source_dict:
                            source_dict['source_type'] = SourceType(source_dict['source_type'])
                        secondary_sources.append(BookMetadata(**source_dict))
                    
                    mapping_dict['primary_sources'] = primary_sources
                    mapping_dict['secondary_sources'] = secondary_sources
                    
                    self.personality_mappings[personality_key] = PersonalitySourceMapping(**mapping_dict)
            
            # Load vector mappings
            if self.vector_mappings_file.exists():
                with open(self.vector_mappings_file, 'r', encoding='utf-8') as f:
                    self.vector_to_source_mapping = json.load(f)
            
            logger.info("✅ Metadata loaded successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to load metadata: {str(e)}")

# Example usage and integration
class EnhancedContentProcessor:
    """Enhanced content processor that integrates with metadata management"""
    
    def __init__(self, vector_db_service: VectorDatabaseService, metadata_manager: MetadataManager):
        self.vector_db = vector_db_service
        self.metadata_manager = metadata_manager
    
    async def process_sourced_content(self, sourced_content: Dict[str, Any], content_source):
        """Process content from the sourcing pipeline with full metadata tracking"""
        
        # Create book metadata
        book_metadata = self.metadata_manager.create_book_metadata_from_source(content_source)
        
        # Register the book
        self.metadata_manager.register_book(book_metadata, is_primary_source=True)
        
        # Process content into chunks (simplified - you'll use your existing chunking logic)
        content = sourced_content['content']
        chunks = self._chunk_content(content)  # Your existing chunking logic
        
        # Create vector documents with metadata
        vector_documents = []
        for i, chunk in enumerate(chunks):
            vector_doc = self.metadata_manager.create_vector_document(
                book_metadata=book_metadata,
                content=chunk,
                chunk_index=i,
                additional_metadata={
                    "processing_pipeline": "content_sourcing_pipeline",
                    "gemini_research_report": True
                }
            )
            vector_documents.append(vector_doc)
        
        # Store in vector database
        for vector_doc in vector_documents:
            await self.vector_db.add_document(vector_doc)
        
        # Update processing stats
        self.metadata_manager.update_processing_stats(
            source_id=book_metadata.source_id,
            content_length=len(content),
            chunk_count=len(chunks),
            quality_score=0.8  # You can calculate this based on your quality metrics
        )
        
        # Save metadata
        self.metadata_manager.save_metadata()
        
        logger.info(f"✅ Processed {book_metadata.work_title} - {len(chunks)} chunks")
        
        return vector_documents
    
    def _chunk_content(self, content: str) -> List[str]:
        """Placeholder for your existing chunking logic"""
        # Use your existing chunking logic from chunking.py
        # This is just a simple example
        chunk_size = 1000
        chunks = []
        for i in range(0, len(content), chunk_size):
            chunks.append(content[i:i + chunk_size])
        return chunks
