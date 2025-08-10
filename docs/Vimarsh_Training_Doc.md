# Vimarsh Project Training Document (Engineering Deep Dive)

Status reference date: 2025-08-10 (analysis of main branch codebase)

---

## 1. High-Level Introduction

Purpose: Vimarsh is a multi-personality AI guidance platform delivering responses in the style of historical, spiritual, philosophical, and scientific figures. It blends template responses, an evolving Retrieval Augmented Generation (RAG) stack, and emerging conversation memory.

North Star:
- Authentic, citation-grounded multi-tradition wisdom delivery
- Scalable RAG pipeline with hybrid search + citation grounding
- Progressive personalization (memory, preferences, journaling—partially scaffolded)
- Operational reliability via modular services & Azure serverless model

Value Proposition:
- Multi-domain perspective switching (12 personalities)
- Explainability through citations (pipeline partially implemented)
- Extensible architecture for future LLM + memory enrichment
- Admin observability endpoints (fallback + progressive enhancement pattern)

Primary Use Cases:
1. Ask guidance questions to a selected personality
2. Explore historically contextualized responses (templated or RAG-backed)
3. (Planned) Persist conversation memory across sessions
4. (Planned) Track insights via wisdom journal
5. Admin monitoring of personalities, content sources, usage metrics
6. Benchmark/QA retrieval + grounding quality (scripts/tests)

---

## 2. Detailed System Architecture

### 2.1 Layered Overview

1. Frontend (React 18 / TypeScript) – Personality selection UI, conversation interface (some legacy components pending refactor, not deeply covered here).  
2. API Layer – Azure Functions (`backend/function_app.py`) hosting HTTP endpoints: health, personalities, guidance, admin endpoints (role, monitoring, dashboard, cost, users, personalities, content sources, settings).  
3. Core Services: PersonalityService, ConversationMemoryService, Simple / Enhanced RAG services, VectorDatabaseService, Hybrid Search, Citation Grounding Checker, Data Pipeline Integration Service.  
4. Data Layer: Cosmos DB (vector embeddings + planned conversation / journal + preferences), local dataset artifacts in `data/`.  
5. Support & Ops: Performance monitoring scripts, production validator, dataset enhancement scripts, refactor/fix scripts.

### 2.2 Modularity & Fallback Strategy
Pattern: Each service attempts import/init; on ImportError falls back to simplified or static behavior. Enables partial deployments and progressive capability loading.

### 2.3 RAG Architecture (Current vs Target)
Current:
- SimpleRAGService: local JSON-based retrieval + basic citations
- EnhancedRAGService: orchestrates HybridSearchService, VectorDatabaseService, CitationGroundingChecker (if present)
- DataPipelineIntegrationService: bridges enhanced retrieval with legacy RAG format

Target (per code comments & scripts):
- Hybrid (BM25 + vector fusion)
- Citation precision & hallucination risk scoring
- Aggregated quality metrics persistence

### 2.4 Deployment Model
- Azure Functions (anonymous auth for public endpoints; unified auth service for admin)  
- Cosmos DB for vector storage (multi-personality structure)  
- Embeddings: Gemini model integration (GeminiTransformer wrapper)  
- Serverless scaling + cost controls (pause/resume philosophy)  

---

## 3. Detailed Data Model

### 3.1 Personality Models (`models/personality_models.py`)
`PersonalityConfig`: id, name, domain enum, description, safety_level, max_response_length, greeting_style, tone_indicators. 12 entries in `PERSONALITY_CONFIGS`.

### 3.2 Conversation & Memory (`models/conversation_models.py`)
Entities: ConversationSession, ConversationMessage, WisdomJournalEntry, UserPreferences.  
Enums: ConversationStatus, MessageType, JournalEntryType.  
Cosmos container specs in `CONVERSATION_CONTAINERS`: sessions, messages, journal, user-preferences.

### 3.3 Vector Documents (`services/vector_database_service.py`)
`VectorDocument` with personality (PersonalityType enum), content_type, embedding, metadata. `SearchResult` holds relevance. `DatabaseStats` used for admin.

### 3.4 RAG Response Structures
- SimpleRAGService → `RAGResponse`
- EnhancedRAGService → `EnhancedRAGResult`
- RAGIntegration/DataPipeline → `RAGContext`, `EnhancedSpiritualResponse`

### 3.5 Fallback Personality Data
`FALLBACK_PERSONALITIES` used if personality models not imported.

---

## 4. Data Flow (Key Scenarios)

### 4.1 Guidance Request (`POST /api/guidance`)
1. Parse body (query, personality_id, language, user_id).  
2. Validate query + personality (fallback to krishna).  
3. Optional ConversationMemoryService: start session, gather recent context, build enhancement.  
4. PersonalityService: LLM path (if LLMService loaded) else template.  
5. Store messages (if memory + DB available).  
6. Return response + metadata (service_mode, memory_enhanced, lengths).  
Fallback: templates if memory/LLM absent.

### 4.2 Personality Listing (`GET /api/personalities/active`)
Domain filter → list from configs or fallback set.

### 4.3 Admin Role (`GET /api/vimarsh-admin/role`)
UnifiedAuthService extraction → AdminService or environment variable fallback; in-function cache.

### 4.4 Enhanced RAG Retrieval
EnhancedRAGService orchestrates: retrieval (hybrid/vector) → simple RAG generation → optional citation validation → quality metrics update → fallback to simple RAG on error.

### 4.5 Data Pipeline Integration
Hybrid search → legacy RAG generation → optional citation validation → integrated DTO.

### 4.6 Conversation Memory
In-memory session cache + optional DB storage. Topic extraction (keyword match), simple user pattern inference.

### 4.7 Vector Embedding Lifecycle
`add_content` → embed (Gemini) → upsert Cosmos → stats update. `semantic_search` manually scores cosine similarity. Bulk embedding + duplicate cleanup utilities.

### 4.8 Performance Monitoring
`rag_performance_monitor.py` hits live endpoint for each personality, records latency & success, emits JSON + MD report.

### 4.9 Dataset Enhancement Scripts
Generate status documents (embedding coverage, authenticity, readiness) during content ingestion/enhancement phases.

---

## 5. Code Walkthrough (Core Components)

### 5.1 `function_app.py`
Registers Azure Functions endpoints. Uses try/except guarded imports for services (personality, memory, safety, admin). Guidance endpoint builds context, calls PersonalityService, stores memory.

### 5.2 PersonalityService
Template response map with optional LLMService integration; event loop created per call for async LLM (refactor candidate). Metadata includes response_source.

### 5.3 ConversationMemoryService
Async interface, session cache, topic extraction, user pattern heuristic, optional DB persistence through Phase 2 database service.

### 5.4 EnhancedRAGService
Initializes: SimpleRAGService, VectorDatabaseService, HybridSearchService, CitationGroundingChecker (if importable). Tracks quality metrics, provides fallback.

### 5.5 VectorDatabaseService
Cosmos DB vector container init, embedding model wrapper (GeminiTransformer). Manual similarity scoring; stats, export, cleanup, health checks.

### 5.6 DataPipelineIntegrationService
Transitional orchestrator bridging hybrid retrieval and legacy RAG interface, with optional citation validation and metrics.

### 5.7 Validation & Tests
`test_simple_rag_fix.py`, `test_enhanced_rag_integration.py` verify import flows, citation validation, enhanced performance metrics. Production validator script tests remote endpoints & citation shapes.

---

## 6. Refactor & Architectural Improvements

### 6.1 Async Hygiene
Convert guidance endpoint to async; remove custom loops, rely on shared event loop.

### 6.2 Dependency Injection
Introduce central registry (capability manifest) returning stub (null object) implementations when unavailable.

### 6.3 Config Management
Consolidate environment usage via pydantic-based settings module; load once at cold start.

### 6.4 Memory Persistence
Formal repository layer (ConversationRepo, MessageRepo). Add summarization for long histories; paginate retrieval.

### 6.5 RAG Unification
Merge EnhancedRAGService + DataPipelineIntegrationService behind strategy pattern for retrieval tiers (simple / hybrid / hybrid+validation).

### 6.6 Observability
Structured JSON logging, correlation IDs, OpenTelemetry traces for retrieval, generation, validation stages.

### 6.7 Vector Layer Optimization
Adopt native vector topK queries (when fully supported) instead of client-side cosine. Add embedding version metadata & ANN warm cache.

### 6.8 Security
Require auth for guidance (derive user_id from token). Add role checks for memory writes. Implement input sanitization layer.

### 6.9 Code Quality
Introduce mypy strict, unify tests under `backend/tests`, add Pydantic/Zod schema validation on requests.

### 6.10 Performance
Add query response caching keyed by (personality, normalized query). Async batch embedding queue. Rate limit expensive retrieval endpoints.

### 6.11 Testing
Segment test suites (unit/integration/performance). Mock Gemini + Cosmos in fixtures. Add contract tests for personality tone indicators.

### 6.12 Documentation Alignment
Create `docs/status.md` matrix: Implemented vs Planned. Auto-generate API spec. Maintain change log for capability manifest.

---

## 7. Known Gaps vs Code Reality

| Claim/Intent | Actual State | Action |
|--------------|-------------|--------|
| Persistent memory | Partial (in-memory + optional DB) | Implement repositories & full persistence |
| Hybrid search always active | Conditional import | Capability manifest endpoint |
| Universal citation grounding | Only when checker imported | Expose validation flag in response |
| Dynamic LLM responses ubiquitous | Template fallback common | Surface response_source to UI |
| Rich admin analytics | Mostly fallback static data | Implement aggregation jobs |
| Full auth protection | Guidance open | Enforce token + RBAC |

---

## 8. Junior Engineer Onboarding

First Week Checklist:
1. Read this doc + `README.md`.
2. `pip install -r backend/requirements.txt`; run `func host start`.
3. `GET /api/health` verify personalities list.
4. `POST /api/guidance` sample query.
5. Run `python backend/test_simple_rag_fix.py`.
6. Inspect `services/personality_service.py`, `services/rag_service.py`.
7. Explore `services/enhanced_rag_service.py`, `services/vector_database_service.py`.
8. Review dataset scripts for ingestion patterns.

Common Changes:
- Add personality: update `PERSONALITY_CONFIGS`, template response.
- Improve retrieval: implement new `RetrievalStrategy` and register.
- Adjust embeddings: modify `_initialize_embedding_model`.

Debug Tips:
- Template only response → LLM import failure.
- Memory absent → conversation service import failure.
- Empty vector results → check Cosmos env vars.
- Citation precision always 0 → checker disabled.

---

## 9. API Surface (Effective)

| Endpoint | Method | Purpose | Auth |
|----------|--------|---------|------|
| /api/health | GET | Availability & capabilities | None |
| /api/personalities/active | GET | Personality list (filterable) | None |
| /api/guidance | POST | Generate response | None (planned protected) |
| /api/vimarsh-admin/role | GET | Role resolution | Required |
| /api/vimarsh-admin/monitoring | GET | Monitoring stats | Required |
| /api/vimarsh-admin/dashboard | GET | Analytics | Required |
| /api/vimarsh-admin/cost-dashboard | GET | Cost analytics | Required |
| /api/vimarsh-admin/users | GET | User list | Required |
| /api/vimarsh-admin/personalities | GET | Personality mgmt | Required |
| /api/vimarsh-admin/content-sources | GET | Content sources | Required |
| /api/vimarsh-admin/settings | GET | System settings | Required |

(Note: Enhanced RAG endpoints not directly exposed; triggered within services/tests.)

---

## 10. Operational & Monitoring Components

Scripts:
- `rag_performance_monitor.py` – latency & success metrics across personalities.
- `production_validator.py` – endpoint & citation structure validation.
- Dataset scripts – embedding coverage & authenticity status outputs.

Recommended Additions: Timer-triggered Azure Function for daily performance; Application Insights integration.

---

## 11. Security Considerations
Current: Auth only on admin endpoints; user_id accepted from request body (spoof risk).  
Planned: JWT-derived user identity, rate limiting, conversation data minimization, structured audit logging.

---

## 12. Performance Considerations
Issues: Full container scans for semantic search; no caching; event loop overhead.  
Optimizations: Native vector topK queries, query caching, pre-warmed embeddings index, async pooling, rate limiting.

---

## 13. Quality & Reliability
Fallback Philosophy: Degradation to templates rather than failure.  
Enhancement: Capability manifest + alerts when a previously available module disappears.

---

## 14. Extension Paths
1. Wisdom journal CRUD + semantic recall.  
2. Personalization loop (adaptive tone, suggestions).  
3. Multi-strategy retrieval ranking.  
4. Observability upgrade (tracing, metrics pipeline).  
5. Multi-language expansion.  

---

## 15. Quick Reference Cheat Sheet

| Task | File(s) |
|------|---------|
| Add personality | `backend/models/personality_models.py`, `services/personality_service.py` |
| Adjust template responses | `services/personality_service.py` |
| Debug memory | `services/conversation_memory_service.py` |
| RAG extension | `services/enhanced_rag_service.py` |
| Vector DB logic | `services/vector_database_service.py` |
| Validate RAG import | `backend/test_simple_rag_fix.py` |
| Health check | `/api/health` |
| Sample guidance call | `/api/guidance` |

---

## 16. Immediate Action Recommendations
1. Async refactor of guidance endpoint.  
2. Capability manifest in health output.  
3. Dependency registry & null objects.  
4. Enforce auth (feature flag).  
5. Add unit tests for retrieval fallback + memory context formatting.  
6. Status matrix doc (implemented vs planned).  

---

## 17. Glossary
Hybrid Search: Fusion lexical + vector retrieval.  
Citation Grounding: Validating cited passages & computing precision.  
Fallback Mode: Template-only response path.  
Conversation Context: Rolling window of recent dialogue + inferred patterns.  
Retrieval Score: Similarity / relevance metric.  
Hallucination Risk: Heuristic classification from validation process.

---

## 18. Caveats & Accuracy Notes
- README includes aspirational claims; this document distinguishes actual vs planned.  
- Some enhanced modules may be absent in certain deployments; fallback pathways deliberate.  
- Fallback ensures availability but can mask regressions—monitor capability manifest.

---

End of training document.
