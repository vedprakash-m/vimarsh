# Vimarsh Data Directory

This directory contains data sources, caches, and runtime files for the Vimarsh spiritual guidance platform.

## 📁 Directory Structure

```
data/
├── sources/               # Spiritual text sources (gitignored - large files)
│   ├── books_registry.json      # ✅ Tracked: Book metadata registry
│   ├── scriptures_registry.json # ✅ Tracked: Scripture metadata  
│   ├── bhagavad_gita_clean.jsonl      # 🚫 Large file: Download separately
│   ├── sri_isopanisad_clean.jsonl     # 🚫 Large file: Download separately
│   └── raw-bg/                         # 🚫 Raw chapter files: Generate locally
├── cache/                 # 🚫 Runtime cache (gitignored)
├── cost_tracking/         # 🚫 Usage analytics (gitignored) 
├── demo_analytics/        # 🚫 Demo reports (gitignored)
├── real_time_monitoring/  # 🚫 Runtime state (gitignored)
├── real_time_demo/        # 🚫 Demo configs (gitignored)
├── validation_test/       # 🚫 Test data (gitignored)
├── spiritual_validation_test/ # 🚫 Test configs (gitignored)
├── test_vector_storage/   # 🚫 Test vectors (gitignored)
├── rag_llm_test_storage/  # 🚫 RAG test data (gitignored)
├── vector_storage/        # 🚫 Vector indices (gitignored)
├── vectors/              # 🚫 Vector data (gitignored)
└── vimarsh-db/           # ✅ Tracked: Sample database files
```

## 🚫 Gitignored Files (Not Synced)

These files are **not tracked in git** because they are:
- Large data files (>1MB)
- Runtime-generated files  
- Environment-specific data
- Cache and temporary files

### Large Spiritual Text Sources
- `sources/*.jsonl` - Processed spiritual texts (generated from scripts)
- `sources/raw-bg/` - Raw Bhagavad Gita chapter files
- `sources/raw-iso/` - Raw Isopanishad files

### Runtime Data
- `cache/` - Application cache files
- `cost_tracking/` - Daily usage tracking logs
- `demo_analytics/` - Analytics reports  
- `real_time_monitoring/` - Runtime monitoring state
- `vector_storage/` - Vector search indices
- `vectors/` - Computed embeddings

### Test Data
- `validation_test/` - Validation test configurations
- `spiritual_validation_test/` - Spiritual content test data
- `test_vector_storage/` - Test vector indices
- `rag_llm_test_storage/` - RAG pipeline test data

## ✅ Tracked Files (In Git)

### Configuration & Registry Files
- `cost_monitoring_config.json` - Cost monitoring configuration template
- `sources/books_registry.json` - Book metadata and registry
- `sources/scriptures_registry.json` - Scripture source registry
- `vimarsh-db/` - Sample database structure and test data

## 🔧 Setup Instructions

### 1. Initial Setup
Run the setup script to create directories and default configs:
```bash
./scripts/setup-data-sources.sh
```

### 2. Download Large Data Files
Large spiritual text files must be downloaded separately:
```bash
# Option 1: Use data processing scripts
python backend/scripts/download_personality_data.py

# Option 2: Generate from production database
python scripts/production_validator.py --export-data

# Option 3: Manual download from authoritative sources
# (See backend/scripts/create_basic_personality_content.py)
```

### 3. Verify Setup
```bash
# Check data structure
ls -la data/

# Validate configuration
python scripts/production_validator.py --validate-data
```

## 📊 File Size Guidelines

- **Small files** (<100KB): Can be tracked in git
- **Medium files** (100KB-1MB): Consider gitignoring  
- **Large files** (>1MB): Must be gitignored and downloaded separately

## 🔒 Security Notes

- **No API keys or secrets** should be stored in data files
- **User data** is never committed to git
- **Cost tracking** contains no sensitive information (aggregated only)
- **Spiritual texts** are from public domain sources

## 🛠️ Maintenance

### Clean Up Cache
```bash
rm -rf data/cache/*
rm -rf data/cost_tracking/*
rm -rf data/demo_analytics/*
```

### Regenerate Data Sources
```bash
./scripts/setup-data-sources.sh
python backend/scripts/create_basic_personality_content.py
```

### Update Registry Files
Registry files (`books_registry.json`, `scriptures_registry.json`) should be updated when:
- Adding new spiritual text sources
- Updating book metadata
- Changing source authentication information

---

**Note**: This data directory structure supports the complete Vimarsh platform including 12 personalities, RAG integration, vector search, and real-time analytics while keeping the git repository clean and performant.
