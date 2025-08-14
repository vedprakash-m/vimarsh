#!/usr/bin/env python3
"""
Post-Deployment Health Check and Smoke Tests
Validates deployed Vimarsh system functionality
"""

import asyncio
import aiohttp
import argparse
import json
import time
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class HealthCheckResult:
    """Health check result"""
    check_name: str
    status: str  # healthy, degraded, unhealthy
    response_time: float
    details: str
    error_message: Optional[str] = None

class PostDeploymentValidator:
    """Post-deployment health and smoke tests"""
    
    def __init__(self, environment: str = "production"):
        self.environment = environment
        self.results: List[HealthCheckResult] = []
        
        # Environment URLs
        self.config = {
            "production": {
                "frontend_url": "https://vimarsh.vedprakash.net",
                "backend_url": "https://vimarsh-backend-app-flex.azurewebsites.net"
            },
            "staging": {
                "frontend_url": "https://staging-vimarsh.vedprakash.net", 
                "backend_url": "https://staging-vimarsh-backend.azurewebsites.net"
            }
        }
    
    async def check_frontend_availability(self, session: aiohttp.ClientSession) -> HealthCheckResult:
        """Check frontend availability and basic functionality"""
        start_time = time.time()
        frontend_url = self.config[self.environment]["frontend_url"]
        
        try:
            async with session.get(frontend_url, timeout=30) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    content = await response.text()
                    
                    # Check for essential content
                    if "Vimarsh" in content and "<html" in content:
                        return HealthCheckResult(
                            check_name="frontend_availability",
                            status="healthy",
                            response_time=response_time,
                            details=f"Frontend accessible and contains expected content (status: {response.status})"
                        )
                    else:
                        return HealthCheckResult(
                            check_name="frontend_availability",
                            status="degraded",
                            response_time=response_time,
                            details="Frontend accessible but missing expected content"
                        )
                else:
                    return HealthCheckResult(
                        check_name="frontend_availability",
                        status="unhealthy",
                        response_time=response_time,
                        details=f"Frontend returned unexpected status: {response.status}"
                    )
                    
        except Exception as e:
            return HealthCheckResult(
                check_name="frontend_availability",
                status="unhealthy",
                response_time=time.time() - start_time,
                details="Frontend not accessible",
                error_message=str(e)
            )
    
    async def check_backend_health(self, session: aiohttp.ClientSession) -> HealthCheckResult:
        """Check backend health endpoint"""
        start_time = time.time()
        backend_url = self.config[self.environment]["backend_url"]
        
        try:
            async with session.get(f"{backend_url}/api/health", timeout=30) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("status") == "healthy":
                        return HealthCheckResult(
                            check_name="backend_health",
                            status="healthy",
                            response_time=response_time,
                            details=f"Backend health check passed (response time: {response_time:.2f}s)"
                        )
                    else:
                        return HealthCheckResult(
                            check_name="backend_health",
                            status="degraded",
                            response_time=response_time,
                            details=f"Backend health check returned: {data.get('status', 'unknown')}"
                        )
                else:
                    return HealthCheckResult(
                        check_name="backend_health",
                        status="unhealthy",
                        response_time=response_time,
                        details=f"Backend health endpoint returned status: {response.status}"
                    )
                    
        except Exception as e:
            return HealthCheckResult(
                check_name="backend_health",
                status="unhealthy",
                response_time=time.time() - start_time,
                details="Backend health endpoint not accessible",
                error_message=str(e)
            )
    
    async def check_spiritual_guidance_api(self, session: aiohttp.ClientSession) -> HealthCheckResult:
        """Test core spiritual guidance functionality"""
        start_time = time.time()
        backend_url = self.config[self.environment]["backend_url"]
        
        test_payload = {
            "query": "What is dharma in Hindu philosophy?",
            "language": "English"
        }
        
        try:
            async with session.post(
                f"{backend_url}/api/spiritual_guidance",
                json=test_payload,
                timeout=60
            ) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("response") and len(data["response"]) > 100:
                        # Check for spiritual content
                        response_text = data["response"].lower()
                        spiritual_indicators = ["dharma", "spiritual", "duty", "righteousness", "hindu"]
                        
                        if any(indicator in response_text for indicator in spiritual_indicators):
                            return HealthCheckResult(
                                check_name="spiritual_guidance_api",
                                status="healthy",
                                response_time=response_time,
                                details=f"Spiritual guidance API working correctly (response time: {response_time:.2f}s)"
                            )
                        else:
                            return HealthCheckResult(
                                check_name="spiritual_guidance_api",
                                status="degraded",
                                response_time=response_time,
                                details="API responding but content quality may be degraded"
                            )
                    else:
                        return HealthCheckResult(
                            check_name="spiritual_guidance_api",
                            status="degraded",
                            response_time=response_time,
                            details="API responding but returned incomplete response"
                        )
                else:
                    return HealthCheckResult(
                        check_name="spiritual_guidance_api",
                        status="unhealthy",
                        response_time=response_time,
                        details=f"Spiritual guidance API returned status: {response.status}"
                    )
                    
        except Exception as e:
            return HealthCheckResult(
                check_name="spiritual_guidance_api",
                status="unhealthy",
                response_time=time.time() - start_time,
                details="Spiritual guidance API not accessible",
                error_message=str(e)
            )
    
    async def check_performance_baseline(self, session: aiohttp.ClientSession) -> HealthCheckResult:
        """Check performance baselines"""
        start_time = time.time()
        backend_url = self.config[self.environment]["backend_url"]
        
        # Test multiple requests to get average response time
        response_times = []
        successful_requests = 0
        
        for i in range(3):
            try:
                request_start = time.time()
                async with session.get(f"{backend_url}/api/health", timeout=15) as response:
                    request_time = time.time() - request_start
                    response_times.append(request_time)
                    
                    if response.status == 200:
                        successful_requests += 1
                        
                # Small delay between requests
                await asyncio.sleep(0.5)
                
            except Exception:
                pass
        
        total_time = time.time() - start_time
        
        if successful_requests >= 2:
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            
            if avg_response_time <= 2.0 and max_response_time <= 5.0:
                return HealthCheckResult(
                    check_name="performance_baseline",
                    status="healthy",
                    response_time=total_time,
                    details=f"Performance baseline met (avg: {avg_response_time:.2f}s, max: {max_response_time:.2f}s)"
                )
            elif avg_response_time <= 5.0:
                return HealthCheckResult(
                    check_name="performance_baseline",
                    status="degraded",
                    response_time=total_time,
                    details=f"Performance slightly degraded (avg: {avg_response_time:.2f}s, max: {max_response_time:.2f}s)"
                )
            else:
                return HealthCheckResult(
                    check_name="performance_baseline",
                    status="unhealthy",
                    response_time=total_time,
                    details=f"Performance below baseline (avg: {avg_response_time:.2f}s, max: {max_response_time:.2f}s)"
                )
        else:
            return HealthCheckResult(
                check_name="performance_baseline",
                status="unhealthy",
                response_time=total_time,
                details=f"Performance test failed, only {successful_requests}/3 requests successful"
            )
    
    async def check_https_security(self, session: aiohttp.ClientSession) -> HealthCheckResult:
        """Check HTTPS security configuration"""
        start_time = time.time()
        frontend_url = self.config[self.environment]["frontend_url"]
        
        try:
            # Test HTTP to HTTPS redirect
            http_url = frontend_url.replace("https://", "http://")
            
            async with session.get(http_url, allow_redirects=False, timeout=15) as response:
                response_time = time.time() - start_time
                
                if response.status in [301, 302, 308]:
                    location = response.headers.get('Location', '')
                    if location.startswith('https://'):
                        return HealthCheckResult(
                            check_name="https_security",
                            status="healthy",
                            response_time=response_time,
                            details="HTTPS redirect working correctly"
                        )
                    else:
                        return HealthCheckResult(
                            check_name="https_security",
                            status="degraded",
                            response_time=response_time,
                            details="Redirect present but not to HTTPS"
                        )
                else:
                    return HealthCheckResult(
                        check_name="https_security",
                        status="unhealthy",
                        response_time=response_time,
                        details=f"No HTTPS redirect found (status: {response.status})"
                    )
                    
        except Exception as e:
            return HealthCheckResult(
                check_name="https_security",
                status="unhealthy",
                response_time=time.time() - start_time,
                details="HTTPS security check failed",
                error_message=str(e)
            )
    
    async def run_comprehensive_health_check(self) -> Dict:
        """Run comprehensive post-deployment health check"""
        print(f"🏥 Running Post-Deployment Health Check for {self.environment.upper()}")
        print("=" * 60)
        
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=120),
            connector=aiohttp.TCPConnector(limit=10)
        ) as session:
            
            # Run all health checks
            self.results.append(await self.check_frontend_availability(session))
            self.results.append(await self.check_backend_health(session))
            self.results.append(await self.check_spiritual_guidance_api(session))
            self.results.append(await self.check_performance_baseline(session))
            self.results.append(await self.check_https_security(session))
        
        return self.generate_health_report()
    
    def generate_health_report(self) -> Dict:
        """Generate comprehensive health report"""
        healthy_checks = len([r for r in self.results if r.status == "healthy"])
        degraded_checks = len([r for r in self.results if r.status == "degraded"])
        unhealthy_checks = len([r for r in self.results if r.status == "unhealthy"])
        
        total_checks = len(self.results)
        health_score = (healthy_checks * 100 + degraded_checks * 50) / total_checks if total_checks > 0 else 0
        
        # Determine overall system status
        if unhealthy_checks == 0 and health_score >= 90:
            overall_status = "HEALTHY"
            recommendation = "System is fully operational"
        elif unhealthy_checks <= 1 and health_score >= 70:
            overall_status = "DEGRADED"
            recommendation = "System operational with some performance issues"
        else:
            overall_status = "UNHEALTHY"
            recommendation = "System has critical issues requiring immediate attention"
        
        return {
            "environment": self.environment,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "overall_status": overall_status,
            "health_score": round(health_score, 1),
            "recommendation": recommendation,
            "summary": {
                "total_checks": total_checks,
                "healthy": healthy_checks,
                "degraded": degraded_checks,
                "unhealthy": unhealthy_checks
            },
            "detailed_results": [
                {
                    "check_name": r.check_name,
                    "status": r.status,
                    "response_time": round(r.response_time, 3),
                    "details": r.details,
                    "error_message": r.error_message
                }
                for r in self.results
            ]
        }
    
    def print_health_report(self, report: Dict):
        """Print formatted health report"""
        status_icons = {
            "HEALTHY": "🟢",
            "DEGRADED": "🟡", 
            "UNHEALTHY": "🔴"
        }
        
        print(f"\n{status_icons.get(report['overall_status'], '⚪')} SYSTEM STATUS: {report['overall_status']}")
        print(f"📊 Health Score: {report['health_score']}%")
        print(f"💡 Recommendation: {report['recommendation']}")
        print(f"🕐 Checked at: {report['timestamp']}")
        
        print(f"\n📋 Check Summary:")
        print(f"   🟢 Healthy: {report['summary']['healthy']}")
        print(f"   🟡 Degraded: {report['summary']['degraded']}")
        print(f"   🔴 Unhealthy: {report['summary']['unhealthy']}")
        
        print(f"\n🔍 Detailed Results:")
        for result in report["detailed_results"]:
            status_icon = {"healthy": "🟢", "degraded": "🟡", "unhealthy": "🔴"}.get(result["status"], "⚪")
            print(f"   {status_icon} {result['check_name']}: {result['details']} ({result['response_time']}s)")
            if result["error_message"]:
                print(f"      Error: {result['error_message']}")
        
        print("\n" + "=" * 60)
        
        if report["overall_status"] == "HEALTHY":
            print("✅ All systems operational - deployment successful!")
        elif report["overall_status"] == "DEGRADED":
            print("⚠️  System operational but monitoring recommended")
        else:
            print("🚨 Critical issues detected - immediate action required")

async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Post-Deployment Health Check")
    parser.add_argument("--environment", choices=["production", "staging"], 
                       default="production", help="Environment to check")
    parser.add_argument("--output", help="Save report to JSON file")
    parser.add_argument("--ci", action="store_true", help="CI mode - minimal output")
    
    args = parser.parse_args()
    
    try:
        validator = PostDeploymentValidator(args.environment)
        report = await validator.run_comprehensive_health_check()
        
        if args.ci:
            # CI mode output
            print(f"HEALTH_STATUS={report['overall_status']}")
            print(f"HEALTH_SCORE={report['health_score']}")
            print(f"UNHEALTHY_CHECKS={report['summary']['unhealthy']}")
        else:
            # Interactive mode
            validator.print_health_report(report)
        
        # Save JSON report if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\n📄 Health report saved to {args.output}")
        
        # Exit with appropriate code
        if report["overall_status"] == "HEALTHY":
            exit(0)
        elif report["overall_status"] == "DEGRADED":
            exit(1)
        else:
            exit(2)
            
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        exit(3)

if __name__ == "__main__":
    asyncio.run(main())
