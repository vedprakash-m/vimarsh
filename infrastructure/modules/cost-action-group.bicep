// Cost Management Action Group Module
// Creates action group for cost alerts and notifications

@description('Action group name')
param actionGroupName string

@description('Short name for action group')
param shortName string

@description('Email addresses for notifications')
param emailAddresses array

@description('Environment name')
param environmentName string

@description('Location')
param location string

resource actionGroup 'Microsoft.Insights/actionGroups@2023-01-01' = {
  name: actionGroupName
  location: 'global'
  tags: {
    Environment: environmentName
    Purpose: 'Cost Management Alerts'
  }
  properties: {
    groupShortName: shortName
    enabled: true
    emailReceivers: [for (email, i) in emailAddresses: {
      name: 'Email${i}'
      emailAddress: email
      useCommonAlertSchema: true
    }]
    armRoleReceivers: [
      {
        name: 'OwnerRole'
        roleId: '8e3af657-a8ff-443c-a75c-2fe8c4bcb635' // Owner role
        useCommonAlertSchema: true
      }
      {
        name: 'ContributorRole'
        roleId: 'b24988ac-6180-42a0-ab88-20f7382dd24c' // Contributor role
        useCommonAlertSchema: true
      }
    ]
    webhookReceivers: []
    smsReceivers: []
    azureAppPushReceivers: []
    itsmReceivers: []
    azureFunctionReceivers: []
    logicAppReceivers: []
    automationRunbookReceivers: []
    voiceReceivers: []
    eventHubReceivers: []
  }
}

output actionGroupId string = actionGroup.id
output actionGroupName string = actionGroup.name
