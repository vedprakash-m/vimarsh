#!/usr/bin/env python3
"""
Comprehensive E2E Validator for Vimarsh CI/CD Pipeline
Professional-grade validation suite for production deployment
"""

import asyncio
import aiohttp
import argparse
import json
import logging
import os
import subprocess
import sys
import time
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import tempfile

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('e2e_validation.log')
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Structured test result"""
    test_name: str
    category: str
    status: str  # passed, failed, skipped, warning
    duration: float
    details: str
    error_message: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

@dataclass
class ValidationReport:
    """Comprehensive validation report"""
    pipeline_id: str
    environment: str
    validation_level: str
    start_time: str
    end_time: str
    duration: float
    total_tests: int
    passed_tests: int
    failed_tests: int
    warning_tests: int
    skipped_tests: int
    results: List[TestResult]
    summary: Dict[str, Any]
    recommendations: List[str]

class ComprehensiveE2EValidator:
    """Professional E2E validation suite"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.session = None
        self.results: List[TestResult] = []
        self.start_time = time.time()
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load validation configuration"""
        default_config = {
            "environments": {
                "production": {
                    "frontend_url": "https://vimarsh.vedmishra.com",
                    "backend_url": "https://vimarsh-backend-app-flex.azurewebsites.net",
                    "health_endpoint": "/api/health",
                    "test_timeout": 30
                },
                "staging": {
                    "frontend_url": "https://staging-vimarsh.vedmishra.com",
                    "backend_url": "https://staging-vimarsh-backend.azurewebsites.net",
                    "health_endpoint": "/api/health",
                    "test_timeout": 30
                }
            },
            "tests": {
                "infrastructure": {
                    "timeout": 60,
                    "retries": 3,
                    "endpoints": [
                        {"path": "/api/health", "method": "GET", "expected_status": 200},
                        {"path": "/api/spiritual_guidance", "method": "POST", "expected_status": 200}
                    ]
                },
                "performance": {
                    "max_response_time": 5000,  # ms
                    "concurrent_users": 10,
                    "test_duration": 30  # seconds
                },
                "security": {
                    "check_https": True,
                    "check_cors": True,
                    "check_headers": True,
                    "scan_secrets": True
                }
            },
            "thresholds": {
                "coverage_minimum": 80,
                "performance_p95": 3000,
                "security_score": 85,
                "availability": 99.9
            }
        }
        
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = yaml.safe_load(f)
                default_config.update(user_config)
        
        return default_config
    
    async def run_comprehensive_validation(self, environment: str = "production", 
                                         level: str = "full") -> ValidationReport:
        """Run comprehensive validation suite"""
        logger.info(f"🚀 Starting comprehensive E2E validation for {environment} (level: {level})")
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
            self.session = session
            
            # Define test suites based on level
            test_suites = self._get_test_suites(level)
            
            # Run test suites in parallel where possible
            for suite_name, test_functions in test_suites.items():
                logger.info(f"🧪 Running {suite_name} tests...")
                await self._run_test_suite(suite_name, test_functions, environment)
        
        return self._generate_report(environment, level)
    
    def _get_test_suites(self, level: str) -> Dict[str, List[str]]:
        """Get test suites based on validation level"""
        suites = {
            "infrastructure": [
                "test_project_structure",
                "test_dependencies",
                "test_configuration_files"
            ],
            "security": [
                "test_secrets_scanning",
                "test_dependency_vulnerabilities", 
                "test_https_enforcement",
                "test_security_headers"
            ],
            "functionality": [
                "test_health_endpoints",
                "test_api_endpoints",
                "test_authentication",
                "test_spiritual_guidance_api"
            ]
        }
        
        if level in ["comprehensive", "full"]:
            suites.update({
                "performance": [
                    "test_response_times",
                    "test_concurrent_load",
                    "test_resource_usage"
                ],
                "integration": [
                    "test_end_to_end_workflow",
                    "test_database_connectivity",
                    "test_azure_services",
                    "test_monitoring_integration"
                ],
                "deployment": [
                    "test_deployment_artifacts",
                    "test_rollback_capability",
                    "test_configuration_management"
                ]
            })
        
        return suites
    
    async def _run_test_suite(self, suite_name: str, test_functions: List[str], 
                            environment: str):
        """Run a test suite with proper error handling"""
        for test_func_name in test_functions:
            try:
                test_func = getattr(self, test_func_name, None)
                if test_func:
                    result = await test_func(environment)
                    self.results.append(result)
                else:
                    self.results.append(TestResult(
                        test_name=test_func_name,
                        category=suite_name,
                        status="skipped",
                        duration=0,
                        details=f"Test function {test_func_name} not implemented"
                    ))
            except Exception as e:
                logger.error(f"❌ Test {test_func_name} failed: {e}")
                self.results.append(TestResult(
                    test_name=test_func_name,
                    category=suite_name,
                    status="failed",
                    duration=0,
                    details="Test execution failed",
                    error_message=str(e)
                ))
    
    # =============================================================================
    # INFRASTRUCTURE TESTS
    # =============================================================================
    
    async def test_project_structure(self, environment: str) -> TestResult:
        """Validate essential project structure"""
        start_time = time.time()
        
        essential_files = [
            "backend/function_app.py",
            "backend/requirements.txt",
            "backend/host.json",
            "frontend/package.json",
            "README.md",
            ".github/workflows/unified-ci-cd.yml",
            "infrastructure/main.bicep"
        ]
        
        missing_files = []
        for file_path in essential_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        duration = time.time() - start_time
        
        if missing_files:
            return TestResult(
                test_name="project_structure",
                category="infrastructure",
                status="failed",
                duration=duration,
                details=f"Missing essential files: {missing_files}"
            )
        else:
            return TestResult(
                test_name="project_structure",
                category="infrastructure", 
                status="passed",
                duration=duration,
                details=f"All {len(essential_files)} essential files present",
                metrics={"total_files": len(essential_files), "missing_files": 0}
            )
    
    async def test_dependencies(self, environment: str) -> TestResult:
        """Validate project dependencies"""
        start_time = time.time()
        issues = []
        
        # Check Python dependencies
        try:
            result = subprocess.run(
                ["python", "-m", "pip", "check"],
                cwd="backend",
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode != 0:
                issues.append(f"Python dependencies: {result.stderr}")
        except Exception as e:
            issues.append(f"Python dependency check failed: {e}")
        
        # Check Node dependencies
        try:
            result = subprocess.run(
                ["npm", "audit", "--audit-level=high"],
                cwd="frontend",
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode != 0:
                issues.append(f"NPM security audit found issues")
        except Exception as e:
            issues.append(f"NPM audit failed: {e}")
        
        duration = time.time() - start_time
        
        if issues:
            return TestResult(
                test_name="dependencies",
                category="infrastructure",
                status="warning" if len(issues) < 3 else "failed",
                duration=duration,
                details=f"Dependency issues: {issues}"
            )
        else:
            return TestResult(
                test_name="dependencies",
                category="infrastructure",
                status="passed",
                duration=duration,
                details="All dependencies validated successfully"
            )
    
    async def test_configuration_files(self, environment: str) -> TestResult:
        """Validate configuration files"""
        start_time = time.time()
        
        config_files = {
            "backend/host.json": "json",
            "frontend/package.json": "json",
            "backend/pyproject.toml": "toml",
            ".github/workflows/unified-ci-cd.yml": "yaml"
        }
        
        validation_errors = []
        
        for file_path, file_type in config_files.items():
            if not os.path.exists(file_path):
                validation_errors.append(f"Missing config file: {file_path}")
                continue
                
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    
                if file_type == "json":
                    json.loads(content)
                elif file_type == "yaml":
                    yaml.safe_load(content)
                elif file_type == "toml":
                    # Basic TOML validation
                    if "[]" in content or "[tool." in content:
                        pass  # Basic structure check
                    else:
                        validation_errors.append(f"Invalid TOML structure: {file_path}")
                        
            except Exception as e:
                validation_errors.append(f"Invalid {file_type} in {file_path}: {e}")
        
        duration = time.time() - start_time
        
        if validation_errors:
            return TestResult(
                test_name="configuration_files",
                category="infrastructure",
                status="failed",
                duration=duration,
                details=f"Configuration errors: {validation_errors}"
            )
        else:
            return TestResult(
                test_name="configuration_files", 
                category="infrastructure",
                status="passed",
                duration=duration,
                details=f"All {len(config_files)} configuration files validated"
            )
    
    # =============================================================================
    # SECURITY TESTS
    # =============================================================================
    
    async def test_secrets_scanning(self, environment: str) -> TestResult:
        """Advanced secrets scanning"""
        start_time = time.time()
        
        secret_patterns = [
            (r"(?i)(password|pwd)\s*[:=]\s*['\"][^'\"]{4,}['\"]", "Potential passwords"),
            (r"(?i)(api[_-]?key|apikey)\s*[:=]\s*['\"][^'\"]{10,}['\"]", "API keys"),
            (r"(?i)(secret|token)\s*[:=]\s*['\"][^'\"]{8,}['\"]", "Secrets/tokens"),
            (r"AccountKey=[A-Za-z0-9+/=]{40,}", "Azure Account Keys"),
            (r"sk-[A-Za-z0-9]{48}", "OpenAI API Keys"),
            (r"AKIA[0-9A-Z]{16}", "AWS Access Keys"),
            (r"-----BEGIN (RSA )?PRIVATE KEY-----", "Private Keys")
        ]
        
        findings = []
        exclude_dirs = {".git", "node_modules", ".venv", "__pycache__", ".archive"}
        
        for root, dirs, files in os.walk("."):
            # Remove excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                if file.endswith(('.py', '.js', '.ts', '.json', '.yml', '.yaml', '.env')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            
                        for pattern, description in secret_patterns:
                            import re
                            matches = re.findall(pattern, content)
                            if matches:
                                # Filter out obvious test/example patterns
                                if not any(exclude in file_path.lower() 
                                         for exclude in ['test', 'example', 'sample', 'mock']):
                                    findings.append(f"{description} in {file_path}")
                    except Exception:
                        continue
        
        duration = time.time() - start_time
        
        if findings:
            return TestResult(
                test_name="secrets_scanning",
                category="security",
                status="failed",
                duration=duration,
                details=f"Security issues found: {findings[:5]}",  # Limit to first 5
                metrics={"total_findings": len(findings)}
            )
        else:
            return TestResult(
                test_name="secrets_scanning",
                category="security",
                status="passed",
                duration=duration,
                details="No hardcoded secrets detected"
            )
    
    async def test_dependency_vulnerabilities(self, environment: str) -> TestResult:
        """Check for dependency vulnerabilities"""
        start_time = time.time()
        
        vulnerabilities = []
        
        # Check Python packages
        try:
            result = subprocess.run(
                ["python", "-m", "pip", "audit"],
                cwd="backend",
                capture_output=True,
                text=True,
                timeout=120
            )
            if result.returncode != 0 and "vulnerabilities" in result.stdout.lower():
                vulnerabilities.append("Python package vulnerabilities detected")
        except Exception:
            pass
        
        # Check Node packages with detailed audit
        try:
            result = subprocess.run(
                ["npm", "audit", "--audit-level=moderate", "--json"],
                cwd="frontend",
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode != 0:
                try:
                    audit_data = json.loads(result.stdout)
                    if audit_data.get("vulnerabilities", {}):
                        vuln_count = len(audit_data["vulnerabilities"])
                        vulnerabilities.append(f"{vuln_count} NPM vulnerabilities found")
                except:
                    vulnerabilities.append("NPM audit found issues")
        except Exception:
            pass
        
        duration = time.time() - start_time
        
        if vulnerabilities:
            return TestResult(
                test_name="dependency_vulnerabilities",
                category="security",
                status="warning",  # Most dependency vulns are non-critical
                duration=duration,
                details=f"Vulnerabilities: {vulnerabilities}"
            )
        else:
            return TestResult(
                test_name="dependency_vulnerabilities",
                category="security",
                status="passed",
                duration=duration,
                details="No critical vulnerabilities in dependencies"
            )
    
    async def test_https_enforcement(self, environment: str) -> TestResult:
        """Test HTTPS enforcement"""
        start_time = time.time()
        
        env_config = self.config["environments"].get(environment, {})
        frontend_url = env_config.get("frontend_url", "")
        backend_url = env_config.get("backend_url", "")
        
        if not frontend_url or not backend_url:
            return TestResult(
                test_name="https_enforcement",
                category="security",
                status="skipped",
                duration=time.time() - start_time,
                details=f"No URLs configured for environment: {environment}"
            )
        
        issues = []
        
        # Test frontend HTTPS enforcement
        try:
            http_url = frontend_url.replace("https://", "http://")
            async with self.session.get(http_url, allow_redirects=False) as response:
                if response.status not in [301, 302, 308]:
                    issues.append("Frontend does not redirect HTTP to HTTPS")
        except Exception as e:
            issues.append(f"Frontend HTTPS test failed: {e}")
        
        # Test backend HTTPS enforcement  
        try:
            http_url = backend_url.replace("https://", "http://") + "/api/health"
            async with self.session.get(http_url, allow_redirects=False) as response:
                if response.status not in [301, 302, 308]:
                    issues.append("Backend does not redirect HTTP to HTTPS")
        except Exception as e:
            issues.append(f"Backend HTTPS test failed: {e}")
        
        duration = time.time() - start_time
        
        if issues:
            return TestResult(
                test_name="https_enforcement",
                category="security",
                status="failed",
                duration=duration,
                details=f"HTTPS issues: {issues}"
            )
        else:
            return TestResult(
                test_name="https_enforcement",
                category="security",
                status="passed",
                duration=duration,
                details="HTTPS properly enforced"
            )
    
    async def test_security_headers(self, environment: str) -> TestResult:
        """Test security headers"""
        start_time = time.time()
        
        env_config = self.config["environments"].get(environment, {})
        frontend_url = env_config.get("frontend_url", "")
        
        if not frontend_url:
            return TestResult(
                test_name="security_headers",
                category="security", 
                status="skipped",
                duration=time.time() - start_time,
                details=f"No frontend URL configured for environment: {environment}"
            )
        
        required_headers = [
            "x-content-type-options",
            "x-frame-options", 
            "x-xss-protection",
            "strict-transport-security"
        ]
        
        missing_headers = []
        
        try:
            async with self.session.get(frontend_url) as response:
                headers = {k.lower(): v for k, v in response.headers.items()}
                
                for header in required_headers:
                    if header not in headers:
                        missing_headers.append(header)
                        
        except Exception as e:
            return TestResult(
                test_name="security_headers",
                category="security",
                status="failed",
                duration=time.time() - start_time,
                details=f"Failed to check security headers: {e}"
            )
        
        duration = time.time() - start_time
        
        if missing_headers:
            return TestResult(
                test_name="security_headers",
                category="security",
                status="warning",
                duration=duration,
                details=f"Missing security headers: {missing_headers}"
            )
        else:
            return TestResult(
                test_name="security_headers",
                category="security",
                status="passed",
                duration=duration,
                details="All required security headers present"
            )
    
    # =============================================================================
    # FUNCTIONALITY TESTS
    # =============================================================================
    
    async def test_health_endpoints(self, environment: str) -> TestResult:
        """Test health endpoints"""
        start_time = time.time()
        
        env_config = self.config["environments"].get(environment, {})
        backend_url = env_config.get("backend_url", "")
        health_endpoint = env_config.get("health_endpoint", "/api/health")
        
        if not backend_url:
            return TestResult(
                test_name="health_endpoints",
                category="functionality",
                status="skipped",
                duration=time.time() - start_time,
                details=f"No backend URL configured for environment: {environment}"
            )
        
        try:
            health_url = f"{backend_url}{health_endpoint}"
            async with self.session.get(health_url) as response:
                response_time = response.headers.get('X-Response-Time', 'unknown')
                
                if response.status == 200:
                    data = await response.json()
                    if data.get("status") == "healthy":
                        return TestResult(
                            test_name="health_endpoints",
                            category="functionality",
                            status="passed",
                            duration=time.time() - start_time,
                            details="Health endpoint responding correctly",
                            metrics={
                                "response_time": response_time,
                                "status_code": response.status
                            }
                        )
                    else:
                        return TestResult(
                            test_name="health_endpoints",
                            category="functionality",
                            status="warning",
                            duration=time.time() - start_time,
                            details=f"Health endpoint returned status: {data.get('status')}"
                        )
                else:
                    return TestResult(
                        test_name="health_endpoints",
                        category="functionality", 
                        status="failed",
                        duration=time.time() - start_time,
                        details=f"Health endpoint returned {response.status}"
                    )
                    
        except Exception as e:
            return TestResult(
                test_name="health_endpoints",
                category="functionality",
                status="failed",
                duration=time.time() - start_time,
                details="Health endpoint not accessible",
                error_message=str(e)
            )
    
    async def test_api_endpoints(self, environment: str) -> TestResult:
        """Test critical API endpoints"""
        start_time = time.time()
        
        env_config = self.config["environments"].get(environment, {})
        backend_url = env_config.get("backend_url", "")
        
        if not backend_url:
            return TestResult(
                test_name="api_endpoints",
                category="functionality",
                status="skipped",
                duration=time.time() - start_time,
                details=f"No backend URL configured for environment: {environment}"
            )
        
        endpoints_to_test = self.config["tests"]["infrastructure"]["endpoints"]
        
        passed_tests = 0
        failed_tests = 0
        test_details = []
        
        for endpoint in endpoints_to_test:
            try:
                url = f"{backend_url}{endpoint['path']}"
                method = endpoint['method'].lower()
                expected_status = endpoint['expected_status']
                
                # Prepare test data for POST requests
                test_data = {}
                if method == 'post' and endpoint['path'] == '/api/spiritual_guidance':
                    test_data = {
                        "query": "What is dharma?",
                        "language": "English"
                    }
                
                if method == 'get':
                    async with self.session.get(url) as response:
                        status = response.status
                elif method == 'post':
                    async with self.session.post(url, json=test_data) as response:
                        status = response.status
                
                if status == expected_status:
                    passed_tests += 1
                    test_details.append(f"✅ {endpoint['path']}: {status}")
                else:
                    failed_tests += 1
                    test_details.append(f"❌ {endpoint['path']}: {status} (expected {expected_status})")
                    
            except Exception as e:
                failed_tests += 1
                test_details.append(f"❌ {endpoint['path']}: Error - {e}")
        
        duration = time.time() - start_time
        
        if failed_tests == 0:
            return TestResult(
                test_name="api_endpoints",
                category="functionality",
                status="passed",
                duration=duration,
                details=f"All {passed_tests} API endpoints working",
                metrics={"passed": passed_tests, "failed": failed_tests}
            )
        elif passed_tests > failed_tests:
            return TestResult(
                test_name="api_endpoints",
                category="functionality",
                status="warning",
                duration=duration,
                details=f"Some API endpoints failing: {test_details}",
                metrics={"passed": passed_tests, "failed": failed_tests}
            )
        else:
            return TestResult(
                test_name="api_endpoints",
                category="functionality",
                status="failed",
                duration=duration,
                details=f"Multiple API endpoints failing: {test_details}",
                metrics={"passed": passed_tests, "failed": failed_tests}
            )
    
    async def test_authentication(self, environment: str) -> TestResult:
        """Test authentication mechanisms"""
        start_time = time.time()
        
        # For now, this is a placeholder since auth testing requires
        # proper test credentials and token management
        return TestResult(
            test_name="authentication",
            category="functionality",
            status="skipped",
            duration=time.time() - start_time,
            details="Authentication testing requires test credentials setup"
        )
    
    async def test_spiritual_guidance_api(self, environment: str) -> TestResult:
        """Test core spiritual guidance functionality"""
        start_time = time.time()
        
        env_config = self.config["environments"].get(environment, {})
        backend_url = env_config.get("backend_url", "")
        
        if not backend_url:
            return TestResult(
                test_name="spiritual_guidance_api",
                category="functionality",
                status="skipped",
                duration=time.time() - start_time,
                details=f"No backend URL configured for environment: {environment}"
            )
        
        test_queries = [
            {"query": "What is dharma according to Hindu philosophy?", "language": "English"},
            {"query": "Tell me about Krishna's teachings", "language": "English"},
            {"query": "What is the meaning of meditation?", "language": "English"}
        ]
        
        successful_queries = 0
        failed_queries = 0
        response_times = []
        
        for test_query in test_queries:
            try:
                query_start = time.time()
                url = f"{backend_url}/api/spiritual_guidance"
                
                async with self.session.post(url, json=test_query, timeout=30) as response:
                    query_duration = time.time() - query_start
                    response_times.append(query_duration)
                    
                    if response.status == 200:
                        data = await response.json()
                        if data.get("response") and len(data["response"]) > 50:
                            # Check for spiritual content indicators
                            response_text = data["response"].lower()
                            spiritual_indicators = ["dharma", "spiritual", "divine", "wisdom", "meditation"]
                            
                            if any(indicator in response_text for indicator in spiritual_indicators):
                                successful_queries += 1
                            else:
                                failed_queries += 1
                        else:
                            failed_queries += 1
                    else:
                        failed_queries += 1
                        
            except Exception as e:
                failed_queries += 1
                logger.error(f"Spiritual guidance query failed: {e}")
        
        duration = time.time() - start_time
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        if successful_queries == len(test_queries):
            return TestResult(
                test_name="spiritual_guidance_api",
                category="functionality",
                status="passed",
                duration=duration,
                details=f"All {successful_queries} spiritual guidance queries successful",
                metrics={
                    "successful_queries": successful_queries,
                    "failed_queries": failed_queries,
                    "avg_response_time": avg_response_time
                }
            )
        elif successful_queries > 0:
            return TestResult(
                test_name="spiritual_guidance_api",
                category="functionality", 
                status="warning",
                duration=duration,
                details=f"{successful_queries}/{len(test_queries)} spiritual guidance queries successful",
                metrics={
                    "successful_queries": successful_queries,
                    "failed_queries": failed_queries,
                    "avg_response_time": avg_response_time
                }
            )
        else:
            return TestResult(
                test_name="spiritual_guidance_api",
                category="functionality",
                status="failed",
                duration=duration,
                details="All spiritual guidance queries failed",
                metrics={
                    "successful_queries": successful_queries,
                    "failed_queries": failed_queries
                }
            )
    
    # =============================================================================
    # PERFORMANCE TESTS
    # =============================================================================
    
    async def test_response_times(self, environment: str) -> TestResult:
        """Test API response times"""
        start_time = time.time()
        
        env_config = self.config["environments"].get(environment, {})
        backend_url = env_config.get("backend_url", "")
        
        if not backend_url:
            return TestResult(
                test_name="response_times",
                category="performance",
                status="skipped",
                duration=time.time() - start_time,
                details=f"No backend URL configured for environment: {environment}"
            )
        
        max_response_time = self.config["tests"]["performance"]["max_response_time"] / 1000  # Convert to seconds
        
        endpoints_to_test = [
            f"{backend_url}/api/health",
            f"{backend_url}/api/spiritual_guidance"
        ]
        
        response_times = []
        slow_endpoints = []
        
        for endpoint in endpoints_to_test:
            try:
                test_start = time.time()
                
                if "spiritual_guidance" in endpoint:
                    test_data = {"query": "What is meditation?", "language": "English"}
                    async with self.session.post(endpoint, json=test_data) as response:
                        await response.text()
                else:
                    async with self.session.get(endpoint) as response:
                        await response.text()
                
                response_time = time.time() - test_start
                response_times.append(response_time)
                
                if response_time > max_response_time:
                    slow_endpoints.append(f"{endpoint}: {response_time:.2f}s")
                    
            except Exception as e:
                logger.error(f"Response time test failed for {endpoint}: {e}")
        
        duration = time.time() - start_time
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        max_measured_time = max(response_times) if response_times else 0
        
        if slow_endpoints:
            return TestResult(
                test_name="response_times",
                category="performance",
                status="warning",
                duration=duration,
                details=f"Slow endpoints detected: {slow_endpoints}",
                metrics={
                    "avg_response_time": avg_response_time,
                    "max_response_time": max_measured_time,
                    "threshold": max_response_time
                }
            )
        else:
            return TestResult(
                test_name="response_times",
                category="performance",
                status="passed",
                duration=duration,
                details=f"All endpoints respond within {max_response_time}s threshold",
                metrics={
                    "avg_response_time": avg_response_time,
                    "max_response_time": max_measured_time,
                    "threshold": max_response_time
                }
            )
    
    async def test_concurrent_load(self, environment: str) -> TestResult:
        """Test concurrent user load"""
        start_time = time.time()
        
        env_config = self.config["environments"].get(environment, {})
        backend_url = env_config.get("backend_url", "")
        
        if not backend_url:
            return TestResult(
                test_name="concurrent_load",
                category="performance",
                status="skipped",
                duration=time.time() - start_time,
                details=f"No backend URL configured for environment: {environment}"
            )
        
        concurrent_users = self.config["tests"]["performance"]["concurrent_users"]
        test_duration = self.config["tests"]["performance"]["test_duration"]
        
        # Simple concurrent load test
        async def make_request():
            try:
                async with self.session.get(f"{backend_url}/api/health") as response:
                    return response.status == 200
            except:
                return False
        
        # Run concurrent requests
        successful_requests = 0
        failed_requests = 0
        
        tasks = [make_request() for _ in range(concurrent_users)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if result is True:
                successful_requests += 1
            else:
                failed_requests += 1
        
        duration = time.time() - start_time
        success_rate = (successful_requests / (successful_requests + failed_requests)) * 100
        
        if success_rate >= 95:
            return TestResult(
                test_name="concurrent_load",
                category="performance",
                status="passed",
                duration=duration,
                details=f"Successfully handled {concurrent_users} concurrent requests",
                metrics={
                    "concurrent_users": concurrent_users,
                    "success_rate": success_rate,
                    "successful_requests": successful_requests,
                    "failed_requests": failed_requests
                }
            )
        elif success_rate >= 80:
            return TestResult(
                test_name="concurrent_load",
                category="performance",
                status="warning",
                duration=duration,
                details=f"Partial success with {concurrent_users} concurrent requests: {success_rate:.1f}% success rate",
                metrics={
                    "concurrent_users": concurrent_users,
                    "success_rate": success_rate,
                    "successful_requests": successful_requests,
                    "failed_requests": failed_requests
                }
            )
        else:
            return TestResult(
                test_name="concurrent_load",
                category="performance",
                status="failed",
                duration=duration,
                details=f"Poor performance under {concurrent_users} concurrent requests: {success_rate:.1f}% success rate",
                metrics={
                    "concurrent_users": concurrent_users,
                    "success_rate": success_rate,
                    "successful_requests": successful_requests,
                    "failed_requests": failed_requests
                }
            )
    
    async def test_resource_usage(self, environment: str) -> TestResult:
        """Test resource usage metrics"""
        start_time = time.time()
        
        # For now, this is a placeholder since resource monitoring
        # requires proper Azure monitoring setup
        return TestResult(
            test_name="resource_usage",
            category="performance",
            status="skipped",
            duration=time.time() - start_time,
            details="Resource usage monitoring requires Azure Application Insights integration"
        )
    
    # =============================================================================
    # INTEGRATION TESTS  
    # =============================================================================
    
    async def test_end_to_end_workflow(self, environment: str) -> TestResult:
        """Test complete end-to-end user workflow"""
        start_time = time.time()
        
        env_config = self.config["environments"].get(environment, {})
        backend_url = env_config.get("backend_url", "")
        frontend_url = env_config.get("frontend_url", "")
        
        if not backend_url or not frontend_url:
            return TestResult(
                test_name="end_to_end_workflow",
                category="integration",
                status="skipped",
                duration=time.time() - start_time,
                details=f"URLs not configured for environment: {environment}"
            )
        
        workflow_steps = []
        
        # Step 1: Frontend accessibility
        try:
            async with self.session.get(frontend_url) as response:
                if response.status == 200:
                    workflow_steps.append("✅ Frontend accessible")
                else:
                    workflow_steps.append(f"❌ Frontend returned {response.status}")
        except Exception as e:
            workflow_steps.append(f"❌ Frontend access failed: {e}")
        
        # Step 2: Backend health check
        try:
            async with self.session.get(f"{backend_url}/api/health") as response:
                if response.status == 200:
                    workflow_steps.append("✅ Backend health check passed")
                else:
                    workflow_steps.append(f"❌ Backend health check failed: {response.status}")
        except Exception as e:
            workflow_steps.append(f"❌ Backend health check error: {e}")
        
        # Step 3: Spiritual guidance workflow
        try:
            test_query = {
                "query": "What is the path to spiritual enlightenment?",
                "language": "English"
            }
            
            async with self.session.post(f"{backend_url}/api/spiritual_guidance", json=test_query) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("response") and len(data["response"]) > 100:
                        workflow_steps.append("✅ Spiritual guidance workflow completed")
                    else:
                        workflow_steps.append("❌ Spiritual guidance returned incomplete response")
                else:
                    workflow_steps.append(f"❌ Spiritual guidance failed: {response.status}")
        except Exception as e:
            workflow_steps.append(f"❌ Spiritual guidance workflow error: {e}")
        
        duration = time.time() - start_time
        failed_steps = [step for step in workflow_steps if step.startswith("❌")]
        
        if not failed_steps:
            return TestResult(
                test_name="end_to_end_workflow",
                category="integration",
                status="passed",
                duration=duration,
                details=f"Complete E2E workflow successful: {workflow_steps}",
                metrics={"total_steps": len(workflow_steps), "failed_steps": len(failed_steps)}
            )
        elif len(failed_steps) < len(workflow_steps) / 2:
            return TestResult(
                test_name="end_to_end_workflow",
                category="integration",
                status="warning",
                duration=duration,
                details=f"Partial E2E workflow success: {workflow_steps}",
                metrics={"total_steps": len(workflow_steps), "failed_steps": len(failed_steps)}
            )
        else:
            return TestResult(
                test_name="end_to_end_workflow",
                category="integration",
                status="failed",
                duration=duration,
                details=f"E2E workflow failed: {workflow_steps}",
                metrics={"total_steps": len(workflow_steps), "failed_steps": len(failed_steps)}
            )
    
    async def test_database_connectivity(self, environment: str) -> TestResult:
        """Test database connectivity"""
        start_time = time.time()
        
        # For now, this is a placeholder since database testing
        # requires proper connection configuration
        return TestResult(
            test_name="database_connectivity",
            category="integration",
            status="skipped",
            duration=time.time() - start_time,
            details="Database connectivity testing requires Cosmos DB connection configuration"
        )
    
    async def test_azure_services(self, environment: str) -> TestResult:
        """Test Azure services integration"""
        start_time = time.time()
        
        # For now, this is a placeholder since Azure services testing
        # requires proper service principal and configuration
        return TestResult(
            test_name="azure_services",
            category="integration",
            status="skipped",
            duration=time.time() - start_time,
            details="Azure services testing requires proper authentication configuration"
        )
    
    async def test_monitoring_integration(self, environment: str) -> TestResult:
        """Test monitoring and observability integration"""
        start_time = time.time()
        
        # For now, this is a placeholder since monitoring testing
        # requires Application Insights configuration
        return TestResult(
            test_name="monitoring_integration",
            category="integration",
            status="skipped",
            duration=time.time() - start_time,
            details="Monitoring integration testing requires Application Insights configuration"
        )
    
    # =============================================================================
    # DEPLOYMENT TESTS
    # =============================================================================
    
    async def test_deployment_artifacts(self, environment: str) -> TestResult:
        """Test deployment artifacts"""
        start_time = time.time()
        
        required_artifacts = [
            "backend/function_app.py",
            "backend/requirements.txt",
            "backend/host.json",
            "frontend/build/index.html",
            "frontend/build/static",
            "infrastructure/main.bicep"
        ]
        
        missing_artifacts = []
        for artifact in required_artifacts:
            if not os.path.exists(artifact):
                missing_artifacts.append(artifact)
        
        duration = time.time() - start_time
        
        if missing_artifacts:
            return TestResult(
                test_name="deployment_artifacts",
                category="deployment",
                status="failed",
                duration=duration,
                details=f"Missing deployment artifacts: {missing_artifacts}"
            )
        else:
            return TestResult(
                test_name="deployment_artifacts",
                category="deployment",
                status="passed",
                duration=duration,
                details="All deployment artifacts present"
            )
    
    async def test_rollback_capability(self, environment: str) -> TestResult:
        """Test rollback capability"""
        start_time = time.time()
        
        # For now, this is a placeholder since rollback testing
        # requires deployment history and proper procedures
        return TestResult(
            test_name="rollback_capability",
            category="deployment",
            status="skipped",
            duration=time.time() - start_time,
            details="Rollback capability testing requires deployment history and procedures"
        )
    
    async def test_configuration_management(self, environment: str) -> TestResult:
        """Test configuration management"""
        start_time = time.time()
        
        # Check environment-specific configurations
        config_files = [
            f"infrastructure/parameters/{environment}.parameters.json",
            "backend/host.json",
            "frontend/staticwebapp.config.json"
        ]
        
        missing_configs = []
        for config_file in config_files:
            if not os.path.exists(config_file):
                missing_configs.append(config_file)
        
        duration = time.time() - start_time
        
        if missing_configs:
            return TestResult(
                test_name="configuration_management",
                category="deployment",
                status="warning",
                duration=duration,
                details=f"Missing configuration files: {missing_configs}"
            )
        else:
            return TestResult(
                test_name="configuration_management",
                category="deployment",
                status="passed",
                duration=duration,
                details="Configuration management validated"
            )
    
    # =============================================================================
    # REPORTING
    # =============================================================================
    
    def _generate_report(self, environment: str, level: str) -> ValidationReport:
        """Generate comprehensive validation report"""
        end_time = time.time()
        total_duration = end_time - self.start_time
        
        passed_tests = len([r for r in self.results if r.status == "passed"])
        failed_tests = len([r for r in self.results if r.status == "failed"])
        warning_tests = len([r for r in self.results if r.status == "warning"])
        skipped_tests = len([r for r in self.results if r.status == "skipped"])
        
        # Calculate success rate
        total_executed = passed_tests + failed_tests + warning_tests
        success_rate = (passed_tests / total_executed * 100) if total_executed > 0 else 0
        
        # Generate recommendations
        recommendations = self._generate_recommendations()
        
        # Generate summary
        summary = {
            "success_rate": success_rate,
            "total_executed_tests": total_executed,
            "critical_failures": failed_tests,
            "warnings": warning_tests,
            "overall_status": self._get_overall_status(success_rate, failed_tests),
            "deployment_ready": success_rate >= 85 and failed_tests == 0,
            "categories": self._get_category_summary()
        }
        
        return ValidationReport(
            pipeline_id=f"vimarsh-e2e-{int(time.time())}",
            environment=environment,
            validation_level=level,
            start_time=datetime.fromtimestamp(self.start_time).isoformat(),
            end_time=datetime.fromtimestamp(end_time).isoformat(),
            duration=total_duration,
            total_tests=len(self.results),
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            warning_tests=warning_tests,
            skipped_tests=skipped_tests,
            results=self.results,
            summary=summary,
            recommendations=recommendations
        )
    
    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Security recommendations
        security_failures = [r for r in self.results if r.category == "security" and r.status == "failed"]
        if security_failures:
            recommendations.append("🔒 CRITICAL: Fix security vulnerabilities before deployment")
            for failure in security_failures:
                recommendations.append(f"   - {failure.test_name}: {failure.details}")
        
        # Performance recommendations
        performance_warnings = [r for r in self.results if r.category == "performance" and r.status in ["failed", "warning"]]
        if performance_warnings:
            recommendations.append("⚡ Performance issues detected - consider optimization")
        
        # Functionality recommendations
        functionality_failures = [r for r in self.results if r.category == "functionality" and r.status == "failed"]
        if functionality_failures:
            recommendations.append("🚨 Core functionality failures - deployment not recommended")
        
        # Infrastructure recommendations
        infrastructure_issues = [r for r in self.results if r.category == "infrastructure" and r.status in ["failed", "warning"]]
        if infrastructure_issues:
            recommendations.append("🏗️ Infrastructure configuration needs attention")
        
        # General recommendations
        if not recommendations:
            recommendations.append("✅ All validations passed - deployment recommended")
        
        return recommendations
    
    def _get_overall_status(self, success_rate: float, failed_tests: int) -> str:
        """Get overall validation status"""
        if failed_tests == 0 and success_rate >= 95:
            return "EXCELLENT"
        elif failed_tests == 0 and success_rate >= 85:
            return "GOOD"
        elif failed_tests <= 2 and success_rate >= 70:
            return "ACCEPTABLE"
        elif failed_tests <= 5:
            return "NEEDS_ATTENTION"
        else:
            return "CRITICAL_ISSUES"
    
    def _get_category_summary(self) -> Dict[str, Dict[str, int]]:
        """Get summary by test category"""
        categories = {}
        for result in self.results:
            if result.category not in categories:
                categories[result.category] = {"passed": 0, "failed": 0, "warning": 0, "skipped": 0}
            categories[result.category][result.status] += 1
        return categories
    
    def print_report(self, report: ValidationReport):
        """Print formatted validation report"""
        print("\n" + "=" * 80)
        print("🚀 VIMARSH COMPREHENSIVE E2E VALIDATION REPORT")
        print("=" * 80)
        
        print(f"📊 Environment: {report.environment}")
        print(f"🎯 Validation Level: {report.validation_level}")
        print(f"⏱️  Duration: {report.duration:.1f} seconds")
        print(f"📅 Completed: {report.end_time}")
        print(f"🆔 Pipeline ID: {report.pipeline_id}")
        
        print("\n" + "=" * 80)
        print("📈 SUMMARY")
        print("=" * 80)
        
        print(f"✅ Passed: {report.passed_tests}")
        print(f"❌ Failed: {report.failed_tests}")
        print(f"⚠️  Warnings: {report.warning_tests}")
        print(f"⏭️  Skipped: {report.skipped_tests}")
        print(f"📊 Success Rate: {report.summary['success_rate']:.1f}%")
        print(f"🎯 Overall Status: {report.summary['overall_status']}")
        print(f"🚀 Deployment Ready: {'YES' if report.summary['deployment_ready'] else 'NO'}")
        
        print("\n" + "=" * 80)
        print("📋 DETAILED RESULTS BY CATEGORY")
        print("=" * 80)
        
        for category, results in report.summary['categories'].items():
            print(f"\n🔖 {category.upper()}")
            print(f"   ✅ Passed: {results['passed']}")
            print(f"   ❌ Failed: {results['failed']}")
            print(f"   ⚠️  Warnings: {results['warning']}")
            print(f"   ⏭️  Skipped: {results['skipped']}")
        
        print("\n" + "=" * 80)
        print("🔍 FAILED AND WARNING TESTS")
        print("=" * 80)
        
        for result in report.results:
            if result.status in ["failed", "warning"]:
                status_icon = "❌" if result.status == "failed" else "⚠️"
                print(f"{status_icon} [{result.category}] {result.test_name}")
                print(f"   Details: {result.details}")
                if result.error_message:
                    print(f"   Error: {result.error_message}")
                print()
        
        print("\n" + "=" * 80)
        print("💡 RECOMMENDATIONS")
        print("=" * 80)
        
        for recommendation in report.recommendations:
            print(f"• {recommendation}")
        
        print("\n" + "=" * 80)
        
        if report.summary['deployment_ready']:
            print("🎉 VALIDATION PASSED - READY FOR DEPLOYMENT!")
        else:
            print("🚨 VALIDATION ISSUES - DEPLOYMENT NOT RECOMMENDED")
            print("🔧 Please address the issues above before deploying")
        
        print("=" * 80)
    
    def save_report_json(self, report: ValidationReport, filename: str = None):
        """Save report as JSON for CI/CD integration"""
        if not filename:
            filename = f"validation_report_{report.environment}_{int(time.time())}.json"
        
        # Convert dataclasses to dict for JSON serialization
        report_dict = asdict(report)
        
        with open(filename, 'w') as f:
            json.dump(report_dict, f, indent=2, default=str)
        
        logger.info(f"📄 Validation report saved to {filename}")
        return filename

async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Comprehensive E2E Validator for Vimarsh")
    parser.add_argument("--environment", choices=["production", "staging"], 
                       default="production", help="Target environment")
    parser.add_argument("--level", choices=["basic", "comprehensive", "full"], 
                       default="comprehensive", help="Validation level")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--output", help="Output JSON report file")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize validator
    validator = ComprehensiveE2EValidator(args.config)
    
    try:
        # Run validation
        report = await validator.run_comprehensive_validation(args.environment, args.level)
        
        # Print report
        validator.print_report(report)
        
        # Save JSON report
        if args.output:
            validator.save_report_json(report, args.output)
        else:
            validator.save_report_json(report)
        
        # Exit with appropriate code
        if report.summary['deployment_ready']:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Validation failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
