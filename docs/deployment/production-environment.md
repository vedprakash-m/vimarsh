# Production Environment Configuration

## Environment Setup

This document outlines the complete production environment configuration for Vimarsh.

## Azure Resource Groups

### Primary Resource Groups
1. **vimarsh-db-rg** (Persistent Resources)
   - Cosmos DB (vimarsh-cosmos)
   - Key Vault (vimarsh-kv) 
   - Storage Account (vimarshstorage)

2. **vimarsh-rg** (Compute Resources)
   - Azure Functions (vimarsh-functions)
   - Static Web App (vimarsh-web)
   - Application Insights (vimarsh-insights)
   - App Service Plan (vimarsh-plan)

## Security Configuration

### Authentication & Authorization
- **Provider**: Microsoft Entra External ID
- **Tenant**: VedID.onmicrosoft.com (existing VED tenant)
- **Application Registration**: Vimarsh AI Agent
- **Scopes**: User.Read, openid, profile, email
- **Token Type**: JWT with RS256 signing

### Network Security
- **TLS Version**: 1.2+ minimum on all services
- **HTTPS Only**: Enforced on all endpoints
- **CORS**: Restricted to production domains only
- **Firewall**: IP whitelisting available for enhanced security

### Data Encryption
- **At Rest**: Azure-managed encryption keys
- **In Transit**: TLS 1.2+ for all communications
- **Key Management**: Azure Key Vault with RBAC
- **Backup**: Encrypted automated backups

## Performance Configuration

### Azure Functions
- **Runtime**: Python 3.11 on Linux
- **Plan**: Consumption (Y1) for cost optimization
- **Scaling**: Dynamic scaling up to 100 concurrent executions
- **Memory**: 1.5GB maximum per execution
- **Timeout**: 10 minutes maximum execution time
- **Cold Start**: Optimized with pre-warming

### Cosmos DB
- **Tier**: Serverless for cost optimization
- **Consistency**: Session level (balanced performance/consistency)
- **Vector Search**: Enabled with quantizedFlat indexing
- **Backup**: Continuous 7-day point-in-time recovery
- **Regions**: Single region (East US) for cost optimization

### Static Web App
- **Tier**: Standard for production features
- **CDN**: Global edge caching enabled
- **Build**: React with TypeScript optimization
- **Caching**: Aggressive caching for static assets
- **Compression**: Gzip/Brotli compression enabled

## Monitoring & Observability

### Application Insights
- **Retention**: 90 days for production
- **Sampling**: Adaptive sampling to control costs
- **Alerts**: Performance, error rate, and cost thresholds
- **Dashboard**: Real-time operational dashboard

### Custom Metrics
- **Response Quality**: Spiritual content authenticity scoring
- **User Engagement**: Query patterns and satisfaction
- **Cost Tracking**: AI usage and budget monitoring
- **Performance**: Response time and availability metrics

### Logging
- **Level**: INFO for production (DEBUG for troubleshooting)
- **Structure**: JSON structured logging
- **Correlation**: Request correlation IDs
- **Security**: Sensitive data excluded from logs

## Cost Optimization

### Budget Management
- **Monthly Budget**: $50-200 for beta testing phase
- **Alert Thresholds**: 80% (warning), 100% (critical)
- **Cost Controls**: Automatic scaling limits and throttling
- **Resource Management**: Pause/resume capability

### Resource Optimization
- **Serverless**: Cosmos DB and Functions for pay-per-use
- **Scaling**: Dynamic scaling based on demand
- **Caching**: Aggressive caching to reduce API calls
- **Storage**: Lifecycle policies for automated cleanup

## Deployment Configuration

### CI/CD Pipeline
- **Trigger**: Push to main branch or manual dispatch
- **Environments**: Staging and Production
- **Testing**: Full test suite before deployment
- **Rollback**: Automated rollback on deployment failures

### Environment Variables
```bash
# Azure Configuration
AZURE_SUBSCRIPTION_ID=<subscription-id>
AZURE_RESOURCE_GROUP=vimarsh-rg
AZURE_LOCATION=eastus

# Application Configuration
ENVIRONMENT=prod
LOG_LEVEL=INFO
MAX_QUERY_LENGTH=1000
RESPONSE_TIMEOUT_SECONDS=30

# Security Configuration
AZURE_AD_TENANT_ID=<tenant-id>
AZURE_AD_CLIENT_ID=<client-id>
JWT_ISSUER=https://login.microsoftonline.com/<tenant-id>/v2.0
JWT_JWKS_URI=https://login.microsoftonline.com/<tenant-id>/discovery/v2.0/keys

# Service Configuration
GEMINI_API_KEY=@Microsoft.KeyVault(SecretUri=<keyvault-uri>)
COSMOS_CONNECTION_STRING=@Microsoft.KeyVault(SecretUri=<keyvault-uri>)
EXPERT_REVIEW_EMAIL=vedprakash.m@me.com
```

### Secret Management
- **Storage**: Azure Key Vault with RBAC access
- **Access**: Managed identity for Function App
- **Rotation**: Automated secret rotation (where supported)
- **Audit**: All secret access logged and monitored

## Disaster Recovery

### Backup Strategy
- **Cosmos DB**: Continuous backup with 7-day retention
- **Storage**: LRS with manual backup for critical data
- **Code**: Git repository with tagged releases
- **Configuration**: Infrastructure as Code in version control

### Recovery Procedures
1. **Data Recovery**: Point-in-time restore from Cosmos DB backup
2. **Service Recovery**: Redeploy from Git repository
3. **Configuration Recovery**: Apply infrastructure templates
4. **Validation**: Automated smoke tests after recovery

### RTO/RPO Targets
- **Recovery Time Objective (RTO)**: 2 hours
- **Recovery Point Objective (RPO)**: 5 minutes
- **Availability Target**: 99.9% uptime
- **Data Loss Tolerance**: Maximum 5 minutes

## Compliance & Legal

### Data Protection
- **GDPR**: Data minimization, consent management, right to deletion
- **Privacy**: Minimal personal data collection
- **Retention**: Configurable data retention policies
- **Anonymization**: User data anonymization for analytics

### Content Compliance
- **Source Verification**: Public domain texts with legal documentation
- **Attribution**: Proper citation of all source materials
- **Expert Review**: Spiritual content validation by qualified experts
- **Cultural Sensitivity**: Respectful handling of sacred content

## Operational Procedures

### Daily Operations
- [ ] Monitor Application Insights dashboard
- [ ] Review cost and budget status
- [ ] Check error rates and performance metrics
- [ ] Validate backup completion
- [ ] Review security alerts

### Weekly Operations
- [ ] Review expert feedback and content quality
- [ ] Analyze user engagement metrics
- [ ] Update dependencies and security patches
- [ ] Conduct cost optimization review
- [ ] Test disaster recovery procedures

### Monthly Operations
- [ ] Security access review
- [ ] Performance optimization analysis
- [ ] Budget and cost forecasting
- [ ] Compliance audit
- [ ] Expert panel feedback review

## Emergency Contacts

### Technical Support
- **Primary**: vedprakash.m@me.com
- **Azure Support**: Enterprise support plan
- **Development Team**: On-call rotation

### Business Contacts
- **Project Owner**: vedprakash.m@me.com
- **Legal/Compliance**: External counsel
- **Expert Panel**: Spiritual content advisors

## Production Checklist

### Pre-Deployment
- [ ] Security configuration validated
- [ ] All secrets stored in Key Vault
- [ ] CORS configured for production domains
- [ ] TLS 1.2+ enforced on all services
- [ ] Monitoring and alerting configured
- [ ] Backup procedures tested
- [ ] Expert review system validated

### Deployment
- [ ] Infrastructure deployed via Bicep templates
- [ ] Function App deployed and validated
- [ ] Static Web App deployed and validated
- [ ] Authentication flow tested
- [ ] End-to-end smoke tests passed
- [ ] Performance benchmarks met

### Post-Deployment
- [ ] All services responding correctly
- [ ] Authentication working end-to-end
- [ ] Monitoring data flowing correctly
- [ ] Cost tracking operational
- [ ] Expert notification system working
- [ ] Documentation updated

---

*This configuration ensures Vimarsh operates securely, efficiently, and cost-effectively in production while maintaining the highest standards of spiritual content quality.*
