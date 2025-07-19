# Vimarsh Deployment Context

**Status**: ✅ Production Live | **Date**: July 11, 2025 | **RG**: `vimarsh-compute-rg`

## 🚀 Live Resources

| Component | Resource | URL |
|-----------|----------|-----|
| Frontend | `vimarsh-frontend` (Azure Static Web App) | `https://vimarsh.vedprakash.net` |
| Backend | `vimarsh-backend-app` (Function App, Python 3.12) | `https://vimarsh-backend-app.azurewebsites.net` |

## 📦 Quick Deploy Commands

**Frontend**:
```bash
cd frontend && npm run build && swa deploy build --env production --resource-group vimarsh-compute-rg --app-name vimarsh-frontend
```

**Backend**:
```bash
cd backend && func azure functionapp publish vimarsh-backend-app
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
- **Backend**: Python 3.12, Linux Consumption, 1.5GB, Oryx remote build
- **Frontend**: React 18 + TypeScript, code splitting, Azure CDN, custom domain
- **Auth**: Microsoft Entra ID (`/common` endpoint), app registration: `vimarsh`
- **Admin**: `vedprakash.m@outlook.com` (super admin), personal accounts supported
- **CORS**: Frontend domain configured
- **Monitoring**: Application Insights ready

## 🏗️ Resource Groups

### vimarsh-compute-rg (Active Resources)
| Resource | Type | Status | Purpose |
|----------|------|--------|---------|
| `vimarsh-frontend` | Static Web App | ✅ Live | React 18 frontend |
| `vimarsh-backend-app` | Function App | ✅ Live | Python 3.12 API |
| `vimarsh-compute-plan` | App Service Plan | ✅ Active | Linux Consumption |
| `vimarsh-storage-compute` | Storage Account | ✅ Active | Function app storage |
| `vimarsh-insights-compute` | Application Insights | ✅ Active | Monitoring & logging |

### vimarsh-persistent-rg (Data & Shared Resources)
| Resource | Type | Status | Purpose |
|----------|------|--------|---------|
| `vimarsh-cosmos-db` | Cosmos DB Account | ✅ Active | Vector & document storage |
| `vimarsh-keyvault` | Key Vault | ✅ Active | Secrets & configuration |
| `vimarsh-storage-persistent` | Storage Account | ✅ Active | Data & file storage |
| `vimarsh-log-analytics` | Log Analytics Workspace | ✅ Active | Centralized logging |
| `vimarsh-insights-shared` | Application Insights | ✅ Active | Cross-service monitoring |
