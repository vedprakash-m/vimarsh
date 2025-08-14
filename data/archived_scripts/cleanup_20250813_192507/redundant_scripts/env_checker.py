"""
Environment Configuration Checker for Vimarsh
Helps diagnose container naming and configuration issues.
"""

import os
import sys
from pathlib import Path

def check_environment_config():
    """Check current environment configuration"""
    print("=" * 60)
    print("🔍 VIMARSH ENVIRONMENT CONFIGURATION CHECK")
    print("=" * 60)
    
    # Check environment variables
    env_vars = [
        'AZURE_COSMOS_CONNECTION_STRING',
        'AZURE_COSMOS_DATABASE_NAME', 
        'AZURE_COSMOS_CONTAINER_NAME'
    ]
    
    print("📋 Environment Variables:")
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive data
            if 'CONNECTION_STRING' in var:
                masked_value = value[:30] + "..." + value[-10:] if len(value) > 40 else value
                print(f"   ✅ {var}: {masked_value}")
            else:
                print(f"   ✅ {var}: {value}")
        else:
            print(f"   ❌ {var}: NOT SET")
    
    print()
    
    # Check .env files
    env_files = [
        Path('.env'),
        Path('backend/.env'),
        Path('.env.development'),
        Path('backend/.env.development'),
        Path('.env.local'),
        Path('backend/.env.local')
    ]
    
    print("📁 Environment Files:")
    found_files = []
    for env_file in env_files:
        if env_file.exists():
            found_files.append(env_file)
            print(f"   ✅ Found: {env_file}")
            
            # Read and check content
            try:
                with open(env_file, 'r') as f:
                    content = f.read()
                    if 'AZURE_COSMOS_CONTAINER_NAME' in content:
                        lines = content.split('\n')
                        for line in lines:
                            if 'AZURE_COSMOS_CONTAINER_NAME' in line and not line.strip().startswith('#'):
                                print(f"      🔧 {line.strip()}")
            except Exception as e:
                print(f"      ❌ Error reading file: {e}")
    
    if not found_files:
        print("   ⚠️ No .env files found")
    
    print()
    
    # Check expected values
    print("🎯 Expected Configuration:")
    print("   AZURE_COSMOS_DATABASE_NAME: vimarsh-multi-personality")
    print("   AZURE_COSMOS_CONTAINER_NAME: personality-vectors")
    
    print()
    
    # Current working directory
    print(f"📍 Current Working Directory: {os.getcwd()}")
    print(f"📍 Python Path: {sys.executable}")
    
    # Recommendations
    print()
    print("💡 RECOMMENDATIONS:")
    
    db_name = os.getenv('AZURE_COSMOS_DATABASE_NAME')
    container_name = os.getenv('AZURE_COSMOS_CONTAINER_NAME')
    
    if container_name == 'spiritual_texts' or container_name == 'spiritual-vectors':
        print("   ⚠️ Your container name is set to an old value.")
        print("   📝 Create a .env file with: AZURE_COSMOS_CONTAINER_NAME=personality-vectors")
    
    if db_name != 'vimarsh-multi-personality':
        print("   ⚠️ Your database name might be incorrect.")
        print("   📝 Set: AZURE_COSMOS_DATABASE_NAME=vimarsh-multi-personality")
    
    if not os.getenv('AZURE_COSMOS_CONNECTION_STRING'):
        print("   ❌ Missing Azure Cosmos DB connection string.")
        print("   📝 Set AZURE_COSMOS_CONNECTION_STRING in your environment")
    
    print("=" * 60)

def create_correct_env_file():
    """Create a .env file with correct settings"""
    env_content = """# Vimarsh Multi-Personality Configuration
# Update these values with your actual Azure credentials

# Azure Cosmos DB Configuration
AZURE_COSMOS_CONNECTION_STRING=AccountEndpoint=https://your-cosmos-account.documents.azure.com:443/;AccountKey=your-key;
AZURE_COSMOS_DATABASE_NAME=vimarsh-multi-personality
AZURE_COSMOS_CONTAINER_NAME=personality-vectors

# Google AI Services
GOOGLE_AI_API_KEY=your-gemini-api-key

# Azure Functions Configuration  
AZURE_FUNCTIONS_ENVIRONMENT=development

# Other configurations...
"""
    
    env_file = Path('backend/.env')
    if not env_file.exists():
        with open(env_file, 'w') as f:
            f.write(env_content)
        print(f"✅ Created template .env file at: {env_file}")
        print("📝 Please update the values with your actual credentials")
    else:
        print(f"⚠️ .env file already exists at: {env_file}")
        print("📝 Please check and update the container name manually")

if __name__ == "__main__":
    check_environment_config()
    print()
    
    response = input("Would you like to create a template .env file? (y/n): ")
    if response.lower() == 'y':
        create_correct_env_file()
