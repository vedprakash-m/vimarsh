#!/bin/bash

# Vimarsh Manual Deployment Guide
# This script provides step-by-step deployment commands for Azure
# Run each section manually to understand the deployment process

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🕉️  Vimarsh Azure Deployment Guide${NC}"
echo "=================================================="
echo ""

# Configuration - Updated to use West US 2 due to East US capacity issues
LOCATION="westus2"
DB_RESOURCE_GROUP="vimarsh-persistent-rg"
COMPUTE_RESOURCE_GROUP="vimarsh-compute-rg"

# Function to select the best available region for Cosmos DB
select_region() {
    echo -e "${YELLOW}Selecting optimal region for deployment...${NC}"
    
    # Priority list of regions (best performance and availability)
    REGIONS=("westus2" "centralus" "eastus2" "westeurope" "southeastasia")
    
    for region in "${REGIONS[@]}"; do
        echo "Testing availability in $region..."
        
        # Test if we can create a Cosmos DB in this region by checking quotas
        available=$(az provider show --namespace Microsoft.DocumentDB --query "resourceTypes[?resourceType=='databaseAccounts'].locations[]" -o tsv | grep -i "$region" | wc -l)
        
        if [ "$available" -gt 0 ]; then
            echo -e "${GREEN}✅ $region is available${NC}"
            LOCATION="$region"
            return 0
        else
            echo -e "${YELLOW}⚠️  $region may have limited availability${NC}"
        fi
    done
    
    # Default to West US 2 if no specific region is found
    LOCATION="westus2"
    echo -e "${BLUE}Using default region: $LOCATION${NC}"
}

# Select the best region
select_region

echo -e "${YELLOW}Step 1: Set Environment Variables${NC}"
echo "Before proceeding, ensure you have set:"
echo "export GEMINI_API_KEY='your-api-key-here'"
echo ""
echo "Current status:"
echo "GEMINI_API_KEY: ${GEMINI_API_KEY:+SET}"
echo ""

if [[ -z "$GEMINI_API_KEY" ]]; then
    echo -e "${RED}❌ GEMINI_API_KEY not set. Please set it first:${NC}"
    echo "export GEMINI_API_KEY='your-api-key-here'"
    echo "Get your key from: https://aistudio.google.com/app/apikey"
    exit 1
fi

echo -e "${GREEN}✅ Environment variables are set${NC}"
echo ""

echo -e "${YELLOW}Step 2: Create Resource Groups${NC}"
echo "Creating two resource groups for cost optimization..."

# Create persistent resource group
echo "Creating persistent resource group (vimarsh-db-rg)..."
az group create \
    --name "$DB_RESOURCE_GROUP" \
    --location "$LOCATION" \
    --tags project=vimarsh type=persistent costStrategy=pause-resume

# Create compute resource group
echo "Creating compute resource group (vimarsh-rg)..."
az group create \
    --name "$COMPUTE_RESOURCE_GROUP" \
    --location "$LOCATION" \
    --tags project=vimarsh type=compute costStrategy=pause-resume

echo -e "${GREEN}✅ Resource groups created${NC}"
echo ""

echo -e "${YELLOW}Step 3: Deploy Persistent Resources${NC}"
echo "Deploying database, storage, and key vault in $LOCATION..."

# Deploy with retry logic for Cosmos DB capacity issues
deploy_persistent_resources() {
    local attempt=1
    local max_attempts=3
    
    while [ $attempt -le $max_attempts ]; do
        echo "Deployment attempt $attempt/$max_attempts..."
        
        if az deployment group create \
            --resource-group "$DB_RESOURCE_GROUP" \
            --template-file infrastructure/persistent.bicep \
            --parameters location="$LOCATION" geminiApiKey="$GEMINI_API_KEY" \
            --output table; then
            echo -e "${GREEN}✅ Persistent resources deployed successfully${NC}"
            return 0
        else
            echo -e "${YELLOW}⚠️  Deployment attempt $attempt failed${NC}"
            
            if [ $attempt -lt $max_attempts ]; then
                echo "Trying alternative region..."
                # Try next region in priority list
                case $LOCATION in
                    "westus2") LOCATION="centralus" ;;
                    "centralus") LOCATION="eastus2" ;;
                    "eastus2") LOCATION="westeurope" ;;
                    "westeurope") LOCATION="southeastasia" ;;
                    *) LOCATION="westus2" ;;
                esac
                echo "Switching to region: $LOCATION"
                
                # Update resource group location
                az group delete --name "$DB_RESOURCE_GROUP" --yes --no-wait 2>/dev/null || true
                sleep 10
                az group create \
                    --name "$DB_RESOURCE_GROUP" \
                    --location "$LOCATION" \
                    --tags project=vimarsh type=persistent costStrategy=pause-resume
            fi
            
            ((attempt++))
        fi
    done
    
    echo -e "${RED}❌ Failed to deploy persistent resources after $max_attempts attempts${NC}"
    echo "Please try again later or contact Azure support for region quota increase"
    exit 1
}

deploy_persistent_resources

echo -e "${GREEN}✅ Persistent resources deployed${NC}"
echo ""

echo -e "${YELLOW}Step 4: Get Connection Strings${NC}"
echo "Retrieving connection information for compute resources..."

COSMOS_ENDPOINT=$(az cosmosdb show --name "vimarsh-db" --resource-group "$DB_RESOURCE_GROUP" --query documentEndpoint -o tsv)
KEY_VAULT_URI=$(az keyvault show --name "vimarsh-kv" --resource-group "$DB_RESOURCE_GROUP" --query properties.vaultUri -o tsv)

echo "Cosmos DB Endpoint: $COSMOS_ENDPOINT"
echo "Key Vault URI: $KEY_VAULT_URI"
echo ""

echo -e "${YELLOW}Step 5: Deploy Compute Resources${NC}"
echo "Deploying Azure Functions and Static Web App..."

az deployment group create \
    --resource-group "$COMPUTE_RESOURCE_GROUP" \
    --template-file infrastructure/compute.bicep \
    --parameters location="$LOCATION" \
                keyVaultUri="$KEY_VAULT_URI" \
                keyVaultName="vimarsh-kv" \
                cosmosDbEndpoint="$COSMOS_ENDPOINT" \
                expertReviewEmail="vedprakash.m@me.com" \
    --output table

echo -e "${GREEN}✅ Compute resources deployed${NC}"
echo ""

echo -e "${YELLOW}Step 6: Deploy Backend Code${NC}"
echo "Deploying Azure Functions backend..."

cd backend
zip -r ../function-app.zip . -x "__pycache__/*" "*.pyc" ".pytest_cache/*" "htmlcov/*" "logs/*"
cd ..

az functionapp deployment source config-zip \
    --resource-group "$COMPUTE_RESOURCE_GROUP" \
    --name "vimarsh-functions" \
    --src function-app.zip

echo -e "${GREEN}✅ Backend deployed${NC}"
echo ""

echo -e "${YELLOW}Step 7: Deploy Frontend${NC}"
echo "Deploying Static Web App frontend..."

# Get the Static Web App deployment token
SWA_TOKEN=$(az staticwebapp secrets list --name "vimarsh-web" --resource-group "$COMPUTE_RESOURCE_GROUP" --query "properties.apiKey" -o tsv)

# Deploy using Azure Static Web Apps CLI
npx @azure/static-web-apps-cli deploy \
    --app-location "./frontend/build" \
    --deployment-token "$SWA_TOKEN"

echo -e "${GREEN}✅ Frontend deployed${NC}"
echo ""

echo -e "${YELLOW}Step 8: Get Deployment URLs${NC}"

FUNCTION_URL=$(az functionapp show --name "vimarsh-functions" --resource-group "$COMPUTE_RESOURCE_GROUP" --query defaultHostName -o tsv)
SWA_URL=$(az staticwebapp show --name "vimarsh-web" --resource-group "$COMPUTE_RESOURCE_GROUP" --query defaultHostname -o tsv)

echo ""
echo -e "${GREEN}🎉 Deployment Complete!${NC}"
echo "=================================================="
echo -e "${BLUE}Frontend URL:${NC} https://$SWA_URL"
echo -e "${BLUE}Backend URL:${NC} https://$FUNCTION_URL"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Test the application at the frontend URL"
echo "2. Monitor costs in Azure portal"
echo "3. Use pause/resume strategy to optimize costs"
echo "4. Set up monitoring and alerting"
echo ""
echo -e "${YELLOW}Cost Optimization:${NC}"
echo "- To pause: az group delete --name $COMPUTE_RESOURCE_GROUP --yes"
echo "- To resume: Re-run this deployment script"
echo "- Data persists in $DB_RESOURCE_GROUP during pause"
