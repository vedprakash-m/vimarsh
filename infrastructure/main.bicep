// Vimarsh Infrastructure as Code Template
// Complete Azure infrastructure for spiritual guidance system

@description('Environment name (dev, staging, prod)')
@allowed(['dev', 'staging', 'prod'])
param environment string = 'dev'

@description('Location for all resources')
param location string = resourceGroup().location

@description('Application name prefix')
param appName string = 'vimarsh'

@description('Project name for resource naming')
param projectName string = 'vimarsh'

@description('Gemini API key for LLM integration')
@secure()
param geminiApiKey string

@description('Expert review email for spiritual content validation')
param expertReviewEmail string = 'experts@example.com'

// Variables
var resourceSuffix = '${projectName}-${environment}'
var functionAppName = '${resourceSuffix}-functions'
var cosmosDbName = '${resourceSuffix}-cosmos'
var staticWebAppName = '${resourceSuffix}-web'
var appInsightsName = '${resourceSuffix}-insights'
var storageAccountName = replace('${resourceSuffix}storage', '-', '')
var keyVaultName = '${resourceSuffix}-kv'

// Storage Account for Function App
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    encryption: {
      services: {
        blob: {
          enabled: true
        }
        file: {
          enabled: true
        }
      }
      keySource: 'Microsoft.Storage'
    }
  }
  tags: {
    project: 'vimarsh'
    environment: environment
    component: 'storage'
  }
}

// Application Insights for monitoring
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    Request_Source: 'rest'
    RetentionInDays: environment == 'prod' ? 90 : 30
    IngestionMode: 'ApplicationInsights'
  }
  tags: {
    project: 'vimarsh'
    environment: environment
    component: 'monitoring'
  }
}

// Key Vault for secrets management
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: tenant().tenantId
    accessPolicies: []
    enableRbacAuthorization: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 7
    enablePurgeProtection: false
  }
  tags: {
    project: 'vimarsh'
    environment: environment
    component: 'security'
  }
}

// Cosmos DB for vector storage and spiritual texts
resource cosmosDb 'Microsoft.DocumentDB/databaseAccounts@2023-11-15' = {
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
        isZoneRedundant: false
      }
    ]
    capabilities: [
      {
        name: 'EnableServerless'
      }
      {
        name: 'EnableVectorSearch'
      }
    ]
    backupPolicy: {
      type: 'Continuous'
      continuousModeProperties: {
        tier: 'Continuous7Days'
      }
    }
    encryption: {
      keySource: 'Microsoft.DocumentDB'
    }
    enableFreeTier: environment == 'dev'
  }
  tags: {
    project: 'vimarsh'
    environment: environment
    component: 'database'
  }
}

// Cosmos DB - Database
resource cosmosDatabase 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2023-11-15' = {
  parent: cosmosDb
  name: 'SpiritualGuidance'
  properties: {
    resource: {
      id: 'SpiritualGuidance'
    }
  }
}

// Cosmos DB - Documents Container
resource documentsContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-11-15' = {
  parent: cosmosDatabase
  name: 'Documents'
  properties: {
    resource: {
      id: 'Documents'
      partitionKey: {
        paths: ['/source']
        kind: 'Hash'
      }
      indexingPolicy: {
        indexingMode: 'consistent'
        includedPaths: [
          {
            path: '/*'
          }
        ]
        excludedPaths: [
          {
            path: '/vector/*'
          }
        ]
        vectorIndexes: [
          {
            path: '/vector'
            type: 'quantizedFlat'
          }
        ]
      }
    }
    options: environment == 'dev' ? {} : {
      throughput: 400
    }
  }
}

// Cosmos DB - Vectors Container
resource vectorsContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-11-15' = {
  parent: cosmosDatabase
  name: 'Vectors'
  properties: {
    resource: {
      id: 'Vectors'
      partitionKey: {
        paths: ['/document_id']
        kind: 'Hash'
      }
      indexingPolicy: {
        indexingMode: 'consistent'
        includedPaths: [
          {
            path: '/*'
          }
        ]
        vectorIndexes: [
          {
            path: '/embedding'
            type: 'quantizedFlat'
          }
        ]
      }
    }
    options: environment == 'dev' ? {} : {
      throughput: 400
    }
  }
}

// App Service Plan for Function App (Consumption Plan for cost optimization)
resource appServicePlan 'Microsoft.Web/serverfarms@2023-01-01' = {
  name: '${resourceSuffix}-plan'
  location: location
  sku: {
    name: environment == 'prod' ? 'P1V2' : 'Y1'  // Y1 = Consumption plan
    tier: environment == 'prod' ? 'PremiumV2' : 'Dynamic'  // Dynamic = Consumption tier
  }
  properties: {}
  tags: {
    project: 'vimarsh'
    environment: environment
    component: 'compute'
  }
}

// Function App for backend API
resource functionApp 'Microsoft.Web/sites@2023-01-01' = {
  name: functionAppName
  location: location
  kind: 'functionapp'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      appSettings: [
        {
          name: 'AzureWebJobsStorage'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};EndpointSuffix=${az.environment().suffixes.storage};AccountKey=${storageAccount.listKeys().keys[0].value}'
        }
        {
          name: 'WEBSITE_CONTENTAZUREFILECONNECTIONSTRING'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};EndpointSuffix=${az.environment().suffixes.storage};AccountKey=${storageAccount.listKeys().keys[0].value}'
        }
        {
          name: 'WEBSITE_CONTENTSHARE'
          value: toLower(functionAppName)
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
          name: 'GEMINI_API_KEY'
          value: geminiApiKey
        }
        {
          name: 'COSMOS_CONNECTION_STRING'
          value: cosmosDb.listConnectionStrings().connectionStrings[0].connectionString
        }
        {
          name: 'ENVIRONMENT'
          value: environment
        }
        {
          name: 'LOG_LEVEL'
          value: environment == 'prod' ? 'INFO' : 'DEBUG'
        }
        {
          name: 'EXPERT_REVIEW_EMAIL'
          value: expertReviewEmail
        }
        {
          name: 'MAX_QUERY_LENGTH'
          value: '1000'
        }
        {
          name: 'RESPONSE_TIMEOUT_SECONDS'
          value: '30'
        }
      ]
      pythonVersion: '3.12'
      use32BitWorkerProcess: false
      ftpsState: 'Disabled'
      minTlsVersion: '1.2'
      scmMinTlsVersion: '1.2'
      cors: {
        allowedOrigins: ['*']
        supportCredentials: false
      }
    }
    httpsOnly: true
    clientAffinityEnabled: false
  }
  tags: {
    project: 'vimarsh'
    environment: environment
    component: 'api'
  }
}

// Static Web App for frontend
resource staticWebApp 'Microsoft.Web/staticSites@2023-01-01' = {
  name: staticWebAppName
  location: location
  sku: {
    name: environment == 'prod' ? 'Standard' : 'Free'
    tier: environment == 'prod' ? 'Standard' : 'Free'
  }
  properties: {
    repositoryUrl: 'https://github.com/vedprakash-m/vimarsh'
    branch: 'main'
    buildProperties: {
      appLocation: '/frontend'
      outputLocation: '/frontend/build'
    }
    stagingEnvironmentPolicy: environment == 'prod' ? 'Enabled' : 'Disabled'
  }
  tags: {
    project: 'vimarsh'
    environment: environment
    component: 'frontend'
  }
}

// Log Analytics Workspace for advanced monitoring
resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' = if (environment == 'prod') {
  name: '${resourceSuffix}-logs'
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
    workspaceCapping: {
      dailyQuotaGb: 1
    }
  }
  tags: {
    project: 'vimarsh'
    environment: environment
    component: 'monitoring'
  }
}

// Action Group for alerts
resource actionGroup 'Microsoft.Insights/actionGroups@2023-01-01' = if (environment == 'prod') {
  name: '${resourceSuffix}-alerts'
  location: 'Global'
  properties: {
    groupShortName: 'vimarsh'
    enabled: true
    emailReceivers: [
      {
        name: 'Admin'
        emailAddress: expertReviewEmail
        useCommonAlertSchema: true
      }
    ]
  }
  tags: {
    project: 'vimarsh'
    environment: environment
    component: 'monitoring'
  }
}

// Metric Alert for Function App errors
resource errorAlert 'Microsoft.Insights/metricAlerts@2018-03-01' = if (environment == 'prod') {
  name: '${resourceSuffix}-error-alert'
  location: 'Global'
  properties: {
    description: 'Alert when Function App error rate is high'
    severity: 2
    enabled: true
    scopes: [functionApp.id]
    evaluationFrequency: 'PT1M'
    windowSize: 'PT5M'
    criteria: {
      'odata.type': 'Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria'
      allOf: [
        {
          name: 'HighErrorRate'
          metricName: 'Http5xx'
          operator: 'GreaterThan'
          threshold: 5
          timeAggregation: 'Total'
        }
      ]
    }
    actions: [
      {
        actionGroupId: actionGroup.id
      }
    ]
  }
  tags: {
    project: 'vimarsh'
    environment: environment
    component: 'monitoring'
  }
}

// RBAC for Function App to access Key Vault
resource keyVaultSecretsUser 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(keyVault.id, functionApp.id, 'Key Vault Secrets User')
  scope: keyVault
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '4633458b-17de-408a-b874-0445c86b69e6') // Key Vault Secrets User
    principalId: functionApp.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

// RBAC for Function App to access Cosmos DB
resource cosmosContributor 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(cosmosDb.id, functionApp.id, 'Cosmos DB Contributor')
  scope: cosmosDb
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '00000000-0000-0000-0000-000000000002') // Cosmos DB Contributor
    principalId: functionApp.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

// Outputs
output functionAppName string = functionApp.name
output functionAppUrl string = 'https://${functionApp.properties.defaultHostName}'
output staticWebAppName string = staticWebApp.name
output staticWebAppUrl string = 'https://${staticWebApp.properties.defaultHostname}'
output cosmosDbName string = cosmosDb.name
output appInsightsName string = appInsights.name
output keyVaultName string = keyVault.name
output resourceGroupName string = resourceGroup().name

// Outputs for configuration
output cosmosConnectionString string = cosmosDb.listConnectionStrings().connectionStrings[0].connectionString
output appInsightsInstrumentationKey string = appInsights.properties.InstrumentationKey
output appInsightsConnectionString string = appInsights.properties.ConnectionString
