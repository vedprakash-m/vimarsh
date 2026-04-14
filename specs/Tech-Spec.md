# Technical Specification Document: Vimarsh Platform

| Document Information | |
|---|---|
| **Environment** | Production Only (Single Environment Topology) |
| **Arch Paradigm** | Azure Serverless / Probabilistic Pragmatism |

## 1. Executive Summary
Vimarsh standardizes volatile LLM operations through rigorous idempotency keys, robust Pydantic schemas, and scalable Azure Cosmos DB structures. The entire backend runs on Azure Functions (Flex Consumption) interconnected via Microsoft Entra ID (`multitenant-personal` tenant configuration).

## 2. Infrastructure Architecture (C4 Model)

```mermaid
C4Context
  title System Context Diagram - Vimarsh 
  Person(user, "User", "Interacts with 25 Historical Figures")
  System(vimarsh, "Vimarsh Platform", "Authentic RAG Conversational System")
  System_Ext(entra, "Microsoft Entra ID", "User Authentication (Multitenant)")
  System_Ext(openai, "Azure OpenAI", "GPT-5-mini & text-embedding-3-large")
  
  Rel(user, vimarsh, "Visits & Chats", "HTTPS")
  Rel(vimarsh, entra, "Validates JWT", "MSAL.js")
  Rel(vimarsh, openai, "Generates Embeddings & Text", "REST")
```

```mermaid
C4Container
  title Container Diagram - Central Services
  Container_Boundary(c1, "Vimarsh Cloud") {
    Container(pwa, "React PWA", "Vite, TypeScript", "Serves decoupled Landing & Chat")
    Container(func, "Azure Functions API", "Python 3.12", "Flex Consumption Plan (West US 2)")
    ContainerDb(cosmos, "Azure Cosmos DB", "NoSQL, Vector Store", "Persists memory, session, & vectors")
  }
  System_Ext(openai, "Azure OpenAI")
  
  Rel(pwa, func, "Executes API (w/ MSAL Token)")
  Rel(func, cosmos, "Stores via 1800s TTL Session State", "NoSQL")
  Rel(func, openai, "Semantic Search & Chat Completion")
```

## 3. Data Architecture (Azure Cosmos DB)
The `vimarsh-db` operates seamlessly across several strictly portioned containers to mitigate Out-Of-Memory flaws inherent to previous Python-dict architectures.

- **`session_state`**: Distributed transient payload cache utilizing native Time-To-Live logic (`TTL: 1800s`). Checked via `USE_REDIS_STATE_V2`.
- **`conversations`**: Long-term thread persistence. Offloads >2000 character interactions utilizing the asynchronous **Semantic Compression Agent** within `hierarchical_memory_service.py` to compile structural meaning.
- **`personality_vectors`**: Pre-embedded documents (`34,039` files) enabling `text-embedding-3-large` Cosine similarities.

## 4. Azure OpenAI Integrations & Schema Validation
All interactions are piped into Azure OpenAI (`vimarsh-chat-gpt5mini`).
* **Vector Truncation**: Native `text-embedding-3-large` operates upon 3072 dimensions. Vimarsh uses MRL truncations down to **768 dimensions** which optimizes Cosmos DB ingestion logic while retaining 94.8% semantic parity.
* **Pydantic Hardening**: To force schema conformity (dark-launched via `ENABLE_STRUCTURED_OUTPUTS_V2`), Pydantic forces deterministic structures mapping 1:1 to Python dataclasses. Extraction failures emit an explicit `🚨 VALIDATION_ERROR` telemetry tag direct to App Insights.

## 5. Security & Idempotency Flow
```mermaid
sequenceDiagram
  participant Client as React PWA
  participant BE as Azure Function
  participant DB as Cosmos DB
  participant AI as Azure OpenAI

  Client->>BE: POST /api/chat (Bearer Token: Entra ID)
  BE->>BE: Validate Token (multitenant-personal)
  BE->>BE: Generate Action SHA256 (User+Session+5minFloor)
  BE->>DB: Check Idempotency Key
  alt Key Exists
      DB-->>BE: Return Previous State
      BE-->>Client: 200 OK (Cached)
  else Key Does Not Exist
      BE->>AI: RAG Semantic Context search + GPT-5-mini
      AI-->>BE: Pydantic Structured Output
      BE->>DB: Write Interaction + Store Idempotency Key
      BE-->>Client: 200 OK (New Response)
  end
```

## 6. Cost Analysis & Resource Estimation
Vimarsh minimizes baseline operational charges leveraging purely scalable architectures:
* **Storage**: Azure Cosmos DB (Serverless model) charges strictly per Request Unit (`RU/s`). 
* **Compute**: Azure Functions (Flex Consumption) auto-scaled to zero, preventing expensive idling.
* **Frontend**: Hosted on Azure Static Web Apps incurring zero fundamental server footprint costs.
* **Estimated P95 Overhead**: ~ $15-40/month active load vs $5-15/month idle.
