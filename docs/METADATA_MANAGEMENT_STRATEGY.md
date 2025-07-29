# Metadata Management & Vector-Personality Mapping Strategy

## Overview
This document outlines the comprehensive metadata management strategy for Vimarsh's multi-personality RAG system, addressing storage of book/paper metadata and vector-personality mapping.

## 🗂️ Metadata Storage Architecture

### **1. Three-Layer Metadata System**

```
📁 metadata_storage/
├── books_metadata.json          # Complete book/paper information
├── personality_mappings.json    # Personality-to-sources mapping
└── vector_mappings.json         # Vector-to-source traceability
```

### **2. Book Metadata Storage (`books_metadata.json`)**
```json
{
  "source_id_12345": {
    "source_id": "source_id_12345",
    "personality": "marcus_aurelius",
    "domain": "philosophical",
    "work_title": "Meditations",
    "edition_translation": "George W. Chrystal (translation)",
    "translator": "George W. Chrystal",
    "original_author": "Marcus Aurelius",
    "repository": "Project Gutenberg",
    "download_url": "http://www.gutenberg.org/ebooks/55317",
    "authenticity_notes": "Public domain. Multiple machine-readable formats.",
    "public_domain": true,
    "copyright_status": "public_domain",
    "source_type": "philosophical_work",
    "content_length": 125000,
    "chunk_count": 156,
    "quality_score": 0.95,
    "recommended_citation": "George W. Chrystal (translation). Meditations. Project Gutenberg.",
    "processing_date": "2025-07-28T10:30:00Z"
  }
}
```

### **3. Personality Mappings (`personality_mappings.json`)**
```json
{
  "marcus_aurelius": {
    "personality": "marcus_aurelius",
    "primary_sources": [...],  // Full BookMetadata objects
    "secondary_sources": [...], 
    "total_chunks": 156,
    "vector_count": 156,
    "last_updated": "2025-07-28T10:30:00Z"
  }
}
```

### **4. Vector Mappings (`vector_mappings.json`)**
```json
{
  "source_id_12345_chunk_0001": "source_id_12345",
  "source_id_12345_chunk_0002": "source_id_12345",
  // Maps every vector ID back to its source book
}
```

## 🔗 Vector-Personality Mapping in Cosmos DB

### **Enhanced Vector Document Structure**
Your existing `VectorDocument` class is extended with comprehensive metadata:

```python
@dataclass
class VectorDocument:
    id: str  # Format: "{source_id}_chunk_{index:04d}"
    content: str
    personality: PersonalityType  # ENUM: MARCUS_AURELIUS, EINSTEIN, etc.
    content_type: ContentType     # ENUM: VERSE, TEACHING, QUOTE, etc.
    source: str                   # "Meditations"
    title: str                    # "Meditations - Chunk 1"
    citation: str                 # "Meditations, Chapter 1 (George W. Chrystal)"
    category: str                 # "philosophical"
    metadata: Dict[str, Any]      # Rich metadata including:
    # {
    #   "source_id": "source_id_12345",
    #   "domain": "philosophical", 
    #   "translator": "George W. Chrystal",
    #   "repository": "Project Gutenberg",
    #   "chunk_index": 1,
    #   "authenticity_notes": "Public domain...",
    #   "public_domain": true,
    #   "copyright_status": "public_domain"
    # }
```

### **Cosmos DB Container Structure**
```javascript
// Container: personality-vectors
// Partition Key: /personality (enables efficient personality-based queries)

// Document structure in Cosmos DB:
{
  "id": "einstein_relativity_chunk_0001",
  "personality": "einstein",           // Partition key
  "content_type": "quote",
  "source": "On the Electrodynamics of Moving Bodies",
  "content": "The introduction of a \"luminiferous ether\"...",
  "embedding": [0.1, 0.2, ...],      // 768-dim vector
  "citation": "On the Electrodynamics of Moving Bodies (Original 1905 Paper)",
  "category": "scientific",
  "metadata": {
    "source_id": "einstein_relativity_1905",
    "domain": "scientific",
    "repository": "astro.puc.cl",
    "chunk_index": 1,
    "authenticity_notes": "Direct PDF of the seminal paper.",
    "public_domain": true
  },
  "created_at": "2025-07-28T10:30:00Z"
}
```

## 🔍 Query Patterns & Retrieval

### **1. Personality-Specific Search**
```python
# Query all vectors for Einstein
personality_vectors = container.query_items(
    query="SELECT * FROM c WHERE c.personality = @personality",
    parameters=[{"name": "@personality", "value": "einstein"}]
)
```

### **2. Multi-Personality Semantic Search**
```python
# Vector similarity search across multiple personalities
search_results = await vector_db.search_similar(
    query_embedding=query_vector,
    personalities=["einstein", "newton", "tesla"],  # Scientific domain
    top_k=10
)
```

### **3. Source Provenance Lookup**
```python
# Given a vector ID, get complete source information
vector_id = "einstein_relativity_chunk_0001"
source_metadata = metadata_manager.get_source_from_vector(vector_id)
# Returns complete BookMetadata with authenticity info
```

### **4. Domain-Based Filtering**
```python
# Get all philosophical content
philosophical_vectors = container.query_items(
    query="SELECT * FROM c WHERE c.category = 'philosophical'",
    enable_cross_partition_query=True
)
```

## 📊 Metadata Management Benefits

### **1. Complete Traceability**
- Every vector traces back to its authentic source
- Full citation information for generated responses
- Copyright and authenticity verification

### **2. Quality Assurance**
- Source authenticity scores
- Translation quality metadata
- Repository credibility tracking

### **3. Legal Compliance**
- Public domain status tracking
- Copyright compliance verification
- Attribution requirements management

### **4. Performance Optimization**
- Personality-based partitioning for fast queries
- Cached metadata for quick lookups
- Efficient cross-personality searches

## 🛠️ Implementation Integration

### **Phase 1: Metadata Infrastructure**
```bash
# 1. Install dependencies (already provided in your codebase)
cd backend/data_processing

# 2. Initialize metadata manager
python -c "
from metadata_manager import MetadataManager
manager = MetadataManager()
print('Metadata infrastructure ready')
"
```

### **Phase 2: Content Processing**
```python
# Use the integrated content manager
from integrated_content_manager import IntegratedContentManager

manager = IntegratedContentManager()
await manager.process_all_personalities()  # Full pipeline
```

### **Phase 3: Query Integration**
```python
# Query by personality
einstein_info = manager.query_by_personality("einstein")

# Get vector provenance
source_info = manager.get_vector_provenance(vector_id)

# Generate citations
citation = source_info["citation"]
```

## 🎯 Key Advantages of This Approach

### **1. Scalability**
- Supports unlimited personalities and sources
- Efficient partition-based querying
- Metadata caching for performance

### **2. Authenticity**
- Direct mapping to authoritative sources
- Quality scoring and validation
- Full provenance chain

### **3. Legal Safety**
- Public domain compliance tracking
- Copyright status verification
- Proper attribution generation

### **4. User Trust**
- Transparent source citations
- Authenticity verification
- Quality indicators

## 📈 Future Enhancements

### **1. Advanced Analytics**
- Source quality trending
- Personality coverage analysis
- User preference tracking

### **2. Dynamic Content**
- Real-time source updates
- Content freshness scoring
- Automated quality assessment

### **3. Multi-Language Support**
- Original language preservation
- Translation quality tracking
- Cross-language semantic search

This architecture ensures that every piece of content in Vimarsh can be traced back to its authentic source while maintaining optimal performance for personality-based RAG queries.
