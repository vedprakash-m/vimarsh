// Vimarsh Unified Resources Template
// RESOURCE GROUP: vimarsh-rg (unified resource group for simplified management)
// PURPOSE: Contains all Vimarsh resources in a single resource group for easier management
// COST STRATEGY: Unified management while maintaining serverless and consumption-based pricing

@description('Location for all resources - single region deployment')
param location string = resourceGroup().location

@description('Gemini API key for LLM integration')
@secure()
param geminiApiKey string

@description('Expert review email for spiritual content validation')
param expertReviewEmail string = 'vedprakash.m@me.com'

// Resource names matching the migrated resources
var cosmosDbName = 'vimarsh-db'
var keyVaultName = 'vimarsh-kv-${uniqueString(resourceGroup().id)}'
var storageAccountName = 'vimarshstorage'
var functionAppName = 'vimarsh-backend-app'
var staticWebAppName = 'vimarsh-frontend'
var appInsightsName = 'vimarsh-backend-app' // Application Insights shares name with Function App
var hostingPlanName = 'EastUSLinuxDynamicPlan'

// Storage Account for Functions and general storage
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: 'Standard_LRS'  // Cost optimized
  }
  kind: 'StorageV2'
  properties: {
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    networkAcls: {
      defaultAction: 'Allow'
    }
  }
  tags: {
    project: 'vimarsh'
    purpose: 'functions-storage'
    costStrategy: 'unified'
  }
}

// Key Vault for secrets management
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  properties: {
    sku: {
      family: 'A'
      name: 'standard'  // Cost optimized
    }
    tenantId: subscription().tenantId
    accessPolicies: []
    enableRbacAuthorization: true
    publicNetworkAccess: 'Enabled'
    networkAcls: {
      defaultAction: 'Allow'
      bypass: 'AzureServices'
    }
  }
  tags: {
    project: 'vimarsh'
    purpose: 'secrets-management'
    costStrategy: 'unified'
  }
}

// Store Gemini API key in Key Vault
resource geminiApiKeySecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: keyVault
  name: 'GEMINI-API-KEY'
  properties: {
    value: geminiApiKey
    contentType: 'application/x-gemini-api-key'
  }
}

// Cosmos DB with Vector Search - Single Region for Cost Efficiency
resource cosmosDb 'Microsoft.DocumentDB/databaseAccounts@2023-04-15' = {
  name: cosmosDbName
  location: location
  kind: 'GlobalDocumentDB'
  properties: {
    databaseAccountOfferType: 'Standard'
    consistencyPolicy: {
      defaultConsistencyLevel: 'Session'
    }
    locations: [
      {
        locationName: location
        failoverPriority: 0
      }
    ]
    capabilities: [
      {
        name: 'EnableServerless'  // Cost optimization - pay per request
      }
    ]
    enableFreeTier: false
    publicNetworkAccess: 'Enabled'
    networkAclBypass: 'AzureServices'
  }
  tags: {
    project: 'vimarsh'
    purpose: 'data-storage'
    costStrategy: 'unified'
  }
}

// Vimarsh Database
resource vimarshDatabase 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2023-04-15' = {
  parent: cosmosDb
  name: 'vimarsh'
  properties: {
    resource: {
      id: 'vimarsh'
    }
  }
}

// Collections/Containers
resource conversationsContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-04-15' = {
  parent: vimarshDatabase
  name: 'conversations'
  properties: {
    resource: {
      id: 'conversations'
      partitionKey: {
        paths: ['/user_id']
        kind: 'Hash'
      }
      indexingPolicy: {
        indexingMode: 'consistent'
        includedPaths: [
          {
            path: '/*'
          }
        ]
      }
    }
  }
}

resource feedbackContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-04-15' = {
  parent: vimarshDatabase
  name: 'feedback'
  properties: {
    resource: {
      id: 'feedback'
      partitionKey: {
        paths: ['/conversation_id']
        kind: 'Hash'
      }
      indexingPolicy: {
        indexingMode: 'consistent'
        includedPaths: [
          {
            path: '/*'
          }
        ]
      }
    }
  }
}

resource spiritualContentContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-04-15' = {
  parent: vimarshDatabase
  name: 'spiritual_content'
  properties: {
    resource: {
      id: 'spiritual_content'
      partitionKey: {
        paths: ['/category']
        kind: 'Hash'
      }
      indexingPolicy: {
        indexingMode: 'consistent'
        includedPaths: [
          {
            path: '/*'
          }
        ]
      }
    }
  }
}

// Application Insights
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: 'eastus' // Matching existing location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    RetentionInDays: 30  // Cost optimization
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
  tags: {
    project: 'vimarsh'
    purpose: 'monitoring'
    costStrategy: 'unified'
  }
}

// Function App Hosting Plan (Consumption)
resource hostingPlan 'Microsoft.Web/serverfarms@2023-01-01' = {
  name: hostingPlanName
  location: 'eastus' // Matching existing location
  sku: {
    name: 'Y1'  // Consumption plan
    tier: 'Dynamic'
  }
  kind: 'functionapp'
  properties: {
    reserved: true  // Linux
  }
  tags: {
    project: 'vimarsh'
    purpose: 'functions-hosting'
    costStrategy: 'unified'
  }
}

// Azure Function App
resource functionApp 'Microsoft.Web/sites@2023-01-01' = {
  name: functionAppName
  location: 'eastus' // Matching existing location
  kind: 'functionapp,linux'
  properties: {
    serverFarmId: hostingPlan.id
    reserved: true
    siteConfig: {
      linuxFxVersion: 'Python|3.12'
      appSettings: [
        {
          name: 'AzureWebJobsStorage'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};AccountKey=${storageAccount.listKeys().keys[0].value};EndpointSuffix=core.windows.net'
        }
        {
          name: 'WEBSITE_CONTENTAZUREFILECONNECTIONSTRING'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};AccountKey=${storageAccount.listKeys().keys[0].value};EndpointSuffix=core.windows.net'
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
          name: 'APPINSIGHTS_INSTRUMENTATIONKEY'
          value: appInsights.properties.InstrumentationKey
        }
        {
          name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
          value: appInsights.properties.ConnectionString
        }
        {
          name: 'COSMOS_DB_ENDPOINT'
          value: cosmosDb.properties.documentEndpoint
        }
        {
          name: 'COSMOS_DB_KEY'
          value: cosmosDb.listKeys().primaryMasterKey
        }
        {
          name: 'KEY_VAULT_URL'
          value: keyVault.properties.vaultUri
        }
        {
          name: 'GEMINI_API_KEY'
          value: '@Microsoft.KeyVault(VaultName=${keyVault.name};SecretName=GEMINI-API-KEY)'
        }
        {
          name: 'EXPERT_REVIEW_EMAIL'
          value: expertReviewEmail
        }
      ]
      cors: {
        allowedOrigins: ['*']
        supportCredentials: false
      }
      use32BitWorkerProcess: false
      ftpsState: 'Disabled'
      minTlsVersion: '1.2'
    }
    httpsOnly: true
  }
  identity: {
    type: 'SystemAssigned'
  }
  tags: {
    project: 'vimarsh'
    purpose: 'backend-api'
    costStrategy: 'unified'
  }
}

// Static Web App
resource staticWebApp 'Microsoft.Web/staticSites@2023-01-01' = {
  name: staticWebAppName
  location: 'eastus2' // Matching existing location
  sku: {
    name: 'Free'  // Cost optimized
    tier: 'Free'
  }
  properties: {
    repositoryUrl: 'https://github.com/vedprakash-m/vimarsh'
    branch: 'main'
    buildProperties: {
      appLocation: '/frontend'
      outputLocation: 'build'
    }
  }
  tags: {
    project: 'vimarsh'
    purpose: 'frontend-app'
    costStrategy: 'unified'
  }
}

// Grant Function App access to Key Vault
resource keyVaultAccessPolicy 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(keyVault.id, functionApp.id, 'Key Vault Secrets User')
  scope: keyVault
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '4633458b-17de-408a-b874-0445c86b69e6') // Key Vault Secrets User
    principalId: functionApp.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

// Outputs
output storageAccountName string = storageAccount.name
output cosmosDbAccountName string = cosmosDb.name
output keyVaultName string = keyVault.name
output functionAppName string = functionApp.name
output staticWebAppName string = staticWebApp.name
output applicationInsightsName string = appInsights.name
output cosmosDbEndpoint string = cosmosDb.properties.documentEndpoint
output keyVaultUri string = keyVault.properties.vaultUri
