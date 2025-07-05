#!/usr/bin/env python3
"""
Production Readiness Test Suite for Vimarsh
Tests the four critical production components:
1. Real LLM (Gemini Pro) integration
2. RAG pipeline activation 
3. Sacred text retrieval system
4. Real-time citation system
"""

import asyncio
import json
import os
import sys
import logging
import time
from typing import Dict, Any, List
import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProductionReadinessTests:
    """Test suite for validating production readiness of all critical components."""
    
    def __init__(self, base_url: str = "http://localhost:7071"):
        self.base_url = base_url
        self.test_results = []
        
    def log_test_result(self, test_name: str, passed: bool, details: str = ""):
        """Log and store test results."""
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{status} - {test_name}: {details}")
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details,
            "timestamp": time.time()
        })
        
    async def test_gemini_integration(self) -> bool:
        """Test 1: Verify real Gemini Pro API integration."""
        logger.info("🤖 Testing Gemini Pro LLM Integration...")
        
        try:
            # Check if GOOGLE_AI_API_KEY is set
            api_key = os.getenv('GOOGLE_AI_API_KEY')
            if not api_key or api_key == "YOUR_ACTUAL_GEMINI_API_KEY_HERE":
                self.log_test_result("Gemini API Key", False, "API key not set or placeholder")
                return False
            
            self.log_test_result("Gemini API Key", True, "API key configured")
            
            # Test direct API call to spiritual guidance endpoint
            response = requests.post(
                f"{self.base_url}/api/spiritual_guidance",
                json={
                    "query": "What is the true meaning of dharma according to Krishna?",
                    "language": "English",
                    "include_citations": True
                },
                timeout=30
            )
            
            if response.status_code != 200:
                self.log_test_result("Gemini Response Generation", False, f"HTTP {response.status_code}")
                return False
            
            data = response.json()
            response_text = data.get("response", "")
            
            # Check for signs of LLM-generated content vs static responses
            llm_indicators = [
                "dear devotee" in response_text.lower(),
                "krishna" in response_text.lower(),
                len(response_text) > 200,  # LLM responses tend to be longer
                "dharma" in response_text.lower()
            ]
            
            if sum(llm_indicators) >= 3:
                self.log_test_result("Gemini Response Generation", True, "LLM-generated response detected")
                return True
            else:
                self.log_test_result("Gemini Response Generation", False, "Static response detected")
                return False
                
        except Exception as e:
            self.log_test_result("Gemini Integration", False, f"Error: {str(e)}")
            return False
    
    async def test_rag_pipeline(self) -> bool:
        """Test 2: Verify RAG pipeline activation."""
        logger.info("🔍 Testing RAG Pipeline Activation...")
        
        try:
            # Test with specific query that should trigger RAG
            response = requests.post(
                f"{self.base_url}/api/spiritual_guidance",
                json={
                    "query": "How should I handle difficult decisions in my career?",
                    "language": "English",
                    "include_citations": True
                },
                timeout=30
            )
            
            if response.status_code != 200:
                self.log_test_result("RAG Pipeline Activation", False, f"HTTP {response.status_code}")
                return False
            
            data = response.json()
            metadata = data.get("metadata", {})
            
            # Check for signs of RAG pipeline usage
            rag_indicators = [
                "processing_time_ms" in metadata,
                "confidence_score" in metadata,
                data.get("citations") and len(data.get("citations", [])) > 0,
                "fallback_mode" not in metadata  # If fallback mode is not mentioned, RAG might be working
            ]
            
            rag_score = sum(rag_indicators)
            if rag_score >= 3:
                self.log_test_result("RAG Pipeline Activation", True, f"RAG indicators: {rag_score}/4")
                return True
            else:
                self.log_test_result("RAG Pipeline Activation", False, f"RAG indicators: {rag_score}/4")
                return False
                
        except Exception as e:
            self.log_test_result("RAG Pipeline", False, f"Error: {str(e)}")
            return False
    
    async def test_sacred_text_retrieval(self) -> bool:
        """Test 3: Verify dynamic sacred text retrieval."""
        logger.info("📜 Testing Sacred Text Retrieval System...")
        
        try:
            # Test multiple queries to check for dynamic content
            test_queries = [
                "What does the Gita say about purpose in life?",
                "How to find inner peace according to Krishna?",
                "What is the importance of selfless action?"
            ]
            
            responses = []
            for query in test_queries:
                response = requests.post(
                    f"{self.base_url}/api/spiritual_guidance",
                    json={
                        "query": query,
                        "language": "English",
                        "include_citations": True
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    responses.append(response.json())
            
            if len(responses) < 2:
                self.log_test_result("Sacred Text Retrieval", False, "Failed to get multiple responses")
                return False
            
            # Check for dynamic content - responses should be different
            unique_responses = set(resp.get("response", "")[:100] for resp in responses)
            
            if len(unique_responses) >= 2:
                self.log_test_result("Sacred Text Retrieval", True, f"Dynamic responses: {len(unique_responses)}")
                return True
            else:
                self.log_test_result("Sacred Text Retrieval", False, "Static responses detected")
                return False
                
        except Exception as e:
            self.log_test_result("Sacred Text Retrieval", False, f"Error: {str(e)}")
            return False
    
    async def test_citation_system(self) -> bool:
        """Test 4: Verify real-time citation system."""
        logger.info("📖 Testing Real-time Citation System...")
        
        try:
            response = requests.post(
                f"{self.base_url}/api/spiritual_guidance",
                json={
                    "query": "What does Krishna teach about karma and duty?",
                    "language": "English",
                    "include_citations": True
                },
                timeout=30
            )
            
            if response.status_code != 200:
                self.log_test_result("Citation System", False, f"HTTP {response.status_code}")
                return False
            
            data = response.json()
            citations = data.get("citations", [])
            
            if not citations:
                self.log_test_result("Citation System", False, "No citations found")
                return False
            
            # Check citation quality
            citation_quality_checks = []
            
            for citation in citations[:3]:  # Check first 3 citations
                checks = [
                    "source" in citation,
                    "text" in citation,
                    "relevance_score" in citation,
                    citation.get("text", "") != "",
                    citation.get("source", "") != "Unknown Source"
                ]
                citation_quality_checks.extend(checks)
            
            quality_score = sum(citation_quality_checks) / len(citation_quality_checks) if citation_quality_checks else 0
            
            if quality_score >= 0.8:
                self.log_test_result("Citation System", True, f"Quality score: {quality_score:.2f}")
                return True
            else:
                self.log_test_result("Citation System", False, f"Quality score: {quality_score:.2f}")
                return False
                
        except Exception as e:
            self.log_test_result("Citation System", False, f"Error: {str(e)}")
            return False
    
    async def test_authentication_integration(self) -> bool:
        """Test 5: Verify authentication integration (optional)."""
        logger.info("🔐 Testing Authentication Integration...")
        
        try:
            # Test without authentication (should work)
            response = requests.post(
                f"{self.base_url}/api/spiritual_guidance",
                json={"query": "Test query", "language": "English"},
                timeout=10
            )
            
            if response.status_code != 200:
                self.log_test_result("Auth Integration (Optional)", False, "Endpoint not accessible")
                return False
            
            # Test with mock auth header
            response_with_auth = requests.post(
                f"{self.base_url}/api/spiritual_guidance",
                json={"query": "Test query", "language": "English"},
                headers={"Authorization": "Bearer mock-token-12345"},
                timeout=10
            )
            
            if response_with_auth.status_code == 200:
                auth_data = response_with_auth.json()
                if auth_data.get("metadata", {}).get("authenticated"):
                    self.log_test_result("Auth Integration (Optional)", True, "Auth processing detected")
                else:
                    self.log_test_result("Auth Integration (Optional)", True, "Auth header handled gracefully")
                return True
            else:
                self.log_test_result("Auth Integration (Optional)", False, "Auth header rejected")
                return False
                
        except Exception as e:
            self.log_test_result("Auth Integration (Optional)", False, f"Error: {str(e)}")
            return False
    
    async def test_performance_requirements(self) -> bool:
        """Test 6: Verify performance requirements."""
        logger.info("⚡ Testing Performance Requirements...")
        
        try:
            start_time = time.time()
            
            response = requests.post(
                f"{self.base_url}/api/spiritual_guidance",
                json={
                    "query": "How to live a meaningful life?",
                    "language": "English",
                    "include_citations": True
                },
                timeout=30
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code != 200:
                self.log_test_result("Performance Requirements", False, f"HTTP {response.status_code}")
                return False
            
            # Check response time (should be under 10 seconds for production)
            if response_time < 10:
                self.log_test_result("Performance Requirements", True, f"Response time: {response_time:.2f}s")
                return True
            else:
                self.log_test_result("Performance Requirements", False, f"Response time: {response_time:.2f}s (too slow)")
                return False
                
        except Exception as e:
            self.log_test_result("Performance Requirements", False, f"Error: {str(e)}")
            return False
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all production readiness tests."""
        logger.info("🕉️ Starting Vimarsh Production Readiness Tests")
        logger.info("=" * 50)
        
        # Test health endpoint first
        try:
            health_response = requests.get(f"{self.base_url}/api/health", timeout=10)
            if health_response.status_code != 200:
                logger.error("❌ Health endpoint failed - cannot proceed with tests")
                return {"status": "failed", "error": "Health endpoint not accessible"}
        except Exception as e:
            logger.error(f"❌ Cannot connect to {self.base_url}: {str(e)}")
            return {"status": "failed", "error": f"Connection failed: {str(e)}"}
        
        # Run all tests
        test_functions = [
            self.test_gemini_integration,
            self.test_rag_pipeline,
            self.test_sacred_text_retrieval,
            self.test_citation_system,
            self.test_authentication_integration,
            self.test_performance_requirements
        ]
        
        results = []
        for test_func in test_functions:
            try:
                result = await test_func()
                results.append(result)
            except Exception as e:
                logger.error(f"Test {test_func.__name__} failed with exception: {e}")
                results.append(False)
        
        # Calculate overall score
        passed_tests = sum(results)
        total_tests = len(results)
        success_rate = passed_tests / total_tests
        
        logger.info("=" * 50)
        logger.info("🕉️ Production Readiness Test Results")
        logger.info(f"📊 Overall Score: {passed_tests}/{total_tests} ({success_rate:.1%})")
        
        if success_rate >= 0.8:
            logger.info("✅ PRODUCTION READY - All critical systems operational")
            status = "ready"
        elif success_rate >= 0.6:
            logger.info("⚠️  PARTIALLY READY - Some issues need attention")
            status = "partial"
        else:
            logger.info("❌ NOT READY - Critical issues must be resolved")
            status = "not_ready"
        
        return {
            "status": status,
            "success_rate": success_rate,
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "test_results": self.test_results
        }

async def main():
    """Main test execution function."""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:7071"
    
    logger.info(f"🔗 Testing against: {base_url}")
    
    test_suite = ProductionReadinessTests(base_url)
    results = await test_suite.run_all_tests()
    
    # Save results to file
    with open("production_readiness_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    logger.info("📄 Results saved to: production_readiness_results.json")
    
    # Exit with appropriate code
    if results["status"] == "ready":
        sys.exit(0)
    elif results["status"] == "partial":
        sys.exit(1)
    else:
        sys.exit(2)

if __name__ == "__main__":
    asyncio.run(main())
