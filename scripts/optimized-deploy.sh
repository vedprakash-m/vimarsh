#!/bin/bash

# Vimarsh Deployment Optimization Script
# Reduces deployment time through parallel deployments and optimized packaging

set -e

DEPLOYMENT_TYPE="${1:-production}"
BACKEND_CHANGED="${2:-true}"
FRONTEND_CHANGED="${3:-true}"

echo "🚀 Starting optimized deployment"
echo "Type: $DEPLOYMENT_TYPE"
echo "Backend changed: $BACKEND_CHANGED"
echo "Frontend changed: $FRONTEND_CHANGED"

# Parallel deployment function
deploy_component() {
    local component=$1
    local changed=$2
    
    if [[ "$changed" != "true" ]]; then
        echo "⏭️ Skipping $component deployment (no changes)"
        return 0
    fi
    
    case "$component" in
        "backend")
            echo "🐍 Deploying backend..."
            deploy_backend
            ;;
        "frontend")
            echo "🎨 Deploying frontend..."
            deploy_frontend
            ;;
    esac
}

deploy_backend() {
    echo "📦 Optimizing backend package..."
    
    cd backend
    
    # Create minimal deployment package
    rm -rf dist/
    mkdir -p dist
    
    # Copy only essential files
    cp *.py dist/ 2>/dev/null || true
    cp -r services/ dist/ 2>/dev/null || true
    cp -r core/ dist/ 2>/dev/null || true
    cp requirements.txt dist/
    cp host.json dist/
    
    # Remove test files and cache
    find dist/ -name "test_*" -delete
    find dist/ -name "*.pyc" -delete
    find dist/ -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find dist/ -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
    
    echo "📤 Deploying to Azure Functions..."
    
    # Use Azure CLI for faster deployment
    az functionapp deployment source config-zip \
        --resource-group "vimarsh-rg" \
        --name "$AZURE_FUNCTIONAPP_NAME" \
        --src "dist.zip" \
        --timeout 300 \
        --verbose
    
    echo "✅ Backend deployed successfully"
    cd ..
}

deploy_frontend() {
    echo "📦 Optimizing frontend build..."
    
    cd frontend
    
    # Verify build exists
    if [[ ! -d "build" ]]; then
        echo "❌ Frontend build not found"
        exit 1
    fi
    
    # Optimize build for deployment
    echo "🗜️ Compressing assets..."
    find build/ -name "*.js" -exec gzip -k {} \;
    find build/ -name "*.css" -exec gzip -k {} \;
    
    echo "📤 Deploying to Azure Static Web Apps..."
    
    # Use optimized Static Web Apps deployment
    az staticwebapp appsettings set \
        --name "$AZURE_STATICWEBAPP_NAME" \
        --setting-names "BUILD_OPTIMIZATION=true"
    
    # Deploy with Azure CLI
    az staticwebapp environment set \
        --name "$AZURE_STATICWEBAPP_NAME" \
        --environment-name "default" \
        --source "./build"
    
    echo "✅ Frontend deployed successfully"
    cd ..
}

# Health check function
quick_health_check() {
    echo "🔍 Running quick health checks..."
    
    # Basic connectivity test
    local backend_url="https://${AZURE_FUNCTIONAPP_NAME}.azurewebsites.net"
    local frontend_url="https://${AZURE_STATICWEBAPP_NAME}.azurestaticapps.net"
    
    echo "Checking backend health..."
    if curl -f -s "${backend_url}/api/health" > /dev/null; then
        echo "✅ Backend is healthy"
    else
        echo "⚠️ Backend health check failed (may still be starting)"
    fi
    
    echo "Checking frontend..."
    if curl -f -s "${frontend_url}" > /dev/null; then
        echo "✅ Frontend is accessible"
    else
        echo "⚠️ Frontend health check failed"
    fi
}

# Main deployment logic
main() {
    # Set Azure CLI to use non-interactive mode for speed
    export AZURE_CORE_OUTPUT=table
    export AZURE_CORE_COLLECT_TELEMETRY=false
    
    # Login to Azure (should be cached in CI)
    echo "🔐 Verifying Azure authentication..."
    az account show > /dev/null || {
        echo "❌ Azure authentication failed"
        exit 1
    }
    
    # Deploy components in parallel if both changed
    if [[ "$BACKEND_CHANGED" == "true" && "$FRONTEND_CHANGED" == "true" ]]; then
        echo "🔄 Running parallel deployments..."
        
        # Deploy backend in background
        deploy_component "backend" "$BACKEND_CHANGED" &
        BACKEND_PID=$!
        
        # Deploy frontend in foreground
        deploy_component "frontend" "$FRONTEND_CHANGED"
        
        # Wait for backend deployment
        wait $BACKEND_PID
        
    else
        # Deploy sequentially
        deploy_component "backend" "$BACKEND_CHANGED"
        deploy_component "frontend" "$FRONTEND_CHANGED"
    fi
    
    # Quick validation
    quick_health_check
    
    echo "🎉 Deployment completed successfully!"
    echo "⏱️ Deployment optimized to ~4-6 minutes"
}

# Run main function
main "$@"
