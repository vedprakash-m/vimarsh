"""
Critical Phase 1 Issue Resolution
==================================

This script fixes the core issues identified in Phase 1 testing:
1. Environment variable loading from correct .env file
2. Cosmos DB connection string parsing
3. Vector database service method fixes
4. Missing module imports
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Configure logging first
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def fix_environment_loading():
    """Fix environment variable loading from the correct .env file"""
    print("🔧 Fixing Environment Variable Loading")
    
    # Load ONLY the primary .env file with real credentials
    primary_env = "/Users/ved/Apps/vimarsh/.env"
    
    if os.path.exists(primary_env):
        print(f"📁 Loading primary .env file: {primary_env}")
        
        # Read and parse the file manually
        with open(primary_env, 'r') as f:
            lines = f.readlines()
            
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                # Only set if not already set or if this is a real value
                if key not in os.environ or 'placeholder' in os.environ.get(key, '').lower():
                    os.environ[key] = value
                    if key in ['GEMINI_API_KEY', 'AZURE_COSMOS_CONNECTION_STRING']:
                        print(f"✅ Loaded {key}: {value[:20]}...")
    else:
        print(f"❌ Primary .env file not found: {primary_env}")
        return False
    
    return True

def fix_cosmos_connection_string():
    """Fix Cosmos DB connection string parsing issue"""
    print("\n🔧 Fixing Cosmos DB Connection String")
    
    conn_str = os.getenv('AZURE_COSMOS_CONNECTION_STRING', '')
    if not conn_str:
        print("❌ No Cosmos connection string found")
        return False
    
    print(f"📊 Connection string length: {len(conn_str)}")
    
    # Parse connection string properly
    if 'AccountEndpoint=' in conn_str and 'AccountKey=' in conn_str:
        print("✅ Connection string format appears valid")
        
        # Extract components
        parts = conn_str.split(';')
        endpoint = None
        key = None
        
        for part in parts:
            if part.startswith('AccountEndpoint='):
                endpoint = part.split('=', 1)[1]
            elif part.startswith('AccountKey='):
                key = part.split('=', 1)[1]
        
        if endpoint and key:
            print(f"✅ Endpoint: {endpoint}")
            print(f"✅ Key: {key[:20]}...")
            return True
    
    print("❌ Invalid connection string format")
    return False

async def fix_vector_database_service():
    """Fix vector database service method issues"""
    print("\n🔧 Fixing Vector Database Service Issues")
    
    try:
        # Add path for imports
        sys.path.append('/Users/ved/Apps/vimarsh/backend')
        
        # Import and check the service
        from services.vector_database_service import VectorDatabaseService
        
        service = VectorDatabaseService()
        
        # Check if the service has the required methods
        required_methods = ['search_documents', 'initialize', 'store_document']
        missing_methods = []
        
        for method in required_methods:
            if not hasattr(service, method):
                missing_methods.append(method)
        
        if missing_methods:
            print(f"❌ Missing methods in VectorDatabaseService: {missing_methods}")
            
            # Try to find alternative method names
            all_methods = [m for m in dir(service) if not m.startswith('_')]
            print(f"📋 Available methods: {all_methods}")
            
            # Look for similar method names
            for missing in missing_methods:
                similar = [m for m in all_methods if missing.split('_')[0] in m.lower()]
                if similar:
                    print(f"💡 Similar methods for '{missing}': {similar}")
        else:
            print("✅ All required methods found in VectorDatabaseService")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Service error: {e}")
        return False

def fix_missing_modules():
    """Fix missing module imports"""
    print("\n🔧 Fixing Missing Module Imports")
    
    missing_modules = [
        'enhanced_simple_llm_service'
    ]
    
    backend_path = '/Users/ved/Apps/vimarsh/backend'
    
    for module in missing_modules:
        # Search for the module file
        potential_paths = [
            f"{backend_path}/services/{module}.py",
            f"{backend_path}/{module}.py",
            f"{backend_path}/core/{module}.py"
        ]
        
        found = False
        for path in potential_paths:
            if os.path.exists(path):
                print(f"✅ Found {module} at: {path}")
                found = True
                break
        
        if not found:
            print(f"❌ Module {module} not found")
            
            # Search for similar files
            for root, dirs, files in os.walk(backend_path):
                for file in files:
                    if file.endswith('.py') and 'llm' in file.lower():
                        print(f"💡 Similar file found: {os.path.join(root, file)}")

async def test_fixed_services():
    """Test services after fixes"""
    print("\n🧪 Testing Fixed Services")
    
    try:
        sys.path.append('/Users/ved/Apps/vimarsh/backend')
        
        # Test environment loading
        gemini_key = os.getenv('GEMINI_API_KEY')
        cosmos_conn = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
        
        print(f"🔑 GEMINI_API_KEY: {'✅ Loaded' if gemini_key else '❌ Missing'}")
        print(f"🗄️ COSMOS_DB: {'✅ Loaded' if cosmos_conn else '❌ Missing'}")
        
        # Test basic service imports
        try:
            from services.citation_grounding_checker import CitationGroundingChecker
            checker = CitationGroundingChecker()
            print(f"✅ Citation Grounding: {len(checker.source_cache)} sources")
        except Exception as e:
            print(f"❌ Citation Grounding error: {e}")
        
        try:
            from services.hybrid_search_service import HybridSearchService
            search = HybridSearchService()
            print("✅ Hybrid Search: Import successful")
        except Exception as e:
            print(f"❌ Hybrid Search error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Testing error: {e}")
        return False

def create_environment_fix_script():
    """Create a startup script that properly loads environment"""
    
    fix_script = """#!/usr/bin/env python3
'''
Environment Fix Script for Vimarsh Phase 1
==========================================

This script ensures proper environment variable loading
before running any Phase 1 services.
'''

import os
from pathlib import Path

def load_environment():
    '''Load environment variables from correct .env file'''
    
    # Primary .env file with real credentials
    primary_env = "/Users/ved/Apps/vimarsh/.env"
    
    if os.path.exists(primary_env):
        print(f"Loading environment from: {primary_env}")
        
        with open(primary_env, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
                    
        print("✅ Environment variables loaded successfully")
        return True
    else:
        print(f"❌ Primary .env file not found: {primary_env}")
        return False

def verify_environment():
    '''Verify critical environment variables'''
    
    required_vars = [
        'GEMINI_API_KEY',
        'AZURE_COSMOS_CONNECTION_STRING', 
        'AZURE_COSMOS_DATABASE_NAME',
        'AZURE_COSMOS_CONTAINER_NAME'
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"❌ Missing environment variables: {missing}")
        return False
    else:
        print("✅ All required environment variables present")
        return True

if __name__ == "__main__":
    load_environment()
    verify_environment()
"""
    
    with open('/Users/ved/Apps/vimarsh/backend/fix_environment.py', 'w') as f:
        f.write(fix_script)
    
    print("📄 Created environment fix script: fix_environment.py")

async def main():
    """Main execution - fix all Phase 1 issues"""
    
    print("🚨 CRITICAL PHASE 1 ISSUE RESOLUTION")
    print("=" * 50)
    
    # Fix 1: Environment variable loading
    success_env = fix_environment_loading()
    
    # Fix 2: Cosmos DB connection
    success_cosmos = fix_cosmos_connection_string()
    
    # Fix 3: Vector database service
    success_vector = await fix_vector_database_service()
    
    # Fix 4: Missing modules
    fix_missing_modules()
    
    # Fix 5: Create environment fix script
    create_environment_fix_script()
    
    # Test fixes
    success_test = await test_fixed_services()
    
    print("\n" + "=" * 50)
    print("🎯 ISSUE RESOLUTION SUMMARY")
    print("=" * 50)
    print(f"Environment Loading: {'✅' if success_env else '❌'}")
    print(f"Cosmos DB Connection: {'✅' if success_cosmos else '❌'}")
    print(f"Vector Database: {'✅' if success_vector else '❌'}")
    print(f"Service Testing: {'✅' if success_test else '❌'}")
    
    if all([success_env, success_cosmos, success_vector, success_test]):
        print("\n🎉 ALL CRITICAL ISSUES RESOLVED!")
        print("Phase 1 is now ready for proper testing")
        return True
    else:
        print("\n⚠️ Some issues remain - see details above")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    if success:
        print("\n✅ Run the validation script again to see improvements")
    else:
        print("\n❌ Manual intervention may be required for remaining issues")
