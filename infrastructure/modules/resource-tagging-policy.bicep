// Resource Tagging Policy Module
// Creates policy for enforcing cost tracking tags

targetScope = 'subscription'

@description('Policy name')
param policyName string

@description('Environment name')
param environmentName string

@description('Required tags for cost tracking')
param requiredTags array

@description('Resource group name for policy scope')
param resourceGroupName string

resource tagPolicy 'Microsoft.Authorization/policyDefinitions@2021-06-01' = {
  name: policyName
  properties: {
    displayName: 'Vimarsh Cost Tracking Tags Policy - ${environmentName}'
    policyType: 'Custom'
    mode: 'Indexed'
    description: 'Enforces required tags for cost tracking and management in Vimarsh ${environmentName} environment'
    metadata: {
      category: 'Tags'
      environment: environmentName
    }
    policyRule: {
      if: {
        allOf: [
          {
            field: 'type'
            notEquals: 'Microsoft.Resources/resourceGroups'
          }
          {
            anyOf: [
              for tag in requiredTags: {
                field: 'tags[\'${tag}\']'
                exists: 'false'
              }
            ]
          }
        ]
      }
      then: {
        effect: 'deny'
      }
    }
    parameters: {}
  }
}

resource tagPolicyAssignment 'Microsoft.Authorization/policyAssignments@2022-06-01' = {
  name: '${policyName}-assignment'
  properties: {
    displayName: 'Vimarsh Cost Tags Assignment - ${environmentName}'
    policyDefinitionId: tagPolicy.id
    scope: '/subscriptions/${subscription().subscriptionId}/resourceGroups/${resourceGroupName}'
    enforcementMode: 'Default'
    description: 'Enforces cost tracking tags for Vimarsh ${environmentName} resources'
    metadata: {
      assignedBy: 'Infrastructure as Code'
    }
  }
}

output policyDefinitionId string = tagPolicy.id
output policyAssignmentId string = tagPolicyAssignment.id
