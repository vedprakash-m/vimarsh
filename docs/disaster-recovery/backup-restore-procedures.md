# Backup and Restore Procedures

## Quick Reference

### Emergency Restore Commands

```bash
# Restore Cosmos DB to 1 hour ago
az cosmosdb restore \
  --account-name vimarsh-prod-cosmos-restored \
  --resource-group vimarsh-prod-rg \
  --source-database-account-name vimarsh-prod-cosmos \
  --restore-timestamp "$(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ)" \
  --location eastus

# Restore configuration from backup
./scripts/config-manager.sh restore-from-backup \
  --environment prod \
  --backup-timestamp latest

# Validate all backups
./scripts/disaster-recovery.sh validate --environment prod
```

## Backup Procedures

### 1. Scheduled Backups

#### Cosmos DB (Automatic)
- **Continuous backup** runs automatically
- No manual intervention required
- Backup retention: 7 days (dev), 30 days (staging), 365 days (prod)

#### Configuration Backup (Daily)
```bash
# Manual configuration backup
./scripts/disaster-recovery.sh backup --environment prod

# Automated via cron (daily at 2 AM)
0 2 * * * /path/to/vimarsh/scripts/disaster-recovery.sh backup --environment prod >> /var/log/vimarsh-backup.log 2>&1
```

### 2. On-Demand Backups

#### Before Major Deployments
```bash
# Create deployment checkpoint
./scripts/disaster-recovery.sh backup --environment prod
echo "Backup completed before deployment at $(date)" >> deployment.log
```

#### Before Data Migration
```bash
# Create pre-migration backup
BACKUP_TIMESTAMP=$(date +%Y%m%d-%H%M%S)
./scripts/disaster-recovery.sh backup --environment prod
echo "Pre-migration backup: $BACKUP_TIMESTAMP" >> migration.log
```

### 3. Backup Validation

#### Weekly Validation
```bash
# Validate backup integrity
./scripts/disaster-recovery.sh validate --environment prod

# Check backup age and accessibility
./scripts/disaster-recovery.sh status --environment prod
```

#### Monthly DR Test
```bash
# Full disaster recovery test
./scripts/disaster-recovery.sh test-dr --environment staging --verbose
```

## Restore Procedures

### 1. Cosmos DB Point-in-Time Restore

#### Identify Restore Point
```bash
# Get database activity logs
az monitor activity-log list \
  --resource-group vimarsh-prod-rg \
  --resource-id "/subscriptions/SUBSCRIPTION_ID/resourceGroups/vimarsh-prod-rg/providers/Microsoft.DocumentDB/databaseAccounts/vimarsh-prod-cosmos" \
  --start-time "2024-01-15T00:00:00Z" \
  --end-time "2024-01-15T23:59:59Z"
```

#### Execute Restore
```bash
# Step 1: Stop application traffic (optional but recommended)
az functionapp stop --name vimarsh-prod-functions --resource-group vimarsh-prod-rg

# Step 2: Create restored database
RESTORE_TIMESTAMP="2024-01-15T10:30:00Z"
az cosmosdb restore \
  --account-name vimarsh-prod-cosmos-restored \
  --resource-group vimarsh-prod-rg \
  --source-database-account-name vimarsh-prod-cosmos \
  --restore-timestamp "$RESTORE_TIMESTAMP" \
  --location eastus

# Step 3: Update application configuration
# Update connection string in Key Vault or environment config

# Step 4: Restart application
az functionapp start --name vimarsh-prod-functions --resource-group vimarsh-prod-rg
```

#### Validate Restore
```bash
# Run data integrity checks
python scripts/validate-cosmos-data.py --connection-string "NEW_CONNECTION_STRING"

# Run application health checks
curl -f https://vimarsh-prod-functions.azurewebsites.net/api/health
```

### 2. Configuration Restore

#### From Backup Manifest
```bash
# List available backups
ls -la backups/configuration/

# Restore specific backup
BACKUP_TIMESTAMP="20240115-103000"
./scripts/config-manager.sh restore-from-backup \
  --environment prod \
  --backup-timestamp "$BACKUP_TIMESTAMP"
```

#### Manual Configuration Restore
```bash
# Restore configuration files (simplified single-environment)
cp backups/configuration/latest/.env.development .env.development
cp backups/configuration/latest/frontend/.env.development frontend/.env.development
cp backups/configuration/latest/backend/local.settings.json backend/local.settings.json

# Note: Production secrets are in Azure Key Vault (no file restore needed)
# Restore infrastructure parameters
cp backups/configuration/latest/infrastructure/parameters/prod.parameters.json infrastructure/parameters/

# Redeploy with restored configuration
az deployment group create \
  --resource-group vimarsh-prod-rg \
  --template-file infrastructure/main.bicep \
  --parameters @infrastructure/parameters/prod.parameters.json
```

### 3. Application Code Restore

#### From Git Repository
```bash
# Identify last known good commit
git log --oneline --since="2024-01-15 10:00" --until="2024-01-15 11:00"

# Create recovery branch
git checkout -b recovery-$(date +%Y%m%d-%H%M%S) LAST_GOOD_COMMIT

# Deploy from recovery branch
git push origin recovery-$(date +%Y%m%d-%H%M%S)
# Trigger CI/CD pipeline for deployment
```

#### Emergency Code Rollback
```bash
# Quick rollback to previous deployment
az functionapp deployment source config \
  --name vimarsh-prod-functions \
  --resource-group vimarsh-prod-rg \
  --repo-url "https://github.com/your-org/vimarsh" \
  --branch "previous-stable-branch"
```

## Cross-Region Recovery

### Production Cross-Region Failover

#### Prerequisites Check
```bash
# Verify secondary region setup
az cosmosdb show \
  --name vimarsh-prod-cosmos \
  --resource-group vimarsh-prod-rg \
  --query "locations[1]"

# Check replication status
az cosmosdb show \
  --name vimarsh-prod-cosmos \
  --resource-group vimarsh-prod-rg \
  --query "consistencyPolicy"
```

#### Execute Failover
```bash
# Step 1: Trigger Cosmos DB failover
az cosmosdb failover-priority-change \
  --resource-group vimarsh-prod-rg \
  --account-name vimarsh-prod-cosmos \
  --failover-policies westus2=0 eastus=1

# Step 2: Deploy application to secondary region
az deployment group create \
  --resource-group vimarsh-prod-westus2-rg \
  --template-file infrastructure/main.bicep \
  --parameters @infrastructure/parameters/prod-westus2.parameters.json

# Step 3: Update DNS/Traffic Manager
az network traffic-manager endpoint update \
  --resource-group vimarsh-prod-rg \
  --profile-name vimarsh-prod-tm \
  --name eastus-endpoint \
  --type azureEndpoints \
  --endpoint-status Disabled

az network traffic-manager endpoint update \
  --resource-group vimarsh-prod-rg \
  --profile-name vimarsh-prod-tm \
  --name westus2-endpoint \
  --type azureEndpoints \
  --endpoint-status Enabled
```

#### Validate Failover
```bash
# Test application functionality
curl -f https://vimarsh-prod-westus2-functions.azurewebsites.net/api/health

# Verify data consistency
python scripts/validate-cosmos-data.py --region westus2

# Monitor performance
./scripts/monitoring-setup.sh check-performance --region westus2
```

## Recovery Validation

### Data Integrity Checks

#### Cosmos DB Validation
```bash
# Check document counts
python -c "
import json
from azure.cosmos import CosmosClient

client = CosmosClient.from_connection_string('CONNECTION_STRING')
database = client.get_database_client('SpiritualGuidance')
container = database.get_container_client('Documents')

query = 'SELECT VALUE COUNT(1) FROM c'
result = list(container.query_items(query, enable_cross_partition_query=True))
print(f'Total documents: {result[0]}')
"

# Validate vector embeddings
python scripts/validate-vector-data.py --connection-string "CONNECTION_STRING"
```

#### Configuration Validation
```bash
# Validate environment configuration
./scripts/config-manager.sh validate --environment prod

# Check Key Vault secrets
az keyvault secret list --vault-name vimarsh-prod-kv --query "[].name" -o table
```

### Application Health Checks

#### Backend API Validation
```bash
# Health endpoint
curl -f https://vimarsh-prod-functions.azurewebsites.net/api/health

# Spiritual guidance endpoint test
curl -X POST https://vimarsh-prod-functions.azurewebsites.net/api/spiritual-guidance \
  -H "Content-Type: application/json" \
  -d '{"query": "What is dharma?", "language": "en"}'
```

#### Frontend Validation
```bash
# Static web app availability
curl -f https://vimarsh-prod-web.azurestaticapps.net/

# Frontend functionality test
curl -f https://vimarsh-prod-web.azurestaticapps.net/manifest.json
```

### Performance Validation

#### Load Testing After Restore
```bash
# Run performance tests
python tests/performance/load_test.py \
  --base-url "https://vimarsh-prod-functions.azurewebsites.net" \
  --duration 300 \
  --concurrent-users 10
```

#### Monitoring Dashboard Check
```bash
# Check Application Insights
az monitor app-insights query \
  --app vimarsh-prod-insights \
  --analytics-query "requests | where timestamp > ago(1h) | summarize count() by bin(timestamp, 5m)"
```

## Troubleshooting Common Issues

### Issue 1: Restore Operation Fails

#### Symptoms
- Cosmos DB restore command fails
- "Source account not found" error

#### Resolution
```bash
# Verify source account exists and is accessible
az cosmosdb show --name vimarsh-prod-cosmos --resource-group vimarsh-prod-rg

# Check restore timestamp is within retention period
az cosmosdb show --name vimarsh-prod-cosmos --resource-group vimarsh-prod-rg \
  --query "backupPolicy.continuousModeProperties.tier"

# Use correct timestamp format (ISO 8601)
date -u +%Y-%m-%dT%H:%M:%SZ
```

### Issue 2: Configuration Restore Incomplete

#### Symptoms
- Application fails to start after config restore
- Missing environment variables

#### Resolution
```bash
# Compare backup with current configuration (simplified single-environment)
diff .env.development backups/configuration/latest/.env.development
diff frontend/.env.development backups/configuration/latest/frontend/.env.development
diff backend/local.settings.json backups/configuration/latest/backend/local.settings.json

# Manually restore missing configurations (simplified single-environment)
cp backups/configuration/latest/.env.development .env.development
cp backups/configuration/latest/frontend/.env.development frontend/.env.development
cp backups/configuration/latest/backend/local.settings.json backend/local.settings.json

# Note: Production secrets are in Azure Key Vault (no file restore needed)
# Validate configuration
./scripts/config-manager.sh validate --environment prod
```

### Issue 3: Data Inconsistency After Restore

#### Symptoms
- Document counts don't match expected values
- Vector search returns incorrect results

#### Resolution
```bash
# Check for partial restore
python scripts/validate-cosmos-data.py --detailed

# Verify vector embeddings integrity
python scripts/validate-vector-data.py --rebuild-index

# If needed, trigger vector reindexing
python scripts/reindex-vectors.py --environment prod
```

## Automation and Monitoring

### Backup Monitoring Setup

#### Log Analytics Queries
```kql
// Failed backup operations
AzureDiagnostics
| where ResourceProvider == "MICROSOFT.DOCUMENTDB"
| where OperationName == "BackupOperation"
| where ResultType != "Success"
| summarize count() by bin(TimeGenerated, 1h)

// Backup age monitoring
AzureDiagnostics
| where ResourceProvider == "MICROSOFT.DOCUMENTDB"
| where OperationName == "BackupOperation"
| where ResultType == "Success"
| summarize max(TimeGenerated) by Resource
```

#### Alert Rules
```bash
# Deploy backup monitoring alerts
az monitor metrics alert create \
  --name "Backup Failure Alert" \
  --resource-group vimarsh-prod-rg \
  --scopes "/subscriptions/SUBSCRIPTION_ID/resourceGroups/vimarsh-prod-rg/providers/Microsoft.DocumentDB/databaseAccounts/vimarsh-prod-cosmos" \
  --condition "count 'Total Requests' > 0" \
  --window-size 1h \
  --evaluation-frequency 15m \
  --action-group vimarsh-prod-dr-alerts
```

### Automated Recovery Scripts

#### Self-Healing Script
```bash
#!/bin/bash
# auto-recovery.sh - Automated recovery for common issues

check_cosmos_health() {
    local cosmos_name="$1"
    local rg="$2"
    
    if ! az cosmosdb show --name "$cosmos_name" --resource-group "$rg" &>/dev/null; then
        echo "CRITICAL: Cosmos DB not accessible"
        return 1
    fi
    
    return 0
}

auto_recover() {
    local environment="$1"
    
    if ! check_cosmos_health "vimarsh-${environment}-cosmos" "vimarsh-${environment}-rg"; then
        echo "Attempting automatic recovery..."
        ./scripts/disaster-recovery.sh validate --environment "$environment"
        
        if [[ $? -ne 0 ]]; then
            echo "Manual intervention required"
            # Send alert to operations team
            curl -X POST "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK" \
                -H 'Content-type: application/json' \
                --data '{"text":"Vimarsh auto-recovery failed for '"$environment"'. Manual intervention required."}'
        fi
    fi
}

# Run auto-recovery
auto_recover "$1"
```

---

**Document Version:** 1.0  
**Last Updated:** December 2024  
**Next Review:** Monthly  
**Owner:** DevOps Team
