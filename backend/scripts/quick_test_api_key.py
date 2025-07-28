#!/usr/bin/env python3
"""
Quick test script to verify Gemini API key works for embeddings
Run this with your API key to verify the embedding service works
"""

import os
import sys

def test_with_api_key(api_key):
    """Test embedding service with provided API key"""
    
    # Set environment variable temporarily
    os.environ["GEMINI_API_KEY"] = api_key
    
    # Add parent directory to path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    try:
        from services.gemini_embedding_service import GeminiEmbeddingService
        
        print("🧪 Testing Gemini embedding service...")
        service = GeminiEmbeddingService()
        
        # Test simple embedding
        result = service.generate_embedding("Hello, spiritual world!")
        print(f"✅ Success! Generated {result.dimension}-dimensional embedding")
        print(f"   Model: {result.model}")
        print(f"   First 5 values: {result.embedding[:5]}")
        
        # Test similarity
        result2 = service.generate_embedding("Spiritual guidance and wisdom")
        similarity = service.calculate_similarity(result.embedding, result2.embedding)
        print(f"✅ Similarity calculation works: {similarity:.4f}")
        
        print("🎉 Gemini embedding service is working perfectly!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🔑 Gemini API Key Test")
    print("=" * 40)
    
    # Check if API key is provided as argument
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    else:
        # Ask for API key
        api_key = input("Enter your Gemini API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided")
        sys.exit(1)
    
    success = test_with_api_key(api_key)
    sys.exit(0 if success else 1)
