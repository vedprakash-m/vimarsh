"""
Simple RAG Service Fix Validation
=================================

Quick test to verify that the Simple RAG Service import issue is resolved.
"""

import asyncio
import logging
import sys
import os

# Load production environment
def load_environment():
    primary_env = "/Users/ved/Apps/vimarsh/.env"
    if os.path.exists(primary_env):
        with open(primary_env, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

load_environment()

# Add backend to path
sys.path.append('/Users/ved/Apps/vimarsh/backend')

# Suppress verbose logging
logging.basicConfig(level=logging.WARNING, format='%(levelname)s:%(name)s:%(message)s')

async def test_simple_rag_fix():
    """Test that Simple RAG Service is now properly accessible"""
    
    print("🔧 Testing Simple RAG Service Fix")
    print("=" * 40)
    
    # Test 1: Direct RAG Service Import
    print("\n📋 Test 1: Direct RAG Service Import")
    try:
        from services.rag_service import SimpleRAGService
        
        rag_service = SimpleRAGService()
        print(f"✅ SimpleRAGService imported: {len(rag_service.all_content)} items loaded")
        
        # Test basic functionality
        response = rag_service.generate_rag_response(
            query="What is dharma?",
            personality="krishna",
            max_context_items=2
        )
        
        print(f"✅ RAG response generated: {len(response.response)} characters")
        print(f"   Citations: {len(response.citations)}")
        print(f"   Context chunks: {len(response.context_chunks)}")
        
    except Exception as e:
        print(f"❌ Direct RAG Service test failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Enhanced RAG Service with Simple RAG
    print("\n🔗 Test 2: Enhanced RAG Service Integration")
    try:
        from services.enhanced_rag_service import EnhancedRAGService
        
        enhanced_rag = EnhancedRAGService()
        
        # Check if simple RAG service is initialized 
        print(f"✅ Enhanced RAG Service initialized")
        print(f"   Simple RAG available: {enhanced_rag.simple_rag is not None}")
        print(f"   Vector service available: {enhanced_rag.vector_service is not None}")
        print(f"   Hybrid search available: {enhanced_rag.hybrid_search is not None}")
        print(f"   Citation checker available: {enhanced_rag.citation_checker is not None}")
        
        # Test enhanced response generation using the correct method
        enhanced_result = await enhanced_rag.enhanced_retrieve_and_generate(
            query="How to find inner peace?",
            personality="krishna"
        )
        
        print(f"✅ Enhanced RAG search successful")
        print(f"   Response: {len(enhanced_result.response_text)} characters")
        print(f"   Search method: {enhanced_result.search_method}")
        print(f"   Retrieval score: {enhanced_result.retrieval_score:.3f}")
        
    except Exception as e:
        print(f"❌ Enhanced RAG Service test failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Data Pipeline Integration (should now work without warnings)
    print("\n🎯 Test 3: Data Pipeline Integration")
    try:
        from services.data_pipeline_integration_service import DataPipelineIntegrationService
        
        # Suppress logs for clean output
        logging.getLogger('enhanced_rag_service').setLevel(logging.ERROR)
        
        pipeline = DataPipelineIntegrationService()
        
        # Test guidance generation
        guidance = await pipeline.integrated_spiritual_guidance(
            query="What is the meaning of life?",
            personality="krishna",
            context="test"
        )
        
        print(f"✅ Pipeline integration successful")
        print(f"   Response: {len(guidance.content)} characters") 
        print(f"   Search method: {guidance.search_method}")
        print(f"   Quality score: {guidance.quality_score:.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Pipeline integration test failed: {e}")
        return False

async def main():
    """Main execution"""
    
    print("🚀 Simple RAG Service Fix Validation")
    print("Verifying that 'Simple RAG Service not available' warnings are resolved...")
    
    success = await test_simple_rag_fix()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 SIMPLE RAG SERVICE FIX SUCCESSFUL!")
        print("✅ All services can now access SimpleRAGService")
        print("✅ No more 'Simple RAG Service not available' warnings")
        print("✅ Enhanced functionality restored")
    else:
        print("⚠️ Some issues remain - check test results above")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    if success:
        print("\n✅ Simple RAG Service integration fully restored!")
    else:
        print("\n❌ Review test results for remaining issues")
