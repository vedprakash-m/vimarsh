# 🚀 Vimarsh Deployment Guide

Complete guide for deploying Vimarsh AI Spiritual Guidance System to production.

## Overview

Vimarsh uses a modern cloud-native architecture with a unified resource group strategy:

### Architecture Components
- **Backend:** Azure Functions (Python) - Consumption plan for cost efficiency
- **Frontend:** Azure Static Web Apps (React) - Free tier for optimal cost
- **Database:** Azure Cosmos DB with vector search - Serverless mode
- **AI:** Google Gemini Pro API - Pay-per-use model
- **Authentication:** Microsoft Entra External ID - Free tier
- **Monitoring:** Azure Application Insights - Basic tier
- **Security:** Azure Key Vault - Standard tier

### Unified Resource Group Strategy (Simplified Management)

**vimarsh-rg (All Resources):**
- Cosmos DB (`vimarsh-db`) - Multi-personality knowledge base
- Key Vault (`vimarsh-kv-*`) - Secrets and configuration  
- Storage Account (`vimarshstorage`) - Content and function storage
- Function App (`vimarsh-backend-app`) - Backend API
- Static Web App (`vimarsh-frontend`) - Frontend application
- Application Insights (`vimarsh-backend-app`) - Monitoring
- App Service Plan (`EastUSLinuxDynamicPlan`) - Consumption hosting

**Benefits:**
- **Unified Management:** All resources in single resource group for simplified administration
- **Cost Optimization:** Serverless and consumption-based pricing across all components
- **Easy Monitoring:** Centralized resource management and cost tracking
- **Simplified Deployment:** Single deployment target with consistent resource naming
- **Idempotent:** Static resource names prevent duplicate resources during CI/CD

## Prerequisites

### Development Tools
- **Azure CLI:** Latest version ([Install Guide](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli))
- **Node.js:** 18.x or higher
- **Python:** 3.12 or higher
- **Git:** For version control
- **VS Code:** Recommended with Azure extensions

### Azure Subscription
- Active Azure subscription with permissions to create resources
- Subscription should have sufficient quota for:
  - Azure Functions (Consumption plan)
  - Cosmos DB (Standard tier)
  - Static Web Apps (Free/Standard tier)
  - Application Insights (Basic tier)

### API Keys
- **Google Gemini Pro API Key:** [Get from Google AI Studio](https://makersuite.google.com/app/apikey)
- **Azure OpenAI** (optional): For fallback LLM scenarios

---

## 🚀 Deployment Steps

### Quick Deployment (Automated)

### 1. Clone and Setup

```bash
# Clone repository
git clone https://github.com/vedprakash-m/vimarsh.git
cd vimarsh

# Login to Azure
az login

# Set subscription (if multiple)
az account set --subscription "Your Subscription Name"

# Run automated deployment (single environment production strategy)
./scripts/deploy.sh
```

### 2. Configure Environment

```bash
# Set required environment variables
export GEMINI_API_KEY="your-gemini-api-key"
export AZURE_SUBSCRIPTION_ID="your-subscription-id"

# Run deployment with unified resource group strategy
./scripts/deploy.sh dev
```

### 3. Deployment Output

The deployment will create one unified resource group:

```bash
# All resources in unified group (serverless cost optimization)
vimarsh-rg:
  ├── vimarsh-db (Cosmos DB - Serverless)
  ├── vimarsh-kv-* (Key Vault - Standard)
  ├── vimarshstorage (Storage Account - Standard LRS)
  ├── vimarsh-backend-app (Function App - Consumption)
  ├── vimarsh-frontend (Static Web App - Free)
  ├── vimarsh-backend-app (Application Insights - Basic)
  └── EastUSLinuxDynamicPlan (App Service Plan - Consumption)

# Compute resources (can be paused to save cost)
vimarsh-rg:
  └── vimarsh-functions (Function App)
  └── vimarsh-web (Static Web App)
  └── vimarsh-insights (Application Insights)
```

### 4. Cost Management Commands

```bash
# Pause application (delete compute resources, keep data)
az group delete --name vimarsh-rg --yes --no-wait

# Resume application (redeploy compute resources)
./scripts/deploy.sh dev

# Check costs
az consumption usage list --billing-period-name current
```

---

## Manual Deployment (Step by Step)

### Phase 1: Unified Resource Group Setup

#### 1.1 Create Unified Resource Group

```bash
# Create unified resource group (All Vimarsh resources)
az group create \
  --name vimarsh-rg \
  --location "West US 2" \
  --tags project=vimarsh costStrategy=unified environment=production
```

#### 1.2 Deploy All Resources with Unified Template

```bash
# Deploy using unified Bicep template
az deployment sub create \
  --location "West US 2" \
  --template-file infrastructure/main.bicep \
  --parameters geminiApiKey="YOUR_API_KEY" expertReviewEmail="your-email@example.com"
```

This creates all Vimarsh resources in the unified vimarsh-rg:
- **vimarsh-db:** Cosmos DB with vector search (serverless)
- **vimarsh-kv-*:** Key Vault for secrets management  
- **vimarshstorage:** Storage account for Functions and content
- **vimarsh-backend-app:** Function App for API (consumption plan)
- **vimarsh-frontend:** Static Web App for frontend (free tier)
- **vimarsh-backend-app:** Application Insights for monitoring
- **EastUSLinuxDynamicPlan:** Linux consumption hosting plan

### Phase 2: Verify Deployment

#### 2.1 Check Resource Creation

```bash
# Verify all resources are deployed in unified resource group
az resource list --resource-group vimarsh-rg --output table

# Check Function App status
az functionapp show --name vimarsh-backend-app --resource-group vimarsh-rg --query state

# Verify Static Web App
az staticwebapp show --name vimarsh-frontend --resource-group vimarsh-rg --query status
```

#### 2.2 Test API Endpoints

```bash
# Get Function App URL
FUNCTION_URL=$(az functionapp show --name vimarsh-backend-app --resource-group vimarsh-rg --query defaultHostName -o tsv)

# Test health endpoint
curl "https://$FUNCTION_URL/api/health"

# Get Static Web App URL
STATIC_URL=$(az staticwebapp show --name vimarsh-frontend --resource-group vimarsh-rg --query defaultHostname -o tsv)
echo "Frontend URL: https://$STATIC_URL"
```

## Production Deployment

### Prerequisites for Production

- Separate Azure subscription or resource group for production
- Production-grade API keys
- Custom domain certificates (optional)
- Production monitoring setup

### 1. Create Production Resources

#### 1.1 Create Cosmos DB Account

```bash
# Create Cosmos DB account for production
az cosmosdb create \
  --name vimarsh-cosmos-prod \
  --resource-group vimarsh-prod \
  --location eastus \
  --kind GlobalDocumentDB \
  --capabilities EnableServerless EnableVectorSearch

# Create database

#### 1.3 Create Storage Account

```bash
# Create storage account for function app
az storage account create \
  --name vimarshistorageprod \
  --resource-group vimarsh-prod \
  --location eastus \
  --sku Standard_LRS \
  --kind StorageV2
```

#### 1.4 Create Application Insights

```bash
# Create Application Insights
az monitor app-insights component create \
  --app vimarsh-insights-prod \
  --location eastus \
  --resource-group vimarsh-prod \
  --kind web \
  --application-type web
```

### Phase 2: Backend Deployment

#### 2.1 Create Function App

```bash
# Create Function App
az functionapp create \
  --name vimarsh-functions-prod \
  --resource-group vimarsh-prod \
  --storage-account vimarshistorageprod \
  --consumption-plan-location eastus \
  --runtime python \
  --runtime-version 3.12 \
  --functions-version 4 \
  --app-insights vimarsh-insights-prod \
  --disable-app-insights false
```

#### 2.2 Configure Function App Settings

```bash
# Get Cosmos DB connection string
COSMOS_CONNECTION_STRING=$(az cosmosdb keys list \
  --name vimarsh-cosmos-prod \
  --resource-group vimarsh-prod \
  --type connection-strings \
  --query 'connectionStrings[0].connectionString' \
  --output tsv)

# Get Application Insights key
APPINSIGHTS_KEY=$(az monitor app-insights component show \
  --app vimarsh-insights-prod \
  --resource-group vimarsh-prod \
  --query 'instrumentationKey' \
  --output tsv)

# Configure app settings
az functionapp config appsettings set \
  --name vimarsh-functions-prod \
  --resource-group vimarsh-prod \
  --settings \
    "GEMINI_API_KEY=$GEMINI_API_KEY" \
    "COSMOS_CONNECTION_STRING=$COSMOS_CONNECTION_STRING" \
    "APPINSIGHTS_INSTRUMENTATIONKEY=$APPINSIGHTS_KEY" \
    "FUNCTIONS_WORKER_RUNTIME=python" \
    "ENVIRONMENT=production" \
    "LOG_LEVEL=INFO"
```

#### 2.3 Deploy Backend Code

```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Create deployment package
func azure functionapp publish vimarsh-functions-prod

# Test deployment
curl https://vimarsh-functions-prod.azurewebsites.net/api/health
```

### Phase 3: Frontend Deployment

#### 3.1 Create Static Web App

```bash
# Return to project root
cd ..

# Create Static Web App
az staticwebapp create \
  --name vimarsh-web-prod \
  --resource-group vimarsh-prod \
  --source https://github.com/vedprakash-m/vimarsh \
  --branch main \
  --app-location "/frontend" \
  --build-location "/frontend/build" \
  --login-with-github
```

#### 3.2 Configure Frontend Environment

```bash
# Get function app URL
FUNCTION_APP_URL=$(az functionapp show \
  --name vimarsh-functions-prod \
  --resource-group vimarsh-prod \
  --query 'defaultHostName' \
  --output tsv)

# Configure Static Web App settings
az staticwebapp appsettings set \
  --name vimarsh-web-prod \
  --resource-group vimarsh-prod \
  --setting-names \
    REACT_APP_API_BASE_URL="https://$FUNCTION_APP_URL/api" \
    REACT_APP_ENVIRONMENT="production" \
    REACT_APP_APP_INSIGHTS_CONNECTION_STRING="$APPINSIGHTS_CONNECTION_STRING"
```

### Phase 4: Data Migration

#### 4.1 Load Sacred Texts

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
source venv/bin/activate

# Run data processing script
python data_processing/build_vector_storage.py \
  --source-dir ../data/sources \
  --output cosmos \
  --connection-string "$COSMOS_CONNECTION_STRING"
```

#### 4.2 Verify Data Loading

```bash
# Test document retrieval
curl -X POST https://vimarsh-functions-prod.azurewebsites.net/api/spiritual_guidance \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $(az functionapp keys list --name vimarsh-functions-prod --resource-group vimarsh-prod --query 'functionKeys.default' --output tsv)" \
  -d '{
    "query": "What is dharma?",
    "language": "English",
    "include_citations": true
  }'
```

### Phase 5: Security & Authentication

#### 5.1 Configure Microsoft Entra External ID

```bash
# Create app registration
az ad app create \
  --display-name "Vimarsh Spiritual Guidance" \
  --web-redirect-uris "https://vimarsh-web-prod.azurestaticapps.net/auth/callback" \
  --identifier-uris "api://vimarsh-spiritual-guidance"

# Get app ID
APP_ID=$(az ad app list --display-name "Vimarsh Spiritual Guidance" --query '[0].appId' --output tsv)

# Update Static Web App with auth settings
az staticwebapp appsettings set \
  --name vimarsh-web-prod \
  --resource-group vimarsh-prod \
  --setting-names \
    REACT_APP_MSAL_CLIENT_ID="$APP_ID" \
    REACT_APP_MSAL_AUTHORITY="https://login.microsoftonline.com/common"
```

#### 5.2 Configure Function App Security

```bash
# Enable managed identity
az functionapp identity assign \
  --name vimarsh-functions-prod \
  --resource-group vimarsh-prod

# Configure authentication
az functionapp auth update \
  --name vimarsh-functions-prod \
  --resource-group vimarsh-prod \
  --enabled true \
  --action LoginWithAzureActiveDirectory \
  --aad-client-id "$APP_ID"
```

---

## Environment Configuration

### Production Environment Variables

**Backend (Function App):**
```json
{
  "GEMINI_API_KEY": "your-gemini-api-key",
  "COSMOS_CONNECTION_STRING": "cosmos-db-connection-string",
  "APPINSIGHTS_INSTRUMENTATIONKEY": "app-insights-key",
  "FUNCTIONS_WORKER_RUNTIME": "python",
  "ENVIRONMENT": "production",
  "LOG_LEVEL": "INFO",
  "EXPERT_REVIEW_EMAIL": "experts@yourdomain.com",
  "MAX_QUERY_LENGTH": "1000",
  "RESPONSE_TIMEOUT_SECONDS": "30"
}
```

**Frontend (Static Web App):**
```json
{
  "REACT_APP_API_BASE_URL": "https://vimarsh-functions-prod.azurewebsites.net/api",
  "REACT_APP_ENVIRONMENT": "production",
  "REACT_APP_MSAL_CLIENT_ID": "your-azure-ad-app-id",
  "REACT_APP_MSAL_AUTHORITY": "https://login.microsoftonline.com/common",
  "REACT_APP_APP_INSIGHTS_CONNECTION_STRING": "app-insights-connection-string"
}
```

---

## CI/CD Pipeline Setup

### GitHub Actions Deployment

The repository includes pre-configured GitHub Actions workflows:

1. **Test Workflow** (`.github/workflows/test.yml`):
   - Runs on every push and pull request
   - Backend unit tests and integration tests
   - Frontend component tests and E2E tests
   - Security scanning and quality checks

2. **Deploy Workflow** (`.github/workflows/deploy.yml`):
   - Manual trigger with environment selection
   - Automated staging deployment
   - Manual production promotion
   - Post-deployment validation

### Setting Up GitHub Secrets

```bash
# Add required secrets to GitHub repository
gh secret set AZURE_SUBSCRIPTION_ID --body "$AZURE_SUBSCRIPTION_ID"
gh secret set AZURE_CREDENTIALS --body "$(az ad sp create-for-rbac --sdk-auth)"
gh secret set GEMINI_API_KEY --body "$GEMINI_API_KEY"
gh secret set COSMOS_CONNECTION_STRING --body "$COSMOS_CONNECTION_STRING"
```

### Manual Deployment Trigger

1. Go to **Actions** tab in GitHub repository
2. Select **Deploy** workflow
3. Click **Run workflow**
4. Choose environment (staging/production)
5. Monitor deployment progress

---

## Monitoring & Observability

### Application Insights Configuration

**Custom Metrics:**
- Spiritual guidance request volume
- Response quality scores
- Citation accuracy metrics
- Voice interaction success rates
- Expert review feedback scores

**Alerts:**
```bash
# Create availability test
az monitor app-insights web-test create \
  --resource-group vimarsh-prod \
  --app-insights vimarsh-insights-prod \
  --name "Vimarsh Health Check" \
  --location eastus \
  --test-locations "us-east-azure" \
  --url "https://vimarsh-functions-prod.azurewebsites.net/api/health" \
  --frequency 300 \
  --timeout 30

# Create alert rule for high error rate
az monitor metrics alert create \
  --name "High Error Rate" \
  --resource-group vimarsh-prod \
  --scopes "/subscriptions/$AZURE_SUBSCRIPTION_ID/resourceGroups/vimarsh-prod/providers/Microsoft.Web/sites/vimarsh-functions-prod" \
  --condition "avg exceptions/server > 5" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --severity 2 \
  --description "Alert when error rate exceeds 5 per minute"
```

### Cost Monitoring

```bash
# Create budget alert
az consumption budget create \
  --resource-group vimarsh-prod \
  --budget-name "vimarsh-monthly-budget" \
  --amount 100 \
  --category Cost \
  --time-grain Monthly \
  --start-date "2025-06-01" \
  --end-date "2026-06-01"
```

---

## Backup & Disaster Recovery

### Automated Backups

**Cosmos DB:**
- Continuous backup enabled by default
- Point-in-time recovery up to 7 days
- Cross-region replication for critical data

**Function App:**
- Source code in Git repository
- Configuration backed up in Key Vault
- Deployment packages stored in Azure Storage

**Static Web App:**
- Source code in Git repository
- CDN cache automatically managed
- Global distribution for high availability

### Recovery Procedures

**Complete Environment Recovery:**
```bash
# 1. Deploy infrastructure
./scripts/deploy.sh prod --recovery-mode

# 2. Restore Cosmos DB to specific timestamp
az cosmosdb sql database restore \
  --account-name vimarsh-cosmos-prod \
  --database-name SpiritualGuidance \
  --restore-timestamp "2025-06-23T10:00:00Z"

# 3. Redeploy applications
func azure functionapp publish vimarsh-functions-prod
az staticwebapp deploy --name vimarsh-web-prod
```

---

## Performance Optimization

### Backend Optimization

**Function App Configuration:**
```bash
# Configure premium plan for better performance
az functionapp plan create \
  --name vimarsh-premium-plan \
  --resource-group vimarsh-prod \
  --location eastus \
  --sku P1V2

# Update function app to use premium plan
az functionapp update \
  --name vimarsh-functions-prod \
  --resource-group vimarsh-prod \
  --plan vimarsh-premium-plan
```

**Cosmos DB Optimization:**
```bash
# Enable autoscale
az cosmosdb sql container throughput update \
  --account-name vimarsh-cosmos-prod \
  --resource-group vimarsh-prod \
  --database-name SpiritualGuidance \
  --name Documents \
  --max-throughput 4000
```

### Frontend Optimization

**CDN Configuration:**
- Static assets served from Azure CDN
- Global edge locations for optimal latency
- Automatic compression and caching

**Performance Monitoring:**
- Core Web Vitals tracking
- Real User Monitoring (RUM)
- Synthetic transaction monitoring

---

## Security Hardening

### Network Security

```bash
# Configure function app to use virtual network
az functionapp vnet-integration add \
  --name vimarsh-functions-prod \
  --resource-group vimarsh-prod \
  --vnet vimarsh-vnet \
  --subnet function-subnet

# Enable private endpoints for Cosmos DB
az cosmosdb private-endpoint-connection create \
  --account-name vimarsh-cosmos-prod \
  --resource-group vimarsh-prod \
  --name cosmos-private-endpoint \
  --private-connection-resource-id "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/vimarsh-prod/providers/Microsoft.DocumentDB/databaseAccounts/vimarsh-cosmos-prod" \
  --group-id Sql
```

### API Security

```bash
# Configure API Management (optional)
az apim create \
  --name vimarsh-apim-prod \
  --resource-group vimarsh-prod \
  --location eastus \
  --publisher-name "Vimarsh Team" \
  --publisher-email "vedprakash.m@me.com" \
  --sku-name Developer
```

---

## Troubleshooting

### Common Issues

**1. Function App Deployment Fails**
```bash
# Check deployment logs
az functionapp log tail --name vimarsh-functions-prod --resource-group vimarsh-prod

# Verify dependencies
cd backend && pip install -r requirements.txt
func azure functionapp publish vimarsh-functions-prod --build remote
```

**2. Cosmos DB Connection Issues**
```bash
# Test connection
az cosmosdb keys list --name vimarsh-cosmos-prod --resource-group vimarsh-prod
az cosmosdb check-name-exists --name vimarsh-cosmos-prod
```

**3. Static Web App Build Failures**
```bash
# Check build logs in GitHub Actions
# Verify Node.js version compatibility
cd frontend && npm install && npm run build
```

### Diagnostic Commands

```bash
# Check all resources status
az resource list --resource-group vimarsh-prod --output table

# Monitor function app metrics
az monitor metrics list \
  --resource "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/vimarsh-prod/providers/Microsoft.Web/sites/vimarsh-functions-prod" \
  --metric "Requests" \
  --interval PT1M

# Check Cosmos DB health
az cosmosdb show --name vimarsh-cosmos-prod --resource-group vimarsh-prod --query 'readLocations[0].provisioningState'
```

---

## Scaling Considerations

### Horizontal Scaling

**Function App:**
- Consumption plan automatically scales
- Premium plan for guaranteed warm instances
- Event-driven scaling based on request volume

**Cosmos DB:**
- Autoscale based on RU consumption
- Partition key optimization for even distribution
- Read replicas for global distribution

### Vertical Scaling

**Performance Tiers:**
- **Development:** Consumption plan, serverless Cosmos DB
- **Production:** Premium plan, provisioned throughput
- **Enterprise:** Dedicated plan, multi-region setup

---

## Cost Optimization

### Current Estimates (Monthly)

| Component | Development | Production | Enterprise |
|-----------|-------------|------------|------------|
| Function App | $0-5 | $50-100 | $200-500 |
| Cosmos DB | $5-10 | $50-200 | $500-1000 |
| Static Web App | Free | $9 | $250 |
| App Insights | Free | $10-50 | $100-500 |
| **Total** | **$5-15** | **$119-359** | **$1,050-2,250** |

### Cost Optimization Tips

```bash
# Monitor costs
az consumption usage list --start-date 2025-06-01 --end-date 2025-06-30

# Set up budget alerts
az consumption budget create \
  --resource-group vimarsh-prod \
  --budget-name monthly-budget \
  --amount 200 \
  --time-grain Monthly
```

---

## ✅ Validation

### Post-Deployment Validation

After deployment, verify all systems are working correctly:

#### 1. Health Check Validation

```bash
# Test API health endpoint
curl -X GET https://vimarsh-functions-prod.azurewebsites.net/api/health

# Expected response:
# {
#   "status": "healthy",
#   "service": "vimarsh-spiritual-guidance",
#   "version": "1.0.0",
#   "timestamp": "2025-06-24T10:30:00Z"
# }
```

#### 2. Spiritual Guidance Validation

```bash
# Test spiritual guidance endpoint
curl -X POST https://vimarsh-functions-prod.azurewebsites.net/api/spiritual-guidance \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_FUNCTION_KEY" \
  -d '{
    "query": "What is the purpose of life according to dharma?",
    "language": "English",
    "include_citations": true
  }'
```

#### 3. Database Connectivity Validation

```bash
# Check Cosmos DB connection
az cosmosdb collection show \
  --collection-name spiritual-texts \
  --db-name vimarsh \
  --resource-group vimarsh-prod \
  --name vimarsh-cosmos-prod
```

#### 4. Frontend Validation

- **Static Web App**: Verify frontend loads at deployment URL
- **Authentication**: Test login flow (if enabled)
- **Voice Interface**: Test speech recognition and synthesis
- **Responsive Design**: Check mobile, tablet, and desktop layouts

#### 5. Monitoring Validation

```bash
# Check Application Insights
az monitor app-insights component show \
  --app vimarsh-insights-prod \
  --resource-group vimarsh-prod

# View recent logs
az monitor app-insights query \
  --app vimarsh-insights-prod \
  --analytics-query "requests | limit 10"
```

#### 6. Performance Validation

- **Response Times**: < 1 second for spiritual guidance queries
- **Concurrent Users**: Support 100+ simultaneous users
- **Error Rates**: < 1% error rate under normal load
- **Availability**: 99.9% uptime target

---

## Support & Maintenance

### Maintenance Schedule

**Weekly:**
- Monitor Application Insights dashboards
- Review error logs and performance metrics
- Update dependencies if needed

**Monthly:**
- Review cost reports and optimize resources
- Check for Azure service updates
- Update sacred text content if needed

**Quarterly:**
- Security review and penetration testing
- Disaster recovery testing
- Performance optimization review

### Support Channels

- **Technical Issues:** GitHub Issues
- **Urgent Problems:** [vedprakash.m@me.com](mailto:vedprakash.m@me.com)
- **Feature Requests:** GitHub Discussions
- **Security Issues:** Private email to security team

---

**Next Steps:**
1. [API Documentation](../api/) - Integrate with the API
2. [Frontend Documentation](../../frontend/) - Customize the user interface
3. [Expert Review Setup](../experts/) - Configure spiritual content validation

*"योगः कर्मसु कौशलम्" - Yoga is skill in action*

**Deployment completed with divine blessings!** 🕉️
