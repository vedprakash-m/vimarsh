# Product Requirements Document (PRD): Vimarsh

| Field | Value |
|---|---|
| **Product** | Vimarsh — AI-Powered Multi-Personality Conversational Wisdom Platform |
| **Version** | 2.1 (April 2026) |
| **Status** | Production — Live at [vimarsh.vedprakash.net](https://vimarsh.vedprakash.net) |
| **License** | Business Source License (BSL) |

---

## 1. Executive Summary

**Vimarsh** (Sanskrit: *विमर्श* — "conversation, thoughtful discourse") is an AI-powered conversational platform that enables authentic dialogues with **25 historical personalities** across **6 knowledge domains**. Powered by **Azure OpenAI GPT-5.4-mini** for response generation and **text-embedding-3-large** for semantic search across a **31,422-document knowledge base**, the platform transforms how users access and interact with humanity's greatest minds.

### Core Achievement
- **25 operational personalities** with domain-specific RAG pipelines and authentic voice preservation
- **31,422 embedded documents** (migrated to Azure OpenAI text-embedding-3-large, 768-dim MRL)
- **Enterprise-grade Azure infrastructure**: Serverless Functions (Flex Consumption), Cosmos DB, Static Web Apps, Microsoft Entra ID authentication
- **PWA-enabled React 18 + TypeScript frontend** with Apple-inspired design system and domain-specific theming
- **Multi-modal interaction**: Text and voice (Azure Neural TTS with 25 personality-matched voices, Web Speech API STT)
- **Production cost**: $15–40/month active, $5–15/month idle

### Vision
To be the definitive "Conversational Wisdom Platform" — combining authentic personality embodiment, strict textual grounding, and cross-domain wisdom access to create a new category at the intersection of AI, education, and cultural heritage.

---

## 2. Objectives & Key Results

| Objective | Key Result | Current Status |
|---|---|---|
| Authenticate every response against source material | Citation rate ≥ 80% across all 25 personalities | ✅ 88% citation rate (validated) |
| Sub-3-second response latency | P95 response time < 3s including AI generation | ✅ 2.17s avg latency |
| Platform reliability | ≥ 99% uptime with automated fallbacks | ✅ 98.7%+ with circuit breakers |
| Engagement retention | Day-1 return rate ≥ 40% via gamified interactions | 🎯 Target (streak system live) |
| Knowledge base completeness | All 25 personalities with ≥ 1 source document | ✅ 31,422 docs across 25 personalities |

---

## 3. Problem Statement

### 3.1 Problem Space
Users seeking wisdom from history's greatest minds face:
- **Inaccessibility** — Historical texts are voluminous, archaic, and require deep scholarly effort to comprehend
- **Fragmentation** — Insights from any specific figure are scattered across multiple lengthy works
- **Domain barriers** — Cross-cultural, cross-discipline navigation is daunting without expert guidance
- **Hallucination risk** — Generic AI chatbots fabricate historical positions, breaking trust
- **Engagement barriers** — Static text interfaces lack the immediacy and naturalness of dialogue
- **Authentication challenges** — Distinguishing authentic wisdom from modern reinterpretation is non-trivial

### 3.2 Vimarsh Solution
Vimarsh distills **31,422 authentic source documents** across 25 personalities into personality-specific, isolated RAG pipelines. Each response is validated against its original knowledge base via Azure Cosmos DB vector search (cosine similarity, 768-dim embeddings), eliminating anachronisms and ensuring strict fidelity to each figure's actual writings and teachings.

---

## 4. Personality Roster

### 🕉️ Spiritual Domain (5 personalities)
| Personality | Key Sources | Documents |
|---|---|---|
| **Krishna** | Bhagavad Gita, Mahabharata, Srimad Bhagavatam | 2,025 |
| **Buddha** | Dhammapada, Suttas, Pali Canon | 289 |
| **Jesus Christ** | King James Bible | 1,847 |
| **Rumi** | Masnavi, Divan-e-Shams | 360 |
| **Swami Vivekananda** | Complete Works, Chicago Lectures | 7 |

### 💭 Philosophical Domain (6 personalities)
| Personality | Key Sources | Documents |
|---|---|---|
| **Marcus Aurelius** | Meditations | 2 |
| **Lao Tzu** | Tao Te Ching | 49 |
| **Confucius** | Analects, Five Classics | 129 |
| **Aristotle** | Nicomachean Ethics, Politics, Metaphysics | 206 |
| **Plato** | Republic, Dialogues | 4 |
| **Socrates** | Via Plato's Dialogues | 3 |

### 🏛️ Leadership Domain (6 personalities)
| Personality | Key Sources | Documents |
|---|---|---|
| **Chanakya** | Arthashastra, Chanakya Niti | 549 |
| **Abraham Lincoln** | Speeches, Letters | 3 |
| **Benjamin Franklin** | Poor Richard's Almanack, Autobiography | 11 |
| **George Washington** | Farewell Address, Papers | 1 |
| **Mahatma Gandhi** | Hind Swaraj, Autobiography | 4 |
| **Martin Luther King Jr.** | Speeches, Letters from Birmingham Jail | 1 |

### 🔬 Scientific Domain (5 personalities)
| Personality | Key Sources | Documents |
|---|---|---|
| **Albert Einstein** | Relativity, Letters, Papers | 332 |
| **Isaac Newton** | Principia, Opticks | 745 |
| **Nikola Tesla** | My Inventions, Patents, Lectures | 18 |
| **Archimedes** | On Floating Bodies, The Sand Reckoner | 33 |
| **Leonardo da Vinci** | Notebooks, Codex | 4 |

### 📚 Literary Domain (2 personalities)
| Personality | Key Sources | Documents |
|---|---|---|
| **Rabindranath Tagore** | Gitanjali, Complete Works | 5,502 |
| **William Shakespeare** | Complete Plays, Sonnets | 19,296 |

### 🧠 Psychology Domain (1 personality)
| Personality | Key Sources | Documents |
|---|---|---|
| **Sigmund Freud** | Interpretation of Dreams, Major Works | 2 |

**Total: 25 personalities · 6 domains · 31,422 documents**

---

## 5. Feature Specifications (MoSCoW)

### 5.1 Must Have — Core Capabilities (Implemented ✅)

| Feature | Description | Status |
|---|---|---|
| **RAG-Driven Conversations** | Every response cross-references personality-specific vector indexes (`text-embedding-3-large`, 768-dim cosine similarity) | ✅ Live |
| **Domain Specialization** | 25 personalities across 6 domains with isolated knowledge bases and authentic voice preservation | ✅ Live |
| **Cross-Session Memory** | Conversation persistence in Cosmos DB with user-personality isolation via `conversations` container | ✅ Live |
| **Microsoft Entra ID Auth** | SSO with `multitenant-personal` configuration; fail-closed pattern (auth failures → 503, never bypass) | ✅ Live |
| **Personality Selector** | Elegant modal interface for browsing/selecting personalities by domain with card-based UI | ✅ Live |
| **Citation Grounding** | Source attribution with automated validation (88% citation rate) — e.g., "Meditations 2.11" for Marcus Aurelius | ✅ Live |
| **PWA Experience** | Full offline functionality, install prompts, service worker, home screen icons, background sync | ✅ Live |
| **Admin Dashboard** | Content management, user analytics, cost monitoring, and quality assurance interface | ✅ Live |
| **Circuit Breaker Resilience** | Three-layer circuit breakers: PersonalityContext, LandingPage onboarding, ProtectedRoute redirect | ✅ Live |
| **Domain Theming** | Apple-inspired design system with 6 domain-specific CSS themes (colors, typography, iconography) | ✅ Live |
| **Voice Interface** | Azure Neural TTS with 25 personality-matched voices (SSML); Web Speech API for STT input | ✅ Live |

### 5.2 Should Have — Engagement & Growth (Implemented ✅)

| Feature | Description | Status |
|---|---|---|
| **Intelligent Onboarding** | 3-step wizard: Intent Discovery → Personality Match → First Question Catalyst (target: < 60s to first interaction) | ✅ Live |
| **Wisdom Streaks** | Daily engagement tracking with fire emoji counter, streak protection (1 free pass/week), milestone badges at 7/30/100/365 days | ✅ Live |
| **Achievement Badges** | Multi-category badge system: Personality Mastery, Engagement, Social, Streak, and Special badges | ✅ Live |
| **Progress Dashboard** | "Your Wisdom Journey" with streak stats, domain exploration radar, personality relationship levels, next milestones | ✅ Live |
| **Wisdom of the Day** | Daily curated wisdom snippets rotating across all 6 domains and 25 personalities | ✅ Live |
| **Social Sharing** | One-click share to Twitter, Facebook, LinkedIn, WhatsApp, Email, and clipboard with styled quote cards | ✅ Live |
| **User Settings Hub** | 5-tab settings page: Profile, Experience, Notifications, Memory & Privacy, Account — with auto-save (500ms debounce) | ✅ Live |
| **Wisdom Archive** | Conversation history with search, bookmarking, and personality-organized browsing | ✅ Live |
| **Memory Dashboard** | Visualization of personality relationship states, insights, and conversation context | ✅ Live |
| **Conversation Style Control** | Brief / Balanced / Detailed response modes configurable per-user in settings | ✅ Live |

### 5.3 Could Have — Future Enhancements (Planned)

| Feature | Description |
|---|---|
| **Personality Quiz** | 5-question adaptive quiz for guided personality discovery with match scoring |
| **Multi-Personality Debates** | Council Mode — summon 2–3 personalities on the same topic for cross-perspective dialogue |
| **Premium Tier** | Unlimited conversations, advanced insights, custom personality training ($9.99/month) |
| **Expanded Personality Roster** | Target 50+ personalities across 10+ domains |
| **Multi-Language Expansion** | Beyond English/Hindi to Sanskrit transliterations and 10+ global languages |
| **Push Notifications** | Re-engagement: streak warnings, daily wisdom, achievement celebrations |
| **Dark Mode** | Adaptive color scheme based on system preference (settings toggle exists) |

---

## 6. Target Audience & Personas

### Primary Personas

| Persona | User Profile | Key Needs | Pain Points |
|---|---|---|---|
| **The Spiritual Seeker** | Exploring inner guidance across traditions (Krishna, Buddha, Jesus, Rumi) | Authentic wisdom, cultural sensitivity, reverent tone | Generic AI bots lack empathy; historical texts are dense and inaccessible |
| **The Domain Researcher** | Seeking analytical frameworks via Einstein, Newton, Aristotle, Freud | Strict source-driven interaction, verifiable citations | Competing platforms hallucinate scientific facts; demand scholarly accuracy |
| **The Cross-Domain Learner** | Curious about connections between spiritual, scientific, and philosophical wisdom | Cross-pollination of ideas, easy personality switching | Knowledge is siloed across academic disciplines |
| **The Professional Leader** | Learning governance and decision-making from Lincoln, Chanakya, Gandhi | Practical applications, strategic wisdom | Historical context lost in modern management literature |

### Audience Characteristics
- **Age Range**: 16–75 (multi-generational)
- **Global**: Multi-cultural audience with emphasis on cross-cultural wisdom traditions
- **Platform**: Mobile-first (PWA-optimized) with desktop support
- **Engagement Mode**: Text-dominant, voice for hands-free and accessibility use cases

---

## 7. Competitive Analysis

### Competitive Positioning

| Competitor | Strengths | Vimarsh's Advantage |
|---|---|---|
| **Character.AI** | 20M+ MAU, vast character variety, open-ended creativity | Scholarly grounding with real source citations; no hallucinated historical positions |
| **Hello History** | Validated historical-chat concept, voice + visuals | Deeper engagement via streaks/badges; sustained value beyond novelty phase |
| **ChatGPT / Gemini / Claude** | Broad knowledge, advanced reasoning | Persistent personality embodiment, cross-session memory, domain-specific RAG |
| **Khan Academy / Coursera** | Structured learning, expert content | Conversational interface makes learning from great minds interactive, not lecture-based |
| **Calm / Headspace** | Spiritual focus, mobile-optimized | Multi-domain (not just spiritual), true personality interaction, scholarly rigor |

### Vimarsh's Unique Differentiators
1. **RAG-First Architecture** — Every response grounded in 31,422 authentic source documents
2. **Cross-Domain Wisdom** — 6 domains in one platform; no competitor spans spiritual through scientific
3. **Enterprise Azure Infrastructure** — 99.9% SLA, HIPAA/SOC2 ready, zero incremental cost via existing Azure credits
4. **Cultural Authenticity** — Indian English voices for South Asian personalities; proper respectful tone per historical context
5. **Voice Character Embodiment** — 25 personality-matched Azure Neural voices with SSML emotional styles

---

## 8. Go-to-Market Strategy

### Growth Flywheel
```
Authentic Wisdom → User Shares Quote → Social Proof → New User → Onboarding Wizard → First Conversation → Streak Begins → Habit Formation → Deeper Engagement → Badge Achievement → Social Sharing
```

### Viral Mechanics
- **Wisdom Quote Cards** — Beautifully designed, personality-branded share cards optimized for social platforms (1200×630 for feeds, 1080×1920 for stories)
- **Achievement Sharing** — "I completed 10 conversations with Krishna" — shareable badge milestones
- **Wisdom of the Day** — Daily curated wisdom driving return visits and introducing unexplored personalities

### Engagement Hooks
- **Streak System** — Daily check-in mechanics with protection and milestone recognition
- **Progressive Feature Discovery** — Contextual tips at optimal moments (e.g., "Try voice mode" after 3rd text message)
- **Re-engagement Mechanics** — Multi-channel re-engagement: in-app welcome-back, personality-specific prompts

---

## 9. Success Metrics

| Metric | Target | Measurement |
|---|---|---|
| **Response Latency (P95)** | < 3s | Azure Application Insights |
| **Citation Rate** | ≥ 80% | RAG service validation |
| **Cache Hit Rate** | ≥ 40% | Cost optimization service |
| **API Call Efficiency** | ≤ 8 calls per page load | Frontend performance monitoring |
| **Time to First Interaction** | < 60s (new users) | Onboarding analytics |
| **Day-1 Retention** | ≥ 40% | Engagement tracking |
| **Personality Exploration Breadth** | ≥ 4 personalities/user | User analytics |
| **Voice Feature Adoption** | ≥ 20% of active users | Usage analytics |
| **Streak Participation** | ≥ 35% of active users | Engagement service |

---

## 10. Non-Functional Requirements

| Requirement | Specification |
|---|---|
| **Security** | Microsoft Entra ID JWT validation; fail-closed auth (503 on auth module failure, never bypass); CORS restricted to production domains only (`vimarsh.vedprakash.net` and Azure Static Web App domain) |
| **Resilience** | Three-layer circuit breakers; intelligent fallback to template responses; Cosmos DB session state with 1,800s TTL replacing in-memory structures |
| **Cost Control** | Monthly budget enforcement ($50 ceiling); real-time cost tracking via Application Insights; 45% cache hit rate reducing AI API costs by ~30% |
| **Data Privacy** | GDPR-compliant data export (JSON); granular privacy modes (Standard / Private / Minimal); configurable data retention (30–365 days); soft-delete with 30-day recovery |
| **Accessibility** | WCAG 2.1 AA compliance; minimum 44×44px touch targets; keyboard navigation; ARIA labels |
| **Performance** | Code splitting via React lazy(); 98% API call reduction via circuit breakers (168+ → 4); sub-2s perceived load on cached visits |

---

*Cross-reference: [Tech-Spec.md](./Tech-Spec.md) for architecture and implementation details · [UX-Spec.md](./UX-Spec.md) for interface design and interaction patterns*
