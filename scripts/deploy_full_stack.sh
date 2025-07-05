#!/bin/bash
# Vimarsh Full Stack Deployment Script
# Deploys both backend and frontend to existing Azure infrastructure

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
FUNCTION_APP_NAME="vimarsh-backend-app"
STATIC_WEB_APP_NAME="vimarsh-frontend"
RESOURCE_GROUP="vimarsh-compute-rg"
BACKEND_DIR="backend"
FRONTEND_DIR="frontend"

# Store the original directory
ORIGINAL_DIR=$(pwd)

echo -e "${BLUE}🚀 Vimarsh Full Stack Deployment${NC}"
echo "=================================================="
echo "Function App: $FUNCTION_APP_NAME"
echo "Static Web App: $STATIC_WEB_APP_NAME"
echo "Resource Group: $RESOURCE_GROUP"
echo "Backend Directory: $BACKEND_DIR"
echo "Frontend Directory: $FRONTEND_DIR"
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

# Check if directories exist
if [ ! -d "$BACKEND_DIR" ]; then
    echo -e "${RED}❌ Backend directory not found: $BACKEND_DIR${NC}"
    exit 1
fi

if [ ! -d "$FRONTEND_DIR" ]; then
    echo -e "${RED}❌ Frontend directory not found: $FRONTEND_DIR${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All prerequisites met${NC}"

# Verify Azure resources exist
echo -e "${YELLOW}🔍 Verifying Azure resources exist...${NC}"

if ! az functionapp show --name "$FUNCTION_APP_NAME" --resource-group "$RESOURCE_GROUP" &> /dev/null; then
    echo -e "${RED}❌ Function App '$FUNCTION_APP_NAME' not found${NC}"
    exit 1
fi

if ! az staticwebapp show --name "$STATIC_WEB_APP_NAME" --resource-group "$RESOURCE_GROUP" &> /dev/null; then
    echo -e "${RED}❌ Static Web App '$STATIC_WEB_APP_NAME' not found${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Azure resources found${NC}"

# Deploy Backend
echo -e "${YELLOW}🚀 Deploying Backend...${NC}"

# Run backend tests
echo "Testing backend core systems..."
python -c "
try:
    import sys
    sys.path.append('$BACKEND_DIR')
    from core.config import get_config
    from core.logging import get_logger
    from core.health import HealthChecker
    from services.llm_service import EnhancedLLMService
    print('✅ Backend core modules import successfully')
except Exception as e:
    print(f'❌ Backend core module test failed: {e}')
    exit(1)
" 2>/dev/null

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Backend tests passed${NC}"
else
    echo -e "${RED}❌ Backend tests failed${NC}"
    exit 1
fi

# Create backend deployment package
echo "📦 Creating backend deployment package..."
cd "$BACKEND_DIR"

TEMP_DIR=$(mktemp -d)
echo "Using temporary directory: $TEMP_DIR"

# Copy essential backend files
cp -r core "$TEMP_DIR/"
cp -r services "$TEMP_DIR/"
cp -r auth "$TEMP_DIR/"
cp function_app.py "$TEMP_DIR/"
cp requirements.txt "$TEMP_DIR/"
cp host.json "$TEMP_DIR/"

# Clean deployment package
find "$TEMP_DIR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find "$TEMP_DIR" -name "*.pyc" -delete 2>/dev/null || true
find "$TEMP_DIR" -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true

# Create backend zip
cd "$TEMP_DIR"
zip -r "../vimarsh-backend-deploy.zip" . -q
cd ..
rm -rf "$TEMP_DIR"

# Deploy backend
echo "🚀 Deploying backend to Azure..."
az functionapp deployment source config-zip \
    --resource-group "$RESOURCE_GROUP" \
    --name "$FUNCTION_APP_NAME" \
    --src "vimarsh-backend-deploy.zip"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Backend deployment successful!${NC}"
    rm -f "vimarsh-backend-deploy.zip"
else
    echo -e "${RED}❌ Backend deployment failed${NC}"
    exit 1
fi

# Deploy Frontend
echo -e "${YELLOW}🚀 Deploying Frontend...${NC}"
cd "$ORIGINAL_DIR/$FRONTEND_DIR"

# Check if Node.js is installed
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ Node.js/npm is not installed${NC}"
    exit 1
fi

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

# Build frontend
echo "🔨 Building frontend..."
npm run build

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Frontend build successful!${NC}"
else
    echo -e "${RED}❌ Frontend build failed${NC}"
    exit 1
fi

# Deploy frontend
echo "🚀 Deploying frontend to Azure Static Web App (Production)..."

# Check what environments currently exist
echo "🔍 Checking existing environments..."
EXISTING_ENVS=$(az staticwebapp environment list --name "$STATIC_WEB_APP_NAME" --resource-group "$RESOURCE_GROUP" --query "[].{name:name, hostname:hostname}" -o table 2>/dev/null || echo "Could not list environments")
echo "$EXISTING_ENVS"

# Use Azure CLI for production deployment to default environment
echo "Deploying to production environment (default)..."
az staticwebapp environment deploy \
    --name "$STATIC_WEB_APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --source build/ \
    --environment-name default

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Frontend deployment to production successful!${NC}"
    FRONTEND_DEPLOYED="✅ Deployed to Production"
else
    echo -e "${YELLOW}⚠️ Production deployment failed, trying alternative method...${NC}"
    
    # Fallback: Try the simpler deployment method
    echo "Trying direct deployment..."
    az staticwebapp deploy \
        --name "$STATIC_WEB_APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --source build/
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Frontend deployment to production successful!${NC}"
        FRONTEND_DEPLOYED="✅ Deployed to Production"
    else
        echo -e "${YELLOW}⚠️ Frontend deployment failed, manual deployment required${NC}"
        FRONTEND_DEPLOYED="⚠️ Manual step required"
    fi
fi
else
    echo -e "${YELLOW}📋 Frontend Deployment Instructions:${NC}"
    echo "Frontend build completed successfully at: $PWD/build/"
    echo ""
    echo "To deploy the frontend, you can either:"
    echo "1. Install Azure Static Web Apps CLI: 'npm install -g @azure/static-web-apps-cli'"
    echo "2. Use GitHub Actions (recommended for automated deployment)"
    echo "3. Upload manually via Azure Portal"
    FRONTEND_DEPLOYED="⚠️ Manual step required"
fi

# Get URLs and test
echo -e "${YELLOW}🔗 Getting Application URLs...${NC}"

FUNCTION_URL=$(az functionapp show --name "$FUNCTION_APP_NAME" --resource-group "$RESOURCE_GROUP" --query "defaultHostName" -o tsv 2>/dev/null)
STATIC_URL=$(az staticwebapp show --name "$STATIC_WEB_APP_NAME" --resource-group "$RESOURCE_GROUP" --query "defaultHostname" -o tsv 2>/dev/null)

echo ""
echo -e "${GREEN}🎉 DEPLOYMENT SUMMARY${NC}"
echo "=================================================="
echo -e "${BLUE}Backend:${NC}"
echo "• Function App: $FUNCTION_APP_NAME"
echo "• URL: https://$FUNCTION_URL"
echo "• Health Check: https://$FUNCTION_URL/api/health"
echo "• Status: ✅ Deployed"
echo ""
echo -e "${BLUE}Frontend:${NC}"
echo "• Static Web App: $STATIC_WEB_APP_NAME"
echo "• URL: https://$STATIC_URL"
echo "• Build: ✅ Completed"
echo "• Environment: Production"
echo "• Deployment: $FRONTEND_DEPLOYED"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "• Complete frontend deployment using one of the methods above"
echo "• Test backend health endpoint"
echo "• Verify frontend connects to backend correctly"
echo "• Monitor application logs in Azure Portal"
echo "=================================================="

cd "$ORIGINAL_DIR"
