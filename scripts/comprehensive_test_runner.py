#!/usr/bin/env python3
"""
Comprehensive Test Runner for Vimarsh AI Agent

This script provides fast, robust local end-to-end validation to catch all issues
before pushing to GitHub. It's optimized for speed while maintaining thoroughness.
"""

import asyncio
import time
import subprocess
import sys
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import pytest


@dataclass
class TestResult:
    """Test execution result."""
    component: str
    test_file: str
    status: str  # 'passed', 'failed', 'skipped'
    duration: float
    coverage: float
    errors: List[str]
    warnings: List[str]


@dataclass
class ValidationReport:
    """Comprehensive validation report."""
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    overall_coverage: float
    duration: float
    critical_failures: List[str]
    components_status: Dict[str, str]
    recommendations: List[str]


class ComprehensiveTestRunner:
    """Fast, comprehensive test runner for local validation."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend"
        self.results: List[TestResult] = []
        self.start_time = None
        
        # Test configuration for speed optimization
        self.test_config = {
            'parallel_workers': min(8, os.cpu_count()),
            'timeout_seconds': 300,  # 5 minutes max per test suite
            'coverage_threshold': 85.0,
            'critical_components': [
                'llm_integration', 'spiritual_guidance', 'rag_pipeline',
                'monitoring', 'data_processing', 'voice_interface'
            ]
        }
        
    def run_comprehensive_validation(self) -> ValidationReport:
        """Run comprehensive validation optimized for speed and thoroughness."""
        print("🚀 Starting Comprehensive Vimarsh Validation...")
        print("=" * 60)
        
        self.start_time = time.time()
        
        # Phase 1: Fast Unit Tests (parallel execution)
        print("📋 Phase 1: Fast Unit Tests (parallel)")
        unit_results = self._run_unit_tests_parallel()
        
        # Phase 2: Integration Tests (sequential for dependencies)
        print("🔗 Phase 2: Integration Tests")
        integration_results = self._run_integration_tests()
        
        # Phase 3: E2E Tests (critical path only)
        print("🌐 Phase 3: Critical E2E Tests")
        e2e_results = self._run_critical_e2e_tests()
        
        # Phase 4: Coverage Analysis
        print("📊 Phase 4: Coverage Analysis")
        coverage_report = self._analyze_coverage()
        
        # Phase 5: Quality Gates
        print("🎯 Phase 5: Quality Gates")
        quality_report = self._check_quality_gates()
        
        # Generate final report
        report = self._generate_validation_report(
            unit_results + integration_results + e2e_results,
            coverage_report,
            quality_report
        )
        
        self._print_validation_summary(report)
        return report
        
    def _run_unit_tests_parallel(self) -> List[TestResult]:
        """Run unit tests in parallel for maximum speed."""
        unit_test_files = [
            'test_llm_integration_comprehensive.py',
            'test_monitoring_comprehensive.py', 
            'test_data_processing_comprehensive.py',
            'test_voice_interface_comprehensive.py',
            'test_basic_integration.py',
            'test_spiritual_guidance_api.py',
            'test_rag_pipeline.py',
            'test_cost_management.py'
        ]
        
        results = []
        with ThreadPoolExecutor(max_workers=self.test_config['parallel_workers']) as executor:
            futures = {
                executor.submit(self._run_single_test_file, test_file): test_file
                for test_file in unit_test_files
                if (self.backend_dir / "tests" / test_file).exists()
            }
            
            for future in as_completed(futures, timeout=self.test_config['timeout_seconds']):
                test_file = futures[future]
                try:
                    result = future.result(timeout=30)  # 30s per test file
                    results.append(result)
                    status_icon = "✅" if result.status == "passed" else "❌"
                    print(f"  {status_icon} {test_file}: {result.status} ({result.duration:.1f}s)")
                except Exception as e:
                    results.append(TestResult(
                        component="unit_test",
                        test_file=test_file,
                        status="failed",
                        duration=0.0,
                        coverage=0.0,
                        errors=[str(e)],
                        warnings=[]
                    ))
                    print(f"  ❌ {test_file}: FAILED - {str(e)}")
                    
        return results
        
    def _run_single_test_file(self, test_file: str) -> TestResult:
        """Run a single test file with coverage."""
        start_time = time.time()
        
        try:
            # Run pytest with coverage for the specific file
            cmd = [
                sys.executable, "-m", "pytest",
                str(self.backend_dir / "tests" / test_file),
                "--cov=.",
                "--cov-report=json:coverage_temp.json",
                "--tb=short",
                "-v"
            ]
            
            result = subprocess.run(
                cmd,
                cwd=self.backend_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            duration = time.time() - start_time
            
            # Parse coverage if available
            coverage = 0.0
            coverage_file = self.backend_dir / "coverage_temp.json"
            if coverage_file.exists():
                try:
                    with open(coverage_file) as f:
                        cov_data = json.load(f)
                        coverage = cov_data.get('totals', {}).get('percent_covered', 0.0)
                except:
                    pass
                finally:
                    coverage_file.unlink(missing_ok=True)
            
            # Determine status
            status = "passed" if result.returncode == 0 else "failed"
            errors = result.stderr.split('\n') if result.stderr else []
            warnings = [line for line in result.stdout.split('\n') if 'WARNING' in line]
            
            return TestResult(
                component=self._extract_component_name(test_file),
                test_file=test_file,
                status=status,
                duration=duration,
                coverage=coverage,
                errors=errors,
                warnings=warnings
            )
            
        except subprocess.TimeoutExpired:
            return TestResult(
                component=self._extract_component_name(test_file),
                test_file=test_file,
                status="failed",
                duration=30.0,
                coverage=0.0,
                errors=["Test timeout after 30 seconds"],
                warnings=[]
            )
        except Exception as e:
            return TestResult(
                component=self._extract_component_name(test_file),
                test_file=test_file,
                status="failed",
                duration=time.time() - start_time,
                coverage=0.0,
                errors=[str(e)],
                warnings=[]
            )
            
    def _run_integration_tests(self) -> List[TestResult]:
        """Run integration tests sequentially."""
        integration_tests = [
            'test_integration_rag_llm.py',
            'test_llm_workflow_integration.py',
            'test_end_to_end_workflow.py'
        ]
        
        results = []
        for test_file in integration_tests:
            if (self.backend_dir / "tests" / test_file).exists():
                print(f"  🔄 Running {test_file}...")
                result = self._run_single_test_file(test_file)
                results.append(result)
                status_icon = "✅" if result.status == "passed" else "❌"
                print(f"  {status_icon} {test_file}: {result.status} ({result.duration:.1f}s)")
            else:
                print(f"  ⚠️  {test_file}: SKIPPED (file not found)")
                
        return results
        
    def _run_critical_e2e_tests(self) -> List[TestResult]:
        """Run critical end-to-end tests."""
        e2e_tests = [
            'e2e/test_full_application_flow.py',
            'e2e/test_spiritual_content_quality.py'
        ]
        
        results = []
        for test_file in e2e_tests:
            test_path = self.backend_dir / "tests" / test_file
            if test_path.exists():
                print(f"  🌐 Running {test_file}...")
                result = self._run_single_test_file(test_file)
                results.append(result)
                status_icon = "✅" if result.status == "passed" else "❌"
                print(f"  {status_icon} {test_file}: {result.status} ({result.duration:.1f}s)")
            else:
                print(f"  ⚠️  {test_file}: SKIPPED (file not found)")
                
        return results
        
    def _analyze_coverage(self) -> Dict[str, Any]:
        """Analyze overall test coverage."""
        try:
            # Run full coverage analysis
            cmd = [
                sys.executable, "-m", "pytest",
                "--cov=.",
                "--cov-report=json:coverage_final.json",
                "--cov-report=term-missing",
                str(self.backend_dir / "tests"),
                "-q"  # Quiet mode for speed
            ]
            
            subprocess.run(cmd, cwd=self.backend_dir, capture_output=True)
            
            # Parse coverage report
            coverage_file = self.backend_dir / "coverage_final.json"
            if coverage_file.exists():
                with open(coverage_file) as f:
                    coverage_data = json.load(f)
                    
                return {
                    'overall_coverage': coverage_data.get('totals', {}).get('percent_covered', 0.0),
                    'files_coverage': {
                        filename: file_data.get('summary', {}).get('percent_covered', 0.0)
                        for filename, file_data in coverage_data.get('files', {}).items()
                    },
                    'missing_lines': coverage_data.get('totals', {}).get('missing_lines', 0),
                    'total_lines': coverage_data.get('totals', {}).get('num_statements', 0)
                }
            else:
                return {'overall_coverage': 0.0, 'error': 'Coverage file not found'}
                
        except Exception as e:
            return {'overall_coverage': 0.0, 'error': str(e)}
            
    def _check_quality_gates(self) -> Dict[str, Any]:
        """Check quality gates and requirements."""
        quality_report = {
            'gates_passed': [],
            'gates_failed': [],
            'warnings': [],
            'critical_issues': []
        }
        
        # Calculate overall metrics
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r.status == "passed"])
        failed_tests = len([r for r in self.results if r.status == "failed"])
        
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Gate 1: Test Pass Rate (must be 100%)
        if pass_rate == 100:
            quality_report['gates_passed'].append("✅ Test Pass Rate: 100%")
        else:
            quality_report['gates_failed'].append(f"❌ Test Pass Rate: {pass_rate:.1f}% (Required: 100%)")
            
        # Gate 2: Coverage Threshold (must be >= 85%)
        coverage_data = self._get_coverage_data()
        overall_coverage = coverage_data.get('overall_coverage', 0.0)
        
        if overall_coverage >= self.test_config['coverage_threshold']:
            quality_report['gates_passed'].append(f"✅ Coverage: {overall_coverage:.1f}%")
        else:
            quality_report['gates_failed'].append(
                f"❌ Coverage: {overall_coverage:.1f}% (Required: {self.test_config['coverage_threshold']}%)"
            )
            
        # Gate 3: Critical Components (all must pass)
        critical_failures = []
        for result in self.results:
            if result.component in self.test_config['critical_components'] and result.status == "failed":
                critical_failures.append(result.component)
                
        if not critical_failures:
            quality_report['gates_passed'].append("✅ Critical Components: All Passing")
        else:
            quality_report['gates_failed'].append(
                f"❌ Critical Components Failed: {', '.join(critical_failures)}"
            )
            quality_report['critical_issues'].extend(critical_failures)
            
        # Gate 4: Performance (total validation time should be reasonable)
        total_duration = time.time() - self.start_time if self.start_time else 0
        max_duration = 480  # 8 minutes max for full validation
        
        if total_duration <= max_duration:
            quality_report['gates_passed'].append(f"✅ Performance: {total_duration:.1f}s")
        else:
            quality_report['warnings'].append(
                f"⚠️  Performance: {total_duration:.1f}s (Target: <{max_duration}s)"
            )
            
        return quality_report
        
    def _generate_validation_report(self, all_results: List[TestResult], 
                                  coverage_report: Dict[str, Any],
                                  quality_report: Dict[str, Any]) -> ValidationReport:
        """Generate comprehensive validation report."""
        self.results = all_results
        
        total_tests = len(all_results)
        passed_tests = len([r for r in all_results if r.status == "passed"])
        failed_tests = len([r for r in all_results if r.status == "failed"])
        skipped_tests = len([r for r in all_results if r.status == "skipped"])
        
        # Component status summary
        components_status = {}
        for component in self.test_config['critical_components']:
            component_results = [r for r in all_results if r.component == component]
            if not component_results:
                components_status[component] = "no_tests"
            elif all(r.status == "passed" for r in component_results):
                components_status[component] = "passing"
            else:
                components_status[component] = "failing"
                
        # Generate recommendations
        recommendations = []
        if failed_tests > 0:
            recommendations.append(f"Fix {failed_tests} failing tests before deployment")
        if coverage_report.get('overall_coverage', 0) < 85:
            recommendations.append("Increase test coverage to meet 85% threshold")
        if quality_report.get('critical_issues'):
            recommendations.append("Address critical component failures immediately")
            
        total_duration = time.time() - self.start_time if self.start_time else 0
        
        return ValidationReport(
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
            overall_coverage=coverage_report.get('overall_coverage', 0.0),
            duration=total_duration,
            critical_failures=quality_report.get('critical_issues', []),
            components_status=components_status,
            recommendations=recommendations
        )
        
    def _print_validation_summary(self, report: ValidationReport):
        """Print comprehensive validation summary."""
        print("\n" + "=" * 60)
        print("📊 VIMARSH VALIDATION SUMMARY")
        print("=" * 60)
        
        # Overall Status
        overall_status = "✅ PASSED" if report.failed_tests == 0 and report.overall_coverage >= 85 else "❌ FAILED"
        print(f"Overall Status: {overall_status}")
        print(f"Duration: {report.duration:.1f}s")
        print()
        
        # Test Results
        print("📋 Test Results:")
        print(f"  Total Tests: {report.total_tests}")
        print(f"  ✅ Passed: {report.passed_tests}")
        print(f"  ❌ Failed: {report.failed_tests}")
        print(f"  ⏭️  Skipped: {report.skipped_tests}")
        print(f"  📊 Coverage: {report.overall_coverage:.1f}%")
        print()
        
        # Component Status
        print("🔧 Component Status:")
        for component, status in report.components_status.items():
            status_icon = {
                "passing": "✅",
                "failing": "❌", 
                "no_tests": "⚠️"
            }.get(status, "❓")
            print(f"  {status_icon} {component}: {status}")
        print()
        
        # Critical Issues
        if report.critical_failures:
            print("🚨 Critical Issues:")
            for issue in report.critical_failures:
                print(f"  ❌ {issue}")
            print()
            
        # Recommendations
        if report.recommendations:
            print("💡 Recommendations:")
            for rec in report.recommendations:
                print(f"  • {rec}")
            print()
            
        # Ready for Push?
        if report.failed_tests == 0 and report.overall_coverage >= 85:
            print("🚀 READY FOR PUSH TO GITHUB! 🚀")
        else:
            print("⛔ NOT READY FOR PUSH - Fix issues above first")
            
        print("=" * 60)
        
    def _extract_component_name(self, test_file: str) -> str:
        """Extract component name from test file."""
        if "llm" in test_file:
            return "llm_integration"
        elif "monitoring" in test_file:
            return "monitoring"
        elif "data_processing" in test_file:
            return "data_processing"
        elif "voice" in test_file:
            return "voice_interface"
        elif "spiritual_guidance" in test_file:
            return "spiritual_guidance"
        elif "rag" in test_file:
            return "rag_pipeline"
        elif "cost" in test_file:
            return "cost_management"
        else:
            return "integration"
            
    def _get_coverage_data(self) -> Dict[str, Any]:
        """Get current coverage data."""
        coverage_file = self.backend_dir / "coverage_final.json"
        if coverage_file.exists():
            try:
                with open(coverage_file) as f:
                    return json.load(f)
            except:
                pass
        return {'overall_coverage': 0.0}


def main():
    """Main entry point for comprehensive validation."""
    project_root = Path(__file__).parent.parent
    runner = ComprehensiveTestRunner(str(project_root))
    
    try:
        report = runner.run_comprehensive_validation()
        
        # Exit with appropriate code
        if report.failed_tests == 0 and report.overall_coverage >= 85:
            sys.exit(0)  # Success
        else:
            sys.exit(1)  # Failure
            
    except KeyboardInterrupt:
        print("\n⚠️  Validation interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Validation failed with error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
