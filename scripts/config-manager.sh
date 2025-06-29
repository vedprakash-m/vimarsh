#!/bin/bash

# Vimarsh Environment Configuration Manager
# This script manages environment-specific configurations for different deployment environments

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CONFIG_DIR="$PROJECT_ROOT/config/environments"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

# Default values
ENVIRONMENT="${ENVIRONMENT:-development}"
OPERATION="${1:-help}"

# Logging functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Help function
show_help() {
    cat << EOF
🙏 Vimarsh Environment Configuration Manager

USAGE:
    $0 <operation> [environment]

OPERATIONS:
    setup           Set up environment configuration
    validate        Validate environment configuration
    deploy          Deploy environment-specific settings
    switch          Switch to different environment
    status          Show current environment status
    help            Show this help message

ENVIRONMENTS:
    development     Local development environment (for local testing only)
    production      Production environment (single Azure deployment)

EXAMPLES:
    $0 setup development           # Set up local development environment
    $0 validate production         # Validate production configuration
    $0 deploy production          # Deploy production configuration
    $0 switch production          # Switch to production environment
    $0 status                     # Show current environment status

ENVIRONMENT VARIABLES:
    ENVIRONMENT                   # Override default environment
    AZURE_SUBSCRIPTION_ID         # Azure subscription ID
    AZURE_RESOURCE_GROUP          # Azure resource group name

🕉️ May this tool serve the divine purpose of spreading wisdom
EOF
}

# Validate environment
validate_environment() {
    local env="$1"
    
    log "🔍 Validating environment: $env"
    
    # Check if environment file exists
    local env_file="$CONFIG_DIR/.env.$env"
    if [ ! -f "$env_file" ]; then
        error "Environment file not found: $env_file"
    fi
    
    # Source environment file for validation
    set -a
    source "$env_file"
    set +a
    
    # Validate required variables
    local required_vars=(
        "ENVIRONMENT"
        "LOG_LEVEL"
        "AZURE_RESOURCE_GROUP"
        "AZURE_LOCATION"
        "MAX_QUERY_LENGTH"
        "MONTHLY_BUDGET_USD"
    )
    
    local missing_vars=()
    for var in "${required_vars[@]}"; do
        if [ -z "${!var:-}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -gt 0 ]; then
        error "Missing required variables: ${missing_vars[*]}"
    fi
    
    # Validate Azure configuration
    if [ "$env" != "development" ]; then
        if [[ ! "$GEMINI_API_KEY" =~ ^@Microsoft\.KeyVault ]]; then
            warning "Production environment should use Key Vault references for secrets"
        fi
    fi
    
    # Validate budget settings
    if [ "$MONTHLY_BUDGET_USD" -gt 200 ]; then
        warning "Monthly budget exceeds recommended beta testing limit"
    fi
    
    log "✅ Environment validation completed successfully"
}

# Set up environment configuration
setup_environment() {
    local env="${1:-$ENVIRONMENT}"
    
    log "🚀 Setting up environment: $env"
    
    # Validate environment first
    validate_environment "$env"
    
    # Create backend configuration
    setup_backend_config "$env"
    
    # Create frontend configuration
    setup_frontend_config "$env"
    
    # Create infrastructure parameters
    setup_infrastructure_config "$env"
    
    log "✅ Environment setup completed for: $env"
}

# Set up backend configuration
setup_backend_config() {
    local env="$1"
    local env_file="$CONFIG_DIR/.env.$env"
    local backend_env="$BACKEND_DIR/.env"
    
    log "🐍 Setting up backend configuration for: $env"
    
    # Copy environment-specific configuration
    cp "$env_file" "$backend_env"
    
    # Add backend-specific configurations
    cat >> "$backend_env" << EOF

# Backend-specific configuration
FUNCTIONS_WORKER_RUNTIME=python
FUNCTIONS_EXTENSION_VERSION=~4
WEBSITE_CONTENTAZUREFILECONNECTIONSTRING=@Microsoft.KeyVault(SecretUri=https://vimarsh-${env}-kv.vault.azure.net/secrets/storage-connection-string)
WEBSITE_CONTENTSHARE=vimarsh-${env}-functions

# Python configuration
PYTHONPATH=/home/site/wwwroot
PYTHON_ISOLATE_WORKER_DEPENDENCIES=1
EOF
    
    log "✅ Backend configuration created: $backend_env"
}

# Set up frontend configuration
setup_frontend_config() {
    local env="$1"
    local env_file="$CONFIG_DIR/.env.$env"
    local frontend_env="$FRONTEND_DIR/.env"
    
    log "⚛️ Setting up frontend configuration for: $env"
    
    # Source environment variables
    set -a
    source "$env_file"
    set +a
    
    # Create React environment file
    cat > "$frontend_env" << EOF
# React Environment Configuration for: $env
REACT_APP_ENVIRONMENT=$env
REACT_APP_API_BASE_URL=https://vimarsh-${env}-functions.azurewebsites.net
REACT_APP_AUTH_CLIENT_ID=$AZURE_AD_CLIENT_ID
REACT_APP_AUTH_TENANT_ID=$AZURE_AD_TENANT_ID
REACT_APP_AUTH_REDIRECT_URI=https://vimarsh-${env}-web.azurestaticapps.net/auth/callback
REACT_APP_ENABLE_ANALYTICS=$ENABLE_ANALYTICS
REACT_APP_ENABLE_VOICE_INTERFACE=$ENABLE_VOICE_INTERFACE
REACT_APP_DEFAULT_LANGUAGE=$DEFAULT_LANGUAGE
REACT_APP_VERSION=\$(cat package.json | grep '"version"' | cut -d'"' -f4)

# Build configuration
CI=false
GENERATE_SOURCEMAP=false
INLINE_RUNTIME_CHUNK=false
EOF
    
    if [ "$env" = "development" ]; then
        cat >> "$frontend_env" << EOF

# Development-specific
REACT_APP_API_BASE_URL=http://localhost:7071
REACT_APP_AUTH_REDIRECT_URI=http://localhost:3000/auth/callback
REACT_APP_DEBUG_MODE=true
CHOKIDAR_USEPOLLING=true
EOF
    fi
    
    log "✅ Frontend configuration created: $frontend_env"
}

# Set up infrastructure configuration
setup_infrastructure_config() {
    local env="$1"
    local env_file="$CONFIG_DIR/.env.$env"
    local infra_params="$PROJECT_ROOT/infrastructure/parameters/$env.parameters.json"
    
    log "🏗️ Setting up infrastructure configuration for: $env"
    
    # Source environment variables
    set -a
    source "$env_file"
    set +a
    
    # Create infrastructure parameters
    mkdir -p "$(dirname "$infra_params")"
    
    cat > "$infra_params" << EOF
{
  "\$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "environment": {
      "value": "$env"
    },
    "location": {
      "value": "$AZURE_LOCATION"
    },
    "appName": {
      "value": "vimarsh"
    },
    "projectName": {
      "value": "vimarsh"
    },
    "geminiApiKey": {
EOF
    
    if [ "$env" = "development" ]; then
        cat >> "$infra_params" << EOF
      "value": "$GEMINI_API_KEY"
EOF
    else
        cat >> "$infra_params" << EOF
      "reference": {
        "keyVault": {
          "id": "/subscriptions/$AZURE_SUBSCRIPTION_ID/resourceGroups/vimarsh-db-rg/providers/Microsoft.KeyVault/vaults/vimarsh-kv"
        },
        "secretName": "gemini-api-key"
      }
EOF
    fi
    
    cat >> "$infra_params" << EOF
    },
    "expertReviewEmail": {
      "value": "$EXPERT_REVIEW_EMAIL"
    },
    "monthlyBudgetUsd": {
      "value": $MONTHLY_BUDGET_USD
    },
    "costAlertThreshold": {
      "value": $COST_ALERT_THRESHOLD
    }
  }
}
EOF
    
    log "✅ Infrastructure parameters created: $infra_params"
}

# Deploy environment configuration
deploy_environment() {
    local env="${1:-$ENVIRONMENT}"
    
    log "🚀 Deploying configuration for environment: $env"
    
    # Validate environment
    validate_environment "$env"
    
    # Set up configuration files
    setup_environment "$env"
    
    # Deploy to Azure (if not development)
    if [ "$env" != "development" ]; then
        deploy_to_azure "$env"
    fi
    
    log "✅ Environment deployment completed for: $env"
}

# Deploy to Azure
deploy_to_azure() {
    local env="$1"
    
    log "☁️ Deploying to Azure environment: $env"
    
    # Check Azure CLI
    if ! command -v az &> /dev/null; then
        error "Azure CLI not found. Please install Azure CLI."
    fi
    
    # Check if logged in
    if ! az account show &> /dev/null; then
        error "Not logged into Azure. Please run 'az login'."
    fi
    
    # Deploy infrastructure
    local infra_params="$PROJECT_ROOT/infrastructure/parameters/$env.parameters.json"
    local resource_group="vimarsh-${env}-rg"
    
    if [ "$env" = "production" ]; then
        resource_group="vimarsh-rg"
    fi
    
    log "Deploying infrastructure to resource group: $resource_group"
    
    # Create resource group if it doesn't exist
    az group create \
        --name "$resource_group" \
        --location "$(jq -r '.parameters.location.value' "$infra_params")" \
        --output none
    
    # Deploy Bicep template
    az deployment group create \
        --resource-group "$resource_group" \
        --template-file "$PROJECT_ROOT/infrastructure/main.bicep" \
        --parameters "@$infra_params" \
        --output none
    
    log "✅ Azure deployment completed"
}

# Switch environment
switch_environment() {
    local env="${1:-}"
    
    if [ -z "$env" ]; then
        error "Environment not specified. Use: development (local) or production"
    fi
    
    log "🔄 Switching to environment: $env"
    
    # Set up new environment
    setup_environment "$env"
    
    # Update current environment marker
    echo "$env" > "$PROJECT_ROOT/.current_environment"
    
    log "✅ Switched to environment: $env"
}

# Show environment status
show_status() {
    log "📊 Environment Status"
    
    # Current environment
    local current_env="development"
    if [ -f "$PROJECT_ROOT/.current_environment" ]; then
        current_env="$(cat "$PROJECT_ROOT/.current_environment")"
    fi
    
    echo -e "${BLUE}Current Environment:${NC} $current_env"
    
    # Available environments
    echo -e "${BLUE}Available Environments:${NC}"
    for env_file in "$CONFIG_DIR"/.env.*; do
        if [ -f "$env_file" ]; then
            local env_name="$(basename "$env_file" | sed 's/\.env\.//')"
            if [ "$env_name" = "$current_env" ]; then
                echo -e "  ${GREEN}* $env_name${NC} (current)"
            else
                echo -e "    $env_name"
            fi
        fi
    done
    
    # Configuration files status
    echo -e "${BLUE}Configuration Files:${NC}"
    echo -e "  Backend:       $([ -f "$BACKEND_DIR/.env" ] && echo "✅" || echo "❌")"
    echo -e "  Frontend:      $([ -f "$FRONTEND_DIR/.env" ] && echo "✅" || echo "❌")"
    echo -e "  Infrastructure: $([ -f "$PROJECT_ROOT/infrastructure/parameters/$current_env.parameters.json" ] && echo "✅" || echo "❌")"
}

# Main execution
main() {
    case "$OPERATION" in
        "setup")
            setup_environment "${2:-$ENVIRONMENT}"
            ;;
        "validate")
            validate_environment "${2:-$ENVIRONMENT}"
            ;;
        "deploy")
            deploy_environment "${2:-$ENVIRONMENT}"
            ;;
        "switch")
            switch_environment "${2:-}"
            ;;
        "status")
            show_status
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Execute main function
main "$@"
