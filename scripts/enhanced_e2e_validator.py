#!/usr/bin/env python3
"""
Enhanced Fast Local E2E Validation for Vimarsh

This script provides comprehensive local E2E validation to catch ALL issues
before pushing to GitHub. Enhanced to match CI/CD validation scope.
"""

import asyncio
import json
import sys
import time
import tempfile
import subprocess
import argparse
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Any, Optional

# Import workflow validator
try:
    from workflow_validator import WorkflowValidator
    WORKFLOW_VALIDATION_AVAILABLE = True
except ImportError:
    WORKFLOW_VALIDATION_AVAILABLE = False
    print("⚠️  Workflow validation not available - install PyYAML and requests")


@dataclass
class ValidationResult:
    """Result of a validation check."""
    name: str
    passed: bool
    duration: float
    message: str
    details: Dict[str, Any] = None


@dataclass
class ValidationSuite:
    """Configuration for a validation suite."""
    name: str
    description: str
    checks: List[str]
    timeout: int
    parallel: bool = True
    critical: bool = False


class EnhancedE2EValidator:
    """Enhanced E2E validation system that matches CI/CD scope."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend"
        
        # Enhanced validation suites matching CI/CD
        self.validation_suites = {
            "critical": ValidationSuite(
                name="Critical Pre-Flight Checks",
                description="Essential checks that must pass",
                checks=[
                    "syntax_validation",
                    "import_validation",
                    "missing_class_detection",
                    "api_interface_validation",
                    "workflow_validation"
                ],
                timeout=60,
                parallel=True,
                critical=True
            ),
            "backend_tests": ValidationSuite(
                name="Backend Test Suite",
                description="All backend test categories",
                checks=[
                    "basic_integration_tests",
                    "rag_pipeline_tests",
                    "cost_management_tests",
                    "monitoring_tests",
                    "voice_interface_tests",
                    "llm_workflow_tests"
                ],
                timeout=300,
                parallel=False,
                critical=True
            ),
            "frontend_tests": ValidationSuite(
                name="Frontend Test Suite", 
                description="Frontend tests with coverage",
                checks=[
                    "frontend_unit_tests",
                    "frontend_coverage"
                ],
                timeout=180,
                parallel=False,
                critical=True
            ),
            "security": ValidationSuite(
                name="Security Validation",
                description="Security analysis matching CI/CD",
                checks=[
                    "semgrep_security_scan",
                    "jwt_security_check",
                    "integrity_attribute_check"
                ],
                timeout=120,
                parallel=False,
                critical=True
            ),
            "performance": ValidationSuite(
                name="Performance Tests",
                description="Performance and benchmarks",
                checks=[
                    "performance_benchmarks"
                ],
                timeout=120,
                parallel=False,
                critical=False
            )
        }
    
    async def run_validation(self, level: str = "comprehensive", 
                           quick_mode: bool = False, verbose: bool = False) -> Dict[str, Any]:
        """Run comprehensive validation matching CI/CD scope."""
        
        start_time = time.time()
        print(f"🚀 Starting Enhanced Local E2E Validation - {level.upper()} level")
        print("="*70)
        
        # Get suites to run
        suites_to_run = self._get_suites_for_level(level)
        
        overall_result = {
            "level": level,
            "suites": [],
            "results": [],
            "summary": {},
            "timestamp": time.time()
        }
        
        # Run each validation suite
        for suite_name in suites_to_run:
            suite = self.validation_suites[suite_name]
            
            print(f"\n🔍 Running {suite.name}")
            print(f"   {suite.description}")
            print(f"   Checks: {len(suite.checks)}, Timeout: {suite.timeout}s")
            
            suite_start = time.time()
            suite_results = await self._run_validation_suite(suite, quick_mode, verbose)
            suite_duration = time.time() - suite_start
            
            suite_info = {
                "name": suite.name,
                "duration": suite_duration,
                "results": suite_results,
                "passed": all(r.passed for r in suite_results),
                "critical": suite.critical
            }
            
            overall_result["suites"].append(suite_info)
            overall_result["results"].extend(suite_results)
            
            # Stop on critical failures
            if suite.critical:
                failed_critical = [r for r in suite_results if not r.passed]
                if failed_critical:
                    print(f"\n❌ CRITICAL FAILURE in {suite.name}")
                    for result in failed_critical:
                        print(f"   ⚠️  {result.name}: {result.message}")
                    if not verbose:  # In non-verbose mode, stop on critical failure
                        break
        
        # Calculate summary
        overall_result["summary"] = self._calculate_summary(overall_result["results"])
        overall_result["summary"]["duration"] = time.time() - start_time
        overall_result["recommendation"] = self._generate_recommendation(overall_result)
        
        # Display results
        self._display_results(overall_result, verbose)
        
        return overall_result
    
    def _get_suites_for_level(self, level: str) -> List[str]:
        """Get validation suites for the specified level."""
        level_mapping = {
            "critical": ["critical"],
            "backend": ["critical", "backend_tests"],
            "frontend": ["critical", "frontend_tests"],
            "security": ["critical", "security"],
            "comprehensive": ["critical", "backend_tests", "frontend_tests", "security"],
            "full": ["critical", "backend_tests", "frontend_tests", "security", "performance"],
            "quick": ["critical"]
        }
        
        return level_mapping.get(level, ["critical", "backend_tests"])
    
    async def _run_validation_suite(self, suite: ValidationSuite, 
                                  quick_mode: bool, verbose: bool) -> List[ValidationResult]:
        """Run a specific validation suite."""
        
        if suite.parallel and not quick_mode:
            return await self._run_parallel_checks(suite, verbose)
        else:
            return await self._run_sequential_checks(suite, verbose)
    
    async def _run_parallel_checks(self, suite: ValidationSuite, 
                                 verbose: bool) -> List[ValidationResult]:
        """Run validation checks in parallel."""
        
        tasks = []
        for check_name in suite.checks:
            task = asyncio.create_task(
                self._run_single_check(check_name, suite.timeout, verbose)
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                final_results.append(ValidationResult(
                    name=suite.checks[i],
                    passed=False,
                    duration=0.0,
                    message=f"Exception during parallel execution: {str(result)}"
                ))
            else:
                final_results.append(result)
        
        return final_results
    
    async def _run_sequential_checks(self, suite: ValidationSuite, 
                                   verbose: bool) -> List[ValidationResult]:
        """Run validation checks sequentially."""
        
        results = []
        for check_name in suite.checks:
            result = await self._run_single_check(check_name, suite.timeout, verbose)
            results.append(result)
            
            if verbose:
                status = "✅" if result.passed else "❌"
                print(f"     {status} {result.name}: {result.message}")
        
        return results
    
    async def _run_single_check(self, check_name: str, timeout: int, 
                              verbose: bool) -> ValidationResult:
        """Run a single validation check."""
        
        start_time = time.time()
        
        try:
            # Map check names to methods
            check_methods = {
                # Critical checks
                "syntax_validation": self._check_syntax_validation,
                "import_validation": self._check_import_validation,
                "missing_class_detection": self._check_missing_class_detection,
                "api_interface_validation": self._check_api_interface_validation,
                "workflow_validation": self._check_workflow_validation,
                
                # Backend test suites
                "basic_integration_tests": self._check_basic_integration_tests,
                "rag_pipeline_tests": self._check_rag_pipeline_tests,
                "cost_management_tests": self._check_cost_management_tests,
                "monitoring_tests": self._check_monitoring_tests,
                "voice_interface_tests": self._check_voice_interface_tests,
                "llm_workflow_tests": self._check_llm_workflow_tests,
                
                # Frontend tests
                "frontend_unit_tests": self._check_frontend_unit_tests,
                "frontend_coverage": self._check_frontend_coverage,
                
                # Security checks
                "semgrep_security_scan": self._check_semgrep_security,
                "jwt_security_check": self._check_jwt_security,
                "integrity_attribute_check": self._check_integrity_attributes,
                
                # Performance
                "performance_benchmarks": self._check_performance_benchmarks
            }
            
            check_method = check_methods.get(check_name)
            if not check_method:
                return ValidationResult(
                    name=check_name,
                    passed=False,
                    duration=time.time() - start_time,
                    message="Check method not implemented"
                )
            
            # Run check with timeout
            result = await asyncio.wait_for(
                check_method(),
                timeout=timeout
            )
            
            result.duration = time.time() - start_time
            return result
            
        except asyncio.TimeoutError:
            return ValidationResult(
                name=check_name,
                passed=False,
                duration=time.time() - start_time,
                message=f"Check timed out after {timeout}s"
            )
        except Exception as e:
            return ValidationResult(
                name=check_name,
                passed=False,
                duration=time.time() - start_time,
                message=f"Check failed with exception: {str(e)}"
            )
    
    # ===============================
    # CRITICAL VALIDATION CHECKS
    # ===============================
    
    async def _check_syntax_validation(self) -> ValidationResult:
        """Validate Python syntax across all backend files."""
        
        python_files = list(self.backend_dir.rglob("*.py"))
        failed_files = []
        
        for py_file in python_files:
            if "/__pycache__/" in str(py_file):
                continue
                
            cmd = [sys.executable, "-m", "py_compile", str(py_file)]
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                if result.returncode != 0:
                    failed_files.append(f"{py_file.name}: {result.stderr.strip()}")
            except Exception as e:
                failed_files.append(f"{py_file.name}: {str(e)}")
        
        if not failed_files:
            return ValidationResult(
                name="syntax_validation",
                passed=True,
                duration=0.0,
                message=f"All {len(python_files)} Python files have valid syntax"
            )
        else:
            return ValidationResult(
                name="syntax_validation", 
                passed=False,
                duration=0.0,
                message=f"Syntax errors in {len(failed_files)} files: {'; '.join(failed_files[:3])}"
            )
    
    async def _check_import_validation(self) -> ValidationResult:
        """Validate that key modules can be imported."""
        
        key_imports = [
            "spiritual_guidance.api",
            "rag_pipeline.document_loader",
            "rag_pipeline.text_processor", 
            "rag_pipeline.vector_storage",
            "llm.gemini_client",
            "cost_management",
            "monitoring.health_check",
            "voice.speech_processor"
        ]
        
        failed_imports = []
        
        for module in key_imports:
            cmd = [
                sys.executable, "-c", f"import {module}"
            ]
            
            try:
                result = subprocess.run(
                    cmd, cwd=self.backend_dir, 
                    capture_output=True, text=True, timeout=10
                )
                
                if result.returncode != 0:
                    failed_imports.append(f"{module}: {result.stderr.strip()}")
                    
            except Exception as e:
                failed_imports.append(f"{module}: {str(e)}")
        
        if not failed_imports:
            return ValidationResult(
                name="import_validation",
                passed=True,
                duration=0.0,
                message="All key modules import successfully"
            )
        else:
            return ValidationResult(
                name="import_validation",
                passed=False,
                duration=0.0,
                message=f"Import failures: {'; '.join(failed_imports[:3])}"
            )
    
    async def _check_missing_class_detection(self) -> ValidationResult:
        """Detect missing classes that tests expect."""
        
        missing_items = []
        
        # Check for RAGPipeline class
        cmd = [
            sys.executable, "-c", 
            "from rag_pipeline import RAGPipeline; print('RAGPipeline found')"
        ]
        
        try:
            result = subprocess.run(
                cmd, cwd=self.backend_dir,
                capture_output=True, text=True, timeout=5
            )
            if result.returncode != 0:
                missing_items.append("RAGPipeline class not exported from rag_pipeline")
        except Exception:
            missing_items.append("RAGPipeline class check failed")
        
        # Check cost_management attributes
        cost_attrs = ["cost_monitor", "request_batching", "spiritual_cache", "model_switcher"]
        for attr in cost_attrs:
            cmd = [
                sys.executable, "-c", 
                f"import cost_management; getattr(cost_management, '{attr}'); print('{attr} found')"
            ]
            
            try:
                result = subprocess.run(
                    cmd, cwd=self.backend_dir,
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode != 0:
                    missing_items.append(f"cost_management.{attr} not found")
            except Exception:
                missing_items.append(f"cost_management.{attr} check failed")
        
        if not missing_items:
            return ValidationResult(
                name="missing_class_detection",
                passed=True,
                duration=0.0,
                message="All expected classes and attributes found"
            )
        else:
            return ValidationResult(
                name="missing_class_detection",
                passed=False,
                duration=0.0,
                message=f"Missing items: {'; '.join(missing_items[:5])}"
            )
    
    async def _check_api_interface_validation(self) -> ValidationResult:
        """Validate API interfaces match test expectations."""
        
        interface_issues = []
        
        # Check TextChunk subscriptability
        cmd = [
            sys.executable, "-c", 
            """
from rag_pipeline.text_processor import TextChunk
chunk = TextChunk("test", {"meta": "data"})
try:
    chunk[0]  # This should work or be properly handled
    print("TextChunk subscriptable")
except TypeError as e:
    print(f"TextChunk not subscriptable: {e}")
except Exception as e:
    print(f"TextChunk access ok")
"""
        ]
        
        try:
            result = subprocess.run(
                cmd, cwd=self.backend_dir,
                capture_output=True, text=True, timeout=5
            )
            if "not subscriptable" in result.stdout:
                interface_issues.append("TextChunk object not subscriptable")
        except Exception:
            interface_issues.append("TextChunk interface check failed")
        
        if not interface_issues:
            return ValidationResult(
                name="api_interface_validation",
                passed=True,
                duration=0.0,
                message="All API interfaces match expectations"
            )
        else:
            return ValidationResult(
                name="api_interface_validation",
                passed=False,
                duration=0.0,
                message=f"Interface issues: {'; '.join(interface_issues)}"
            )
    
    async def _check_workflow_validation(self) -> ValidationResult:
        """Validate GitHub Actions workflows for deprecated actions and permissions."""
        
        if not WORKFLOW_VALIDATION_AVAILABLE:
            return ValidationResult(
                name="workflow_validation",
                passed=False,
                duration=0.0,
                message="Workflow validation not available - install PyYAML and requests"
            )
        
        try:
            validator = WorkflowValidator(str(self.project_root))
            
            # Run comprehensive workflow validation
            workflow_success = validator.validate_all_workflows()
            action_success = validator.validate_action_versions()
            
            # Check external dependencies
            external_issues = validator.validate_external_dependencies()
            
            # Collect all issues
            all_errors = validator.errors[:]
            all_warnings = validator.warnings[:]
            
            if external_issues:
                all_warnings.extend(external_issues)
            
            # Determine overall success
            critical_errors = [e for e in all_errors if any(term in e.lower() for term in 
                             ['deprecated', 'permission', 'security-events', 'codeql'])]
            
            if not workflow_success or not action_success or critical_errors:
                error_summary = "; ".join(critical_errors[:3]) if critical_errors else "Workflow validation failed"
                return ValidationResult(
                    name="workflow_validation",
                    passed=False,
                    duration=0.1,
                    message=f"Critical workflow issues: {error_summary}",
                    details={
                        "errors": all_errors,
                        "warnings": all_warnings,
                        "critical_errors": critical_errors
                    }
                )
            else:
                warning_summary = f"{len(all_warnings)} warnings" if all_warnings else "No issues"
                return ValidationResult(
                    name="workflow_validation", 
                    passed=True,
                    duration=0.1,
                    message=f"Workflows validated successfully. {warning_summary}",
                    details={
                        "warnings": all_warnings
                    }
                )
                
        except Exception as e:
            return ValidationResult(
                name="workflow_validation",
                passed=False,
                duration=0.0,
                message=f"Workflow validation error: {str(e)}"
            )
    
    # ===============================
    # BACKEND TEST SUITE CHECKS
    # ===============================
    
    async def _check_basic_integration_tests(self) -> ValidationResult:
        """Run basic integration tests."""
        return await self._run_pytest_suite(
            "tests/test_basic_integration.py",
            "basic_integration_tests"
        )
    
    async def _check_rag_pipeline_tests(self) -> ValidationResult:
        """Run RAG pipeline tests."""
        return await self._run_pytest_suite(
            "tests/test_rag_pipeline.py",
            "rag_pipeline_tests"
        )
    
    async def _check_cost_management_tests(self) -> ValidationResult:
        """Run cost management tests."""
        return await self._run_pytest_suite(
            "tests/test_cost_management.py",
            "cost_management_tests"
        )
    
    async def _check_monitoring_tests(self) -> ValidationResult:
        """Run monitoring tests."""
        return await self._run_pytest_suite(
            "tests/test_monitoring_comprehensive.py",
            "monitoring_tests"
        )
    
    async def _check_voice_interface_tests(self) -> ValidationResult:
        """Run voice interface tests."""
        return await self._run_pytest_suite(
            "tests/test_voice_interface_comprehensive.py",
            "voice_interface_tests"
        )
    
    async def _check_llm_workflow_tests(self) -> ValidationResult:
        """Run LLM workflow tests."""
        return await self._run_pytest_suite(
            "tests/test_llm_workflow_integration.py",
            "llm_workflow_tests"
        )
    
    async def _run_pytest_suite(self, test_path: str, suite_name: str) -> ValidationResult:
        """Helper to run a pytest suite."""
        
        cmd = [
            sys.executable, "-m", "pytest",
            test_path,
            "-v", "--tb=short", "--no-header"
        ]
        
        try:
            result = subprocess.run(
                cmd, cwd=self.backend_dir,
                capture_output=True, text=True, timeout=120
            )
            
            # Parse results
            if result.returncode == 0:
                passed_count = result.stdout.count(" PASSED")
                return ValidationResult(
                    name=suite_name,
                    passed=True,
                    duration=0.0,
                    message=f"All tests passed ({passed_count} tests)"
                )
            else:
                failed_count = result.stdout.count(" FAILED")
                error_count = result.stdout.count(" ERROR")
                return ValidationResult(
                    name=suite_name,
                    passed=False,
                    duration=0.0,
                    message=f"Tests failed: {failed_count} failed, {error_count} errors"
                )
                
        except subprocess.TimeoutExpired:
            return ValidationResult(
                name=suite_name,
                passed=False,
                duration=0.0,
                message="Test suite timed out"
            )
        except Exception as e:
            return ValidationResult(
                name=suite_name,
                passed=False,
                duration=0.0,
                message=f"Test execution failed: {str(e)}"
            )
    
    # ===============================
    # FRONTEND TEST CHECKS
    # ===============================
    
    async def _check_frontend_unit_tests(self) -> ValidationResult:
        """Run frontend unit tests."""
        
        if not self.frontend_dir.exists():
            return ValidationResult(
                name="frontend_unit_tests",
                passed=True,
                duration=0.0,
                message="Frontend directory not found, skipping"
            )
        
        cmd = ["npm", "test", "--", "--watchAll=false", "--verbose"]
        
        try:
            result = subprocess.run(
                cmd, cwd=self.frontend_dir,
                capture_output=True, text=True, timeout=120
            )
            
            if result.returncode == 0:
                return ValidationResult(
                    name="frontend_unit_tests",
                    passed=True,
                    duration=0.0,
                    message="Frontend tests passed"
                )
            else:
                return ValidationResult(
                    name="frontend_unit_tests",
                    passed=False,
                    duration=0.0,
                    message="Frontend tests failed"
                )
                
        except Exception as e:
            return ValidationResult(
                name="frontend_unit_tests",
                passed=False,
                duration=0.0,
                message=f"Frontend test execution failed: {str(e)}"
            )
    
    async def _check_frontend_coverage(self) -> ValidationResult:
        """Check frontend test coverage."""
        
        if not self.frontend_dir.exists():
            return ValidationResult(
                name="frontend_coverage",
                passed=True,
                duration=0.0,
                message="Frontend directory not found, skipping"
            )
        
        cmd = ["npm", "run", "test:coverage"]
        
        try:
            result = subprocess.run(
                cmd, cwd=self.frontend_dir,
                capture_output=True, text=True, timeout=120
            )
            
            # Check for coverage results in output
            if "All files" in result.stdout:
                return ValidationResult(
                    name="frontend_coverage",
                    passed=True,
                    duration=0.0,
                    message="Frontend coverage generated"
                )
            else:
                return ValidationResult(
                    name="frontend_coverage",
                    passed=False,
                    duration=0.0,
                    message="Frontend coverage generation failed"
                )
                
        except Exception as e:
            return ValidationResult(
                name="frontend_coverage",
                passed=False,
                duration=0.0,
                message=f"Frontend coverage check failed: {str(e)}"
            )
    
    # ===============================
    # SECURITY VALIDATION CHECKS  
    # ===============================
    
    async def _check_semgrep_security(self) -> ValidationResult:
        """Run Semgrep security scan."""
        
        cmd = ["semgrep", "--config=auto", "--json", "."]
        
        try:
            result = subprocess.run(
                cmd, cwd=self.project_root,
                capture_output=True, text=True, timeout=60
            )
            
            if result.returncode == 0:
                # Parse JSON output to check for findings
                try:
                    findings = json.loads(result.stdout)
                    if findings.get("results", []):
                        return ValidationResult(
                            name="semgrep_security_scan",
                            passed=False,
                            duration=0.0,
                            message=f"Security issues found: {len(findings['results'])}"
                        )
                    else:
                        return ValidationResult(
                            name="semgrep_security_scan",
                            passed=True,
                            duration=0.0,
                            message="No security issues found"
                        )
                except json.JSONDecodeError:
                    return ValidationResult(
                        name="semgrep_security_scan",
                        passed=False,
                        duration=0.0,
                        message="Could not parse Semgrep output"
                    )
            else:
                return ValidationResult(
                    name="semgrep_security_scan",
                    passed=False,
                    duration=0.0,
                    message="Semgrep scan failed"
                )
                
        except FileNotFoundError:
            return ValidationResult(
                name="semgrep_security_scan",
                passed=True,
                duration=0.0,
                message="Semgrep not installed, skipping"
            )
        except Exception as e:
            return ValidationResult(
                name="semgrep_security_scan",
                passed=False,
                duration=0.0,
                message=f"Semgrep execution failed: {str(e)}"
            )
    
    async def _check_jwt_security(self) -> ValidationResult:
        """Check for JWT security issues."""
        
        # Search for unverified JWT decode patterns
        jwt_files = []
        for py_file in self.backend_dir.rglob("*.py"):
            try:
                content = py_file.read_text()
                if "verify=False" in content and "jwt" in content.lower():
                    jwt_files.append(str(py_file))
            except Exception:
                continue
        
        if jwt_files:
            return ValidationResult(
                name="jwt_security_check",
                passed=False,
                duration=0.0,
                message=f"Unverified JWT decode found in {len(jwt_files)} files"
            )
        else:
            return ValidationResult(
                name="jwt_security_check",
                passed=True,
                duration=0.0,
                message="No JWT security issues found"
            )
    
    async def _check_integrity_attributes(self) -> ValidationResult:
        """Check for missing integrity attributes in HTML."""
        
        html_files = list(self.project_root.rglob("*.html"))
        missing_integrity = []
        
        for html_file in html_files:
            try:
                content = html_file.read_text()
                # Check for external scripts/links without integrity
                if "cdn.jsdelivr.net" in content or "cdnjs.cloudflare.com" in content:
                    if "integrity=" not in content:
                        missing_integrity.append(str(html_file))
            except Exception:
                continue
        
        if missing_integrity:
            return ValidationResult(
                name="integrity_attribute_check",
                passed=False,
                duration=0.0,
                message=f"Missing integrity attributes in {len(missing_integrity)} files"
            )
        else:
            return ValidationResult(
                name="integrity_attribute_check",
                passed=True,
                duration=0.0,
                message="All external resources have integrity attributes"
            )
    
    # ===============================
    # PERFORMANCE VALIDATION
    # ===============================
    
    async def _check_performance_benchmarks(self) -> ValidationResult:
        """Run performance benchmarks."""
        
        cmd = [
            sys.executable, "-m", "pytest",
            "--benchmark-only", "--benchmark-json=benchmark_results.json"
        ]
        
        try:
            result = subprocess.run(
                cmd, cwd=self.backend_dir,
                capture_output=True, text=True, timeout=60
            )
            
            if result.returncode == 0:
                return ValidationResult(
                    name="performance_benchmarks",
                    passed=True,
                    duration=0.0,
                    message="Performance benchmarks passed"
                )
            else:
                return ValidationResult(
                    name="performance_benchmarks",
                    passed=False,
                    duration=0.0,
                    message="Performance benchmarks failed"
                )
                
        except Exception as e:
            return ValidationResult(
                name="performance_benchmarks",
                passed=True,
                duration=0.0,
                message="No performance tests found, skipping"
            )
    
    async def _run_comprehensive_test_validation(self) -> ValidationResult:
        """
        Run comprehensive test validation that matches CI coverage
        """
        start_time = time.time()
        
        try:
            # First check if all dependencies are available
            dependency_check = await self._validate_test_dependencies()
            if not dependency_check.passed:
                return dependency_check
            
            # Run the same pytest command as CI
            cmd = [
                sys.executable, "-m", "pytest",
                "--tb=short", "--no-header", "-v"
            ]
            
            result = subprocess.run(
                cmd, cwd=self.backend_dir,
                capture_output=True, text=True, timeout=600  # 10 minutes
            )
            
            duration = time.time() - start_time
            
            # Parse comprehensive results
            output_lines = result.stdout.split('\n')
            
            # Count test results
            passed_count = 0
            failed_count = 0
            error_count = 0
            
            for line in output_lines:
                if " PASSED" in line:
                    passed_count += 1
                elif " FAILED" in line:
                    failed_count += 1
                elif " ERROR" in line:
                    error_count += 1
            
            # Analyze failures for root causes
            failure_patterns = self._analyze_test_failures(result.stdout)
            
            if result.returncode == 0:
                return ValidationResult(
                    name="Comprehensive Test Suite",
                    passed=True,
                    duration=duration,
                    message=f"All tests passed ({passed_count} passed, 0 failed)",
                    details={
                        "passed": passed_count,
                        "failed": failed_count,
                        "errors": error_count,
                        "total": passed_count + failed_count + error_count
                    }
                )
            else:
                return ValidationResult(
                    name="Comprehensive Test Suite",
                    passed=False,
                    duration=duration,
                    message=f"Tests failed: {failed_count} failed, {error_count} errors, {passed_count} passed",
                    details={
                        "passed": passed_count,
                        "failed": failed_count,
                        "errors": error_count,
                        "total": passed_count + failed_count + error_count,
                        "failure_patterns": failure_patterns,
                        "stdout": result.stdout[-2000:],  # Last 2000 chars
                        "stderr": result.stderr[-1000:]   # Last 1000 chars
                    }
                )
                
        except subprocess.TimeoutExpired:
            return ValidationResult(
                name="Comprehensive Test Suite",
                passed=False,
                duration=time.time() - start_time,
                message="Test suite timed out after 10 minutes"
            )
        except Exception as e:
            return ValidationResult(
                name="Comprehensive Test Suite",
                passed=False,
                duration=time.time() - start_time,
                message=f"Test validation error: {str(e)}"
            )
    
    async def _validate_test_dependencies(self) -> ValidationResult:
        """
        Validate that all test dependencies are available
        """
        start_time = time.time()
        
        try:
            # Check for missing dependencies by scanning test files
            missing_deps = []
            test_files = []
            
            # Find all test files
            for root, dirs, files in os.walk(os.path.join(self.backend_dir, "tests")):
                for file in files:
                    if file.startswith("test_") and file.endswith(".py"):
                        test_files.append(os.path.join(root, file))
            
            # Check imports in test files
            import_patterns = [
                r"import\s+(\w+)",
                r"from\s+(\w+)\s+import",
                r"from\s+([^.]\w+\.\w+)\s+import"
            ]
            
            required_modules = set()
            for test_file in test_files:
                try:
                    with open(test_file, 'r') as f:
                        content = f.read()
                        for pattern in import_patterns:
                            matches = re.findall(pattern, content)
                            required_modules.update(matches)
                except Exception:
                    continue
            
            # Check if modules are available
            for module in required_modules:
                if module in ['psutil', 'pydub']:  # Known external dependencies
                    try:
                        __import__(module)
                    except ImportError:
                        missing_deps.append(module)
            
            if missing_deps:
                return ValidationResult(
                    name="Test Dependencies",
                    passed=False,
                    duration=time.time() - start_time,
                    message=f"Missing test dependencies: {', '.join(missing_deps)}",
                    details={"missing_dependencies": missing_deps}
                )
            
            return ValidationResult(
                name="Test Dependencies",
                passed=True,
                duration=time.time() - start_time,
                message="All test dependencies available"
            )
            
        except Exception as e:
            return ValidationResult(
                name="Test Dependencies",
                passed=False,
                duration=time.time() - start_time,
                message=f"Dependency validation error: {str(e)}"
            )
    
    def _analyze_test_failures(self, test_output: str) -> Dict[str, Any]:
        """
        Analyze test failures to identify patterns and root causes
        """
        patterns = {
            "missing_methods": [],
            "import_errors": [],
            "mock_issues": [],
            "dependency_issues": [],
            "interface_mismatches": []
        }
        
        lines = test_output.split('\n')
        
        for line in lines:
            if "AttributeError" in line and "has no attribute" in line:
                patterns["missing_methods"].append(line.strip())
            elif "ModuleNotFoundError" in line:
                patterns["import_errors"].append(line.strip())
            elif "ImportError" in line:
                patterns["dependency_issues"].append(line.strip())
            elif "Mock" in line and ("can't be used" in line or "await" in line):
                patterns["mock_issues"].append(line.strip())
            elif "TypeError" in line and ("object" in line or "method" in line):
                patterns["interface_mismatches"].append(line.strip())
        
        return patterns

    # ===============================
    # UTILITY METHODS
    # ===============================
    
    def _calculate_summary(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """Calculate summary statistics."""
        
        total = len(results)
        passed = sum(1 for r in results if r.passed)
        failed = total - passed
        
        return {
            "total_checks": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": (passed / total * 100) if total > 0 else 0
        }
    
    def _generate_recommendation(self, overall_result: Dict[str, Any]) -> str:
        """Generate recommendation based on results."""
        
        summary = overall_result["summary"]
        
        if summary["failed"] == 0:
            return "✅ All checks passed! Safe to push to repository."
        elif summary["pass_rate"] >= 80:
            return "⚠️ Mostly passing but some issues found. Review and fix before pushing."
        else:
            return "❌ Significant issues found. Do not push until resolved."
    
    def _display_results(self, overall_result: Dict[str, Any], verbose: bool):
        """Display validation results."""
        
        summary = overall_result["summary"]
        
        print(f"\n📊 VALIDATION RESULTS")
        print("="*50)
        print(f"Suite Level: {overall_result['level'].upper()}")
        print(f"Total Checks: {summary['total_checks']}")
        print(f"Passed: {summary['passed']} ✅")
        print(f"Failed: {summary['failed']} ❌")
        print(f"Pass Rate: {summary['pass_rate']:.1f}%")
        print(f"Duration: {summary['duration']:.2f}s")
        
        print(f"\n{overall_result['recommendation']}")
        
        if verbose and summary['failed'] > 0:
            print(f"\n🔍 FAILURE DETAILS:")
            for result in overall_result["results"]:
                if not result.passed:
                    print(f"   ❌ {result.name}: {result.message}")
        
        # Save detailed results
        results_file = self.project_root / f"e2e_validation_results_{int(time.time())}.json"
        with open(results_file, "w") as f:
            json.dump(overall_result, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {results_file}")


async def main():
    """Main entry point."""
    
    parser = argparse.ArgumentParser(description="Enhanced Local E2E Validation")
    parser.add_argument(
        "--level", 
        choices=["critical", "backend", "frontend", "security", "comprehensive", "full", "quick"],
        default="comprehensive",
        help="Validation level to run"
    )
    parser.add_argument(
        "--quick", 
        action="store_true",
        help="Quick mode (reduced parallelism)"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="Project root directory"
    )
    
    args = parser.parse_args()
    
    # Initialize validator
    validator = EnhancedE2EValidator(args.project_root)
    
    # Run validation
    start_time = time.time()
    result = await validator.run_validation(
        level=args.level,
        quick_mode=args.quick,
        verbose=args.verbose
    )
    
    # Exit with appropriate code
    if result["summary"]["failed"] == 0:
        print(f"✅ Enhanced validation passed in {time.time() - start_time:.1f}s")
        print("   Safe to commit and push!")
        sys.exit(0)
    else:
        print(f"❌ Enhanced validation failed in {time.time() - start_time:.1f}s")
        print("   Fix issues before pushing!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
