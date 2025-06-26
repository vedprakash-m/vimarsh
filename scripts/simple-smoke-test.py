#!/usr/bin/env python3
"""
Vimarsh Production Deployment Smoke Test Runner (Simplified)
Basic smoke testing without external dependencies beyond requests
"""

import json
import time
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import argparse
import sys
import os

@dataclass
class TestResult:
    name: str
    category: str
    status: str  # PASS, FAIL, SKIP
    response_time: float
    error_message: Optional[str] = None
    response_data: Optional[Dict] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class SimpleSmokeTestRunner:
    def __init__(self, environment: str, verbose: bool = False):
        self.environment = environment
        self.verbose = verbose
        self.results: List[TestResult] = []
        
        # Set environment-specific URLs
        if environment == "staging":
            self.function_url = "https://vimarsh-staging-functions.azurewebsites.net"
            self.web_url = "https://vimarsh-staging-web.azurestaticapps.net"
        elif environment == "prod":
            self.function_url = "https://vimarsh-functions.azurewebsites.net"
            self.web_url = "https://vimarsh-web.azurestaticapps.net"
        else:
            raise ValueError(f"Unknown environment: {environment}")
        
        # Initialize session
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Vimarsh-SmokeTest/1.0',
            'Accept': 'application/json'
        })
    
    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        color_codes = {
            "INFO": "\033[0;34m",  # Blue
            "SUCCESS": "\033[0;32m",  # Green
            "ERROR": "\033[0;31m",  # Red
            "WARNING": "\033[1;33m",  # Yellow
        }
        reset = "\033[0m"
        
        if self.verbose or level != "DEBUG":
            color = color_codes.get(level, "")
            print(f"{timestamp} [{color}{level}{reset}] {message}")
    
    def make_request(self, name: str, category: str, method: str, url: str, 
                    expected_status: int = 200, payload: dict = None,
                    timeout: int = 30) -> TestResult:
        """Execute a single HTTP test"""
        start_time = time.time()
        
        try:
            self.log(f"Testing: {name} ({method} {url})", "DEBUG")
            
            # Prepare request
            kwargs = {'timeout': timeout}
            if payload and method.upper() in ['POST', 'PUT', 'PATCH']:
                kwargs['json'] = payload
                kwargs['headers'] = {'Content-Type': 'application/json'}
            
            # Make request
            response = self.session.request(method.upper(), url, **kwargs)
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            # Check status code
            if response.status_code != expected_status:
                return TestResult(
                    name=name,
                    category=category,
                    status="FAIL",
                    response_time=response_time,
                    error_message=f"Expected status {expected_status}, got {response.status_code}"
                )
            
            # Parse response
            response_data = None
            if response.content:
                try:
                    response_data = response.json()
                except json.JSONDecodeError:
                    response_data = {"content": response.text[:200]}  # Truncate
            
            # Success
            self.log(f"✓ {name} ({response_time:.0f}ms)", "SUCCESS")
            return TestResult(
                name=name,
                category=category,
                status="PASS",
                response_time=response_time,
                response_data=response_data
            )
            
        except requests.exceptions.Timeout:
            response_time = (time.time() - start_time) * 1000
            return TestResult(
                name=name,
                category=category,
                status="FAIL",
                response_time=response_time,
                error_message="Request timeout"
            )
        except requests.exceptions.RequestException as e:
            response_time = (time.time() - start_time) * 1000
            return TestResult(
                name=name,
                category=category,
                status="FAIL",
                response_time=response_time,
                error_message=f"Request error: {str(e)}"
            )
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return TestResult(
                name=name,
                category=category,
                status="FAIL",
                response_time=response_time,
                error_message=f"Unexpected error: {str(e)}"
            )
    
    def run_health_checks(self) -> List[TestResult]:
        """Run basic health check tests"""
        self.log("Running health check tests...", "INFO")
        results = []
        
        # Azure Functions health
        result = self.make_request(
            "Azure Functions Health",
            "health_checks",
            "GET",
            f"{self.function_url}/api/health"
        )
        results.append(result)
        
        # Static Web App availability
        result = self.make_request(
            "Static Web App Availability",
            "health_checks", 
            "GET",
            self.web_url
        )
        results.append(result)
        
        return results
    
    def run_infrastructure_tests(self) -> List[TestResult]:
        """Run infrastructure connectivity tests"""
        self.log("Running infrastructure tests...", "INFO")
        results = []
        
        # Cosmos DB connectivity
        result = self.make_request(
            "Cosmos DB Connectivity",
            "infrastructure",
            "GET",
            f"{self.function_url}/api/test/cosmos"
        )
        results.append(result)
        
        # Key Vault connectivity
        result = self.make_request(
            "Key Vault Connectivity",
            "infrastructure",
            "GET",
            f"{self.function_url}/api/test/keyvault"
        )
        results.append(result)
        
        # Application Insights
        result = self.make_request(
            "Application Insights Integration",
            "infrastructure",
            "GET",
            f"{self.function_url}/api/test/insights"
        )
        results.append(result)
        
        return results
    
    def run_functional_tests(self) -> List[TestResult]:
        """Run functional smoke tests"""
        self.log("Running functional tests...", "INFO")
        results = []
        
        # Spiritual guidance API test
        result = self.make_request(
            "Spiritual Guidance API",
            "functional",
            "POST",
            f"{self.function_url}/api/spiritual-guidance",
            payload={"query": "What is dharma?", "language": "en"}
        )
        results.append(result)
        
        # Voice capabilities
        result = self.make_request(
            "Voice Interface Capabilities",
            "functional",
            "GET",
            f"{self.function_url}/api/voice/capabilities"
        )
        results.append(result)
        
        # Authentication config
        result = self.make_request(
            "Authentication Configuration",
            "functional",
            "GET",
            f"{self.function_url}/api/auth/config"
        )
        results.append(result)
        
        return results
    
    def run_performance_tests(self) -> List[TestResult]:
        """Run basic performance tests"""
        self.log("Running performance tests...", "INFO")
        results = []
        
        # Response time test
        start_time = time.time()
        result = self.make_request(
            "Response Time Performance",
            "performance",
            "POST",
            f"{self.function_url}/api/spiritual-guidance",
            payload={"query": "What is the meaning of life?", "language": "en"},
            timeout=30
        )
        
        # Check if response time is acceptable (< 5 seconds)
        if result.status == "PASS" and result.response_time > 5000:
            result.status = "FAIL"
            result.error_message = f"Response time {result.response_time:.0f}ms exceeds 5000ms limit"
        
        results.append(result)
        
        return results
    
    def run_security_tests(self) -> List[TestResult]:
        """Run basic security tests"""
        self.log("Running security tests...", "INFO")
        results = []
        
        # HTTPS enforcement test
        http_url = self.function_url.replace('https://', 'http://')
        if http_url != self.function_url:
            try:
                response = self.session.get(f"{http_url}/api/health", allow_redirects=False, timeout=10)
                if response.status_code in [301, 302, 307, 308]:
                    location = response.headers.get('location', '')
                    if location.startswith('https://'):
                        result = TestResult(
                            name="HTTPS Enforcement",
                            category="security",
                            status="PASS",
                            response_time=0,
                            response_data={"redirect_location": location}
                        )
                    else:
                        result = TestResult(
                            name="HTTPS Enforcement",
                            category="security",
                            status="FAIL",
                            response_time=0,
                            error_message="HTTP not redirected to HTTPS"
                        )
                else:
                    result = TestResult(
                        name="HTTPS Enforcement",
                        category="security",
                        status="FAIL",
                        response_time=0,
                        error_message=f"No redirect from HTTP (status: {response.status_code})"
                    )
            except Exception as e:
                result = TestResult(
                    name="HTTPS Enforcement",
                    category="security",
                    status="FAIL",
                    response_time=0,
                    error_message=f"HTTPS test error: {str(e)}"
                )
        else:
            result = TestResult(
                name="HTTPS Enforcement",
                category="security",
                status="PASS",
                response_time=0,
                response_data={"note": "URL already HTTP, assuming redirect configured"}
            )
        
        results.append(result)
        
        # CORS headers test
        try:
            response = self.session.options(f"{self.function_url}/api/health", timeout=10)
            cors_headers = [h.lower() for h in response.headers.keys() if 'access-control' in h.lower()]
            
            if len(cors_headers) > 0:
                result = TestResult(
                    name="CORS Headers",
                    category="security",
                    status="PASS",
                    response_time=0,
                    response_data={"cors_headers": cors_headers}
                )
            else:
                result = TestResult(
                    name="CORS Headers",
                    category="security",
                    status="FAIL",
                    response_time=0,
                    error_message="No CORS headers found"
                )
        except Exception as e:
            result = TestResult(
                name="CORS Headers",
                category="security",
                status="FAIL",
                response_time=0,
                error_message=f"CORS test error: {str(e)}"
            )
        
        results.append(result)
        
        return results
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all test suites"""
        self.log(f"Starting smoke tests for environment: {self.environment}", "INFO")
        self.log(f"Function URL: {self.function_url}", "INFO")
        self.log(f"Web URL: {self.web_url}", "INFO")
        
        start_time = time.time()
        all_results = []
        
        # Run all test suites
        all_results.extend(self.run_health_checks())
        all_results.extend(self.run_infrastructure_tests())
        all_results.extend(self.run_functional_tests())
        all_results.extend(self.run_performance_tests())
        all_results.extend(self.run_security_tests())
        
        total_time = time.time() - start_time
        
        # Generate summary
        total_tests = len(all_results)
        passed_tests = sum(1 for r in all_results if r.status == "PASS")
        failed_tests = sum(1 for r in all_results if r.status == "FAIL")
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        summary = {
            "environment": self.environment,
            "timestamp": datetime.now().isoformat(),
            "execution_time": total_time,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "test_results": [asdict(result) for result in all_results]
        }
        
        # Log summary
        self.log(f"\n=== Test Summary ===", "INFO")
        self.log(f"Total Tests: {total_tests}", "INFO")
        self.log(f"Passed: {passed_tests}", "SUCCESS")
        self.log(f"Failed: {failed_tests}", "ERROR" if failed_tests > 0 else "INFO")
        self.log(f"Success Rate: {success_rate:.1f}%", "SUCCESS" if success_rate >= 90 else "WARNING")
        self.log(f"Execution Time: {total_time:.1f}s", "INFO")
        
        if failed_tests > 0:
            self.log(f"\nFailed Tests:", "ERROR")
            for result in all_results:
                if result.status == "FAIL":
                    self.log(f"  - {result.name}: {result.error_message}", "ERROR")
        
        return summary
    
    def generate_report(self, summary: Dict[str, Any], output_file: str = None):
        """Generate a simple JSON report"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            output_file = f"smoke-test-{self.environment}-{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        self.log(f"Report generated: {output_file}", "SUCCESS")
        return output_file

def main():
    parser = argparse.ArgumentParser(description="Vimarsh Simple Smoke Tests")
    parser.add_argument("--environment", "-e", required=True, choices=["staging", "prod"], 
                       help="Target environment")
    parser.add_argument("--output", "-o", help="Output file for JSON report")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose output")
    parser.add_argument("--no-report", action="store_true",
                       help="Skip report generation")
    
    args = parser.parse_args()
    
    try:
        # Initialize test runner
        runner = SimpleSmokeTestRunner(args.environment, args.verbose)
        
        # Run tests
        summary = runner.run_all_tests()
        
        # Generate report
        if not args.no_report:
            runner.generate_report(summary, args.output)
        
        # Exit with appropriate code
        if summary['failed_tests'] > 0:
            print(f"\n❌ Some tests failed! Success rate: {summary['success_rate']:.1f}%")
            sys.exit(1)
        else:
            print(f"\n✅ All tests passed! Success rate: {summary['success_rate']:.1f}%")
            sys.exit(0)
            
    except Exception as e:
        print(f"❌ Test execution failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
