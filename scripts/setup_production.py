#!/usr/bin/env python3
"""
Production Setup Script for Vimarsh
Guides users through complete production setup with all required services
"""

import os
import sys
import json
import asyncio
import logging
from typing import Dict, Any, Optional
import requests
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProductionSetup:
    """Complete production setup and configuration."""
    
    def __init__(self):
        self.config = {}
        self.workspace_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
    def print_banner(self):
        """Print setup banner."""
        print("""
🕉️  VIMARSH PRODUCTION SETUP
=================================
AI-powered Spiritual Guidance System
Production Configuration Assistant

This script will guide you through setting up:
1. Google Gemini Pro API
2. Azure Cosmos DB (Vector Database)
3. Azure Entra ID Authentication
4. Production Environment Configuration
5. Frontend/Backend Integration
""")

    def get_user_input(self, prompt: str, default: str = "", secret: bool = False) -> str:
        """Get user input with optional default."""
        if default:
            display_prompt = f"{prompt} [{default}]: "
        else:
            display_prompt = f"{prompt}: "
            
        if secret:
            import getpass
            return getpass.getpass(display_prompt) or default
        else:
            return input(display_prompt) or default

    def setup_gemini_api(self) -> Dict[str, str]:
        """Setup Google Gemini Pro API configuration."""
        print("\n🤖 STEP 1: Google Gemini Pro API Setup")
        print("=" * 50)
        print("1. Go to https://aistudio.google.com/app/apikey")
        print("2. Create a new API key")
        print("3. Copy the API key")
        
        api_key = self.get_user_input("Enter your Gemini API key", secret=True)
        project_id = self.get_user_input("Enter your Google Cloud project ID (optional)")
        
        # Test the API key
        if api_key and api_key != "YOUR_ACTUAL_GEMINI_API_KEY_HERE":
            print("Testing Gemini API connection...")
            try:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-pro')
                test_response = model.generate_content("Test connection")
                print("✅ Gemini API connection successful!")
            except Exception as e:
                print(f"❌ Gemini API test failed: {e}")
                print("Please check your API key and try again.")
        
        return {
            "GOOGLE_AI_API_KEY": api_key,
            "GOOGLE_CLOUD_PROJECT": project_id
        }

    def setup_cosmos_db(self) -> Dict[str, str]:
        """Setup Azure Cosmos DB configuration."""
        print("\n💾 STEP 2: Azure Cosmos DB Setup")
        print("=" * 50)
        print("Choose your vector database option:")
        print("1. Azure Cosmos DB (Production recommended)")
        print("2. Local FAISS (Development only)")
        
        choice = self.get_user_input("Enter your choice (1/2)", "1")
        
        if choice == "1":
            print("\nFor Azure Cosmos DB setup:")
            print("1. Go to https://portal.azure.com")
            print("2. Create a new Cosmos DB account (Core SQL API)")
            print("3. Create database 'vimarsh' and container 'spiritual_texts'")
            print("4. Copy the connection string from Keys section")
            
            connection_string = self.get_user_input("Enter Cosmos DB connection string", secret=True)
            database_name = self.get_user_input("Enter database name", "vimarsh")
            container_name = self.get_user_input("Enter container name", "spiritual_texts")
            
            return {
                "AZURE_COSMOS_CONNECTION_STRING": connection_string,
                "AZURE_COSMOS_DATABASE_NAME": database_name,
                "AZURE_COSMOS_CONTAINER_NAME": container_name
            }
        else:
            print("Using local FAISS for development...")
            return {
                "AZURE_COSMOS_CONNECTION_STRING": "",
                "AZURE_COSMOS_DATABASE_NAME": "vimarsh",
                "AZURE_COSMOS_CONTAINER_NAME": "spiritual_texts"
            }

    def setup_entra_id(self) -> Dict[str, str]:
        """Setup Azure Entra ID authentication."""
        print("\n🔐 STEP 3: Azure Entra ID Authentication Setup")
        print("=" * 50)
        print("Choose authentication mode:")
        print("1. Full Azure Entra ID (Production)")
        print("2. Development mode (No authentication)")
        
        choice = self.get_user_input("Enter your choice (1/2)", "2")
        
        if choice == "1":
            print("\nFor Azure Entra ID setup:")
            print("1. Go to https://portal.azure.com")
            print("2. Navigate to Azure Active Directory > App registrations")
            print("3. Create a new application registration")
            print("4. Configure redirect URIs for your domain")
            print("5. Generate a client secret")
            
            client_id = self.get_user_input("Enter Client ID")
            client_secret = self.get_user_input("Enter Client Secret", secret=True)
            tenant_id = self.get_user_input("Enter Tenant ID")
            redirect_uri = self.get_user_input("Enter Redirect URI", "http://localhost:3000/auth/callback")
            
            return {
                "AZURE_CLIENT_ID": client_id,
                "AZURE_CLIENT_SECRET": client_secret,
                "AZURE_TENANT_ID": tenant_id,
                "AZURE_AUTHORITY": f"https://login.microsoftonline.com/{tenant_id}",
                "AZURE_REDIRECT_URI": redirect_uri
            }
        else:
            print("Using development mode (authentication disabled)...")
            return {
                "AZURE_CLIENT_ID": "dev-mode",
                "AZURE_CLIENT_SECRET": "dev-mode",
                "AZURE_TENANT_ID": "dev-mode",
                "AZURE_AUTHORITY": "dev-mode",
                "AZURE_REDIRECT_URI": "http://localhost:3000"
            }

    def setup_additional_config(self) -> Dict[str, str]:
        """Setup additional configuration options."""
        print("\n⚙️  STEP 4: Additional Configuration")
        print("=" * 50)
        
        # LLM Configuration
        llm_temp = self.get_user_input("LLM Temperature (0.0-1.0)", "0.7")
        max_tokens = self.get_user_input("Max tokens per response", "4096")
        
        # RAG Configuration
        similarity_threshold = self.get_user_input("Vector similarity threshold", "0.7")
        max_chunks = self.get_user_input("Max retrieved text chunks", "10")
        
        # Environment
        environment = self.get_user_input("Environment (development/production)", "development")
        debug_mode = "true" if environment == "development" else "false"
        
        return {
            "LLM_MODEL": "gemini-pro",
            "LLM_TEMPERATURE": llm_temp,
            "MAX_TOKENS": max_tokens,
            "SAFETY_SETTINGS": "BLOCK_MEDIUM_AND_ABOVE",
            "EMBEDDING_MODEL": "sentence-transformers/all-MiniLM-L6-v2",
            "VECTOR_DIMENSION": "384",
            "SIMILARITY_THRESHOLD": similarity_threshold,
            "MAX_RETRIEVED_CHUNKS": max_chunks,
            "DEFAULT_LANGUAGE": "English",
            "SUPPORTED_LANGUAGES": "English,Hindi",
            "CORS_ORIGINS": "http://localhost:3000,http://localhost:8000",
            "EXPERT_REVIEW_ENABLED": "true",
            "EXPERT_NOTIFICATION_EMAIL": "experts@vimarsh.ai",
            "DEBUG": debug_mode,
            "LOG_LEVEL": "INFO"
        }

    def create_backend_config(self, config: Dict[str, str]):
        """Create backend configuration files."""
        print("\n📝 Creating backend configuration...")
        
        # Create local.settings.json
        backend_config = {
            "IsEncrypted": False,
            "Values": {
                "AzureWebJobsStorage": "UseDevelopmentStorage=true",
                "FUNCTIONS_WORKER_RUNTIME": "python",
                "FUNCTIONS_EXTENSION_VERSION": "~4",
                **config
            },
            "Host": {
                "LocalHttpPort": 7071,
                "CORS": "*",
                "CORSCredentials": False
            }
        }
        
        backend_path = os.path.join(self.workspace_path, "backend", "local.settings.json")
        with open(backend_path, 'w') as f:
            json.dump(backend_config, f, indent=2)
        
        print(f"✅ Backend config saved to: {backend_path}")

    def create_frontend_config(self, config: Dict[str, str]):
        """Create frontend configuration files."""
        print("\n📝 Creating frontend configuration...")
        
        frontend_path = os.path.join(self.workspace_path, "frontend")
        
        # Development environment
        dev_env = f"""# Vimarsh Frontend Development Configuration
REACT_APP_API_BASE_URL=http://localhost:7071
REACT_APP_AZURE_CLIENT_ID={config.get('AZURE_CLIENT_ID', 'dev-mode')}
REACT_APP_AZURE_TENANT_ID={config.get('AZURE_TENANT_ID', 'dev-mode')}
REACT_APP_AZURE_REDIRECT_URI={config.get('AZURE_REDIRECT_URI', 'http://localhost:3000')}
REACT_APP_ENVIRONMENT=development
REACT_APP_DEBUG=true
REACT_APP_ENABLE_AUTH={config.get('AZURE_CLIENT_ID') != 'dev-mode'}
"""
        
        # Production environment
        prod_env = f"""# Vimarsh Frontend Production Configuration
REACT_APP_API_BASE_URL=https://your-function-app.azurewebsites.net
REACT_APP_AZURE_CLIENT_ID={config.get('AZURE_CLIENT_ID', '')}
REACT_APP_AZURE_TENANT_ID={config.get('AZURE_TENANT_ID', '')}
REACT_APP_AZURE_REDIRECT_URI=https://your-domain.com/auth/callback
REACT_APP_ENVIRONMENT=production
REACT_APP_DEBUG=false
REACT_APP_ENABLE_AUTH=true
"""
        
        # Save environment files
        with open(os.path.join(frontend_path, ".env.development"), 'w') as f:
            f.write(dev_env)
        
        with open(os.path.join(frontend_path, ".env.production"), 'w') as f:
            f.write(prod_env)
        
        print(f"✅ Frontend config saved to: {frontend_path}/.env.*")

    def populate_sacred_texts(self):
        """Populate sacred texts and vector database."""
        print("\n📚 STEP 5: Populating Sacred Texts Database")
        print("=" * 50)
        
        choice = self.get_user_input("Populate sacred texts database? (y/n)", "y")
        
        if choice.lower() == 'y':
            try:
                # Run sacred text loader
                loader_path = os.path.join(self.workspace_path, "backend", "data_processing", "sacred_text_loader.py")
                print("Loading sacred texts...")
                subprocess.run([sys.executable, loader_path], cwd=self.workspace_path, check=True)
                
                # Run vector database population
                vector_path = os.path.join(self.workspace_path, "backend", "data_processing", "populate_vector_db.py")
                print("Populating vector database...")
                subprocess.run([sys.executable, vector_path], cwd=self.workspace_path, check=True)
                
                print("✅ Sacred texts database populated successfully!")
                
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to populate database: {e}")
                print("You can run this manually later using:")
                print(f"  python {loader_path}")
                print(f"  python {vector_path}")

    def run_production_tests(self):
        """Run production readiness tests."""
        print("\n🧪 STEP 6: Running Production Tests")
        print("=" * 50)
        
        choice = self.get_user_input("Run production readiness tests? (y/n)", "y")
        
        if choice.lower() == 'y':
            try:
                test_path = os.path.join(self.workspace_path, "scripts", "test_production_readiness.py")
                print("Running production readiness tests...")
                subprocess.run([sys.executable, test_path], cwd=self.workspace_path, check=True)
                print("✅ Production tests completed!")
                
            except subprocess.CalledProcessError as e:
                print(f"❌ Some tests failed: {e}")
                print("Please review the test output and fix any issues.")

    def print_next_steps(self):
        """Print next steps for user."""
        print("\n🚀 SETUP COMPLETE!")
        print("=" * 50)
        print("Next steps to launch Vimarsh:")
        print()
        print("1. BACKEND:")
        print("   cd backend")
        print("   func host start")
        print()
        print("2. FRONTEND:")
        print("   cd frontend")
        print("   npm install")
        print("   npm start")
        print()
        print("3. ACCESS APPLICATION:")
        print("   Open http://localhost:3000 in your browser")
        print()
        print("4. PRODUCTION DEPLOYMENT:")
        print("   Use scripts/deploy-production.sh for Azure deployment")
        print()
        print("📋 Configuration files created:")
        print("   - backend/local.settings.json")
        print("   - frontend/.env.development")
        print("   - frontend/.env.production")
        print()
        print("🔧 For issues or customization:")
        print("   - Check logs in backend/logs/")
        print("   - Review docs/ directory")
        print("   - Run scripts/test_production_readiness.py")
        print()
        print("🕉️  May Lord Krishna guide your spiritual journey!")

    def run_setup(self):
        """Run complete production setup."""
        try:
            self.print_banner()
            
            # Gather all configuration
            gemini_config = self.setup_gemini_api()
            cosmos_config = self.setup_cosmos_db()
            auth_config = self.setup_entra_id()
            additional_config = self.setup_additional_config()
            
            # Merge all config
            full_config = {**gemini_config, **cosmos_config, **auth_config, **additional_config}
            
            # Create configuration files
            self.create_backend_config(full_config)
            self.create_frontend_config(full_config)
            
            # Optional steps
            self.populate_sacred_texts()
            self.run_production_tests()
            
            # Final instructions
            self.print_next_steps()
            
        except KeyboardInterrupt:
            print("\n\n❌ Setup cancelled by user.")
            sys.exit(1)
        except Exception as e:
            print(f"\n\n❌ Setup failed: {e}")
            logger.exception("Setup error")
            sys.exit(1)

if __name__ == "__main__":
    setup = ProductionSetup()
    setup.run_setup()
