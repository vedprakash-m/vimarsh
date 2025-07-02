#!/bin/bash

# Vimarsh Production Environment Setup Script
# Creates necessary environment variables and secrets for Azure deployment
# Usage: ./setup-production-env.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🕉️  Vimarsh Production Environment Setup${NC}"
echo ""

# Configuration
RESOURCE_GROUP_DB="vimarsh-db-rg"
RESOURCE_GROUP_COMPUTE="vimarsh-rg"
KEY_VAULT_NAME="vimarsh-kv"
FUNCTION_APP_NAME="vimarsh-functions"

# Check if Azure CLI is logged in
if ! az account show &> /dev/null; then
    echo -e "${RED}❌ Please login to Azure first: az login${NC}"
    exit 1
fi

# Check if resource groups exist
echo -e "${BLUE}🔍 Checking resource groups...${NC}"
if ! az group show --name $RESOURCE_GROUP_DB &> /dev/null; then
    echo -e "${YELLOW}⚠️  Persistent resource group $RESOURCE_GROUP_DB not found${NC}"
    echo -e "${YELLOW}   Please deploy infrastructure first: ./deploy.sh${NC}"
    exit 1
fi

if ! az group show --name $RESOURCE_GROUP_COMPUTE &> /dev/null; then
    echo -e "${YELLOW}⚠️  Compute resource group $RESOURCE_GROUP_COMPUTE not found${NC}"
    echo -e "${YELLOW}   Please deploy infrastructure first: ./deploy.sh${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Resource groups found${NC}"

# Collect environment variables
echo -e "${BLUE}📝 Setting up environment variables...${NC}"
echo ""

# Required: Gemini API Key
echo -e "${YELLOW}Please provide your Google AI API key for Gemini Pro:${NC}"
read -s GEMINI_API_KEY
if [ -z "$GEMINI_API_KEY" ]; then
    echo -e "${RED}❌ Gemini API key is required${NC}"
    exit 1
fi

# Optional: Google Cloud Services
echo -e "${YELLOW}Do you want to enable Google Cloud TTS/STT? (y/n):${NC}"
read -r ENABLE_GOOGLE_CLOUD

GOOGLE_CLOUD_PROJECT=""
GOOGLE_CLOUD_TTS_KEY=""
GOOGLE_CLOUD_STT_KEY=""

if [[ $ENABLE_GOOGLE_CLOUD =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Google Cloud Project ID:${NC}"
    read -r GOOGLE_CLOUD_PROJECT
    
    echo -e "${YELLOW}Google Cloud TTS API Key (or press Enter to use Application Default Credentials):${NC}"
    read -s GOOGLE_CLOUD_TTS_KEY
    
    echo -e "${YELLOW}Google Cloud STT API Key (or press Enter to use Application Default Credentials):${NC}"
    read -s GOOGLE_CLOUD_STT_KEY
fi

# Store secrets in Azure Key Vault
echo -e "${BLUE}🔐 Storing secrets in Azure Key Vault...${NC}"

# Set Gemini API key
az keyvault secret set \
    --vault-name $KEY_VAULT_NAME \
    --name "gemini-api-key" \
    --value "$GEMINI_API_KEY" \
    --output none

echo -e "${GREEN}✅ Gemini API key stored${NC}"

# Set Google Cloud credentials if provided
if [ ! -z "$GOOGLE_CLOUD_PROJECT" ]; then
    az keyvault secret set \
        --vault-name $KEY_VAULT_NAME \
        --name "google-cloud-project" \
        --value "$GOOGLE_CLOUD_PROJECT" \
        --output none
    echo -e "${GREEN}✅ Google Cloud project ID stored${NC}"
fi

if [ ! -z "$GOOGLE_CLOUD_TTS_KEY" ]; then
    az keyvault secret set \
        --vault-name $KEY_VAULT_NAME \
        --name "google-cloud-tts-key" \
        --value "$GOOGLE_CLOUD_TTS_KEY" \
        --output none
    echo -e "${GREEN}✅ Google Cloud TTS key stored${NC}"
fi

if [ ! -z "$GOOGLE_CLOUD_STT_KEY" ]; then
    az keyvault secret set \
        --vault-name $KEY_VAULT_NAME \
        --name "google-cloud-stt-key" \
        --value "$GOOGLE_CLOUD_STT_KEY" \
        --output none
    echo -e "${GREEN}✅ Google Cloud STT key stored${NC}"
fi

# Configure Function App environment variables
echo -e "${BLUE}⚙️  Configuring Function App environment...${NC}"

# Get Cosmos DB connection string
COSMOS_CONNECTION_STRING=$(az cosmosdb keys list \
    --resource-group $RESOURCE_GROUP_DB \
    --name vimarsh-db \
    --type connection-strings \
    --query "connectionStrings[0].connectionString" \
    --output tsv)

# Get Storage connection string
STORAGE_CONNECTION_STRING=$(az storage account show-connection-string \
    --resource-group $RESOURCE_GROUP_DB \
    --name vimarshstorage \
    --query connectionString \
    --output tsv)

# Get Key Vault URI
KEY_VAULT_URI=$(az keyvault show \
    --resource-group $RESOURCE_GROUP_DB \
    --name $KEY_VAULT_NAME \
    --query properties.vaultUri \
    --output tsv)

# Set Function App configuration
az functionapp config appsettings set \
    --resource-group $RESOURCE_GROUP_COMPUTE \
    --name $FUNCTION_APP_NAME \
    --settings \
        "AZURE_FUNCTIONS_ENVIRONMENT=production" \
        "AZURE_COSMOS_CONNECTION_STRING=$COSMOS_CONNECTION_STRING" \
        "AZURE_COSMOS_DATABASE_NAME=vimarsh" \
        "AZURE_COSMOS_CONTAINER_NAME=spiritual_texts" \
        "AZURE_STORAGE_CONNECTION_STRING=$STORAGE_CONNECTION_STRING" \
        "AZURE_KEY_VAULT_URI=$KEY_VAULT_URI" \
        "LLM_MODEL=gemini-pro" \
        "LLM_TEMPERATURE=0.7" \
        "MAX_TOKENS=4096" \
        "SAFETY_SETTINGS=BLOCK_MEDIUM_AND_ABOVE" \
        "EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2" \
        "VECTOR_DIMENSION=384" \
        "SIMILARITY_THRESHOLD=0.7" \
        "MAX_RETRIEVED_CHUNKS=10" \
        "LOG_LEVEL=INFO" \
        "ENABLE_MONITORING=true" \
    --output none

echo -e "${GREEN}✅ Function App configuration updated${NC}"

# Enable managed identity for Function App
echo -e "${BLUE}🔑 Enabling managed identity...${NC}"
FUNCTION_PRINCIPAL_ID=$(az functionapp identity assign \
    --resource-group $RESOURCE_GROUP_COMPUTE \
    --name $FUNCTION_APP_NAME \
    --query principalId \
    --output tsv)

# Grant Function App access to Key Vault
az keyvault set-policy \
    --name $KEY_VAULT_NAME \
    --object-id $FUNCTION_PRINCIPAL_ID \
    --secret-permissions get list \
    --output none

echo -e "${GREEN}✅ Managed identity configured${NC}"

echo ""
echo -e "${GREEN}🎉 Production environment setup complete!${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo -e "1. Deploy spiritual texts: ./upload-spiritual-texts.sh"
echo -e "2. Test production endpoints: ./test-production.sh"
echo -e "3. Monitor application: Azure Portal → Application Insights"
echo ""
echo -e "${YELLOW}📊 Cost monitoring: The two-resource-group architecture allows you to:${NC}"
echo -e "   • Pause costs: Delete $RESOURCE_GROUP_COMPUTE (keeps data)"
echo -e "   • Resume service: Re-deploy infrastructure (connects to existing data)"
echo -e "   • Monitor spending: Azure Cost Management"
echo ""
