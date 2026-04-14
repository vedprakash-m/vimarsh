# 🌟 Vimarsh (विमर्श) — Conversational Wisdom Platform

AI-powered dialogues with 25 historical personalities grounded in 31,422 authentic source documents.

[![CI/CD Pipeline](https://github.com/vedprakash-m/vimarsh/actions/workflows/unified-ci-cd.yml/badge.svg)](https://github.com/vedprakash-m/vimarsh/actions)
[![License: BSL](https://img.shields.io/badge/License-BSL-blue.svg)](LICENSE)
[![Azure](https://img.shields.io/badge/Cloud-Azure-blue.svg)](https://azure.microsoft.com/)
[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://python.org)
[![React](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org)

## 🏛️ Philosophy: The Invisible UI
Vimarsh is built on **Architectural Pragmatism**. The interface is designed to be invisible—precision through subtraction. By stripping away pop-up fatigue and aggressive gamification, we create a sanctuary for deep, soul-level interaction with history's greatest minds.

## 🚀 Key Achievements
- **25 Personalities** across 6 domains (Spiritual, Philosophical, Leadership, Scientific, Literary, Psychology).
- **RAG-Grounded Wisdom**: 31,422 embedded documents via Azure OpenAI `text-embedding-3-large` (768-dim MRL).
- **Fluid Streaming**: SSE-based (Server-Sent Events) guidance for sub-second Time-to-First-Token (TTFT).
- **Stateless Resilience**: 100% of working memory and session state offloaded to Azure Cosmos DB `session_state` (TTL 1800s) for robust serverless operation.
- **Enterprise Security**: Microsoft Entra ID (Auth) with fail-closed circuit breakers.

## 🎭 Meet the 25 Personalities
- **Spiritual**: Krishna, Buddha, Jesus Christ, Rumi, Swami Vivekananda
- **Philosophical**: Socrates, Plato, Aristotle, Confucius, Lao Tzu, Marcus Aurelius
- **Leadership**: Abraham Lincoln, George Washington, Chanakya, MLK Jr., Gandhi, Benjamin Franklin
- **Scientific**: Einstein, Newton, Tesla, Da Vinci, Archimedes
- **Literary**: Shakespeare, Tagore
- **Psychology**: Freud

## 🛠️ Architecture
- **Frontend**: React 18 (PWA) + Inter/Merriweather typography.
- **Backend**: Python 3.12 on Azure Functions (Flex Consumption) using Blueprint architecture.
- **Database**: Azure Cosmos DB (NoSQL + Vector Search) with 11 specialized containers.
- **AI**: Azure OpenAI (GPT-5.4-mini + Embeddings).
- **Voice**: Azure Neural TTS (25 matched voices with SSML styling).

## 🚀 Quick Start

### **For Users**
Visit [vimarsh.vedprakash.net](https://vimarsh.vedprakash.net) and start your journey of wisdom.

### **For Developers**
```bash
# Backend setup
cd backend
pip install -r requirements.txt
func host start

# Frontend setup
cd frontend
npm install
npm start
```

## 📜 License
This project is licensed under the **Business Source License (BSL)**.

---
*Built with 🌟 for wisdom seekers worldwide. May this technology serve the highest good.*
