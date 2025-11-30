# Vimarsh Deployment Context

**S- **Backend**: Python 3.12, Linux Flex Consumption (West US 2), 1.5GB, Oryx remote buildatus**: ✅ Production Live | **Date**: July 11, 2025 | **RG**: `vimarsh-rg`

## 🚀 Live Resources

| Component | Resource | URL |
|-----------|----------|-----|
| Frontend | `vimarsh-frontend` (Azure Static Web App) | `https://vimarsh.vedprakash.net` |
| Backend | `vimarsh-backend-app-flex` (Function App, Python 3.12, Flex Consumption) | `https://vimarsh-backend-app-flex-accch9cmbah2bzb0.westus2-01.azurewebsites.net` |

## 📦 Quick Deploy Commands

**Frontend**:
```bash
cd frontend && npm run build && swa deploy build --env production --resource-group vimarsh-rg --app-name vimarsh-frontend
```

**Backend**:
```bash
cd backend && func azure functionapp publish vimarsh-backend-app-flex --python
```

## 🔍 Health Endpoints
- Main: `GET /api/health`
- Detailed: `GET /api/health/detailed`
- Admin: `GET /api/vimarsh-admin/health`
- Spiritual: `POST /api/spiritual_guidance`

## ⚙️ Key Functions (27 total)
**Core**: `spiritual_guidance`, `health_check`, `supported_languages`, `user_budget_status`
**Admin**: `admin_*` (alerts, budget, cost, user management, system health)
**Feedback**: `collect_feedback`, `feedback_analytics`, `export_feedback_report`

## 🔧 Runtime Config
- **Backend**: Python 3.12, Linux Flex Consumption (West US 2), 1.5GB, Oryx remote build
- **Frontend**: React 18 + TypeScript, code splitting, Azure CDN, custom domain (West US 2)
- **Auth**: Microsoft Entra ID (`/common` endpoint), app registration: `vimarsh`
- **Admin**: `vedprakash.m@outlook.com` (super admin), personal accounts supported
- **CORS**: Frontend domain configured
- **Monitoring**: Application Insights ready

## 🔑 Environment Variables

### Required Backend Environment Variables

Set these in **Azure Portal > Function App > Configuration > Application Settings**:

| Variable | Description | Where to Get |
|----------|-------------|--------------|
| `GEMINI_API_KEY` | Google Gemini API key for LLM | [Google AI Studio](https://aistudio.google.com/) |
| `AZURE_COSMOS_CONNECTION_STRING` | Cosmos DB connection string | Azure Portal > Cosmos DB > Keys |
| `AZURE_COSMOS_DATABASE_NAME` | Database name (default: `vimarsh-multi-personality`) | Your Cosmos DB setup |
| `AZURE_SPEECH_KEY` | Azure Speech Service subscription key | Azure Portal > Speech Service > Keys |
| `AZURE_SPEECH_REGION` | Azure Speech Service region (default: `eastus`) | Your Speech Service location |

### Local Development Setup

Create a `.env` file in the backend directory (already in `.gitignore`):

```bash
# backend/.env
GEMINI_API_KEY=your-gemini-api-key
AZURE_COSMOS_CONNECTION_STRING=your-cosmos-connection-string
AZURE_COSMOS_DATABASE_NAME=vimarsh-multi-personality
AZURE_SPEECH_KEY=your-speech-key
AZURE_SPEECH_REGION=eastus
```

Or set them in `local.settings.json` (also in `.gitignore`):

```json
{
  "IsEncrypted": false,
  "Values": {
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "GEMINI_API_KEY": "your-gemini-api-key",
    "AZURE_COSMOS_CONNECTION_STRING": "your-cosmos-connection-string",
    "AZURE_SPEECH_KEY": "your-speech-key",
    "AZURE_SPEECH_REGION": "eastus"
  }
}
```

### Azure Portal Configuration

To set environment variables in Azure Portal:

1. Go to **Azure Portal** → **Function App** → `vimarsh-backend-app-flex`
2. Navigate to **Settings** → **Environment variables** (or Configuration → Application settings)
3. Click **+ Add** for each variable
4. Save and restart the Function App

### Creating Azure Speech Service

1. Go to **Azure Portal** → **Create a resource** → **Speech**
2. Select subscription and resource group (`vimarsh-rg`)
3. Choose region: `East US` (or your preferred region)
4. Pricing tier: `Free F0` (500K chars/month) or `Standard S0` ($15/1M chars)
5. Click **Create**
6. After creation, go to **Keys and Endpoint**
7. Copy **Key 1** → Use as `AZURE_SPEECH_KEY`
8. Copy **Location/Region** → Use as `AZURE_SPEECH_REGION`

## 🏗️ Resource Groups

### vimarsh-rg (Unified Resources)
| Resource | Type | Status | Purpose |
|----------|------|--------|---------|
| `vimarsh-frontend` | Static Web App | ✅ Live | React 18 frontend |
| `vimarsh-backend-app-flex` | Function App | ✅ Live | Python 3.12 API (Flex Consumption) |
| `vimarsh-db` | Cosmos DB Account | ✅ Active | Vector & document storage (serverless) |
| `vimarsh-kv-*` | Key Vault | ✅ Active | Secrets & configuration |
| `vimarshstorage` | Storage Account | ✅ Active | Function app & data storage |
| `ASP-vimarshrg-84c5` | Flex Consumption Plan | ✅ Active | Serverless hosting (West US 2) |
| `vimarsh-backend-app-flex` | Application Insights | ✅ Active | Monitoring & logging |
