#!/usr/bin/env python3
"""
Diagnostic script to test Enhanced RAG service dependencies
"""

import os
import sys
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import centralized AI model configuration
try:
    from config.ai_models import AI_CONFIG
    GEMINI_MODEL = AI_CONFIG.gemini_generation_model
except ImportError:
    # Fallback if config not available  
    GEMINI_MODEL = "models/gemini-2.5-flash"

async def test_environment_variables():
    """Test if all required environment variables are set"""
    print("🔍 Testing Environment Variables...")
    
    required_vars = [
        'AZURE_COSMOS_CONNECTION_STRING',
        'GEMINI_API_KEY',
        'AZURE_COSMOS_DATABASE_NAME',
        'AZURE_COSMOS_CONTAINER_NAME'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: Present (length: {len(value)})")
        else:
            print(f"❌ {var}: Missing")
            missing_vars.append(var)
    
    return len(missing_vars) == 0, missing_vars

async def test_package_imports():
    """Test if required packages can be imported"""
    print("\n🔍 Testing Package Imports...")
    
    try:
        import google.generativeai as genai
        print("✅ google.generativeai: Available")
        genai_available = True
    except ImportError as e:
        print(f"❌ google.generativeai: {e}")
        genai_available = False
    
    try:
        import azure.cosmos.cosmos_client as cosmos_client
        print("✅ azure.cosmos: Available")
        cosmos_available = True
    except ImportError as e:
        print(f"❌ azure.cosmos: {e}")
        cosmos_available = False
    
    try:
        import numpy as np
        print("✅ numpy: Available")
        numpy_available = True
    except ImportError as e:
        print(f"❌ numpy: {e}")
        numpy_available = False
    
    return genai_available and cosmos_available, {
        'genai': genai_available,
        'cosmos': cosmos_available, 
        'numpy': numpy_available
    }

async def test_cosmos_connection():
    """Test Cosmos DB connection"""
    print("\n🔍 Testing Cosmos DB Connection...")
    
    connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
    if not connection_string:
        print("❌ No connection string available")
        return False, "No connection string"
    
    try:
        import azure.cosmos.cosmos_client as cosmos_client
        client = cosmos_client.CosmosClient.from_connection_string(connection_string)
        
        # Test database access
        database_name = os.getenv('AZURE_COSMOS_DATABASE_NAME', 'vimarsh-multi-personality')
        database = client.get_database_client(database_name)
        
        # Test container access
        container_name = os.getenv('AZURE_COSMOS_CONTAINER_NAME', 'personality_vectors')
        container = database.get_container_client(container_name)
        
        # Try a simple read operation
        # This will fail if database/container doesn't exist
        properties = container.read()
        print(f"✅ Cosmos DB connected: {database_name}/{container_name}")
        print(f"   Container properties: {properties.get('id', 'unknown')}")
        return True, "Connected successfully"
        
    except Exception as e:
        print(f"❌ Cosmos DB connection failed: {str(e)}")
        return False, str(e)

async def test_gemini_api():
    """Test Gemini API configuration and connectivity"""
    print("\n🔍 Testing Gemini AI API...")
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ No API key available")
        return False, "No API key"
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        # Test with a simple generation
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content("Say hello")
        
        if response and response.text:
            print(f"✅ Gemini API working: {response.text[:50]}...")
            return True, "API working"
        else:
            print("❌ Gemini API returned no response")
            return False, "No response from API"
            
    except Exception as e:
        print(f"❌ Gemini API failed: {str(e)}")
        return False, str(e)

async def test_enhanced_rag_initialization():
    """Test Enhanced RAG service initialization"""
    print("\n🔍 Testing Enhanced RAG Service Initialization...")
    
    try:
        from services.enhanced_rag_service_v6 import EnhancedRAGService
        service = EnhancedRAGService()
        print("✅ Enhanced RAG service initialized successfully")
        return True, service
    except Exception as e:
        print(f"❌ Enhanced RAG service initialization failed: {str(e)}")
        return False, str(e)

async def main():
    """Run all diagnostic tests"""
    print("🧪 Enhanced RAG Service Diagnostic Report")
    print("=" * 50)
    
    # Test 1: Environment Variables
    env_ok, missing_vars = await test_environment_variables()
    
    # Test 2: Package Imports  
    imports_ok, import_status = await test_package_imports()
    
    # Test 3: Cosmos DB Connection
    cosmos_ok, cosmos_msg = await test_cosmos_connection()
    
    # Test 4: Gemini API
    gemini_ok, gemini_msg = await test_gemini_api()
    
    # Test 5: Service Initialization
    service_ok, service_result = await test_enhanced_rag_initialization()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 DIAGNOSTIC SUMMARY:")
    print(f"Environment Variables: {'✅ PASS' if env_ok else '❌ FAIL'}")
    if not env_ok:
        print(f"   Missing: {missing_vars}")
    
    print(f"Package Imports: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    if not imports_ok:
        print(f"   Issues: {import_status}")
    
    print(f"Cosmos DB Connection: {'✅ PASS' if cosmos_ok else '❌ FAIL'}")
    if not cosmos_ok:
        print(f"   Error: {cosmos_msg}")
    
    print(f"Gemini AI API: {'✅ PASS' if gemini_ok else '❌ FAIL'}")
    if not gemini_ok:
        print(f"   Error: {gemini_msg}")
    
    print(f"Enhanced RAG Service: {'✅ PASS' if service_ok else '❌ FAIL'}")
    if not service_ok:
        print(f"   Error: {service_result}")
    
    # Overall assessment
    all_ok = env_ok and imports_ok and cosmos_ok and gemini_ok and service_ok
    print(f"\n🎯 OVERALL STATUS: {'✅ ALL SYSTEMS GO' if all_ok else '❌ ISSUES DETECTED'}")
    
    if not all_ok:
        print("\n🔧 RECOMMENDED ACTIONS:")
        if not env_ok:
            print("   1. Set missing environment variables")
        if not imports_ok:
            print("   2. Install missing Python packages")
        if not cosmos_ok:
            print("   3. Fix Cosmos DB connection/configuration")
        if not gemini_ok:
            print("   4. Fix Gemini API key/configuration")
        if not service_ok:
            print("   5. Debug Enhanced RAG service initialization")

if __name__ == "__main__":
    asyncio.run(main())
