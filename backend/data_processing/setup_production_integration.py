#!/usr/bin/env python3
"""
Setup script to configure environment variables and complete production integration.
This script helps set up the required API keys and connection strings for production deployment.
"""

import os
import json
from pathlib import Path

def check_environment_setup():
    """Check and display current environment configuration"""
    
    print("🔧 ENVIRONMENT CONFIGURATION CHECK")
    print("=" * 50)
    
    # Check for required environment variables
    required_vars = {
        'GEMINI_API_KEY': 'Google Gemini API key for embeddings',
        'GOOGLE_API_KEY': 'Alternative Google API key',
        'COSMOS_CONNECTION_STRING': 'Azure Cosmos DB connection string',
        'AZURE_COSMOS_ENDPOINT': 'Azure Cosmos DB endpoint',
        'AZURE_COSMOS_KEY': 'Azure Cosmos DB access key'
    }
    
    found_vars = {}
    missing_vars = {}
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # Mask sensitive information
            if len(value) > 10:
                masked_value = f"{value[:6]}...{value[-4:]}"
            else:
                masked_value = f"{value[:3]}..."
            found_vars[var] = masked_value
        else:
            missing_vars[var] = description
    
    if found_vars:
        print("✅ Found environment variables:")
        for var, value in found_vars.items():
            print(f"   {var}: {value}")
    
    if missing_vars:
        print("\n⚠️ Missing environment variables:")
        for var, description in missing_vars.items():
            print(f"   {var}: {description}")
    
    return len(missing_vars) == 0

def create_environment_template():
    """Create a template .env file for easy configuration"""
    
    env_template = """# Vimarsh Production Environment Configuration
# Copy this file to .env and fill in your actual values

# Google Gemini API Key (required for real embeddings)
# Get from: https://ai.google.dev/
GEMINI_API_KEY=your_gemini_api_key_here

# Azure Cosmos DB Configuration (required for vector database)
# Get from Azure Portal > Cosmos DB > Keys
COSMOS_CONNECTION_STRING=your_cosmos_connection_string_here

# Alternative: Separate endpoint and key
AZURE_COSMOS_ENDPOINT=https://your-cosmos-account.documents.azure.com:443/
AZURE_COSMOS_KEY=your_cosmos_key_here

# Optional: Azure Key Vault for production security
AZURE_KEY_VAULT_URL=https://your-keyvault.vault.azure.net/

# Optional: Application Insights for monitoring
APPLICATIONINSIGHTS_CONNECTION_STRING=your_app_insights_connection_string
"""
    
    env_file = Path(".env.template")
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(env_template)
    
    print(f"📝 Created environment template: {env_file}")
    print("   1. Copy to .env file")
    print("   2. Fill in your actual API keys and connection strings")
    print("   3. Run the integration script again")

def load_dotenv_if_available():
    """Try to load .env file if python-dotenv is available"""
    
    try:
        from dotenv import load_dotenv
        env_file = Path(".env")
        if env_file.exists():
            load_dotenv(env_file)
            print(f"✅ Loaded environment from {env_file}")
            return True
        else:
            print(f"⚠️ No .env file found at {env_file}")
            return False
    except ImportError:
        print("💡 Consider installing python-dotenv: pip install python-dotenv")
        return False

def get_current_data_status():
    """Check the current status of processed data"""
    
    print("\n📊 CURRENT DATA STATUS")
    print("=" * 30)
    
    # Check manual downloads
    manual_path = Path("processed_manual_downloads/manual_downloads_report.json")
    if manual_path.exists():
        with open(manual_path, 'r', encoding='utf-8') as f:
            manual_data = json.load(f)
        manual_chunks = manual_data["statistics"]["total_chunks"]
        manual_personalities = manual_data["statistics"]["personalities_added"]
        print(f"✅ Manual downloads: {manual_chunks} chunks")
        print(f"   Personalities: {', '.join(manual_personalities)}")
    else:
        print("❌ No manual downloads data found")
        manual_chunks = 0
    
    # Check new intake
    intake_path = Path("processed_new_intake/new_intake_books_report.json")
    if intake_path.exists():
        with open(intake_path, 'r', encoding='utf-8') as f:
            intake_data = json.load(f)
        intake_chunks = intake_data["statistics"]["total_chunks"]
        enhanced_personalities = intake_data["statistics"]["personalities_enhanced"]
        print(f"✅ New intake books: {intake_chunks} chunks")
        print(f"   Enhanced personalities: {', '.join(enhanced_personalities)}")
    else:
        print("❌ No new intake data found")
        intake_chunks = 0
    
    total_new_chunks = manual_chunks + intake_chunks
    print(f"\n📈 Total new chunks ready for integration: {total_new_chunks}")
    
    return total_new_chunks

def provide_setup_guidance():
    """Provide step-by-step setup guidance"""
    
    print("\n🎯 SETUP GUIDANCE")
    print("=" * 25)
    
    print("To complete production integration, you need:")
    
    print("\n1. 🔑 GEMINI API KEY:")
    print("   • Visit: https://ai.google.dev/")
    print("   • Create API key")
    print("   • Set: GEMINI_API_KEY=your_key")
    
    print("\n2. 🗄️ COSMOS DB CONNECTION:")
    print("   • Azure Portal > Cosmos DB > Keys")
    print("   • Copy Primary Connection String")
    print("   • Set: COSMOS_CONNECTION_STRING=your_connection_string")
    
    print("\n3. 🔄 INTEGRATION STEPS:")
    print("   • Set environment variables")
    print("   • Run: python integrate_new_content_to_production.py")
    print("   • Verify: Test RAG queries with new personalities")
    
    print("\n4. 🧪 TESTING:")
    print("   • Query Einstein content: 'What is relativity?'")
    print("   • Query Confucius wisdom: 'How should I behave ethically?'")
    print("   • Query Lao Tzu: 'What is the Tao?'")

def main():
    """Main setup check and guidance"""
    
    print("🚀 VIMARSH PRODUCTION SETUP CHECKER")
    print("=" * 45)
    
    # Try to load .env file
    load_dotenv_if_available()
    
    # Check environment
    env_ready = check_environment_setup()
    
    # Check data status
    total_chunks = get_current_data_status()
    
    if not env_ready:
        create_environment_template()
        provide_setup_guidance()
        
        print("\n⚠️ SETUP REQUIRED")
        print("Configure environment variables before running integration.")
        return False
    else:
        print("\n✅ ENVIRONMENT READY")
        print("You can now run the production integration!")
        print("Command: python integrate_new_content_to_production.py")
        return True

if __name__ == "__main__":
    main()
