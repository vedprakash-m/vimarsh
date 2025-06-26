// Vimarsh Cost Management and Budget Monitoring Infrastructure
// Comprehensive cost optimization, budget alerts, and resource monitoring

targetScope = 'subscription'

@description('Environment name (dev, staging, prod)')
param environmentName string = 'dev'

@description('Resource group name for cost management resources')
param resourceGroupName string = 'vimarsh-${environmentName}-cost-mgmt'

@description('Location for cost management resources')
param location string = 'East US'

@description('Monthly budget amount in USD')
param monthlyBudgetAmount int = 100

@description('Budget alert thresholds (percentages)')
param budgetThresholds array = [50, 80, 90, 100]

@description('Email addresses for budget alerts')
param alertEmailAddresses array = ['admin@vimarsh.ai']

@description('Project name for tagging')
param projectName string = 'Vimarsh'

@description('Owner contact for resource management')
param ownerContact string = 'DevOps Team'

// Create resource group for cost management
resource costMgmtResourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: resourceGroupName
  location: location
  tags: {
    Project: projectName
    Environment: environmentName
    Purpose: 'Cost Management and Monitoring'
    Owner: ownerContact
    CostCenter: 'Engineering'
    CreatedBy: 'Infrastructure-as-Code'
  }
}

// Cost management action group for notifications
module costActionGroup 'modules/cost-action-group.bicep' = {
  name: 'vimarsh-cost-action-group'
  scope: costMgmtResourceGroup
  params: {
    actionGroupName: 'vimarsh-${environmentName}-cost-alerts'
    shortName: 'CostAlert'
    emailAddresses: alertEmailAddresses
    environmentName: environmentName
    location: location
  }
}

// Monthly budget with multiple alert thresholds
module monthlyBudget 'modules/cost-budget.bicep' = {
  name: 'vimarsh-monthly-budget'
  params: {
    budgetName: 'vimarsh-${environmentName}-monthly-budget'
    budgetAmount: monthlyBudgetAmount
    thresholds: budgetThresholds
    actionGroupId: costActionGroup.outputs.actionGroupId
    environmentName: environmentName
    resourceGroupName: resourceGroupName
  }
}

// Cost anomaly detector
module costAnomalyDetector 'modules/cost-anomaly-detector.bicep' = {
  name: 'vimarsh-cost-anomaly-detector'
  params: {
    detectorName: 'vimarsh-${environmentName}-anomaly-detector'
    actionGroupId: costActionGroup.outputs.actionGroupId
    environmentName: environmentName
    resourceGroupName: resourceGroupName
  }
}

// Cost optimization advisor
module costOptimizationAdvisor 'modules/cost-optimization-advisor.bicep' = {
  name: 'vimarsh-cost-optimization'
  scope: costMgmtResourceGroup
  params: {
    advisorName: 'vimarsh-${environmentName}-cost-advisor'
    environmentName: environmentName
    location: location
  }
}

// Resource tagging policy for cost tracking
module resourceTaggingPolicy 'modules/resource-tagging-policy.bicep' = {
  name: 'vimarsh-resource-tagging-policy'
  params: {
    policyName: 'vimarsh-${environmentName}-cost-tagging'
    environmentName: environmentName
    requiredTags: [
      'Project'
      'Environment'
      'Owner'
      'CostCenter'
      'Purpose'
    ]
    resourceGroupName: resourceGroupName
  }
}

// Log Analytics workspace for cost analysis
module costAnalyticsWorkspace 'modules/cost-analytics-workspace.bicep' = {
  name: 'vimarsh-cost-analytics-workspace'
  scope: costMgmtResourceGroup
  params: {
    workspaceName: 'vimarsh-${environmentName}-cost-analytics'
    location: location
    environmentName: environmentName
    retentionInDays: 90
  }
}

// Cost dashboard and visualizations
module costDashboard 'modules/cost-dashboard.bicep' = {
  name: 'vimarsh-cost-dashboard'
  scope: costMgmtResourceGroup
  params: {
    dashboardName: 'vimarsh-${environmentName}-cost-dashboard'
    workspaceId: costAnalyticsWorkspace.outputs.workspaceId
    environmentName: environmentName
    location: location
  }
}

// Outputs for integration with other systems
output costManagementResourceGroupId string = costMgmtResourceGroup.id
output budgetId string = monthlyBudget.outputs.budgetId
output actionGroupId string = costActionGroup.outputs.actionGroupId
output anomalyDetectorId string = costAnomalyDetector.outputs.detectorId
output costAnalyticsWorkspaceId string = costAnalyticsWorkspace.outputs.workspaceId
output costDashboardId string = costDashboard.outputs.dashboardId

output costManagementConfig object = {
  resourceGroupName: resourceGroupName
  budgetAmount: monthlyBudgetAmount
  thresholds: budgetThresholds
  alertEmails: alertEmailAddresses
  environment: environmentName
  location: location
}
