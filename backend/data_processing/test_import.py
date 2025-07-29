#!/usr/bin/env python3
"""Test import of embedding service"""

import os
import sys

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, backend_path)

print(f"Python path: {sys.path}")
print(f"Backend path: {backend_path}")
print(f"Current dir: {os.getcwd()}")

try:
    from services.gemini_embedding_service import get_gemini_embedding_service
    print("✅ Successfully imported get_gemini_embedding_service")
    
    # Try to initialize the service
    service = get_gemini_embedding_service()
    print(f"✅ Successfully created embedding service: {service}")
    
    # Test simple embedding
    result = service.generate_embedding("This is a test", task_type="RETRIEVAL_DOCUMENT")
    print(f"✅ Test embedding result: success={result.success}, dimensions={len(result.embedding) if result.embedding else 'None'}")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Other error: {e}")
