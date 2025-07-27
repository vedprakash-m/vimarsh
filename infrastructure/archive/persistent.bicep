// Vimarsh Persistent Resources Template
// RESOURCE GROUP: vimarsh-db-rg (persistent resources for data retention)
// PURPOSE: Contains all data and secrets that must persist through deployment cycles
// COST STRATEGY: These resources provide foundational data storage and remain active
// NAMING: Static, minimal names for idempotent deployments (vimarsh-db, vimarsh-kv, etc.)

@description('Location for all persistent resources - single region deployment')
param location string = resourceGroup().location

@description('Gemini API key for LLM integration')
@secure()
param geminiApiKey string

// Static resource names for idempotent deployments - no duplicates
var cosmosDbName = 'vimarsh-db'
var keyVaultName = 'vimarsh-kv-${uniqueString(resourceGroup().id)}'
var storageAccountName = 'vimarshstorage'

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
    enableFreeTier: false  // Disabled to avoid conflicts in production
    publicNetworkAccess: 'Enabled'
    networkAclBypass: 'AzureServices'
  }
  tags: {
    project: 'vimarsh'
    type: 'persistent'
    purpose: 'data-retention'
    costStrategy: 'serverless-pricing'
  }
}

// Cosmos DB Database
resource database 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2023-04-15' = {
  parent: cosmosDb
  name: 'vimarsh'
  properties: {
    resource: {
      id: 'vimarsh'
    }
  }
}

// Spiritual Texts Container with Vector Search
resource spiritualTextsContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-04-15' = {
  parent: database
  name: 'spiritual-texts'
  properties: {
    resource: {
      id: 'spiritual-texts'
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
            path: '/embedding/*'
          }
        ]
      }
    }
  }
}

// Conversations Container
resource conversationsContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-04-15' = {
  parent: database
  name: 'conversations'
  properties: {
    resource: {
      id: 'conversations'
      partitionKey: {
        paths: ['/userId']
        kind: 'Hash'
      }
    }
  }
}

// Key Vault for Secrets
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  properties: {
    tenantId: subscription().tenantId
    sku: {
      family: 'A'
      name: 'standard'
    }
    enabledForDeployment: false
    enabledForTemplateDeployment: true
    enabledForDiskEncryption: false
    enableRbacAuthorization: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 7  // Minimum for cost savings
    enablePurgeProtection: true  // Required by Azure policy
    accessPolicies: []
  }
  tags: {
    project: 'vimarsh'
    type: 'persistent'
    purpose: 'secrets-management'
    costStrategy: 'minimal-retention'
  }
}

// Store Gemini API Key in Key Vault
resource geminiApiKeySecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: keyVault
  name: 'gemini-api-key'
  properties: {
    value: geminiApiKey
    contentType: 'text/plain'
  }
}

// Storage Account for Persistent Data
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: 'Standard_LRS'  // Cost-effective for beta testing
  }
  kind: 'StorageV2'
  properties: {
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    accessTier: 'Cool'  // Cost optimization for infrequent access
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
    type: 'persistent'
    purpose: 'data-storage'
    costStrategy: 'cool-storage-tier'
  }
}

// Blob Container for Spiritual Content
resource spiritualContentContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  name: '${storageAccount.name}/default/spiritual-content'
  properties: {
    publicAccess: 'None'
  }
}

// Blob Container for Audio Responses (Future)
resource audioContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  name: '${storageAccount.name}/default/audio-responses'
  properties: {
    publicAccess: 'None'
  }
}

// Outputs for compute template (non-sensitive values only)
output cosmosDbEndpoint string = cosmosDb.properties.documentEndpoint
output keyVaultUri string = keyVault.properties.vaultUri
output keyVaultName string = keyVault.name
output storageAccountName string = storageAccount.name
output cosmosDbName string = cosmosDb.name
