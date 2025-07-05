#!/bin/bash
# Vimarsh Infrastructure Deployment Script
# Purpose: Deploy the two-resource-group pause-resume architecture
# Usage: ./deploy.sh [dev|prod] [validate|deploy]

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_FILE="$SCRIPT_DIR/main.bicep"
PARAMETERS_FILE="$SCRIPT_DIR/main.parameters.json"

# Default values
ENVIRONMENT=${1:-dev}
ACTION=${2:-validate}
LOCATION="East US"
SUBSCRIPTION_ID=""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Validate prerequisites
validate_prerequisites() {
    log_info "Validating prerequisites..."
    
    # Check Azure CLI
    if ! command -v az &> /dev/null; then
        log_error "Azure CLI is not installed"
        exit 1
    fi
    
    # Check login status
    if ! az account show &> /dev/null; then
        log_error "Not logged in to Azure. Run 'az login' first"
        exit 1
    fi
    
    # Get subscription ID
    SUBSCRIPTION_ID=$(az account show --query id -o tsv)
    log_info "Using subscription: $SUBSCRIPTION_ID"
    
    # Check Bicep template exists
    if [[ ! -f "$TEMPLATE_FILE" ]]; then
        log_error "Template file not found: $TEMPLATE_FILE"
        exit 1
    fi
    
    # Check parameters file exists
    if [[ ! -f "$PARAMETERS_FILE" ]]; then
        log_error "Parameters file not found: $PARAMETERS_FILE"
        exit 1
    fi
    
    log_success "Prerequisites validated"
}

# Validate Bicep template
validate_template() {
    log_info "Validating Bicep template..."
    
    # Validate syntax
    if az bicep validate --file "$TEMPLATE_FILE"; then
        log_success "Bicep template syntax is valid"
    else
        log_error "Bicep template validation failed"
        exit 1
    fi
    
    # Validate deployment (what-if)
    log_info "Running deployment validation..."
    if az deployment sub validate \
        --location "$LOCATION" \
        --template-file "$TEMPLATE_FILE" \
        --parameters "$PARAMETERS_FILE"; then
        log_success "Deployment validation passed"
    else
        log_error "Deployment validation failed"
        exit 1
    fi
}

# Deploy infrastructure
deploy_infrastructure() {
    log_info "Deploying infrastructure..."
    
    DEPLOYMENT_NAME="vimarsh-deployment-$(date +%Y%m%d-%H%M%S)"
    
    log_info "Starting deployment: $DEPLOYMENT_NAME"
    
    if az deployment sub create \
        --name "$DEPLOYMENT_NAME" \
        --location "$LOCATION" \
        --template-file "$TEMPLATE_FILE" \
        --parameters "$PARAMETERS_FILE"; then
        log_success "Deployment completed successfully"
        
        # Get outputs
        log_info "Deployment outputs:"
        az deployment sub show \
            --name "$DEPLOYMENT_NAME" \
            --query "properties.outputs" \
            --output table
    else
        log_error "Deployment failed"
        exit 1
    fi
}

# Show what-if analysis
show_whatif() {
    log_info "Running what-if analysis..."
    
    az deployment sub what-if \
        --location "$LOCATION" \
        --template-file "$TEMPLATE_FILE" \
        --parameters "$PARAMETERS_FILE"
}

# Main execution
main() {
    log_info "Vimarsh Infrastructure Deployment"
    log_info "Environment: $ENVIRONMENT"
    log_info "Action: $ACTION"
    log_info "Location: $LOCATION"
    echo ""
    
    validate_prerequisites
    
    case $ACTION in
        validate)
            validate_template
            ;;
        deploy)
            validate_template
            deploy_infrastructure
            ;;
        whatif)
            validate_template
            show_whatif
            ;;
        *)
            log_error "Invalid action: $ACTION"
            log_info "Usage: $0 [dev|prod] [validate|deploy|whatif]"
            exit 1
            ;;
    esac
    
    log_success "Operation completed successfully"
}

# Run main function
main "$@"
