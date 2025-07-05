# Environment Variables Documentation

## Overview
This document provides complete documentation for all environment variables used in the Vimarsh application.

## Configuration Categories

### 1. Azure Services Configuration

#### Core Azure Settings
- **AZURE_SUBSCRIPTION_ID**: Your Azure subscription ID
  - Required: Yes (Production)
  - Example: `12345678-1234-1234-1234-123456789012`

- **AZURE_RESOURCE_GROUP**: Azure resource group name
  - Required: Yes (Production)
  - Example: `vimarsh-rg`

- **AZURE_LOCATION**: Azure region for resources
  - Required: No
  - Default: `eastus`
  - Example: `eastus`, `westus2`, `centralindia`

- **AZURE_TENANT_ID**: Azure AD tenant ID
  - Required: Yes (if authentication enabled)
  - Example: `87654321-4321-4321-4321-210987654321`

- **AZURE_CLIENT_ID**: Azure AD application client ID
  - Required: Yes (if authentication enabled)
  - Example: `11111111-2222-3333-4444-555555555555`

#### Azure Cosmos DB
- **AZURE_COSMOS_CONNECTION_STRING**: Connection string for Cosmos DB
  - Required: Yes (Production)
  - Development: `dev-mode-local-storage` (uses local JSON storage)
  - Production: `AccountEndpoint=https://your-cosmos.documents.azure.com:443/;AccountKey=your-key;`

- **AZURE_COSMOS_DATABASE_NAME**: Cosmos DB database name
  - Required: No
  - Default: `vimarsh`

- **AZURE_COSMOS_CONTAINER_NAME**: Cosmos DB container name
  - Required: No
  - Default: `spiritual_texts`

#### Azure Storage
- **AZURE_STORAGE_CONNECTION_STRING**: Storage account connection string
  - Required: Yes (Production)
  - Example: `DefaultEndpointsProtocol=https;AccountName=your-storage;AccountKey=your-key`

### 2. LLM Configuration

#### Gemini API
- **GEMINI_API_KEY** or **GOOGLE_AI_API_KEY**: Google AI API key for Gemini
  - Required: Yes (for real LLM responses)
  - Development: `dev-mode-placeholder` (uses fallback responses)
  - Production: Your actual Gemini API key

- **LLM_MODEL**: Gemini model to use
  - Required: No
  - Default: `gemini-2.5-flash`
  - Options: `gemini-1.5-flash`, `gemini-2.5-flash`, `gemini-pro`

- **LLM_TEMPERATURE**: Temperature for response generation
  - Required: No
  - Default: `0.7`
  - Range: `0.0` to `2.0`

- **MAX_TOKENS**: Maximum tokens for response generation
  - Required: No
  - Default: `4096`
  - Range: `1` to `8192`

- **SAFETY_SETTINGS**: Safety level for content filtering
  - Required: No
  - Default: `BLOCK_MEDIUM_AND_ABOVE`
  - Options: `BLOCK_NONE`, `BLOCK_ONLY_HIGH`, `BLOCK_MEDIUM_AND_ABOVE`, `BLOCK_LOW_AND_ABOVE`

#### Vector Search
- **EMBEDDING_MODEL**: Model for text embeddings
  - Required: No
  - Default: `sentence-transformers/all-MiniLM-L6-v2`

- **VECTOR_DIMENSION**: Dimension of vector embeddings
  - Required: No
  - Default: `384`

- **SIMILARITY_THRESHOLD**: Threshold for vector similarity
  - Required: No
  - Default: `0.7`
  - Range: `0.0` to `1.0`

- **MAX_RETRIEVED_CHUNKS**: Maximum text chunks to retrieve
  - Required: No
  - Default: `10`

### 3. Authentication Configuration

#### Microsoft Entra ID
- **ENABLE_AUTH**: Enable/disable authentication
  - Required: No
  - Default: `false`
  - Options: `true`, `false`

- **ENTRA_TENANT_ID**: Microsoft Entra tenant ID
  - Required: Yes (if authentication enabled)
  - Example: `vedid.onmicrosoft.com`

- **ENTRA_CLIENT_ID**: Microsoft Entra application client ID
  - Required: Yes (if authentication enabled)
  - Development: `dev-mode-placeholder`

- **AZURE_AUTHORITY**: Microsoft Entra authority URL
  - Required: Yes (if authentication enabled)
  - Example: `https://login.microsoftonline.com/vedid.onmicrosoft.com/v2.0`

- **AZURE_REDIRECT_URI**: OAuth redirect URI
  - Required: Yes (if authentication enabled)
  - Development: `http://localhost:3000`
  - Production: `https://your-app.com`

### 4. Monitoring & Logging

#### Application Insights
- **APPLICATIONINSIGHTS_CONNECTION_STRING**: Azure Application Insights connection string
  - Required: Yes (Production)
  - Example: `InstrumentationKey=your-key;IngestionEndpoint=https://your-region.in.applicationinsights.azure.com/`

#### Logging
- **LOG_LEVEL**: Logging level
  - Required: No
  - Default: `INFO`
  - Options: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

- **DEBUG**: Enable debug mode
  - Required: No
  - Default: `false`
  - Options: `true`, `false`

### 5. Security Configuration

#### CORS
- **CORS_ORIGINS**: Allowed CORS origins (comma-separated)
  - Required: No
  - Default: `http://localhost:3000`
  - Example: `http://localhost:3000,https://your-app.com`

### 6. Application Configuration

#### Language Support
- **DEFAULT_LANGUAGE**: Default language for responses
  - Required: No
  - Default: `English`
  - Options: `English`, `Hindi`

- **SUPPORTED_LANGUAGES**: Supported languages (comma-separated)
  - Required: No
  - Default: `English,Hindi`

#### Expert Review
- **EXPERT_REVIEW_ENABLED**: Enable expert review system
  - Required: No
  - Default: `true`
  - Options: `true`, `false`

- **EXPERT_NOTIFICATION_EMAIL**: Email for expert notifications
  - Required: No
  - Example: `experts@vimarsh.ai`

### 7. Azure Functions Specific

#### Runtime Configuration
- **FUNCTIONS_WORKER_RUNTIME**: Azure Functions runtime
  - Required: Yes
  - Value: `python`

- **FUNCTIONS_EXTENSION_VERSION**: Azure Functions extension version
  - Required: Yes
  - Value: `~4`

- **AzureWebJobsStorage**: Azure Functions storage connection
  - Required: Yes
  - Development: `UseDevelopmentStorage=true`
  - Production: Storage connection string

## Environment-Specific Configurations

### Development Environment
```bash
ENVIRONMENT=development
ENABLE_AUTH=false
DEBUG=true
LOG_LEVEL=DEBUG
GEMINI_API_KEY=dev-mode-placeholder
AZURE_COSMOS_CONNECTION_STRING=dev-mode-local-storage
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

### Production Environment
```bash
ENVIRONMENT=production
ENABLE_AUTH=true
DEBUG=false
LOG_LEVEL=INFO
GEMINI_API_KEY=your-actual-api-key
AZURE_COSMOS_CONNECTION_STRING=your-cosmos-connection-string
APPLICATIONINSIGHTS_CONNECTION_STRING=your-app-insights-connection-string
CORS_ORIGINS=https://your-production-domain.com
```

### Testing Environment
```bash
ENVIRONMENT=testing
ENABLE_AUTH=false
DEBUG=true
LOG_LEVEL=DEBUG
GEMINI_API_KEY=test-mode-placeholder
AZURE_COSMOS_CONNECTION_STRING=test-mode-local-storage
```

## Configuration Validation

The configuration system automatically validates all settings on startup and provides warnings for:
- Missing required values
- Invalid value ranges
- Incompatible settings
- Production readiness issues

## Security Considerations

### Secrets Management
- Never commit API keys or connection strings to version control
- Use Azure Key Vault for production secrets
- Use environment variables for local development
- Rotate keys regularly

### Access Control
- Limit access to configuration files
- Use least privilege principle for service accounts
- Monitor configuration changes

## Troubleshooting

### Common Issues

1. **Configuration not loading**
   - Check file permissions
   - Verify environment variable names
   - Check for typos in configuration files

2. **Authentication failures**
   - Verify tenant ID and client ID
   - Check redirect URI configuration
   - Ensure correct authority URL

3. **LLM API failures**
   - Verify API key is valid
   - Check quota limits
   - Verify model availability

4. **Database connection issues**
   - Verify connection string format
   - Check network connectivity
   - Verify database exists

### Configuration Debug Mode
Enable debug mode to see detailed configuration loading:
```bash
DEBUG=true LOG_LEVEL=DEBUG python your_app.py
```

This will show:
- Configuration sources being loaded
- Environment variable values (sensitive data masked)
- Validation results
- Configuration summary
