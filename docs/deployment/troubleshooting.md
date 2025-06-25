# 🔧 Vimarsh Deployment Troubleshooting Guide

Common issues and solutions for deploying Vimarsh AI Spiritual Guidance System.

## Quick Diagnostics

### 1. Check Overall Health

```bash
# Verify all resources exist
az resource list --resource-group vimarsh-prod --output table

# Check Function App status
az functionapp show --name vimarsh-functions-prod --resource-group vimarsh-prod --query "state"

# Test API endpoints
curl -s https://vimarsh-functions-prod.azurewebsites.net/api/health | jq .
```

### 2. Common Deployment Commands

```bash
# Get deployment logs
az functionapp log tail --name vimarsh-functions-prod --resource-group vimarsh-prod

# Restart Function App
az functionapp restart --name vimarsh-functions-prod --resource-group vimarsh-prod

# Check app settings
az functionapp config appsettings list --name vimarsh-functions-prod --resource-group vimarsh-prod
```

---

## Issue Categories

### 🚫 Infrastructure Issues

#### **Issue:** Resource creation fails
```
Error: The subscription is not registered to use namespace 'Microsoft.DocumentDB'
```

**Solution:**
```bash
# Register required resource providers
az provider register --namespace Microsoft.DocumentDB
az provider register --namespace Microsoft.Web
az provider register --namespace Microsoft.Storage
az provider register --namespace Microsoft.Insights

# Check registration status
az provider show --namespace Microsoft.DocumentDB --query "registrationState"
```

#### **Issue:** Cosmos DB vector search not available
```
Error: The capability 'EnableVectorSearch' is not supported in this region
```

**Solution:**
```bash
# Check available regions for vector search
az cosmosdb locations list --query "[?contains(capabilities, 'EnableVectorSearch')].{name:name, region:documentEndpoint}"

# Use supported region
az group create --name vimarsh-prod --location "East US 2"
```

#### **Issue:** Storage account name conflicts
```
Error: The storage account name 'vimarshistorageprod' is already taken
```

**Solution:**
```bash
# Generate unique storage account name
UNIQUE_SUFFIX=$(date +%s | tail -c 5)
STORAGE_NAME="vimarshstorage${UNIQUE_SUFFIX}"

# Update deployment script
sed -i "s/vimarshistorageprod/$STORAGE_NAME/g" scripts/deploy.sh
```

### 🐍 Backend Issues

#### **Issue:** Function App deployment fails
```
Error: The process cannot access the file because it is being used by another process
```

**Solution:**
```bash
# Stop Function App before deployment
az functionapp stop --name vimarsh-functions-prod --resource-group vimarsh-prod

# Deploy with build flag
cd backend
func azure functionapp publish vimarsh-functions-prod --build remote

# Start Function App
az functionapp start --name vimarsh-functions-prod --resource-group vimarsh-prod
```

#### **Issue:** Python dependencies not installing
```
Error: Could not find a version that satisfies the requirement azure-functions
```

**Solution:**
```bash
# Clean virtual environment
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install --upgrade setuptools wheel
pip install -r requirements.txt

# If specific packages fail, install individually
pip install azure-functions azure-cosmos openai
```

#### **Issue:** Function app cold start issues
```
Error: Timeout waiting for response
```

**Solution:**
```bash
# Switch to Premium plan for production
az functionapp plan create \
  --name vimarsh-premium-plan \
  --resource-group vimarsh-prod \
  --location eastus \
  --sku P1V2

az functionapp update \
  --name vimarsh-functions-prod \
  --resource-group vimarsh-prod \
  --plan vimarsh-premium-plan

# Configure always-on
az functionapp config set \
  --name vimarsh-functions-prod \
  --resource-group vimarsh-prod \
  --always-on true
```

#### **Issue:** Gemini API authentication fails
```
Error: Invalid API key provided
```

**Solution:**
```bash
# Verify API key format
echo $GEMINI_API_KEY | grep -E '^AIza[0-9A-Za-z_-]{35}$'

# Test API key directly
curl -H "Authorization: Bearer $GEMINI_API_KEY" \
  "https://generativelanguage.googleapis.com/v1/models" 

# Update app settings
az functionapp config appsettings set \
  --name vimarsh-functions-prod \
  --resource-group vimarsh-prod \
  --settings "GEMINI_API_KEY=$GEMINI_API_KEY"
```

### 🌐 Frontend Issues

#### **Issue:** Static Web App build fails
```
Error: npm ERR! code ENOTFOUND
```

**Solution:**
```bash
# Check Node.js version compatibility
cd frontend
node --version  # Should be 18.x or higher

# Clear npm cache and reinstall
npm cache clean --force
rm -rf node_modules package-lock.json
npm install

# Test local build
npm run build
```

#### **Issue:** API calls fail from frontend
```
Error: CORS policy: No 'Access-Control-Allow-Origin' header
```

**Solution:**
```bash
# Update Function App CORS settings
az functionapp cors add \
  --name vimarsh-functions-prod \
  --resource-group vimarsh-prod \
  --allowed-origins "https://vimarsh-web-prod.azurestaticapps.net"

# Or allow all origins for development
az functionapp cors add \
  --name vimarsh-functions-prod \
  --resource-group vimarsh-prod \
  --allowed-origins "*"
```

#### **Issue:** Environment variables not loading
```
Error: process.env.REACT_APP_API_BASE_URL is undefined
```

**Solution:**
```bash
# Verify Static Web App settings
az staticwebapp appsettings list \
  --name vimarsh-web-prod \
  --resource-group vimarsh-prod

# Update settings
FUNCTION_URL=$(az functionapp show \
  --name vimarsh-functions-prod \
  --resource-group vimarsh-prod \
  --query defaultHostName -o tsv)

az staticwebapp appsettings set \
  --name vimarsh-web-prod \
  --resource-group vimarsh-prod \
  --setting-names REACT_APP_API_BASE_URL="https://$FUNCTION_URL/api"
```

### 🗄️ Database Issues

#### **Issue:** Cosmos DB connection fails
```
Error: Unable to connect to Cosmos DB endpoint
```

**Solution:**
```bash
# Verify Cosmos DB is accessible
az cosmosdb show \
  --name vimarsh-cosmos-prod \
  --resource-group vimarsh-prod \
  --query "documentEndpoint"

# Test connection string
COSMOS_CONNECTION=$(az cosmosdb keys list \
  --name vimarsh-cosmos-prod \
  --resource-group vimarsh-prod \
  --type connection-strings \
  --query 'connectionStrings[0].connectionString' -o tsv)

echo $COSMOS_CONNECTION | grep -o 'AccountKey=[^;]*'

# Update Function App with new connection string
az functionapp config appsettings set \
  --name vimarsh-functions-prod \
  --resource-group vimarsh-prod \
  --settings "COSMOS_CONNECTION_STRING=$COSMOS_CONNECTION"
```

#### **Issue:** Vector search not working
```
Error: Vector indexing is not enabled
```

**Solution:**
```bash
# Verify vector search capability
az cosmosdb show \
  --name vimarsh-cosmos-prod \
  --resource-group vimarsh-prod \
  --query "capabilities"

# Update container with vector indexing
az cosmosdb sql container update \
  --account-name vimarsh-cosmos-prod \
  --resource-group vimarsh-prod \
  --database-name SpiritualGuidance \
  --name Documents \
  --indexing-policy '{
    "indexingMode": "consistent",
    "includedPaths": [{"path": "/*"}],
    "excludedPaths": [{"path": "/vector/*"}],
    "vectorIndexes": [{"path": "/vector", "type": "quantizedFlat"}]
  }'
```

### 🔐 Authentication Issues

#### **Issue:** Azure AD authentication fails
```
Error: AADSTS50011: The reply URL specified does not match
```

**Solution:**
```bash
# Get Static Web App URL
STATIC_URL=$(az staticwebapp show \
  --name vimarsh-web-prod \
  --resource-group vimarsh-prod \
  --query defaultHostname -o tsv)

# Update app registration
az ad app update \
  --id $APP_ID \
  --web-redirect-uris "https://$STATIC_URL/auth/callback" \
                       "https://$STATIC_URL/"

# Verify redirect URIs
az ad app show --id $APP_ID --query "web.redirectUris"
```

#### **Issue:** Function app authentication not working
```
Error: 401 Unauthorized
```

**Solution:**
```bash
# Get function keys
az functionapp keys list \
  --name vimarsh-functions-prod \
  --resource-group vimarsh-prod

# Test with function key
FUNCTION_KEY=$(az functionapp keys list \
  --name vimarsh-functions-prod \
  --resource-group vimarsh-prod \
  --query 'functionKeys.default' -o tsv)

curl -H "Authorization: Bearer $FUNCTION_KEY" \
  https://vimarsh-functions-prod.azurewebsites.net/api/spiritual_guidance
```

---

## Performance Issues

### High Latency

**Diagnosis:**
```bash
# Check Application Insights metrics
az monitor app-insights metrics show \
  --app vimarsh-insights-prod \
  --resource-group vimarsh-prod \
  --metric "requests/duration" \
  --start-time "2025-06-24T00:00:00Z"
```

**Solutions:**
1. **Upgrade to Premium Plan:** Eliminate cold starts
2. **Enable CDN:** Cache static content globally
3. **Optimize Cosmos DB:** Increase RU/s for hot partitions
4. **Connection Pooling:** Reuse database connections

### High Memory Usage

**Diagnosis:**
```bash
# Monitor memory metrics
az monitor metrics list \
  --resource "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/vimarsh-prod/providers/Microsoft.Web/sites/vimarsh-functions-prod" \
  --metric "MemoryWorkingSet"
```

**Solutions:**
1. **Optimize Vector Storage:** Use smaller embedding dimensions
2. **Implement Caching:** Cache frequently requested spiritual texts
3. **Batch Processing:** Process multiple queries together

---

## Monitoring & Debugging

### Enable Debug Logging

```bash
# Update log level
az functionapp config appsettings set \
  --name vimarsh-functions-prod \
  --resource-group vimarsh-prod \
  --settings "LOG_LEVEL=DEBUG"

# Stream logs in real-time
az functionapp log tail \
  --name vimarsh-functions-prod \
  --resource-group vimarsh-prod
```

### Application Insights Queries

**Find errors in last hour:**
```kusto
traces
| where timestamp > ago(1h) 
| where severityLevel >= 3
| order by timestamp desc
```

**Monitor API response times:**
```kusto
requests
| where timestamp > ago(24h)
| where name contains "spiritual_guidance"
| summarize avg(duration), count() by bin(timestamp, 1h)
| render timechart
```

**Track spiritual guidance quality:**
```kusto
customEvents
| where name == "SpiritualGuidanceProcessed"
| extend confidence = toreal(customDimensions.confidence_score)
| summarize avg(confidence) by bin(timestamp, 1h)
| render timechart
```

---

## Recovery Procedures

### Complete Environment Recovery

1. **Backup Current State:**
```bash
# Export resource group template
az group export \
  --name vimarsh-prod \
  --output-file backup-$(date +%Y%m%d).json
```

2. **Create New Environment:**
```bash
# Deploy to new resource group
az group create --name vimarsh-recovery --location eastus2
az deployment group create \
  --resource-group vimarsh-recovery \
  --template-file infrastructure/main.bicep \
  --parameters infrastructure/parameters/prod.parameters.json
```

3. **Restore Data:**
```bash
# Restore Cosmos DB to specific point in time
az cosmosdb sql database restore \
  --account-name vimarsh-cosmos-recovery \
  --database-name SpiritualGuidance \
  --restore-timestamp "2025-06-24T10:00:00Z"
```

### Rollback Deployment

```bash
# Get previous deployment
PREVIOUS_DEPLOYMENT=$(az functionapp deployment list \
  --name vimarsh-functions-prod \
  --resource-group vimarsh-prod \
  --query '[1].id' -o tsv)

# Rollback to previous version
az functionapp deployment source show \
  --name vimarsh-functions-prod \
  --resource-group vimarsh-prod \
  --deployment-id $PREVIOUS_DEPLOYMENT
```

---

## Getting Help

### Log Collection

```bash
# Collect all relevant logs
mkdir vimarsh-logs-$(date +%Y%m%d)
cd vimarsh-logs-$(date +%Y%m%d)

# Function App logs
az functionapp log download \
  --name vimarsh-functions-prod \
  --resource-group vimarsh-prod

# Resource status
az resource list \
  --resource-group vimarsh-prod \
  --output json > resource-status.json

# App settings (redacted)
az functionapp config appsettings list \
  --name vimarsh-functions-prod \
  --resource-group vimarsh-prod \
  --output json > app-settings.json
```

### Support Channels

1. **GitHub Issues:** [Create Issue](https://github.com/vedprakash-m/vimarsh/issues)
2. **Email Support:** [vedprakash.m@me.com](mailto:vedprakash.m@me.com)
3. **Azure Support:** For infrastructure issues

### Useful Resources

- [Azure Functions Troubleshooting](https://docs.microsoft.com/en-us/azure/azure-functions/functions-diagnostics)
- [Cosmos DB Troubleshooting](https://docs.microsoft.com/en-us/azure/cosmos-db/troubleshoot-common-issues)
- [Static Web Apps Troubleshooting](https://docs.microsoft.com/en-us/azure/static-web-apps/troubleshooting)

---

*"अभयं सत्त्वसंशुद्धिर्ज्ञानयोगव्यवस्थितिः" - Be fearless and pure, steadfast in yoga and knowledge*

**May divine guidance help resolve all technical challenges!** 🕉️
