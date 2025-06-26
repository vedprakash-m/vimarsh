# Vimarsh Deployment Guide

## Overview

This guide documents the deployment and operational procedures for Vimarsh's innovative two-resource-group architecture, designed for maximum cost efficiency through pause-resume operations.

## Architecture Summary

### Resource Group Strategy

**vimarsh-db-rg (Persistent Resources)**
- **Purpose**: Data retention and persistence
- **Lifecycle**: Always active, never deleted
- **Monthly Cost**: $5-10 (storage only)
- **Resources**:
  - `vimarsh-db` - Cosmos DB with spiritual texts and user data
  - `vimarsh-kv` - Key Vault with API keys and secrets
  - `vimarshstorage` - Storage Account for content and media

**vimarsh-rg (Compute Resources)**
- **Purpose**: Application execution and user interaction
- **Lifecycle**: Create for active service, delete for cost savings
- **Monthly Cost**: $45-90 (compute and hosting)
- **Resources**:
  - `vimarsh-functions` - Function App for backend API
  - `vimarsh-web` - Static Web App for frontend
  - `vimarsh-insights` - Application Insights for monitoring

## Deployment Procedures

### Initial Production Deployment

```bash
# 1. Deploy both resource groups and all resources
az deployment sub create \
  --location "East US" \
  --template-file infrastructure/main.bicep \
  --parameters geminiApiKey="<api-key>" expertReviewEmail="<email>"

# 2. Verify deployment
az group list --query "[?contains(name, 'vimarsh')].{Name:name, Location:location, State:properties.provisioningState}"

# 3. Test connectivity between resource groups
az functionapp show --name vimarsh-functions --resource-group vimarsh-rg
az cosmosdb show --name vimarsh-db --resource-group vimarsh-db-rg
```

### Pause Operation (Cost Savings)

```bash
# 1. Notify users of planned maintenance (48 hours advance notice recommended)
# 2. Delete compute resource group (preserves all data)
az group delete --name vimarsh-rg --yes --no-wait

# 3. Verify compute resources deleted while data preserved
az group exists --name vimarsh-rg        # Should return false
az group exists --name vimarsh-db-rg     # Should return true

# 4. Confirm data preservation
az cosmosdb show --name vimarsh-db --resource-group vimarsh-db-rg
az keyvault show --name vimarsh-kv --resource-group vimarsh-db-rg
```

### Resume Operation (Service Restoration)

```bash
# 1. Recreate compute resource group and resources
az deployment sub create \
  --location "East US" \
  --template-file infrastructure/main.bicep \
  --parameters geminiApiKey="<api-key>" expertReviewEmail="<email>"

# 2. Verify service restoration (<10 minutes typical)
az functionapp show --name vimarsh-functions --resource-group vimarsh-rg --query "state"
az staticwebapp show --name vimarsh-web --resource-group vimarsh-rg --query "buildProperties"

# 3. Test end-to-end functionality
curl https://vimarsh-functions.azurewebsites.net/api/health
curl https://vimarsh-web.azurestaticapps.net

# 4. Notify users of service restoration
```

## Cost Monitoring

### Active Production Costs

```bash
# Monitor monthly costs by resource group
az consumption budget list --scope "/subscriptions/{subscription-id}/resourceGroups/vimarsh-rg"
az consumption budget list --scope "/subscriptions/{subscription-id}/resourceGroups/vimarsh-db-rg"

# Expected cost ranges:
# vimarsh-rg (active): $45-90/month
# vimarsh-db-rg (always): $5-10/month
```

### Pause State Verification

```bash
# Verify only storage costs during pause
az consumption usage list --start-date 2024-01-01 --end-date 2024-01-31 \
  --scope "/subscriptions/{subscription-id}/resourceGroups/vimarsh-db-rg"

# Expected pause state: $5-10/month total
```

## Operational Procedures

### Daily Monitoring

```bash
# Check service health
az functionapp show --name vimarsh-functions --resource-group vimarsh-rg --query "state"
az monitor app-insights component show --app vimarsh-insights --resource-group vimarsh-rg

# Monitor cost trends
az consumption usage list --start-date $(date -d "7 days ago" +%Y-%m-%d) --end-date $(date +%Y-%m-%d)
```

### Weekly Cost Review

```bash
# Generate cost report
az consumption usage list --start-date $(date -d "30 days ago" +%Y-%m-%d) --end-date $(date +%Y-%m-%d) \
  --query "value[?contains(instanceName, 'vimarsh')].{Resource:instanceName, Cost:pretaxCost, Date:usageStart}"

# Decision criteria for pause:
# - Low user activity for 7+ days
# - Monthly budget approaching 80% threshold
# - Planned feature development requiring service interruption
```

### Monthly Operations

```bash
# Full cost analysis
az consumption budget list --scope "/subscriptions/{subscription-id}"

# Performance review
az monitor app-insights query --app vimarsh-insights \
  --analytics-query "requests | summarize count() by bin(timestamp, 1d) | order by timestamp desc"

# Data backup verification (automatic with Cosmos DB continuous backup)
az cosmosdb show --name vimarsh-db --resource-group vimarsh-db-rg --query "backupPolicy"
```

## Troubleshooting

### Failed Resume Operation

```bash
# 1. Check resource group creation
az group show --name vimarsh-rg

# 2. Check deployment status
az deployment sub show --name vimarsh-compute-deployment

# 3. Verify persistent resources intact
az cosmosdb show --name vimarsh-db --resource-group vimarsh-db-rg --query "provisioningState"

# 4. Manual resource recreation if needed
az deployment group create --resource-group vimarsh-rg --template-file infrastructure/compute.bicep
```

### Data Connectivity Issues

```bash
# Verify cross-resource-group connectivity
az functionapp config appsettings list --name vimarsh-functions --resource-group vimarsh-rg \
  --query "[?name=='COSMOS_DB_ENDPOINT'].value"

# Test Key Vault access
az functionapp identity show --name vimarsh-functions --resource-group vimarsh-rg
az keyvault show --name vimarsh-kv --resource-group vimarsh-db-rg
```

## Security Considerations

### Key Vault Access

- Function App uses managed identity for Key Vault access
- No hardcoded secrets in compute resources
- Secrets persist in vimarsh-db-rg during pause cycles

### Network Security

- All resources use HTTPS/TLS 1.2+
- Function App CORS configured for Static Web App domain
- No public access to Cosmos DB data plane

### Backup and Recovery

- Cosmos DB: Continuous backup (7-day point-in-time recovery)
- Key Vault: Soft delete enabled with 7-day retention
- Storage Account: Geo-redundant storage for critical content

## Best Practices

### Operational Excellence

1. **Advance Planning**: Schedule pause operations during low-usage periods
2. **User Communication**: Provide 48-hour advance notice for planned downtime
3. **Monitoring**: Set up automated alerts for cost thresholds and service health
4. **Documentation**: Maintain deployment logs and cost tracking spreadsheets

### Cost Optimization

1. **Regular Review**: Weekly assessment of usage patterns and cost trends
2. **Pause Criteria**: Establish clear criteria for when to pause services
3. **Resume Planning**: Plan resume operations around expected usage spikes
4. **Budget Alerts**: Configure multiple threshold alerts (50%, 80%, 95%, 100%)

### Service Quality

1. **Health Checks**: Implement automated health monitoring
2. **Performance Baseline**: Establish performance metrics for comparison
3. **User Feedback**: Monitor user satisfaction through service disruptions
4. **Continuous Improvement**: Regular review of pause-resume procedures

---

*This deployment guide ensures reliable, cost-effective operation of Vimarsh's innovative infrastructure architecture while maintaining high service quality and user satisfaction.*
