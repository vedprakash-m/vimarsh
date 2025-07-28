#!/usr/bin/env python3
"""
Simple Gemini Embedding Test
Tests just the embedding functionality without complex imports
"""

import os
import sys

# Set up path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
root_dir = os.path.dirname(backend_dir)
sys.path.insert(0, backend_dir)

# Load environment from root .env file
try:
    from dotenv import load_dotenv
    env_file = os.path.join(root_dir, '.env')
    if os.path.exists(env_file):
        load_dotenv(env_file)
        print(f"✅ Loaded environment from {env_file}")
    else:
        print("⚠️ No .env file found in root directory")
except ImportError:
    print("⚠️ python-dotenv not available")

# Check if API key is available
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_AI_API_KEY")
if api_key:
    print(f"✅ API key found (length: {len(api_key)})")
else:
    print("❌ No API key found")
    sys.exit(1)

# Test Google Generative AI package
try:
    import google.generativeai as genai
    print("✅ google-generativeai package available")
except ImportError as e:
    print(f"❌ google-generativeai package not available: {e}")
    sys.exit(1)

# Test numpy
try:
    import numpy as np
    print("✅ numpy package available")
except ImportError as e:
    print(f"❌ numpy package not available: {e}")
    sys.exit(1)

# Now test the embedding service directly
try:
    print("\n🧪 Testing Gemini embedding generation...")
    
    # Configure Gemini
    genai.configure(api_key=api_key)
    
    # Test embedding generation
    test_text = "What is the meaning of dharma in spiritual practice?"
    
    result = genai.embed_content(
        model="models/text-embedding-004",
        content=test_text,
        task_type="RETRIEVAL_DOCUMENT"
    )
    
    embedding = result['embedding']
    
    print(f"✅ Successfully generated embedding!")
    print(f"   Text: {test_text}")
    print(f"   Embedding dimension: {len(embedding)}")
    print(f"   First 5 values: {embedding[:5]}")
    
    # Test query embedding
    query_result = genai.embed_content(
        model="models/text-embedding-004",
        content="dharma spiritual guidance",
        task_type="RETRIEVAL_QUERY"
    )
    
    query_embedding = query_result['embedding']
    print(f"✅ Query embedding generated (dimension: {len(query_embedding)})")
    
    # Test similarity calculation
    vec1 = np.array(embedding)
    vec2 = np.array(query_embedding)
    
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    similarity = dot_product / (norm1 * norm2)
    print(f"✅ Similarity calculation: {similarity:.4f}")
    
    print("\n🎉 All tests passed! Gemini embeddings are working correctly.")
    print("✅ Ready to proceed with vector database migration")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
