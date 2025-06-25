"""
Test runner for all infrastructure and deployment tests.

This module provides a comprehensive test suite runner for validating
infrastructure, deployment scripts, documentation, and integration tests.
"""

import pytest
import sys
from pathlib import Path


def run_infrastructure_tests():
    """Run infrastructure validation tests."""
    test_dir = Path(__file__).parent
    
    print("🏗️ Running Infrastructure Tests...")
    print("=" * 50)
    
    # Run Bicep validation tests
    bicep_tests = test_dir / "infrastructure" / "test_bicep_validation.py"
    if bicep_tests.exists():
        result = pytest.main([str(bicep_tests), "-v", "--tb=short"])
        if result != 0:
            print("❌ Infrastructure validation tests failed!")
            return False
    
    print("✅ Infrastructure tests passed!")
    return True


def run_deployment_tests():
    """Run deployment script tests."""
    test_dir = Path(__file__).parent
    
    print("\n🚀 Running Deployment Tests...")
    print("=" * 50)
    
    # Run deployment script tests
    deployment_tests = test_dir / "deployment" / "test_deployment_scripts.py"
    if deployment_tests.exists():
        result = pytest.main([str(deployment_tests), "-v", "--tb=short"])
        if result != 0:
            print("❌ Deployment script tests failed!")
            return False
    
    print("✅ Deployment tests passed!")
    return True


def run_documentation_tests():
    """Run documentation validation tests."""
    test_dir = Path(__file__).parent
    
    print("\n📚 Running Documentation Tests...")
    print("=" * 50)
    
    # Run API documentation tests
    api_doc_tests = test_dir / "documentation" / "test_api_documentation.py"
    if api_doc_tests.exists():
        result = pytest.main([str(api_doc_tests), "-v", "--tb=short"])
        if result != 0:
            print("❌ Documentation tests failed!")
            return False
    
    print("✅ Documentation tests passed!")
    return True


def run_integration_tests():
    """Run integration tests."""
    test_dir = Path(__file__).parent
    
    print("\n🔄 Running Integration Tests...")
    print("=" * 50)
    
    # Run deployment integration tests
    integration_tests = test_dir / "integration" / "test_deployment_integration.py"
    if integration_tests.exists():
        result = pytest.main([str(integration_tests), "-v", "--tb=short"])
        if result != 0:
            print("❌ Integration tests failed!")
            return False
    
    print("✅ Integration tests passed!")
    return True


def run_all_tests():
    """Run all infrastructure and deployment tests."""
    print("🕉️ Vimarsh Infrastructure & Deployment Test Suite")
    print("=" * 60)
    print("Running comprehensive validation of infrastructure, deployment,")
    print("documentation, and integration components...")
    print("=" * 60)
    
    # Track test results
    results = {
        "infrastructure": run_infrastructure_tests(),
        "deployment": run_deployment_tests(), 
        "documentation": run_documentation_tests(),
        "integration": run_integration_tests()
    }
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_type, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_type.upper():<15} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("🎉 ALL TESTS PASSED! Infrastructure and deployment ready for production.")
        print("🙏 The divine wisdom of Lord Krishna guides our code to success!")
        return 0
    else:
        print("⚠️  SOME TESTS FAILED! Please review and fix issues before deployment.")
        print("📝 Check test output above for specific failure details.")
        return 1


if __name__ == "__main__":
    # Allow running specific test suites
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        
        if test_type == "infrastructure":
            sys.exit(0 if run_infrastructure_tests() else 1)
        elif test_type == "deployment":
            sys.exit(0 if run_deployment_tests() else 1)
        elif test_type == "documentation":
            sys.exit(0 if run_documentation_tests() else 1)
        elif test_type == "integration":
            sys.exit(0 if run_integration_tests() else 1)
        else:
            print(f"Unknown test type: {test_type}")
            print("Available options: infrastructure, deployment, documentation, integration")
            sys.exit(1)
    else:
        # Run all tests
        sys.exit(run_all_tests())
