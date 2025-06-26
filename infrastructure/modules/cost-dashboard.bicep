// Cost Dashboard Module
// Creates simple cost monitoring dashboard

@description('Dashboard name')
param dashboardName string

@description('Log Analytics workspace ID')
param workspaceId string

@description('Environment name')
param environmentName string

@description('Location')
param location string

resource costDashboard 'Microsoft.Portal/dashboards@2020-09-01-preview' = {
  name: dashboardName
  location: location
  properties: {
    lenses: [
      {
        order: 0
        parts: [
          {
            position: {
              x: 0
              y: 0
              rowSpan: 4
              colSpan: 6
            }
            metadata: {
              inputs: []
              type: 'Extension/HubsExtension/PartType/MarkdownPart'
              settings: {
                content: {
                  settings: {
                    content: '''
# Vimarsh Cost Management Dashboard - ${environmentName}

## 📊 Cost Monitoring Overview

This dashboard provides real-time cost monitoring and optimization insights for the Vimarsh AI Spiritual Guidance platform.

### Key Metrics
- **Daily Cost Tracking**: Monitor spending trends
- **Resource Cost Analysis**: Identify expensive resources  
- **Budget Alerts**: Stay within budget limits
- **Optimization Recommendations**: Reduce costs

### Quick Actions
- View detailed cost analytics in Log Analytics workspace
- Review budget alerts and notifications
- Access cost optimization recommendations
- Monitor resource usage patterns

### Spiritual Guidance
"Just as a wise person manages their household expenses with care and mindfulness, we must monitor our cloud resources with the same dharmic principles of stewardship and responsibility." - Inspired by Bhagavad Gita teachings on resource management

---
**Workspace ID**: ${workspaceId}
**Environment**: ${environmentName}
**Last Updated**: Today
                    '''
                    title: 'Vimarsh Cost Management'
                    subtitle: 'Real-time cost monitoring and optimization'
                  }
                }
              }
            }
          }
        ]
      }
    ]
    metadata: {
      model: {
        timeRange: {
          value: {
            relative: {
              duration: 24
              timeUnit: 1
            }
          }
          type: 'MsPortalFx.Composition.Configuration.ValueTypes.TimeRange'
        }
      }
    }
  }
  tags: {
    Environment: environmentName
    Purpose: 'Cost Monitoring Dashboard'
    CostCenter: 'Engineering'
  }
}

output dashboardId string = costDashboard.id
output dashboardName string = costDashboard.name
