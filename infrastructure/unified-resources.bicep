// Vimarsh Unified Resources Template
// RESOURCE GROUP: vimarsh-rg (unified resource group for simplified management)
// PURPOSE: Contains all Vimarsh resources in a single resource group for easier management
// COST STRATEGY: Unified management while maintaining serverless and consumption-based pricing

@description('Location for all resources - single region deployment')
param location string = resourceGroup().location

@description('Expert review email for spiritual content validation')
param expertReviewEmail string = 'vedprakash.m@me.com'

// Resource names matching the migrated resources
var cosmosDbName = 'vimarsh-db'
var keyVaultName = 'vimarsh-kv-${uniqueString(resourceGroup().id)}'
var storageAccountName = 'vimarshstorage'
var functionAppName = 'vimarsh-backend-app-flex'
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

// Store Cosmos DB key in Key Vault (never expose as plaintext app setting)
resource cosmosDbKeySecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: keyVault
  name: 'COSMOS-DB-KEY'
  properties: {
    value: cosmosDb.listKeys().primaryMasterKey
    contentType: 'application/x-cosmos-db-key'
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
  name: 'vimarsh-multi-personality'
  properties: {
    resource: {
      id: 'vimarsh-multi-personality'
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

// Personalities container - stores personality configurations
resource personalitiesContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-04-15' = {
  parent: vimarshDatabase
  name: 'personalities'
  properties: {
    resource: {
      id: 'personalities'
      partitionKey: {
        paths: ['/personality_id']
        kind: 'Hash'
      }
      indexingPolicy: {
        indexingMode: 'consistent'
        includedPaths: [{ path: '/*' }]
      }
    }
  }
}

// Personality vectors - stores embeddings for RAG
resource personalityVectorsContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-04-15' = {
  parent: vimarshDatabase
  name: 'personality_vectors'
  properties: {
    resource: {
      id: 'personality_vectors'
      partitionKey: {
        paths: ['/personality_id']
        kind: 'Hash'
      }
      indexingPolicy: {
        indexingMode: 'consistent'
        includedPaths: [{ path: '/*' }]
        excludedPaths: [{ path: '/embedding/*' }] // Don't index embeddings
      }
    }
  }
}

// Users container - stores user profiles
resource usersContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-04-15' = {
  parent: vimarshDatabase
  name: 'users'
  properties: {
    resource: {
      id: 'users'
      partitionKey: {
        paths: ['/user_id']
        kind: 'Hash'
      }
      indexingPolicy: {
        indexingMode: 'consistent'
        includedPaths: [{ path: '/*' }]
      }
    }
  }
}

// User preferences container
resource userPreferencesContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-04-15' = {
  parent: vimarshDatabase
  name: 'user_preferences'
  properties: {
    resource: {
      id: 'user_preferences'
      partitionKey: {
        paths: ['/user_id']
        kind: 'Hash'
      }
      indexingPolicy: {
        indexingMode: 'consistent'
        includedPaths: [{ path: '/*' }]
      }
    }
  }
}

// User sessions container
resource userSessionsContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-04-15' = {
  parent: vimarshDatabase
  name: 'user_sessions'
  properties: {
    resource: {
      id: 'user_sessions'
      partitionKey: {
        paths: ['/user_id']
        kind: 'Hash'
      }
      indexingPolicy: {
        indexingMode: 'consistent'
        includedPaths: [{ path: '/*' }]
      }
    }
  }
}

// User interactions container
resource userInteractionsContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-04-15' = {
  parent: vimarshDatabase
  name: 'user_interactions'
  properties: {
    resource: {
      id: 'user_interactions'
      partitionKey: {
        paths: ['/user_id']
        kind: 'Hash'
      }
      indexingPolicy: {
        indexingMode: 'consistent'
        includedPaths: [{ path: '/*' }]
      }
    }
  }
}

// User activity container
resource userActivityContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-04-15' = {
  parent: vimarshDatabase
  name: 'user_activity'
  properties: {
    resource: {
      id: 'user_activity'
      partitionKey: {
        paths: ['/user_id']
        kind: 'Hash'
      }
      indexingPolicy: {
        indexingMode: 'consistent'
        includedPaths: [{ path: '/*' }]
      }
    }
  }
}

// Notification subscriptions container
resource notificationSubscriptionsContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-04-15' = {
  parent: vimarshDatabase
  name: 'notification_subscriptions'
  properties: {
    resource: {
      id: 'notification_subscriptions'
      partitionKey: {
        paths: ['/user_id']
        kind: 'Hash'
      }
      indexingPolicy: {
        indexingMode: 'consistent'
        includedPaths: [{ path: '/*' }]
      }
    }
  }
}

// Token usage tracking container
resource tokenUsageContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-04-15' = {
  parent: vimarshDatabase
  name: 'token_usage'
  properties: {
    resource: {
      id: 'token_usage'
      partitionKey: {
        paths: ['/user_id']
        kind: 'Hash'
      }
      indexingPolicy: {
        indexingMode: 'consistent'
        includedPaths: [{ path: '/*' }]
      }
    }
  }
}

// User cost totals container
resource userCostTotalsContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-04-15' = {
  parent: vimarshDatabase
  name: 'user_cost_totals'
  properties: {
    resource: {
      id: 'user_cost_totals'
      partitionKey: {
        paths: ['/user_id']
        kind: 'Hash'
      }
      indexingPolicy: {
        indexingMode: 'consistent'
        includedPaths: [{ path: '/*' }]
      }
    }
  }
}

// Engagement tracking container
resource engagementTrackingContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-04-15' = {
  parent: vimarshDatabase
  name: 'engagement_tracking'
  properties: {
    resource: {
      id: 'engagement_tracking'
      partitionKey: {
        paths: ['/user_id']
        kind: 'Hash'
      }
      indexingPolicy: {
        indexingMode: 'consistent'
        includedPaths: [{ path: '/*' }]
      }
    }
  }
}

// Memory profiles container (hierarchical memory)
resource memoryProfilesContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-04-15' = {
  parent: vimarshDatabase
  name: 'memory_profiles'
  properties: {
    resource: {
      id: 'memory_profiles'
      partitionKey: {
        paths: ['/user_id']
        kind: 'Hash'
      }
      indexingPolicy: {
        indexingMode: 'consistent'
        includedPaths: [{ path: '/*' }]
      }
    }
  }
}

// Conversation history container (hierarchical memory)
resource conversationHistoryContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-04-15' = {
  parent: vimarshDatabase
  name: 'conversation_history'
  properties: {
    resource: {
      id: 'conversation_history'
      partitionKey: {
        paths: ['/user_id']
        kind: 'Hash'
      }
      indexingPolicy: {
        indexingMode: 'consistent'
        includedPaths: [{ path: '/*' }]
      }
    }
  }
}

// Relationship states container (hierarchical memory)
resource relationshipStatesContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-04-15' = {
  parent: vimarshDatabase
  name: 'relationship_states'
  properties: {
    resource: {
      id: 'relationship_states'
      partitionKey: {
        paths: ['/user_id']
        kind: 'Hash'
      }
      indexingPolicy: {
        indexingMode: 'consistent'
        includedPaths: [{ path: '/*' }]
      }
    }
  }
}

// Session summaries container (hierarchical memory)
resource sessionSummariesContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-04-15' = {
  parent: vimarshDatabase
  name: 'session_summaries'
  properties: {
    resource: {
      id: 'session_summaries'
      partitionKey: {
        paths: ['/user_id']
        kind: 'Hash'
      }
      indexingPolicy: {
        indexingMode: 'consistent'
        includedPaths: [{ path: '/*' }]
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
          value: '@Microsoft.KeyVault(VaultName=${keyVault.name};SecretName=COSMOS-DB-KEY)'
        }
        {
          name: 'KEY_VAULT_URL'
          value: keyVault.properties.vaultUri
        }
        {
          name: 'EXPERT_REVIEW_EMAIL'
          value: expertReviewEmail
        }
      ]
      cors: {
        allowedOrigins: [
          'https://vimarsh.vedmishra.com'
          'https://white-forest-05c196d0f.2.azurestaticapps.net'
        ]
        supportCredentials: true
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
