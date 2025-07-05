# Vimarsh - AI Spiritual Guidance System

[![CI/CD Pipeline](https://github.com/vedprakash-m/vimarsh/actions/workflows/unified-ci-cd.yml/badge.svg)](https://github.com/vedprakash-m/vimarsh/actions)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

Vimarsh is an AI-powered chat application that provides spiritual guidance based on Hindu sacred texts. The system uses a RAG (Retrieval-Augmented Generation) architecture to answer questions about dharma, meditation, and spiritual practices, drawing from sources like the Bhagavad Gita and Mahabharata.

**Live Application**: https://vimarsh.vedprakash.net

## Architecture

### Backend
- **Runtime**: Python 3.12 on Azure Functions (serverless)
- **LLM Integration**: Google Gemini 2.5 Flash API
- **Database**: Azure Cosmos DB for vector storage and chat history
- **Authentication**: Microsoft Entra ID
- **Infrastructure**: Azure cloud services managed via Bicep templates

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **UI**: Custom CSS with spiritual theming
- **Deployment**: Azure Static Web Apps
- **Features**: Markdown rendering, responsive design

### Data Sources
- Bhagavad Gita (English translations)
- Selected portions of Mahabharata
- Srimad Bhagavatam excerpts
- All sources are public domain texts

## Setup

### Prerequisites
- Node.js 18+
- Python 3.12+
- Azure CLI (for deployment)

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/vedprakash-m/vimarsh.git
   cd vimarsh
   ```

2. **Backend setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Frontend setup**
   ```bash
   cd frontend
   npm install
   ```

4. **Environment configuration**
   - Copy `backend/local.settings.json.template` to `backend/local.settings.json`
   - Add your Google Gemini API key and Azure connection strings
   - Configure CORS settings for local development

5. **Start development servers**
   ```bash
   # Terminal 1 - Backend
   cd backend && func start
   
   # Terminal 2 - Frontend
   cd frontend && npm start
   ```

## Deployment

The application uses Azure cloud services with infrastructure defined in Bicep templates.

### Cost Management
The project implements a two-resource-group architecture:
- **vimarsh-db-rg**: Persistent storage (Cosmos DB, Key Vault) - ~$5-10/month
- **vimarsh-rg**: Compute resources (Functions, Static Web App) - can be paused when not in use

### Production Deployment
```bash
# Deploy infrastructure and application
az login
./scripts/deploy.sh

# Monitor costs
az consumption budget list
```

## Features

### Core Functionality
- **Chat Interface**: Ask questions about spiritual topics and receive responses with citations
- **Vector Search**: Semantic search through processed sacred texts
- **Context Preservation**: Conversation history maintained across sessions
- **Markdown Support**: Rich text formatting in responses
- **Mobile Responsive**: Works on desktop and mobile devices

### AI Integration
- **LLM Provider**: Google Gemini 2.5 Flash for text generation
- **Prompt Engineering**: Specialized prompts for spiritual context and persona consistency
- **Response Formatting**: Structured responses with proper citations and Sanskrit terms
- **Safety Measures**: Content filtering and appropriate spiritual guidance

### Data Processing
- **Text Chunking**: Sacred texts processed into searchable segments
- **Vector Embeddings**: Text converted to vectors for similarity search
- **Citation Tracking**: Source references maintained for all content
- **Content Validation**: Quality checks for spiritual accuracy

## Technical Details

### Backend Components
```
backend/
├── function_app.py           # Azure Functions entry point
├── spiritual_guidance/       # Core AI service
├── rag_pipeline/            # Text processing and search
├── auth/                    # Authentication handlers
├── config/                  # Configuration management
└── tests/                   # Test suites
```

### Frontend Structure
```
frontend/
├── src/
│   ├── components/          # React components
│   ├── services/           # API integration
│   ├── styles/             # CSS and theming
│   └── utils/              # Helper functions
├── public/                 # Static assets
└── build/                  # Production build output
```

### Infrastructure
- **Resource Groups**: Separated persistent and ephemeral resources
- **Monitoring**: Application Insights for performance tracking
- **Security**: Key Vault for secrets, Entra ID for authentication
- **CI/CD**: GitHub Actions for automated deployment

## Testing

### Running Tests
```bash
# Backend tests
cd backend
python -m pytest tests/ -v --cov

# Frontend tests
cd frontend
npm test

# End-to-end validation
python scripts/local_e2e_validation.py
```

### Test Coverage
- Backend: Core spiritual guidance functionality
- Frontend: Component rendering and user interactions
- Integration: API endpoints and data flow
- Security: Authentication and authorization

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/description`
3. Make changes and add tests
4. Submit a pull request

### Guidelines
- Maintain respectful treatment of spiritual content
- Follow existing code style and conventions
- Add tests for new functionality
- Update documentation as needed

## Documentation

Additional documentation is available in the `docs/` directory:
- `metadata.md` - Project overview and status
- `PRD_Vimarsh.md` - Product requirements
- `Tech_Spec_Vimarsh.md` - Technical specifications
- `User_Experience.md` - UX design guidelines

## License

This project is licensed under the GNU Affero General Public License v3 (AGPLv3). See [LICENSE](LICENSE) for details.

### Sacred Text Attribution
All sacred texts used are in the public domain:
- Bhagavad Gita: Translation by Kisari Mohan Ganguli (1883-1896)
- Mahabharata: Translation by Kisari Mohan Ganguli (1883-1896)
- Srimad Bhagavatam: Public domain English translations

## Contact

- **Repository**: https://github.com/vedprakash-m/vimarsh
- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Email**: vedprakash.m@me.com
