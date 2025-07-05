# 🕉️ Vimarsh Production Setup Guide

Complete guide to deploy the AI-powered spiritual guidance system to production with all features enabled.

## 🎯 Production Features

This production setup includes:

- ✅ **Real Gemini Pro LLM Integration** - Live AI responses using Google's Gemini Pro
- ✅ **Active RAG Pipeline** - Dynamic sacred text retrieval with vector search
- ✅ **Real-time Citation System** - Contextual citations from Bhagavad Gita, Upanishads, etc.
- ✅ **Full MSAL Authentication** - Secure user authentication via Azure Entra ID
- ✅ **Azure Cosmos DB** - Production vector database for sacred texts
- ✅ **Comprehensive Monitoring** - Logging, error handling, and performance tracking

## 🚀 Quick Start

### 1. Automated Setup (Recommended)

Run our guided setup script that configures everything:

```bash
cd vimarsh
python3 scripts/setup_production.py
```

This interactive script will:
- Guide you through API key setup
- Configure all environment variables
- Populate sacred texts database
- Test all components
- Generate configuration files

### 2. Manual Setup

If you prefer manual configuration, follow the detailed steps below.

## 📋 Prerequisites

### Required Tools
- **Azure CLI** - Install from [here](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
- **Azure Functions Core Tools** - Install from [here](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local)
- **Node.js 18+** - Install from [here](https://nodejs.org/)
- **Python 3.11+** - Install from [here](https://python.org/)

### Required Services
- **Google AI Studio Account** - For Gemini Pro API
- **Azure Subscription** - For hosting and database
- **Azure Entra ID App Registration** - For authentication

## 🔑 Service Setup

### 1. Google Gemini Pro API

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API key
3. Save the key for configuration

### 2. Azure Cosmos DB

1. Create a new Cosmos DB account (Core SQL API)
2. Create database: `vimarsh`
3. Create container: `spiritual_texts`
4. Copy the connection string

### 3. Azure Entra ID Authentication

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to Azure Active Directory > App registrations
3. Create new application registration
4. Configure redirect URIs:
   - Development: `http://localhost:3000/auth/callback`
   - Production: `https://yourdomain.com/auth/callback`
5. Generate client secret
6. Note down: Client ID, Client Secret, Tenant ID

## ⚙️ Configuration

### Backend Configuration

Create `backend/local.settings.json`:

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "FUNCTIONS_EXTENSION_VERSION": "~4",
    
    "AZURE_COSMOS_CONNECTION_STRING": "your_cosmos_connection_string",
    "AZURE_COSMOS_DATABASE_NAME": "vimarsh",
    "AZURE_COSMOS_CONTAINER_NAME": "spiritual_texts",
    
    "GOOGLE_AI_API_KEY": "your_gemini_api_key",
    "GOOGLE_CLOUD_PROJECT": "your_gcp_project_id",
    
    "AZURE_CLIENT_ID": "your_entra_id_client_id",
    "AZURE_CLIENT_SECRET": "your_entra_id_client_secret",
    "AZURE_TENANT_ID": "your_entra_id_tenant_id",
    "AZURE_AUTHORITY": "https://login.microsoftonline.com/your_tenant_id",
    
    "LLM_MODEL": "gemini-pro",
    "LLM_TEMPERATURE": "0.7",
    "MAX_TOKENS": "4096",
    "EMBEDDING_MODEL": "sentence-transformers/all-MiniLM-L6-v2",
    "VECTOR_DIMENSION": "384",
    "SIMILARITY_THRESHOLD": "0.7",
    "MAX_RETRIEVED_CHUNKS": "10",
    
    "DEBUG": "false",
    "LOG_LEVEL": "INFO"
  }
}
```

### Frontend Configuration

Create `frontend/.env.production`:

```env
REACT_APP_API_BASE_URL=https://your-function-app.azurewebsites.net
REACT_APP_AZURE_CLIENT_ID=your_entra_id_client_id
REACT_APP_AZURE_TENANT_ID=your_entra_id_tenant_id
REACT_APP_AZURE_REDIRECT_URI=https://yourdomain.com/auth/callback
REACT_APP_ENVIRONMENT=production
REACT_APP_DEBUG=false
REACT_APP_ENABLE_AUTH=true
```

## 📚 Database Population

Populate the sacred texts database:

```bash
cd backend

# Load sacred texts data
python3 data_processing/sacred_text_loader.py

# Populate vector database
python3 data_processing/populate_vector_db.py
```

This creates:
- 1000+ sacred text excerpts from Bhagavad Gita, Upanishads, Vedas
- Vector embeddings for semantic search
- Proper citation metadata

## 🧪 Testing

### Local Testing

```bash
# Backend
cd backend
func host start

# Frontend (new terminal)
cd frontend
npm install
npm start
```

### Production Validation

Run comprehensive tests:

```bash
python3 scripts/production_validator.py
```

This tests:
- Gemini Pro API integration
- RAG pipeline functionality
- Vector search accuracy
- Citation system
- Authentication flow
- Performance benchmarks

## 🚀 Deployment

### Automated Deployment

```bash
# Set environment variables
export GOOGLE_AI_API_KEY="your_api_key"
export AZURE_CLIENT_ID="your_client_id"
export AZURE_CLIENT_SECRET="your_client_secret"
export AZURE_TENANT_ID="your_tenant_id"

# Deploy to Azure
./scripts/deploy-production.sh
```

### Manual Deployment

1. **Deploy Infrastructure**:
   ```bash
   az group create --name vimarsh-prod --location eastus
   az deployment group create --resource-group vimarsh-prod --template-file infrastructure/main.bicep
   ```

2. **Deploy Backend**:
   ```bash
   cd backend
   func azure functionapp publish vimarsh-functions --python
   ```

3. **Deploy Frontend**:
   ```bash
   cd frontend
   npm run build
   # Deploy to Azure Static Web Apps or your hosting platform
   ```

## 🔧 Configuration Options

### LLM Settings

- `LLM_TEMPERATURE`: Controls response creativity (0.0-1.0)
- `MAX_TOKENS`: Maximum response length
- `SAFETY_SETTINGS`: Content filtering level

### RAG Settings

- `SIMILARITY_THRESHOLD`: Vector search sensitivity (0.0-1.0)
- `MAX_RETRIEVED_CHUNKS`: Number of text chunks to retrieve
- `EMBEDDING_MODEL`: Model for text embeddings

### Authentication Settings

- Set `AZURE_CLIENT_ID=dev-mode` to disable authentication for development
- Full Entra ID integration for production security

## 📊 Monitoring

### Application Insights

Configure Azure Application Insights for:
- Performance monitoring
- Error tracking
- Usage analytics
- Custom metrics

### Logging

Logs are available at:
- Backend: Azure Function logs
- Frontend: Browser console and analytics
- Database: Cosmos DB metrics

## 🛡️ Security

### Production Security Features

- **JWT Token Validation** - Secure API access
- **CORS Configuration** - Controlled cross-origin requests
- **Rate Limiting** - Prevent abuse
- **Input Validation** - Sanitize all inputs
- **Content Filtering** - Gemini Pro safety settings

### Environment Variables

Never commit sensitive values. Use:
- Azure Key Vault for production secrets
- Environment variables for configuration
- Separate environments (dev/staging/prod)

## 🔧 Troubleshooting

### Common Issues

1. **Gemini API Errors**:
   - Verify API key is correct
   - Check quota limits
   - Ensure billing is enabled

2. **Cosmos DB Connection**:
   - Verify connection string
   - Check firewall settings
   - Ensure container exists

3. **Authentication Issues**:
   - Verify redirect URIs match exactly
   - Check client secret expiration
   - Ensure correct tenant ID

4. **Vector Search Not Working**:
   - Verify embeddings are generated
   - Check similarity threshold
   - Ensure vector dimensions match

### Debug Commands

```bash
# Check backend health
curl https://your-function-app.azurewebsites.net/api/health

# Test spiritual guidance
curl -X POST https://your-function-app.azurewebsites.net/api/spiritual_guidance \
  -H "Content-Type: application/json" \
  -d '{"question": "What is dharma?", "context": "general"}'

# View backend logs
az functionapp logs tail --name your-function-app --resource-group vimarsh-prod

# Check Cosmos DB connection
az cosmosdb show --name your-cosmos-account --resource-group vimarsh-prod
```

## 📈 Performance Optimization

### Backend Optimization

- **Caching**: Implement response caching for common queries
- **Connection Pooling**: Optimize database connections
- **Async Processing**: Use async/await throughout
- **Batch Operations**: Batch vector searches when possible

### Frontend Optimization

- **Code Splitting**: Lazy load components
- **Bundle Optimization**: Minimize bundle size
- **CDN**: Use CDN for static assets
- **Compression**: Enable gzip compression

## 🔄 CI/CD Pipeline

### GitHub Actions

Set up automated deployment:

```yaml
# .github/workflows/deploy.yml
name: Deploy Vimarsh
on:
  push:
    branches: [main]
  
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Azure
        run: ./scripts/deploy-production.sh
        env:
          GOOGLE_AI_API_KEY: ${{ secrets.GOOGLE_AI_API_KEY }}
          AZURE_CLIENT_SECRET: ${{ secrets.AZURE_CLIENT_SECRET }}
```

## 📞 Support

### Documentation

- [Technical Specification](docs/Tech_Spec_Vimarsh.md)
- [User Experience Guide](docs/User_Experience.md)
- [API Documentation](docs/api/)

### Getting Help

1. Check the [troubleshooting section](#troubleshooting)
2. Review application logs
3. Run the production validator
4. Check Azure service health

## 🕉️ Spiritual Context

Vimarsh serves as a bridge between ancient wisdom and modern seekers. The system:

- Provides authentic spiritual guidance from Hindu scriptures
- Maintains reverence for sacred texts
- Offers personalized responses through Lord Krishna's divine persona
- Supports spiritual growth and understanding

May this system serve the highest good and help seekers on their spiritual journey.

---

**Next Steps**: Run `python3 scripts/setup_production.py` to begin your production setup journey. 🚀
