# Vimarsh Book Registry & Vector Database Integration

This directory contains the implementation for Vimarsh's book registry management system and Azure Cosmos DB (MongoDB vCore) integration for vector storage.

## 🎯 Overview

The system provides:
1. **Spiritual Books Processing Pipeline** - Converts raw spiritual texts into clean RAG chunks
2. **Vector Database Integration** - Stores embeddings in Azure Cosmos DB for semantic search
3. **Book Registry Management** - Tracks book processing status and metadata
4. **Admin Dashboard** - Web-based interface for content management

## 📁 File Structure

```
scripts/
├── process_all_spiritual_books.py  # Main processing pipeline
├── cosmos_db_integration.py        # Vector database integration
├── book_registry_admin.py          # Admin dashboard Flask app
├── requirements_admin.txt          # Dependencies for admin tools
└── templates/                      # HTML templates for admin UI
    ├── base.html                   # Base template with sacred design
    ├── dashboard.html              # Main dashboard overview
    ├── books.html                  # Books management interface
    ├── add_book.html               # Add new book form
    ├── book_detail.html            # Individual book details
    └── error.html                  # Error page template
```

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Install dependencies
pip install -r requirements_admin.txt

# Set environment variables
export OPENAI_API_KEY="your-openai-api-key"
export COSMOS_DB_CONNECTION_STRING="your-cosmos-db-connection-string"
export VIMARSH_BASE_DIR="/path/to/vimarsh"
```

### 2. Process Spiritual Books

```bash
# Process all books (creates clean chunks and registry)
python process_all_spiritual_books.py
```

### 3. Generate and Upload Vectors

```bash
# Generate embeddings and upload to Cosmos DB
python cosmos_db_integration.py
```

### 4. Start Admin Dashboard

```bash
# Launch the admin web interface
python book_registry_admin.py
```

Visit `http://localhost:5001` to access the admin dashboard.

## 🗄️ Data Flow

```
Raw Books (JSON) → Processing Pipeline → Clean Chunks (JSONL) → Embeddings → Cosmos DB
                                    ↓
                              Book Registry (JSON) → Admin Dashboard
```

### Processing Pipeline

1. **Text Cleaning**: Remove spam/donor text, deduplicate content
2. **Chunking**: Create multiple RAG chunks per verse (verse-only, commentary-only, complete)
3. **Metadata Extraction**: Extract chapter, verse, and content type information
4. **Registry Update**: Track processing status and statistics

### Vector Database Integration

1. **Embedding Generation**: Use OpenAI's text-embedding-ada-002 model
2. **Batch Processing**: Process embeddings in configurable batches
3. **Vector Upload**: Store in Azure Cosmos DB (MongoDB vCore) with vector search index
4. **Search Capability**: Support semantic search with optional book filtering

## 📊 Admin Dashboard Features

### Dashboard Overview
- **Real-time Statistics**: Book counts, processing status, content metrics
- **Visual Charts**: Status distribution, content type breakdown
- **Recent Activity**: Processing updates and system events
- **Collection Health**: Vector database statistics and storage metrics

### Book Management
- **Book Registry**: View all processed and planned books
- **Status Tracking**: Monitor processing pipeline progress
- **Metadata Editing**: Update book information and classifications
- **Quality Control**: Expert review and validation tools

### Content Operations
- **Add Books**: Interface for planning new book additions
- **Processing Control**: Start, pause, and monitor processing tasks
- **Metadata Enrichment**: Semi-automated web scraping for additional context
- **Vector Search Testing**: Test semantic search functionality

## 🔧 Configuration

### Book Configuration (process_all_spiritual_books.py)

```python
books_config = {
    "book_id": {
        "title": "Book Title",
        "author": "Author Name",
        "source_file": "raw-data/book.json",
        "output_file": "book_clean.jsonl",
        "book_code": "code",
        "type": "scripture|dialogue|upanisad"
    }
}
```

### Cosmos DB Configuration

```python
# Connection settings
DATABASE_NAME = "vimarsh"
COLLECTION_NAME = "spiritual_embeddings"
VECTOR_DIMENSIONS = 1536  # OpenAI ada-002 embedding size
```

### Admin Dashboard Configuration

```python
# Flask settings
DEBUG = False  # Set to True for development
PORT = 5001
SECRET_KEY = "change-in-production"
```

## 📈 Registry Schema

### Books Registry (books_registry.json)

```json
{
  "version": "1.0",
  "last_updated": "2025-06-26T00:00:00",
  "books": {
    "book_id": {
      "book_id": "unique_identifier",
      "title": "Book Title",
      "author": "Author Name",
      "type": "scripture",
      "language": "Sanskrit/English",
      "book_code": "code",
      "status": "success|processing|planned|error",
      "chapters_processed": 18,
      "verses_processed": 700,
      "chunks_created": 2100,
      "vectors_count": 2100,
      "embeddings_generated": true,
      "embeddings_uploaded": true,
      "metadata_enriched": false,
      "web_sources": [],
      "processed_date": "2025-06-26T00:00:00",
      "vectorized_date": "2025-06-26T01:00:00"
    }
  },
  "planned_books": [
    {
      "book_id": "planned_book",
      "title": "Planned Book",
      "author": "Author",
      "type": "scripture",
      "priority": "high|medium|low",
      "added_date": "2025-06-26T00:00:00",
      "status": "planned"
    }
  ]
}
```

### Vector Document Schema (Cosmos DB)

```json
{
  "_id": "chunk_id",
  "book": "Book Title",
  "chapter": 1,
  "verse": "1.1",
  "content_type": "verse|commentary|complete",
  "content": "Full text content",
  "embedding": [0.1, 0.2, ...],  // 1536 dimensions
  "metadata": {
    "verse_citation": "Book 1.1",
    "book_title": "Book Title",
    "chapter_number": 1,
    "content_focus": "verse_text|commentary|complete"
  },
  "book_id": "book_identifier",
  "created_at": "2025-06-26T00:00:00",
  "hash": "content_hash"
}
```

## 🔍 Vector Search

### Search API

```python
# Search for similar content
results = vectorizer.search_similar_content(
    query="What is the nature of duty?",
    top_k=5,
    book_filter="bhagavad_gita"  # Optional
)
```

### Search Results

```json
[
  {
    "content": "Verse content with translation and purport",
    "book": "Bhagavad Gita As It Is",
    "verse": "18.47",
    "content_type": "complete",
    "score": 0.95,
    "metadata": {
      "verse_citation": "BG 18.47",
      "chapter_number": 18
    }
  }
]
```

## 🛡️ Security & Privacy

### Data Protection
- **Encryption**: All data encrypted in transit and at rest
- **API Keys**: Stored securely in environment variables
- **Access Control**: Role-based permissions in admin dashboard
- **Audit Logging**: Track all administrative actions

### Content Integrity
- **Hash Verification**: Content integrity checks using SHA-256
- **Deduplication**: Prevent duplicate embeddings
- **Version Control**: Track changes to processed content
- **Backup Strategy**: Automated registry and vector database backups

## 🔧 Development & Deployment

### Local Development

```bash
# Clone repository
git clone <repository-url>
cd vimarsh/scripts

# Install dependencies
pip install -r requirements_admin.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Run processing pipeline
python process_all_spiritual_books.py

# Start admin dashboard
FLASK_ENV=development python book_registry_admin.py
```

### Production Deployment

```bash
# Set production environment variables
export FLASK_ENV=production
export SECRET_KEY="secure-random-key"
export PORT=5001

# Install production dependencies
pip install -r requirements_admin.txt gunicorn

# Start with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 book_registry_admin:app
```

### Azure Functions Integration

The processing pipeline can be integrated with Azure Functions for automated processing:

```python
# Azure Function wrapper
import azure.functions as func
from scripts.process_all_spiritual_books import SpiritualBooksProcessor

def main(req: func.HttpRequest) -> func.HttpResponse:
    processor = SpiritualBooksProcessor("/tmp/vimarsh")
    result = processor.process_all_books()
    return func.HttpResponse(json.dumps(result))
```

## 📊 Monitoring & Analytics

### System Metrics
- **Processing Performance**: Time per book, chunks per second
- **Vector Database Health**: Query response times, storage utilization
- **Cost Tracking**: OpenAI API usage, Azure resource consumption
- **Quality Metrics**: Processing success rates, error frequencies

### Content Analytics
- **Search Performance**: Query accuracy, relevance scores
- **Usage Patterns**: Most searched books, popular content types
- **Quality Scores**: Expert validation ratings, user feedback
- **Processing Efficiency**: Resource utilization, optimization opportunities

## 🚨 Troubleshooting

### Common Issues

1. **Processing Fails**
   ```bash
   # Check source file structure
   python -c "import json; print(json.load(open('data/sources/raw-bg/bhagavad_gita_complete.json')))"
   
   # Verify registry file
   cat data/sources/books_registry.json | jq '.'
   ```

2. **Cosmos DB Connection Issues**
   ```bash
   # Test connection
   python -c "from pymongo import MongoClient; MongoClient('your-connection-string').admin.command('ping')"
   ```

3. **Embedding Generation Fails**
   ```bash
   # Check OpenAI API key
   python -c "import openai; print(openai.OpenAI().models.list())"
   ```

4. **Admin Dashboard Issues**
   ```bash
   # Check Flask configuration
   python -c "from book_registry_admin import app; print(app.config)"
   ```

### Error Codes

- **E001**: Source file not found or corrupted
- **E002**: Registry file malformed or inaccessible
- **E003**: Cosmos DB connection failure
- **E004**: OpenAI API authentication error
- **E005**: Vector index creation failed
- **E006**: Processing pipeline interrupted

## 📞 Support & Contributing

### Getting Help
- **Documentation**: Check PRD_Vimarsh.md and User_Experience.md
- **Issues**: Create GitHub issues for bugs and feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Code Style
- **Python**: Follow PEP 8, use Black formatter
- **HTML/CSS**: Maintain sacred design language consistency
- **JavaScript**: ES6+ features, consistent indentation
- **Comments**: Include docstrings for all public functions

---

## 🙏 Acknowledgments

This system enables the preservation and accessibility of timeless spiritual wisdom through modern AI technology, serving seekers worldwide with authentic guidance from sacred texts.

*May this tool serve the divine purpose of spreading spiritual knowledge and wisdom to all who seek it.*

🕉️ **Om Namah Shivaya** 🕉️
