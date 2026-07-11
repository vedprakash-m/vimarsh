# Technical Specification: Vimarsh

| Field | Value |
|---|---|
| **Product** | Vimarsh — AI-Powered Multi-Personality Conversational Wisdom Platform |
| **Version** | 2.1 (April 2026) |
| **Status** | Production — Live at [vimarsh.vedmishra.com](https://vimarsh.vedmishra.com) |
| **Architecture** | Serverless microservices on Azure |
| **Integrity** | Stateless workers with External Session State (TTL 1800s) |

---

## 1. Architecture Overview

### 1.1 High-Level Architecture

```
                          ┌──────────────────────────────────────┐
                          │        Azure Static Web Apps         │
                          │   (vimarsh-frontend / React 18 PWA)  │
                          │   vimarsh.vedmishra.com              │
                          └──────────────┬───────────────────────┘
                                         │ HTTPS / SSE (Streaming)
                                         ▼
                    ┌────────────────────────────────────────────────┐
                    │   Azure Functions (Flex Consumption Plan)      │
                    │   vimarsh-backend-app-flex                     │
                    │   Python 3.12 · Stateless Worker Nodes         │
                    └───┬──────┬──────┬──────┬──────┬───────────────┘
                        │      │      │      │      │
            ┌───────────┘      │      │      │      └──────────┐
            ▼                  ▼      ▼      ▼                 ▼
     ┌──────────┐    ┌────────────────────────────┐    ┌──────────────┐
     │ Azure    │    │   Azure OpenAI Service      │    │ Azure Speech │
     │ Cosmos   │    │   (vimarsh-openai)           │    │ Service      │
     │ DB       │    │                              │    │ (TTS/SSML)   │
     │ (State)  │    │ Chat: gpt-5.4-mini (SSE)     │    └──────────────┘
     │ 11+ cont.│    │ Embed: text-embedding-3-large│
     └──────────┘    └────────────────────────────────┘
```

### 1.2 Design Principles
1. **100% Azure-native** — No cross-cloud dependencies (migrated from Google Gemini, Dec 2025)
2. **Stateless Resilience** — 100% of working memory and session state offloaded to Cosmos `session_state` (TTL enabled) to prevent OOM in ephemeral workers.
3. **Hardware Sympathy** — Minimal abstraction between the streaming LLM buffer and the browser DOM.
4. **Structured Handoffs** — Strict JSON Schema enforcement for all personality configurations and agentic memory extracts.

---

## 2. Backend Architecture

### 2.1 Azure Functions Application

**Runtime:** Python 3.12 on Azure Functions Flex Consumption Plan  
**Entry Point:** `backend/function_app.py`  
**Auth Level:** `func.AuthLevel.ANONYMOUS` (JWT validation handled per-route)

#### Route Registration Architecture

The application uses a modular blueprint architecture:

| Module | File | Routes | Purpose |
|---|---|---|---|
| **Guidance** | `routes/guidance_bp.py` | Spiritual guidance endpoint | Core conversation AI |
| **Personalities** | `routes/personalities_bp.py` | Active personality listing | Personality catalog |
| **User** | `routes/user_bp.py` | Profile, preferences, export, delete | User management (GDPR) |
| **Wisdom** | `routes/wisdom_bp.py` | Wisdom of the Day, sharing | Social/engagement features |
| **Admin** | `routes/admin_bp.py` | Admin dashboard, analytics, content mgmt | Administrative operations |
| **Diagnostics** | `routes/diagnostics_bp.py` | Health check, system status | Monitoring |
| **Voice** | `routes/voice_bp.py` | Text-to-speech synthesis | Voice interface |
| **Memory API** | `services/memory_api.py` | Memory dashboard, conversation context | Cross-session memory |
| **Onboarding** | `onboarding/onboarding_api.py` | Onboarding flow state | New user experience |
| **Engagement** | `engagement/engagement_api.py` | Streaks, badges, achievements | Gamification |
| **Notifications** | `notifications/notification_api.py` | Notification preferences, push | User notifications |
| **Notification Timers** | `notifications/notification_trigger.py` | Scheduled triggers | Cron-based notifications |

**Shared Services** (`routes/shared_services.py`):
- CORS header management
- Personality list retrieval
- Service availability flags (database, RAG, memory, engagement, etc.)
- Fallback personality definitions

### 2.2 AI Model Configuration

Centralized in `backend/config/ai_models.py`:

```python
@dataclass
class AIModelConfig:
    # Chat (migrated from Gemini → Azure OpenAI)
    azure_openai_chat_deployment: str     # Default: "gpt-5.4-mini"
    azure_openai_chat_api_version: str    # Default: "2024-08-01-preview"

    # Embeddings (migrated from text-embedding-004 → text-embedding-3-large)
    azure_openai_embedding_deployment: str  # Default: "vimarsh-embedding-large"
    embedding_output_dimensionality: int    # 768 (MRL-truncated from 3072)

    # Parameters
    max_tokens: int       # 8192
    temperature: float    # 0.7
    top_p: float          # 0.95
    requests_per_minute: int  # 100
    max_retries: int      # 3
    fallback_chat_deployment: str  # "gpt-5.4-mini"
```

### 2.3 Core Service Layer

#### 2.3.1 RAG Pipeline — Enhanced RAG Service V6

**File:** `services/enhanced_rag_service_v6.py` (35.6 KB)

The flagship AI service that orchestrates the complete conversation pipeline:

1. **Query Analysis** — Classify user intent, extract entities and emotional tone
2. **Embedding Generation** — Convert query to 768-dim vector via Azure OpenAI `text-embedding-3-large`
3. **Vector Search** — Cosmos DB vector similarity search with personality-scoped partitioning
4. **Context Assembly** — Combine retrieved documents with conversation history and memory context
5. **Response Generation** — Azure OpenAI `gpt-5.4-mini` with personality-specific system prompts
6. **Citation Grounding** — Validate response against retrieved sources; attach citation metadata
7. **Caching** — Cache frequently asked queries to reduce AI API costs

#### 2.3.2 Embedding Services

| Service | File | Purpose |
|---|---|---|
| `AzureOpenAIEmbeddingService` | `azure_openai_embedding_service.py` | Production embedding (text-embedding-3-large) with retry logic (5 attempts, exponential backoff) |
| `GeminiEmbeddingService` | `gemini_embedding_service.py` | Legacy (deprecated, retained for reference) |
| `EmbeddingGenerator` | `embedding_generator.py` | Orchestrates batch embedding for data pipeline |

**Embedding Specifications:**
- **Model:** `text-embedding-3-large` (Azure OpenAI)
- **Native Dimensionality:** 3,072
- **Output Dimensionality:** 768 (Matryoshka truncation for Cosmos DB compatibility)
- **Normalization:** L2
- **Batch Size:** 100 texts/API call
- **Rate Limit:** 120K tokens/min

#### 2.3.3 Memory System

**Hierarchical Memory Service** (`hierarchical_memory_service.py`, 115.8 KB — largest service file):

```
Memory Architecture:
├── Session Memory (active conversation context)
├── Short-Term Memory (recent conversations, last 3-5 sessions)
├── Long-Term Memory (persistent user-personality relationship insights)
└── Cross-Session Context (emotional themes, topic continuity, growth patterns)
```

Supporting services:
- `conversation_memory_service.py` — CRUD for conversation records
- `memory_analytics_service.py` — Relationship strength, engagement trends
- `memory_context_builder.py` — Assembles multi-layer context for prompt injection
- `memory_api.py` — REST endpoints for frontend Memory Dashboard

#### 2.3.4 Personalization Engine

| Service | File | Responsibility |
|---|---|---|
| `PersonalizationService` | `personalization_service.py` | User-specific response calibration (formality, depth, style) |
| `PromptTemplateService` | `prompt_template_service.py` | Dynamic prompt construction with persona-specific system prompts |
| `TopicExtractionService` | `topic_extraction_service.py` | NLP topic categorization for insight discovery |
| `UserProfileService` | `user_profile_service.py` | Journey statistics, wisdom level calculation, domain exploration tracking |

#### 2.3.5 Voice Interface

| Service | File | Responsibility |
|---|---|---|
| `AzureSpeechService` | `azure_speech_service.py` | Azure Neural TTS with SSML (Speech Synthesis Markup Language) |
| `VoiceConfig` | `config/voice_config.py` | 25 personality-specific voice mappings with style, rate, pitch parameters |

**Voice Mapping Summary:**

| Locale | Voice | Personalities |
|---|---|---|
| `en-IN-PrabhatNeural` | Indian English, Male | Krishna, Buddha, Vivekananda, Gandhi, Chanakya, Tagore |
| `en-US-GuyNeural` | American English, Male | Einstein, Lincoln, MLK, Confucius, Franklin |
| `en-US-DavisNeural` | American English, Male | Jesus, Tesla, Washington, Lao Tzu |
| `en-GB-RyanNeural` | British English, Male | Rumi, Newton, Marcus Aurelius, Plato, Shakespeare |
| `en-GB-ThomasNeural` | British English, Male | Archimedes, Socrates, Aristotle, Freud |
| `it-IT-DiegoNeural` | Italian, Male | Leonardo da Vinci |

SSML styles per personality: `empathetic`, `calm`, `gentle`, `lyrical`, `friendly`, `serious`, `hopeful`, `excited`, `chat`, `newscast`, `cheerful`.

#### 2.3.6 Additional Services

| Service | File | Purpose |
|---|---|---|
| `CacheService` | `cache_service.py` | In-memory + Cosmos-backed caching with TTL management |
| `CostOptimizationService` | `cost_optimization_service.py` | Real-time cost tracking, budget enforcement, query throttling |
| `SafetyService` | `safety_service.py` | Content moderation, PII detection, harmful input filtering |
| `SharingService` | `sharing_service.py` | Social sharing with OG image generation for wisdom cards |
| `OGImageService` | `og_image_service.py` | Server-rendered Open Graph images for social previews |
| `BookmarkService` | `bookmark_service.py` | Conversation bookmarking with notes |
| `WisdomJournalService` | `wisdom_journal_service.py` | Personal wisdom journaling and reflection |
| `DataExportService` | `data_export_service.py` | GDPR-compliant data export in JSON format |
| `AnalyticsService` | `analytics_service.py` | Usage analytics, AI cost tracking, trend analysis |
| `LLMJudgeService` | `llm_judge_service.py` | Automated response quality evaluation |
| `ExpertReviewService` | `expert_review_service.py` | Expert content review workflow |
| `PerformanceMonitor` | `performance_monitor.py` | Endpoint latency tracking, error rate monitoring |

---

## 3. Frontend Architecture

### 3.1 Technology Stack

| Layer | Technology | Version |
|---|---|---|
| **Framework** | React + TypeScript | 18.3.1 / 5.8.3 |
| **Build Tool** | Create React App (react-scripts) | 5.0.1 |
| **Routing** | React Router DOM | 6.18.0 |
| **Authentication** | MSAL.js (@azure/msal-browser + @azure/msal-react) | 3.5.0 / 2.0.12 |
| **UI Components** | MUI (Material UI) | 7.2.0 |
| **Icons** | Lucide React | 0.292.0 |
| **Markdown Rendering** | react-markdown | 10.1.0 |
| **HTTP Client** | Axios | 1.6.0 |
| **PWA** | Workbox (webpack-plugin + window) | 7.0.0 |
| **Testing** | Jest + React Testing Library + Cypress | - |

### 3.2 Application Routes

```typescript
// App.tsx route definitions
/                    → LandingPage (public)
/auth/callback       → AuthCallback (MSAL redirect handling)
/guidance            → GuidanceInterface (protected — core conversation UI)
/admin               → AdminDashboard (protected, requireAdmin)
/share/:shareId      → ShareView (public — shared wisdom cards)
/wisdom/archive      → WisdomArchive (protected)
/memory              → MemoryDashboard (protected)
/progress            → ProgressDashboard (protected)
/settings            → UserSettings (protected)
*                    → LandingPage (fallback)
```

All protected routes wrapped in `<ProtectedRoute>` component with circuit-breaker redirect protection.

### 3.3 Context Architecture

Nine React contexts provide application-wide state:

```
MsalProvider
└── AuthProvider (MSAL token management, account state)
    └── AdminProvider (admin role detection with 150ms debounce)
        └── PersonalityProvider (personality catalog, active selection, circuit-breaker loading)
            └── MemoryProvider (cross-session memory state)
                └── EngagementProvider (streaks, badges, achievements)
                    └── SettingsProvider (user preferences, 2s lazy load)
                        └── AppLoadingProvider (coordinated initialization readiness)
                            └── LanguageProvider (i18n, English/Hindi)
```

**Key Optimizations:**
- `PersonalityContext` uses module-level `hasLoadedPersonalities` circuit breaker — loads exactly once
- `SettingsProvider` delays profile load by 2,000ms — non-blocking initial render
- `AdminProvider` debounces with 150ms — prevents cascade during auth state transitions
- `AppLoadingProvider` coordinates `contextsReady` gate — prevents premature navigation

### 3.4 Key Component Architecture

#### GuidanceInterface.tsx (56.6 KB — largest component)
The primary conversation UI, containing:
- Message input with auto-resize textarea
- Personality badge display with domain colors
- Streaks and engagement metrics in top nav
- Response rendering with Markdown, citations, and voice playback
- Integrated personality selector modal
- Wisdom of the Day integration

#### LandingPage.tsx (57.3 KB)
The public-facing landing page with:
- Hero section with personality showcase
- Authentication flow (MSAL redirect login)
- Onboarding integration (3-step wizard)
- Authenticated-user redirect to `/guidance` (500ms stabilization delay)

#### ProtectedRoute.tsx (9.8 KB)
Route guard with three-layer circuit breaker:
1. **Mount Stabilization** — 500ms wait after mount before redirecting
2. **Cooldown Period** — 1-second minimum between redirects
3. **Redirect Threshold** — Max 3 redirects per 60-second window; triggers error screen if exceeded

#### ResponseDisplay.tsx (45.8 KB)
Rich response renderer:
- Markdown with syntax highlighting
- Citation source cards with expandable details
- Voice playback controls (play/pause/stop)
- Sharing and bookmarking actions
- Copy-to-clipboard

### 3.5 Design System

Three CSS design system layers:

| File | Purpose |
|---|---|
| `vimarsh-design-system.css` | Core tokens: typography, spacing, colors, shadows, transitions |
| `spiritual-design-system.css` | Spiritual domain–specific styles and theming |
| `domain-themes.css` | CSS custom properties for 6 domain color palettes |

**Domain Color Mapping:**

| Domain | Primary | Background | Border |
|---|---|---|---|
| Spiritual | Amber/Orange | `#fef3c7` | `#f59e0b` |
| Philosophical | Indigo/Purple | `#eef2ff` | `#6366f1` |
| Leadership | Emerald/Green | `#ecfdf5` | `#10b981` |
| Scientific | Blue/Cyan | `#eff6ff` | `#3b82f6` |
| Literary | Rose/Pink | `#fff1f2` | `#f43f5e` |
| Psychology | Teal | `#f0fdfa` | `#14b8a6` |

---

## 4. Data Architecture

### 4.1 Azure Cosmos DB (NoSQL)

**Database:** `vimarsh-multi-personality`  
**Consistency Level:** Session  
**Region:** West US 2 (for proximity to Azure OpenAI)

#### 11-Container Architecture

| Container | Partition Key | Purpose |
|---|---|---|
| `users` | `/user_id` | User accounts and profiles |
| `user_sessions` | `/user_id` | Active session management |
| `user_interactions` | `/user_id` | Conversations, usage tracking, user stats, personality configs |
| `personalities` | `/personality` | Personality definitions and metadata |
| `personality_vectors` | `/personality` | 31,422 embedded knowledge base documents |
| `user_analytics` | `/user_id` | Per-user analytics and engagement metrics |
| `content_analytics` | `/personality` | Content performance and popularity metrics |
| `daily_metrics` | `/date` | Aggregated daily platform metrics |
| `abuse_incidents` | `/user_id` | Abuse detection and incident tracking |
| `engagement_summary` | `/user_id` | Streak data, badges, achievements |
| `content_popularity` | `/personality` | Content ranking and popularity scores |
| `incidents_by_content` | `/content_id` | Content-level incident tracking |

#### Document Schema (Knowledge Base)
```json
{
  "id": "doc_12345",
  "personality": "krishna",
  "text": "The Supreme Lord said: Many births...",
  "embedding": [0.123, -0.456, ...],        // 768 dimensions
  "embedding_model": "text-embedding-3-large",
  "embedding_dimension": 768,
  "embedding_provider": "Azure OpenAI",
  "embedding_generated_at": "2025-12-06T15:30:00Z",
  "source": "Bhagavad Gita",
  "chapter": "4",
  "verse": "5"
}
```

### 4.2 Embedding Migration (Completed Dec 2025)

| Metric | Value |
|---|---|
| **From** | Google Gemini `text-embedding-004` |
| **To** | Azure OpenAI `text-embedding-3-large` (768-dim MRL) |
| **Documents** | 31,422 / 31,424 (99.99%) |
| **Duration** | 47h 24m |
| **Cost** | $0.19 (78% under $0.88 estimate) |
| **MTEB Score** | 64.6 (maintained) |
| **Batch Size** | 100 texts/API call |
| **Retry Rate** | 100% recovery with exponential backoff |

---

## 5. Authentication & Security

### 5.1 Microsoft Entra ID Integration

**Configuration:**
- **Tenant Type:** Multitenant with personal accounts
- **Authority:** `https://login.microsoftonline.com/common`
- **MSAL Flow:** Redirect (not popup)
- **Token Extraction:** `sub` claim (standard) → `oid` claim (Entra fallback)

**Frontend (MSAL.js):**
```typescript
// msalConfig.ts
{
  auth: {
    clientId: "e4bd74b8-9a82-40c6-8d52-3e231733095e",
    authority: "https://login.microsoftonline.com/common",
    redirectUri: window.location.origin,
    postLogoutRedirectUri: "/",
    navigateToLoginRequestUrl: true,
  },
  cache: {
    cacheLocation: "localStorage",
    storeAuthStateInCookie: true,   // Required for cross-domain redirect flow
  }
}
```

**Backend (JWT Validation):**
- Standard `Authorization: Bearer <jwt>` header
- Validates issuer: `https://login.microsoftonline.com/common/v2.0`
- JWKS URI: `https://login.microsoftonline.com/common/discovery/v2.0/keys`
- Fail-closed: Auth module failure → 503 (never bypass to prevent unauthorized access)

### 5.2 Security Controls

| Control | Implementation |
|---|---|
| **CORS** | Production: `vimarsh.vedmishra.com` and Azure Static Web App domain only |
| **Rate Limiting** | 60 requests/minute per user (configurable) |
| **Content Safety** | `SafetyService` — PII detection, harmful content filtering |
| **Input Validation** | Max query length: 1,000 characters |
| **Security Scanning** | Trivy (filesystem scan), npm audit, CodeQL (SARIF-based), custom Python audit script |
| **Encryption** | At rest: Cosmos DB encryption; In transit: TLS 1.3 |
| **RBAC** | Admin role detection via Cosmos DB lookup with cached results |

---

## 6. Infrastructure & Deployment

### 6.1 Azure Resource Architecture

**Two Resource Groups:**

| Resource Group | Resources |
|---|---|
| `vimarsh-rg` | Functions App (Flex), Static Web Apps, OpenAI Service, Speech Service, App Insights, Key Vault |
| `vimarsh-db-rg` | Cosmos DB account (separated for independent scaling and cost management) |

| Resource | Service | SKU/Plan |
|---|---|---|
| `vimarsh-backend-app-flex` | Azure Functions | Flex Consumption (Python 3.12) |
| `vimarsh-frontend` | Azure Static Web Apps | Free tier |
| `vimarsh-openai` | Azure OpenAI | S0 (West US) |
| `vimarsh-db` | Azure Cosmos DB | Serverless NoSQL |
| Azure Speech | Cognitive Services | Standard |
| Application Insights | Monitoring | Standard |

### 6.2 CI/CD Pipeline

**File:** `.github/workflows/unified-ci-cd.yml` (687 lines, 8-stage pipeline)

```
Stage 1: Setup & Change Detection (dorny/paths-filter)
    ↓
Stage 2: Security Scan (npm audit + Trivy + custom audit)
    ↓
Stage 3: Parallel Testing (Backend: pytest + Frontend: Jest)
    ↓
Stage 4: Integration Testing (Enhanced E2E validator)
    ↓
Stage 5: Build Artifacts (Backend package + Frontend build)
    ↓
Stage 6: Deploy to Production (Azure Static Web Apps + Azure Functions publish)
    ↓
Stage 7: Post-Deploy Validation (Health check + performance baseline + smoke tests)
    ↓
Stage 8: Notification & Cleanup
```

**CI Environment:**
- Python 3.12, Node 18
- Coverage threshold: 10% (minimum)
- Deploy trigger: Push to `main` branch
- Single environment strategy (production only, no staging)

### 6.3 Cost Profile

| Component | Monthly Cost (Active) | Monthly Cost (Idle) |
|---|---|---|
| Azure Functions (Flex) | $5–15 | $0–1 |
| Cosmos DB (Serverless) | $5–15 | $3–5 |
| Azure OpenAI (chat + embeddings) | $3–8 | $0 |
| Static Web Apps | $0 (free tier) | $0 |
| Application Insights | $0–2 | $0 |
| Azure Speech | $0–2 | $0 |
| **Total** | **$15–40** | **$5–15** |

---

## 7. Performance Characteristics

### 7.1 Response Pipeline Latency

| Stage | Target | Actual |
|---|---|---|
| Query → Vector Embedding | < 200ms | ~150ms |
| Cosmos DB Vector Search | < 300ms | ~250ms |
| Context Assembly + Prompt | < 50ms | ~30ms |
| LLM Generation (GPT-5.4-mini) | < 2s | ~1.5s |
| Post-Processing + Caching | < 100ms | ~50ms |
| **Total (P95)** | **< 3s** | **~2.17s** |

### 7.2 Frontend Performance Optimizations

| Optimization | Impact |
|---|---|
| React.lazy() code splitting | 7 lazy-loaded route components |
| Module-level personality circuit breaker | 98% API call reduction (168+ → 4) |
| 500ms mount stabilization (ProtectedRoute) | Eliminates auth redirect loops |
| 150ms admin check debounce | 50% reduction in admin API calls |
| 2s lazy settings profile load | Non-blocking initial render |
| AppLoadingProvider coordination | Prevents premature navigation |
| Empty useEffect dependency arrays | Prevents re-render cascades |

**Cumulative Result:** 70-80% faster load times; initial load 5-6s → 1.5-2s

### 7.3 Caching Strategy

| Cache Layer | TTL | Scope |
|---|---|---|
| Personality list | 3,600s | Global (module-level) |
| Wisdom of the Day | 86,400s | Global |
| Recent queries | 1,800s | Per-personality |
| User preferences | 1,800s | Per-user |
| Admin role | Session | Per-user |

---

## 8. Testing Strategy

| Layer | Framework | Coverage Target | Configuration |
|---|---|---|---|
| **Backend Unit** | pytest + pytest-cov + pytest-asyncio | ≥ 10% (CI gate) | `backend/tests/` |
| **Frontend Unit** | Jest + React Testing Library | ≥ 10% (CI gate) | `frontend/jest.config.js` |
| **E2E** | Cypress 14.5.0 | Critical paths | `frontend/cypress/` |
| **Integration** | Custom Python E2E validator | Comprehensive | `scripts/enhanced_e2e_validator.py` |
| **Post-Deploy** | Custom health check script | Health/Smoke | `scripts/post_deployment_health_check.py` |
| **RAG Quality** | Manual validation + LLM Judge | 88% citation rate | `backend/test_all_personalities_rag.py` |

---

## 9. Monitoring & Observability

| Signal | Tool | Dashboard |
|---|---|---|
| **Application Metrics** | Azure Application Insights | Response latency, error rates, throughput |
| **AI Cost Tracking** | Custom `CostOptimizationService` | Monthly spend, per-query cost, budget utilization |
| **Performance** | Custom `PerformanceMonitor` | Endpoint P50/P95/P99 latencies |
| **Health** | `diagnostics_bp.py` `/api/health` | Service availability matrix |
| **Security** | CI/CD Trivy + npm audit + CodeQL | Vulnerability scanning per deployment |
| **Frontend Errors** | Console-level logging (debug mode) | Circuit breaker activations, auth state transitions |

---

## 10. Environment Configuration

### Key Environment Variables

| Variable | Purpose | Default |
|---|---|---|
| `AZURE_OPENAI_ENDPOINT` | Unified Azure OpenAI endpoint | Required |
| `AZURE_OPENAI_API_KEY` | API key for chat + embeddings | Required |
| `AZURE_OPENAI_CHAT_DEPLOYMENT` | Chat model deployment name | `gpt-5.4-mini` |
| `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` | Embedding model deployment name | `vimarsh-embedding-large` |
| `EMBEDDING_OUTPUT_DIMENSIONALITY` | Vector dimensions | `768` |
| `AZURE_COSMOS_CONNECTION_STRING` | Cosmos DB connection | Required |
| `COSMOS_DATABASE_NAME` | Database name | `vimarsh-multi-personality` |
| `REACT_APP_CLIENT_ID` | MSAL client ID | `e4bd74b8-...` |
| `REACT_APP_AUTHORITY` | MSAL authority | `https://login.microsoftonline.com/common` |
| `MONTHLY_BUDGET_USD` | Cost ceiling | `50` |
| `ENABLE_VOICE_INTERFACE` | Voice feature flag | `true` |
| `ENABLE_PWA_FEATURES` | PWA feature flag | `true` |

---

*Cross-reference: [PRD.md](./PRD.md) for product requirements and feature scope · [UX-Spec.md](./UX-Spec.md) for interface design and interaction patterns*
