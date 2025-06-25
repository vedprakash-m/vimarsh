#!/bin/bash

# Vimarsh Development Environment Setup Script
# This script sets up the complete development environment for Vimarsh

set -e  # Exit on any error

echo "🕉️  Setting up Vimarsh Development Environment..."

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1)
echo "Python version: $PYTHON_VERSION"

if ! python3 -c "import sys; assert sys.version_info >= (3, 9)" 2>/dev/null; then
    echo "❌ Error: Python 3.9+ is required"
    exit 1
fi

echo "✅ Python version check passed"

# Create project directories
echo "📁 Creating project structure..."
mkdir -p backend/{spiritual_guidance,rag_pipeline,llm_integration,citation_system,error_handling,voice_interface,expert_review,data_processing,tests}
mkdir -p data/{sources,processed}
mkdir -p frontend/{src,public}
mkdir -p infrastructure
mkdir -p docs/{api,deployment,legal,experts}
mkdir -p scripts

echo "✅ Project directories created"

# Set up Python virtual environment
echo "🐍 Setting up Python virtual environment..."
cd backend

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate
echo "✅ Virtual environment activated"

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo "✅ Python dependencies installed"

# Install Azure Functions Core Tools (if not installed)
if ! command -v func &> /dev/null; then
    echo "🔧 Installing Azure Functions Core Tools..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew tap azure/functions
            brew install azure-functions-core-tools@4
        else
            echo "❌ Homebrew not found. Please install Azure Functions Core Tools manually."
            echo "Visit: https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local"
        fi
    else
        echo "❌ Please install Azure Functions Core Tools manually for your OS."
        echo "Visit: https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local"
    fi
else
    echo "✅ Azure Functions Core Tools already installed"
fi

# Copy environment file
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ Environment file created (.env)"
    echo "📝 Please update .env with your actual API keys and configurations"
else
    echo "✅ Environment file already exists"
fi

# Create local.settings.json for Azure Functions
if [ ! -f "local.settings.json" ]; then
    cat > local.settings.json << EOF
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "FUNCTIONS_EXTENSION_VERSION": "~4",
    "AZURE_FUNCTIONS_ENVIRONMENT": "development"
  },
  "Host": {
    "LocalHttpPort": 7071,
    "CORS": "*",
    "CORSCredentials": false
  }
}
EOF
    echo "✅ Azure Functions local settings created"
else
    echo "✅ Azure Functions local settings already exist"
fi

# Download NLTK data (required for text processing)
echo "📚 Downloading NLTK data..."
python -c "
import nltk
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
    print('✅ NLTK data downloaded')
except Exception as e:
    print(f'⚠️  NLTK download warning: {e}')
"

# Initialize git repository (if not already initialized)
cd ..
if [ ! -d ".git" ]; then
    git init
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already exists"
fi

# Create .gitignore
if [ ! -f ".gitignore" ]; then
    cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# Environment Variables
.env
.env.local
.env.production

# Azure Functions
local.settings.json
.azure/
.vscode/
bin/
obj/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
logs/
*.log

# Runtime data
pids/
*.pid
*.seed
*.pid.lock

# Node.js (for frontend)
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Build outputs
dist/
build/

# Temporary files
tmp/
temp/

# Test coverage
coverage/
.coverage
.pytest_cache/

# ML Models and Data
*.pkl
*.model
data/sources/*.txt
!data/sources/sample_*.txt

# Vector databases
*.faiss
*.index
EOF
    echo "✅ .gitignore created"
else
    echo "✅ .gitignore already exists"
fi

echo ""
echo "🎉 Vimarsh development environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Update backend/.env with your API keys"
echo "2. Activate virtual environment: cd backend && source venv/bin/activate"
echo "3. Start development: func start (from backend directory)"
echo ""
echo "📖 For more information, see README.md"
