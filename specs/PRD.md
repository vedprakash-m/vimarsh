# Product Requirements Document (PRD): Vimarsh Multi-Personality Platform

| Document Information | |
|---|---|
| **Project** | Vimarsh |
| **Status** | Implementation (v2.0) |

## 1. Executive Summary

**Vimarsh** is an enterprise-grade, AI-powered conversational platform designed to democratize access to the greatest minds in history through interactive, domain-specific chat interfaces. Driven by Azure OpenAI GPT-5-mini and large-scale semantic vector indexing, Vimarsh hosts 25 historical personalities across 6 diverse domains.

The primary business objective is to transition from basic generic AI chatbot engagements into highly authenticated, source-grounded relationship building. This platform empowers users with spiritual contemplation, strategic leadership advice, and deep historical reflection.

## 2. Objective & Key Results (OKRs)
* **Objective**: Establish the world's most authentic conversational wisdom platform.
  * **KR 1**: Achieve <3s P95 latency for cross-domain AI response generation.
  * **KR 2**: Reduce output hallucinations to 0% by strictly enforcing Pydantic validations against indexed vector constraints.
  * **KR 3**: Attain a 40% Day-1 return rate via gamified 'Streak' interactions.

## 3. Product Vision & Problem Statement

### 3.1 Problem Space
Modern users looking for profound guidance often sift through thousands of archaic pages or face modern AI counterparts that hallucinate historical positions, breaking immersion and trust. Knowledge is fragmented, largely inaccessible, and lacks personalization to actual human challenges.

### 3.2 Vimarsh Solution
Vimarsh distills thousands of historical excerpts across 34,039 indexed documents spanning 25 personalities into highly specialized, isolated AI models. Each interaction is validated natively against Azure Cosmos DB vector spaces and outputted strictly within the guardrails of the historical figure's known writings, eliminating anachronisms and generic responses.

## 4. Persona Framework

| Persona | Needs | Pain Points |
|---|---|---|
| **The Spiritual Seeker** | Looking for deep, philosophical and moral guidance through the lens of figures like Krishna or Marcus Aurelius. | Confused by complex historical texts; generic AI bots lack empathy and factual continuity. |
| **The Domain Researcher** | Exploring analytical frameworks via Einstein, Newton, or Freud. | Fictionalized "personas" in other apps hallucinate scientific facts. Demand for strict source-driven interaction. |

*(Refer to `UX-Spec.md` for detailed Empathy Maps and user journeys).*

## 5. Feature Specifications (MoSCoW)

### 5.1 Must Have (Core Capabilities)
- **Authentic RAG-Driven Interactions**: AI replies strictly cross-reference embedded text indexes (`text-embedding-3-large`).
- **Domain Specialization**: 25 personas operating within 6 major domains: Spiritual, Philosophical, Leadership, Scientific, Literary, and Psychology.
- **Cross-Session Continuity**: Utilizing the *Semantic Compression Agent* to abstract episodic context without blowing out LLM token limitations.
- **Strict Role-Based MSAL Auth**: Enforced `multitenant-personal` Entra ID logins prior to session modifications.

### 5.2 Should Have (Engagement & Growth)
- **Intelligent Onboarding Funnel (Intent Discovery)**: 3-step intent validation mapping new users to optimal figures (e.g., "Need leadership advice" -> Chanakya).
- **Gamified Wisdom Streaks & Protection**: Fire emoji trackers, Day-7 "Consistency Seeker" badges, and daily check-ins.
- **Quote Share Cards**: Embedded UI CTAs generating stylized quote-cards for viral social media growth.

## 6. Success Metrics & Non-Functional Requirements

- **Zero-Trust Failsafes**: Native circuit breakers; if Entra middlewares fail or Pydantic extracts malformed JSON, endpoints explicitly emit a `503 Service Unavailable` rather than degrading to insecure states.
- **Platform Resilience**: Cosmos DB entirely manages session transience via auto-evicting `session_state` constructs (1800s TTL) replacing brittle in-memory structures.
