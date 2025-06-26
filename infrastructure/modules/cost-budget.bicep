// Cost Budget Module
// Creates budget with multiple alert thresholds

targetScope = 'subscription'

@description('Budget name')
param budgetName string

@description('Budget amount in USD')
param budgetAmount int

@description('Alert thresholds (percentages)')
param thresholds array = [50, 80, 90, 100]

@description('Action group resource ID for notifications')
param actionGroupId string

@description('Environment name')
param environmentName string

@description('Resource group name for scoping')
param resourceGroupName string

@description('Start date for budget (YYYY-MM-DD format)')
param startDate string = '2024-01-01'

@description('End date for budget (YYYY-MM-DD format)')
param endDate string = '2024-12-31'

resource budget 'Microsoft.Consumption/budgets@2023-05-01' = {
  name: budgetName
  properties: {
    timePeriod: {
      startDate: startDate
      endDate: endDate
    }
    timeGrain: 'Monthly'
    amount: budgetAmount
    category: 'Cost'
    notifications: {
      Alert50Percent: {
        enabled: true
        operator: 'GreaterThan'
        threshold: 50
        contactEmails: []
        contactRoles: [
          'Owner'
          'Contributor'
        ]
        contactGroups: [
          actionGroupId
        ]
        thresholdType: 'Actual'
      }
      Alert80Percent: {
        enabled: true
        operator: 'GreaterThan'
        threshold: 80
        contactEmails: []
        contactRoles: [
          'Owner'
          'Contributor'
        ]
        contactGroups: [
          actionGroupId
        ]
        thresholdType: 'Actual'
      }
      Alert90Percent: {
        enabled: true
        operator: 'GreaterThan'
        threshold: 90
        contactEmails: []
        contactRoles: [
          'Owner'
          'Contributor'
        ]
        contactGroups: [
          actionGroupId
        ]
        thresholdType: 'Actual'
      }
      Alert100Percent: {
        enabled: true
        operator: 'GreaterThan'
        threshold: 100
        contactEmails: []
        contactRoles: [
          'Owner'
          'Contributor'
        ]
        contactGroups: [
          actionGroupId
        ]
        thresholdType: 'Forecast'
      }
    }
    filter: {
      dimensions: {
        name: 'ResourceGroupName'
        operator: 'In'
        values: [
          resourceGroupName
        ]
      }
    }
  }
}

output budgetId string = budget.id
output budgetName string = budget.name
