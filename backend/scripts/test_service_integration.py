#!/usr/bin/env python3
"""
Test Gemini Embedding Service Integration
Tests the full service with proper environment setup
"""

import os
import sys

# Set up environment and paths
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
root_dir = os.path.dirname(backend_dir)
sys.path.insert(0, backend_dir)

# Load environment
try:
    from dotenv import load_dotenv
    env_file = os.path.join(root_dir, '.env')
    if os.path.exists(env_file):
        load_dotenv(env_file)
        print(f"✅ Loaded environment from {env_file}")
except ImportError:
    pass

# Test the service
try:
    from services.gemini_embedding_service import GeminiEmbeddingService, GeminiTransformer
    
    print("\n🧪 Testing GeminiEmbeddingService...")
    
    # Test direct service initialization
    service = GeminiEmbeddingService()
    print("✅ Service initialized successfully")
    
    # Test embedding generation
    result = service.generate_embedding("Spiritual wisdom and guidance")
    print(f"✅ Embedding generated - Dimension: {result.dimension}")
    print(f"   Model: {result.model}")
    
    # Test batch embeddings
    texts = ["dharma", "karma", "moksha"]
    batch_results = service.generate_embeddings_batch(texts)
    print(f"✅ Batch embeddings generated - {len(batch_results)} embeddings")
    
    # Test query embedding
    query_result = service.generate_query_embedding("what is dharma")
    print(f"✅ Query embedding generated - Dimension: {query_result.dimension}")
    
    # Test similarity
    similarity = service.calculate_similarity(result.embedding, query_result.embedding)
    print(f"✅ Similarity calculated: {similarity:.4f}")
    
    # Test drop-in compatibility
    print("\n🧪 Testing GeminiTransformer compatibility...")
    transformer = GeminiTransformer()
    compat_result = transformer.encode("Test compatibility")
    print(f"✅ Transformer compatibility - Dimension: {len(compat_result)}")
    
    # Test model info
    info = service.get_model_info()
    print(f"\n📊 Model Info:")
    print(f"   Provider: {info['provider']}")
    print(f"   Model: {info['model_name']}")
    print(f"   Dimension: {info['dimension']}")
    print(f"   API-based: {info['api_based']}")
    
    print("\n🎉 All service tests passed!")
    print("✅ GeminiEmbeddingService is fully functional")
    print("✅ Ready for vector database migration")
    
except Exception as e:
    print(f"❌ Service test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
