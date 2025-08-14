#!/usr/bin/env python3
"""
Simple embedding test to diagnose issues
"""

import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../../.env')

async def test_embedding_generation():
    """Test basic embedding generation to identify issues"""
    try:
        import google.generativeai as genai
        
        # Get API key
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("❌ GEMINI_API_KEY not found in environment variables")
            return False
            
        print(f"✅ API key found: {api_key[:10]}...")
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        print("✅ Gemini configured successfully")
        
        # Test simple embedding
        test_text = "This is a simple test for embedding generation."
        print(f"🧪 Testing embedding generation with: '{test_text}'")
        
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=test_text,
            task_type="retrieval_document"
        )
        
        embedding = result['embedding']
        print(f"✅ Embedding generated successfully!")
        print(f"   Dimensions: {len(embedding)}")
        print(f"   First 5 values: {embedding[:5]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during embedding test: {str(e)}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

async def test_cosmos_connection():
    """Test Cosmos DB connection"""
    try:
        from azure.cosmos import CosmosClient
        
        connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
        if not connection_string:
            print("❌ AZURE_COSMOS_CONNECTION_STRING not found")
            return False
            
        print("✅ Cosmos connection string found")
        
        client = CosmosClient.from_connection_string(connection_string)
        database = client.get_database_client('vimarsh-multi-personality')
        container = database.get_container_client('personality-vectors')
        
        # Test simple query
        test_query = "SELECT TOP 1 * FROM c"
        items = list(container.query_items(query=test_query, enable_cross_partition_query=True))
        
        print(f"✅ Cosmos DB connection successful!")
        print(f"   Retrieved {len(items)} test items")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during Cosmos test: {str(e)}")
        print(f"   Error type: {type(e).__name__}")
        return False

async def test_rate_limiting():
    """Test rate limiting behavior"""
    try:
        import google.generativeai as genai
        import time
        
        api_key = os.getenv('GEMINI_API_KEY')
        genai.configure(api_key=api_key)
        
        print("🧪 Testing rate limiting with 3 rapid requests...")
        
        for i in range(3):
            start_time = time.time()
            
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=f"Test request {i+1}",
                task_type="retrieval_document"
            )
            
            end_time = time.time()
            print(f"   Request {i+1}: {end_time - start_time:.2f}s")
            
        print("✅ Rate limiting test passed")
        return True
        
    except Exception as e:
        print(f"❌ Rate limiting test failed: {str(e)}")
        return False

async def main():
    """Run all diagnostic tests"""
    print("🔍 Running Embedding Diagnostic Tests")
    print("=" * 50)
    
    # Test 1: Basic embedding generation
    print("\n1️⃣ Testing basic embedding generation...")
    embedding_ok = await test_embedding_generation()
    
    # Test 2: Cosmos DB connection
    print("\n2️⃣ Testing Cosmos DB connection...")
    cosmos_ok = await test_cosmos_connection()
    
    # Test 3: Rate limiting
    if embedding_ok:
        print("\n3️⃣ Testing rate limiting...")
        rate_ok = await test_rate_limiting()
    else:
        rate_ok = False
    
    print("\n" + "=" * 50)
    print("📊 Diagnostic Results:")
    print(f"   Embedding generation: {'✅ OK' if embedding_ok else '❌ FAILED'}")
    print(f"   Cosmos DB connection: {'✅ OK' if cosmos_ok else '❌ FAILED'}")
    print(f"   Rate limiting: {'✅ OK' if rate_ok else '❌ FAILED'}")
    
    if embedding_ok and cosmos_ok:
        print("\n🎉 All tests passed! The embedding system should work.")
        print("💡 If you're still seeing errors, they might be:")
        print("   - API quota/billing limits")
        print("   - Network connectivity issues")
        print("   - Specific text content causing problems")
    else:
        print("\n⚠️ Some tests failed. Please address these issues before running embeddings.")

if __name__ == "__main__":
    asyncio.run(main())
