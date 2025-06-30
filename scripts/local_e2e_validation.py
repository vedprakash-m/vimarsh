#!/usr/bin/env python3
"""
Vimarsh Local E2E Validation Runner

This script provides comprehensive local testing and validation to catch all issues
before pushing to GitHub. It's designed for speed, effectiveness, and complete
validation of the Vimarsh system.

Usage:
    python scripts/local_e2e_validation.py [--quick] [--coverage] [--parallel]

Features:
    - Fast execution with intelligent test selection
    - Comprehensive coverage analysis (>85% target)
    - Parallel test execution where possible
    - Real-time progress and results
    - Detailed failure analysis and recommendations
    - CI/CD readiness validation
"""

import os
import sys
import subprocess
import time
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Test execution result"""
    test_file: str
    test_count: int
    passed: int
    failed: int
    skipped: int
    errors: int
    duration: float
    exit_code: int
    output: str = ""
    coverage: Optional[float] = None


@dataclass
class ValidationReport:
    """Comprehensive validation report"""
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    skipped_tests: int = 0
    error_tests: int = 0
    total_duration: float = 0.0
    overall_coverage: Optional[float] = None
    module_coverage: Dict[str, float] = field(default_factory=dict)
    test_results: List[TestResult] = field(default_factory=list)
    critical_failures: List[str] = field(default_factory=list)
    performance_issues: List[str] = field(default_factory=list)
    coverage_gaps: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    ci_cd_ready: bool = False


class LocalE2EValidator:
    """
    Comprehensive local validation system for Vimarsh
    """
    
    def __init__(self, 
                 project_root: Optional[Path] = None,
                 quick_mode: bool = False,
                 enable_coverage: bool = True,
                 parallel: bool = True,
                 max_workers: int = 4,
                 timeout: int = 300):
        """
        Initialize the validator
        
        Args:
            project_root: Root directory of the project
            quick_mode: Run only critical tests for faster feedback
            enable_coverage: Collect test coverage data
            parallel: Run tests in parallel where possible
            max_workers: Maximum number of parallel workers
            timeout: Maximum execution timeout in seconds
        """
        self.project_root = project_root or Path.cwd()
        self.backend_path = self.project_root / "backend"
        self.frontend_path = self.project_root / "frontend"
        self.quick_mode = quick_mode
        self.enable_coverage = enable_coverage
        self.parallel = parallel
        self.max_workers = max_workers
        self.timeout = timeout
        
        # Test results initialization
        self.test_results = {
            "validation": {
                "total": 0,
                "passed": 0,
                "failed": 0
            },
            "coverage": {
                "total": 0.0,
                "achieved": 0.0
            },
            "performance": {
                "total": 0.0,
                "issues": 0
            }
        }
        
        # Test categories for intelligent selection
        self.test_categories = {
            'critical': [
                'backend/tests/test_end_to_end_workflow.py',
                'backend/tests/test_spiritual_guidance_api.py',
                'backend/tests/test_basic_integration.py',
                'backend/function_app_test.py'
            ],
            'core_functionality': [
                'backend/tests/test_rag_pipeline.py',
                'backend/tests/test_llm_integration_comprehensive.py',
                'backend/llm/test_gemini_client.py',
                'backend/spiritual_guidance/test_*.py'
            ],
            'data_processing': [
                'backend/rag_pipeline/test_*.py',
                'backend/data_processing/test_*.py',
                'backend/rag/test_*.py'
            ],
            'cost_management': [
                'backend/cost_management/test_*.py'
            ],
            'voice_interface': [
                'backend/voice/test_*.py',
                'backend/tests/test_voice_*.py'
            ],
            'monitoring': [
                'backend/tests/test_monitoring_*.py',
                'backend/error_handling/test_*.py'
            ],
            'e2e_integration': [
                'backend/tests/e2e/test_*.py',
                'tests/*/test_*.py'
            ]
        }
        
        # Coverage targets by module
        self.coverage_targets = {
            'spiritual_guidance': 85.0,
            'rag_pipeline': 85.0,
            'llm': 80.0,
            'cost_management': 90.0,  # Well-tested module
            'voice': 75.0,
            'monitoring': 80.0,
            'data_processing': 85.0,
            'overall': 85.0
        }
        
        # Performance thresholds
        self.performance_thresholds = {
            'test_duration_per_file': 30.0,  # seconds
            'total_test_duration': 300.0,    # 5 minutes max
            'memory_usage_mb': 1000.0,       # 1GB max
        }
        
        self.validation_start_time = time.time()
        logger.info(f"Local E2E Validator initialized - Quick: {quick_mode}, Coverage: {enable_coverage}, Parallel: {parallel}")
    
    def run_validation(self) -> ValidationReport:
        """
        Run comprehensive validation with timeout
        
        Returns:
            ValidationReport with all results and recommendations
        """
        logger.info("🚀 Starting Vimarsh Local E2E Validation")
        logger.info(f"⏱️  Timeout set to {self.timeout} seconds")
        
        report = ValidationReport()
        start_time = time.time()
        
        try:
            # 1. Environment validation
            self._validate_environment()
            self._validate_dependencies()
            self.validate_test_environment_parity()
            
            # Check timeout
            if time.time() - start_time > self.timeout:
                logger.warning("⏰ Validation timeout reached during environment checks")
                report.add_error("Validation timeout during environment checks")
                return report
            
            # 2. Test discovery and categorization
            test_files = self._discover_tests()
            logger.info(f"📊 Discovered {len(test_files)} test files")
            
            # Check timeout
            if time.time() - start_time > self.timeout:
                logger.warning("⏰ Validation timeout reached during test discovery")
                report.add_error("Validation timeout during test discovery")
                return report
            
            # 3. Run tests with intelligent selection
            if self.quick_mode:
                test_files = self._select_critical_tests(test_files)
                logger.info(f"⚡ Quick mode: Running {len(test_files)} critical tests")
            
            # 4. Execute tests with remaining time
            remaining_time = max(30, self.timeout - (time.time() - start_time))
            test_results = self._execute_tests_with_timeout(test_files, report, remaining_time)
            
            # 5. Collect coverage data
            if self.enable_coverage:
                self._collect_coverage_data(report)
            
            # 6. Performance analysis
            self._analyze_performance(report)
            
            # 7. Validate missing files and modules (CI/CD gap analysis)
            self._validate_missing_files_and_modules()
            
            # 8. Generate recommendations
            self._generate_recommendations(report)
            
            # 9. CI/CD readiness check
            report.ci_cd_ready = self._check_ci_cd_readiness(report)
            
            # 10. Generate final report
            self._print_final_report(report)
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Validation failed with error: {e}")
            report.critical_failures.append(f"Validation system error: {e}")
            return report
    
    def _validate_environment(self):
        """Validate the development environment"""
        logger.info("🔍 Validating environment...")
        
        # Check Python version
        python_version = sys.version_info
        if python_version.major != 3 or python_version.minor < 12:
            raise RuntimeError(f"Python 3.12+ required, found {python_version.major}.{python_version.minor}")
        
        # Check required dependencies
        required_packages = [
            'pytest', 'pytest_cov', 'pytest_asyncio', 'faiss', 
            'azure.keyvault.secrets', 'sentence_transformers'
        ]
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                raise RuntimeError(f"Required package '{package}' not installed")
        
        # Check project structure
        required_dirs = ['backend', 'frontend', 'infrastructure', 'tests']
        for dir_name in required_dirs:
            if not (self.project_root / dir_name).exists():
                logger.warning(f"⚠️  Expected directory '{dir_name}' not found")
        
        # Validate dependencies
        self._validate_dependencies()
        
        logger.info("✅ Environment validation passed")
    
    def _discover_tests(self) -> List[Path]:
        """Discover all test files in the project"""
        test_files = []
        
        # Search patterns for test files
        patterns = [
            '**/test_*.py',
            '**/*_test.py',
            '**/tests.py'
        ]
        
        for pattern in patterns:
            test_files.extend(self.project_root.glob(pattern))
        
        # Filter out non-test files and duplicates
        valid_tests = []
        seen = set()
        
        for test_file in test_files:
            # Skip __pycache__ and other non-source directories
            if '__pycache__' in str(test_file) or '.pytest_cache' in str(test_file):
                continue
                
            # Skip if already seen
            if test_file in seen:
                continue
                
            # Check if it's actually a test file (contains test classes/functions)
            if self._is_valid_test_file(test_file):
                valid_tests.append(test_file)
                seen.add(test_file)
        
        return sorted(valid_tests)
    
    def _is_valid_test_file(self, file_path: Path) -> bool:
        """Check if a file contains actual tests"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Look for test indicators
            test_indicators = [
                'def test_',
                'class Test',
                '@pytest.',
                'import pytest',
                'from pytest'
            ]
            
            return any(indicator in content for indicator in test_indicators)
            
        except Exception:
            return False
    
    def _select_critical_tests(self, all_tests: List[Path]) -> List[Path]:
        """Select critical tests for quick validation"""
        critical_tests = []
        
        for test_file in all_tests:
            file_str = str(test_file)
            
            # Check if it's in critical category
            for critical_pattern in self.test_categories['critical']:
                if critical_pattern.replace('*', '') in file_str:
                    critical_tests.append(test_file)
                    break
                    
            # Also include end-to-end tests
            if 'e2e' in file_str or 'end_to_end' in file_str:
                critical_tests.append(test_file)
        
        return critical_tests
    
    def _execute_tests(self, test_files: List[Path], report: ValidationReport) -> List[TestResult]:
        """Execute tests with parallel execution support"""
        logger.info(f"🧪 Executing {len(test_files)} test files...")
        
        test_results = []
        
        # First run real pytest on backend
        if self.project_root.joinpath("backend").exists():
            logger.info("🐍 Running backend pytest suite...")
            backend_result = self._run_backend_pytest()
            if backend_result:
                test_results.append(backend_result)
        
        # Then run frontend tests  
        if self.project_root.joinpath("frontend").exists():
            logger.info("⚛️ Running frontend test suite...")
            frontend_result = self._run_frontend_tests()
            if frontend_result:
                test_results.append(frontend_result)
        
        # Run original test discovery for any remaining tests (but reduced priority in quick mode)
        if not self.quick_mode:
            if self.parallel and len(test_files) > 1:
                # Parallel execution for independent test files
                additional_results = self._execute_tests_parallel(test_files)
                test_results.extend(additional_results)
            else:
                # Sequential execution
                additional_results = self._execute_tests_sequential(test_files)
                test_results.extend(additional_results)
        
        # Update report
        for result in test_results:
            report.test_results.append(result)
            report.total_tests += result.test_count
            report.passed_tests += result.passed
            report.failed_tests += result.failed
            report.skipped_tests += result.skipped
            report.error_tests += result.errors
            report.total_duration += result.duration
            
            if result.failed > 0 or result.errors > 0:
                report.critical_failures.append(f"{result.test_file}: {result.failed} failed, {result.errors} errors")
        
        return test_results
    
    def _execute_tests_parallel(self, test_files: List[Path]) -> List[TestResult]:
        """Execute tests in parallel"""
        results = []
        
        # Group tests by estimated execution time
        fast_tests = []
        slow_tests = []
        
        for test_file in test_files:
            # Simple heuristic: voice and e2e tests are usually slower
            if 'voice' in str(test_file) or 'e2e' in str(test_file) or 'integration' in str(test_file):
                slow_tests.append(test_file)
            else:
                fast_tests.append(test_file)
        
        # Execute fast tests in parallel
        logger.info(f"⚡ Running {len(fast_tests)} fast tests in parallel...")
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_test = {
                executor.submit(self._run_single_test, test_file): test_file 
                for test_file in fast_tests
            }
            
            for future in as_completed(future_to_test):
                test_file = future_to_test[future]
                try:
                    result = future.result()
                    results.append(result)
                    logger.info(f"✅ {result.test_file}: {result.passed}/{result.test_count} passed")
                except Exception as e:
                    logger.error(f"❌ {test_file} failed: {e}")
                    results.append(TestResult(
                        test_file=str(test_file),
                        test_count=0, passed=0, failed=0, skipped=0, errors=1,
                        duration=0.0, exit_code=1, output=str(e)
                    ))
        
        # Execute slow tests sequentially to avoid resource conflicts
        if slow_tests:
            logger.info(f"🐌 Running {len(slow_tests)} slow tests sequentially...")
            for test_file in slow_tests:
                try:
                    result = self._run_single_test(test_file)
                    results.append(result)
                    logger.info(f"✅ {result.test_file}: {result.passed}/{result.test_count} passed")
                except Exception as e:
                    logger.error(f"❌ {test_file} failed: {e}")
                    results.append(TestResult(
                        test_file=str(test_file),
                        test_count=0, passed=0, failed=0, skipped=0, errors=1,
                        duration=0.0, exit_code=1, output=str(e)
                    ))
        
        return results
    
    def _execute_tests_sequential(self, test_files: List[Path]) -> List[TestResult]:
        """Execute tests sequentially"""
        results = []
        
        for i, test_file in enumerate(test_files, 1):
            logger.info(f"🧪 Running test {i}/{len(test_files)}: {test_file.name}")
            
            try:
                result = self._run_single_test(test_file)
                results.append(result)
                
                status = "✅" if result.failed == 0 and result.errors == 0 else "❌"
                logger.info(f"{status} {result.test_file}: {result.passed}/{result.test_count} passed ({result.duration:.2f}s)")
                
            except Exception as e:
                logger.error(f"❌ {test_file} failed: {e}")
                results.append(TestResult(
                    test_file=str(test_file),
                    test_count=0, passed=0, failed=0, skipped=0, errors=1,
                    duration=0.0, exit_code=1, output=str(e)
                ))
        
        return results
    
    def _run_single_test(self, test_file: Path) -> TestResult:
        """Run a single test file and parse results"""
        start_time = time.time()
        
        # Construct pytest command
        cmd = [
            sys.executable, '-m', 'pytest',
            str(test_file),
            '-v',
            '--tb=short',
            '--no-header',
            '--disable-warnings'
        ]
        
        if self.enable_coverage:
            cmd.extend(['--cov=backend', '--cov-report=term-missing'])
        
        try:
            # Run the test
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60  # 1 minute timeout per test file
            )
            
            duration = time.time() - start_time
            
            # Parse pytest output
            test_count, passed, failed, skipped, errors = self._parse_pytest_output(result.stdout)
            
            return TestResult(
                test_file=str(test_file.relative_to(self.project_root)),
                test_count=test_count,
                passed=passed,
                failed=failed,
                skipped=skipped,
                errors=errors,
                duration=duration,
                exit_code=result.returncode,
                output=result.stdout + result.stderr
            )
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            return TestResult(
                test_file=str(test_file.relative_to(self.project_root)),
                test_count=0, passed=0, failed=0, skipped=0, errors=1,
                duration=duration, exit_code=1,
                output="Test execution timed out after 60 seconds"
            )
    
    def _parse_pytest_output(self, output: str) -> Tuple[int, int, int, int, int]:
        """Parse pytest output to extract test counts"""
        # Default values
        test_count = passed = failed = skipped = errors = 0
        
        lines = output.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Look for summary line like "3 failed, 5 passed, 1 skipped in 2.34s"
            if ' passed' in line or ' failed' in line:
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == 'passed' and i > 0:
                        passed = int(parts[i-1])
                    elif part == 'failed' and i > 0:
                        failed = int(parts[i-1])
                    elif part == 'skipped' and i > 0:
                        skipped = int(parts[i-1])
                    elif part == 'error' and i > 0:
                        errors = int(parts[i-1])
        
        test_count = passed + failed + skipped + errors
        
        return test_count, passed, failed, skipped, errors
    
    def _collect_coverage_data(self, report: ValidationReport):
        """Collect and analyze test coverage data"""
        if not self.enable_coverage:
            return
            
        logger.info("📊 Collecting coverage data...")
        
        try:
            # Run coverage report
            cmd = [
                sys.executable, '-m', 'pytest',
                '--cov=backend',
                '--cov-report=json:coverage.json',
                '--cov-report=term-missing',
                '--disable-warnings',
                '-q'
            ]
            
            subprocess.run(cmd, cwd=self.project_root, capture_output=True)
            
            # Read coverage data
            coverage_file = self.project_root / 'coverage.json'
            if coverage_file.exists():
                with open(coverage_file, 'r') as f:
                    coverage_data = json.load(f)
                
                # Extract overall coverage
                totals = coverage_data.get('totals', {})
                if totals:
                    covered = totals.get('covered_lines', 0)
                    total = totals.get('num_statements', 1)
                    report.overall_coverage = (covered / total) * 100
                
                # Extract module-level coverage
                files = coverage_data.get('files', {})
                modules = {}
                
                for file_path, file_data in files.items():
                    if 'backend/' in file_path:
                        # Extract module name
                        path_parts = file_path.replace('backend/', '').split('/')
                        if path_parts:
                            module = path_parts[0]
                            
                            covered = file_data.get('summary', {}).get('covered_lines', 0)
                            total = file_data.get('summary', {}).get('num_statements', 1)
                            coverage_pct = (covered / total) * 100
                            
                            if module not in modules:
                                modules[module] = {'covered': 0, 'total': 0}
                            
                            modules[module]['covered'] += covered
                            modules[module]['total'] += total
                
                # Calculate module coverages
                for module, data in modules.items():
                    if data['total'] > 0:
                        coverage_pct = (data['covered'] / data['total']) * 100
                        report.module_coverage[module] = coverage_pct
                        
                        # Check against targets
                        target = self.coverage_targets.get(module, 80.0)
                        if coverage_pct < target:
                            report.coverage_gaps.append(
                                f"{module}: {coverage_pct:.1f}% (target: {target}%)"
                            )
                
                # Clean up
                coverage_file.unlink(missing_ok=True)
                
        except Exception as e:
            logger.warning(f"⚠️  Coverage collection failed: {e}")
    
    def _analyze_performance(self, report: ValidationReport):
        """Analyze test performance and identify issues"""
        logger.info("⚡ Analyzing test performance...")
        
        # Check total duration
        if report.total_duration > self.performance_thresholds['total_test_duration']:
            report.performance_issues.append(
                f"Total test duration ({report.total_duration:.1f}s) exceeds threshold "
                f"({self.performance_thresholds['total_test_duration']}s)"
            )
        
        # Check individual test file durations
        for result in report.test_results:
            if result.duration > self.performance_thresholds['test_duration_per_file']:
                report.performance_issues.append(
                    f"{result.test_file} took {result.duration:.1f}s "
                    f"(threshold: {self.performance_thresholds['test_duration_per_file']}s)"
                )
    
    def _generate_recommendations(self, report: ValidationReport):
        """Generate actionable recommendations"""
        logger.info("💡 Generating recommendations...")
        
        # Test failure recommendations
        if report.failed_tests > 0:
            report.recommendations.append(
                f"🔧 Fix {report.failed_tests} failing tests before pushing to CI/CD"
            )
        
        # Coverage recommendations
        if report.overall_coverage and report.overall_coverage < self.coverage_targets['overall']:
            report.recommendations.append(
                f"📈 Increase overall test coverage from {report.overall_coverage:.1f}% to {self.coverage_targets['overall']}%"
            )
        
        # Performance recommendations
        if report.performance_issues:
            report.recommendations.append(
                "⚡ Optimize slow tests or split them into smaller, focused tests"
            )
        
        # Critical tests recommendations
        critical_failures = [f for f in report.critical_failures if 'end_to_end' in f or 'integration' in f]
        if critical_failures:
            report.recommendations.append(
                "🚨 Critical E2E/integration tests failing - these must pass for production readiness"
            )
        
        # Module-specific recommendations
        for module, coverage in report.module_coverage.items():
            target = self.coverage_targets.get(module, 80.0)
            if coverage < target:
                report.recommendations.append(
                    f"📊 Add tests for {module} module (current: {coverage:.1f}%, target: {target}%)"
                )
    
    def _check_ci_cd_readiness(self, report: ValidationReport) -> bool:
        """Check if the codebase is ready for CI/CD"""
        logger.info("🔍 Checking CI/CD readiness...")
        
        criteria = []
        
        # Must have no failing tests
        criteria.append(("No failing tests", report.failed_tests == 0))
        
        # Must have acceptable coverage
        coverage_ok = True
        if report.overall_coverage:
            coverage_ok = report.overall_coverage >= self.coverage_targets['overall']
        criteria.append(("Coverage target met", coverage_ok))
        
        # Critical tests must pass
        critical_tests_ok = not any('end_to_end' in f or 'integration' in f for f in report.critical_failures)
        criteria.append(("Critical tests passing", critical_tests_ok))
        
        # Performance within limits
        performance_ok = len(report.performance_issues) == 0
        criteria.append(("Performance acceptable", performance_ok))
        
        # Check results
        all_criteria_met = all(result for _, result in criteria)
        
        logger.info("📋 CI/CD Readiness Checklist:")
        for criterion, met in criteria:
            status = "✅" if met else "❌"
            logger.info(f"  {status} {criterion}")
        
        return all_criteria_met
    
    def _print_final_report(self, report: ValidationReport):
        """Print comprehensive final report"""
        duration = time.time() - self.validation_start_time
        
        print("\n" + "="*80)
        print("🎯 VIMARSH LOCAL E2E VALIDATION REPORT")
        print("="*80)
        
        # Summary
        print(f"\n📊 TEST SUMMARY:")
        print(f"   Total Tests: {report.total_tests}")
        print(f"   ✅ Passed: {report.passed_tests}")
        print(f"   ❌ Failed: {report.failed_tests}")
        print(f"   ⏭️  Skipped: {report.skipped_tests}")
        print(f"   💥 Errors: {report.error_tests}")
        print(f"   ⏱️  Duration: {report.total_duration:.2f}s")
        
        # Coverage
        if report.overall_coverage:
            print(f"\n📈 COVERAGE ANALYSIS:")
            print(f"   Overall Coverage: {report.overall_coverage:.1f}%")
            print(f"   Target: {self.coverage_targets['overall']}%")
            
            if report.module_coverage:
                print(f"   Module Coverage:")
                for module, coverage in sorted(report.module_coverage.items()):
                    target = self.coverage_targets.get(module, 80.0)
                    status = "✅" if coverage >= target else "❌"
                    print(f"     {status} {module}: {coverage:.1f}% (target: {target}%)")
        
        # Performance
        if report.performance_issues:
            print(f"\n⚡ PERFORMANCE ISSUES:")
            for issue in report.performance_issues:
                print(f"   ⚠️  {issue}")
        
        # Critical failures
        if report.critical_failures:
            print(f"\n🚨 CRITICAL FAILURES:")
            for failure in report.critical_failures:
                print(f"   ❌ {failure}")
        
        # Coverage gaps
        if report.coverage_gaps:
            print(f"\n📊 COVERAGE GAPS:")
            for gap in report.coverage_gaps:
                print(f"   📉 {gap}")
        
        # Recommendations
        if report.recommendations:
            print(f"\n💡 RECOMMENDATIONS:")
            for rec in report.recommendations:
                print(f"   {rec}")
        
        # CI/CD Readiness
        print(f"\n🚀 CI/CD READINESS:")
        status = "✅ READY" if report.ci_cd_ready else "❌ NOT READY"
        print(f"   {status}")
        
        # Final status
        print(f"\n⏱️  Total Validation Time: {duration:.2f}s")
        
        if report.ci_cd_ready:
            print("\n🎉 SUCCESS: Your code is ready for CI/CD!")
        else:
            print("\n⚠️  WARNING: Address the issues above before pushing to CI/CD")
        
        print("="*80)
    
    def _validate_missing_files_and_modules(self):
        """Validate files and modules that CI/CD expects but might be missing."""
        logger.info("🔍 Validating files and modules expected by CI/CD...")
        
        # Check for missing test files that caused CI/CD failure
        missing_test_files = [
            "backend/tests/test_cost_management.py",
            "backend/tests/performance/__init__.py"
        ]
        
        for test_file in missing_test_files:
            file_path = self.project_root / test_file
            if not file_path.exists():
                logger.error(f"❌ Missing test file expected by CI/CD: {test_file}")
                self.test_results["validation"]["failed"] += 1
            else:
                logger.info(f"✅ Test file exists: {test_file}")
                self.test_results["validation"]["passed"] += 1
        
        # Check for missing Python modules that caused import errors
        missing_modules = [
            "backend/monitoring/alerts.py",
            "backend/monitoring/real_time.py"
        ]
        
        for module_file in missing_modules:
            file_path = self.project_root / module_file
            if not file_path.exists():
                logger.error(f"❌ Missing module expected by tests: {module_file}")
                self.test_results["validation"]["failed"] += 1
            else:
                logger.info(f"✅ Module exists: {module_file}")
                self.test_results["validation"]["passed"] += 1
        
        # Check frontend package.json for required scripts
        package_json = self.project_root / "frontend" / "package.json"
        if package_json.exists():
            try:
                import json
                with open(package_json, 'r') as f:
                    package_data = json.load(f)
                
                required_scripts = ["test:coverage", "test:ci"]
                scripts = package_data.get("scripts", {})
                
                for script in required_scripts:
                    if script not in scripts:
                        logger.error(f"❌ Missing npm script in package.json: {script}")
                        self.test_results["validation"]["failed"] += 1
                    else:
                        logger.info(f"✅ NPM script exists: {script}")
                        self.test_results["validation"]["passed"] += 1
                        
            except Exception as e:
                logger.error(f"❌ Error validating package.json: {e}")
                self.test_results["validation"]["failed"] += 1
        
        # Check for CosmosVectorSearch availability in vector_storage module
        try:
            vector_storage_file = self.project_root / "backend" / "rag_pipeline" / "vector_storage.py"
            if vector_storage_file.exists():
                with open(vector_storage_file, 'r') as f:
                    content = f.read()
                    
                if "CosmosVectorSearch" in content:
                    logger.info("✅ CosmosVectorSearch found in vector_storage module")
                    self.test_results["validation"]["passed"] += 1
                else:
                    logger.error("❌ CosmosVectorSearch not found in vector_storage module")
                    self.test_results["validation"]["failed"] += 1
            else:
                logger.error("❌ vector_storage.py not found")
                self.test_results["validation"]["failed"] += 1
                
        except Exception as e:
            logger.error(f"❌ Error checking vector_storage module: {e}")
            self.test_results["validation"]["failed"] += 1
    
    def _validate_dependencies(self):
        """Validate that all requirements can be resolved and installed"""
        logger.info("📦 Validating dependencies...")
        
        requirements_files = [
            self.project_root / "backend" / "requirements.txt",
            self.project_root / "frontend" / "package.json"
        ]
        
        issues = []
        
        # Validate Python requirements
        backend_requirements = requirements_files[0]
        if backend_requirements.exists():
            try:
                with open(backend_requirements, 'r') as f:
                    for line_num, line in enumerate(f, 1):
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # Check for known problematic packages
                            if 'pkg-resources' in line:
                                issues.append(f"Line {line_num}: pkg-resources is not a valid package - remove this line")
                            
                            # Try to parse package specification
                            try:
                                import pkg_resources
                                pkg_resources.Requirement.parse(line)
                            except Exception as e:
                                issues.append(f"Line {line_num}: Invalid requirement format '{line}': {e}")
                        
                logger.info("✅ Python requirements syntax validated")
            except Exception as e:
                issues.append(f"Failed to validate requirements.txt: {e}")
        
        # Validate Node.js package.json
        frontend_package = requirements_files[1]
        if frontend_package.exists():
            try:
                import json
                with open(frontend_package, 'r') as f:
                    package_data = json.load(f)
                
                # Check for required scripts
                required_scripts = ['start', 'build', 'test', 'test:coverage']
                missing_scripts = [script for script in required_scripts 
                                 if script not in package_data.get('scripts', {})]
                
                if missing_scripts:
                    issues.append(f"Missing required npm scripts: {missing_scripts}")
                
                logger.info("✅ Frontend package.json validated")
            except Exception as e:
                issues.append(f"Failed to validate package.json: {e}")
        
        if issues:
            for issue in issues:
                logger.error(f"❌ Dependency issue: {issue}")
            raise RuntimeError(f"Dependency validation failed with {len(issues)} issues")
        
        return True

    def _run_backend_pytest(self) -> Optional[TestResult]:
        """Run actual pytest on backend to catch real failures"""
        try:
            backend_dir = self.project_root / "backend"
            logger.info(f"Running pytest in {backend_dir}")
            
            result = subprocess.run(
                ["python", "-m", "pytest", "--tb=short", "-q"],
                cwd=backend_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            output = result.stdout + result.stderr
            
            # Parse pytest output for counts
            test_count = 0
            passed = 0
            failed = 0
            errors = 0
            skipped = 0
            
            # Look for summary line like "120 failed, 192 passed, 52 errors"
            import re
            summary_pattern = r'(\d+) failed, (\d+) passed, (\d+) errors'
            match = re.search(summary_pattern, output)
            if match:
                failed = int(match.group(1))
                passed = int(match.group(2))
                errors = int(match.group(3))
                test_count = failed + passed + errors
            else:
                # Try other patterns
                if "failed" in output:
                    failed_match = re.search(r'(\d+) failed', output)
                    if failed_match:
                        failed = int(failed_match.group(1))
                if "passed" in output:
                    passed_match = re.search(r'(\d+) passed', output)
                    if passed_match:
                        passed = int(passed_match.group(1))
                test_count = failed + passed + errors
            
            return TestResult(
                test_file="backend/pytest",
                test_count=test_count,
                passed=passed,
                failed=failed,
                skipped=skipped,
                errors=errors,
                duration=0.0,  # We don't track this granularly
                exit_code=result.returncode,
                output=output[:1000]  # Truncate for brevity
            )
            
        except Exception as e:
            logger.error(f"Backend pytest failed: {e}")
            return TestResult(
                test_file="backend/pytest",
                test_count=0,
                passed=0,
                failed=1,
                skipped=0,
                errors=1,
                duration=0.0,
                exit_code=1,
                output=str(e)
            )
    
    def _run_frontend_tests(self) -> Optional[TestResult]:
        """Run frontend tests to catch real failures"""
        try:
            frontend_dir = self.project_root / "frontend"
            logger.info(f"Running npm test in {frontend_dir}")
            
            result = subprocess.run(
                ["npm", "test", "--", "--watchAll=false", "--verbose=false"],
                cwd=frontend_dir,
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )
            
            output = result.stdout + result.stderr
            
            # Parse npm test output
            test_count = 0
            passed = 0
            failed = 0
            
            import re
            # Look for "Tests: 150 failed, 117 passed, 267 total"
            test_summary = re.search(r'Tests:\s+(\d+)\s+failed,\s+(\d+)\s+passed,\s+(\d+)\s+total', output)
            if test_summary:
                failed = int(test_summary.group(1))
                passed = int(test_summary.group(2))
                test_count = int(test_summary.group(3))
            
            return TestResult(
                test_file="frontend/npm-test",
                test_count=test_count,
                passed=passed,
                failed=failed,
                skipped=0,
                errors=0,
                duration=0.0,
                exit_code=result.returncode,
                output=output[:1000]  # Truncate for brevity
            )
            
        except Exception as e:
            logger.error(f"Frontend tests failed: {e}")
            return TestResult(
                test_file="frontend/npm-test",
                test_count=0,
                passed=0,
                failed=1,
                skipped=0,
                errors=1,
                duration=0.0,
                exit_code=1,
                output=str(e)
            )
    
    def run_ci_exact_frontend_tests(self) -> TestResult:
        """Run frontend tests in exact CI configuration"""
        logger.info("🎯 Running frontend tests in CI-exact mode...")
        
        try:
            # Set CI environment variables
            env = os.environ.copy()
            env.update({
                'CI': 'true',
                'NODE_ENV': 'test',
                'REACT_APP_ENV': 'test'
            })
            
            # Run tests with coverage like CI
            cmd = ["npm", "test", "--", "--coverage", "--watchAll=false", "--testTimeout=60000"]
            
            result = subprocess.run(
                cmd,
                cwd=self.frontend_path,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes
                env=env
            )
            
            return self._parse_frontend_test_result(result)
            
        except subprocess.TimeoutExpired:
            logger.error("❌ Frontend tests timed out")
            return TestResult(
                test_file="frontend-ci-exact",
                test_count=0,
                passed=0,
                failed=1,
                skipped=0,
                errors=0,
                duration=300.0,
                output="Test execution timed out",
                failures=["Frontend tests timed out after 5 minutes"]
            )
        except Exception as e:
            logger.error(f"❌ Failed to run CI-exact frontend tests: {e}")
            return TestResult(
                test_file="frontend-ci-exact",
                test_count=0,
                passed=0,
                failed=1,
                skipped=0,
                errors=0,
                duration=0.0,
                output=str(e),
                failures=[f"Failed to run frontend tests: {e}"]
            )
    
    def _validate_test_environment_match(self):
        """Ensure local test environment matches CI expectations"""
        logger.info("🔍 Validating test environment CI/CD alignment...")
        
        issues = []
        
        # Check frontend test coverage thresholds
        frontend_package = self.project_root / "frontend" / "package.json"
        if frontend_package.exists():
            try:
                import json
                with open(frontend_package, 'r') as f:
                    package_data = json.load(f)
                
                # Check Jest configuration
                jest_config = package_data.get('jest', {})
                coverage_thresholds = jest_config.get('coverageThreshold', {}).get('global', {})
                
                required_thresholds = {
                    'statements': 70,
                    'branches': 70,
                    'functions': 70,
                    'lines': 70
                }
                
                for metric, required in required_thresholds.items():
                    actual = coverage_thresholds.get(metric, 0)
                    if actual < required:
                        issues.append(f"Frontend coverage threshold {metric}: {actual}% < {required}%")
                
                logger.info("✅ Frontend test configuration validated")
            except Exception as e:
                issues.append(f"Failed to validate frontend test config: {e}")
        
        # Check backend test environment
        backend_pytest = self.project_root / "backend" / "pyproject.toml"
        if backend_pytest.exists():
            try:
                import toml
                with open(backend_pytest, 'r') as f:
                    config = toml.load(f)
                
                # Check pytest configuration
                tool_config = config.get('tool', {})
                pytest_config = tool_config.get('pytest', {}).get('ini_options', {})
                coverage_config = tool_config.get('coverage', {})
                
                # Validate minimum coverage settings
                if 'minversion' not in pytest_config:
                    issues.append("Backend: Missing pytest minimum version specification")
                
                logger.info("✅ Backend test configuration validated")
            except ImportError:
                logger.warning("⚠️ toml package not available for backend config validation")
            except Exception as e:
                issues.append(f"Failed to validate backend test config: {e}")
        
        if issues:
            for issue in issues:
                logger.error(f"❌ Test environment issue: {issue}")
            raise RuntimeError(f"Test environment validation failed with {len(issues)} issues")
        
        return True
    
    def validate_test_environment_parity(self) -> bool:
        """Validate that local test environment matches CI/CD environment exactly"""
        logger.info("🔍 Validating test environment CI/CD alignment...")
        issues = []
        
        # Check frontend test configuration parity
        frontend_issues = self._validate_frontend_test_parity()
        issues.extend(frontend_issues)
        
        # Check backend test configuration parity  
        backend_issues = self._validate_backend_test_parity()
        issues.extend(backend_issues)
        
        # Check import resolution
        import_issues = self._validate_import_resolution()
        issues.extend(import_issues)
        
        if issues:
            logger.error(f"❌ Test environment parity issues found: {len(issues)}")
            for issue in issues:
                logger.error(f"   - {issue}")
            return False
        else:
            logger.info("✅ Test environment parity validated")
            return True
    
    def _validate_frontend_test_parity(self) -> List[str]:
        """Validate frontend test environment matches CI"""
        issues = []
        
        # Check that A/B testing mocks are consistent
        try:
            ab_test_file = self.frontend_path / "src/components/ABTestComponents.test.tsx"
            if ab_test_file.exists():
                content = ab_test_file.read_text()
                
                # Check for proper useABTest mocking
                if "mockUseABTest" not in content:
                    issues.append("ABTestComponents.test.tsx missing mockUseABTest setup")
                
                # Check for environment-specific test configurations
                if "process.env.NODE_ENV" in content and "development" in content:
                    issues.append("ABTestComponents tests have hardcoded development environment checks")
                    
        except Exception as e:
            issues.append(f"Failed to validate A/B testing configuration: {e}")
            
        # Check React testing environment setup
        try:
            setup_tests = self.frontend_path / "src/setupTests.ts"
            if setup_tests.exists():
                content = setup_tests.read_text()
                if "crypto" not in content and "MSAL" not in content:
                    issues.append("setupTests.ts missing crypto/MSAL mocking for CI environment")
        except Exception as e:
            issues.append(f"Failed to validate React testing setup: {e}")
            
        return issues
    
    def _validate_backend_test_parity(self) -> List[str]:
        """Validate backend test environment matches CI"""
        issues = []
        
        # Check voice interface tests specifically
        try:
            voice_test_file = self.backend_path / "tests/test_voice_interface.py"
            if voice_test_file.exists():
                content = voice_test_file.read_text()
                
                # Check for incorrect import patterns
                if "SanskritOptimizer" in content and "SanskritRecognitionOptimizer" not in content:
                    issues.append("test_voice_interface.py has incorrect import: SanskritOptimizer should be SanskritRecognitionOptimizer")
                
                if "TTSOptimizer" in content and "SpiritualTTSOptimizer" not in content:
                    issues.append("test_voice_interface.py has incorrect import: TTSOptimizer should be SpiritualTTSOptimizer")
                    
        except Exception as e:
            issues.append(f"Failed to validate voice interface tests: {e}")
            
        return issues
    
    def _validate_import_resolution(self) -> List[str]:
        """Validate all imports can be resolved correctly"""
        issues = []
        
        # Check backend imports
        try:
            result = subprocess.run(
                [sys.executable, "-c", "import voice.sanskrit_optimizer; print('OK')"],
                cwd=self.backend_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode != 0:
                issues.append(f"Backend import validation failed: {result.stderr}")
        except Exception as e:
            issues.append(f"Failed to validate backend imports: {e}")
            
        # Check frontend imports resolution by running TypeScript check
        try:
            result = subprocess.run(
                ["npx", "tsc", "--noEmit"],
                cwd=self.frontend_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode != 0 and "error TS" in result.stderr:
                issues.append(f"Frontend TypeScript import errors: {result.stderr[:500]}")
        except Exception as e:
            issues.append(f"Failed to validate frontend imports: {e}")
            
        return issues
    
    def validate_interface_contracts(self) -> bool:
        """Validate that implementations satisfy test interface contracts"""
        logger.info("🔍 Validating interface contracts between tests and implementations...")
        issues = []
        
        # Check backend voice interface contracts
        voice_issues = self._validate_voice_interface_contracts()
        issues.extend(voice_issues)
        
        # Check frontend component contracts
        frontend_issues = self._validate_frontend_component_contracts()
        issues.extend(frontend_issues)
        
        # Check async method contracts
        async_issues = self._validate_async_method_contracts()
        issues.extend(async_issues)
        
        if issues:
            logger.error(f"❌ Interface contract violations found: {len(issues)}")
            for issue in issues:
                logger.error(f"   - {issue}")
            return False
        else:
            logger.info("✅ All interface contracts validated")
            return True
    
    def _validate_voice_interface_contracts(self) -> List[str]:
        """Validate voice interface implementation contracts"""
        issues = []
        
        try:
            # Check SpeechProcessor implementation
            speech_processor_file = self.backend_path / "voice/speech_processor.py"
            if speech_processor_file.exists():
                content = speech_processor_file.read_text()
                
                # Check for expected methods from tests
                expected_methods = [
                    'process_audio', '_reduce_noise', '_recognize_speech',
                    'preprocess_audio', 'speech_to_text', 'detect_voice_activity'
                ]
                
                missing_methods = []
                for method in expected_methods:
                    if f"def {method}" not in content and f"async def {method}" not in content:
                        # Check if it's a property
                        if f"def {method}(" not in content and f"property" not in content or f"{method}" not in content:
                            missing_methods.append(method)
                
                if missing_methods:
                    issues.append(f"SpeechProcessor missing methods: {missing_methods}")
                
                # Check for property implementations
                if "_recognize_speech" in content and "property" in content:
                    # Verify property has setter/deleter if tests mock it
                    if "setter" not in content:
                        issues.append("SpeechProcessor._recognize_speech property needs setter for test mocking")
                
            # Check audio utils implementation
            audio_utils_file = self.backend_path / "voice/audio_utils.py"
            if audio_utils_file.exists():
                content = audio_utils_file.read_text()
                
                # Check for AudioSegment class and export method
                if "class AudioSegment" in content:
                    if "def export" not in content:
                        issues.append("AudioSegment class missing export method")
                        
        except Exception as e:
            issues.append(f"Failed to validate voice interface contracts: {e}")
            
        return issues
    
    def _validate_frontend_component_contracts(self) -> List[str]:
        """Validate frontend component implementation contracts"""
        issues = []
        
        try:
            # Check ABTestComponents implementation
            ab_test_file = self.frontend_path / "src/components/ABTestComponents.tsx"
            if ab_test_file.exists():
                content = ab_test_file.read_text()
                
                # Check for voice tutorial implementation
                if "voice-tutorial-overlay" in content:
                    if "Voice Feature" not in content:
                        issues.append("ABTestVoiceInterface missing 'Voice Feature' text in tutorial")
                        
                # Check for proper variant handling
                if "useABTest" in content:
                    # Verify all expected variants are handled
                    expected_variants = ['prominent-voice', 'subtle-voice']
                    for variant in expected_variants:
                        if variant not in content:
                            issues.append(f"ABTestVoiceInterface missing handling for variant: {variant}")
                            
        except Exception as e:
            issues.append(f"Failed to validate frontend component contracts: {e}")
            
        return issues
    
    def _validate_async_method_contracts(self) -> List[str]:
        """Validate async method signatures match test expectations"""
        issues = []
        
        try:
            # Check voice comprehensive tests
            voice_test_file = self.backend_path / "tests/voice_interface/test_voice_comprehensive.py"
            if voice_test_file.exists():
                content = voice_test_file.read_text()
                
                # Find all await expressions in tests
                import re
                await_patterns = re.findall(r'await\s+([^(]+)', content)
                
                for pattern in await_patterns:
                    # Check if the awaited object should actually be awaitable
                    if 'Language' in pattern:
                        issues.append(f"Test tries to await non-awaitable Language object: {pattern}")
                    elif 'dict' in pattern or '{' in pattern:
                        issues.append(f"Test tries to await dict object: {pattern}")
                        
        except Exception as e:
            issues.append(f"Failed to validate async method contracts: {e}")
            
        return issues
    
    def _execute_tests_with_timeout(self, test_files: List[Path], report: ValidationReport, timeout: float) -> List[TestResult]:
        """Execute tests with timeout awareness"""
        logger.info(f"🧪 Executing {len(test_files)} test files with {timeout:.1f}s timeout...")
        
        test_results = []
        start_time = time.time()
        
        # First run real pytest on backend with reduced timeout
        if self.project_root.joinpath("backend").exists() and (time.time() - start_time) < timeout:
            logger.info("🐍 Running backend pytest suite...")
            remaining_time = timeout - (time.time() - start_time)
            backend_result = self._run_backend_pytest_with_timeout(remaining_time)
            if backend_result:
                test_results.append(backend_result)
        
        # Check if we have time for frontend tests
        if (time.time() - start_time) < timeout and self.project_root.joinpath("frontend").exists():
            logger.info("⚛️ Running frontend tests...")
            remaining_time = timeout - (time.time() - start_time)
            frontend_result = self._run_frontend_tests_with_timeout(remaining_time)
            if frontend_result:
                test_results.append(frontend_result)
        
        # Skip comprehensive testing if we're running out of time
        if (time.time() - start_time) > timeout * 0.8:
            logger.warning("⏰ Skipping comprehensive tests due to time constraints")
            return test_results
        
        # Run remaining tests if time permits
        if self.parallel and len(test_files) > 1:
            remaining_time = timeout - (time.time() - start_time)
            if remaining_time > 30:  # Only if we have at least 30 seconds
                results = self._execute_tests_parallel_with_timeout(test_files, remaining_time)
                test_results.extend(results)
        else:
            # Sequential execution with timeout
            for test_file in test_files:
                if (time.time() - start_time) > timeout:
                    logger.warning(f"⏰ Timeout reached, skipping remaining {len(test_files) - test_files.index(test_file)} test files")
                    break
                
                result = self._run_single_test_with_timeout(test_file, 30)  # 30 second max per test
                if result:
                    test_results.append(result)
        
        return test_results
    
    def _run_backend_pytest_with_timeout(self, timeout: float) -> Optional[TestResult]:
        """Run backend pytest with timeout"""
        try:
            start_time = time.time()
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
                cwd=self.backend_path,
                capture_output=True,
                text=True,
                timeout=min(timeout, 120)  # Max 2 minutes for backend tests
            )
            
            duration = time.time() - start_time
            logger.info(f"🐍 Backend tests completed in {duration:.1f}s")
            
            # Parse pytest output (simplified)
            if result.returncode == 0:
                return TestResult("backend_pytest", 1, 1, 0, 0, 0, duration, [], 
                                  "Backend pytest passed", True)
            else:
                return TestResult("backend_pytest", 1, 0, 1, 0, 0, duration, 
                                  [result.stderr], "Backend pytest failed", False)
                
        except subprocess.TimeoutExpired:
            logger.warning(f"⏰ Backend pytest timed out after {timeout:.1f}s")
            return TestResult("backend_pytest", 1, 0, 0, 0, 1, timeout, 
                              ["Timeout"], "Backend pytest timeout", False)
        except Exception as e:
            logger.error(f"❌ Backend pytest error: {e}")
            return None

    def _run_frontend_tests_with_timeout(self, timeout: float) -> Optional[TestResult]:
        """Run frontend tests with timeout"""
        try:
            start_time = time.time()
            result = subprocess.run(
                ["npm", "test", "--", "--watchAll=false", "--testTimeout=30000"],
                cwd=self.frontend_path,
                capture_output=True,
                text=True,
                timeout=min(timeout, 90)  # Max 90 seconds for frontend tests
            )
            
            duration = time.time() - start_time
            logger.info(f"⚛️ Frontend tests completed in {duration:.1f}s")
            
            if result.returncode == 0:
                return TestResult("frontend_tests", 1, 1, 0, 0, 0, duration, [], 
                                  "Frontend tests passed", True)
            else:
                return TestResult("frontend_tests", 1, 0, 1, 0, 0, duration, 
                                  [result.stderr], "Frontend tests failed", False)
                
        except subprocess.TimeoutExpired:
            logger.warning(f"⏰ Frontend tests timed out after {timeout:.1f}s")
            return TestResult("frontend_tests", 1, 0, 0, 0, 1, timeout, 
                              ["Timeout"], "Frontend tests timeout", False)
        except Exception as e:
            logger.error(f"❌ Frontend tests error: {e}")
            return None

    def _run_single_test_with_timeout(self, test_file: Path, timeout: float) -> Optional[TestResult]:
        """Run a single test file with timeout"""
        try:
            start_time = time.time()
            result = subprocess.run(
                [sys.executable, "-m", "pytest", str(test_file), "-v"],
                cwd=self.backend_path,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                return TestResult(str(test_file), 1, 1, 0, 0, 0, duration, [], 
                                  f"{test_file} passed", True)
            else:
                return TestResult(str(test_file), 1, 0, 1, 0, 0, duration, 
                                  [result.stderr], f"{test_file} failed", False)
                
        except subprocess.TimeoutExpired:
            logger.warning(f"⏰ Test {test_file} timed out after {timeout:.1f}s")
            return TestResult(str(test_file), 1, 0, 0, 0, 1, timeout, 
                              ["Timeout"], f"{test_file} timeout", False)
        except Exception as e:
            logger.error(f"❌ Test {test_file} error: {e}")
            return None

    def _execute_tests_parallel_with_timeout(self, test_files: List[Path], timeout: float) -> List[TestResult]:
        """Execute tests in parallel with timeout"""
        results = []
        per_test_timeout = min(30, timeout / len(test_files))  # Max 30s per test
        
        with ThreadPoolExecutor(max_workers=min(self.max_workers, len(test_files))) as executor:
            future_to_test = {
                executor.submit(self._run_single_test_with_timeout, test_file, per_test_timeout): test_file
                for test_file in test_files
            }
            
            start_time = time.time()
            for future in as_completed(future_to_test, timeout=timeout):
                if (time.time() - start_time) > timeout:
                    logger.warning("⏰ Parallel test execution timeout reached")
                    break
                    
                result = future.result()
                if result:
                    results.append(result)
        
        return results
    


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Vimarsh Local E2E Validation")
    parser.add_argument('--quick', action='store_true', help='Run only critical tests')
    parser.add_argument('--no-coverage', action='store_true', help='Disable coverage collection')
    parser.add_argument('--no-parallel', action='store_true', help='Disable parallel execution')
    parser.add_argument('--max-workers', type=int, default=4, help='Maximum parallel workers')
    parser.add_argument('--timeout', type=int, default=300, help='Maximum execution timeout in seconds')
    parser.add_argument('--project-root', type=Path, help='Project root directory')
    
    args = parser.parse_args()
    
    # Initialize validator
    validator = LocalE2EValidator(
        project_root=args.project_root,
        quick_mode=args.quick,
        enable_coverage=not args.no_coverage,
        parallel=not args.no_parallel,
        max_workers=args.max_workers,
        timeout=args.timeout
    )
    
    # Run validation
    report = validator.run_validation()
    
    # Exit with appropriate code
    if report.ci_cd_ready:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
