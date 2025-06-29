// Enhanced Monitoring and Alerting Configuration for Vimarsh
// This template sets up comprehensive monitoring with spiritual guidance specific metrics
// DEPLOYMENT STRATEGY: Single environment production for cost efficiency

@description('Location for all resources - single region deployment')
param location string = resourceGroup().location

@description('Application name prefix')
param appName string = 'vimarsh'

@description('Application Insights resource name')
param appInsightsName string

@description('Function App name for metric collection')
param functionAppName string

@description('Cosmos DB account name for database monitoring')
param cosmosDbName string

@description('Expert review email for alert notifications')
param expertReviewEmail string = 'vedprakash.m@me.com'

@description('Monthly budget in USD for cost alerts')
param monthlyBudgetUsd int = 50

@description('Cost alert threshold (0 to 100)')
@minValue(0)
@maxValue(100)
param costAlertThreshold int = 80

// Variables for production single environment deployment
var resourceSuffix = appName
var actionGroupName = '${resourceSuffix}-alerts'
var smartDetectorName = '${resourceSuffix}-smart-detector'

// Existing Application Insights resource reference
resource appInsights 'Microsoft.Insights/components@2020-02-02' existing = {
  name: appInsightsName
}

// Action Group for alert notifications
resource alertActionGroup 'Microsoft.Insights/actionGroups@2023-01-01' = {
  name: actionGroupName
  location: 'Global'
  properties: {
    groupShortName: 'Vimarsh'
    enabled: true
    emailReceivers: [
      {
        name: 'ExpertTeam'
        emailAddress: expertReviewEmail
        useCommonAlertSchema: true
      }
    ]
    smsReceivers: []
    webhookReceivers: []
    azureAppPushReceivers: []
    itsmReceivers: []
    automationRunbookReceivers: []
    voiceReceivers: []
    logicAppReceivers: []
    azureFunctionReceivers: []
    armRoleReceivers: []
  }
  tags: {
    project: appName
    environment: environment
    component: 'monitoring'
  }
}

// Smart Detection for Application Insights
resource smartDetectorAlertRule 'Microsoft.AlertsManagement/smartDetectorAlertRules@2021-04-01' = {
  name: smartDetectorName
  location: 'Global'
  properties: {
    description: 'Smart detection for Vimarsh spiritual guidance system'
    state: 'Enabled'
    severity: 'Sev3'
    frequency: 'PT1M'
    detector: {
      id: 'FailureAnomaliesDetector'
    }
    scope: [appInsights.id]
    actionGroups: {
      groupIds: [alertActionGroup.id]
    }
  }
  tags: {
    project: appName
    environment: environment
    component: 'monitoring'
  }
}

// High Error Rate Alert
resource errorRateAlert 'Microsoft.Insights/metricAlerts@2018-03-01' = {
  name: '${resourceSuffix}-high-error-rate'
  location: 'Global'
  properties: {
    description: 'Alert when error rate exceeds threshold - spiritual guidance quality concern'
    severity: 2
    enabled: true
    scopes: [appInsights.id]
    evaluationFrequency: 'PT5M'
    windowSize: 'PT15M'
    criteria: {
      'odata.type': 'Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria'
      allOf: [
        {
          name: 'ErrorRate'
          metricName: 'requests/failed'
          operator: 'GreaterThan'
          threshold: environment == 'prod' ? 5 : 10
          timeAggregation: 'Count'
          criterionType: 'StaticThresholdCriterion'
        }
      ]
    }
    actions: [
      {
        actionGroupId: alertActionGroup.id
        webHookProperties: {}
      }
    ]
  }
  tags: {
    project: appName
    environment: environment
    component: 'monitoring'
  }
}

// High Response Time Alert
resource responseTimeAlert 'Microsoft.Insights/metricAlerts@2018-03-01' = {
  name: '${resourceSuffix}-high-response-time'
  location: 'Global'
  properties: {
    description: 'Alert when response time is too high - affects spiritual seeker experience'
    severity: 3
    enabled: true
    scopes: [appInsights.id]
    evaluationFrequency: 'PT5M'
    windowSize: 'PT15M'
    criteria: {
      'odata.type': 'Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria'
      allOf: [
        {
          name: 'ResponseTime'
          metricName: 'requests/duration'
          operator: 'GreaterThan'
          threshold: environment == 'prod' ? 10000 : 15000 // milliseconds
          timeAggregation: 'Average'
          criterionType: 'StaticThresholdCriterion'
        }
      ]
    }
    actions: [
      {
        actionGroupId: alertActionGroup.id
        webHookProperties: {}
      }
    ]
  }
  tags: {
    project: appName
    environment: environment
    component: 'monitoring'
  }
}

// Low Availability Alert
resource availabilityAlert 'Microsoft.Insights/metricAlerts@2018-03-01' = {
  name: '${resourceSuffix}-low-availability'
  location: 'Global'
  properties: {
    description: 'Alert when availability drops - spiritual guidance service disruption'
    severity: 1
    enabled: true
    scopes: [appInsights.id]
    evaluationFrequency: 'PT1M'
    windowSize: 'PT5M'
    criteria: {
      'odata.type': 'Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria'
      allOf: [
        {
          name: 'Availability'
          metricName: 'availabilityResults/availabilityPercentage'
          operator: 'LessThan'
          threshold: environment == 'prod' ? 99 : 95
          timeAggregation: 'Average'
          criterionType: 'StaticThresholdCriterion'
        }
      ]
    }
    actions: [
      {
        actionGroupId: alertActionGroup.id
        webHookProperties: {}
      }
    ]
  }
  tags: {
    project: appName
    environment: environment
    component: 'monitoring'
  }
}

// Function App CPU Alert
resource functionCpuAlert 'Microsoft.Insights/metricAlerts@2018-03-01' = if (functionAppName != '') {
  name: '${resourceSuffix}-function-high-cpu'
  location: 'Global'
  properties: {
    description: 'Alert when Function App CPU usage is high'
    severity: 2
    enabled: true
    scopes: [resourceId('Microsoft.Web/sites', functionAppName)]
    evaluationFrequency: 'PT5M'
    windowSize: 'PT15M'
    criteria: {
      'odata.type': 'Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria'
      allOf: [
        {
          name: 'CpuPercentage'
          metricName: 'CpuPercentage'
          operator: 'GreaterThan'
          threshold: 80
          timeAggregation: 'Average'
          criterionType: 'StaticThresholdCriterion'
        }
      ]
    }
    actions: [
      {
        actionGroupId: alertActionGroup.id
        webHookProperties: {}
      }
    ]
  }
  tags: {
    project: appName
    environment: environment
    component: 'monitoring'
  }
}

// Cosmos DB Request Rate Alert
resource cosmosRequestRateAlert 'Microsoft.Insights/metricAlerts@2018-03-01' = if (cosmosDbName != '') {
  name: '${resourceSuffix}-cosmos-high-requests'
  location: 'Global'
  properties: {
    description: 'Alert when Cosmos DB requests are unusually high'
    severity: 2
    enabled: true
    scopes: [resourceId('Microsoft.DocumentDB/databaseAccounts', cosmosDbName)]
    evaluationFrequency: 'PT5M'
    windowSize: 'PT15M'
    criteria: {
      'odata.type': 'Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria'
      allOf: [
        {
          name: 'TotalRequests'
          metricName: 'TotalRequests'
          operator: 'GreaterThan'
          threshold: environment == 'prod' ? 1000 : 500
          timeAggregation: 'Total'
          criterionType: 'StaticThresholdCriterion'
        }
      ]
    }
    actions: [
      {
        actionGroupId: alertActionGroup.id
        webHookProperties: {}
      }
    ]
  }
  tags: {
    project: appName
    environment: environment
    component: 'monitoring'
  }
}

// Budget Alert for Cost Management
resource budgetAlert 'Microsoft.Consumption/budgets@2023-05-01' = {
  name: '${resourceSuffix}-budget'
  properties: {
    timePeriod: {
      startDate: '2024-01-01'
      endDate: '2025-12-31'
    }
    timeGrain: 'Monthly'
    amount: monthlyBudgetUsd
    category: 'Cost'
    notifications: {
      'actual_${costAlertThreshold}': {
        enabled: true
        operator: 'GreaterThan'
        threshold: costAlertThreshold
        contactEmails: [expertReviewEmail]
        contactRoles: ['Owner', 'Contributor']
        thresholdType: 'Actual'
      }
      forecasted_100: {
        enabled: true
        operator: 'GreaterThan'
        threshold: 100
        contactEmails: [expertReviewEmail]
        contactRoles: ['Owner', 'Contributor']
        thresholdType: 'Forecasted'
      }
    }
    filter: {
      dimensions: {
        name: 'ResourceGroupName'
        operator: 'In'
        values: [resourceGroup().name]
      }
    }
  }
}

// Workbook for Spiritual Guidance Monitoring
resource monitoringWorkbook 'Microsoft.Insights/workbooks@2022-04-01' = {
  name: guid('${resourceSuffix}-workbook')
  location: location
  kind: 'shared'
  properties: {
    displayName: 'Vimarsh Spiritual Guidance Monitoring'
    serializedData: string({
      version: 'Notebook/1.0'
      items: [
        {
          type: 1
          content: {
            json: '## 🙏 Vimarsh Spiritual Guidance System Monitoring\n\nThis dashboard provides comprehensive monitoring for the divine wisdom platform, ensuring optimal service for spiritual seekers.'
          }
          name: 'text - Header'
        }
        {
          type: 3
          content: {
            version: 'KqlItem/1.0'
            query: 'requests\n| where timestamp > ago(24h)\n| summarize RequestCount = count(), AvgDuration = avg(duration), ErrorCount = countif(success == false) by bin(timestamp, 1h)\n| render timechart'
            size: 0
            title: '📊 Request Volume and Performance (24h)'
            timeContext: {
              durationMs: 86400000
            }
            queryType: 0
            resourceType: 'microsoft.insights/components'
          }
          name: 'query - Requests'
        }
        {
          type: 3
          content: {
            version: 'KqlItem/1.0'
            query: 'customEvents\n| where name == "SpiritualGuidanceRequested"\n| where timestamp > ago(7d)\n| summarize SeekersServed = dcount(user_Id) by bin(timestamp, 1d)\n| render columnchart'
            size: 0
            title: '🕉️ Daily Spiritual Seekers Served (7d)'
            timeContext: {
              durationMs: 604800000
            }
            queryType: 0
            resourceType: 'microsoft.insights/components'
          }
          name: 'query - Seekers'
        }
      ]
      styleSettings: {
        spacingStyle: 'wide'
      }
    })
    category: 'workbook'
    sourceId: appInsights.id
  }
  tags: {
    project: appName
    environment: environment
    component: 'monitoring'
  }
}

// Output important values
output actionGroupId string = alertActionGroup.id
output smartDetectorId string = smartDetectorAlertRule.id
output workbookId string = monitoringWorkbook.id
output budgetName string = budgetAlert.name

output monitoringEndpoints object = {
  appInsights: {
    instrumentationKey: appInsights.properties.InstrumentationKey
    connectionString: appInsights.properties.ConnectionString
  }
  actionGroup: {
    id: alertActionGroup.id
    name: alertActionGroup.name
  }
  workbook: {
    id: monitoringWorkbook.id
    name: monitoringWorkbook.properties.displayName
  }
}
