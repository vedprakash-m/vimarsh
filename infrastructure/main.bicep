// Vimarsh Infrastructure as Code Template
// DEPLOYMENT STRATEGY: Single environment (production), single region, single slot for cost efficiency
// RESOURCE ORGANIZATION: This template orchestrates deployment to two resource groups:
// - vimarsh-db-rg: Persistent resources (Cosmos DB, Key Vault, Storage) for data retention  
// - vimarsh-rg: Compute resources (Functions, Static Web App, App Insights) for pause-resume cost strategy

targetScope = 'subscription'

@description('Location for all resources - single region deployment for cost efficiency')
param location string = 'East US'

@description('Gemini API key for LLM integration')
@secure()
param geminiApiKey string

@description('Expert review email for spiritual content validation')
param expertReviewEmail string = 'vedprakash.m@me.com'

// Resource Group for Persistent Resources (Database, Secrets, Storage)
// This resource group contains data that must persist through deployment cycles
resource persistentResourceGroup 'Microsoft.Resources/resourceGroups@2023-07-01' = {
  name: 'vimarsh-db-rg'
  location: location
  tags: {
    project: 'vimarsh'
    type: 'persistent'
    purpose: 'data-retention'
    costCenter: 'production'
  }
}

// Resource Group for Compute Resources (Functions, Web App, Monitoring)
// This resource group can be deleted/recreated for cost savings while preserving data
resource computeResourceGroup 'Microsoft.Resources/resourceGroups@2023-07-01' = {
  name: 'vimarsh-rg'
  location: location
  tags: {
    project: 'vimarsh'
    type: 'compute'
    purpose: 'pause-resume-strategy'
    costCenter: 'production'
  }
}

// Deploy Persistent Resources (Cosmos DB, Key Vault, Storage)
module persistentResources 'persistent.bicep' = {
  name: 'vimarsh-persistent-deployment'
  scope: persistentResourceGroup
  params: {
    location: location
    geminiApiKey: geminiApiKey
  }
}

// Deploy Compute Resources (Functions, Static Web App, App Insights)
module computeResources 'compute.bicep' = {
  name: 'vimarsh-compute-deployment'
  scope: computeResourceGroup
  params: {
    location: location
    keyVaultUri: persistentResources.outputs.keyVaultUri
    keyVaultName: persistentResources.outputs.keyVaultName
    cosmosDbEndpoint: persistentResources.outputs.cosmosDbEndpoint
    expertReviewEmail: expertReviewEmail
  }
}

// Outputs for operational reference
output persistentResourceGroup string = persistentResourceGroup.name
output computeResourceGroup string = computeResourceGroup.name
output functionAppUrl string = computeResources.outputs.functionAppUrl
output staticWebAppUrl string = computeResources.outputs.staticWebAppUrl
output cosmosDbName string = persistentResources.outputs.cosmosDbName
output keyVaultName string = persistentResources.outputs.keyVaultName

// Deployment Strategy Documentation
// 
// PAUSE-RESUME COST STRATEGY:
// 1. To pause costs: Delete vimarsh-rg resource group (keeps data in vimarsh-db-rg)
// 2. To resume: Re-deploy this template (recreates compute resources, connects to existing data)
// 3. Data persistence: All user data, configurations, and content remain in vimarsh-db-rg
// 4. Cost savings: Only pay for storage costs during pause periods
//
// IDEMPOTENT DEPLOYMENTS:
// - All resource names are static (e.g., vimarsh-db, vimarsh-kv, vimarsh-functions)
// - No timestamp or random suffixes that create duplicates
// - Safe to re-deploy multiple times without resource conflicts
// - Consistent naming across all deployment cycles
