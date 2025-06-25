#!/bin/bash

# Vimarsh Automated Deployment Script
# Usage: ./deploy.sh [environment] [options]
# Environments: dev, staging, prod
# Options: --skip-infrastructure, --data-only, --recovery-mode

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Default values
ENVIRONMENT="dev"
SKIP_INFRASTRUCTURE=false
DATA_ONLY=false
RECOVERY_MODE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        dev|staging|prod)
            ENVIRONMENT="$1"
            shift
            ;;
        --skip-infrastructure)
            SKIP_INFRASTRUCTURE=true
            shift
            ;;
        --data-only)
            DATA_ONLY=true
            shift
            ;;
        --recovery-mode)
            RECOVERY_MODE=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [environment] [options]"
            echo "Environments: dev, staging, prod"
            echo "Options:"
            echo "  --skip-infrastructure  Skip Azure resource creation"
            echo "  --data-only           Only deploy data and content"
            echo "  --recovery-mode       Deploy in disaster recovery mode"
            echo "  -h, --help           Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown parameter: $1"
            exit 1
            ;;
    esac
done

# Environment-specific configuration
case $ENVIRONMENT in
    dev)
        RESOURCE_GROUP="vimarsh-dev"
        LOCATION="eastus"
        FUNCTION_APP_NAME="vimarsh-functions-dev"
        COSMOS_DB_NAME="vimarsh-cosmos-dev"
        STATIC_WEB_APP_NAME="vimarsh-web-dev"
        APP_INSIGHTS_NAME="vimarsh-insights-dev"
        STORAGE_ACCOUNT_NAME="vimarshistoragedev"
        ;;
    staging)
        RESOURCE_GROUP="vimarsh-staging"
        LOCATION="eastus"
        FUNCTION_APP_NAME="vimarsh-functions-staging"
        COSMOS_DB_NAME="vimarsh-cosmos-staging"
        STATIC_WEB_APP_NAME="vimarsh-web-staging"
        APP_INSIGHTS_NAME="vimarsh-insights-staging"
        STORAGE_ACCOUNT_NAME="vimarshistoragestaging"
        ;;
    prod)
        RESOURCE_GROUP="vimarsh-prod"
        LOCATION="eastus"
        FUNCTION_APP_NAME="vimarsh-functions-prod"
        COSMOS_DB_NAME="vimarsh-cosmos-prod"
        STATIC_WEB_APP_NAME="vimarsh-web-prod"
        APP_INSIGHTS_NAME="vimarsh-insights-prod"
        STORAGE_ACCOUNT_NAME="vimarshistorageprod"
        ;;
esac

echo -e "${BLUE}🕉️  Vimarsh Deployment Script${NC}"
echo -e "${BLUE}Environment: ${YELLOW}$ENVIRONMENT${NC}"
echo -e "${BLUE}Resource Group: ${YELLOW}$RESOURCE_GROUP${NC}"
echo -e "${BLUE}Location: ${YELLOW}$LOCATION${NC}"
echo ""

# Verify prerequisites
echo -e "${BLUE}🔍 Checking prerequisites...${NC}"

# Check Azure CLI
if ! command -v az &> /dev/null; then
    echo -e "${RED}❌ Azure CLI is not installed${NC}"
    echo "Please install Azure CLI: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check if logged in to Azure
if ! az account show &> /dev/null; then
    echo -e "${YELLOW}⚠️  Not logged in to Azure. Please login...${NC}"
    az login
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed${NC}"
    echo "Please install Node.js 18.x or higher"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    echo "Please install Python 3.12 or higher"
    exit 1
fi

# Check Bicep CLI (for infrastructure deployment)
if ! command -v bicep &> /dev/null; then
    echo -e "${YELLOW}⚠️  Bicep CLI not found. Installing...${NC}"
    az bicep install
    if ! command -v bicep &> /dev/null; then
        echo -e "${RED}❌ Failed to install Bicep CLI${NC}"
        echo "Please install Bicep CLI manually: https://docs.microsoft.com/en-us/azure/azure-resource-manager/bicep/install"
        exit 1
    fi
fi

# Check required environment variables
if [[ -z "$GEMINI_API_KEY" ]]; then
    echo -e "${YELLOW}⚠️  GEMINI_API_KEY not set. Please provide your Gemini API key:${NC}"
    read -s -p "Gemini API Key: " GEMINI_API_KEY
    echo ""
    export GEMINI_API_KEY
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"

# Function to create Azure infrastructure using Bicep
create_infrastructure() {
    echo -e "${BLUE}🏗️  Creating Azure infrastructure using Bicep templates...${NC}"

    # Create resource group
    echo "Creating resource group..."
    az group create \
        --name "$RESOURCE_GROUP" \
        --location "$LOCATION" \
        --tags project=vimarsh environment="$ENVIRONMENT"

    # Deploy infrastructure using Bicep template
    echo "Deploying infrastructure from Bicep template..."
    if [[ -f "$PROJECT_ROOT/infrastructure/main.bicep" ]]; then
        az deployment group create \
            --resource-group "$RESOURCE_GROUP" \
            --template-file "$PROJECT_ROOT/infrastructure/main.bicep" \
            --parameters "$PROJECT_ROOT/infrastructure/parameters/$ENVIRONMENT.parameters.json" \
            --output table
        echo -e "${GREEN}✅ Bicep deployment completed${NC}"
    else
        echo -e "${YELLOW}⚠️  Bicep template not found, falling back to individual resource creation...${NC}"
        create_infrastructure_individual_resources
    fi
}

# Function to create individual Azure resources (fallback)
create_infrastructure_individual_resources() {

    # Create storage account
    echo "Creating storage account..."
    az storage account create \
        --name "$STORAGE_ACCOUNT_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --location "$LOCATION" \
        --sku Standard_LRS \
        --kind StorageV2

    # Create Application Insights
    echo "Creating Application Insights..."
    az monitor app-insights component create \
        --app "$APP_INSIGHTS_NAME" \
        --location "$LOCATION" \
        --resource-group "$RESOURCE_GROUP" \
        --kind web \
        --application-type web

    # Create Cosmos DB
    echo "Creating Cosmos DB..."
    az cosmosdb create \
        --name "$COSMOS_DB_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --default-consistency-level Session \
        --locations regionName="$LOCATION" \
        --capabilities EnableServerless EnableVectorSearch \
        --backup-policy-type Continuous

    # Create Cosmos DB database and containers
    echo "Creating Cosmos DB database and containers..."
    az cosmosdb sql database create \
        --account-name "$COSMOS_DB_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --name SpiritualGuidance

    az cosmosdb sql container create \
        --account-name "$COSMOS_DB_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --database-name SpiritualGuidance \
        --name Documents \
        --partition-key-path "/source" \
        --throughput 400

    az cosmosdb sql container create \
        --account-name "$COSMOS_DB_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --database-name SpiritualGuidance \
        --name Vectors \
        --partition-key-path "/document_id" \
        --throughput 400

    # Create Function App
    echo "Creating Function App..."
    az functionapp create \
        --name "$FUNCTION_APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --storage-account "$STORAGE_ACCOUNT_NAME" \
        --consumption-plan-location "$LOCATION" \
        --runtime python \
        --runtime-version 3.12 \
        --functions-version 4 \
        --app-insights "$APP_INSIGHTS_NAME" \
        --disable-app-insights false

    echo -e "${GREEN}✅ Infrastructure created successfully${NC}"
}

# Function to configure application settings
configure_app_settings() {
    echo -e "${BLUE}⚙️  Configuring application settings...${NC}"

    # Get connection strings and keys
    COSMOS_CONNECTION_STRING=$(az cosmosdb keys list \
        --name "$COSMOS_DB_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --type connection-strings \
        --query 'connectionStrings[0].connectionString' \
        --output tsv)

    APPINSIGHTS_KEY=$(az monitor app-insights component show \
        --app "$APP_INSIGHTS_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --query 'instrumentationKey' \
        --output tsv)

    # Configure Function App settings
    az functionapp config appsettings set \
        --name "$FUNCTION_APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --settings \
            "GEMINI_API_KEY=$GEMINI_API_KEY" \
            "COSMOS_CONNECTION_STRING=$COSMOS_CONNECTION_STRING" \
            "APPINSIGHTS_INSTRUMENTATIONKEY=$APPINSIGHTS_KEY" \
            "FUNCTIONS_WORKER_RUNTIME=python" \
            "ENVIRONMENT=$ENVIRONMENT" \
            "LOG_LEVEL=INFO" \
            "EXPERT_REVIEW_EMAIL=experts@example.com" \
            "MAX_QUERY_LENGTH=1000" \
            "RESPONSE_TIMEOUT_SECONDS=30"

    echo -e "${GREEN}✅ Application settings configured${NC}"
}

# Function to deploy backend
deploy_backend() {
    echo -e "${BLUE}🐍 Deploying backend...${NC}"

    cd "$PROJECT_ROOT/backend"

    # Install dependencies
    if [[ ! -d "venv" ]]; then
        python3 -m venv venv
    fi

    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt

    # Deploy to Azure Functions
    func azure functionapp publish "$FUNCTION_APP_NAME"

    cd "$PROJECT_ROOT"

    echo -e "${GREEN}✅ Backend deployed successfully${NC}"
}

# Function to deploy frontend
deploy_frontend() {
    echo -e "${BLUE}⚛️  Deploying frontend...${NC}"

    # Get Function App URL
    FUNCTION_APP_URL=$(az functionapp show \
        --name "$FUNCTION_APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --query 'defaultHostName' \
        --output tsv)

    # Create Static Web App (if doesn't exist)
    if ! az staticwebapp show --name "$STATIC_WEB_APP_NAME" --resource-group "$RESOURCE_GROUP" &> /dev/null; then
        echo "Creating Static Web App..."
        az staticwebapp create \
            --name "$STATIC_WEB_APP_NAME" \
            --resource-group "$RESOURCE_GROUP" \
            --source https://github.com/vedprakash-m/vimarsh \
            --branch main \
            --app-location "/frontend" \
            --build-location "/frontend/build"
    fi

    # Configure Static Web App settings
    az staticwebapp appsettings set \
        --name "$STATIC_WEB_APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --setting-names \
            REACT_APP_API_BASE_URL="https://$FUNCTION_APP_URL/api" \
            REACT_APP_ENVIRONMENT="$ENVIRONMENT"

    echo -e "${GREEN}✅ Frontend deployed successfully${NC}"
}

# Function to load sacred texts data
load_data() {
    echo -e "${BLUE}📚 Loading sacred texts data...${NC}"

    cd "$PROJECT_ROOT/backend"

    # Activate virtual environment
    source venv/bin/activate

    # Get Cosmos DB connection string
    COSMOS_CONNECTION_STRING=$(az cosmosdb keys list \
        --name "$COSMOS_DB_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --type connection-strings \
        --query 'connectionStrings[0].connectionString' \
        --output tsv)

    # Run data loading script
    if [[ -f "data_processing/build_vector_storage.py" ]]; then
        python data_processing/build_vector_storage.py \
            --source-dir "../data/sources" \
            --output cosmos \
            --connection-string "$COSMOS_CONNECTION_STRING"
    else
        echo -e "${YELLOW}⚠️  Data loading script not found. Skipping data load.${NC}"
    fi

    cd "$PROJECT_ROOT"

    echo -e "${GREEN}✅ Data loading completed${NC}"
}

# Function to verify deployment
verify_deployment() {
    echo -e "${BLUE}🔍 Verifying deployment...${NC}"

    # Get Function App URL
    FUNCTION_APP_URL=$(az functionapp show \
        --name "$FUNCTION_APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --query 'defaultHostName' \
        --output tsv)

    # Test health endpoint
    echo "Testing health endpoint..."
    if curl -f -s "https://$FUNCTION_APP_URL/api/health" > /dev/null; then
        echo -e "${GREEN}✅ Health endpoint responding${NC}"
    else
        echo -e "${RED}❌ Health endpoint not responding${NC}"
        return 1
    fi

    # Test spiritual guidance endpoint
    echo "Testing spiritual guidance endpoint..."
    FUNCTION_KEY=$(az functionapp keys list \
        --name "$FUNCTION_APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --query 'functionKeys.default' \
        --output tsv)

    RESPONSE=$(curl -f -s -X POST "https://$FUNCTION_APP_URL/api/spiritual_guidance" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $FUNCTION_KEY" \
        -d '{"query": "What is dharma?", "language": "English"}')

    if [[ $? -eq 0 ]] && [[ $(echo "$RESPONSE" | jq -r '.response' 2>/dev/null) != "null" ]]; then
        echo -e "${GREEN}✅ Spiritual guidance endpoint working${NC}"
    else
        echo -e "${RED}❌ Spiritual guidance endpoint not working${NC}"
        echo "Response: $RESPONSE"
        return 1
    fi

    echo -e "${GREEN}✅ Deployment verification completed${NC}"
}

# Function to display deployment summary
display_summary() {
    echo ""
    echo -e "${BLUE}📋 Deployment Summary${NC}"
    echo -e "${BLUE}===================${NC}"
    echo -e "Environment: ${YELLOW}$ENVIRONMENT${NC}"
    echo -e "Resource Group: ${YELLOW}$RESOURCE_GROUP${NC}"
    
    FUNCTION_APP_URL=$(az functionapp show \
        --name "$FUNCTION_APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --query 'defaultHostName' \
        --output tsv 2>/dev/null || echo "Not deployed")
    
    STATIC_WEB_APP_URL=$(az staticwebapp show \
        --name "$STATIC_WEB_APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --query 'defaultHostname' \
        --output tsv 2>/dev/null || echo "Not deployed")

    echo -e "Backend API: ${GREEN}https://$FUNCTION_APP_URL/api${NC}"
    echo -e "Frontend URL: ${GREEN}https://$STATIC_WEB_APP_URL${NC}"
    echo ""
    echo -e "${BLUE}🔗 Useful Commands:${NC}"
    echo -e "Monitor logs: ${YELLOW}az functionapp log tail --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP${NC}"
    echo -e "View metrics: ${YELLOW}az monitor app-insights component show --app $APP_INSIGHTS_NAME --resource-group $RESOURCE_GROUP${NC}"
    echo -e "Test API: ${YELLOW}curl https://$FUNCTION_APP_URL/api/health${NC}"
    echo ""
    echo -e "${GREEN}🕉️  Deployment completed with divine blessings!${NC}"
}

# Main deployment flow
main() {
    echo -e "${BLUE}🚀 Starting Vimarsh deployment...${NC}"

    if [[ "$DATA_ONLY" == "true" ]]; then
        load_data
        echo -e "${GREEN}✅ Data-only deployment completed${NC}"
        return 0
    fi

    if [[ "$SKIP_INFRASTRUCTURE" == "false" ]]; then
        create_infrastructure
        configure_app_settings
    fi

    deploy_backend

    if [[ "$SKIP_INFRASTRUCTURE" == "false" ]]; then
        deploy_frontend
    fi

    load_data
    verify_deployment
    display_summary
}

# Run main function
main "$@"
