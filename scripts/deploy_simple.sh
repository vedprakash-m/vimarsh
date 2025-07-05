#!/bin/bash
# Simplified Azure Functions Deployment Script
# Using zip deployment to avoid remote build issues

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
FUNCTION_APP_NAME="vimarsh-backend-app"
RESOURCE_GROUP="vimarsh-compute-rg"
BACKEND_DIR="backend"
DEPLOYMENT_PACKAGE="deployment.zip"

echo -e "${BLUE}🚀 Vimarsh Simplified Deployment${NC}"
echo "=================================================="

# Navigate to backend directory
cd "$BACKEND_DIR"

# Create deployment package
echo -e "${YELLOW}📦 Creating deployment package...${NC}"

# Remove old deployment package if it exists
rm -f "../$DEPLOYMENT_PACKAGE"

# Create zip package excluding unnecessary files
zip -r "../$DEPLOYMENT_PACKAGE" . \
  -x "*.git*" \
  -x "*__pycache__*" \
  -x "*.pytest_cache*" \
  -x "*htmlcov*" \
  -x "*.coverage*" \
  -x "*logs/*" \
  -x "*test_*" \
  -x "*tests/*" \
  -x "*.env" \
  -x "*venv*" \
  -x "*.pyc" \
  -x "*.pyo"

echo -e "${GREEN}✅ Deployment package created${NC}"

# Move back to root
cd ..

# Deploy using Azure CLI
echo -e "${YELLOW}🚀 Deploying via Azure CLI...${NC}"

az functionapp deployment source config-zip \
  --resource-group "$RESOURCE_GROUP" \
  --name "$FUNCTION_APP_NAME" \
  --src "$DEPLOYMENT_PACKAGE"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Deployment successful!${NC}"
    
    # Get function app URL
    FUNCTION_URL=$(az functionapp show --name "$FUNCTION_APP_NAME" --resource-group "$RESOURCE_GROUP" --query "defaultHostName" -o tsv)
    
    if [ ! -z "$FUNCTION_URL" ]; then
        echo -e "${GREEN}🌐 Function App URL: https://$FUNCTION_URL${NC}"
        echo -e "${GREEN}🏥 Health Check: https://$FUNCTION_URL/api/health${NC}"
    fi
    
    # Clean up deployment package
    rm -f "$DEPLOYMENT_PACKAGE"
    
else
    echo -e "${RED}❌ Deployment failed${NC}"
    exit 1
fi

echo -e "${GREEN}🎉 DEPLOYMENT COMPLETE!${NC}"
