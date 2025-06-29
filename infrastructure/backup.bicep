// Vimarsh Backup and Disaster Recovery Infrastructure
// Comprehensive backup and recovery configuration for all Azure resources
// DEPLOYMENT STRATEGY: Single environment production for cost efficiency

@description('Location for all resources - single region deployment')
param location string = resourceGroup().location

@description('Project name for resource naming')
param projectName string = 'vimarsh'

@description('Recovery Services Vault name with static naming')
param recoveryVaultName string = '${projectName}-vault'

@description('Backup retention days for production environment')
param backupRetentionDays int = 365

@description('Geo-redundant backup storage for production reliability')
param storageType string = 'GeoRedundant'

// Variables for static resource naming
var resourceSuffix = projectName

// Recovery Services Vault for backup and disaster recovery
resource recoveryVault 'Microsoft.RecoveryServices/vaults@2023-04-01' = {
  name: recoveryVaultName
  location: location
  sku: {
    name: 'Standard'
  }
  properties: {
    encryption: {
      infrastructureEncryption: 'Enabled'
    }
    publicNetworkAccess: 'Disabled'
    securitySettings: {
      immutabilitySettings: {
        state: environment == 'prod' ? 'Locked' : 'Unlocked'
      }
    }
  }
  tags: {
    project: 'vimarsh'
    environment: environment
    component: 'backup'
  }
}

// Backup configuration for Recovery Services Vault
resource backupStorageConfig 'Microsoft.RecoveryServices/vaults/backupstorageconfig@2023-04-01' = {
  parent: recoveryVault
  name: 'vaultstorageconfig'
  properties: {
    storageModelType: storageType
    crossRegionRestoreFlag: environment == 'prod'
  }
}

// Backup Policy for Azure Storage Accounts
resource storageBackupPolicy 'Microsoft.RecoveryServices/vaults/backupPolicies@2023-04-01' = {
  parent: recoveryVault
  name: 'StorageBackupPolicy'
  properties: {
    backupManagementType: 'AzureStorage'
    retentionPolicy: {
      retentionPolicyType: 'LongTermRetentionPolicy'
      dailySchedule: {
        retentionTimes: ['2023-01-01T02:00:00Z']
        retentionDuration: {
          count: backupRetentionDays
          durationType: 'Days'
        }
      }
      weeklySchedule: {
        daysOfTheWeek: ['Sunday']
        retentionTimes: ['2023-01-01T02:00:00Z']
        retentionDuration: {
          count: environment == 'prod' ? 52 : 12
          durationType: 'Weeks'
        }
      }
      monthlySchedule: {
        retentionScheduleFormatType: 'Weekly'
        retentionScheduleWeekly: {
          daysOfTheWeek: ['Sunday']
          weeksOfTheMonth: ['First']
        }
        retentionTimes: ['2023-01-01T02:00:00Z']
        retentionDuration: {
          count: environment == 'prod' ? 12 : 6
          durationType: 'Months'
        }
      }
    }
    schedulePolicy: {
      schedulePolicyType: 'SimpleSchedulePolicy'
      scheduleRunFrequency: 'Daily'
      scheduleRunTimes: ['2023-01-01T02:00:00Z']
    }
  }
}

// Disaster Recovery Log Analytics Workspace
resource disasterRecoveryLogAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: '${resourceSuffix}-dr-logs'
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: environment == 'prod' ? 730 : 90
    features: {
      enableLogAccessUsingOnlyResourcePermissions: true
    }
  }
  tags: {
    project: 'vimarsh'
    environment: environment
    component: 'disaster-recovery'
  }
}

// Action Group for Disaster Recovery Alerts
resource drActionGroup 'Microsoft.Insights/actionGroups@2023-01-01' = {
  name: '${resourceSuffix}-dr-alerts'
  location: 'Global'
  properties: {
    groupShortName: 'VimDR'
    enabled: true
    emailReceivers: [
      {
        name: 'DR Team'
        emailAddress: 'disaster-recovery@vimarsh.app'
        useCommonAlertSchema: true
      }
    ]
    smsReceivers: []
    webhookReceivers: []
  }
  tags: {
    project: 'vimarsh'
    environment: environment
    component: 'disaster-recovery'
  }
}

// Backup Failure Alert Rule
resource backupFailureAlert 'Microsoft.Insights/metricAlerts@2018-03-01' = {
  name: '${resourceSuffix}-backup-failure'
  location: 'Global'
  properties: {
    description: 'Alert when backup operations fail'
    severity: 1
    enabled: true
    scopes: [
      recoveryVault.id
    ]
    evaluationFrequency: 'PT15M'
    windowSize: 'PT1H'
    criteria: {
      'odata.type': 'Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria'
      allOf: [
        {
          name: 'BackupFailure'
          criterionType: 'StaticThresholdCriterion'
          metricName: 'BackupJobFailedCount'
          operator: 'GreaterThan'
          threshold: 0
          timeAggregation: 'Total'
        }
      ]
    }
    actions: [
      {
        actionGroupId: drActionGroup.id
      }
    ]
  }
}

// Data Export Rule for Disaster Recovery Logs
resource dataExportRule 'Microsoft.OperationalInsights/workspaces/dataExports@2020-08-01' = {
  parent: disasterRecoveryLogAnalytics
  name: 'disaster-recovery-export'
  properties: {
    destination: {
      resourceId: recoveryVault.id
    }
    tableNames: [
      'AzureDiagnostics'
      'AzureActivity'
      'AzureMetrics'
    ]
    enable: true
  }
}

// Outputs
output recoveryVaultId string = recoveryVault.id
output recoveryVaultName string = recoveryVault.name
output backupPolicyId string = storageBackupPolicy.id
output drLogAnalyticsWorkspaceId string = disasterRecoveryLogAnalytics.id
output drActionGroupId string = drActionGroup.id
