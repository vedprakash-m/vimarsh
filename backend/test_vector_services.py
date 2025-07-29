#!/usr/bin/env python3
"""
Quick Vector Database Test
Tests the vector database services directly
"""

import os
import sys
import asyncio
import logging

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(backend_dir)
sys.path.insert(0, root_dir)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_vector_database():
    """Test vector database functionality"""
    try:
        logger.info("🔧 Testing Vector Database Services...")
        
        # Test imports
        from backend.services.vector_database_service import VectorDatabaseService
        from backend.services.rag_integration_service import RAGIntegrationService
        from backend.admin.vector_database_admin import VectorDatabaseAdmin
        
        logger.info("✅ All imports successful")
        
        # Test vector service initialization
        vector_service = VectorDatabaseService()
        logger.info("✅ Vector service created")
        
        # Test health check
        health_info = await vector_service.health_check()
        logger.info(f"✅ Health check completed: {health_info.get('status', 'unknown')}")
        
        # Test RAG service
        rag_service = RAGIntegrationService()
        logger.info("✅ RAG service initialized")
        
        # Test admin service
        admin_service = VectorDatabaseAdmin()
        logger.info("✅ Admin service initialized")
        
        logger.info("🎉 All vector database services are working!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_vector_database())
    sys.exit(0 if success else 1)
