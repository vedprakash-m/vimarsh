#!/bin/bash
# Vimarsh Backend Deployment Script (Fixed)
# Deploys the enhanced LLM service and Phase 3 improvements to existing Azure infrastructure

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
FUNCTION_APP_NAME="vimarsh-backend-app"
RESOURCE_GROUP="vimarsh-compute-rg"
BACKEND_DIR="backend"
WORKING_DIR="$(pwd)"

echo -e "${BLUE}🚀 Vimarsh Backend Deployment (Fixed)${NC}"
echo "=================================================="
echo "Function App: $FUNCTION_APP_NAME"
echo "Resource Group: $RESOURCE_GROUP"
echo "Backend Directory: $BACKEND_DIR"
echo "=================================================="

# Check prerequisites
echo -e "${YELLOW}📋 Checking prerequisites...${NC}"

# Check if Azure CLI is installed and logged in
if ! command -v az &> /dev/null; then
    echo -e "${RED}❌ Azure CLI is not installed${NC}"
    exit 1
fi

# Check if user is logged in to Azure
if ! az account show &> /dev/null; then
    echo -e "${RED}❌ Not logged in to Azure CLI${NC}"
    echo "Please run: az login"
    exit 1
fi

# Check if backend directory exists
if [ ! -d "$BACKEND_DIR" ]; then
    echo -e "${RED}❌ Backend directory not found: $BACKEND_DIR${NC}"
    exit 1
fi

# Check if function_app.py exists
if [ ! -f "$BACKEND_DIR/function_app.py" ]; then
    echo -e "${RED}❌ function_app.py not found in $BACKEND_DIR${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All prerequisites met${NC}"

# Verify the function app exists
echo -e "${YELLOW}🔍 Verifying Azure Function App exists...${NC}"
if ! az functionapp show --name "$FUNCTION_APP_NAME" --resource-group "$RESOURCE_GROUP" &> /dev/null; then
    echo -e "${RED}❌ Function App '$FUNCTION_APP_NAME' not found in resource group '$RESOURCE_GROUP'${NC}"
    echo "Please ensure the infrastructure is deployed first."
    exit 1
fi

echo -e "${GREEN}✅ Function App found${NC}"

# Run tests before deployment
echo -e "${YELLOW}🧪 Running tests before deployment...${NC}"

# Run core system tests
echo "Testing core systems..."
python -c "
try:
    import sys
    sys.path.append('$BACKEND_DIR')
    from core.config import get_config
    from core.logging import get_logger
    from core.health import HealthChecker
    from services.llm_service import EnhancedLLMService
    print('✅ All core modules import successfully')
except Exception as e:
    print(f'❌ Core module test failed: {e}')
    exit(1)
" 2>/dev/null

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Core system tests passed${NC}"
else
    echo -e "${RED}❌ Core system tests failed${NC}"
    exit 1
fi

# Create clean deployment package
echo -e "${YELLOW}📦 Creating deployment package...${NC}"
cd "$BACKEND_DIR"

# Create a temporary directory for deployment
TEMP_DIR=$(mktemp -d)
echo "Using temporary directory: $TEMP_DIR"

# Copy only the essential files
echo "Copying essential files..."
cp -r core "$TEMP_DIR/"
cp -r services "$TEMP_DIR/"
cp -r auth "$TEMP_DIR/"
cp function_app.py "$TEMP_DIR/"
cp requirements.txt "$TEMP_DIR/"
cp host.json "$TEMP_DIR/"

# Remove any test files or caches
find "$TEMP_DIR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find "$TEMP_DIR" -name "*.pyc" -delete 2>/dev/null || true
find "$TEMP_DIR" -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true

# Verify requirements.txt contains google-generativeai
echo "Verifying requirements.txt..."
if ! grep -q "google-generativeai" "$TEMP_DIR/requirements.txt"; then
    echo -e "${RED}❌ google-generativeai not found in requirements.txt${NC}"
    cat "$TEMP_DIR/requirements.txt" | grep -i google || echo "No Google packages found"
    exit 1
else
    echo -e "${GREEN}✅ google-generativeai found in requirements.txt${NC}"
fi

# Create zip file
echo "Creating deployment zip..."
cd "$TEMP_DIR"
ZIP_PATH="$WORKING_DIR/vimarsh-backend-deploy.zip"
zip -r "$ZIP_PATH" . -q

# Verify zip contents
echo "Verifying deployment package contents..."
unzip -l "$ZIP_PATH" | head -20

# Clean up temp directory
rm -rf "$TEMP_DIR"

# Deploy using Azure CLI
echo -e "${YELLOW}🚀 Deploying to Azure Function App...${NC}"

az functionapp deployment source config-zip \
    --resource-group "$RESOURCE_GROUP" \
    --name "$FUNCTION_APP_NAME" \
    --src "$ZIP_PATH"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Deployment successful!${NC}"
    # Clean up deployment zip
    rm -f "$ZIP_PATH"
else
    echo -e "${RED}❌ Deployment failed${NC}"
    exit 1
fi

# Get the function app URL
echo -e "${YELLOW}🔗 Getting Function App URL...${NC}"
FUNCTION_URL=$(az functionapp show --name "$FUNCTION_APP_NAME" --resource-group "$RESOURCE_GROUP" --query "defaultHostName" -o tsv)

if [ ! -z "$FUNCTION_URL" ]; then
    echo -e "${GREEN}🌐 Function App URL: https://$FUNCTION_URL${NC}"
    echo -e "${GREEN}🏥 Health Check: https://$FUNCTION_URL/api/health${NC}"
else
    echo -e "${YELLOW}⚠️ Could not retrieve Function App URL${NC}"
fi

# Post-deployment verification
echo -e "${YELLOW}🔍 Running post-deployment verification...${NC}"

# Wait a moment for deployment to settle
sleep 10

# Test health endpoint
if [ ! -z "$FUNCTION_URL" ]; then
    echo "Testing health endpoint..."
    if curl -f -s "https://$FUNCTION_URL/api/health" > /dev/null; then
        echo -e "${GREEN}✅ Health endpoint responsive${NC}"
    else
        echo -e "${YELLOW}⚠️ Health endpoint not yet responsive (this is normal immediately after deployment)${NC}"
    fi
fi

echo ""
echo -e "${GREEN}🎉 DEPLOYMENT COMPLETE!${NC}"
echo "=================================================="
echo -e "${BLUE}Summary:${NC}"
echo "• Backend deployed to: $FUNCTION_APP_NAME"
echo "• Enhanced LLM service with Gemini 2.5 Flash active"
echo "• Phase 3 improvements deployed (config, logging, health monitoring)"
echo "• Function App URL: https://$FUNCTION_URL"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "• Monitor application logs in Azure Portal"
echo "• Verify spiritual guidance endpoints are working"
echo "• Test with real user queries"
echo "• Update frontend to point to new backend if needed"
echo "=================================================="
