"""
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
