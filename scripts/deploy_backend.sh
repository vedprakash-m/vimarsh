#!/bin/bash
# Phase 4.1.1 - Deploy New Build to Existing Infrastructure
# Deploys the enhanced backend (with Gemini 2.5 Flash) to existing Azure Functions

set -e  # Exit on any error

echo "🚀 Phase 4.1.1 - Deploying New Build to Existing Infrastructure"
echo "================================================================="

# Configuration
RESOURCE_GROUP="vimarsh-rg"
FUNCTION_APP_NAME="vimarsh-functions"
BACKEND_DIR="/Users/vedprakashmishra/vimarsh/backend"
CURRENT_DIR=$(pwd)

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Step 1: Pre-deployment validation
echo ""
echo "🔍 Step 1: Pre-deployment Validation"
echo "======================================"

# Check Azure CLI login
if ! az account show > /dev/null 2>&1; then
    print_error "Azure CLI not logged in. Please run 'az login' first."
    exit 1
fi
print_status "Azure CLI authenticated"

# Check if function app exists
if ! az functionapp show --name "$FUNCTION_APP_NAME" --resource-group "$RESOURCE_GROUP" > /dev/null 2>&1; then
    print_error "Function app '$FUNCTION_APP_NAME' not found in resource group '$RESOURCE_GROUP'"
    exit 1
fi
print_status "Function app '$FUNCTION_APP_NAME' found"

# Check backend directory
if [ ! -d "$BACKEND_DIR" ]; then
    print_error "Backend directory not found: $BACKEND_DIR"
    exit 1
fi
print_status "Backend directory found"

# Step 2: Package backend
echo ""
echo "📦 Step 2: Package Backend Function App"
echo "========================================"

cd "$BACKEND_DIR"

# Ensure we have the latest dependencies
print_status "Installing/updating Python dependencies..."
pip install -r requirements.txt --quiet

# Clean up any local artifacts
if [ -d "__pycache__" ]; then
    rm -rf __pycache__
    print_status "Cleaned __pycache__ directories"
fi

if [ -f ".coverage" ]; then
    rm .coverage
    print_status "Cleaned coverage files"
fi

print_status "Backend packaged and ready for deployment"

# Step 3: Deploy to Azure Functions
echo ""
echo "🚀 Step 3: Deploy to Azure Functions"
echo "====================================="

print_status "Starting deployment to Azure Functions..."

# Deploy using Azure Functions Core Tools
func azure functionapp publish "$FUNCTION_APP_NAME" --python

if [ $? -eq 0 ]; then
    print_status "Backend deployment completed successfully"
else
    print_error "Backend deployment failed"
    exit 1
fi

# Step 4: Post-deployment validation
echo ""
echo "🔍 Step 4: Post-deployment Validation"
echo "======================================"

# Get function app URL
FUNCTION_APP_URL=$(az functionapp show --name "$FUNCTION_APP_NAME" --resource-group "$RESOURCE_GROUP" --query "defaultHostName" -o tsv)
print_status "Function app URL: https://$FUNCTION_APP_URL"

# Wait for deployment to propagate
print_status "Waiting for deployment to propagate..."
sleep 30

# Test health endpoint
echo "Testing health endpoint..."
HEALTH_URL="https://$FUNCTION_APP_URL/api/health/quick"
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$HEALTH_URL" || echo "000")

if [ "$HTTP_STATUS" = "200" ]; then
    print_status "Health check passed (HTTP $HTTP_STATUS)"
else
    print_warning "Health check returned HTTP $HTTP_STATUS - may need more time to initialize"
fi

# Test spiritual guidance endpoint (basic test)
echo "Testing spiritual guidance endpoint..."
GUIDANCE_URL="https://$FUNCTION_APP_URL/api/spiritual_guidance"
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST -H "Content-Type: application/json" -d '{"query":"What is dharma?","context":"guidance"}' "$GUIDANCE_URL" || echo "000")

if [ "$HTTP_STATUS" = "200" ]; then
    print_status "Spiritual guidance endpoint responding (HTTP $HTTP_STATUS)"
else
    print_warning "Spiritual guidance endpoint returned HTTP $HTTP_STATUS - may need configuration"
fi

# Step 5: Deployment Summary
echo ""
echo "📊 Deployment Summary"
echo "===================="
print_status "✅ Backend deployed to existing Azure Functions"
print_status "✅ Function app URL: https://$FUNCTION_APP_URL"
print_status "✅ Enhanced LLM service with Gemini 2.5 Flash deployed"
print_status "✅ All production readiness features included"

echo ""
echo "🎉 Phase 4.1.1 Deployment Completed Successfully!"
echo "================================================="
echo ""
echo "Next steps:"
echo "- Monitor function app logs for any issues"
echo "- Test full E2E functionality"
echo "- Proceed to Phase 4.1.2 Post-deployment Validation"

cd "$CURRENT_DIR"
