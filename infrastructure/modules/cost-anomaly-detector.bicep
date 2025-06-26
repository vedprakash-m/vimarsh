// Cost Anomaly Detector Module
// Creates anomaly detection for unusual spending patterns

targetScope = 'subscription'

@description('Anomaly detector name')
param detectorName string

@description('Action group resource ID for notifications')
param actionGroupId string

@description('Environment name')
param environmentName string

@description('Resource group name for scoping')
param resourceGroupName string

resource costAnomalyDetector 'Microsoft.CostManagement/scheduledActions@2023-11-01' = {
  name: detectorName
  properties: {
    displayName: detectorName
    fileDestination: {
      fileFormats: [
        'Csv'
      ]
    }
    notification: {
      to: [
        'admin@vimarsh.ai'
      ]
      language: 'en'
      message: 'Cost anomaly detected for Vimarsh ${environmentName} environment'
      regionalFormat: 'en'
      subject: 'Vimarsh Cost Anomaly Alert - ${environmentName}'
    }
    schedule: {
      frequency: 'Daily'
      hourOfDay: 8
      daysOfWeek: [
        'Monday'
        'Tuesday'
        'Wednesday'
        'Thursday'
        'Friday'
      ]
      weeksOfMonth: []
    }
    scope: '/subscriptions/${subscription().subscriptionId}/resourceGroups/${resourceGroupName}'
    status: 'Enabled'
    viewId: '/subscriptions/${subscription().subscriptionId}/providers/Microsoft.CostManagement/views/AccumulatedCosts'
  }
}

output detectorId string = costAnomalyDetector.id
output detectorName string = costAnomalyDetector.name
