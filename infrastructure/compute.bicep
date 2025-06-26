// Vimarsh Compute Resources Template  
// RESOURCE GROUP: vimarsh-rg (compute/ephemeral resources for pause-resume strategy)
// PURPOSE: Contains all compute resources that can be deleted/recreated for cost savings
// COST STRATEGY: Delete this entire resource group to pause costs, redeploy to resume
// NAMING: Static, minimal names for idempotent deployments (vimarsh-functions, vimarsh-web, etc.)

@description('Location for all compute resources - single region deployment')
param location string = resourceGroup().location

@description('URI of the Key Vault containing secrets')
param keyVaultUri string

@description('Name of the Key Vault')
param keyVaultName string

@description('Cosmos DB endpoint')
param cosmosDbEndpoint string

@description('Expert review email for spiritual content validation')
param expertReviewEmail string = 'vedprakash.m@me.com'

// Static resource names for idempotent deployments - no duplicates
var functionAppName = 'vimarsh-functions'
var staticWebAppName = 'vimarsh-web'
var appInsightsName = 'vimarsh-insights'
var hostingPlanName = 'vimarsh-plan'

// Application Insights
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    RetentionInDays: 30  // Cost optimization
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
  tags: {
    project: 'vimarsh'
    type: 'compute'
    purpose: 'monitoring'
    costStrategy: 'pause-resume'
  }
}

// Function App Hosting Plan (Consumption)
resource hostingPlan 'Microsoft.Web/serverfarms@2023-01-01' = {
  name: hostingPlanName
  location: location
  sku: {
    name: 'Y1'
    tier: 'Dynamic'
  }
  kind: 'functionapp'
  properties: {
    reserved: true  // Linux
  }
  tags: {
    project: 'vimarsh'
    type: 'compute'
    purpose: 'hosting-plan'
    costStrategy: 'consumption-based'
  }
}

// Function App
resource functionApp 'Microsoft.Web/sites@2023-01-01' = {
  name: functionAppName
  location: location
  kind: 'functionapp,linux'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: hostingPlan.id
    reserved: true
    siteConfig: {
      linuxFxVersion: 'Python|3.11'
      pythonVersion: '3.11'
      appSettings: [
        {
          name: 'AzureWebJobsStorage'
          value: '@Microsoft.KeyVault(SecretUri=${keyVaultUri}secrets/storage-connection-string)'
        }
        {
          name: 'WEBSITE_CONTENTAZUREFILECONNECTIONSTRING'
          value: '@Microsoft.KeyVault(SecretUri=${keyVaultUri}secrets/storage-connection-string)'
        }
        {
          name: 'WEBSITE_CONTENTSHARE'
          value: functionAppName
        }
        {
          name: 'FUNCTIONS_EXTENSION_VERSION'
          value: '~4'
        }
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'python'
        }
        {
          name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
          value: appInsights.properties.ConnectionString
        }
        {
          name: 'GEMINI_API_KEY'
          value: '@Microsoft.KeyVault(SecretUri=${keyVaultUri}secrets/gemini-api-key)'
        }
        {
          name: 'COSMOS_DB_ENDPOINT'
          value: cosmosDbEndpoint
        }
        {
          name: 'COSMOS_DB_KEY'
          value: '@Microsoft.KeyVault(SecretUri=${keyVaultUri}secrets/cosmos-db-key)'
        }
        {
          name: 'EXPERT_REVIEW_EMAIL'
          value: expertReviewEmail
        }
        {
          name: 'AZURE_FUNCTIONS_ENVIRONMENT'
          value: 'production'
        }
        {
          name: 'WEBSITE_RUN_FROM_PACKAGE'
          value: '1'
        }
      ]
      cors: {
        allowedOrigins: [
          'https://${staticWebAppName}.azurestaticapps.net'
          'http://localhost:3000'  // Local development
        ]
        supportCredentials: false
      }
      ftpsState: 'Disabled'
      minTlsVersion: '1.2'
      http20Enabled: true
      use32BitWorkerProcess: false
    }
    httpsOnly: true
  }
  tags: {
    project: 'vimarsh'
    type: 'compute'
    purpose: 'backend-api'
    costStrategy: 'serverless-functions'
  }
}

// Grant Function App access to Key Vault
resource keyVaultAccess 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(functionApp.id, keyVaultName, 'Key Vault Secrets User')
  scope: resourceGroup()
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '4633458b-17de-408a-b874-0445c86b69e6') // Key Vault Secrets User
    principalId: functionApp.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

// Static Web App
resource staticWebApp 'Microsoft.Web/staticSites@2023-01-01' = {
  name: staticWebAppName
  location: location
  sku: {
    name: 'Free'  // Cost-effective for beta testing
    tier: 'Free'
  }
  properties: {
    buildProperties: {
      appLocation: '/frontend'
      apiLocation: ''  // Using separate Function App
      outputLocation: 'build'
    }
    repositoryUrl: 'https://github.com/vedprakash-m/vimarsh'
    branch: 'main'
    stagingEnvironmentPolicy: 'Enabled'
  }
  tags: {
    project: 'vimarsh'
    type: 'compute'
    purpose: 'frontend-hosting'
    costStrategy: 'free-tier'
  }
}

// Configure Static Web App settings
resource staticWebAppSettings 'Microsoft.Web/staticSites/config@2023-01-01' = {
  parent: staticWebApp
  name: 'appsettings'
  properties: {
    REACT_APP_API_BASE_URL: 'https://${functionApp.properties.defaultHostName}/api'
    REACT_APP_APP_INSIGHTS_CONNECTION_STRING: appInsights.properties.ConnectionString
    REACT_APP_ENVIRONMENT: 'production'
  }
}

// Budget Alert for Cost Management - Single Environment Production
resource budget 'Microsoft.Consumption/budgets@2023-05-01' = {
  name: 'vimarsh-production-budget'
  properties: {
    timePeriod: {
      startDate: '2024-01-01'
      endDate: '2025-12-31'
    }
    timeGrain: 'Monthly'
    amount: 100  // $100 monthly budget for production deployment
    category: 'Cost'
    notifications: {
      actual_GreaterThan_80_Percent: {
        enabled: true
        operator: 'GreaterThan'
        threshold: 80
        contactEmails: [
          expertReviewEmail
        ]
        contactRoles: []
      }
      forecast_GreaterThan_100_Percent: {
        enabled: true
        operator: 'GreaterThan'
        threshold: 100
        contactEmails: [
          expertReviewEmail
        ]
        contactRoles: []
      }
    }
  }
}

// Outputs
output functionAppName string = functionApp.name
output functionAppUrl string = 'https://${functionApp.properties.defaultHostName}'
output staticWebAppName string = staticWebApp.name
output staticWebAppUrl string = 'https://${staticWebApp.properties.defaultHostname}'
output appInsightsConnectionString string = appInsights.properties.ConnectionString
output appInsightsName string = appInsights.name
