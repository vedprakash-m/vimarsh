# Azure OpenAI Production Deployment Checklist

**Deployment Date**: TBD  
**Status**: 📋 PENDING  
**Prerequisites**: ✅ Phase 1-3 COMPLETE

---

## Pre-Deployment Verification

### ✅ Code Readiness
- [x] All backend services updated to use Azure OpenAI
- [x] All data pipelines updated with text-embedding-3-large
- [x] Test suite created and passing (96% pass rate)
- [x] Documentation complete (README.md, AZURE_OPENAI_MIGRATION.md)
- [x] Migration validated (31,422 docs, 99.99% success)

### ✅ Testing Validation
- [x] Unit tests: 24/27 passed (89%)
- [x] Integration tests: 3/3 passed (100%)
- [x] Manual quality tests: 50/50 passed (100%)
- [x] Performance tests: 2.17s avg latency (target <3s)
- [x] Cost validation: $0.19 actual vs $0.88 estimate

---

## Azure Function App Configuration

### Environment Variables to Add

Navigate to Azure Portal → Function App → Configuration → Application Settings

Add the following environment variables:

```bash
# Azure OpenAI Embedding Configuration
AZURE_OPENAI_EMBEDDING_ENDPOINT=https://vimarsh-openai.openai.azure.com/
AZURE_OPENAI_EMBEDDING_API_KEY=<retrieve-from-azure-keyvault>
AZURE_OPENAI_EMBEDDING_MODEL=text-embedding-3-large
AZURE_OPENAI_EMBEDDING_API_VERSION=2024-06-01
AZURE_OPENAI_EMBEDDING_DIMENSIONS=768

# Rate Limiting Configuration
AZURE_OPENAI_MAX_BATCH_SIZE=100
AZURE_OPENAI_RATE_LIMIT_DELAY=0.6
AZURE_OPENAI_MAX_RETRIES=5

# Optional: Key Vault Integration
AZURE_KEY_VAULT_NAME=vimarsh-kv
AZURE_KEY_VAULT_SECRET_NAME=azure-openai-embedding-key
```

### Retrieve API Key from Key Vault (Optional)

If storing API key in Azure Key Vault:

```bash
# Via Azure CLI
az keyvault secret show \
  --vault-name vimarsh-kv \
  --name azure-openai-embedding-key \
  --query value -o tsv

# Or use managed identity (recommended)
# Enable system-assigned managed identity on Function App
# Grant Key Vault access policy to managed identity
```

### Configuration Steps

1. **Open Azure Portal**
   - Navigate to vimarsh-function-app
   - Go to Configuration → Application Settings

2. **Add Environment Variables**
   - Click "+ New application setting"
   - Add each variable from the list above
   - Click "Save" after adding all variables

3. **Verify Configuration**
   - Check "Advanced edit" to verify JSON format
   - Ensure no typos in variable names
   - Confirm endpoint URL has trailing slash

4. **Restart Function App**
   - Go to Overview tab
   - Click "Restart" to apply new configuration
   - Wait for restart to complete (~30 seconds)

---

## Deployment Options

### Option 1: GitHub Actions (Recommended)

The repository has automated CI/CD via GitHub Actions:

```bash
# Trigger deployment by pushing to main branch
git add .
git commit -m "Deploy Azure OpenAI migration to production"
git push origin main

# Or trigger manual deployment
gh workflow run deploy-production.yml
```

GitHub Actions will:
- Run tests automatically
- Build backend and frontend
- Deploy to Azure Function App and Static Web Apps
- Verify deployment health

### Option 2: Azure Functions Core Tools

Manual deployment using CLI:

```bash
# Navigate to backend directory
cd backend

# Deploy to Azure Function App
func azure functionapp publish vimarsh-function-app

# Verify deployment
func azure functionapp show --name vimarsh-function-app
```

### Option 3: VS Code Extension

Using Azure Functions VS Code extension:

1. Open VS Code
2. Install "Azure Functions" extension
3. Sign in to Azure account
4. Right-click on backend folder
5. Select "Deploy to Function App..."
6. Choose vimarsh-function-app
7. Confirm deployment

---

## Post-Deployment Verification

### 1. Function App Health Check

```bash
# Check Function App status
az functionapp show \
  --name vimarsh-function-app \
  --resource-group vimarsh-rg \
  --query state

# Expected: "Running"
```

### 2. Test Embedding Generation

Test Azure OpenAI embedding endpoint:

```bash
curl -X POST https://vimarsh-function-app.azurewebsites.net/api/generate-embedding \
  -H "Content-Type: application/json" \
  -d '{"text": "Test embedding generation"}'

# Expected: 768-dimensional embedding vector
```

### 3. Test RAG Query

Test full RAG pipeline:

```bash
curl -X POST https://vimarsh-function-app.azurewebsites.net/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "personality": "krishna",
    "query": "What is dharma?",
    "user_id": "test-user-123"
  }'

# Expected: Response with citations and 2-3s latency
```

### 4. Verify Application Insights

Check Application Insights for:
- Function execution success rate (>99%)
- Average embedding latency (<1s)
- Error rates (<1%)
- Request volumes match expectations

Navigate to: Azure Portal → Application Insights → vimarsh-insights

Key metrics to monitor:
- `Requests` → Check success rate
- `Performance` → Check response times
- `Failures` → Check for errors
- `Live Metrics` → Real-time monitoring

---

## Monitoring & Alerting

### Application Insights Alerts

Configure these alerts in Azure Portal:

#### 1. Embedding API Error Rate Alert

```yaml
Alert Name: Azure OpenAI Embedding API Errors
Condition: Error rate > 5%
Window: 5 minutes
Severity: Warning
Action Group: vimarsh-alerts
```

#### 2. Embedding Latency Alert

```yaml
Alert Name: High Embedding Latency
Condition: P95 latency > 2 seconds
Window: 15 minutes
Severity: Warning
Action Group: vimarsh-alerts
```

#### 3. Rate Limit Alert

```yaml
Alert Name: Azure OpenAI Rate Limit Exceeded
Condition: HTTP 429 errors detected
Window: 5 minutes
Severity: Critical
Action Group: vimarsh-alerts
```

#### 4. Daily Cost Anomaly Alert

```yaml
Alert Name: Unexpected Daily Cost Spike
Condition: Daily cost > $5 (anomaly detection)
Window: 24 hours
Severity: Info
Action Group: vimarsh-alerts
```

### Setting Up Alerts

1. Navigate to Application Insights → Alerts
2. Click "+ New alert rule"
3. Configure each alert from the list above
4. Create action group "vimarsh-alerts" with:
   - Email notifications
   - SMS notifications (optional)
   - Azure Mobile App push (optional)

---

## Rollback Plan

If issues arise during deployment:

### Immediate Rollback (< 5 minutes)

```bash
# Revert to previous deployment slot
az functionapp deployment slot swap \
  --name vimarsh-function-app \
  --resource-group vimarsh-rg \
  --slot staging

# Or redeploy previous version
git checkout <previous-commit-hash>
func azure functionapp publish vimarsh-function-app
```

### Complete Rollback (< 30 minutes)

1. **Revert Environment Variables**
   - Remove Azure OpenAI variables
   - Re-add Gemini variables (if needed)
   - Restart Function App

2. **Redeploy Previous Code**
   ```bash
   git revert HEAD
   git push origin main
   # GitHub Actions will auto-deploy
   ```

3. **Verify Rollback**
   - Test embedding generation
   - Check Application Insights
   - Validate user queries

---

## Success Criteria

### Technical Success
- [ ] Function App deployment successful (green status)
- [ ] Azure OpenAI embedding generation working (768 dims)
- [ ] RAG queries returning results with citations
- [ ] Response latency <3s average
- [ ] Error rate <1%
- [ ] All 25 personalities responding correctly

### User Experience Success
- [ ] Zero user-visible changes or errors
- [ ] Response quality maintained (MTEB 64.6)
- [ ] Citation accuracy maintained (>80%)
- [ ] No increase in response latency
- [ ] Mobile and desktop working correctly

### Monitoring Success
- [ ] Application Insights tracking all metrics
- [ ] Alerts configured and tested
- [ ] Cost monitoring active
- [ ] Dashboard showing real-time health
- [ ] No critical errors in logs

---

## Post-Deployment Tasks

### Immediate (0-2 hours)
- [ ] Monitor Application Insights for errors
- [ ] Test 5-10 queries per personality
- [ ] Verify citation accuracy
- [ ] Check response latency
- [ ] Monitor Azure OpenAI usage metrics

### Short-term (2-24 hours)
- [ ] Monitor daily cost vs. projections ($0.05-0.10/day)
- [ ] Review error logs and fix any issues
- [ ] Gather user feedback (if any)
- [ ] Optimize batch sizes if needed
- [ ] Document any unexpected behaviors

### Medium-term (1-7 days)
- [ ] Analyze full week of production metrics
- [ ] Compare quality vs. Gemini baseline
- [ ] Identify cost optimization opportunities
- [ ] Consider enabling Reserved Capacity (40% savings)
- [ ] Update documentation with learnings

---

## Contact & Escalation

**For Issues During Deployment:**
- Check Application Insights logs first
- Review GitHub Actions workflow logs
- Consult `docs/AZURE_OPENAI_MIGRATION.md` for details
- Rollback if critical issues detected

**Post-Deployment Support:**
- Monitor Application Insights dashboard
- Review Azure Cost Management daily
- Check user feedback channels
- Update `docs/metadata.md` with status

---

**Last Updated**: December 6, 2025  
**Status**: 📋 PENDING DEPLOYMENT  
**Next Step**: Configure Azure Function App environment variables
