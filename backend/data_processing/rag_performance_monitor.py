"""
RAG Performance Monitoring and Optimization
===========================================

This script monitors RAG performance in production and provides optimization recommendations.
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Any
import aiohttp

class RAGPerformanceMonitor:
    """Monitor RAG system performance in production"""
    
    def __init__(self):
        self.base_url = "https://vimarsh-backend-app-flex-accch9cmbah2bzb0.westus2-01.azurewebsites.net"
        self.test_queries = [
            {"personality_id": "krishna", "query": "What is dharma?"},
            {"personality_id": "einstein", "query": "What is time?"},
            {"personality_id": "buddha", "query": "What is suffering?"},
            {"personality_id": "chanakya", "query": "What makes a good leader?"},
            {"personality_id": "lincoln", "query": "How to preserve democracy?"},
            {"personality_id": "marcus_aurelius", "query": "What is virtue?"},
            {"personality_id": "newton", "query": "What are the laws of motion?"},
            {"personality_id": "tesla", "query": "What is electricity?"},
            {"personality_id": "jesus", "query": "What is love?"},
            {"personality_id": "rumi", "query": "What is divine love?"},
            {"personality_id": "lao_tzu", "query": "What is the Tao?"},
            {"personality_id": "confucius", "query": "What is wisdom?"}
        ]
    
    async def test_rag_performance(self) -> Dict[str, Any]:
        """Test RAG performance across all personalities"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "total_personalities": len(self.test_queries),
            "personality_results": {},
            "overall_metrics": {}
        }
        
        total_time = 0
        successful_queries = 0
        failed_queries = 0
        
        async with aiohttp.ClientSession() as session:
            for test_query in self.test_queries:
                personality = test_query["personality_id"]
                query = test_query["query"]
                
                try:
                    start_time = time.time()
                    
                    async with session.post(
                        f"{self.base_url}/api/spiritual_guidance",
                        json={
                            "query": query,
                            "personality_id": personality,
                            "safety_level": "moderate"
                        },
                        headers={"Content-Type": "application/json"}
                    ) as response:
                        
                        response_time = time.time() - start_time
                        
                        if response.status == 200:
                            response_data = await response.json()
                            response_text = response_data.get("response", "")
                            
                            results["personality_results"][personality] = {
                                "status": "success",
                                "response_time_seconds": round(response_time, 2),
                                "response_length": len(response_text),
                                "query": query,
                                "response_preview": response_text[:100] + "..." if len(response_text) > 100 else response_text
                            }
                            
                            total_time += response_time
                            successful_queries += 1
                            
                        else:
                            results["personality_results"][personality] = {
                                "status": "failed",
                                "error_code": response.status,
                                "response_time_seconds": round(response_time, 2),
                                "query": query
                            }
                            failed_queries += 1
                            
                except Exception as e:
                    results["personality_results"][personality] = {
                        "status": "error",
                        "error": str(e),
                        "query": query
                    }
                    failed_queries += 1
                
                # Brief pause between requests
                await asyncio.sleep(0.5)
        
        # Calculate overall metrics
        results["overall_metrics"] = {
            "successful_queries": successful_queries,
            "failed_queries": failed_queries,
            "success_rate_percentage": round((successful_queries / len(self.test_queries)) * 100, 1),
            "average_response_time_seconds": round(total_time / successful_queries, 2) if successful_queries > 0 else 0,
            "total_test_duration_seconds": round(sum(
                r.get("response_time_seconds", 0) for r in results["personality_results"].values()
            ), 2)
        }
        
        return results
    
    async def check_system_health(self) -> Dict[str, Any]:
        """Check overall system health"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/health") as response:
                    if response.status == 200:
                        health_data = await response.json()
                        return {
                            "status": "healthy",
                            "health_data": health_data,
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        return {
                            "status": "unhealthy",
                            "error_code": response.status,
                            "timestamp": datetime.now().isoformat()
                        }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def generate_performance_report(self, performance_results: Dict[str, Any], health_results: Dict[str, Any]) -> str:
        """Generate a comprehensive performance report"""
        
        report = f"""
# RAG Production Performance Report
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🎯 System Health
- **Status**: {health_results.get('status', 'unknown').upper()}
- **Personalities Available**: {health_results.get('health_data', {}).get('personalities_available', 'N/A')}
- **Backend Version**: {health_results.get('health_data', {}).get('version', 'N/A')}

## 📊 RAG Performance Metrics
- **Total Personalities Tested**: {performance_results['total_personalities']}
- **Success Rate**: {performance_results['overall_metrics']['success_rate_percentage']}%
- **Average Response Time**: {performance_results['overall_metrics']['average_response_time_seconds']}s
- **Successful Queries**: {performance_results['overall_metrics']['successful_queries']}
- **Failed Queries**: {performance_results['overall_metrics']['failed_queries']}

## 👥 Personality Performance
"""
        
        for personality, result in performance_results['personality_results'].items():
            status_emoji = "✅" if result['status'] == 'success' else "❌"
            report += f"**{personality.title()}**: {status_emoji} "
            
            if result['status'] == 'success':
                report += f"{result['response_time_seconds']}s - {result['response_length']} chars\n"
                report += f"   *Preview*: {result['response_preview']}\n\n"
            else:
                report += f"Failed - {result.get('error', result.get('error_code', 'Unknown error'))}\n\n"
        
        # Performance recommendations
        avg_time = performance_results['overall_metrics']['average_response_time_seconds']
        report += f"\n## 🚀 Performance Analysis\n"
        
        if avg_time < 2.0:
            report += "- **Excellent**: Response times under 2 seconds ✅\n"
        elif avg_time < 4.0:
            report += "- **Good**: Response times reasonable but could be optimized\n"
        else:
            report += "- **Attention Needed**: Response times over 4 seconds may impact UX\n"
        
        success_rate = performance_results['overall_metrics']['success_rate_percentage']
        if success_rate >= 95:
            report += "- **Reliability**: Excellent success rate ✅\n"
        elif success_rate >= 85:
            report += "- **Reliability**: Good success rate but monitor for issues\n"
        else:
            report += "- **Critical**: Success rate below 85% - needs immediate attention ⚠️\n"
        
        report += f"\n## 📈 Next Steps\n"
        report += f"1. **Monitor**: Continue tracking these metrics daily\n"
        report += f"2. **Optimize**: Focus on personalities with slower response times\n"
        report += f"3. **Scale**: Consider caching for frequently asked questions\n"
        report += f"4. **Enhance**: Add more comprehensive test queries\n"
        
        return report

async def main():
    """Run comprehensive RAG performance monitoring"""
    print("🚀 Starting RAG Production Performance Monitoring...")
    
    monitor = RAGPerformanceMonitor()
    
    # Check system health
    print("📊 Checking system health...")
    health_results = await monitor.check_system_health()
    print(f"System Status: {health_results['status'].upper()}")
    
    # Test RAG performance
    print("🧠 Testing RAG performance across all personalities...")
    performance_results = await monitor.test_rag_performance()
    
    # Generate report
    report = monitor.generate_performance_report(performance_results, health_results)
    
    # Save results
    with open("rag_performance_report.json", "w") as f:
        json.dump({
            "health": health_results,
            "performance": performance_results
        }, f, indent=2)
    
    with open("rag_performance_report.md", "w", encoding='utf-8') as f:
        f.write(report)
    
    print("\n" + "="*60)
    print(report)
    print("="*60)
    print(f"\n📝 Full results saved to:")
    print(f"   - rag_performance_report.json")
    print(f"   - rag_performance_report.md")

if __name__ == "__main__":
    asyncio.run(main())
