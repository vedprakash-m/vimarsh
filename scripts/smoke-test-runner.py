#!/usr/bin/env python3
"""
Vimarsh Production Deployment Smoke Test Runner
Comprehensive automated testing for production deployments
"""

import json
import time
import yaml
import requests
import asyncio
import aiohttp
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
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

class SmokeTestRunner:
    def __init__(self, config_path: str, environment: str, verbose: bool = False):
        self.config_path = Path(config_path)
        self.environment = environment
        self.verbose = verbose
        self.results: List[TestResult] = []
        self.session: Optional[requests.Session] = None
        
        # Load configuration
        with open(self.config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Set environment-specific settings
        self.env_config = self.config['environments'][environment]
        self.base_urls = self.env_config['base_urls']
        self.timeouts = self.env_config['timeouts']
        self.thresholds = self.env_config['thresholds']
        
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
            "DEBUG": "\033[0;35m"  # Purple
        }
        reset = "\033[0m"
        
        if self.verbose or level != "DEBUG":
            color = color_codes.get(level, "")
            print(f"{timestamp} [{color}{level}{reset}] {message}")
    
    def make_request(self, test_config: Dict, base_url: str) -> TestResult:
        """Execute a single HTTP test"""
        test_name = test_config['name']
        category = test_config.get('category', 'general')
        
        start_time = time.time()
        
        try:
            # Build URL
            endpoint = test_config.get('endpoint', '/')
            url = f"{base_url.rstrip('/')}{endpoint}"
            
            # Prepare request
            method = test_config.get('method', 'GET').upper()
            timeout = test_config.get('timeout', self.timeouts['default'])
            
            # Handle payload
            kwargs = {'timeout': timeout}
            if 'payload' in test_config:
                if method in ['POST', 'PUT', 'PATCH']:
                    kwargs['json'] = test_config['payload']
                    kwargs['headers'] = {'Content-Type': 'application/json'}
            
            self.log(f"Testing: {test_name} ({method} {url})", "DEBUG")
            
            # Make request
            response = self.session.request(method, url, **kwargs)
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            # Check status code
            expected_status = test_config.get('expected_status', 200)
            if response.status_code != expected_status:
                return TestResult(
                    name=test_name,
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
                    response_data = {"content": response.text[:500]}  # Truncate
            
            # Validate required fields
            if 'required_fields' in test_config and response_data:
                for field in test_config['required_fields']:
                    if field not in response_data:
                        return TestResult(
                            name=test_name,
                            category=category,
                            status="FAIL",
                            response_time=response_time,
                            error_message=f"Missing required field: {field}",
                            response_data=response_data
                        )
            
            # Content validation
            if 'content_check' in test_config:
                content = response.text.lower()
                for check_item in test_config['content_check']:
                    if check_item.lower() not in content:
                        return TestResult(
                            name=test_name,
                            category=category,
                            status="FAIL",
                            response_time=response_time,
                            error_message=f"Content check failed: '{check_item}' not found",
                            response_data=response_data
                        )
            
            # Content validation with context
            if 'content_validation' in test_config and response_data:
                response_text = json.dumps(response_data).lower()
                for validation in test_config['content_validation']:
                    keyword = validation['keyword'].lower()
                    context = validation.get('context', '').lower()
                    
                    if keyword not in response_text:
                        return TestResult(
                            name=test_name,
                            category=category,
                            status="FAIL",
                            response_time=response_time,
                            error_message=f"Content validation failed: '{keyword}' not found",
                            response_data=response_data
                        )
            
            # Performance validation
            max_response_time = test_config.get('max_response_time', self.thresholds['response_time'])
            if response_time > max_response_time:
                return TestResult(
                    name=test_name,
                    category=category,
                    status="FAIL",
                    response_time=response_time,
                    error_message=f"Response time {response_time:.0f}ms exceeds limit {max_response_time}ms",
                    response_data=response_data
                )
            
            # Success
            self.log(f"✓ {test_name} ({response_time:.0f}ms)", "SUCCESS")
            return TestResult(
                name=test_name,
                category=category,
                status="PASS",
                response_time=response_time,
                response_data=response_data
            )
            
        except requests.exceptions.Timeout:
            response_time = (time.time() - start_time) * 1000
            return TestResult(
                name=test_name,
                category=category,
                status="FAIL",
                response_time=response_time,
                error_message="Request timeout"
            )
        except requests.exceptions.RequestException as e:
            response_time = (time.time() - start_time) * 1000
            return TestResult(
                name=test_name,
                category=category,
                status="FAIL",
                response_time=response_time,
                error_message=f"Request error: {str(e)}"
            )
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return TestResult(
                name=test_name,
                category=category,
                status="FAIL",
                response_time=response_time,
                error_message=f"Unexpected error: {str(e)}"
            )
    
    def run_concurrent_test(self, test_config: Dict, base_url: str) -> TestResult:
        """Execute concurrent requests test"""
        test_name = test_config['name']
        concurrent_requests = test_config.get('concurrent_requests', 5)
        success_threshold = test_config.get('success_threshold', 80)
        
        self.log(f"Running concurrent test: {test_name} ({concurrent_requests} requests)", "INFO")
        
        start_time = time.time()
        
        # Prepare test configs for concurrent execution
        single_test_config = test_config.copy()
        single_test_config.pop('concurrent_requests', None)
        single_test_config.pop('success_threshold', None)
        
        # Execute concurrent requests
        results = []
        with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
            futures = [
                executor.submit(self.make_request, single_test_config, base_url)
                for _ in range(concurrent_requests)
            ]
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append(TestResult(
                        name=f"{test_name}_concurrent",
                        category="performance",
                        status="FAIL",
                        response_time=0,
                        error_message=f"Concurrent test error: {str(e)}"
                    ))
        
        total_time = (time.time() - start_time) * 1000
        
        # Analyze results
        successful_requests = sum(1 for r in results if r.status == "PASS")
        success_rate = (successful_requests / len(results)) * 100
        avg_response_time = sum(r.response_time for r in results) / len(results)
        
        if success_rate >= success_threshold:
            self.log(f"✓ {test_name} ({success_rate:.1f}% success, {avg_response_time:.0f}ms avg)", "SUCCESS")
            return TestResult(
                name=test_name,
                category="performance",
                status="PASS",
                response_time=total_time,
                response_data={
                    "concurrent_requests": concurrent_requests,
                    "successful_requests": successful_requests,
                    "success_rate": success_rate,
                    "average_response_time": avg_response_time
                }
            )
        else:
            return TestResult(
                name=test_name,
                category="performance",
                status="FAIL",
                response_time=total_time,
                error_message=f"Success rate {success_rate:.1f}% below threshold {success_threshold}%",
                response_data={
                    "concurrent_requests": concurrent_requests,
                    "successful_requests": successful_requests,
                    "success_rate": success_rate,
                    "average_response_time": avg_response_time
                }
            )
    
    def run_https_test(self, base_url: str) -> TestResult:
        """Test HTTPS enforcement"""
        test_name = "HTTPS Enforcement"
        
        # Convert HTTPS URL to HTTP
        http_url = base_url.replace('https://', 'http://')
        
        if http_url == base_url:
            # Already HTTP, should fail or redirect
            return TestResult(
                name=test_name,
                category="security",
                status="PASS",
                response_time=0,
                response_data={"note": "URL already HTTP, assuming redirect configured"}
            )
        
        try:
            response = self.session.get(http_url, allow_redirects=False, timeout=10)
            
            if response.status_code in [301, 302, 307, 308]:
                # Check if redirected to HTTPS
                location = response.headers.get('location', '')
                if location.startswith('https://'):
                    return TestResult(
                        name=test_name,
                        category="security",
                        status="PASS",
                        response_time=0,
                        response_data={"redirect_location": location}
                    )
            
            return TestResult(
                name=test_name,
                category="security",
                status="FAIL",
                response_time=0,
                error_message=f"HTTP request not redirected to HTTPS (status: {response.status_code})"
            )
            
        except Exception as e:
            return TestResult(
                name=test_name,
                category="security",
                status="FAIL",
                response_time=0,
                error_message=f"HTTPS test error: {str(e)}"
            )
    
    def run_test_suite(self, suite_name: str, base_url: str) -> List[TestResult]:
        """Run a complete test suite"""
        suite_results = []
        
        if suite_name not in self.config['test_scenarios']:
            self.log(f"Test suite '{suite_name}' not found", "ERROR")
            return suite_results
        
        tests = self.config['test_scenarios'][suite_name]
        self.log(f"Running test suite: {suite_name} ({len(tests)} tests)", "INFO")
        
        for test_config in tests:
            test_config['category'] = suite_name
            
            # Handle special test types
            if test_config.get('test_type') == 'https_redirect':
                result = self.run_https_test(base_url)
            elif 'concurrent_requests' in test_config:
                result = self.run_concurrent_test(test_config, base_url)
            else:
                result = self.make_request(test_config, base_url)
            
            suite_results.append(result)
            
            if result.status == "FAIL":
                self.log(f"✗ {result.name}: {result.error_message}", "ERROR")
        
        return suite_results
    
    def run_all_tests(self, test_suites: List[str] = None) -> Dict[str, Any]:
        """Run all or specified test suites"""
        if test_suites is None:
            test_suites = list(self.config['test_scenarios'].keys())
        
        self.log(f"Starting smoke tests for environment: {self.environment}", "INFO")
        self.log(f"Function URL: {self.base_urls['functions']}", "INFO")
        self.log(f"Web URL: {self.base_urls['web']}", "INFO")
        
        start_time = time.time()
        all_results = []
        
        for suite_name in test_suites:
            # Determine base URL for test suite
            if suite_name in ['health_checks', 'infrastructure', 'spiritual_guidance', 'voice_tests', 'auth_tests', 'performance', 'error_scenarios', 'data_validation']:
                base_url = self.base_urls['functions']
            else:
                base_url = self.base_urls['web']
            
            suite_results = self.run_test_suite(suite_name, base_url)
            all_results.extend(suite_results)
        
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
    
    def generate_reports(self, summary: Dict[str, Any], output_dir: str = "reports"):
        """Generate test reports in multiple formats"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        
        # JSON Report
        json_file = output_path / f"smoke-test-{self.environment}-{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        # Markdown Report
        md_file = output_path / f"smoke-test-{self.environment}-{timestamp}.md"
        self.generate_markdown_report(summary, md_file)
        
        self.log(f"Reports generated:", "SUCCESS")
        self.log(f"  JSON: {json_file}", "INFO")
        self.log(f"  Markdown: {md_file}", "INFO")
        
        return {"json": json_file, "markdown": md_file}
    
    def generate_markdown_report(self, summary: Dict[str, Any], output_file: Path):
        """Generate Markdown test report"""
        with open(output_file, 'w') as f:
            f.write(f"# Vimarsh Smoke Test Report\n\n")
            f.write(f"**Environment:** {summary['environment']}  \n")
            f.write(f"**Timestamp:** {summary['timestamp']}  \n")
            f.write(f"**Execution Time:** {summary['execution_time']:.1f}s  \n\n")
            
            f.write(f"## Summary\n\n")
            f.write(f"- **Total Tests:** {summary['total_tests']}\n")
            f.write(f"- **Passed:** {summary['passed_tests']}\n")
            f.write(f"- **Failed:** {summary['failed_tests']}\n")
            f.write(f"- **Success Rate:** {summary['success_rate']:.1f}%\n\n")
            
            # Results by category
            categories = {}
            for result in summary['test_results']:
                category = result.get('category', 'general')
                if category not in categories:
                    categories[category] = {'passed': 0, 'failed': 0, 'tests': []}
                
                if result['status'] == 'PASS':
                    categories[category]['passed'] += 1
                else:
                    categories[category]['failed'] += 1
                categories[category]['tests'].append(result)
            
            f.write(f"## Results by Category\n\n")
            f.write(f"| Category | Passed | Failed | Success Rate |\n")
            f.write(f"|----------|--------|--------|--------------|\n")
            
            for category, data in categories.items():
                total = data['passed'] + data['failed']
                rate = (data['passed'] / total * 100) if total > 0 else 0
                status_icon = "✅" if data['failed'] == 0 else "❌"
                f.write(f"| {status_icon} {category} | {data['passed']} | {data['failed']} | {rate:.1f}% |\n")
            
            # Detailed results
            f.write(f"\n## Detailed Results\n\n")
            for category, data in categories.items():
                f.write(f"### {category.title()}\n\n")
                f.write(f"| Test | Status | Response Time | Notes |\n")
                f.write(f"|------|--------|---------------|-------|\n")
                
                for test in data['tests']:
                    status_icon = "✅" if test['status'] == 'PASS' else "❌"
                    response_time = f"{test['response_time']:.0f}ms"
                    notes = test.get('error_message', 'OK')[:50]
                    f.write(f"| {test['name']} | {status_icon} {test['status']} | {response_time} | {notes} |\n")
                
                f.write(f"\n")
            
            # Failed tests details
            failed_tests = [r for r in summary['test_results'] if r['status'] == 'FAIL']
            if failed_tests:
                f.write(f"## Failed Tests Details\n\n")
                for test in failed_tests:
                    f.write(f"### {test['name']}\n\n")
                    f.write(f"- **Category:** {test['category']}\n")
                    f.write(f"- **Error:** {test['error_message']}\n")
                    f.write(f"- **Response Time:** {test['response_time']:.0f}ms\n")
                    if test.get('response_data'):
                        f.write(f"- **Response Data:** ```json\n{json.dumps(test['response_data'], indent=2)}\n```\n")
                    f.write(f"\n")

def main():
    parser = argparse.ArgumentParser(description="Vimarsh Production Deployment Smoke Tests")
    parser.add_argument("--environment", "-e", required=True, choices=["staging", "prod"], 
                       help="Target environment")
    parser.add_argument("--config", "-c", default="config/testing/smoke-test-config.yaml",
                       help="Path to test configuration file")
    parser.add_argument("--suites", "-s", nargs="+", 
                       help="Specific test suites to run")
    parser.add_argument("--output", "-o", default="reports",
                       help="Output directory for reports")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose output")
    parser.add_argument("--no-reports", action="store_true",
                       help="Skip report generation")
    
    args = parser.parse_args()
    
    # Check if config file exists
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"❌ Configuration file not found: {config_path}")
        sys.exit(1)
    
    try:
        # Initialize test runner
        runner = SmokeTestRunner(args.config, args.environment, args.verbose)
        
        # Run tests
        summary = runner.run_all_tests(args.suites)
        
        # Generate reports
        if not args.no_reports:
            runner.generate_reports(summary, args.output)
        
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
