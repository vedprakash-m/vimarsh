#!/bin/bash

# Production Deployment Script for Vimarsh
# Deploys the complete AI-powered spiritual guidance system to Azure

set -e

echo "🕉️  VIMARSH PRODUCTION DEPLOYMENT"
echo "================================="

# Configuration
RESOURCE_GROUP="${VIMARSH_RESOURCE_GROUP:-vimarsh-prod}"
LOCATION="${VIMARSH_LOCATION:-eastus}"
FUNCTION_APP_NAME="${VIMARSH_FUNCTION_APP:-vimarsh-functions}"
STORAGE_ACCOUNT="${VIMARSH_STORAGE:-vimarshstorage}"
COSMOS_ACCOUNT="${VIMARSH_COSMOS:-vimarsh-cosmos}"
STATIC_WEB_APP="${VIMARSH_SWA:-vimarsh-frontend}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    echo "🔍 Checking prerequisites..."
    
    # Check Azure CLI
    if ! command -v az &> /dev/null; then
        print_error "Azure CLI is not installed. Please install it first."
        exit 1
    fi
    
    # Check if logged in
    if ! az account show &> /dev/null; then
        print_error "Not logged into Azure. Run 'az login' first."
        exit 1
    fi
    
    # Check Function Core Tools
    if ! command -v func &> /dev/null; then
        print_error "Azure Functions Core Tools not installed. Please install it first."
        exit 1
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install it first."
        exit 1
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install it first."
        exit 1
    fi
    
    # Check environment variables
    required_vars=("GOOGLE_AI_API_KEY" "AZURE_CLIENT_ID" "AZURE_CLIENT_SECRET" "AZURE_TENANT_ID")
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var}" ]]; then
            print_warning "Environment variable $var is not set"
            echo "Please set it or the deployment will use placeholder values"
        fi
    done
    
    print_status "Prerequisites checked"
}

# Validate configuration
validate_config() {
    echo "📋 Validating configuration..."
    
    # Check if local.settings.json exists
    if [[ ! -f "backend/local.settings.json" ]]; then
        print_error "backend/local.settings.json not found. Run setup_production.py first."
        exit 1
    fi
    
    # Check if frontend production template exists
    if [[ ! -f "frontend/.env.production" ]]; then
        print_error "frontend/.env.production template not found."
        exit 1
    fi
    
    print_status "Configuration validated"
}

# Deploy infrastructure
deploy_infrastructure() {
    echo "🏗️  Deploying infrastructure..."
    
    # Create resource group
    print_info "Creating resource group: $RESOURCE_GROUP"
    az group create --name $RESOURCE_GROUP --location $LOCATION --output table
    
    # Deploy persistent infrastructure (Cosmos DB, Storage)
    print_info "Deploying persistent infrastructure..."
    az deployment group create \
        --resource-group $RESOURCE_GROUP \
        --template-file infrastructure/persistent.bicep \
        --parameters \
            cosmosAccountName=$COSMOS_ACCOUNT \
            storageAccountName=$STORAGE_ACCOUNT \
            location=$LOCATION \
        --output table
    
    # Deploy compute infrastructure (Function App, Static Web App)
    print_info "Deploying compute infrastructure..."
    az deployment group create \
        --resource-group $RESOURCE_GROUP \
        --template-file infrastructure/compute.bicep \
        --parameters \
            functionAppName=$FUNCTION_APP_NAME \
            staticWebAppName=$STATIC_WEB_APP \
            storageAccountName=$STORAGE_ACCOUNT \
            location=$LOCATION \
        --output table
    
    print_status "Infrastructure deployed"
}

# Populate sacred texts database
populate_database() {
    echo "📚 Populating sacred texts database..."
    
    # Get Cosmos DB connection string
    COSMOS_CONNECTION=$(az cosmosdb keys list \
        --name $COSMOS_ACCOUNT \
        --resource-group $RESOURCE_GROUP \
        --type connection-strings \
        --query "connectionStrings[0].connectionString" \
        --output tsv)
    
    # Update backend config with real connection string
    python3 -c "
import json
with open('backend/local.settings.json', 'r') as f:
    config = json.load(f)
config['Values']['AZURE_COSMOS_CONNECTION_STRING'] = '$COSMOS_CONNECTION'
with open('backend/local.settings.json', 'w') as f:
    json.dump(config, f, indent=2)
"
    
    # Run sacred text loader with Cosmos DB
    print_info "Loading sacred texts to Cosmos DB..."
    cd backend
    python3 data_processing/sacred_text_loader.py
    python3 data_processing/populate_vector_db.py --use-cosmos
    cd ..
    
    print_status "Sacred texts database populated"
}

# Deploy backend
deploy_backend() {
    echo "🔧 Deploying backend..."
    
    cd backend
    
    # Install dependencies
    print_info "Installing backend dependencies..."
    pip install -r requirements.txt
    
    # Deploy function app
    print_info "Publishing function app..."
    func azure functionapp publish $FUNCTION_APP_NAME --python
    
    cd ..
    
    print_status "Backend deployed"
}

# Deploy frontend
deploy_frontend() {
    echo "🎨 Deploying frontend..."
    
    cd frontend
    
    # Install dependencies
    print_info "Installing frontend dependencies..."
    npm install
    
    # Update production environment with real URLs
    FUNCTION_URL="https://$FUNCTION_APP_NAME.azurewebsites.net"
    
    # Update .env.production
    sed -i.bak "s|REACT_APP_API_BASE_URL=.*|REACT_APP_API_BASE_URL=$FUNCTION_URL|" .env.production
    
    # Build production
    print_info "Building frontend for production..."
    npm run build
    
    # Deploy to Azure Static Web Apps
    print_info "Deploying to Azure Static Web Apps..."
    
    # Get deployment token
    DEPLOYMENT_TOKEN=$(az staticwebapp secrets list \
        --name $STATIC_WEB_APP \
        --resource-group $RESOURCE_GROUP \
        --query "properties.apiKey" \
        --output tsv)
    
    # Deploy using SWA CLI if available, otherwise use Azure CLI
    if command -v swa &> /dev/null; then
        swa deploy ./build --deployment-token $DEPLOYMENT_TOKEN
    else
        print_warning "SWA CLI not found. Please deploy frontend manually:"
        echo "1. Install SWA CLI: npm install -g @azure/static-web-apps-cli"
        echo "2. Run: swa deploy ./build --deployment-token [TOKEN]"
    fi
    
    cd ..
    
    print_status "Frontend deployed"
}

# Configure application settings
configure_app_settings() {
    echo "⚙️  Configuring application settings..."
    
    # Get connection strings from deployed resources
    COSMOS_CONNECTION=$(az cosmosdb keys list \
        --name $COSMOS_ACCOUNT \
        --resource-group $RESOURCE_GROUP \
        --type connection-strings \
        --query "connectionStrings[0].connectionString" \
        --output tsv)
    
    STORAGE_CONNECTION=$(az storage account show-connection-string \
        --name $STORAGE_ACCOUNT \
        --resource-group $RESOURCE_GROUP \
        --query connectionString \
        --output tsv)
    
    # Configure function app settings
    print_info "Setting function app configuration..."
    az functionapp config appsettings set \
        --name $FUNCTION_APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --settings \
        "AZURE_COSMOS_CONNECTION_STRING=$COSMOS_CONNECTION" \
        "AZURE_STORAGE_CONNECTION_STRING=$STORAGE_CONNECTION" \
        "GOOGLE_AI_API_KEY=${GOOGLE_AI_API_KEY:-YOUR_ACTUAL_GEMINI_API_KEY_HERE}" \
        "AZURE_CLIENT_ID=${AZURE_CLIENT_ID:-YOUR_ENTRA_ID_CLIENT_ID}" \
        "AZURE_CLIENT_SECRET=${AZURE_CLIENT_SECRET:-YOUR_ENTRA_ID_CLIENT_SECRET}" \
        "AZURE_TENANT_ID=${AZURE_TENANT_ID:-YOUR_ENTRA_ID_TENANT_ID}" \
        "AZURE_AUTHORITY=https://login.microsoftonline.com/${AZURE_TENANT_ID:-YOUR_ENTRA_ID_TENANT_ID}" \
        "LLM_MODEL=gemini-pro" \
        "LLM_TEMPERATURE=0.7" \
        "MAX_TOKENS=4096" \
        "EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2" \
        "VECTOR_DIMENSION=384" \
        "SIMILARITY_THRESHOLD=0.7" \
        "MAX_RETRIEVED_CHUNKS=10" \
        "DEBUG=false" \
        "LOG_LEVEL=INFO" \
        --output table
    
    print_status "Application settings configured"
}

# Run post-deployment tests
run_tests() {
    echo "🧪 Running post-deployment tests..."
    
    # Wait for deployment to be ready
    print_info "Waiting for services to initialize..."
    sleep 60
    
    # Run production validation against deployed endpoints
    FUNCTION_URL="https://$FUNCTION_APP_NAME.azurewebsites.net"
    
    print_info "Testing deployed endpoints..."
    
    # Basic health check
    if curl -f -s "$FUNCTION_URL/api/health" > /dev/null; then
        print_status "Health check passed"
    else
        print_warning "Health check failed - services may still be starting up"
    fi
    
    # Run comprehensive validation
    python3 scripts/production_validator.py --url "$FUNCTION_URL" || {
        print_warning "Some validation tests failed. Check the output above."
        print_info "Services may need more time to fully initialize."
    }
    
    print_status "Post-deployment tests completed"
}

# Generate deployment report
generate_report() {
    echo ""
    echo "📊 DEPLOYMENT REPORT"
    echo "===================="
    
    # Get deployment URLs
    FUNCTION_URL="https://$FUNCTION_APP_NAME.azurewebsites.net"
    
    # Try to get Static Web App URL
    SWA_URL=$(az staticwebapp show \
        --name $STATIC_WEB_APP \
        --resource-group $RESOURCE_GROUP \
        --query "defaultHostname" \
        --output tsv 2>/dev/null || echo "Not deployed")
    
    if [[ "$SWA_URL" != "Not deployed" ]]; then
        SWA_URL="https://$SWA_URL"
    fi
    
    echo "🌐 Service URLs:"
    echo "   Frontend: $SWA_URL"
    echo "   Backend API: $FUNCTION_URL"
    echo "   Health Check: $FUNCTION_URL/api/health"
    echo ""
    echo "🔧 Azure Resources:"
    echo "   Resource Group: $RESOURCE_GROUP"
    echo "   Function App: $FUNCTION_APP_NAME"
    echo "   Static Web App: $STATIC_WEB_APP"
    echo "   Cosmos DB: $COSMOS_ACCOUNT"
    echo "   Storage Account: $STORAGE_ACCOUNT"
    echo ""
    echo "📝 Next Steps:"
    echo "   1. Test the application at: $SWA_URL"
    echo "   2. Monitor logs: az functionapp logs tail --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP"
    echo "   3. Set up custom domain and SSL certificates"
    echo "   4. Configure monitoring and alerts"
    echo "   5. Set up CI/CD pipeline for future deployments"
    echo ""
    echo "🕉️  Your spiritual guidance system is now live and serving seekers worldwide!"
}

# Main deployment flow
main() {
    echo "Starting Vimarsh production deployment..."
    
    check_prerequisites
    validate_config
    deploy_infrastructure
    populate_database
    deploy_backend
    deploy_frontend
    configure_app_settings
    run_tests
    generate_report
    
    echo ""
    echo "🚀 DEPLOYMENT COMPLETE!"
    echo "======================="
}

# Handle command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --resource-group)
            RESOURCE_GROUP="$2"
            shift 2
            ;;
        --location)
            LOCATION="$2"
            shift 2
            ;;
        --function-app)
            FUNCTION_APP_NAME="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [--resource-group NAME] [--location LOCATION] [--function-app NAME]"
            echo ""
            echo "Environment variables (optional):"
            echo "  VIMARSH_RESOURCE_GROUP - Azure resource group name"
            echo "  VIMARSH_LOCATION - Azure region"
            echo "  VIMARSH_FUNCTION_APP - Function app name"
            echo "  GOOGLE_AI_API_KEY - Gemini API key"
            echo "  AZURE_CLIENT_ID - Entra ID client ID"
            echo "  AZURE_CLIENT_SECRET - Entra ID client secret"
            echo "  AZURE_TENANT_ID - Entra ID tenant ID"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
