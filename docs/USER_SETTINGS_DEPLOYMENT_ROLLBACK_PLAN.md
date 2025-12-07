# User Settings Feature - Deployment Rollback Plan

## Document Information
- **Feature**: User Settings & Preferences Management
- **Version**: 1.0.0
- **Last Updated**: Phase 5 Production Deployment
- **Owner**: Development Team
- **Severity Matrix**: Critical (< 5 min), High (< 15 min), Medium (< 1 hour), Low (< 4 hours)

---

## Table of Contents
1. [Overview](#overview)
2. [Pre-Deployment Checklist](#pre-deployment-checklist)
3. [Rollback Triggers](#rollback-triggers)
4. [Frontend Rollback Procedures](#frontend-rollback-procedures)
5. [Backend Rollback Procedures](#backend-rollback-procedures)
6. [Database Rollback Procedures](#database-rollback-procedures)
7. [Feature Flag Strategy](#feature-flag-strategy)
8. [Smoke Testing Protocol](#smoke-testing-protocol)
9. [Emergency Contacts](#emergency-contacts)
10. [Post-Rollback Actions](#post-rollback-actions)

---

## Overview

### Purpose
This document provides comprehensive rollback procedures for the User Settings feature deployment to production. It ensures minimal downtime and data loss in case deployment issues arise.

### Deployment Phases
1. **Phase 1**: Backend API deployment (Azure Functions)
2. **Phase 2**: Frontend deployment (Azure Static Web Apps)
3. **Phase 3**: Database schema updates (Cosmos DB)
4. **Phase 4**: Monitoring setup (Application Insights)

### Rollback Philosophy
- **Quick Detection**: Monitor key metrics for 1 hour post-deployment
- **Fast Decision**: Rollback within 15 minutes of issue identification
- **Data Safety**: Preserve all user data during rollback
- **Communication**: Notify stakeholders immediately

---

## Pre-Deployment Checklist

### Backend Pre-Flight
- [ ] All 490+ tests passing (backend: 210+, frontend: 330+, E2E: 50+)
- [ ] `backend/requirements.txt` includes all dependencies:
  - `azure-functions>=1.11.0`
  - `azure-cosmos>=4.3.0`
  - `pydantic>=2.0.0`
  - `jwt>=1.3.1`
- [ ] Environment variables configured in Azure Functions:
  - `COSMOS_DB_ENDPOINT`
  - `COSMOS_DB_KEY`
  - `JWT_SECRET_KEY`
  - `ENTRA_ID_CLIENT_ID`
  - `ENTRA_ID_TENANT_ID`
- [ ] API endpoints tested in staging:
  - GET `/api/user/profile`
  - PATCH `/api/user/preferences`
  - GET `/api/user/usage-summary`
  - POST `/api/user/export`
  - DELETE `/api/user/account`

### Frontend Pre-Flight
- [ ] Production build successful (`npm run build`)
- [ ] Bundle size < 500KB (check with `webpack-bundle-analyzer`)
- [ ] Environment variables configured:
  - `VITE_API_BASE_URL=https://vimarsh-api.azurewebsites.net`
  - `VITE_AUTH_ENABLED=true`
- [ ] PWA manifest updated with Settings feature
- [ ] Service worker caches Settings routes

### Database Pre-Flight
- [ ] Backup of `user_preferences` container created
- [ ] Migration script tested in staging
- [ ] Rollback script validated
- [ ] Read/write throughput sufficient (400 RU/s minimum)

### Monitoring Pre-Flight
- [ ] Application Insights connected to both frontend and backend
- [ ] Custom metrics configured:
  - `settings_page_visits`
  - `preferences_update_success_rate`
  - `api_latency_p95`
  - `error_rate`
- [ ] Alerts configured for:
  - Error rate > 5%
  - P95 latency > 2 seconds
  - Settings save failures > 2%

---

## Rollback Triggers

### Automatic Rollback Triggers
Execute immediate rollback if any condition persists for 5+ minutes:

| **Trigger** | **Threshold** | **Severity** | **Action** |
|-------------|---------------|--------------|------------|
| Error Rate | > 10% | Critical | Immediate rollback |
| API Latency P95 | > 5 seconds | Critical | Immediate rollback |
| Settings Save Failure Rate | > 5% | High | Rollback within 15 min |
| Frontend Load Failure | > 3% | High | Rollback within 15 min |
| Database Connection Errors | > 1% | Critical | Immediate rollback |
| Authentication Failures | > 2% | High | Rollback within 15 min |

### Manual Rollback Triggers
- User reports indicating critical functionality broken
- Data corruption detected in `user_preferences` container
- Security vulnerability discovered
- Cascading failures in dependent services
- Regulatory/compliance concerns

---

## Frontend Rollback Procedures

### Azure Static Web Apps Rollback

#### Method 1: Deployment History (Recommended)
**Time to Execute**: ~2 minutes

```bash
# 1. Login to Azure CLI
az login

# 2. List recent deployments
az staticwebapp deployment list \
  --name vimarsh-frontend \
  --resource-group vimarsh-prod-rg

# 3. Identify previous stable deployment ID (e.g., abc123def456)
PREVIOUS_DEPLOYMENT_ID="abc123def456"

# 4. Rollback to previous deployment
az staticwebapp deployment show \
  --name vimarsh-frontend \
  --resource-group vimarsh-prod-rg \
  --deployment-id $PREVIOUS_DEPLOYMENT_ID

# Note: Azure Static Web Apps maintains deployment history
# Simply promote the previous deployment to production
```

#### Method 2: Git Revert & Redeploy
**Time to Execute**: ~5 minutes

```bash
# 1. Navigate to frontend directory
cd /Users/ved/Apps/vimarsh/frontend

# 2. Identify the commit before User Settings merge
git log --oneline -10
# Example output:
# a1b2c3d (HEAD -> main) feat: User Settings deployment
# e4f5g6h (previous stable) fix: Performance optimization

# 3. Revert to previous commit
STABLE_COMMIT="e4f5g6h"
git revert a1b2c3d --no-commit
git commit -m "ROLLBACK: Revert User Settings deployment"

# 4. Push to trigger automatic deployment
git push origin main

# 5. Monitor GitHub Actions for deployment completion
```

#### Method 3: Manual File Restoration
**Time to Execute**: ~3 minutes

```bash
# 1. Remove User Settings files
rm -rf frontend/src/components/Settings/
rm frontend/src/tests/Settings/*
rm frontend/cypress/e2e/user-settings.cy.ts

# 2. Revert App.tsx routing changes
git checkout HEAD~1 -- frontend/src/App.tsx

# 3. Rebuild and deploy
npm run build
npm run deploy:prod

# 4. Verify deployment
curl https://vimarsh.app/settings
# Should return 404 Not Found
```

### Verification Steps
After frontend rollback:

```bash
# 1. Check Settings page is inaccessible
curl -I https://vimarsh.app/settings
# Expected: 404 Not Found

# 2. Verify main app functionality
curl -I https://vimarsh.app/
# Expected: 200 OK

# 3. Test conversation interface
# Open browser -> https://vimarsh.app/chat/krishna
# Should load normally without Settings option

# 4. Check Application Insights
az monitor app-insights metrics show \
  --app vimarsh-frontend-insights \
  --resource-group vimarsh-prod-rg \
  --metric requests/failed \
  --start-time $(date -u -d '10 minutes ago' +%Y-%m-%dT%H:%M:%SZ)
# Expected: Error rate < 1%
```

---

## Backend Rollback Procedures

### Azure Functions Rollback

#### Method 1: Deployment Slots (Recommended)
**Time to Execute**: ~1 minute

```bash
# 1. Login to Azure
az login

# 2. Swap production slot back to previous staging slot
az functionapp deployment slot swap \
  --name vimarsh-functions \
  --resource-group vimarsh-prod-rg \
  --slot staging \
  --target-slot production

# 3. Verify slot swap
az functionapp show \
  --name vimarsh-functions \
  --resource-group vimarsh-prod-rg \
  --query "defaultHostName"
```

#### Method 2: Redeploy Previous Version
**Time to Execute**: ~3 minutes

```bash
# 1. Navigate to backend directory
cd /Users/ved/Apps/vimarsh/backend

# 2. Identify previous stable commit
git log --oneline -10
STABLE_COMMIT="e4f5g6h"

# 3. Checkout previous version
git checkout $STABLE_COMMIT

# 4. Deploy to Azure Functions
func azure functionapp publish vimarsh-functions \
  --python \
  --build remote

# 5. Return to main branch
git checkout main
```

#### Method 3: Remove User Settings Endpoints
**Time to Execute**: ~2 minutes

```python
# Edit backend/function_app.py
# Comment out User Settings endpoints:

# @app.route(route="user/profile", methods=["GET"], auth_level=func.AuthLevel.FUNCTION)
# async def get_user_profile(req: func.HttpRequest) -> func.HttpResponse:
#     """Get user profile endpoint - TEMPORARILY DISABLED"""
#     return func.HttpResponse("Endpoint temporarily unavailable", status_code=503)

# Repeat for all 5 User Settings endpoints
```

```bash
# Deploy updated function_app.py
func azure functionapp publish vimarsh-functions --python
```

### Verification Steps
After backend rollback:

```bash
# 1. Test User Settings endpoints are disabled
curl -H "Authorization: Bearer $JWT_TOKEN" \
  https://vimarsh-functions.azurewebsites.net/api/user/profile
# Expected: 404 Not Found or 503 Service Unavailable

# 2. Test core functionality still works
curl -H "Authorization: Bearer $JWT_TOKEN" \
  https://vimarsh-functions.azurewebsites.net/api/multi_domain_guidance \
  -d '{"query": "What is wisdom?", "personality": "krishna"}'
# Expected: 200 OK with guidance response

# 3. Check Azure Functions logs
az functionapp log tail \
  --name vimarsh-functions \
  --resource-group vimarsh-prod-rg
# Look for: No errors related to missing modules/dependencies

# 4. Monitor Application Insights
az monitor app-insights metrics show \
  --app vimarsh-backend-insights \
  --resource-group vimarsh-prod-rg \
  --metric requests/failed \
  --start-time $(date -u -d '10 minutes ago' +%Y-%m-%dT%H:%M:%SZ)
# Expected: Error rate < 1%
```

---

## Database Rollback Procedures

### Cosmos DB Rollback

#### Scenario 1: Schema Change Rollback
**Time to Execute**: ~5 minutes

```python
# backend/scripts/rollback_user_preferences_schema.py

import asyncio
from azure.cosmos.aio import CosmosClient
from azure.cosmos import PartitionKey
import os

async def rollback_schema():
    """Rollback user_preferences schema to previous version"""
    
    # Connect to Cosmos DB
    client = CosmosClient(
        os.getenv("COSMOS_DB_ENDPOINT"),
        os.getenv("COSMOS_DB_KEY")
    )
    
    database = client.get_database_client("vimarsh_production")
    container = database.get_container_client("user_preferences")
    
    print("🔄 Starting schema rollback...")
    
    # Query all documents
    query = "SELECT * FROM c"
    items = [item async for item in container.query_items(query, enable_cross_partition_query=True)]
    
    print(f"📊 Found {len(items)} user preference documents")
    
    rollback_count = 0
    
    for item in items:
        try:
            # Remove new User Settings fields if they exist
            fields_to_remove = [
                'journey_stats',
                'ai_usage',
                'favorite_personalities',
                'conversation_memory',
                'privacy_settings',
                'subscription_tier',
                'usage_limits'
            ]
            
            modified = False
            for field in fields_to_remove:
                if field in item:
                    del item[field]
                    modified = True
            
            if modified:
                await container.replace_item(item=item['id'], body=item)
                rollback_count += 1
                print(f"✅ Rolled back user_id: {item['user_id']}")
        
        except Exception as e:
            print(f"❌ Error rolling back {item['user_id']}: {str(e)}")
            continue
    
    print(f"🎉 Rollback complete! Modified {rollback_count} documents")
    await client.close()

if __name__ == "__main__":
    asyncio.run(rollback_schema())
```

```bash
# Execute rollback script
cd /Users/ved/Apps/vimarsh/backend
python scripts/rollback_user_preferences_schema.py
```

#### Scenario 2: Point-in-Time Restore
**Time to Execute**: ~15 minutes (requires Azure support)

```bash
# 1. Create restore request in Azure Portal
az cosmosdb sql container restore \
  --account-name vimarsh-cosmosdb \
  --resource-group vimarsh-prod-rg \
  --database-name vimarsh_production \
  --name user_preferences \
  --restore-timestamp "2024-01-15T10:00:00Z" \
  --target-container-name user_preferences_restored

# 2. Verify restored data
az cosmosdb sql container show \
  --account-name vimarsh-cosmosdb \
  --resource-group vimarsh-prod-rg \
  --database-name vimarsh_production \
  --name user_preferences_restored

# 3. Swap containers (requires manual intervention)
# Contact Azure support to swap container names
```

#### Scenario 3: Restore from Backup
**Time to Execute**: ~10 minutes

```bash
# 1. List available backups
az cosmosdb sql container backup list \
  --account-name vimarsh-cosmosdb \
  --resource-group vimarsh-prod-rg \
  --database-name vimarsh_production \
  --name user_preferences

# 2. Restore from latest backup before deployment
BACKUP_ID="backup-20240115-0900"
az cosmosdb sql container restore \
  --account-name vimarsh-cosmosdb \
  --resource-group vimarsh-prod-rg \
  --database-name vimarsh_production \
  --name user_preferences \
  --backup-id $BACKUP_ID

# 3. Verify data integrity
python backend/scripts/verify_backup_integrity.py
```

### Verification Steps
After database rollback:

```python
# backend/scripts/verify_database_rollback.py

import asyncio
from azure.cosmos.aio import CosmosClient
import os

async def verify_rollback():
    """Verify database rollback completed successfully"""
    
    client = CosmosClient(
        os.getenv("COSMOS_DB_ENDPOINT"),
        os.getenv("COSMOS_DB_KEY")
    )
    
    database = client.get_database_client("vimarsh_production")
    container = database.get_container_client("user_preferences")
    
    # Sample 10 random documents
    query = "SELECT TOP 10 * FROM c"
    items = [item async for item in container.query_items(query, enable_cross_partition_query=True)]
    
    print("🔍 Verifying rollback...")
    
    for item in items:
        # Check that new fields don't exist
        new_fields = ['journey_stats', 'ai_usage', 'subscription_tier']
        has_new_fields = any(field in item for field in new_fields)
        
        if has_new_fields:
            print(f"❌ FAILED: Document {item['id']} still has new fields")
            return False
        else:
            print(f"✅ OK: Document {item['id']} rolled back successfully")
    
    print("🎉 All sampled documents verified!")
    await client.close()
    return True

if __name__ == "__main__":
    result = asyncio.run(verify_rollback())
    exit(0 if result else 1)
```

---

## Feature Flag Strategy

### Gradual Rollout with Feature Flags

#### Implementation
Add feature flag support to control User Settings visibility:

```typescript
// frontend/src/utils/featureFlags.ts

interface FeatureFlags {
  userSettingsEnabled: boolean;
  settingsAutoSaveEnabled: boolean;
  dataExportEnabled: boolean;
  accountDeletionEnabled: boolean;
}

export const getFeatureFlags = async (): Promise<FeatureFlags> => {
  try {
    const response = await fetch('/api/feature-flags');
    return await response.json();
  } catch (error) {
    // Default to disabled if flag service unavailable
    return {
      userSettingsEnabled: false,
      settingsAutoSaveEnabled: false,
      dataExportEnabled: false,
      accountDeletionEnabled: false,
    };
  }
};
```

```typescript
// frontend/src/App.tsx

import { useEffect, useState } from 'react';
import { getFeatureFlags } from './utils/featureFlags';

function App() {
  const [flags, setFlags] = useState<FeatureFlags | null>(null);
  
  useEffect(() => {
    getFeatureFlags().then(setFlags);
  }, []);
  
  if (!flags) return <LoadingSpinner />;
  
  return (
    <Router>
      {/* Existing routes */}
      
      {/* Conditional Settings route */}
      {flags.userSettingsEnabled && (
        <Route path="/settings" element={<UserSettings />} />
      )}
    </Router>
  );
}
```

#### Gradual Rollout Plan

**Phase 1: Internal Testing (0-24 hours)**
```json
{
  "userSettingsEnabled": true,
  "enabledForUserIds": ["internal-team-user-1", "internal-team-user-2"],
  "enabledForEmails": ["*@vimarsh.app"]
}
```

**Phase 2: Beta Users (24-72 hours)**
```json
{
  "userSettingsEnabled": true,
  "rolloutPercentage": 10,
  "betaUserGroup": true
}
```

**Phase 3: General Availability (72+ hours)**
```json
{
  "userSettingsEnabled": true,
  "rolloutPercentage": 100
}
```

#### Emergency Disable (Soft Rollback)
**Time to Execute**: ~30 seconds

```bash
# Update feature flags in Azure App Configuration
az appconfig kv set \
  --name vimarsh-app-config \
  --key "feature-flags:user-settings:enabled" \
  --value false \
  --yes

# Feature will be disabled for all users within 30 seconds
# No deployment required!
```

---

## Smoke Testing Protocol

### Post-Deployment Smoke Tests
Execute these tests immediately after deployment (before declaring success):

#### Backend API Tests
```bash
# backend/tests/smoke_tests_production.sh

#!/bin/bash
set -e

API_BASE_URL="https://vimarsh-functions.azurewebsites.net/api"
JWT_TOKEN="<production-test-user-token>"

echo "🧪 Starting User Settings smoke tests..."

# Test 1: Get user profile
echo "Test 1: GET /user/profile"
RESPONSE=$(curl -s -w "%{http_code}" -o /tmp/profile.json \
  -H "Authorization: Bearer $JWT_TOKEN" \
  "$API_BASE_URL/user/profile")

if [ "$RESPONSE" == "200" ]; then
  echo "✅ Profile retrieval successful"
else
  echo "❌ FAILED: Profile returned $RESPONSE"
  exit 1
fi

# Test 2: Update preferences
echo "Test 2: PATCH /user/preferences"
RESPONSE=$(curl -s -w "%{http_code}" -o /dev/null \
  -X PATCH \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"conversation_style":"formal"}' \
  "$API_BASE_URL/user/preferences")

if [ "$RESPONSE" == "200" ]; then
  echo "✅ Preferences update successful"
else
  echo "❌ FAILED: Preferences update returned $RESPONSE"
  exit 1
fi

# Test 3: Get usage summary
echo "Test 3: GET /user/usage-summary"
RESPONSE=$(curl -s -w "%{http_code}" -o /tmp/usage.json \
  -H "Authorization: Bearer $JWT_TOKEN" \
  "$API_BASE_URL/user/usage-summary")

if [ "$RESPONSE" == "200" ]; then
  echo "✅ Usage summary retrieval successful"
else
  echo "❌ FAILED: Usage summary returned $RESPONSE"
  exit 1
fi

# Test 4: Request data export
echo "Test 4: POST /user/export"
RESPONSE=$(curl -s -w "%{http_code}" -o /tmp/export.json \
  -X POST \
  -H "Authorization: Bearer $JWT_TOKEN" \
  "$API_BASE_URL/user/export")

if [ "$RESPONSE" == "200" ]; then
  echo "✅ Data export successful"
else
  echo "❌ FAILED: Data export returned $RESPONSE"
  exit 1
fi

echo "🎉 All backend smoke tests passed!"
```

#### Frontend Tests
```bash
# frontend/tests/smoke_tests_production.sh

#!/bin/bash
set -e

FRONTEND_URL="https://vimarsh.app"

echo "🧪 Starting frontend smoke tests..."

# Test 1: Settings page loads
echo "Test 1: Settings page accessibility"
RESPONSE=$(curl -s -w "%{http_code}" -o /dev/null "$FRONTEND_URL/settings")

if [ "$RESPONSE" == "200" ]; then
  echo "✅ Settings page loads successfully"
else
  echo "❌ FAILED: Settings page returned $RESPONSE"
  exit 1
fi

# Test 2: Main app still works
echo "Test 2: Main conversation interface"
RESPONSE=$(curl -s -w "%{http_code}" -o /dev/null "$FRONTEND_URL/chat/krishna")

if [ "$RESPONSE" == "200" ]; then
  echo "✅ Conversation interface loads successfully"
else
  echo "❌ FAILED: Conversation interface returned $RESPONSE"
  exit 1
fi

# Test 3: PWA manifest includes Settings
echo "Test 3: PWA manifest integrity"
MANIFEST=$(curl -s "$FRONTEND_URL/manifest.json")
if echo "$MANIFEST" | grep -q "settings"; then
  echo "✅ PWA manifest includes Settings"
else
  echo "⚠️  WARNING: Settings not in PWA manifest"
fi

echo "🎉 All frontend smoke tests passed!"
```

#### E2E Cypress Tests (Critical Paths Only)
```bash
# Run critical user journeys in production
cd /Users/ved/Apps/vimarsh/frontend

# Set production environment
export CYPRESS_BASE_URL="https://vimarsh.app"
export CYPRESS_API_BASE_URL="https://vimarsh-functions.azurewebsites.net/api"

# Run only critical tests (tagged with @smoke)
npx cypress run \
  --spec "cypress/e2e/user-settings.cy.ts" \
  --env grepTags=@smoke \
  --config video=true,screenshotOnRunFailure=true
```

### Monitoring During Smoke Tests
```bash
# Monitor Application Insights in real-time
az monitor app-insights metrics show \
  --app vimarsh-frontend-insights \
  --resource-group vimarsh-prod-rg \
  --metric requests/failed \
  --interval PT1M \
  --start-time $(date -u -d '5 minutes ago' +%Y-%m-%dT%H:%M:%SZ) \
  --aggregation Average

# Expected: error_rate < 1%, latency_p95 < 2s
```

---

## Emergency Contacts

### On-Call Rotation
| **Role** | **Primary** | **Secondary** | **Phone** | **Email** |
|----------|-------------|---------------|-----------|-----------|
| **DevOps Lead** | Ved Prakash | [TBD] | [TBD] | ved@vimarsh.app |
| **Backend Lead** | [TBD] | [TBD] | [TBD] | backend@vimarsh.app |
| **Frontend Lead** | [TBD] | [TBD] | [TBD] | frontend@vimarsh.app |
| **Database Admin** | [TBD] | [TBD] | [TBD] | dba@vimarsh.app |

### Escalation Path
1. **Level 1** (0-15 min): On-call engineer attempts automated rollback
2. **Level 2** (15-30 min): Team lead involvement, manual rollback if needed
3. **Level 3** (30-60 min): CTO involvement, Azure support ticket opened
4. **Level 4** (60+ min): Full incident response team, stakeholder notification

### Communication Channels
- **Slack**: `#vimarsh-deployments` (real-time updates)
- **Email**: `deployments@vimarsh.app` (formal notifications)
- **Status Page**: `status.vimarsh.app` (public updates)

---

## Post-Rollback Actions

### Immediate Actions (Within 1 hour)
1. **Root Cause Analysis**: Create incident document in `/docs/incidents/`
2. **User Communication**: Post status update on `status.vimarsh.app`
3. **Monitoring**: Keep enhanced monitoring active for 24 hours
4. **Data Integrity Check**: Verify no user data was corrupted

### Short-term Actions (Within 24 hours)
1. **Incident Report**: Complete detailed post-mortem document
2. **Fix Development**: Create hotfix branch with issue resolution
3. **Testing Enhancement**: Add regression tests for failure scenario
4. **Staging Validation**: Deploy fix to staging, validate for 24 hours

### Long-term Actions (Within 1 week)
1. **Process Improvement**: Update deployment checklist with new learnings
2. **Monitoring Enhancement**: Add new Application Insights metrics if gaps identified
3. **Training**: Share incident learnings with team
4. **Prevention**: Implement additional safeguards to prevent recurrence

### Post-Rollback Incident Template
```markdown
# Incident Report: User Settings Deployment Rollback

## Incident Summary
- **Date**: [YYYY-MM-DD]
- **Time**: [HH:MM UTC]
- **Duration**: [XX minutes]
- **Severity**: [Critical/High/Medium/Low]
- **Services Affected**: [Frontend/Backend/Database]

## Timeline
- **[HH:MM]**: Deployment initiated
- **[HH:MM]**: Issue detected (describe symptoms)
- **[HH:MM]**: Rollback decision made
- **[HH:MM]**: Rollback completed
- **[HH:MM]**: Services restored

## Root Cause
[Detailed explanation of what went wrong]

## Impact
- **Users Affected**: [Number/Percentage]
- **Data Loss**: [None/Minimal/Significant]
- **Downtime**: [XX minutes]
- **Revenue Impact**: [If applicable]

## Resolution
[Steps taken to resolve the issue]

## Prevention
[Actions to prevent recurrence]

## Action Items
- [ ] [Action 1] - Owner: [Name] - Due: [Date]
- [ ] [Action 2] - Owner: [Name] - Due: [Date]
```

---

## Rollback Success Criteria

### Backend Rollback Success
- ✅ All User Settings API endpoints return 404 or 503
- ✅ Core RAG pipeline endpoints respond successfully
- ✅ Error rate < 1% in Application Insights
- ✅ No missing module errors in Azure Functions logs

### Frontend Rollback Success
- ✅ `/settings` route returns 404 Not Found
- ✅ Main conversation interface loads normally
- ✅ No console errors related to Settings components
- ✅ Bundle size within expected range (< 3MB)

### Database Rollback Success
- ✅ Sample documents verified without new fields
- ✅ No orphaned data in `user_preferences` container
- ✅ Read/write operations performing normally
- ✅ No data corruption reported

### Overall Success
- ✅ All smoke tests passing
- ✅ No user-reported issues for 1 hour post-rollback
- ✅ Monitoring metrics within normal ranges
- ✅ Zero data loss confirmed

---

## Appendix A: Quick Reference Commands

### Fast Rollback Commands (Copy-Paste Ready)

#### Frontend Rollback (Azure CLI)
```bash
az staticwebapp deployment list --name vimarsh-frontend --resource-group vimarsh-prod-rg
az staticwebapp deployment show --name vimarsh-frontend --resource-group vimarsh-prod-rg --deployment-id <PREVIOUS_ID>
```

#### Backend Rollback (Azure CLI)
```bash
az functionapp deployment slot swap --name vimarsh-functions --resource-group vimarsh-prod-rg --slot staging --target-slot production
```

#### Feature Flag Disable
```bash
az appconfig kv set --name vimarsh-app-config --key "feature-flags:user-settings:enabled" --value false --yes
```

#### Check Application Insights
```bash
az monitor app-insights metrics show --app vimarsh-frontend-insights --resource-group vimarsh-prod-rg --metric requests/failed --interval PT1M
```

---

## Document Revision History
- **v1.0.0** (Phase 5): Initial rollback plan created with comprehensive procedures for frontend, backend, database rollback, feature flags, smoke testing, and emergency contacts

---

**Status**: ✅ Ready for Phase 5 Production Deployment

