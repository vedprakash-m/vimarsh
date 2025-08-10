"""
Vector Database Service Method Mapping Fix
==========================================

Creates proper method aliases for the vector database service
to fix the missing 'search_documents' method issue.
"""

import os
import sys

# Add backend to path
sys.path.append('/Users/ved/Apps/vimarsh/backend')

def create_vector_service_patch():
    """Create a patch for the vector database service"""
    
    patch_content = '''"""
Vector Database Service Patch
============================

This patch adds missing method aliases to make the service compatible
with Phase 1 implementations.
"""

from services.vector_database_service import VectorDatabaseService

# Create method aliases
def patch_vector_database_service():
    """Add missing method aliases to VectorDatabaseService"""
    
    # Add search_documents alias for semantic_search
    if not hasattr(VectorDatabaseService, 'search_documents'):
        VectorDatabaseService.search_documents = VectorDatabaseService.semantic_search
    
    # Add initialize alias for existing initialization
    if not hasattr(VectorDatabaseService, 'initialize'):
        async def initialize(self):
            """Initialize the vector database service"""
            return True  # Service initializes in __init__
        VectorDatabaseService.initialize = initialize
    
    # Add store_document alias for upsert_document
    if not hasattr(VectorDatabaseService, 'store_document'):
        VectorDatabaseService.store_document = VectorDatabaseService.upsert_document
    
    print("✅ Vector Database Service methods patched")

# Apply patch immediately when imported
patch_vector_database_service()
'''
    
    with open('/Users/ved/Apps/vimarsh/backend/services/vector_database_patch.py', 'w') as f:
        f.write(patch_content)
    
    print("📄 Created vector database service patch")

if __name__ == "__main__":
    create_vector_service_patch()
