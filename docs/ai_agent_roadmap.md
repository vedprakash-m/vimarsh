# AI Agent Roadmap for Vimarsh Platform
**⚠️ STRATEGIC PIVOT IMPLEMENTED - See ai_agent_roadmap_revised.md for Updated Strategy**

---

## Executive Summary

Vimarsh currently operates at **Level 3 (RAG Excellence)**. Previous ambitions targeted rapid advancement to autonomous multi-agent collaboration (Levels 7–9). After strategic review (PRD, Tech Spec, UX alignment) we are **pivoting to an authenticity-first, user-value-centric roadmap** that deepens core strengths (textual fidelity, personality expansion, evaluation) **before** introducing any orchestration beyond independent personalities.

**Strategic Pivot Highlights:**
- Preserve the platform’s differentiator: strict textual grounding + authentic voice per personality.
- Accelerate high-ROI deliverables: add validated personalities, conversation history, wisdom journal, search, scoped memory.
- Pull forward evaluation & citation integrity (prioritize Levels 3–4 + targeted parts of 6 & 8). Delay complex autonomous multi-agent “consensus” (original Level 7) in favor of **user-invoked Panel / Symposium Mode** with **independent** outputs.
- Reframe multi-agent synthesis as optional, explicitly labeled, and only after maturity in evaluation & guardrails.

**Revised Target Horizon (18 months):**
- Mastery of Levels 3–4 (RAG + LLMOps) → Introduce scoped Level 6 memory + selective Level 8 evaluation → User-controlled multi-view (re-imagined Level 7) **without agent cross-talk** → Optional orchestration (post-18m, gated by quality metrics).

---

## Strategic Principles
1. Authenticity over Autonomy: No hidden cross-personality blending; each answer must remain attributable and citation-grounded.
2. User-Orchestrated Multiplicity: Multi-view insights are **requested**, never implicit.
3. Precision Before Expansion: Elevate retrieval & evaluation quality before layering complexity.
4. Isolation & Privacy: Memory is partitioned (user_id + personality_id); no leakage.
5. Measurable Quality: Every phase gated by objective authenticity, citation, and consistency metrics.
6. Cost Discipline: Time-To-Add-New-Personality (TANP) reduction and per-query cost ceilings.

---

## Current Assessment by Level (Condensed)

### 🎯 Level 1: GenAI & Transformer Foundations – ✅ STRONG (95%)
(Unchanged; foundations solid.)

### 🎯 Level 2: Prompting & Language Model Behavior – ✅ STRONG (85%)
Next: introduce structured reasoning (optional CoT expansion), but only where it improves citation clarity.

### 🎯 Level 3: RAG – ✅ EXCELLENT (95%)
Focus: hybrid search (BM25 + dense), re-ranking, diversity filtering, adaptive k per personality.

### 🎯 Level 4: LLMOps & Tools – ⚠️ MODERATE (45%)
Refactor into modular retrieval/prompt services before adopting frameworks (avoid premature lock-in). Selective LangChain components for tooling consistency (prompt templates, tracing) only after refactor.

### 🎯 Level 5: Agents & Frameworks – 🔄 REDEFINED (was WEAK 25%)
Old vision (autonomous multi-agent orchestration) replaced with **Independent Personality Pipelines**. Each personality = self-contained RAG + style + evaluation bundle. No inter-agent planning layer in Phase 1–2.

### 🎯 Level 6: Memory, State & Orchestration – ❌ LIMITED (30%)
Re-scope to **Scoped Memory v1**: per user-per personality episodic + compressed semantic summaries. No cross-personality synthesis. Working memory = recent turns + distilled prior milestones.

### 🎯 Level 7: Multi-Agent Systems – 🔄 RE-IMAGINED (Deferred Orchestration)
Now defined as **Panel / Symposium Mode**: fan-out independent generation → side-by-side responses → optional user-requested comparative summary (Phase 3). No hidden negotiation layer.

### 🎯 Level 8: Evaluation & Reinforcement – ⬆️ PULL-FORWARD (Early Partial Implementation)
Introduce automated authenticity & citation verification early (Phase 1). Reinforcement / reward modeling postponed until stable evaluation baselines (Phase 3+).

### 🎯 Level 9: Protocols & Safety – ⚠️ MODERATE (40%)
Add persona deviation detector, cultural sensitivity classifier, refusal policy tests (Phase 2). Formal safety orchestration later.

### 🎯 Level 10: Build & Deploy – ⚠️ MODERATE (60%)
Incremental improvements: tracing, metrics pipeline, CI gated evaluation scores. Avoid full platform migration until retrieval refactor complete.

---

## High-ROI Gaps (Ranked)
1. Retrieval Quality (hybrid + rerank + dedupe) – immediate user impact.
2. Personality Expansion Pipeline (tooling + validation harness).
3. Automated Citation & Grounding Verification (precision baseline).
4. Conversation History & Wisdom Journal (retention + premium conversion).
5. Scoped Memory (episodic + semantic compression) with privacy guardrails.
6. Evaluation Observability (persona style score, hallucination rate, latency SLOs).
7. Panel Mode (distinct outputs) – cross-domain insight after quality maturity.

---

## Revised Phased Roadmap

### Phase 1 (Months 0–6): Depth & Coverage
Focus: Strengthen core retrieval + expand validated personalities.
- Add 4–6 new personalities (Einstein, Buddha, Marcus Aurelius, Lincoln, + optional Rumi / Lao Tzu) with ingestion QA.
- Retrieval Enhancements: BM25 + dense fusion, semantic rerank (cross-encoder), min redundancy filter, adaptive k.
- Evaluation v1: Citation grounding checker (string overlap + embedding relevance), persona style classifier (few-shot), hallucination detector heuristic.
- Conversation History MVP + Wisdom Journal (user export + semantic search).
- Modular Refactor: `retrieval_service`, `prompt_service`, `citation_service`, instrumentation hooks.
- Metrics Platform: log retrieval_hit_rate, citation_precision, p95_latency, cost_per_response.

Gate to Phase 2:
- Citation precision ≥ 90%.
- Persona deviation score ≤ 15% variance across personalities.
- TANP ≤ 3 weeks → ≤ 2 weeks target trending.
- p95 end-to-end latency ≤ 2.5 s (median ≤ 1.4 s) on 80% of queries.

### Phase 2 (Months 6–12): Personalization & Trust
- Scoped Memory v1: per user-per personality episodic events + compressed semantic snapshot (rolling summary ≤ 1 KB/personality).
- Memory Safety: partition key (user_id|personality_id), PII scrubbing (regex + heuristic) before persist.
- Wisdom Journal Enhancements: tagging, milestone auto-detection, search facets (topic, personality, timeframe).
- Evaluation v2: LLM-as-Judge ensemble (authenticity, tone, citation alignment); drift alerts (weekly baselines).
- Persona Expansion Pipeline Automation: ingestion QA checklist & automated coverage report.
- Safety Additions: refusal tests, cultural sensitivity classifier, adversarial prompt regression set.

Gates:
- Return Rate (Day 7) +10% vs Phase 1 baseline.
- Hallucination rate < 5% (LLM-judge validated).
- Memory impact: personalization uplift (measured via user feedback) with no increase in hallucination rate.

### Phase 3 (Months 12–18): Multi-View Insight (Panel Mode)
- Panel (Symposium) Mode: independent parallel RAG+LLM per selected personalities (max 3 default, extensible to 5).
- Optional Comparative Summary: only if user toggles “Compare Perspectives” (meta summary cites each persona explicitly).
- Advanced Retrieval: persona-adaptive k, cluster-based diversity (embedding centroid spread), intent classification for query rewriting.
- Evaluation v3: multi-response consistency analyzer (ensures each response remains within persona style band) + cross-personality contrast quality metric.
- Proactive Suggestions (lightweight): suggest related authentic passages (no unsolicited synthesis).

Gates:
- Panel responses maintain citation precision parity (±2%) with single-personality baseline.
- Comparative summary hallucination rate < 5%.
- Panel adoption ≥ 20% weekly active advanced users.

### Phase 4 (Post-18m, Optional): Selective Orchestration
- ONLY if metrics plateau and user demand substantiated.
- Introduce Optional Guided Synthesis Agent (clearly labeled “Derived Comparative Analysis – Not Primary Voice”).
- Strict transparency: each synthesized claim must link to originating personality outputs & citations.

Go/No-Go Criteria:
- Sustained authenticity score ≥ 92%.
- User request rate for deeper synthesis > defined threshold (e.g., 15% of panel sessions).

---

## Memory Architecture (Scoped v1)
- Working Memory: last N (configurable, default 10) turns + compressed prior summary.
- Episodic Memory: milestone events (practice applied, gratitude expressed) keyed by timestamp.
- Semantic Memory: evolving principles (ranked list) with decay & reinforcement weights.
- Compression Policy: Summarize after every 25 turns or 2 KB raw accumulation (whichever first). Maintain diffs for audit.
- Data Model (conceptual): `partition_key = f"{user_id}#{personality_id}"`, items typed: {type: episodic|semantic|summary|journal_entry}.

---

## Evaluation Stack (Evolution)
| Version | Components | Automation Frequency |
|--------|------------|----------------------|
| v1 | Citation grounding (overlap + embedding), persona style heuristic | per deploy + nightly |
| v2 | LLM-as-judge ensemble, drift detector, hallucination scorer | per batch + weekly trend |
| v3 | Multi-view contrast metrics, summary hallucination audit | panel sessions + weekly |

Key Scores:
- Citation Precision = cited_chunks_used / cited_chunks_total.
- Grounding Score = mean cosine(sim(response segment, source chunk)).
- Persona Style Score = classifier confidence vs persona profile baseline.
- Hallucination Rate = % sentences lacking ≥ threshold grounding.
- Deviation Delta = |current style embedding – baseline centroid|.

Alerts:
- Any personality citation precision < 85% (critical).
- Style drift > 2σ over 7-day moving window.

---

## Metrics & Targets
- Retrieval Hit Rate: 66.7% → 80% (Phase 1) → 85% (Phase 2).
- Citation Precision: 90% Phase 1 gate → 92% Phase 2 → 93%+ Phase 3.
- Persona Consistency: ≥ 85% Phase 1 → ≥ 90% Phase 2.
- Hallucination Rate: < 7% Phase 1 → < 5% Phase 2 → < 4% Phase 3.
- TANP: 4–6 weeks current → ≤ 3 weeks Phase 1 → ≤ 2 weeks Phase 2.
- Day 7 Return Rate: +10% Phase 2 vs Phase 1 baseline.
- Panel Adoption: ≥ 20% advanced users (Phase 3).

---

## Cost & Performance Guardrails
- p95 Latency Targets: Single response ≤ 2.5 s; Panel (3 personas) ≤ 4.5 s.
- Cost per Query (avg): ≤ $0.005 single, ≤ $0.012 panel (Gemini + retrieval + infra).
- Personality Storage Overhead: < 5% duplication (dedupe hashing per chunk).
- Memory Storage Budget: ≤ 25 KB active + 100 KB archived per user per personality (rolling window retention + compression).

---

## Tooling & Refactor Plan
1. Service Modularization (retrieval, prompts, citations, evaluation hooks).
2. Hybrid Search Integration (BM25 index + existing vector) + late fusion weighting.
3. Cross-Encoder Re-rank (e.g., MiniLM cross encoder) – top 50 → top k.
4. Evaluation Harness CLI/CI (run canonical prompt suite, produce JSON scorecard).
5. Memory Service (compression worker + summarization prompt template).
6. Panel Execution Orchestrator (fan-out async gather + structured response schema).

---

## Risk Register (Condensed)
| Risk | Impact | Mitigation |
|------|--------|-----------|
| Authenticity dilution | High | Independent pipelines; forbid hidden synthesis |
| Cost creep with personalities | Medium | Monthly cost dashboard; usage-based retention |
| Memory privacy leakage | High | Partitioning + automated test suite for access layer |
| Style drift | High | Drift detector + rollback gating |
| Panel hallucination | Medium | Per-personality grounding + summary gating |
| Framework lock-in | Medium | Refactor before partial LangChain adoption |

---

## Resource & Investment (Revised Projection ~12–15 Months Core)
| Category | Previous Plan | Revised Focus | Est. Allocation |
|----------|---------------|--------------|----------------|
| Retrieval & Refactor | Under-scoped | Core early | 25% |
| Personality Expansion & QA | Moderate | Accelerated | 20% |
| Evaluation & Safety | Late | Pulled Forward | 20% |
| Memory & Journal | Mid | Phase 2 Core | 15% |
| Panel Mode | Heavy multi-agent | Lightweight fan-out | 10% |
| Optional Orchestration (Phase 4) | Large | Conditional | 0–10% |

Reduction vs original multi-agent heavy plan lowers projected 24‑month spend by ~30–40% while accelerating user-visible value.

---

## Sample Acceptance Criteria (Phase 1 Extract)
- Retrieval pipeline returns ≥ 1 grounded chunk for 85% of canonical test queries.
- Citation evaluator F1 ≥ 0.9 on validation set (hand-labeled relevance).
- New personality ingestion script produces coverage report (unique sections %, orphan sections %, duplicate hash collisions < 2%).
- Wisdom Journal search latency < 300 ms for 95th percentile queries (index warm).

---

## Panel Mode Response Schema (Phase 3 Draft)
```json
{
  "question": "<user_query>",
  "responses": [
    {"personality": "krishna", "text": "...", "citations": [ ... ], "meta": {"grounding_score": 0.93}},
    {"personality": "einstein", "text": "...", "citations": [ ... ], "meta": {"grounding_score": 0.90}}
  ],
  "comparative_summary": {
    "enabled": true,
    "text": "(Only if user requested)",
    "attribution_map": {"krishna": ["Gita 2.47"], "einstein": ["Letter 1926"]}
  }
}
```

---

## Go / No-Go Gates Summary
| Gate | Metric | Threshold |
|------|--------|-----------|
| Phase 1 → 2 | Citation precision | ≥ 90% |
| Phase 1 → 2 | TANP | ≤ 3 weeks |
| Phase 2 → 3 | Hallucination rate | < 5% |
| Phase 2 → 3 | Return rate uplift | ≥ +10% |
| Phase 3 → 4 (Optional) | Authenticity score | ≥ 92% sustained 60 days |
| Phase 3 → 4 (Optional) | User demand (panel synthesis requests) | ≥ 15% panel sessions |

---

## Conclusion
This revised roadmap concentrates investment where Vimarsh’s brand moat is deepest: **authentic, citation-grounded wisdom from multiple historically faithful personalities**. By postponing autonomous multi-agent synthesis and emphasizing verifiable quality, scoped memory, and user-controlled multi-view, we accelerate retention, trust, and monetization while reducing architectural risk. Optional orchestration remains a future lever—activated only if user value plateaus after mastering authenticity at scale.

*Revised: August 9, 2025*
