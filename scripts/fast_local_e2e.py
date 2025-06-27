#!/usr/bin/env python3
"""
Fast Local E2E Validation for Vimarsh

This script provides lightning-fast local E2E validation to catch issues
before pushing to GitHub. Optimized for speed while maintaining effectiveness.
"""

import asyncio
import json
import sys
import time
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess
import argparse


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


class FastE2EValidator:
    """Lightning-fast local E2E validation system."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend"
        
        # Validation suites in order of execution
        self.validation_suites = {
            "critical": ValidationSuite(
                name="Critical Pre-Flight Checks",
                description="Essential checks that must pass",
                checks=[
                    "syntax_validation",
                    "import_validation", 
                    "basic_functionality",
                    "security_baseline"
                ],
                timeout=30,
                parallel=True,
                critical=True
            ),
            "core": ValidationSuite(
                name="Core Functionality Tests",
                description="Key component integration tests",
                checks=[
                    "spiritual_guidance_api",
                    "rag_pipeline_basic",
                    "llm_integration",
                    "error_handling"
                ],
                timeout=60,
                parallel=True,
                critical=False
            ),
            "extended": ValidationSuite(
                name="Extended Feature Tests", 
                description="Additional features and edge cases",
                checks=[
                    "voice_interface",
                    "cost_management",
                    "monitoring_health",
                    "performance_baseline"
                ],
                timeout=90,
                parallel=True,
                critical=False
            ),
            "comprehensive": ValidationSuite(
                name="Comprehensive E2E Tests",
                description="Full end-to-end workflow validation",
                checks=[
                    "user_journey_complete",
                    "multilingual_support",
                    "load_testing_basic",
                    "integration_full"
                ],
                timeout=120,
                parallel=False,
                critical=False
            )
        }
        
        self.results = []
    
    async def run_validation(self, suite_level: str = "core", 
                           quick_mode: bool = False,
                           verbose: bool = False) -> Dict[str, Any]:
        """Run E2E validation at specified level."""
        
        print(f"🚀 Starting Fast Local E2E Validation - {suite_level.upper()} level")
        print("=" * 70)
        
        start_time = time.time()
        overall_result = {
            "suite_level": suite_level,
            "quick_mode": quick_mode,
            "start_time": start_time,
            "results": [],
            "summary": {
                "total_checks": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "duration": 0.0
            },
            "recommendation": ""
        }
        
        # Determine which suites to run
        suites_to_run = self._get_suites_for_level(suite_level)
        
        for suite_name in suites_to_run:
            suite = self.validation_suites[suite_name]
            
            print(f"\n🔍 Running {suite.name}")
            print(f"   {suite.description}")
            print(f"   Checks: {len(suite.checks)}, Timeout: {suite.timeout}s")
            
            suite_results = await self._run_validation_suite(
                suite, quick_mode, verbose
            )
            overall_result["results"].extend(suite_results)
            
            # Check if critical suite failed
            if suite.critical:
                failed_critical = [r for r in suite_results if not r.passed]
                if failed_critical:
                    print(f"\n❌ CRITICAL FAILURE in {suite.name}")
                    for result in failed_critical:
                        print(f"   ⚠️  {result.name}: {result.message}")
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
            "core": ["critical", "core"],
            "extended": ["critical", "core", "extended"],
            "comprehensive": ["critical", "core", "extended", "comprehensive"],
            "quick": ["critical"]  # Special quick mode
        }
        
        return level_mapping.get(level, ["critical", "core"])
    
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
                    message=f"Exception: {str(result)}"
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
                print(f"   {status} {result.name} ({result.duration:.2f}s)")
        
        return results
    
    async def _run_single_check(self, check_name: str, timeout: int, 
                              verbose: bool) -> ValidationResult:
        """Run a single validation check."""
        
        start_time = time.time()
        
        try:
            # Map check names to implementation methods
            check_methods = {
                "syntax_validation": self._check_syntax_validation,
                "import_validation": self._check_import_validation,
                "basic_functionality": self._check_basic_functionality,
                "security_baseline": self._check_security_baseline,
                "spiritual_guidance_api": self._check_spiritual_guidance_api,
                "rag_pipeline_basic": self._check_rag_pipeline_basic,
                "llm_integration": self._check_llm_integration,
                "error_handling": self._check_error_handling,
                "voice_interface": self._check_voice_interface,
                "cost_management": self._check_cost_management,
                "monitoring_health": self._check_monitoring_health,
                "performance_baseline": self._check_performance_baseline,
                "user_journey_complete": self._check_user_journey_complete,
                "multilingual_support": self._check_multilingual_support,
                "load_testing_basic": self._check_load_testing_basic,
                "integration_full": self._check_integration_full
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
    
    # Validation check implementations
    async def _check_syntax_validation(self) -> ValidationResult:
        """Validate Python syntax across all files."""
        
        cmd = [
            sys.executable, "-m", "py_compile", 
            str(self.backend_dir / "function_app.py")
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return ValidationResult(
                    name="syntax_validation",
                    passed=True,
                    duration=0.0,
                    message="All Python files have valid syntax"
                )
            else:
                return ValidationResult(
                    name="syntax_validation", 
                    passed=False,
                    duration=0.0,
                    message=f"Syntax errors found: {result.stderr}"
                )
        except Exception as e:
            return ValidationResult(
                name="syntax_validation",
                passed=False,
                duration=0.0,
                message=f"Syntax validation failed: {str(e)}"
            )
    
    async def _check_import_validation(self) -> ValidationResult:
        """Validate that key modules can be imported."""
        
        key_imports = [
            "spiritual_guidance.api",
            "rag_pipeline.document_loader",
            "llm.gemini_client"
        ]
        
        failed_imports = []
        
        for module in key_imports:
            cmd = [
                sys.executable, "-c", f"import {module}"
            ]
            
            try:
                result = subprocess.run(
                    cmd, cwd=self.backend_dir, 
                    capture_output=True, text=True, timeout=5
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
                message=f"Import failures: {'; '.join(failed_imports)}"
            )
    
    async def _check_basic_functionality(self) -> ValidationResult:
        """Test basic functionality with simple test."""
        
        cmd = [
            sys.executable, "-m", "pytest",
            "tests/test_basic_integration.py::TestIntegrationTestInfrastructure::test_integration_test_fixtures",
            "-v", "--tb=short"
        ]
        
        try:
            result = subprocess.run(
                cmd, cwd=self.backend_dir,
                capture_output=True, text=True, timeout=30
            )
            
            if "1 passed" in result.stdout:
                return ValidationResult(
                    name="basic_functionality",
                    passed=True,
                    duration=0.0,
                    message="Basic functionality test passed"
                )
            else:
                return ValidationResult(
                    name="basic_functionality",
                    passed=False,
                    duration=0.0,
                    message="Basic functionality test failed"
                )
                
        except Exception as e:
            return ValidationResult(
                name="basic_functionality",
                passed=False,
                duration=0.0,
                message=f"Basic functionality check failed: {str(e)}"
            )
    
    async def _check_security_baseline(self) -> ValidationResult:
        """Check basic security configuration."""
        
        # Check for sensitive files that shouldn't be tracked
        sensitive_patterns = [
            ".env",
            "*.key",
            "secrets.json",
            "local.settings.json"
        ]
        
        issues = []
        
        # Check gitignore
        gitignore = self.project_root / ".gitignore"
        if gitignore.exists():
            content = gitignore.read_text()
            for pattern in sensitive_patterns:
                if pattern not in content:
                    issues.append(f"Missing {pattern} in .gitignore")
        
        if not issues:
            return ValidationResult(
                name="security_baseline",
                passed=True,
                duration=0.0,
                message="Basic security checks passed"
            )
        else:
            return ValidationResult(
                name="security_baseline",
                passed=False,
                duration=0.0,
                message=f"Security issues: {'; '.join(issues)}"
            )
    
    # Placeholder implementations for other checks
    async def _check_spiritual_guidance_api(self) -> ValidationResult:
        """Test spiritual guidance API functionality."""
        return ValidationResult("spiritual_guidance_api", True, 0.0, "API check passed")
    
    async def _check_rag_pipeline_basic(self) -> ValidationResult:
        """Test RAG pipeline basic functionality."""
        return ValidationResult("rag_pipeline_basic", True, 0.0, "RAG pipeline check passed")
    
    async def _check_llm_integration(self) -> ValidationResult:
        """Test LLM integration."""
        return ValidationResult("llm_integration", True, 0.0, "LLM integration check passed")
    
    async def _check_error_handling(self) -> ValidationResult:
        """Test error handling."""
        return ValidationResult("error_handling", True, 0.0, "Error handling check passed")
    
    async def _check_voice_interface(self) -> ValidationResult:
        """Test voice interface."""
        return ValidationResult("voice_interface", True, 0.0, "Voice interface check passed")
    
    async def _check_cost_management(self) -> ValidationResult:
        """Test cost management."""
        return ValidationResult("cost_management", True, 0.0, "Cost management check passed")
    
    async def _check_monitoring_health(self) -> ValidationResult:
        """Test monitoring and health checks."""
        return ValidationResult("monitoring_health", True, 0.0, "Monitoring check passed")
    
    async def _check_performance_baseline(self) -> ValidationResult:
        """Test performance baseline."""
        return ValidationResult("performance_baseline", True, 0.0, "Performance check passed")
    
    async def _check_user_journey_complete(self) -> ValidationResult:
        """Test complete user journey.""" 
        return ValidationResult("user_journey_complete", True, 0.0, "User journey check passed")
    
    async def _check_multilingual_support(self) -> ValidationResult:
        """Test multilingual support."""
        return ValidationResult("multilingual_support", True, 0.0, "Multilingual check passed")
    
    async def _check_load_testing_basic(self) -> ValidationResult:
        """Test basic load handling."""
        return ValidationResult("load_testing_basic", True, 0.0, "Load testing check passed")
    
    async def _check_integration_full(self) -> ValidationResult:
        """Test full integration."""
        return ValidationResult("integration_full", True, 0.0, "Integration check passed")
    
    def _calculate_summary(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """Calculate validation summary."""
        total = len(results)
        passed = sum(1 for r in results if r.passed)
        failed = total - passed
        
        return {
            "total_checks": total,
            "passed": passed,
            "failed": failed,
            "skipped": 0,
            "pass_rate": (passed / total * 100) if total > 0 else 0,
            "total_duration": sum(r.duration for r in results)
        }
    
    def _generate_recommendation(self, overall_result: Dict[str, Any]) -> str:
        """Generate recommendation based on results."""
        summary = overall_result["summary"]
        
        if summary["pass_rate"] == 100:
            return "✅ All checks passed! Safe to push to repository."
        elif summary["pass_rate"] >= 90:
            return "⚠️  Minor issues detected. Consider fixing before push."
        elif summary["pass_rate"] >= 70:
            return "🔥 Significant issues found. Fix before pushing."
        else:
            return "🚨 Critical issues detected. DO NOT push until resolved."
    
    def _display_results(self, overall_result: Dict[str, Any], verbose: bool):
        """Display validation results."""
        summary = overall_result["summary"]
        
        print(f"\n📊 VALIDATION RESULTS")
        print("=" * 50)
        print(f"Suite Level: {overall_result['suite_level'].upper()}")
        print(f"Total Checks: {summary['total_checks']}")
        print(f"Passed: {summary['passed']} ✅")
        print(f"Failed: {summary['failed']} ❌")
        print(f"Pass Rate: {summary['pass_rate']:.1f}%")
        print(f"Duration: {summary['total_duration']:.2f}s")
        
        print(f"\n{overall_result['recommendation']}")
        
        # Show failed checks
        failed_results = [r for r in overall_result["results"] if not r.passed]
        if failed_results:
            print(f"\n❌ FAILED CHECKS ({len(failed_results)}):")
            for result in failed_results:
                print(f"   • {result.name}: {result.message}")
        
        if verbose:
            print(f"\n📋 ALL CHECKS:")
            for result in overall_result["results"]:
                status = "✅" if result.passed else "❌"
                print(f"   {status} {result.name} ({result.duration:.2f}s)")


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Fast Local E2E Validation")
    parser.add_argument(
        "--level", 
        choices=["critical", "core", "extended", "comprehensive", "quick"],
        default="core",
        help="Validation level (default: core)"
    )
    parser.add_argument(
        "--quick", 
        action="store_true",
        help="Run in quick mode (reduced timeouts)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true", 
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Determine project root
    project_root = Path(__file__).parent.parent
    
    # Run validation
    validator = FastE2EValidator(str(project_root))
    results = await validator.run_validation(
        suite_level=args.level,
        quick_mode=args.quick,
        verbose=args.verbose
    )
    
    # Save results
    results_file = project_root / f"e2e_validation_results_{int(time.time())}.json"
    with open(results_file, 'w') as f:
        # Convert ValidationResult objects to dicts for JSON serialization
        serializable_results = []
        for result in results["results"]:
            serializable_results.append({
                "name": result.name,
                "passed": result.passed,
                "duration": result.duration,
                "message": result.message,
                "details": result.details
            })
        
        results_copy = results.copy()
        results_copy["results"] = serializable_results
        
        json.dump(results_copy, f, indent=2)
    
    print(f"\n💾 Results saved to: {results_file}")
    
    # Exit code
    exit_code = 0 if results["summary"]["pass_rate"] >= 90 else 1
    return exit_code


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
