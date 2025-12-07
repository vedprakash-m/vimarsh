# RAG Verification Guide

## How to Verify RAG is Working (Not Just Direct LLM)

This guide helps you confirm that your RAG (Retrieval-Augmented Generation) pipeline is actually retrieving content from your vector database (24,799 embeddings) rather than just having the LLM respond directly from its training data.

---

## 🎯 Quick Verification Checklist

**RAG is working when you see:**
- ✅ `content_backed: true` in response metadata
- ✅ `citations` array has source references
- ✅ `chunks_used > 0` (typically 3-5)
- ✅ `avg_similarity > 0.5` (typically 0.7-0.9)
- ✅ `response_source: "enhanced_rag_gemini"`
- ✅ Backend logs show vector search activity

**LLM is responding directly (RAG not used) when:**
- ❌ `content_backed: false`
- ❌ `citations` is empty `[]`
- ❌ `chunks_used: 0`
- ❌ `response_source: "enhanced_llm"` or `"personality_service"`
- ❌ Backend logs show RAG fallback messages

---

## 📊 Method 1: API Response Metadata (Primary Method)

Every response from `/api/guidance` includes detailed metadata:

```json
{
  "response": "As Lord Krishna teaches in the Bhagavad Gita...",
  "personality": { ... },
  "metadata": {
    // RAG-specific metrics
    "content_backed": true,                      // ✅ Using source content
    "citations": [                                // ✅ Sources cited
      "Bhagavad Gita 2.47",
      "Bhagavad Gita 3.19"
    ],
    "chunks_used": 3,                            // ✅ Content chunks retrieved
    "retrieval_method": "vector_similarity",     // ✅ How content was found
    "avg_similarity": 0.847,                     // ✅ Relevance score (0-1)
    "confidence_score": 0.856,                   // ✅ Overall confidence
    
    // General metadata
    "response_source": "enhanced_rag_gemini",    // ✅ Service used
    "ai_generated": true,
    "language": "en",
    "service_mode": "enhanced"
  }
}
```

### Understanding the Metrics

| Metric | Meaning | Good Value | Poor Value |
|--------|---------|------------|------------|
| `content_backed` | Response uses retrieved content | `true` | `false` |
| `chunks_used` | Number of content chunks retrieved | 3-5 | 0 |
| `avg_similarity` | How relevant chunks are to query | 0.7-0.9 | < 0.5 |
| `confidence_score` | Overall response confidence | > 0.7 | < 0.5 |
| `citations` | Source references | 1-3 items | empty |

---

## 🔍 Method 2: Backend Logs

When RAG is working, you'll see this sequence in logs:

```bash
# Query received
🕉️ Processing multi-domain guidance request

# RAG pipeline active
📊 Found 245 chunks with embeddings for krishna
🎯 Vector search returned 5 top chunks
📈 Similarity scores: ['0.847', '0.823', '0.801', '0.789', '0.765']
📚 Retrieved context: 5 chunks, avg similarity: 0.805
✅ Generated enhanced RAG response: 847 chars, confidence: 0.856

# Success
✅ Enhanced RAG service provided response (confidence: 0.856, content-backed: true)
```

### When RAG Fails (Fallback to LLM)

```bash
⚠️ Enhanced RAG service failed: <error>, falling back to enhanced LLM
✅ Enhanced LLM service provided response (source: enhanced_llm)
```

---

## 🧪 Method 3: Run Verification Test

Execute the RAG verification script:

```bash
cd /Users/ved/Apps/vimarsh/backend
source ../.venv/bin/activate
python test_rag_verification.py
```

This will test multiple queries and show:
- Whether RAG retrieved content for each query
- Citation quality
- Similarity scores
- Overall RAG health

---

## 🎨 Method 4: Admin UI Badge (Frontend)

If you're logged in as admin, you'll see a badge on each message showing the source:

```tsx
[📊 RAG] // content-backed: true, using vector retrieval
[🤖 LLM] // direct LLM response, no retrieval
[📋 Template] // fallback template response
```

The code is in `GuidanceInterface.tsx`:
```tsx
{message.metadata && user?.role === 'admin' && (
  <MessageSourceBadge metadata={message.metadata} compact={true} />
)}
```

---

## 💡 Method 5: Ask Domain-Specific Questions

Test with queries that require specific source content:

### Good Test Queries

**For Krishna (Bhagavad Gita):**
- "What does Krishna say in chapter 2 verse 47?"
- "Explain the concept of Karma Yoga"
- "What is the path of detachment?"

**For Einstein:**
- "What did Einstein say about imagination vs knowledge?"
- "Explain relativity in simple terms"

**For Buddha:**
- "What are the Four Noble Truths?"
- "How can I practice mindfulness?"

### Expected RAG Response vs Direct LLM

| Aspect | RAG Response | Direct LLM Response |
|--------|--------------|---------------------|
| **Specificity** | Exact verse/chapter citations | Generic references |
| **Language** | Original terminology (karma, dharma) | Paraphrased concepts |
| **Citations** | "Bhagavad Gita 2.47" | "ancient teachings" |
| **Accuracy** | Matches source texts | Common knowledge |
| **Metadata** | `content_backed: true` | `content_backed: false` |

---

## 🔧 Troubleshooting: RAG Not Working

If `content_backed: false` consistently:

### 1. Check Database Connection
```bash
cd backend
python -c "
from services.enhanced_rag_service_v6 import EnhancedRAGService
import asyncio
async def test():
    service = EnhancedRAGService()
    print(f'✅ Connected to: {service.database.id}')
asyncio.run(test())
"
```

### 2. Verify Embeddings Exist
```bash
cd backend
python -c "
from services.enhanced_rag_service_v6 import EnhancedRAGService
import asyncio
async def test():
    service = EnhancedRAGService()
    chunks = await service.vector_search('peace', 'krishna', top_k=5)
    print(f'Found {len(chunks)} chunks')
    for c in chunks: print(f'  - {c.source}: {c.similarity_score:.3f}')
asyncio.run(test())
"
```

### 3. Check Environment Variables
```bash
# Required for RAG
echo $AZURE_COSMOS_CONNECTION_STRING
echo $GEMINI_API_KEY  # For embeddings
```

### 4. Review Diagnostic Endpoint
```bash
curl http://localhost:7071/api/diagnostic
```

Look for:
```json
{
  "tests": {
    "cosmos_db": {"status": "connected"},
    "enhanced_rag_service": {"status": "initialized"}
  }
}
```

---

## 📈 Understanding the RAG Pipeline

```
User Query
    ↓
1. Generate Query Embedding (Gemini)
    ↓
2. Vector Search in Cosmos DB (24,799 embeddings)
    ↓
3. Retrieve Top 3-5 Chunks (sorted by similarity)
    ↓
4. Build Enhanced Prompt (context + personality + query)
    ↓
5. Generate Response (Gemini + retrieved context)
    ↓
6. Return with Metadata (citations, confidence, etc.)
```

### Key Files
- **RAG Service:** `backend/services/enhanced_rag_service_v6.py`
- **Function Handler:** `backend/function_app.py` (lines 2216-2259)
- **Database:** Cosmos DB `personality_vectors` container
- **Embeddings:** 24,799 chunks across 25 personalities

---

## 🎯 Success Criteria

**Your RAG is working correctly when:**

1. ✅ **High Content-Backed Rate:** > 80% of responses have `content_backed: true`
2. ✅ **Good Similarity Scores:** Average > 0.7 for domain-specific queries
3. ✅ **Citations Present:** Most responses include source references
4. ✅ **Appropriate Chunking:** 3-5 chunks per response
5. ✅ **Fast Retrieval:** Vector search completes in < 500ms
6. ✅ **Correct Fallback:** Only falls back to LLM when truly necessary

---

## 📞 Quick Reference

| Check | Command/Location |
|-------|------------------|
| **API Metadata** | Response JSON at `/api/guidance` |
| **Backend Logs** | Azure Functions logs or terminal output |
| **Test Script** | `python backend/test_rag_verification.py` |
| **Admin Badge** | Frontend UI (admin users only) |
| **Diagnostic** | `GET /api/diagnostic` |

---

## 🚀 Next Steps

If RAG is not working:
1. Run `test_rag_verification.py` for detailed diagnostics
2. Check backend logs for initialization errors
3. Verify Cosmos DB has embeddings: `data/validate_embeddings.py`
4. Ensure Gemini API quota is available
5. Review `enhanced_rag_service_v6.py` initialization

If RAG is working:
1. Monitor `avg_similarity` scores to optimize retrieval
2. Expand test coverage with more personalities
3. Fine-tune chunking strategy if needed
4. Consider implementing hybrid search (vector + keyword)
