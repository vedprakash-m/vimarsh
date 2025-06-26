// Cost Optimization Advisor Module
// Creates advisor recommendations for cost optimization

@description('Advisor name')
param advisorName string

@description('Environment name')
param environmentName string

@description('Location')
param location string

resource costOptimizationWorkbook 'Microsoft.Insights/workbooks@2023-06-01' = {
  name: guid(advisorName)
  location: location
  kind: 'shared'
  properties: {
    displayName: advisorName
    serializedData: '''
    {
      "version": "Notebook/1.0",
      "items": [
        {
          "type": 1,
          "content": {
            "json": "# Vimarsh Cost Optimization Dashboard\\n\\nThis dashboard provides cost optimization recommendations for the ${environmentName} environment."
          }
        },
        {
          "type": 3,
          "content": {
            "version": "KqlItem/1.0",
            "query": "Usage\\n| where TimeGenerated > ago(30d)\\n| summarize TotalCost = sum(Quantity * UnitPrice) by ResourceId\\n| top 10 by TotalCost desc",
            "size": 0,
            "title": "Top 10 Most Expensive Resources (Last 30 Days)",
            "queryType": 0,
            "visualization": "barchart"
          }
        },
        {
          "type": 3,
          "content": {
            "version": "KqlItem/1.0",
            "query": "Usage\\n| where TimeGenerated > ago(7d)\\n| summarize Cost = sum(Quantity * UnitPrice) by bin(TimeGenerated, 1d)\\n| render timechart",
            "size": 0,
            "title": "Daily Cost Trend (Last 7 Days)",
            "queryType": 0,
            "visualization": "timechart"
          }
        }
      ]
    }
    '''
    category: 'workbook'
    tags: {
      Environment: environmentName
      Purpose: 'Cost Optimization'
    }
  }
}

output workbookId string = costOptimizationWorkbook.id
output workbookName string = costOptimizationWorkbook.name
