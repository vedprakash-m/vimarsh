# Technical Specification Document: Vimarsh Platform

## 1. Overview
The architectural source of truth for the Vimarsh Multi-Personality Platform. Designed around the principles of "Probabilistic Pragmatism", the platform transforms LLM inferences into perfectly resilient, predictable system operations.

## 2. Infrastructure & Cloud Footprint
* **Compute**: Azure Functions (Flex Consumption Plan)
* **Database**: Azure Cosmos DB (Serverless). Partitions unified under `/user_id`.
* **State Management**: Distributed Serverless Caching (`session_state` container with 1800s TTL), replacing brittle python-in-memory caching. Checked via flag `USE_REDIS_STATE_V2`.
* **Frontend Delivery**: Azure Static Web Apps representing a React 18, Vite-built PWA bundle.

## 3. Core AI Integration (Azure OpenAI)
* **Inference Layer**: `GPT-5-mini` enforcing JSON validation boundaries (`ResponseSchema` using Pydantic). Fallbacks exist to recover from LLM token hallucinations. Dark-launched via `ENABLE_STRUCTURED_OUTPUTS_V2`.
* **Embedding Layer**: `text-embedding-3-large` (MRL dimensions truncated to 768) facilitating robust hybrid search and RAG indexing. 

## 4. Architectural Patterns & Guardrails
* **Idempotency Execution**: Every LLM write request encodes a SHA256 deterministic key (user+session+time-floor) preventing loop database duplicate writes.
* **Extractive Semantic Compression**: Episodic contexts are continuously condensed by an internal asynchronous compressor if payload spans bypass 2000 characters, drastically boosting context density.
* **Telemetry & Error Catching**: Azure application insights catch tagged `VALIDATION_ERROR` markers to natively log failing extraction boundaries or payload generation limits.
* **Fail-Closed Auth Boundaries**: MSAL.js integrates with Microsoft Entra ID (`vedid.onmicrosoft.com`). If access boundaries fail to load, endpoints strictly 503 rather than bypass.

## 5. Deployment Specs
* Hosted entirely on West US 2 (Compute) and East US 2 (Delivery). Single environment topology optimized to reduce idling costs.
