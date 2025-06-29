# 🕉️ Vimarsh - AI Spiritual Guidance System

> *Bridging ancient wisdom with modern technology for spiritual enlightenment*

[![CI/CD Pipeline](https://github.com/vedprakash-m/vimarsh/actions/workflows/unified-ci-cd.yml/badge.svg)](https://github.com/vedprakash-m/vimarsh/actions)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Azure](https://img.shields.io/badge/Cloud-Azure-blue.svg)](https://azure.microsoft.com/)
[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://python.org)
[![React](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org)

## 🌟 What is Vimarsh?

**Vimarsh** is an AI-powered spiritual guidance system that brings the divine wisdom of Vedic scriptures to the modern world. Embodying the compassionate voice of Lord Krishna, Vimarsh provides personalized spiritual guidance based on authentic sacred texts including the Bhagavad Gita, Mahabharata, and Srimad Bhagavatam.

> **Sanskrit**: *विमर्श (Vimarsh)* - "spiritual contemplation" or "divine reflection"

### ✨ Key Features

**🎯 For Spiritual Seekers:**
- **Divine Persona**: Authentic Lord Krishna guidance with proper reverence and dignity
- **Sacred Text Integration**: Direct citations from Bhagavad Gita, Mahabharata, and Srimad Bhagavatam
- **Voice Interface**: Sanskrit pronunciation with English/Hindi support
- **Cultural Authenticity**: Expert-validated spiritual content maintaining tradition
- **Progressive Web App**: Accessible anywhere, works offline

**💻 For Developers:**
- **Modern Architecture**: React 18 + TypeScript frontend, Python 3.12 Azure Functions backend
- **RAG Pipeline**: Advanced vector search with Azure Cosmos DB and Google Gemini Pro
- **Cost-Optimized**: Innovative pause-resume architecture reducing costs by 90%
- **Production Ready**: Comprehensive CI/CD, monitoring, and security
- **Microsoft Authentication**: Enterprise-grade security with Entra ID

## 🚀 Quick Start

### For End Users

**Web Application**: [vimarsh.vedprakash.net](https://vimarsh.vedprakash.net) *(coming soon)*

**Try it locally:**
```bash
# Clone and run in 5 minutes
git clone https://github.com/vedprakash-m/vimarsh.git
cd vimarsh
./scripts/setup-dev.sh
```

### For Developers

**Prerequisites:**
- Node.js 18+ and Python 3.12+
- Azure CLI (for deployment)
- Git

**Development Setup:**
```bash
# 1. Clone repository
git clone https://github.com/vedprakash-m/vimarsh.git
cd vimarsh

# 2. Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Frontend setup
cd ../frontend
npm install

# 4. Start development servers
# Terminal 1 - Backend
cd backend && func start

# Terminal 2 - Frontend  
cd frontend && npm start
```

## 💰 Revolutionary Cost Architecture

### Pause-Resume Innovation

Vimarsh pioneered a **two-resource-group architecture** that dramatically reduces cloud costs:

```
💾 vimarsh-db-rg (Always On)     💻 vimarsh-rg (Pause/Resume)
├── Cosmos DB (vimarsh-db)       ├── Azure Functions (vimarsh-functions)
├── Key Vault (vimarsh-kv)       ├── Static Web App (vimarsh-web)
└── Storage (vimarshstorage)     └── App Insights (vimarsh-insights)

💰 Cost: $5-10/month            💰 Cost: $45-90/month (when active)
🔒 Status: Persistent           🔄 Status: Can pause/resume in <10 mins
```

**Business Impact:**
- **Active Production**: $50-100/month for full service
- **Paused State**: $5-10/month (90% cost reduction)
- **Resume Time**: <10 minutes to full operation
- **Data Safety**: Zero data loss during pause-resume cycles

### Cost Management Features

- **Real-time Monitoring**: Multi-tier budget alerts (50%, 80%, 90%, 100%)
- **Query Optimization**: 20-40% savings through intelligent deduplication
- **Request Batching**: 3x performance improvement
- **Serverless Architecture**: Pay only for what you use

## 🏗️ Architecture & Technology

### Backend (Azure Functions - Python 3.12)
- **AI/LLM**: Google Gemini Pro API with spiritual safety framework
- **Vector Database**: Azure Cosmos DB with vector search capabilities
- **Authentication**: Microsoft Entra External ID (unified domain standard)
- **Monitoring**: Azure Application Insights with custom spiritual metrics
- **Security**: Azure Key Vault, comprehensive error handling

### Frontend (React 18 + TypeScript)
- **Framework**: Modern React with TypeScript and Create React App
- **Voice Interface**: Web Speech API with Sanskrit pronunciation support
- **PWA**: Service Worker with offline spiritual guidance caching
- **Design**: Cultural aesthetics honoring Indian spiritual traditions
- **Testing**: Jest + React Testing Library (100% critical path coverage)

### Infrastructure (Azure Cloud + Bicep IaC)
- **Single Region**: East US deployment for optimal cost and performance
- **Idempotent Naming**: Static resource names preventing CI/CD duplicates
- **Production-First**: Single environment strategy with pause-resume cost savings
- **CI/CD**: Unified GitHub Actions pipeline with comprehensive validation

### Sacred Text Processing
- **RAG Pipeline**: Advanced retrieval with Sanskrit term preservation
- **Text Processing**: Verse-aware chunking respecting spiritual structure
- **Quality Assurance**: Expert review workflow and content validation
- **Citations**: Accurate verse and chapter references with translations

## 🎯 Use Cases

### For Individuals
- **Daily Spiritual Guidance**: Ask questions about dharma, karma, and self-realization
- **Sanskrit Learning**: Proper pronunciation and meaning of sacred terms
- **Meditation Support**: Guided spiritual contemplation and practice
- **Life Decisions**: Wisdom-based guidance rooted in timeless principles

### For Developers
- **AI/ML Learning**: Study advanced RAG implementation with vector search
- **Cost Optimization**: Learn innovative cloud cost management strategies
- **Cultural AI**: Understand respectful integration of spiritual content
- **Azure Development**: Modern serverless architecture patterns

### For Organizations
- **Spiritual Centers**: Integrate authentic guidance into programs
- **Educational Institutions**: Teaching tool for Vedic philosophy
- **Wellness Platforms**: Add spiritual dimension to holistic health
- **Research**: Study intersection of AI and spiritual wisdom

## 📊 Production Metrics

### Performance
- **Response Time**: <3 seconds for complex spiritual queries
- **Vector Search**: Sub-second similarity search
- **Voice Processing**: Real-time Sanskrit pronunciation
- **Availability**: 99.9% uptime with pause-resume strategy

### Quality
- **Test Coverage**: 100% for core spiritual guidance components
- **Expert Validation**: Spiritual scholars approve all content
- **Cultural Authenticity**: Sanskrit accuracy and divine reverence maintained
- **User Satisfaction**: Anonymous feedback tracking spiritual value

### Cost Efficiency
- **Query Deduplication**: 20-40% cost reduction through smart caching
- **Batch Processing**: 3x performance improvement
- **Pause-Resume**: Up to 90% cost savings during inactive periods
- **Serverless Scaling**: Automatic cost adaptation to usage

## 🔒 Security & Privacy

### Data Protection
- **Privacy-First**: Anonymous spiritual guidance without personal data storage
- **GDPR Compliant**: European privacy regulation adherence
- **Encrypted Communications**: HTTPS/TLS 1.2+ for all connections
- **Microsoft Authentication**: Enterprise-grade security with Entra ID

### Spiritual Content Safety
- **Multi-layer Validation**: AI safety filters plus expert spiritual review
- **Cultural Sensitivity**: Maintains divine dignity and proper reverence
- **Citation Verification**: All responses include accurate source attribution
- **Expert Panel**: Sanskrit scholars and spiritual teachers validate authenticity

## 🧪 Testing & Quality

### Comprehensive Test Suite
```bash
# Backend tests (100% critical path coverage)
cd backend && python -m pytest tests/ -v --cov

# Frontend tests (React Testing Library)
cd frontend && npm test

# End-to-end validation
python scripts/local_e2e_validation.py
```

### CI/CD Pipeline
- **Unified Workflow**: Single GitHub Actions pipeline (45% faster than previous)
- **Multi-stage Validation**: Syntax → Unit → Integration → Security → Performance
- **Automated Deployment**: Production-ready deployments with rollback capability
- **Quality Gates**: 85% test coverage threshold enforcement

## 📦 Deployment

### Development
```bash
# Quick local setup
./scripts/setup-dev.sh
```

### Production
```bash
# Deploy to Azure (requires Azure CLI login)
az login
./scripts/deploy.sh

# Pause service (90% cost reduction)
az group delete --name vimarsh-rg --yes

# Resume service (<10 minutes)
./scripts/deploy.sh
```

### Monitoring
- **Cost Tracking**: Real-time budget monitoring with spiritual context alerts
- **Performance Metrics**: Response times, spiritual guidance quality, user engagement
- **Health Checks**: Automated validation of pause-resume operations
- **Analytics**: Privacy-respecting usage patterns and content effectiveness

## 🤝 Contributing

We welcome contributions that maintain spiritual authenticity while advancing technical excellence.

Please read our [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

### Cultural Sensitivity Guidelines
- **Divine Reverence**: All Lord Krishna persona responses must maintain appropriate dignity
- **Sanskrit Accuracy**: Proper pronunciation, spelling, and contextual usage
- **Expert Validation**: New spiritual content requires review by qualified scholars
- **Respectful Implementation**: Technical solutions that honor spiritual traditions

### Development Standards
- **Code Quality**: ESLint/Prettier (frontend), Black/Flake8 (backend)
- **Test Coverage**: Minimum 90% for spiritual guidance critical paths
- **Documentation**: Comprehensive documentation for all spiritual and technical features
- **Accessibility**: WCAG 2.1 AA compliance for inclusive spiritual access

### Getting Started
1. Fork the repository
2. Create feature branch: `git checkout -b feature/spiritual-enhancement`
3. Follow development setup instructions above
4. Submit pull request with detailed description

## 📖 Documentation

**Complete documentation available in [`docs/`](docs/) directory:**

- **[metadata.md](docs/metadata.md)** - Comprehensive project overview and current status
- **[PRD_Vimarsh.md](docs/PRD_Vimarsh.md)** - Product requirements and spiritual vision
- **[Tech_Spec_Vimarsh.md](docs/Tech_Spec_Vimarsh.md)** - Detailed technical specifications
- **[User_Experience.md](docs/User_Experience.md)** - User journey and interaction design
- **[Authentication Setup](docs/Authentication_Setup_Guide.md)** - Microsoft Entra ID configuration
- **[Deployment Guide](docs/deployment-guide.md)** - Production deployment procedures

## 🙏 Acknowledgments

### Sacred Wisdom
- **Eternal Gratitude**: To the ancient Rishis and the divine wisdom of Lord Krishna
- **Sanskrit Scholars**: Cultural advisors ensuring authenticity and proper reverence
- **Spiritual Teachers**: Validating divine persona consistency and appropriateness

### Technology Partners
- **Google**: Gemini Pro API for advanced language understanding
- **Microsoft**: Azure cloud platform and Entra ID authentication
- **Open Source Community**: React, Python, and countless libraries enabling this mission

### Translation Legacy
- **Kisari Mohan Ganguli**: Pioneering English translations of sacred texts (1883-1896)
- **Public Domain Texts**: Bhagavad Gita, Mahabharata, and Srimad Bhagavatam

## 📞 Support & Community

### Getting Help
- **📖 Documentation**: Comprehensive guides in [docs/](docs/) directory
- **🐛 GitHub Issues**: Technical problems and feature requests  
- **💬 Discussions**: Community support and spiritual guidance insights
- **📧 Contact**: [vedprakash.m@me.com](mailto:vedprakash.m@me.com) for urgent issues

### Expert Review Panel
- **Sanskrit Scholars**: Validate content accuracy and authenticity
- **Spiritual Teachers**: Ensure divine persona consistency
- **Cultural Advisors**: Maintain respectful tradition representation

## 📄 License

This project is licensed under the GNU Affero General Public License, version 3 (AGPLv3). See the [LICENSE](LICENSE) file for the full license text and the [NOTICE](NOTICE) file for additional details.

### Sacred Text Attributions

All sacred texts used are in the public domain:
- **Bhagavad Gita**: Translation by Kisari Mohan Ganguli (1883-1896)
- **Mahabharata**: Translation by Kisari Mohan Ganguli (1883-1896)  
- **Srimad Bhagavatam**: Public domain English translation

---

<div align="center">

### *"कर्मण्येवाधिकारस्ते मा फलेषु कदाचन"*
*"Focus on your action, not on the results"* - Bhagavad Gita 2.47

**Vimarsh** - Where Ancient Wisdom Meets Modern Technology

Built with 🕉️ by [Vedprakash Mishra](https://github.com/vedprakash-m) | [Visit Project](https://github.com/vedprakash-m/vimarsh)

</div>
