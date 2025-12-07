# Application Insights Monitoring - User Settings Feature

## Document Information
- **Feature**: User Settings & Preferences Management
- **Version**: 1.0.0
- **Last Updated**: Phase 5 Production Deployment
- **Monitoring Platform**: Azure Application Insights

---

## Table of Contents
1. [Overview](#overview)
2. [Custom Metrics Configuration](#custom-metrics-configuration)
3. [Alert Rules](#alert-rules)
4. [Dashboards](#dashboards)
5. [Log Analytics Queries](#log-analytics-queries)
6. [Setup Commands](#setup-commands)
7. [Monitoring Best Practices](#monitoring-best-practices)

---

## Overview

### Monitoring Objectives
The User Settings feature requires comprehensive monitoring to ensure:
- **Availability**: All 5 API endpoints operational (>99.5% uptime)
- **Performance**: Fast response times (P95 <500ms, P99 <1000ms)
- **Reliability**: Low error rates (<0.5%)
- **User Experience**: Successful auto-save, preference updates, data exports
- **Adoption**: Track feature usage and user engagement

### Monitoring Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                  Frontend (React)                           │
│  • Page views: /settings                                    │
│  • User actions: tab navigation, preference changes         │
│  • Auto-save events: success/failure with debounce timing   │
│  • Client-side errors: React error boundaries               │
│  └───────────────────────────────────────────────────────────┘
                          ↓ (telemetry)
┌─────────────────────────────────────────────────────────────┐
│            Application Insights (Frontend)                  │
│  • Custom Events: settings_visit, preference_update         │
│  • Page Views: /settings, /settings#profile                 │
│  • Performance: bundle load time, render metrics            │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│              Azure Functions (Backend)                      │
│  • API requests: GET/PATCH/POST/DELETE                      │
│  • Service calls: PreferencesService, DataExportService     │
│  • Database operations: Cosmos DB queries                   │
│  • Errors: exceptions, failed validations                   │
└─────────────────────────────────────────────────────────────┘
                          ↓ (telemetry)
┌─────────────────────────────────────────────────────────────┐
│            Application Insights (Backend)                   │
│  • Requests: latency, success rate, throughput              │
│  • Dependencies: Cosmos DB calls, JWT validation            │
│  • Exceptions: stack traces, error rates                    │
│  • Custom Metrics: settings_api_calls, data_export_count    │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                  Alerts & Dashboards                        │
│  • Critical: Error rate >5%, Latency >2s                    │
│  • Warning: Unusual traffic, slow Cosmos DB queries         │
│  • Info: Daily adoption reports, weekly summaries           │
└─────────────────────────────────────────────────────────────┘
```

---

## Custom Metrics Configuration

### Frontend Custom Events

#### 1. Settings Page Visit
**Event Name**: `settings_page_visit`
**When Triggered**: User navigates to `/settings` route
**Custom Properties**:
```typescript
{
  user_id: string;
  entry_point: "navigation" | "direct_url" | "notification";
  device_type: "mobile" | "tablet" | "desktop";
  is_first_visit: boolean;
  session_id: string;
}
```

**Implementation** (frontend):
```typescript
// frontend/src/pages/UserSettings.tsx
import { useEffect } from 'react';
import { trackEvent } from '../utils/analytics';

const UserSettings = () => {
  useEffect(() => {
    trackEvent('settings_page_visit', {
      user_id: currentUser.id,
      entry_point: document.referrer ? 'navigation' : 'direct_url',
      device_type: getDeviceType(),
      is_first_visit: !localStorage.getItem('settings_visited'),
      session_id: sessionStorage.getItem('session_id')
    });
    
    localStorage.setItem('settings_visited', 'true');
  }, []);
  
  // Component code...
};
```

---

#### 2. Preference Update Event
**Event Name**: `preference_update`
**When Triggered**: User changes any setting and auto-save completes
**Custom Properties**:
```typescript
{
  user_id: string;
  preference_type: "conversation_style" | "language" | "theme" | "notifications" | "privacy" | "favorites";
  old_value: string;
  new_value: string;
  update_source: "manual" | "bulk_import";
  save_duration_ms: number;
  success: boolean;
}
```

**Implementation** (frontend):
```typescript
// frontend/src/hooks/useSettings.ts
const updateSetting = async (key: string, value: any) => {
  const startTime = Date.now();
  const oldValue = settings[key];
  
  try {
    await preferencesService.updatePreferences({ [key]: value });
    const duration = Date.now() - startTime;
    
    trackEvent('preference_update', {
      user_id: currentUser.id,
      preference_type: key,
      old_value: JSON.stringify(oldValue),
      new_value: JSON.stringify(value),
      update_source: 'manual',
      save_duration_ms: duration,
      success: true
    });
  } catch (error) {
    trackEvent('preference_update', {
      user_id: currentUser.id,
      preference_type: key,
      save_duration_ms: Date.now() - startTime,
      success: false,
      error_message: error.message
    });
    throw error;
  }
};
```

---

#### 3. Tab Navigation Event
**Event Name**: `settings_tab_change`
**When Triggered**: User switches between Settings tabs
**Custom Properties**:
```typescript
{
  user_id: string;
  from_tab: "profile" | "experience" | "notifications" | "memory" | "account";
  to_tab: "profile" | "experience" | "notifications" | "memory" | "account";
  navigation_method: "click" | "keyboard" | "url_hash";
  time_on_previous_tab_seconds: number;
}
```

---

#### 4. Auto-Save Event
**Event Name**: `settings_autosave`
**When Triggered**: Auto-save debounce timer triggers save
**Custom Properties**:
```typescript
{
  user_id: string;
  debounce_delay_ms: 500;
  changes_count: number;
  save_success: boolean;
  save_duration_ms: number;
}
```

---

#### 5. Data Export Event
**Event Name**: `user_data_export`
**When Triggered**: User requests data export
**Custom Properties**:
```typescript
{
  user_id: string;
  export_format: "json";
  data_size_kb: number;
  export_duration_ms: number;
  export_success: boolean;
}
```

---

### Backend Custom Metrics

#### 1. API Latency Tracking
**Metric Name**: `settings_api_latency_ms`
**Type**: Histogram
**Dimensions**:
- `endpoint`: "profile" | "preferences" | "usage" | "export" | "account"
- `http_method`: "GET" | "PATCH" | "POST" | "DELETE"
- `success`: true | false

**Implementation** (backend):
```python
# backend/function_app.py
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import metrics
import time

# Initialize meter
meter = metrics.get_meter(__name__)
api_latency = meter.create_histogram(
    name="settings_api_latency_ms",
    description="API endpoint latency in milliseconds",
    unit="ms"
)

@app.route(route="api/user/profile", methods=["GET"])
async def get_user_profile(req: func.HttpRequest) -> func.HttpResponse:
    start_time = time.time()
    success = False
    
    try:
        # Endpoint logic...
        response = create_response(profile_data)
        success = True
        return response
        
    except Exception as e:
        logger.error(f"Profile retrieval error: {e}")
        return error_response(500)
        
    finally:
        duration_ms = (time.time() - start_time) * 1000
        api_latency.record(
            duration_ms,
            attributes={
                "endpoint": "profile",
                "http_method": "GET",
                "success": str(success)
            }
        )
```

---

#### 2. Preference Update Count
**Metric Name**: `preferences_update_count`
**Type**: Counter
**Dimensions**:
- `preference_type`: "conversation_style" | "language" | "theme" | etc.
- `user_tier`: "free" | "premium"

**Implementation** (backend):
```python
# backend/services/preferences_service.py
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import metrics

meter = metrics.get_meter(__name__)
update_counter = meter.create_counter(
    name="preferences_update_count",
    description="Number of preference updates by type"
)

async def update_preferences(self, user_id: str, updates: dict) -> UserPreferences:
    # Update logic...
    
    for key in updates.keys():
        update_counter.add(
            1,
            attributes={
                "preference_type": key,
                "user_tier": await self._get_user_tier(user_id)
            }
        )
    
    return updated_preferences
```

---

#### 3. Data Export Success Rate
**Metric Name**: `data_export_success_rate`
**Type**: Gauge
**Dimensions**:
- `export_format`: "json"
- `data_size_category`: "small" | "medium" | "large"

---

#### 4. Cosmos DB Query Latency
**Metric Name**: `cosmosdb_query_latency_ms`
**Type**: Histogram
**Dimensions**:
- `container`: "user_preferences" | "conversation_memory" | "user_activity"
- `operation`: "read" | "write" | "update" | "delete"
- `ru_consumed`: float (Request Units)

**Implementation** (backend):
```python
# backend/services/preferences_service.py
import time
from azure.cosmos import exceptions

async def get_preferences(self, user_id: str) -> UserPreferences:
    start_time = time.time()
    ru_consumed = 0
    
    try:
        response = await self.container.read_item(
            item=user_id,
            partition_key=user_id
        )
        ru_consumed = response.headers.get('x-ms-request-charge', 0)
        
        return UserPreferences(**response)
        
    except exceptions.CosmosResourceNotFoundError:
        return self._get_default_preferences(user_id)
        
    finally:
        duration_ms = (time.time() - start_time) * 1000
        self.cosmos_latency_metric.record(
            duration_ms,
            attributes={
                "container": "user_preferences",
                "operation": "read",
                "ru_consumed": str(ru_consumed)
            }
        )
```

---

## Alert Rules

### Critical Alerts (Immediate Action Required)

#### Alert 1: High Error Rate in User Settings APIs
**Severity**: Critical (Sev 1)
**Trigger Condition**: Error rate > 5% for 5 consecutive minutes
**Target**: All 5 User Settings API endpoints
**Action**: Email + SMS to on-call engineer

**Azure CLI Setup**:
```bash
az monitor metrics alert create \
  --name "UserSettings-HighErrorRate" \
  --resource-group vimarsh-prod-rg \
  --scopes "/subscriptions/<sub-id>/resourceGroups/vimarsh-prod-rg/providers/Microsoft.Insights/components/vimarsh-backend-insights" \
  --condition "avg customMetrics/settings_api_latency_ms where success='false' > 5" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --severity 1 \
  --description "Critical: User Settings API error rate exceeds 5%" \
  --action-group "/subscriptions/<sub-id>/resourceGroups/vimarsh-prod-rg/providers/microsoft.insights/actionGroups/vimarsh-critical-alerts"
```

---

#### Alert 2: High API Latency (P95 > 2 seconds)
**Severity**: Critical (Sev 1)
**Trigger Condition**: P95 latency > 2000ms for 5 consecutive minutes
**Target**: All User Settings API endpoints
**Action**: Email + SMS to on-call engineer

**Kusto Query**:
```kusto
customMetrics
| where name == "settings_api_latency_ms"
| summarize P95Latency = percentile(value, 95) by bin(timestamp, 1m)
| where P95Latency > 2000
```

---

#### Alert 3: Data Export Failures
**Severity**: High (Sev 2)
**Trigger Condition**: > 2 export failures in 15 minutes
**Target**: POST /api/user/export endpoint
**Action**: Email to engineering team

---

#### Alert 4: Cosmos DB High Latency
**Severity**: High (Sev 2)
**Trigger Condition**: Cosmos DB query latency > 500ms (P95) for user_preferences
**Action**: Email to database team

**Kusto Query**:
```kusto
customMetrics
| where name == "cosmosdb_query_latency_ms"
| where customDimensions.container == "user_preferences"
| summarize P95Latency = percentile(value, 95) by bin(timestamp, 5m)
| where P95Latency > 500
```

---

### Warning Alerts (Monitor Closely)

#### Alert 5: Unusual Settings Traffic Pattern
**Severity**: Warning (Sev 3)
**Trigger Condition**: Settings page visits > 3x daily average
**Purpose**: Detect potential bot traffic or viral event
**Action**: Email to product team

---

#### Alert 6: Auto-Save Failure Rate Increase
**Severity**: Warning (Sev 3)
**Trigger Condition**: Auto-save failures > 2% in 10 minutes
**Purpose**: Detect frontend-backend connectivity issues
**Action**: Email to frontend team

---

## Dashboards

### Dashboard 1: User Settings Overview
**Purpose**: Executive summary of Settings feature adoption and health
**Refresh Rate**: 5 minutes

**Tiles**:
1. **Total Settings Visits (Last 7 Days)**
   - KQL Query:
   ```kusto
   customEvents
   | where timestamp > ago(7d)
   | where name == "settings_page_visit"
   | summarize TotalVisits = count()
   ```

2. **Unique Users with Settings Configured**
   - KQL Query:
   ```kusto
   customEvents
   | where timestamp > ago(7d)
   | where name == "preference_update"
   | summarize UniqueUsers = dcount(user_Id)
   ```

3. **Settings Adoption Rate**
   - KQL Query:
   ```kusto
   let totalUsers = toscalar(customEvents | where timestamp > ago(7d) | dcount(user_Id));
   let settingsUsers = toscalar(customEvents | where timestamp > ago(7d) | where name == "settings_page_visit" | dcount(user_Id));
   print AdoptionRate = (settingsUsers * 100.0) / totalUsers
   ```

4. **API Error Rate (Real-Time)**
   - KQL Query:
   ```kusto
   requests
   | where timestamp > ago(15m)
   | where url contains "/api/user/"
   | summarize ErrorRate = 100.0 * countif(success == false) / count()
   ```

5. **P95 API Latency by Endpoint**
   - KQL Query:
   ```kusto
   customMetrics
   | where timestamp > ago(1h)
   | where name == "settings_api_latency_ms"
   | summarize P95Latency = percentile(value, 95) by tostring(customDimensions.endpoint)
   | render barchart
   ```

---

### Dashboard 2: User Settings Performance
**Purpose**: Technical deep-dive for engineering team
**Refresh Rate**: 1 minute

**Tiles**:
1. **API Latency Distribution (Last 1 Hour)**
   ```kusto
   customMetrics
   | where timestamp > ago(1h)
   | where name == "settings_api_latency_ms"
   | summarize 
       P50 = percentile(value, 50),
       P75 = percentile(value, 75),
       P95 = percentile(value, 95),
       P99 = percentile(value, 99),
       Max = max(value)
     by bin(timestamp, 5m)
   | render timechart
   ```

2. **Cosmos DB Request Units (RU) Consumption**
   ```kusto
   customMetrics
   | where timestamp > ago(1h)
   | where name == "cosmosdb_query_latency_ms"
   | extend RU = todouble(customDimensions.ru_consumed)
   | summarize TotalRU = sum(RU) by bin(timestamp, 5m)
   | render timechart
   ```

3. **Top 10 Slowest API Calls**
   ```kusto
   customMetrics
   | where timestamp > ago(1h)
   | where name == "settings_api_latency_ms"
   | top 10 by value desc
   | project 
       timestamp,
       Endpoint = customDimensions.endpoint,
       LatencyMs = value,
       Success = customDimensions.success
   ```

4. **Preference Update Frequency by Type**
   ```kusto
   customEvents
   | where timestamp > ago(24h)
   | where name == "preference_update"
   | summarize UpdateCount = count() by PreferenceType = tostring(customDimensions.preference_type)
   | render piechart
   ```

---

### Dashboard 3: User Engagement Analytics
**Purpose**: Product insights for Settings feature
**Refresh Rate**: 1 hour

**Tiles**:
1. **Most Visited Settings Tabs**
   ```kusto
   customEvents
   | where timestamp > ago(7d)
   | where name == "settings_tab_change"
   | summarize Visits = count() by Tab = tostring(customDimensions.to_tab)
   | render barchart
   ```

2. **Average Time Spent per Tab**
   ```kusto
   customEvents
   | where timestamp > ago(7d)
   | where name == "settings_tab_change"
   | extend TimeOnTab = todouble(customDimensions.time_on_previous_tab_seconds)
   | summarize AvgTimeSeconds = avg(TimeOnTab) by Tab = tostring(customDimensions.from_tab)
   | render barchart
   ```

3. **Data Export Requests (Last 30 Days)**
   ```kusto
   customEvents
   | where timestamp > ago(30d)
   | where name == "user_data_export"
   | summarize 
       TotalExports = count(),
       SuccessfulExports = countif(customDimensions.export_success == "true"),
       AvgExportSizeKB = avg(todouble(customDimensions.data_size_kb))
   ```

4. **Settings Entry Points**
   ```kusto
   customEvents
   | where timestamp > ago(7d)
   | where name == "settings_page_visit"
   | summarize Visits = count() by EntryPoint = tostring(customDimensions.entry_point)
   | render piechart
   ```

---

## Log Analytics Queries

### Query 1: Identify Users with Slow Settings Page Load
**Purpose**: Find users experiencing poor performance
**Use Case**: Proactive customer support

```kusto
customEvents
| where timestamp > ago(24h)
| where name == "settings_page_visit"
| join kind=inner (
    pageViews
    | where timestamp > ago(24h)
    | where url contains "/settings"
  ) on user_Id
| where duration > 3000  // More than 3 seconds
| summarize 
    SlowLoads = count(),
    AvgLoadTime = avg(duration)
  by user_Id
| order by SlowLoads desc
| take 20
```

---

### Query 2: Detect Failed Preference Updates with Retry Attempts
**Purpose**: Identify intermittent backend issues
**Use Case**: Debugging connection problems

```kusto
customEvents
| where timestamp > ago(1h)
| where name == "preference_update"
| where customDimensions.success == "false"
| summarize 
    FailedAttempts = count(),
    DistinctUsers = dcount(user_Id),
    AvgDurationMs = avg(todouble(customDimensions.save_duration_ms))
  by PreferenceType = tostring(customDimensions.preference_type)
| order by FailedAttempts desc
```

---

### Query 3: Calculate Settings Feature ROI (Engagement Uplift)
**Purpose**: Measure impact of Settings on user retention
**Use Case**: Product metrics reporting

```kusto
let settingsUsers = customEvents
  | where timestamp between(ago(14d) .. ago(7d))
  | where name == "settings_page_visit"
  | distinct user_Id;
let nonSettingsUsers = customEvents
  | where timestamp between(ago(14d) .. ago(7d))
  | distinct user_Id
  | where user_Id !in (settingsUsers);
let settingsEngagement = customEvents
  | where timestamp > ago(7d)
  | where user_Id in (settingsUsers)
  | summarize AvgConversations = count() / dcount(user_Id);
let nonSettingsEngagement = customEvents
  | where timestamp > ago(7d)
  | where user_Id in (nonSettingsUsers)
  | summarize AvgConversations = count() / dcount(user_Id);
union settingsEngagement, nonSettingsEngagement
| summarize 
    SettingsUsersEngagement = max_if(AvgConversations, $table == "settingsEngagement"),
    NonSettingsUsersEngagement = max_if(AvgConversations, $table == "nonSettingsEngagement")
| extend UpliftPercentage = ((SettingsUsersEngagement - NonSettingsUsersEngagement) / NonSettingsUsersEngagement) * 100
```

---

## Setup Commands

### 1. Configure Application Insights Connection String

#### Backend (Azure Functions)
```bash
# Set Application Insights connection string
az functionapp config appsettings set \
  --name vimarsh-functions \
  --resource-group vimarsh-prod-rg \
  --settings "APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=<key>;IngestionEndpoint=https://eastus-8.in.applicationinsights.azure.com/;LiveEndpoint=https://eastus.livediagnostics.monitor.azure.com/"
```

#### Frontend (Static Web App)
```bash
# Set in frontend environment variables
az staticwebapp appsettings set \
  --name vimarsh-frontend \
  --resource-group vimarsh-prod-rg \
  --setting-names "REACT_APP_APPINSIGHTS_CONNECTION_STRING=<connection-string>"
```

---

### 2. Create Alert Action Group
```bash
# Create action group for critical alerts
az monitor action-group create \
  --name vimarsh-critical-alerts \
  --resource-group vimarsh-prod-rg \
  --short-name "VimarshCrit" \
  --email-receiver \
    name="OnCallEngineer" \
    email-address="oncall@vimarsh.app" \
    use-common-alert-schema=true
```

---

### 3. Deploy Monitoring Configuration
```bash
# Deploy all alert rules
az deployment group create \
  --resource-group vimarsh-prod-rg \
  --template-file infrastructure/monitoring/user-settings-alerts.bicep \
  --parameters \
    appInsightsName="vimarsh-backend-insights" \
    actionGroupId="/subscriptions/<sub-id>/resourceGroups/vimarsh-prod-rg/providers/microsoft.insights/actionGroups/vimarsh-critical-alerts"
```

---

## Monitoring Best Practices

### 1. Progressive Monitoring Rollout
- **Week 1**: Monitor only critical metrics (error rate, latency)
- **Week 2**: Add engagement metrics (page visits, preference updates)
- **Week 3**: Full analytics (user behavior, retention, ROI)

### 2. Alert Fatigue Prevention
- Start with high thresholds (error rate >10%)
- Gradually tighten thresholds as baseline stabilizes
- Use alert suppression during maintenance windows

### 3. Cost Optimization
- Use sampling for high-volume events (1% for page views)
- Disable debug logging after 7 days
- Archive logs to blob storage after 30 days

### 4. Privacy Compliance
- Never log PII (email, name, address) in custom properties
- Use anonymized user_id only
- Enable GDPR data export for Application Insights

---

## Monitoring Checklist

### Pre-Deployment
- [ ] Application Insights connection strings configured (backend + frontend)
- [ ] Custom events instrumentation code deployed
- [ ] Alert rules created and tested
- [ ] Action groups configured with correct email/SMS recipients
- [ ] Dashboards created in Azure Portal

### Post-Deployment (First 24 Hours)
- [ ] Verify telemetry flowing into Application Insights (check Live Metrics)
- [ ] Test alert triggers with synthetic errors
- [ ] Review initial user adoption metrics
- [ ] Check for unexpected error spikes

### Ongoing (Weekly)
- [ ] Review dashboard for anomalies
- [ ] Analyze user engagement trends
- [ ] Optimize slow API endpoints (P95 > 500ms)
- [ ] Update alert thresholds based on baseline

---

## Document Status
- **Version**: 1.0.0
- **Last Updated**: Phase 5 Production Deployment
- **Status**: ✅ Ready for implementation

---

**Next Steps**:
1. Deploy monitoring code to backend and frontend
2. Create alert rules in Azure Portal
3. Build dashboards for engineering and product teams
4. Train on-call engineers on alert response procedures

