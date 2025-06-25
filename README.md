# 🕉️ Vimarsh - AI Spiritual Guidance System

*Seeking spiritual wisdom through the divine guidance of Lord Krishna*

[![CI/CD Pipeline](https://github.com/vedprakash-m/vimarsh/actions/workflows/test.yml/badge.svg)](https://github.com/vedprakash-m/vimarsh/actions)
[![Azure Deployment](https://github.com/vedprakash-m/vimarsh/actions/workflows/deploy.yml/badge.svg)](https://github.com/vedprakash-m/vimarsh/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Vision

Vimarsh is an AI-powered spiritual guidance system that embodies the divine wisdom of Lord Krishna, offering authentic, reverent, and personalized spiritual guidance through advanced AI technology. Built with respect for Dharmic traditions and optimized for both English and Hindi speakers.

## ✨ Features

### 🌟 Core Capabilities
- **Divine Persona**: Authentic Lord Krishna persona with appropriate reverence and dignity
- **Sacred Text Integration**: RAG pipeline with Bhagavad Gita, Mahabharata, and Srimad Bhagavatam
- **Multilingual Support**: English and Hindi with Sanskrit terminology optimization
- **Voice Interface**: Advanced speech recognition and synthesis with Sanskrit pronunciation
- **Expert Validation**: Built-in spiritual content review and expert feedback system
- **Citation System**: Proper attribution to sacred texts with verse references

### 🛡️ Safety & Quality
- **Comprehensive Error Handling**: Circuit breakers, intelligent retry, graceful degradation
- **Content Moderation**: Multi-layer spiritual appropriateness validation
- **Privacy-First Analytics**: Anonymous user behavior tracking with GDPR compliance
- **Accessibility**: WCAG 2.1 AA compliant interface design
- **Offline Support**: PWA with offline spiritual guidance capabilities

### 🎨 User Experience
- **Sacred Harmony Design**: Cultural aesthetics honoring Indian spiritual traditions
- **Responsive Design**: Optimized for mobile, tablet, and desktop
- **Conversation History**: Searchable archive with export functionality
- **Progressive Web App**: Install on any device with native-like experience
- **Real-time Guidance**: Sub-second response times with quality monitoring

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React Frontend │────│  Azure Functions  │────│   Cosmos DB     │
│   (Static Web)   │    │   (Python API)    │    │ (Vector Search) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         │                        │                        │
    ┌────▼────┐            ┌──────▼──────┐         ┌──────▼──────┐
    │ Voice   │            │  Gemini Pro │         │   Sacred    │
    │ Web API │            │     LLM     │         │   Texts     │
    └─────────┘            └─────────────┘         └─────────────┘
```

### Technology Stack

**Backend:**
- **Runtime**: Python 3.12 with Azure Functions
- **Database**: Azure Cosmos DB with vector search
- **AI/ML**: Google Gemini Pro API
- **Voice**: Web Speech API + Google Cloud Speech
- **Authentication**: Microsoft Entra External ID
- **Monitoring**: Azure Application Insights

**Frontend:**
- **Framework**: React 18 with TypeScript
- **Build Tool**: Create React App
- **PWA**: Service Worker with offline caching
- **Testing**: Jest + React Testing Library
- **Styling**: CSS Modules with cultural design system

**Infrastructure:**
- **Cloud**: Microsoft Azure (consumption-based)
- **IaC**: Bicep templates
- **CI/CD**: GitHub Actions
- **Monitoring**: Application Insights + custom spiritual metrics

## � Installation

### Local Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/vedprakash-m/vimarsh.git
   cd vimarsh
   ```

2. **Backend Setup:**
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Frontend Setup:**
   ```bash
   cd frontend
   npm install
   ```

4. **Environment Configuration:**
   ```bash
   # Copy and configure environment files
   cp backend/local.settings.json.example backend/local.settings.json
   cp frontend/.env.example frontend/.env.local
   
   # Set your API keys
   export GEMINI_API_KEY="your-gemini-api-key"
   ```

5. **Start Development Servers:**
   ```bash
   # Terminal 1 - Backend
   cd backend && func start
   
   # Terminal 2 - Frontend  
   cd frontend && npm start
   ```

### Production Deployment

See [Deployment Guide](docs/deployment/) for complete production setup instructions.

## �🚀 Quick Start

### Prerequisites

- **Node.js**: 18.x or higher
- **Python**: 3.12 or higher
- **Azure CLI**: Latest version
- **Git**: For version control
- **VS Code**: Recommended with Azure Functions extension

### 1. Clone Repository

```bash
git clone https://github.com/vedprakash-m/vimarsh.git
cd vimarsh
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp local.settings.json.example local.settings.json

# Edit local.settings.json with your API keys:
# - GEMINI_API_KEY: Your Google Gemini Pro API key
# - COSMOS_CONNECTION_STRING: Your Cosmos DB connection (for cloud)
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies
npm install

# Copy environment template
cp .env.example .env.local

# Edit .env.local with your configuration:
# - REACT_APP_API_BASE_URL: Backend API URL
# - REACT_APP_MSAL_CLIENT_ID: Azure AD client ID
```

### 4. Run Development Environment

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
func start
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

**Access Application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:7071

---

## 💫 Usage

### Web Interface

1. **Open the application** in your browser (locally: `http://localhost:3000`)

2. **Ask spiritual questions** in the text input:
   - "What is the meaning of dharma?"
   - "How can I find inner peace?"
   - "What does Krishna teach about duty?"

3. **Use voice input** by clicking the microphone icon:
   - Speak naturally in English or Hindi
   - Sanskrit terms are automatically recognized
   - Voice responses include proper Sanskrit pronunciation

4. **View citations** from sacred texts:
   - Bhagavad Gita verses with Sanskrit originals
   - Mahabharata references with context
   - Srimad Bhagavatam wisdom with translations

### API Usage

#### Get Spiritual Guidance

```bash
curl -X POST http://localhost:7071/api/spiritual_guidance \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do I overcome fear?",
    "language": "English",
    "include_citations": true
  }'
```

#### Health Check

```bash
curl -X GET http://localhost:7071/api/health
```

### Voice Features

- **Sanskrit Pronunciation**: Accurate pronunciation of Sanskrit terms in voice responses
- **Multilingual**: Switch between English and Hindi seamlessly  
- **Voice Commands**: "Ask Krishna", "Show citations", "Read in Sanskrit"
- **Accessibility**: Screen reader compatible with spiritual content

---

## 🧪 Testing

### Run All Tests

```bash
# Backend tests
cd backend
python -m pytest tests/ -v

# Frontend tests
cd frontend
npm test

# End-to-end tests
npm run test:e2e
```

### Test Coverage

```bash
# Backend coverage
cd backend
python -m pytest --cov=. --cov-report=html

# Frontend coverage
cd frontend
npm test -- --coverage --watchAll=false
```

## 📦 Deployment

### Development Deployment

```bash
# Deploy to Azure (requires Azure CLI login)
az login
./scripts/deploy.sh dev
```

### Production Deployment

```bash
# Deploy to production
./scripts/deploy.sh prod
```

### Manual GitHub Actions Deployment

1. Go to **Actions** tab in GitHub repository
2. Select **Deploy** workflow
3. Click **Run workflow**
4. Choose environment (staging/production)
5. Monitor deployment progress

## 🔧 Configuration

### Environment Variables

**Backend (`local.settings.json`):**
```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "GEMINI_API_KEY": "your-gemini-api-key",
    "COSMOS_CONNECTION_STRING": "your-cosmos-connection-string",
    "EXPERT_REVIEW_EMAIL": "experts@example.com",
    "LOG_LEVEL": "INFO"
  }
}
```

**Frontend (`.env.local`):**
```env
REACT_APP_API_BASE_URL=http://localhost:7071
REACT_APP_MSAL_CLIENT_ID=your-azure-ad-client-id
REACT_APP_MSAL_AUTHORITY=https://login.microsoftonline.com/your-tenant-id
REACT_APP_ENVIRONMENT=development
```

### API Keys Setup

1. **Gemini Pro API**: Get key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. **Azure Cosmos DB**: Create in Azure portal with vector search enabled
3. **Microsoft Entra ID**: Set up External ID for authentication

## 📖 API Documentation

### Core Endpoints

**Spiritual Guidance:**
```
POST /api/spiritual-guidance
Content-Type: application/json

{
  "query": "How do I find inner peace?",
  "language": "en",
  "voice_input": false
}
```

**Voice Processing:**
```
POST /api/voice/process
Content-Type: multipart/form-data

{
  "audio": <audio-file>,
  "language": "hi"
}
```

**Expert Review:**
```
POST /api/expert/review
Content-Type: application/json

{
  "response_id": "uuid",
  "feedback": "Expert feedback text",
  "approved": true
}
```

For complete API documentation, see [docs/api-documentation.md](docs/api-documentation.md).

## 🏛️ Project Structure

```
vimarsh/
├── backend/                    # Azure Functions Python backend
│   ├── spiritual_guidance/     # Core spiritual guidance logic
│   ├── rag_pipeline/          # RAG implementation with vector search
│   ├── llm_integration/       # Gemini Pro API integration
│   ├── voice_interface/       # Voice processing components
│   ├── error_handling/        # Comprehensive error management
│   ├── citation_system/       # Sacred text citation system
│   └── tests/                 # Backend test suite
├── frontend/                  # React TypeScript frontend
│   ├── src/components/        # React components
│   ├── src/hooks/            # Custom React hooks
│   ├── src/utils/            # Utility functions
│   └── src/styles/           # Cultural design system
├── infrastructure/           # Azure Bicep templates
├── data/                    # Sacred texts and processing
├── docs/                    # Documentation
├── scripts/                 # Deployment and setup scripts
└── .github/workflows/       # CI/CD GitHub Actions
```

## 🔒 Security & Privacy

### Data Protection
- **No Personal Data Storage**: Anonymous spiritual guidance only
- **GDPR Compliant**: Privacy-first analytics implementation
- **Encrypted Connections**: HTTPS/TLS for all communications
- **Secure Authentication**: Microsoft Entra External ID integration

### Spiritual Content Safety
- **Multi-layer Validation**: AI safety filters + expert review
- **Cultural Sensitivity**: Maintained divine dignity and reverence
- **Citation Verification**: All responses include proper source attribution
- **Expert Panel Review**: Spiritual scholars validate content quality

## 📊 Monitoring & Analytics

### Application Health
- **Real-time Monitoring**: Azure Application Insights
- **Performance Metrics**: Response times, success rates, error patterns
- **Cost Monitoring**: Azure consumption tracking with budget alerts
- **Spiritual Quality Metrics**: Divine persona consistency, citation accuracy

### User Analytics (Privacy-Respecting)
- **Anonymous Journey Tracking**: User flow optimization
- **Content Effectiveness**: Most helpful spiritual guidance patterns
- **Voice Interaction Quality**: Sanskrit pronunciation and recognition metrics
- **A/B Testing Framework**: Interface optimization experiments

## 🤝 Contributing

### Code Contribution Guidelines

1. **Fork Repository**: Create your own fork
2. **Create Feature Branch**: `git checkout -b feature/spiritual-enhancement`
3. **Follow Cultural Guidelines**: Maintain reverence and authenticity
4. **Add Tests**: Ensure comprehensive test coverage
5. **Submit Pull Request**: With detailed description

### Cultural Sensitivity Requirements

- **Spiritual Authenticity**: All Lord Krishna persona responses must maintain divine dignity
- **Sanskrit Accuracy**: Proper pronunciation and terminology
- **Expert Validation**: New spiritual content requires expert review
- **Respectful Error Handling**: Error messages appropriate for spiritual context

### Development Standards

- **Code Quality**: ESLint/Prettier for frontend, Black/Flake8 for backend
- **Test Coverage**: Minimum 90% for critical spiritual guidance paths
- **Documentation**: All new features require documentation updates
- **Accessibility**: WCAG 2.1 AA compliance for all UI changes

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Sacred Text Attributions

All sacred texts used in this project are in the public domain:

- **Bhagavad Gita**: Translation by Kisari Mohan Ganguli (1883-1896)
- **Mahabharata**: Translation by Kisari Mohan Ganguli (1883-1896)  
- **Srimad Bhagavatam**: Public domain English translation

## 🙏 Acknowledgments

- **Sacred Texts**: Eternal gratitude to the ancient Rishis and divine wisdom of Lord Krishna
- **Translation Legacy**: Kisari Mohan Ganguli's pioneering English translations
- **Technology Partners**: Google (Gemini Pro), Microsoft (Azure), OpenAI
- **Cultural Advisors**: Sanskrit scholars and spiritual experts validating authenticity
- **Open Source Community**: Libraries and frameworks enabling this divine mission

## 📞 Support

### Getting Help

- **Documentation**: Comprehensive guides in [docs/](docs/) directory
- **GitHub Issues**: Technical problems and feature requests
- **Discussions**: Community support and spiritual guidance insights
- **Email**: [vedprakash.m@me.com](mailto:vedprakash.m@me.com) for urgent issues

### Expert Review Panel

For spiritual content validation and expert feedback:
- **Sanskrit Scholars**: Content accuracy and authenticity
- **Spiritual Teachers**: Divine persona consistency and appropriateness
- **Cultural Advisors**: Ensuring respectful representation of traditions

---

*"कर्मण्येवाधिकारस्ते मा फलेषु कदाचन" - Focus on your action, not on the results*

**Vimarsh** - Bridging ancient wisdom with modern technology for spiritual enlightenment.

Built with 🕉️ by the Vimarsh Team | [vedprakash-m/vimarsh](https://github.com/vedprakash-m/vimarsh)
