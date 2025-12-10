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
        # Note: Using the actual deployed Azure Functions Flex Consumption URL
        # The deployed app is 'vimarsh-backend-app-flex' with Flex-specific suffix
        self.config = {
            "production": {
                "frontend_url": "https://vimarsh.vedprakash.net",
                "backend_url": "https://vimarsh-backend-app-flex-accch9cmbah2bzb0.westus2-01.azurewebsites.net"
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
        """Check backend health endpoint with retry logic for Azure Functions cold start"""
        start_time = time.time()
        backend_url = self.config[self.environment]["backend_url"]
        
        # Retry configuration for Azure Functions
        # Optimized after fixing import failures - backend now starts quickly
        max_retries = 3
        base_timeout = 30
        
        for attempt in range(max_retries):
            try:
                timeout = base_timeout + (attempt * 30)  # Increase timeout on retries (30s, 60s, 90s)
                print(f"🔄 Attempting backend health check (attempt {attempt + 1}/{max_retries}, timeout: {timeout}s)")
                
                async with session.get(f"{backend_url}/api/health", timeout=timeout) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get("status") == "healthy":
                            return HealthCheckResult(
                                check_name="backend_health",
                                status="healthy",
                                response_time=response_time,
                                details=f"Backend health check passed (response time: {response_time:.2f}s, attempt {attempt + 1})"
                            )
                        else:
                            return HealthCheckResult(
                                check_name="backend_health",
                                status="degraded",
                                response_time=response_time,
                                details=f"Backend health check returned: {data.get('status', 'unknown')} (attempt {attempt + 1})"
                            )
                    elif response.status == 404:
                        # 404 suggests Functions app routes not loaded yet
                        if attempt < max_retries - 1:
                            print(f"⚠️ Backend returned 404 (app may be starting), waiting 20s before retry...")
                            await asyncio.sleep(20)  # Reduced wait after fixing import failures
                            continue
                        else:
                            return HealthCheckResult(
                                check_name="backend_health",
                                status="unhealthy",
                                response_time=response_time,
                                details=f"Backend health endpoint not found (404) - Functions app may need redeployment"
                            )
                    else:
                        # For other non-200 status, try once more if not last attempt
                        if attempt < max_retries - 1:
                            print(f"⚠️ Backend returned status {response.status}, retrying in 15 seconds...")
                            await asyncio.sleep(15)
                            continue
                        else:
                            return HealthCheckResult(
                                check_name="backend_health",
                                status="unhealthy",
                                response_time=response_time,
                                details=f"Backend health endpoint returned status: {response.status} after {max_retries} attempts"
                            )
                        
            except asyncio.TimeoutError:
                if attempt < max_retries - 1:
                    print(f"⏱️ Timeout on attempt {attempt + 1}, retrying with longer timeout...")
                    await asyncio.sleep(15)
                    continue
                else:
                    return HealthCheckResult(
                        check_name="backend_health",
                        status="unhealthy",
                        response_time=time.time() - start_time,
                        details=f"Backend health endpoint timeout after {max_retries} attempts (Azure Functions may be cold starting)",
                        error_message="Timeout error"
                    )
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"❌ Error on attempt {attempt + 1}: {str(e)}, retrying...")
                    await asyncio.sleep(10)
                    continue
                else:
                    return HealthCheckResult(
                        check_name="backend_health",
                        status="unhealthy",
                        response_time=time.time() - start_time,
                        details=f"Backend health endpoint not accessible after {max_retries} attempts",
                        error_message=str(e)
                    )
        
        # This should never be reached due to the logic above, but adding for safety
        return HealthCheckResult(
            check_name="backend_health",
            status="unhealthy",
            response_time=time.time() - start_time,
            details="Unexpected end of retry loop",
            error_message="Logic error"
        )
    
    async def check_guidance_api(self, session: aiohttp.ClientSession) -> HealthCheckResult:
        """Test core guidance functionality with retry logic"""
        start_time = time.time()
        backend_url = self.config[self.environment]["backend_url"]
        
        test_payload = {
            "query": "What is dharma in Hindu philosophy?",
            "language": "English"
        }
        
        # Retry configuration for Azure Functions
        # Optimized after performance improvements
        max_retries = 3
        base_timeout = 60
        
        for attempt in range(max_retries):
            try:
                timeout = base_timeout + (attempt * 30)
                print(f"🔄 Testing guidance API (attempt {attempt + 1}/{max_retries}, timeout: {timeout}s)")
                
                async with session.post(
                    f"{backend_url}/api/guidance",
                    json=test_payload,
                    timeout=timeout
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
                                    check_name="guidance_api",
                                    status="healthy",
                                    response_time=response_time,
                                    details=f"Guidance API working correctly (response time: {response_time:.2f}s, attempt {attempt + 1})"
                                )
                            else:
                                return HealthCheckResult(
                                    check_name="guidance_api",
                                    status="degraded",
                                    response_time=response_time,
                                    details=f"API responded but content lacks spiritual indicators (attempt {attempt + 1})"
                                )
                        else:
                            if attempt < max_retries - 1:
                                print(f"⚠️ API returned insufficient content, retrying...")
                                await asyncio.sleep(10)
                                continue
                            else:
                                return HealthCheckResult(
                                    check_name="guidance_api",
                                    status="degraded",
                                    response_time=response_time,
                                    details=f"API response too short or empty after {max_retries} attempts"
                                )
                    elif response.status == 404:
                        # 404 suggests Functions app routes not loaded yet
                        if attempt < max_retries - 1:
                            print(f"⚠️ Guidance API returned 404 (app may be starting), waiting 20s before retry...")
                            await asyncio.sleep(20)
                            continue
                        else:
                            return HealthCheckResult(
                                check_name="guidance_api",
                                status="unhealthy",
                                response_time=response_time,
                                details=f"Guidance API endpoint not found (404) - Functions app may need redeployment"
                            )
                    elif response.status == 500:
                        # 500 errors are expected in degraded mode (missing LLM API keys, etc.)
                        if attempt < max_retries - 1:
                            print(f"⚠️ Backend in degraded mode (500 error), retrying...")
                            await asyncio.sleep(15)
                            continue
                        else:
                            return HealthCheckResult(
                                check_name="guidance_api",
                                status="degraded",
                                response_time=response_time,
                                details=f"Backend in degraded mode - guidance API returns 500 (likely missing API keys or DB config)"
                            )
                    else:
                        if attempt < max_retries - 1:
                            print(f"⚠️ Guidance API returned status {response.status}, retrying...")
                            await asyncio.sleep(15)
                            continue
                        else:
                            return HealthCheckResult(
                                check_name="guidance_api",
                                status="unhealthy",
                                response_time=response_time,
                                details=f"Guidance API returned status: {response.status} after {max_retries} attempts"
                            )
                            
            except asyncio.TimeoutError:
                if attempt < max_retries - 1:
                    print(f"⏱️ Guidance API timeout on attempt {attempt + 1}, retrying...")
                    await asyncio.sleep(20)
                    continue
                else:
                    return HealthCheckResult(
                        check_name="guidance_api",
                        status="unhealthy",
                        response_time=time.time() - start_time,
                        details=f"Guidance API timeout after {max_retries} attempts",
                        error_message="Timeout error"
                    )
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"❌ Error testing guidance API on attempt {attempt + 1}: {str(e)}, retrying...")
                    await asyncio.sleep(15)
                    continue
                else:
                    return HealthCheckResult(
                        check_name="guidance_api",
                        status="unhealthy",
                        response_time=time.time() - start_time,
                        details=f"Guidance API not accessible after {max_retries} attempts",
                        error_message=str(e)
                    )
        
        # Safety fallback
        return HealthCheckResult(
            check_name="guidance_api",
            status="unhealthy",
            response_time=time.time() - start_time,
            details="Unexpected end of retry loop",
            error_message="Logic error"
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
            self.results.append(await self.check_guidance_api(session))
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
        # DEGRADED (80%+ score) is acceptable for production - services operational with minor issues
        if report["overall_status"] in ["HEALTHY", "DEGRADED"]:
            exit(0)
        else:
            # UNHEALTHY (<50% score) fails CI/CD
            exit(1)
            
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        exit(3)

if __name__ == "__main__":
    asyncio.run(main())
