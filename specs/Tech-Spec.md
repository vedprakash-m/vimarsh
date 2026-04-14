# Technical Specification Document: Vimarsh Platform

## 1. Architectural Philosophy & Strategy

The Vimarsh System operates under the ethos of **"Probabilistic Pragmatism"** — ensuring inherently volatile AI structures (LLMs) are wrapped in rigid, unyielding computational frameworks. The current codebase enforces strict deterministic validations, stateless serverless memory boundaries, and idempotent processing to build a 99.9% reliable enterprise platform without compounding architectural debt.

## 2. Infrastructure & Cloud Deployment

### 2.1 Compute and Integration Topology
* **Environment Strategy**: Single environment (Production Only) housed entirely within a shared `vimarsh-rg` Azure Resource cluster. 
* **Backend Processing**: Executed on **Azure Functions (Flex Consumption Plan)** built in Python 3.12, ensuring highly responsive autoscaling for varying burst loads.
* **Frontend Delivery**: Built on React 18, Vite, packaged as a Progressive Web App (PWA) served dynamically via **Azure Static Web Apps**. 
* **Cross-Origin Strategy**: Strict CORS restrictions mapping completely and exclusively to designated production URIs (`vimarsh.vedprakash.net`). Wildcard permissions are structurally eradicated.

### 2.2 Database layer (Azure Cosmos DB)
The platform effectively mitigated previous `Out-Of-Memory (OOM)` risks by ripping out brittle in-memory dict cache mechanisms. The backbone leverages Cosmos DB Serverless with specialized containers:
* `conversations`: Stores persistent cross-session memories.
* `session_state`: A highly performant distributed transient state tracking session payloads subject to strict **Time To Live (TTL: 1800s)** limits. Monitored specifically via the feature flag `USE_REDIS_STATE_V2`.
* `analytics`: Houses real-time telemetry usage metrics.

## 3. Advanced AI Engine Integrations

### 3.1 Azure OpenAI Models and Dimension Truncation
Vimarsh executed a full migration off external third-party models into a unified Microsoft Azure perimeter:
* **Response Generation**: Utilizing **`GPT-5-mini`** (`vimarsh-chat-gpt5mini` deployment) optimized precisely for latency and narrative logic. 
* **Embedding Model**: Leveraging **`text-embedding-3-large`**. Natively a 3072 dimension space, this has been intentionally optimized to **768 dimensions** (MRL truncation) resulting in lower memory usage while retaining roughly 94.8% of the embedding's raw analytical power, perfect for Cosmos DB's vector lookup compatibility constraints.

### 3.2 Robust Request Idempotency 
Mitigating duplicate database insertions or corrupt states originating from LLM retry-loops, **Idempotency Execution** is mandatory on the `llm_service.py` component:
* A SHA-256 hash maps `user_id`, `session_id`, and a normalized 5-minute `time-floor`. 
* Actions flagged with this execution hash terminate duplication immediately guaranteeing pristine database states despite variable agentic recursion.

### 3.3 Semantic Compression Agent (Memory Pipeline)
Managing immense episodic interaction records naturally inflates token dependencies, leading to prohibitive execution costs. The `HierarchicalMemoryService.py`:
* Continuously measures local episodic context token footprints.
* Activates a fully asynchronous **Semantic Compression Agent** passing 2000-character payload sweeps, distilling broad interactions into concise, structured knowledge snapshots fed back into working memory.

### 3.4 Pydantic Forced Output Validation Loop
Enacted via the feature switch `ENABLE_STRUCTURED_OUTPUTS_V2`, the system categorically rejects hallucinated schemas from the LLM. 
* Uses **`ResponseSchema`** to enforce explicitly typed Python structures mapping JSON boundaries.
* Tagged implicitly to Azure Application Insights: Missing parameters or incorrect values emit `🚨 VALIDATION_ERROR` metrics ensuring absolute observability across error states.

## 4. Microsoft Entra ID Authentication 

The platform relies on the `MSAL.js` v3 protocol connecting specifically to the localized MSFT tenant (`vedid.onmicrosoft.com`).
* **Fail-Closed Execution**: If upstream auth architectures degrade or libraries crash via `ImportError`, the backend defaults strictly to 503 Service Unavailable, ensuring partial logic bypasses do not accidentally unlock unauthorized access levels.
