#!/bin/bash
# Manual deployment script for Vimarsh
# Use this if CI/CD is not working properly

set -e

echo "🚀 Vimarsh Manual Deployment Script"
echo "==================================="

# Get current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Check if we're in the right directory
if [[ ! -f "$PROJECT_ROOT/package.json" ]] || [[ ! -f "$PROJECT_ROOT/backend/function_app.py" ]]; then
    echo "❌ Error: This script must be run from the Vimarsh project root or scripts directory"
    exit 1
fi

echo "📍 Project root: $PROJECT_ROOT"

# Function to deploy frontend
deploy_frontend() {
    echo ""
    echo "🎨 Deploying Frontend..."
    echo "------------------------"
    
    cd "$PROJECT_ROOT/frontend"
    
    echo "📦 Installing dependencies..."
    npm ci --prefer-offline --no-audit --no-fund
    
    echo "🏗️ Building production bundle..."
    npm run build
    
    echo "🚀 Deploying to Azure Static Web Apps..."
    # Check if SWA CLI is available
    if command -v swa &> /dev/null; then
        swa deploy build/ --api-location ../backend/ --verbose
    else
        echo "⚠️ Azure SWA CLI not found. Please install it:"
        echo "   npm install -g @azure/static-web-apps-cli"
        echo "   Then run: swa deploy build/ --api-location ../backend/"
    fi
    
    echo "✅ Frontend deployment completed"
}

# Function to deploy backend
deploy_backend() {
    echo ""
    echo "🐍 Deploying Backend..."
    echo "----------------------"
    
    cd "$PROJECT_ROOT/backend"
    
    echo "🔍 Checking Azure Functions Core Tools..."
    if ! command -v func &> /dev/null; then
        echo "❌ Azure Functions Core Tools not found"
        echo "   Please install it and run: func azure functionapp publish vimarsh-backend-app-flex --python"
        return 1
    fi
    
    echo "🚀 Deploying to Azure Functions..."
    func azure functionapp publish vimarsh-backend-app-flex --python
    
    echo "✅ Backend deployment completed"
}

# Main deployment logic
echo ""
echo "What would you like to deploy?"
echo "1) Frontend only"
echo "2) Backend only"  
echo "3) Both frontend and backend"
echo "4) Exit"
echo ""
read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        deploy_frontend
        ;;
    2)
        deploy_backend
        ;;
    3)
        deploy_backend
        deploy_frontend
        ;;
    4)
        echo "👋 Deployment cancelled"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "🎉 Deployment process completed!"
echo ""
echo "🔍 To verify deployment:"
echo "   Frontend: https://vimarsh.vedprakash.net"
echo "   Backend:  https://vimarsh-backend-app-flex.azurewebsites.net/api/health"
echo ""
echo "📊 Check GitHub Actions for CI/CD status:"
echo "   https://github.com/vedprakash-m/vimarsh/actions"
