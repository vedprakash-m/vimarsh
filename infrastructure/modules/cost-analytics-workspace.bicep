// Cost Analytics Workspace Module
// Creates Log Analytics workspace for cost analysis

@description('Workspace name')
param workspaceName string

@description('Location')
param location string

@description('Environment name')
param environmentName string

@description('Retention in days')
param retentionInDays int = 90

resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: workspaceName
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: retentionInDays
    features: {
      searchVersion: 1
      legacy: 0
      enableLogAccessUsingOnlyResourcePermissions: true
    }
    workspaceCapping: {
      dailyQuotaGb: 1
    }
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
  tags: {
    Environment: environmentName
    Purpose: 'Cost Analytics'
    CostCenter: 'Engineering'
  }
}

// Create saved searches for cost analysis
resource costAnalysisQueries 'Microsoft.OperationalInsights/workspaces/savedSearches@2020-08-01' = {
  parent: logAnalyticsWorkspace
  name: 'VimarshCostAnalysis'
  properties: {
    category: 'Cost Management'
    displayName: 'Vimarsh Cost Analysis Queries'
    query: '''
      // Daily cost trend
      Usage
      | where TimeGenerated > ago(30d)
      | summarize DailyCost = sum(Quantity * UnitPrice) by bin(TimeGenerated, 1d)
      | render timechart
      
      // Top expensive resources
      Usage
      | where TimeGenerated > ago(7d)
      | summarize TotalCost = sum(Quantity * UnitPrice) by ResourceUri
      | top 10 by TotalCost desc
      
      // Cost by resource type
      Usage
      | where TimeGenerated > ago(7d)
      | summarize Cost = sum(Quantity * UnitPrice) by ResourceType
      | render piechart
    '''
    tags: [
      {
        name: 'Environment'
        value: environmentName
      }
      {
        name: 'Purpose'
        value: 'Cost Monitoring'
      }
    ]
  }
}

output workspaceId string = logAnalyticsWorkspace.id
output workspaceName string = logAnalyticsWorkspace.name
output customerId string = logAnalyticsWorkspace.properties.customerId
