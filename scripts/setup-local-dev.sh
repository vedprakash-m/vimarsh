#!/bin/bash

# Vimarsh Local Development Setup
# Simple setup for single-environment architecture

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] $1${NC}"
}

warning() {
    echo -e "${YELLOW}[$(date +'%H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

info() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')] $1${NC}"
}

# Project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "🕉️  Vimarsh Local Development Setup"
echo "=================================="
echo "Setting up simplified single-environment development"
echo ""

# Check prerequisites
log "🔍 Checking prerequisites..."

# Check Node.js
if ! command -v node &> /dev/null; then
    error "Node.js not found. Please install Node.js 18+ from https://nodejs.org/"
fi

NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    error "Node.js version $NODE_VERSION found. Please install Node.js 18 or higher."
fi

log "✅ Node.js $(node --version) found"

# Check Python
if ! command -v python3 &> /dev/null; then
    error "Python 3 not found. Please install Python 3.9+ from https://python.org/"
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
log "✅ Python $PYTHON_VERSION found"

# Check Azure Functions Core Tools (optional)
if command -v func &> /dev/null; then
    log "✅ Azure Functions Core Tools $(func --version) found"
else
    warning "Azure Functions Core Tools not found - install for local backend testing"
    info "Install: npm install -g azure-functions-core-tools@4 --unsafe-perm true"
fi

# Setup backend
log "🐍 Setting up backend..."

cd "$PROJECT_ROOT/backend"

# Create Python virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    log "Creating Python virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install Python dependencies
if [ -f "requirements.txt" ]; then
    log "Installing Python dependencies..."
    pip install -r requirements.txt
else
    warning "requirements.txt not found in backend/"
fi

# Verify backend configuration
if [ -f "local.settings.json" ]; then
    log "✅ Backend configuration found"
else
    error "Backend local.settings.json not found"
fi

# Setup frontend
log "⚛️ Setting up frontend..."

cd "$PROJECT_ROOT/frontend"

# Install Node.js dependencies
if [ -f "package.json" ]; then
    log "Installing Node.js dependencies..."
    npm install
else
    error "package.json not found in frontend/"
fi

# Verify frontend configuration
if [ -f ".env.development" ]; then
    log "✅ Frontend development configuration found"
else
    error "Frontend .env.development not found"
fi

# Create .env.local if it doesn't exist
if [ ! -f ".env.local" ]; then
    log "Creating .env.local for personal overrides..."
    cat > .env.local << EOF
# Personal Local Development Overrides
# This file is ignored by git - safe for personal settings

# Uncomment and customize as needed:
# REACT_APP_API_BASE_URL=http://localhost:7071/api
# REACT_APP_DEBUG_MODE=true
# REACT_APP_LOG_LEVEL=debug

# Add your personal development settings here
EOF
    log "✅ Created .env.local template"
fi

# Final verification
cd "$PROJECT_ROOT"

log "🧪 Running quick validation..."

# Check if configuration files are valid
if [ -f ".env.development" ]; then
    log "✅ Root development configuration found"
else
    warning "Root .env.development not found"
fi

if [ -f ".env.example" ]; then
    log "✅ Configuration template found"
else
    warning ".env.example not found"
fi

# Success message
echo ""
log "🎉 Local development setup completed!"
echo ""
echo -e "${BLUE}📋 Next Steps:${NC}"
echo "  1. Backend: cd backend && func host start"
echo "  2. Frontend: cd frontend && npm start"
echo "  3. Open: http://localhost:3000"
echo ""
echo -e "${BLUE}📝 Configuration:${NC}"
echo "  • Backend config: backend/local.settings.json"
echo "  • Frontend config: frontend/.env.development"
echo "  • Personal overrides: frontend/.env.local"
echo ""
echo -e "${BLUE}🔧 Customization:${NC}"
echo "  • Edit frontend/.env.local for personal settings"
echo "  • All secrets use safe development defaults"
echo "  • Production uses Azure Key Vault (no local secrets)"
echo ""
echo -e "${GREEN}🙏 May your development bring wisdom to all seekers!${NC}"