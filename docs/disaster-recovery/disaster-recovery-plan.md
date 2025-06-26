# Vimarsh Disaster Recovery Plan

## Overview

This document outlines the comprehensive backup and disaster recovery procedures for the Vimarsh spiritual guidance platform. The plan ensures business continuity, data protection, and rapid recovery from various failure scenarios.

## Architecture Overview

### Backup Strategy

Our backup strategy follows the 3-2-1 rule:
- **3** copies of critical data
- **2** different storage media
- **1** offsite backup

### Components Covered

1. **Cosmos DB** - Vector storage and spiritual texts
2. **Azure Functions** - Backend API and business logic
3. **Static Web App** - Frontend application
4. **Application Insights** - Monitoring and analytics data
5. **Key Vault** - Secrets and encryption keys
6. **Configuration** - Environment and deployment settings

## Backup Configuration

### Cosmos DB Backup

- **Type:** Continuous backup with point-in-time restore
- **Retention:** 7 days (development), 30 days (staging), 365 days (production)
- **Features:**
  - Automatic backups every few minutes
  - Point-in-time restore capability
  - Cross-region backup for production
  - No performance impact on database operations

### Azure Functions Backup

- **Source Code:** Git repository with automated CI/CD
- **Configuration:** Environment-specific parameter files
- **Dependencies:** Requirements.txt and package.json versioning
- **Deployment Artifacts:** ARM templates and Bicep files

### Static Web App Backup

- **Source Code:** Git repository with automated deployment
- **Build Artifacts:** Automated rebuild from source
- **Configuration:** Environment-specific configuration files
- **CDN Content:** Automatic regeneration from source

### Configuration Backup

- **Environment Files:** Daily backup to Azure Storage
- **Secrets:** Key Vault with versioning and soft delete
- **Infrastructure:** ARM template exports
- **Monitoring:** Application Insights data retention

## Recovery Time Objectives (RTO) and Recovery Point Objectives (RPO)

| Component | Environment | RTO | RPO | Recovery Method |
|-----------|-------------|-----|-----|-----------------|
| Cosmos DB | Production | < 4 hours | < 15 minutes | Point-in-time restore |
| Cosmos DB | Staging | < 8 hours | < 1 hour | Point-in-time restore |
| Cosmos DB | Development | < 24 hours | < 4 hours | Point-in-time restore |
| Azure Functions | Production | < 2 hours | < 5 minutes | CI/CD redeploy |
| Azure Functions | Staging | < 4 hours | < 30 minutes | CI/CD redeploy |
| Static Web App | Production | < 1 hour | < 5 minutes | Automated rebuild |
| Configuration | All | < 30 minutes | < 1 hour | Backup restore |

## Disaster Recovery Procedures

### 1. Cosmos DB Recovery

#### Point-in-Time Restore

```bash
# Restore Cosmos DB to a specific point in time
az cosmosdb restore \
  --account-name vimarsh-prod-cosmos-restored \
  --resource-group vimarsh-prod-rg \
  --source-database-account-name vimarsh-prod-cosmos \
  --restore-timestamp "2024-01-15T10:30:00Z" \
  --location eastus
```

#### Cross-Region Failover (Production Only)

```bash
# Trigger manual failover to secondary region
az cosmosdb failover-priority-change \
  --resource-group vimarsh-prod-rg \
  --account-name vimarsh-prod-cosmos \
  --failover-policies eastus=1 westus2=0
```

### 2. Application Recovery

#### Backend Recovery

```bash
# Deploy from backup using disaster recovery script
./scripts/disaster-recovery.sh backup --environment prod
./scripts/disaster-recovery.sh validate --environment prod

# Redeploy Azure Functions from CI/CD
az deployment group create \
  --resource-group vimarsh-prod-rg \
  --template-file infrastructure/main.bicep \
  --parameters @infrastructure/parameters/prod.parameters.json
```

#### Frontend Recovery

```bash
# Redeploy Static Web App
az staticwebapp deploy \
  --name vimarsh-prod-web \
  --resource-group vimarsh-prod-rg \
  --source frontend/
```

### 3. Configuration Recovery

```bash
# Restore environment configuration
./scripts/config-manager.sh restore-from-backup \
  --environment prod \
  --backup-timestamp 20240115-103000
```

## Disaster Recovery Testing

### Monthly DR Tests

1. **Backup Validation Test**
   ```bash
   ./scripts/disaster-recovery.sh validate --environment staging
   ```

2. **Point-in-Time Restore Test**
   ```bash
   ./scripts/disaster-recovery.sh test-dr --environment dev
   ```

3. **End-to-End Recovery Test** (Quarterly)
   - Full environment restoration
   - Application functionality validation
   - Performance benchmark comparison

### Test Schedule

| Test Type | Frequency | Environment | Responsibility |
|-----------|-----------|-------------|----------------|
| Backup Validation | Weekly | All | DevOps Team |
| Point-in-Time Restore | Monthly | Development | Development Team |
| Cross-Region Failover | Quarterly | Production | DevOps Team |
| Full DR Simulation | Annually | Staging | All Teams |

## Monitoring and Alerting

### Backup Monitoring

- **Failed Backup Jobs:** Immediate alert to DevOps team
- **Backup Age:** Alert if no backup in 24 hours
- **Storage Consumption:** Alert at 80% capacity
- **Cross-Region Sync:** Alert if replication fails

### Recovery Monitoring

- **RTO Compliance:** Track actual vs. target recovery times
- **RPO Compliance:** Monitor data loss during recovery
- **Recovery Success Rate:** Track successful vs. failed recoveries
- **Test Results:** Monthly DR test status reporting

### Alert Configuration

```bash
# Deploy monitoring and alerting
./scripts/monitoring-setup.sh deploy-alerts \
  --environment prod \
  --notification-email disaster-recovery@vimarsh.app
```

## Security Considerations

### Backup Security

- **Encryption at Rest:** All backups encrypted with customer-managed keys
- **Encryption in Transit:** TLS 1.3 for all backup transfers
- **Access Control:** RBAC with least privilege principle
- **Audit Logging:** All backup operations logged and monitored

### Recovery Security

- **Authentication:** Multi-factor authentication required for recovery operations
- **Authorization:** Role-based access for different recovery scenarios
- **Data Validation:** Integrity checks before recovery completion
- **Compliance:** GDPR and data protection compliance maintained

## Compliance and Documentation

### Regulatory Compliance

- **Data Retention:** Compliant with local data protection laws
- **Cross-Border Data:** Proper handling of international data transfers
- **Audit Trails:** Complete documentation of all backup and recovery operations
- **Reporting:** Regular compliance reports for stakeholders

### Documentation Maintenance

- **Procedure Updates:** Monthly review and updates
- **Test Documentation:** Results of all DR tests documented
- **Lessons Learned:** Post-incident reviews and improvements
- **Training Records:** Team training and certification tracking

## Contact Information

### Emergency Contacts

| Role | Primary Contact | Secondary Contact |
|------|----------------|-------------------|
| DevOps Lead | devops-lead@vimarsh.app | backup-devops@vimarsh.app |
| Database Admin | dba@vimarsh.app | backup-dba@vimarsh.app |
| Security Team | security@vimarsh.app | backup-security@vimarsh.app |
| Product Owner | product@vimarsh.app | backup-product@vimarsh.app |

### Escalation Matrix

1. **Level 1:** DevOps Team (Response time: 15 minutes)
2. **Level 2:** Engineering Lead (Response time: 30 minutes)
3. **Level 3:** CTO/VP Engineering (Response time: 1 hour)
4. **Level 4:** Executive Team (Response time: 2 hours)

## Automation Scripts

### Available Scripts

1. **disaster-recovery.sh** - Main DR automation script
   - Deploy backup infrastructure
   - Create immediate backups
   - Validate backup integrity
   - Run DR tests
   - Monitor backup health

2. **config-manager.sh** - Configuration management
   - Backup configuration files
   - Restore from configuration backups
   - Environment switching

3. **monitoring-setup.sh** - Monitoring configuration
   - Deploy monitoring infrastructure
   - Configure alerting rules
   - Set up dashboards

### Usage Examples

```bash
# Deploy backup infrastructure
./scripts/disaster-recovery.sh deploy --environment prod

# Create immediate backup
./scripts/disaster-recovery.sh backup --environment prod

# Validate backup integrity
./scripts/disaster-recovery.sh validate --environment prod

# Run DR test
./scripts/disaster-recovery.sh test-dr --environment staging

# Monitor backup health
./scripts/disaster-recovery.sh monitor --environment prod
```

## Recovery Scenarios

### Scenario 1: Single Component Failure

**Example:** Azure Functions service disruption

1. **Detection:** Monitoring alerts indicate function app unavailability
2. **Assessment:** Determine scope and cause of failure
3. **Recovery:** Redeploy from CI/CD pipeline or switch to backup region
4. **Validation:** Run health checks and functionality tests
5. **Communication:** Update stakeholders on status and resolution

### Scenario 2: Database Corruption

**Example:** Cosmos DB data corruption or accidental deletion

1. **Detection:** Data integrity checks or user reports
2. **Assessment:** Determine extent of corruption and last known good state
3. **Recovery:** Point-in-time restore to pre-corruption state
4. **Validation:** Data integrity verification and application testing
5. **Prevention:** Review and strengthen data protection measures

### Scenario 3: Regional Outage

**Example:** Complete Azure region unavailability

1. **Detection:** Multiple service failures and Azure status confirmation
2. **Assessment:** Determine duration estimate and impact scope
3. **Recovery:** Failover to secondary region (production only)
4. **Validation:** End-to-end testing in failover region
5. **Rollback:** Plan for return to primary region when available

### Scenario 4: Security Incident

**Example:** Suspected data breach or unauthorized access

1. **Detection:** Security monitoring alerts or external notification
2. **Assessment:** Determine breach scope and compromised data
3. **Recovery:** Restore from clean backup and secure environment
4. **Validation:** Security scan and vulnerability assessment
5. **Reporting:** Compliance reporting and stakeholder communication

---

**Document Version:** 1.0  
**Last Updated:** December 2024  
**Next Review:** January 2025  
**Owner:** DevOps Team
