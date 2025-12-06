# Embedding Model Comparison for Vimarsh RAG Migration

**Date:** January 2025  
**Current Model:** Google `text-embedding-004` (768 dimensions)  
**Deprecation Date:** January 14, 2026  
**Application:** RAG-powered multi-personality spiritual guidance platform (~25 personalities, ~24,800 embeddings)

---

## Executive Summary

Your application currently uses Google's `text-embedding-004` which will be deprecated on January 14, 2026. This document provides a comprehensive analysis of replacement options, considering your Azure-hosted infrastructure, moderate traffic levels, and the need for high-quality semantic search across 25 diverse personalities.

### Top Recommendations

| Priority | Model | Why |
|----------|-------|-----|
| 🥇 **Best Overall** | Google `gemini-embedding-001` | Drop-in replacement, same SDK, enhanced features (MRL), free tier available |
| 🥈 **Best Azure Native** | Azure OpenAI `text-embedding-3-small` | Native Azure integration, competitive pricing, good quality |
| 🥉 **Best Performance** | Voyage AI `voyage-3-large` | Top MTEB scores, flexible dimensions, Azure Marketplace available |

---

## Current Implementation Analysis

### Codebase Touchpoints

Based on my analysis, embedding-related code exists in:

| File | Usage | Migration Impact |
|------|-------|------------------|
| `backend/services/gemini_embedding_service.py` | Primary embedding service, uses `text-embedding-004` | **HIGH** - Core service to update |
| `backend/services/enhanced_rag_service_v6.py` | Vector search, query embedding | **MEDIUM** - Uses genai.embed_content() |
| `backend/services/embedding_generator.py` | Batch embedding generation | **MEDIUM** - Production embedding pipeline |
| `backend/models/personality_models.py` | PersonalityConfig dataclass | **LOW** - Just field definition |
| `backend/config/ai_models.py` | Centralized model config | **LOW** - Configuration update |
| `scripts/upload-spiritual-texts.sh` | Uses sentence-transformers fallback | **LOW** - Alternative path |

### Current Embedding Specifications
- **Model:** `models/text-embedding-004`
- **Dimensions:** 768
- **SDK:** `google.generativeai` (genai)
- **Task Types:** `RETRIEVAL_DOCUMENT`, `RETRIEVAL_QUERY`
- **Vector Storage:** Azure Cosmos DB (`personality-vectors` container)
- **Total Embeddings:** ~24,800 documents

---

## Model Comparison Matrix

### Cloud-Hosted Models

| Model | Provider | Dimensions | Pricing (per 1M tokens) | MTEB Avg | Max Tokens | Free Tier |
|-------|----------|------------|------------------------|----------|------------|-----------|
| **gemini-embedding-001** | Google | 768/1536/3072 | $0.15 | 68.17 (1536d) | 2,048 | Yes (1,500 req/day) |
| **text-embedding-3-large** | Azure OpenAI | 256-3072 | $0.13 | 64.6 | 8,191 | No |
| **text-embedding-3-small** | Azure OpenAI | 512-1536 | $0.02 | 62.3 | 8,191 | No |
| **text-embedding-ada-002** | Azure OpenAI | 1536 | $0.10 | 61.0 | 8,191 | No |
| **voyage-3-large** | Voyage AI | 256-2048 | $0.18 | 67.3* | 32,000 | 200M tokens |
| **voyage-3.5** | Voyage AI | 1024 | $0.06 | 66.5* | 32,000 | 200M tokens |
| **voyage-3.5-lite** | Voyage AI | 1024 | $0.02 | 64.8* | 32,000 | 200M tokens |
| **embed-v4.0** | Cohere | 256-1536 | Variable | 67.0* | 128,000 | Limited |
| **embed-english-v3.0** | Cohere | 1024 | Variable | 64.5* | 512 | Limited |

*Estimated from vendor benchmarks

### Open Source / Self-Hosted Models

| Model | Dimensions | MTEB Avg | Speed | License | Azure Hosting |
|-------|------------|----------|-------|---------|---------------|
| **all-mpnet-base-v2** | 768 | 57.8 | ~170 sent/sec | Apache 2.0 | Container Apps |
| **all-MiniLM-L6-v2** | 384 | 50.2 | ~750 sent/sec | Apache 2.0 | Container Apps |
| **bge-large-en-v1.5** | 1024 | 63.5 | ~150 sent/sec | MIT | Container Apps |
| **bge-m3** | 1024 | 66.0 | ~100 sent/sec | MIT | Container Apps |
| **e5-large-v2** | 1024 | 62.7 | ~120 sent/sec | MIT | Container Apps |
| **gte-large-en-v1.5** | 1024 | 65.4 | ~130 sent/sec | Apache 2.0 | Container Apps |

---

## Detailed Model Analysis

### 1. Google gemini-embedding-001 (Recommended)

**Best for:** Minimal migration effort, production continuity

```python
# Migration: Single line change
# OLD:
result = genai.embed_content(model="models/text-embedding-004", content=text)

# NEW:
result = genai.embed_content(model="models/gemini-embedding-001", content=text)
```

**Pros:**
- ✅ Drop-in replacement - same SDK, same API structure
- ✅ Matryoshka Representation Learning (MRL) - reduce to 768d for compatibility
- ✅ Better MTEB scores (68.17 at 1536d vs text-embedding-004)
- ✅ Enhanced task types (8 total including `CODE_RETRIEVAL_QUERY`, `FACT_VERIFICATION`)
- ✅ Free tier: 1,500 requests/day
- ✅ Batch API at 50% discount

**Cons:**
- ⚠️ Shorter context (2,048 tokens vs 8,191 for OpenAI)
- ⚠️ Requires re-embedding for new dimensions (if upgrading from 768d)

**Pricing Estimate (25 personalities, ~25K docs):**
- Initial re-embedding: ~5M tokens ≈ $0.75
- Monthly queries (moderate traffic ~10K/day): ~1.5M tokens ≈ $0.225/month
- **Total Year 1:** ~$3.50

**Migration Strategy:**
```python
# Option A: Keep 768 dimensions (no re-embedding needed if using MRL)
genai.embed_content(
    model="models/gemini-embedding-001", 
    content=text,
    output_dimensionality=768  # MRL truncation
)

# Option B: Upgrade to 1536 dimensions (requires full re-embedding)
genai.embed_content(
    model="models/gemini-embedding-001", 
    content=text,
    output_dimensionality=1536
)
```

---

### 2. Azure OpenAI text-embedding-3-small

**Best for:** Azure-native integration, cost optimization

**Pros:**
- ✅ Native Azure integration via Azure OpenAI Service
- ✅ Extremely cost-effective ($0.02/1M tokens)
- ✅ Longer context (8,191 tokens)
- ✅ Dimension flexibility (512-1536)
- ✅ Same VNet as your Functions app
- ✅ Azure AI Search integrated vectorization support

**Cons:**
- ⚠️ Lower MTEB scores than Gemini/Voyage
- ⚠️ Requires Azure OpenAI resource provisioning
- ⚠️ Different SDK (`openai` instead of `genai`)

**Pricing Estimate:**
- Initial re-embedding: ~5M tokens ≈ $0.10
- Monthly queries: ~1.5M tokens ≈ $0.03/month
- **Total Year 1:** ~$0.50

**Azure Integration:**
```python
from openai import AzureOpenAI

client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2024-02-15-preview"
)

response = client.embeddings.create(
    model="text-embedding-3-small",
    input=text,
    dimensions=768  # Match current vector dimensions
)
embedding = response.data[0].embedding
```

---

### 3. Azure OpenAI text-embedding-3-large

**Best for:** Best quality within Azure ecosystem

**Pros:**
- ✅ Highest quality Azure-native option (MTEB 64.6)
- ✅ Best multilingual support (MIRACL 54.9)
- ✅ Flexible dimensions up to 3072
- ✅ All Azure integration benefits

**Cons:**
- ⚠️ Higher cost than 3-small
- ⚠️ Still lower MTEB than Gemini/Voyage

**Pricing Estimate:**
- Initial re-embedding: ~5M tokens ≈ $0.715
- Monthly queries: ~1.5M tokens ≈ $0.215/month
- **Total Year 1:** ~$3.30

---

### 4. Voyage AI voyage-3-large

**Best for:** Maximum retrieval quality

**Pros:**
- ✅ Top-tier MTEB scores (67.3+)
- ✅ 32K context window (excellent for long documents)
- ✅ Available on Azure Marketplace
- ✅ Domain-specific variants (law, finance, code)
- ✅ 200M token free tier

**Cons:**
- ⚠️ Higher cost ($0.18/1M tokens)
- ⚠️ New vendor relationship
- ⚠️ Different SDK

**Pricing Estimate:**
- Initial re-embedding: ~5M tokens ≈ $0.90
- Monthly queries: ~1.5M tokens ≈ $0.27/month
- **Total Year 1:** ~$4.14

**Implementation:**
```python
import voyageai

client = voyageai.Client(api_key=os.getenv("VOYAGE_API_KEY"))

result = client.embed(
    texts=[text],
    model="voyage-3-large",
    input_type="document"  # or "query" for search queries
)
embedding = result.embeddings[0]
```

---

### 5. Self-Hosted (Sentence Transformers)

**Best for:** Full control, no per-token costs

**Pros:**
- ✅ No per-request costs after deployment
- ✅ Data never leaves your infrastructure
- ✅ Full control over model updates
- ✅ You already have `all-MiniLM-L6-v2` in scripts

**Cons:**
- ⚠️ Requires Azure Container Apps or dedicated compute
- ⚠️ Cold start latency
- ⚠️ Lower quality than cloud APIs
- ⚠️ Maintenance burden

**Hosting Options on Azure:**
1. **Azure Container Apps** - Serverless, scale to zero, ~$50-100/month at moderate traffic
2. **Azure Kubernetes Service** - More control, higher base cost
3. **Azure Functions + Docker** - Complex, cold start issues

**Cost Estimate (Container Apps):**
- Container Apps: ~$50-100/month
- **Total Year 1:** ~$600-1,200 (vs $3-50 for cloud APIs)

**Only recommended if:**
- You have >100K queries/month
- Data sovereignty is critical
- You have DevOps capacity for container management

---

## Critical Migration Considerations

### Can Different Embedding Models Be Used Together?

**Short answer: No, you need full re-embedding.**

Embeddings from different models exist in incompatible vector spaces. Even if dimensions match (e.g., both 768d), the semantic representations are different. Mixing embeddings will result in:
- Incorrect similarity calculations
- Random/nonsensical search results
- Degraded RAG quality

**Migration Requirement:** All ~24,800 documents must be re-embedded with the new model.

### Re-Embedding Strategy

```python
# Recommended migration approach
async def migrate_embeddings(new_model: str):
    """Batch re-embed all documents"""
    
    # 1. Create backup of current embeddings
    await backup_cosmos_container("personality-vectors", "personality-vectors-backup")
    
    # 2. Re-embed in batches (100 docs per batch)
    for batch in get_document_batches(batch_size=100):
        new_embeddings = await generate_embeddings_batch(batch, model=new_model)
        await update_cosmos_embeddings(batch, new_embeddings)
        
    # 3. Validate search quality
    await run_search_quality_tests()
    
    # 4. Update application config
    update_embedding_model_config(new_model)
```

### Dimension Considerations

| Current | Target | Action Required |
|---------|--------|-----------------|
| 768d | 768d | Re-embed only (MRL if available) |
| 768d | 1024d+ | Re-embed + update Cosmos DB index + update search code |

If upgrading dimensions, update:
1. Cosmos DB container indexing policy
2. Vector search queries
3. Any dimension-specific code

---

## Azure-Specific Integrations

### Azure AI Search Integrated Vectorization

If you decide to move from Cosmos DB to Azure AI Search:

**Benefits:**
- Built-in vectorization (no separate embedding service needed)
- Automatic chunking with Text Split skill
- Hybrid search (BM25 + vector) out of the box
- Semantic ranker for re-ranking

**Supported Models:**
- Azure OpenAI embeddings (ada-002, 3-small, 3-large)
- Custom skills for other models

**Implementation:**
```json
{
  "name": "vector-skill",
  "@odata.type": "#Microsoft.Skills.Text.AzureOpenAIEmbeddingSkill",
  "resourceUri": "[your-azure-openai-endpoint]",
  "deploymentId": "text-embedding-3-small",
  "modelName": "text-embedding-3-small"
}
```

### Azure OpenAI Provisioned Throughput

For consistent performance at scale:
- Provisioned Throughput Units (PTU) guarantee capacity
- More cost-effective at high volume
- Consider if >50K embeddings/month

---

## Cost Comparison Summary

### Initial Re-Embedding Cost (~25K documents, ~5M tokens)

| Model | Cost |
|-------|------|
| Gemini gemini-embedding-001 | $0.75 |
| Azure OpenAI 3-small | $0.10 |
| Azure OpenAI 3-large | $0.71 |
| Voyage voyage-3-large | $0.90 |
| Self-hosted | $0 (compute only) |

### Annual Operating Cost (Moderate traffic: ~300K queries/month)

| Model | Monthly | Annual |
|-------|---------|--------|
| Gemini gemini-embedding-001 | $0.45 | $5.40 |
| Azure OpenAI 3-small | $0.06 | $0.72 |
| Azure OpenAI 3-large | $0.43 | $5.16 |
| Voyage voyage-3-large | $0.54 | $6.48 |
| Self-hosted (Container Apps) | $75 | $900 |

**Note:** At your current scale (~25 personalities, moderate traffic), cloud APIs are dramatically more cost-effective than self-hosting.

---

## Migration Timeline

### Recommended Approach: Phased Migration to gemini-embedding-001

```
Phase 1 (Week 1-2): Preparation
├── Update gemini_embedding_service.py to support both models
├── Add feature flag for model switching
├── Create embedding migration script
└── Set up staging environment

Phase 2 (Week 3-4): Staging Migration
├── Re-embed all documents in staging
├── Run search quality benchmarks
├── Compare retrieval accuracy
└── Performance testing

Phase 3 (Week 5): Production Migration
├── Create production backup
├── Run migration during low-traffic window
├── Validate search results
└── Monitor for issues

Phase 4 (Week 6): Cleanup
├── Remove old model code
├── Update documentation
├── Archive migration scripts
└── Document lessons learned
```

---

## Final Recommendation

### For Vimarsh's Specific Needs:

**Primary Choice: Google `gemini-embedding-001`**

| Factor | Assessment |
|--------|------------|
| Migration Effort | ⭐⭐⭐⭐⭐ Minimal - same SDK |
| Quality | ⭐⭐⭐⭐⭐ Best MTEB scores |
| Cost | ⭐⭐⭐⭐ Very affordable |
| Azure Compatibility | ⭐⭐⭐⭐ Works from Azure Functions |
| Future-Proof | ⭐⭐⭐⭐ New model, active development |

**Why not Azure OpenAI?**
- Lower quality scores (62-64 vs 68 MTEB)
- Additional Azure resource setup
- SDK change required

**Why not Voyage AI?**
- New vendor relationship
- Higher cost
- SDK change required
- Overkill for your use case

**Why not Self-Hosted?**
- Much higher operational cost ($900/year vs $5/year)
- DevOps burden
- Lower quality

---

## Appendix: Code Migration Example

### Current Implementation (text-embedding-004)

```python
# backend/services/gemini_embedding_service.py
class GeminiEmbeddingService:
    def __init__(self, model_name: str = "models/text-embedding-004", ...):
        self.model_name = model_name
        self.dimension = 768
```

### Migrated Implementation (gemini-embedding-001)

```python
# backend/services/gemini_embedding_service.py
class GeminiEmbeddingService:
    def __init__(
        self, 
        model_name: str = "models/gemini-embedding-001",
        output_dimensionality: int = 768,  # Use MRL for compatibility
        ...
    ):
        self.model_name = model_name
        self.dimension = output_dimensionality
        
    def generate_embedding(self, text: str, task_type: str = "RETRIEVAL_DOCUMENT") -> EmbeddingResult:
        result = genai.embed_content(
            model=self.model_name,
            content=self._clean_text(text),
            task_type=task_type,
            output_dimensionality=self.dimension  # MRL truncation
        )
        return EmbeddingResult(
            embedding=result['embedding'],
            model=self.model_name,
            dimension=len(result['embedding']),
            text_length=len(text)
        )
```

---

## References

- [Google AI Embedding Models](https://ai.google.dev/gemini-api/docs/embeddings)
- [Azure OpenAI Embeddings](https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/models#embeddings-models)
- [MTEB Leaderboard](https://huggingface.co/spaces/mteb/leaderboard)
- [Voyage AI Documentation](https://docs.voyageai.com/)
- [Sentence Transformers](https://www.sbert.net/)
