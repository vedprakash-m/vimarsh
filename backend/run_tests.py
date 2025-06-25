"""
Comprehensive test suite runner for Vimarsh backend components.

This script runs all unit tests, integration tests, and performance tests
for the Vimarsh spiritual guidance platform backend.
"""

import sys
import os
import pytest
import time
from pathlib import Path
import subprocess
import json

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Test configuration
TEST_SUITES = {
    "unit": {
        "description": "Unit tests for individual components",
        "paths": [
            "tests/test_spiritual_guidance_api.py",
            "tests/test_rag_pipeline.py", 
            "tests/test_llm_integration.py",
            "tests/test_voice_interface.py"
        ],
        "markers": "not integration and not performance"
    },
    "integration": {
        "description": "Integration tests for RAG/LLM workflows",
        "paths": [
            "tests/test_integration_rag_llm.py",
            "tests/test_llm_workflow_integration.py",
            "tests/test_end_to_end_workflow.py"
        ],
        "markers": "integration"
    },
    "performance": {
        "description": "Performance and load tests",
        "paths": [
            "tests/test_spiritual_guidance_api.py",
            "tests/test_integration_rag_llm.py",
            "tests/test_end_to_end_workflow.py"
        ],
        "markers": "performance"
    },
    "all": {
        "description": "All tests including unit, integration, and performance",
        "paths": ["tests/"],
        "markers": ""
    }
}


def run_test_suite(suite_name: str, verbose: bool = True, coverage: bool = True) -> dict:
    """
    Run a specific test suite and return results.
    
    Args:
        suite_name: Name of the test suite to run
        verbose: Whether to run in verbose mode
        coverage: Whether to generate coverage report
        
    Returns:
        Dictionary with test results
    """
    if suite_name not in TEST_SUITES:
        raise ValueError(f"Unknown test suite: {suite_name}. Available: {list(TEST_SUITES.keys())}")
    
    suite = TEST_SUITES[suite_name]
    print(f"\n🧪 Running {suite_name} tests: {suite['description']}")
    print("=" * 60)
    
    # Build pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add paths
    cmd.extend(suite["paths"])
    
    # Add markers
    if suite["markers"]:
        cmd.extend(["-m", suite["markers"]])
    
    # Add verbosity
    if verbose:
        cmd.append("-v")
    
    # Add coverage
    if coverage:
        cmd.extend([
            "--cov=spiritual_guidance",
            "--cov=rag_pipeline", 
            "--cov=llm",
            "--cov=voice",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov"
        ])
    
    # Add other useful options
    cmd.extend([
        "--tb=short",  # Shorter traceback format
        "--strict-markers",  # Strict marker checking
        "--durations=10",  # Show 10 slowest tests
        "-x"  # Stop on first failure for quick feedback
    ])
    
    # Run the tests
    start_time = time.time()
    try:
        result = subprocess.run(cmd, cwd=backend_dir, capture_output=True, text=True)
        elapsed_time = time.time() - start_time
        
        return {
            "suite": suite_name,
            "success": result.returncode == 0,
            "elapsed_time": elapsed_time,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode
        }
    except Exception as e:
        return {
            "suite": suite_name,
            "success": False,
            "elapsed_time": time.time() - start_time,
            "error": str(e),
            "return_code": -1
        }


def check_test_dependencies() -> bool:
    """Check if all required test dependencies are available."""
    print("🔍 Checking test dependencies...")
    
    required_packages = [
        "pytest",
        "pytest-cov",
        "pytest-asyncio",
        "pytest-mock"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("Please install them with: pip install " + " ".join(missing_packages))
        return False
    
    print("✅ All test dependencies are available")
    return True


def run_linting_and_formatting() -> dict:
    """Run code linting and formatting checks."""
    print("\n🔧 Running code quality checks...")
    
    # Check if tools are available
    tools = {
        "flake8": "Code linting",
        "black": "Code formatting", 
        "isort": "Import sorting"
    }
    
    results = {}
    
    for tool, description in tools.items():
        try:
            print(f"Running {tool} ({description})...")
            result = subprocess.run(
                [tool, "--check", "." if tool != "flake8" else "--exclude=venv,__pycache__ ."],
                cwd=backend_dir,
                capture_output=True,
                text=True
            )
            results[tool] = {
                "success": result.returncode == 0,
                "output": result.stdout + result.stderr
            }
        except FileNotFoundError:
            results[tool] = {
                "success": False,
                "output": f"{tool} not found. Install with: pip install {tool}"
            }
    
    return results


def generate_test_report(results: list) -> str:
    """Generate a comprehensive test report."""
    report = [
        "\n" + "=" * 80,
        "🕉️  VIMARSH BACKEND TEST REPORT",
        "=" * 80,
        f"Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        ""
    ]
    
    total_time = sum(r.get("elapsed_time", 0) for r in results)
    successful_suites = sum(1 for r in results if r.get("success", False))
    total_suites = len(results)
    
    report.extend([
        f"Total test suites: {total_suites}",
        f"Successful suites: {successful_suites}",
        f"Failed suites: {total_suites - successful_suites}",
        f"Total execution time: {total_time:.2f} seconds",
        ""
    ])
    
    # Individual suite results
    for result in results:
        status = "✅ PASSED" if result.get("success", False) else "❌ FAILED"
        suite_name = result.get("suite", "Unknown")
        elapsed = result.get("elapsed_time", 0)
        
        report.extend([
            f"{status} {suite_name.upper()} ({elapsed:.2f}s)",
            "-" * 40
        ])
        
        if not result.get("success", False):
            if "error" in result:
                report.append(f"Error: {result['error']}")
            elif "stderr" in result and result["stderr"]:
                report.append(f"Error output: {result['stderr'][:500]}...")
        
        report.append("")
    
    # Quality recommendations
    report.extend([
        "🎯 Quality Standards:",
        "- All tests should pass with >95% coverage",
        "- Response times should meet performance targets", 
        "- Spiritual authenticity must be maintained",
        "- Error handling should be comprehensive",
        ""
    ])
    
    return "\n".join(report)


def main():
    """Main test runner function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Vimarsh Backend Test Runner")
    parser.add_argument(
        "suite", 
        nargs="?", 
        default="unit",
        choices=list(TEST_SUITES.keys()),
        help="Test suite to run"
    )
    parser.add_argument(
        "--all", 
        action="store_true", 
        help="Run all test suites"
    )
    parser.add_argument(
        "--no-coverage", 
        action="store_true",
        help="Skip coverage reporting"
    )
    parser.add_argument(
        "--quiet", 
        action="store_true",
        help="Run in quiet mode"
    )
    parser.add_argument(
        "--lint", 
        action="store_true",
        help="Run linting and formatting checks"
    )
    
    args = parser.parse_args()
    
    print("🕉️  Vimarsh Backend Test Suite")
    print("Divine wisdom through comprehensive testing")
    print("=" * 50)
    
    # Check dependencies
    if not check_test_dependencies():
        sys.exit(1)
    
    # Run linting if requested
    if args.lint:
        lint_results = run_linting_and_formatting()
        for tool, result in lint_results.items():
            status = "✅" if result["success"] else "❌"
            print(f"{status} {tool}: {'PASSED' if result['success'] else 'FAILED'}")
            if not result["success"]:
                print(f"   {result['output'][:200]}...")
        print()
    
    # Determine which suites to run
    suites_to_run = list(TEST_SUITES.keys())[:-1] if args.all else [args.suite]  # Exclude 'all' when running all
    
    # Run test suites
    results = []
    for suite in suites_to_run:
        result = run_test_suite(
            suite, 
            verbose=not args.quiet,
            coverage=not args.no_coverage
        )
        results.append(result)
        
        # Print immediate result
        status = "✅ PASSED" if result["success"] else "❌ FAILED"
        print(f"\n{status} {suite.upper()} suite completed in {result['elapsed_time']:.2f}s")
        
        # Show errors immediately for failed tests
        if not result["success"] and not args.quiet:
            if "stderr" in result and result["stderr"]:
                print("Error details:")
                print(result["stderr"][:1000])
            if "stdout" in result and "FAILED" in result["stdout"]:
                print("Test output:")
                print(result["stdout"][-1000:])
    
    # Generate and display final report
    report = generate_test_report(results)
    print(report)
    
    # Save report to file
    report_file = backend_dir / "test_report.txt"
    report_file.write_text(report)
    print(f"📄 Detailed report saved to: {report_file}")
    
    # Exit with appropriate code
    all_passed = all(r.get("success", False) for r in results)
    if all_passed:
        print("\n🎉 All tests passed! The divine code flows harmoniously.")
    else:
        print("\n⚠️  Some tests failed. May wisdom guide the path to resolution.")
    
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
