# Vimarsh Deployment Context

**S- **Backend**: Python 3.12, Linux Flex Consumption (West US 2), 1.5GB, Oryx remote buildatus**: ✅ Production Live | **Date**: July 11, 2025 | **RG**: `vimarsh-rg`

## 🚀 Live Resources

| Component | Resource | URL |
|-----------|----------|-----|
| Frontend | `vimarsh-frontend-westus2` (Azure Static Web App, West US 2) | `https://vimarsh.vedprakash.net` |
| Backend | `vimarsh-backend-app-flex` (Function App, Python 3.12, Flex Consumption) | `https://vimarsh-backend-app-flex-accch9cmbah2bzb0.westus2-01.azurewebsites.net` |

## 📦 Quick Deploy Commands

**Frontend**:
```bash
cd frontend && npm run build && swa deploy build --env production --resource-group vimarsh-rg --app-name vimarsh-frontend-westus2
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

## 🏗️ Resource Groups

### vimarsh-rg (Unified Resources)
| Resource | Type | Status | Purpose |
|----------|------|--------|---------|
| `vimarsh-frontend-westus2` | Static Web App | ✅ Live | React 18 frontend (West US 2) |
| `vimarsh-backend-app-flex` | Function App | ✅ Live | Python 3.12 API (Flex Consumption) |
| `vimarsh-db` | Cosmos DB Account | ✅ Active | Vector & document storage (serverless) |
| `vimarsh-kv-*` | Key Vault | ✅ Active | Secrets & configuration |
| `vimarshstorage` | Storage Account | ✅ Active | Function app & data storage |
| `ASP-vimarshrg-84c5` | Flex Consumption Plan | ✅ Active | Serverless hosting (West US 2) |
| `vimarsh-backend-app-flex` | Application Insights | ✅ Active | Monitoring & logging |
