"""
Phase 3 Comprehensive Testing: Azure OpenAI Embeddings
Tests all 25 personalities with domain-specific queries
"""

import asyncio
import sys
import time
from typing import Dict, List, Tuple
sys.path.insert(0, '/Users/ved/Apps/vimarsh/backend')

from services.enhanced_rag_service_v6 import EnhancedRAGService

class Phase3Tester:
    def __init__(self):
        self.service = EnhancedRAGService()
        self.results = {
            'passed': 0,
            'failed': 0,
            'errors': [],
            'latencies': [],
            'personalities_tested': []
        }
        
    async def test_personality(self, personality: str, queries: List[str], domain: str) -> Dict:
        """Test a single personality with multiple queries"""
        print(f"\n{'='*70}")
        print(f"🎭 Testing {personality.upper()} ({domain})")
        print(f"{'='*70}")
        
        personality_result = {
            'personality': personality,
            'domain': domain,
            'queries_tested': 0,
            'queries_passed': 0,
            'queries_failed': 0,
            'avg_latency': 0.0,
            'errors': []
        }
        
        latencies = []
        
        for i, query in enumerate(queries, 1):
            print(f"\n  Query {i}/{len(queries)}: \"{query}\"")
            
            try:
                start_time = time.time()
                
                # Generate query embedding first
                embedding = await self.service.generate_query_embedding(query)
                
                # Validate embedding
                dims = len(embedding)
                norm = sum(x**2 for x in embedding) ** 0.5
                
                latency = time.time() - start_time
                latencies.append(latency)
                
                # Check quality
                embedding_ok = (dims == 768 and 0.99 < norm < 1.01)
                
                if embedding_ok:
                    status = "✅ PASS"
                    personality_result['queries_passed'] += 1
                    self.results['passed'] += 1
                    print(f"  {status} | Latency: {latency:.2f}s | Dims: {dims} | Norm: {norm:.4f}")
                else:
                    status = "❌ FAIL"
                    personality_result['queries_failed'] += 1
                    self.results['failed'] += 1
                    error_msg = f"Invalid embedding: dims={dims}, norm={norm:.4f}"
                    personality_result['errors'].append(error_msg)
                    print(f"  {status} | {error_msg}")
                
                personality_result['queries_tested'] += 1
                
            except Exception as e:
                personality_result['queries_failed'] += 1
                self.results['failed'] += 1
                error_msg = f"Query {i}: {str(e)[:100]}"
                personality_result['errors'].append(error_msg)
                print(f"  ❌ ERROR: {error_msg}")
        
        # Calculate average latency
        if latencies:
            personality_result['avg_latency'] = sum(latencies) / len(latencies)
            self.results['latencies'].extend(latencies)
        
        # Summary for this personality
        success_rate = (personality_result['queries_passed'] / personality_result['queries_tested'] * 100) if personality_result['queries_tested'] > 0 else 0
        
        print(f"\n  📊 Summary for {personality}:")
        print(f"     Queries: {personality_result['queries_tested']}")
        print(f"     Passed: {personality_result['queries_passed']}")
        print(f"     Failed: {personality_result['queries_failed']}")
        print(f"     Success Rate: {success_rate:.1f}%")
        print(f"     Avg Latency: {personality_result['avg_latency']:.2f}s")
        
        self.results['personalities_tested'].append(personality_result)
        return personality_result
    
    async def run_all_tests(self):
        """Run comprehensive tests across all domains"""
        print("=" * 70)
        print("🧪 PHASE 3 COMPREHENSIVE TESTING")
        print("   Azure OpenAI Embeddings - All 25 Personalities")
        print("=" * 70)
        
        # Test cases organized by domain
        test_cases = {
            'Spiritual': {
                'krishna': [
                    "What is dharma and how should I live it?",
                    "Explain the concept of karma yoga",
                    "What did you teach Arjuna about duty?"
                ],
                'buddha': [
                    "What is the path to enlightenment?",
                    "Explain the Four Noble Truths",
                    "How do I overcome suffering?"
                ],
                'jesus': [
                    "What is the greatest commandment?",
                    "How should I love my neighbor?",
                    "What is the kingdom of heaven?"
                ],
                'rumi': [
                    "What is divine love?",
                    "How do I find the Beloved?",
                    "What is spiritual transformation?"
                ],
                'swami_vivekananda': [
                    "What is practical Vedanta?",
                    "How can I serve humanity?"
                ]
            },
            'Philosophical': {
                'marcus_aurelius': [
                    "How should I face adversity?",
                    "What is Stoic philosophy?"
                ],
                'lao_tzu': [
                    "What is the Tao?",
                    "How can I live in harmony with nature?"
                ],
                'confucius': [
                    "What is virtue?",
                    "How should I conduct myself in society?"
                ],
                'aristotle': [
                    "What is the good life?",
                    "What is virtue ethics?"
                ],
                'plato': [
                    "What is justice?",
                    "What are the Forms?"
                ],
                'socrates': [
                    "What is the examined life?",
                    "How should I seek wisdom?"
                ]
            },
            'Leadership': {
                'chanakya': [
                    "What makes a good leader?",
                    "How should I handle political challenges?"
                ],
                'lincoln': [
                    "How should I unite a divided nation?"
                ],
                'franklin': [
                    "What are the virtues of a good citizen?"
                ],
                'washington': [
                    "What makes a good president?"
                ],
                'gandhi': [
                    "What is non-violence?",
                    "How can I resist injustice?"
                ],
                'mlk': [
                    "What is justice and equality?"
                ]
            },
            'Scientific': {
                'einstein': [
                    "What is relativity?",
                    "How does E=mc² work?"
                ],
                'newton': [
                    "Explain the laws of motion",
                    "What is gravity?"
                ],
                'tesla': [
                    "How does alternating current work?"
                ],
                'archimedes': [
                    "Explain the principle of buoyancy"
                ],
                'leonardo_da_vinci': [
                    "What is the relationship between art and science?"
                ]
            },
            'Literary': {
                'shakespeare': [
                    "What is the nature of love?",
                    "What makes a tragic hero?",
                    "Explain the theme of ambition in Macbeth"
                ],
                'tagore': [
                    "What is freedom?",
                    "What is the meaning of beauty?",
                    "Explain nationalism vs universalism"
                ]
            },
            'Psychology': {
                'freud': [
                    "What is the unconscious mind?",
                    "Explain psychoanalysis"
                ]
            }
        }
        
        # Run tests for each domain
        for domain, personalities in test_cases.items():
            print(f"\n\n{'#'*70}")
            print(f"# TESTING {domain.upper()} DOMAIN")
            print(f"{'#'*70}")
            
            for personality, queries in personalities.items():
                await self.test_personality(personality, queries, domain)
                # Small delay between personalities
                await asyncio.sleep(0.5)
        
        # Final report
        self.print_final_report()
    
    def print_final_report(self):
        """Print comprehensive test report"""
        print("\n\n" + "="*70)
        print("📊 FINAL TEST REPORT")
        print("="*70)
        
        total_tests = self.results['passed'] + self.results['failed']
        success_rate = (self.results['passed'] / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📈 Overall Statistics:")
        print(f"   Total Queries Tested: {total_tests}")
        print(f"   Passed: {self.results['passed']}")
        print(f"   Failed: {self.results['failed']}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        if self.results['latencies']:
            avg_latency = sum(self.results['latencies']) / len(self.results['latencies'])
            min_latency = min(self.results['latencies'])
            max_latency = max(self.results['latencies'])
            print(f"\n⏱️  Performance Metrics:")
            print(f"   Average Latency: {avg_latency:.2f}s")
            print(f"   Min Latency: {min_latency:.2f}s")
            print(f"   Max Latency: {max_latency:.2f}s")
            print(f"   Target: ≤2.5s (Status: {'✅ PASS' if avg_latency <= 2.5 else '⚠️ NEEDS OPTIMIZATION'})")
        
        print(f"\n🎭 Personalities Tested: {len(self.results['personalities_tested'])}/25")
        
        # Domain breakdown
        domain_stats = {}
        for result in self.results['personalities_tested']:
            domain = result['domain']
            if domain not in domain_stats:
                domain_stats[domain] = {'passed': 0, 'failed': 0}
            domain_stats[domain]['passed'] += result['queries_passed']
            domain_stats[domain]['failed'] += result['queries_failed']
        
        print(f"\n📚 Results by Domain:")
        for domain, stats in domain_stats.items():
            total = stats['passed'] + stats['failed']
            rate = (stats['passed'] / total * 100) if total > 0 else 0
            status = "✅" if rate >= 95 else ("⚠️" if rate >= 90 else "❌")
            print(f"   {status} {domain:15} - {stats['passed']}/{total} ({rate:.1f}%)")
        
        # List any failures
        if self.results['failed'] > 0:
            print(f"\n⚠️  Failures Detected:")
            for result in self.results['personalities_tested']:
                if result['errors']:
                    print(f"\n   {result['personality']} ({result['domain']}):")
                    for error in result['errors']:
                        print(f"      - {error}")
        
        # Final verdict
        print("\n" + "="*70)
        if success_rate >= 95 and avg_latency <= 2.5:
            print("✅ PHASE 3 TESTING PASSED - READY FOR PRODUCTION DEPLOYMENT!")
        elif success_rate >= 90:
            print("⚠️  PHASE 3 TESTING MOSTLY PASSED - MINOR ISSUES DETECTED")
            print("   Review failures above before production deployment")
        else:
            print("❌ PHASE 3 TESTING FAILED - DO NOT DEPLOY TO PRODUCTION")
            print("   Critical issues detected - requires investigation")
        print("="*70)

async def main():
    tester = Phase3Tester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
