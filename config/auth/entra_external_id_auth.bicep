
// Microsoft Entra External ID Authentication Configuration
// Uses existing VED tenant and VedID.onmicrosoft.com domain

param tenantId string = '${TENANT_ID}'
param clientId string = '${CLIENT_ID}'
param keyVaultName string = 'vimarsh-kv'

// Configure Static Web App authentication
resource staticWebApp 'Microsoft.Web/staticSites@2022-03-01' existing = {
  name: 'vimarsh-app'
}

resource staticWebAppAuthSettings 'Microsoft.Web/staticSites/config@2022-03-01' = {
  parent: staticWebApp
  name: 'authsettingsV2'
  properties: {
    platform: {
      enabled: true
      runtimeVersion: '~1'
    }
    globalValidation: {
      requireAuthentication: false
      unauthenticatedClientAction: 'AllowAnonymous'
    }
    identityProviders: {
      azureActiveDirectory: {
        enabled: true
        registration: {
          openIdIssuer: 'https://login.microsoftonline.com/${tenantId}/v2.0'
          clientId: clientId
          clientSecretSettingName: 'MICROSOFT_PROVIDER_AUTHENTICATION_SECRET'
        }
        validation: {
          allowedAudiences: [
            clientId
          ]
        }
      }
    }
    login: {
      routes: {
        logoutEndpoint: '/.auth/logout'
      }
      tokenStore: {
        enabled: true
        tokenRefreshExtensionHours: 72
      }
    }
  }
}

// Configure Function App authentication
resource functionApp 'Microsoft.Web/sites@2022-03-01' existing = {
  name: 'vimarsh-functions'
}

resource functionAppAuthSettings 'Microsoft.Web/sites/config@2022-03-01' = {
  parent: functionApp
  name: 'authsettingsV2'
  properties: {
    platform: {
      enabled: true
      runtimeVersion: '~1'
    }
    globalValidation: {
      requireAuthentication: true
      unauthenticatedClientAction: 'RedirectToLoginPage'
    }
    identityProviders: {
      azureActiveDirectory: {
        enabled: true
        registration: {
          openIdIssuer: 'https://login.microsoftonline.com/${tenantId}/v2.0'
          clientId: clientId
          clientSecretSettingName: 'MICROSOFT_PROVIDER_AUTHENTICATION_SECRET'
        }
        validation: {
          allowedAudiences: [
            clientId
          ]
        }
      }
    }
    login: {
      routes: {
        logoutEndpoint: '/.auth/logout'
      }
      tokenStore: {
        enabled: true
        tokenRefreshExtensionHours: 72
      }
    }
  }
}

// Store client secret in Key Vault
resource keyVault 'Microsoft.KeyVault/vaults@2021-11-01-preview' existing = {
  name: keyVaultName
}

resource clientSecretSecret 'Microsoft.KeyVault/vaults/secrets@2021-11-01-preview' = {
  parent: keyVault
  name: 'entra-client-secret'
  properties: {
    value: '${CLIENT_SECRET}' // To be replaced with actual secret
  }
}

output authConfiguration object = {
  tenantId: tenantId
  clientId: clientId
  authority: 'https://login.microsoftonline.com/${tenantId}'
  issuer: 'https://login.microsoftonline.com/${tenantId}/v2.0'
  jwksUri: 'https://login.microsoftonline.com/${tenantId}/discovery/v2.0/keys'
}
