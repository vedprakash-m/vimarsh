# Container Migration Resolution Guide

## Current Situation Analysis 

### ✅ Code Configuration (Correct)
Your `vector_database_service.py` is correctly configured:
- Database: `vimarsh-multi-personality` 
- Container: `personality-vectors`

### ❓ Azure Portal vs Code Mismatch
You see `spiritual-vectors` in Azure Portal but code expects `personality-vectors`.

### ❌ Missing Environment Configuration
No `.env` file or environment variables set for Cosmos DB connection.

## Immediate Action Plan

### Step 1: Set Up Environment Variables

Create a `.env` file in the `backend` directory with your actual values:

```bash
# Azure Cosmos DB Configuration
AZURE_COSMOS_CONNECTION_STRING=AccountEndpoint=https://your-actual-cosmos-account.documents.azure.com:443/;AccountKey=your-actual-key;
AZURE_COSMOS_DATABASE_NAME=vimarsh-multi-personality
AZURE_COSMOS_CONTAINER_NAME=personality-vectors

# Google AI Configuration (if using)
GOOGLE_AI_API_KEY=your-actual-gemini-api-key
```

### Step 2: Verify Actual Container Status

Once environment is set up, run:
```bash
cd backend/data_processing
python container_migration_manager.py
```

This will show you:
- What containers actually exist
- How many documents are in each
- Whether migration is needed

### Step 3A: If Data is in `spiritual-vectors`
The script will automatically migrate data to `personality-vectors` with enhanced metadata.

### Step 3B: If Data is Already in `personality-vectors`
The script will verify and enhance existing data with proper metadata structure.

## What the Migration Script Will Do

### For Existing Krishna Data (Bhagavad Gita & Isopanishad):
1. **Enhance metadata structure**:
   ```json
   {
     "id": "existing_document_id",
     "personality": "krishna",
     "content_type": "verse",
     "metadata": {
       "migrated_from": "spiritual-vectors",
       "migration_date": "2025-07-28T...",
       "original_source": "Bhagavad Gita",
       "authenticity_notes": "Existing Krishna content"
     }
   }
   ```

2. **Register with metadata management**:
   - Create `BookMetadata` entries for Gita and Isopanishad
   - Map vectors to their sources
   - Enable full provenance tracking

3. **Maintain existing embeddings**:
   - No re-embedding needed
   - Preserve all existing vector data
   - Just enhance metadata structure

## Expected Outcome

After migration, you'll have:
- ✅ All data in correct `personality-vectors` container
- ✅ Enhanced metadata for existing Krishna content  
- ✅ Ready to add new personalities with proper tracking
- ✅ Full provenance from vector → source book
- ✅ Proper citations for generated responses

## Next Steps After Migration

1. **Verify migration**: Check Azure Portal - should see `personality-vectors`
2. **Test existing functionality**: Ensure Krishna queries still work
3. **Add new personalities**: Use content sourcing pipeline for other personalities
4. **Enable metadata management**: Full tracking for all future content

## Quick Environment Setup

If you need help finding your Cosmos DB connection string:
1. Go to Azure Portal → Your Cosmos DB Account
2. Settings → Keys
3. Copy "Primary Connection String"
4. Add to `.env` file as shown above

Once environment is configured, the migration script will handle everything automatically!
