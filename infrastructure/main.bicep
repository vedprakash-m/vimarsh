// Vimarsh Infrastructure as Code Template - Unified Resource Group
// DEPLOYMENT STRATEGY: Single environment (production), single region, single unified resource group for simplified management
// RESOURCE ORGANIZATION: All resources deployed to vimarsh-rg for unified management and easier maintenance

targetScope = 'subscription'

@description('Location for all resources - single region deployment for cost efficiency')
param location string = 'West US 2'

@description('Gemini API key for LLM integration')
@secure()
param geminiApiKey string

@description('Expert review email for spiritual content validation')
param expertReviewEmail string = 'vedprakash.m@me.com'

// Unified Resource Group for All Resources
// This resource group contains all Vimarsh resources for simplified management
resource vimarshResourceGroup 'Microsoft.Resources/resourceGroups@2023-07-01' = {
  name: 'vimarsh-rg'
  location: location
  tags: {
    project: 'vimarsh'
    costStrategy: 'unified'
    environment: 'production'
    purpose: 'spiritual-guidance-platform'
  }
}

// Deploy All Vimarsh Resources in Unified Resource Group
module vimarshResources 'unified-resources.bicep' = {
  name: 'vimarsh-unified-deployment'
  scope: vimarshResourceGroup
  params: {
    location: location
    geminiApiKey: geminiApiKey
    expertReviewEmail: expertReviewEmail
  }
}

// Outputs for application configuration
output resourceGroupName string = vimarshResourceGroup.name
output storageAccountName string = vimarshResources.outputs.storageAccountName
output cosmosDbAccountName string = vimarshResources.outputs.cosmosDbAccountName
output keyVaultName string = vimarshResources.outputs.keyVaultName
output functionAppName string = vimarshResources.outputs.functionAppName
output staticWebAppName string = vimarshResources.outputs.staticWebAppName
output applicationInsightsName string = vimarshResources.outputs.applicationInsightsName
