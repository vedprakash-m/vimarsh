#!/usr/bin/env python3
"""
Enhanced Local E2E Validation with CI/CD Failure Prevention
===========================================================

This script performs comprehensive validation to catch issues before CI/CD.
It includes dependency validation, test environment consistency checks,
and API contract validation.
"""

import subprocess
import sys
import os
import json
import time
import venv
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional

class ComprehensiveE2EValidator:
    """Enhanced E2E validator that catches CI/CD issues before they happen."""
    
    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = repo_root or Path(__file__).parent.parent
        self.results = {
            "validation_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "tests": {},
            "overall_success": False,
            "issues_found": [],
            "recommendations": []
        }
        print(f"🔍 Enhanced E2E Validation for {self.repo_root}")
        print("=" * 60)
    
    def validate_dependencies(self) -> Dict[str, Any]:
        """Validate all dependencies can be installed in clean environment."""
        print("\n🔧 Dependency Validation (CI Environment Simulation)")
        
        test_result = {
            "name": "dependency_validation",
            "passed": False,
            "duration": 0,
            "message": "",
            "details": {}
        }
        
        start_time = time.time()
        
        try:
            # Test backend dependencies
            backend_result = self._test_backend_dependencies()
            test_result["details"]["backend"] = backend_result
            
            # Test frontend dependencies  
            frontend_result = self._test_frontend_dependencies()
            test_result["details"]["frontend"] = frontend_result
            
            if backend_result["success"] and frontend_result["success"]:
                test_result["passed"] = True
                test_result["message"] = "All dependencies validate successfully"
                print("✅ All dependencies can be installed in clean environment")
            else:
                issues = []
                if not backend_result["success"]:
                    issues.append(f"Backend: {backend_result['error']}")
                if not frontend_result["success"]:
                    issues.append(f"Frontend: {frontend_result['error']}")
                test_result["message"] = f"Dependency issues: {'; '.join(issues)}"
                self.results["issues_found"].extend(issues)
                print(f"❌ Dependency validation failed: {test_result['message']}")
                
        except Exception as e:
            test_result["message"] = f"Dependency validation error: {str(e)}"
            print(f"❌ Dependency validation error: {e}")
            
        test_result["duration"] = time.time() - start_time
        return test_result
    
    def _test_backend_dependencies(self) -> Dict[str, Any]:
        """Test backend dependencies in isolated environment."""
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Create virtual environment
                venv_path = Path(temp_dir) / "test_venv"
                venv.create(venv_path, with_pip=True)
                
                # Get pip path
                if sys.platform == "win32":
                    pip_path = venv_path / "Scripts" / "pip.exe"
                else:
                    pip_path = venv_path / "bin" / "pip"
                
                # Install requirements
                requirements_path = self.repo_root / "backend" / "requirements.txt"
                if not requirements_path.exists():
                    return {"success": False, "error": "requirements.txt not found"}
                
                result = subprocess.run([
                    str(pip_path), "install", "-r", str(requirements_path)
                ], capture_output=True, text=True, timeout=300)
                
                if result.returncode != 0:
                    return {
                        "success": False, 
                        "error": f"pip install failed: {result.stderr}",
                        "stdout": result.stdout,
                        "stderr": result.stderr
                    }
                
                return {"success": True, "message": "Backend dependencies installed successfully"}
                
            except subprocess.TimeoutExpired:
                return {"success": False, "error": "pip install timed out"}
            except Exception as e:
                return {"success": False, "error": f"Exception: {str(e)}"}
    
    def _test_frontend_dependencies(self) -> Dict[str, Any]:
        """Test frontend dependencies."""
        try:
            frontend_path = self.repo_root / "frontend"
            if not frontend_path.exists():
                return {"success": False, "error": "Frontend directory not found"}
            
            package_json = frontend_path / "package.json"
            if not package_json.exists():
                return {"success": False, "error": "package.json not found"}
            
            # Check if package-lock.json exists for npm ci
            package_lock = frontend_path / "package-lock.json"
            if not package_lock.exists():
                return {"success": False, "error": "package-lock.json not found, use npm ci"}
            
            # Test npm ci in frontend directory
            result = subprocess.run([
                "npm", "ci", "--prefix", str(frontend_path)
            ], capture_output=True, text=True, timeout=180)
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": f"npm ci failed: {result.stderr}",
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
            
            return {"success": True, "message": "Frontend dependencies installed successfully"}
            
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "npm ci timed out"}
        except Exception as e:
            return {"success": False, "error": f"Exception: {str(e)}"}
    
    def validate_test_environment(self) -> Dict[str, Any]:
        """Validate test environment matches CI configuration."""
        print("\n🧪 Test Environment Validation")
        
        test_result = {
            "name": "test_environment_validation", 
            "passed": False,
            "duration": 0,
            "message": "",
            "details": {}
        }
        
        start_time = time.time()
        
        try:
            # Check Node.js version
            node_result = self._check_node_version()
            test_result["details"]["node_version"] = node_result
            
            # Check Python version
            python_result = self._check_python_version()
            test_result["details"]["python_version"] = python_result
            
            # Run frontend tests with same configuration as CI
            frontend_test_result = self._run_frontend_tests_ci_mode()
            test_result["details"]["frontend_tests"] = frontend_test_result
            
            # Check for test configuration issues
            test_config_result = self._validate_test_configuration()
            test_result["details"]["test_configuration"] = test_config_result
            
            all_passed = all([
                node_result.get("success", False),
                python_result.get("success", False), 
                frontend_test_result.get("success", False),
                test_config_result.get("success", False)
            ])
            
            if all_passed:
                test_result["passed"] = True
                test_result["message"] = "Test environment matches CI configuration"
                print("✅ Test environment validation passed")
            else:
                issues = []
                for check, result in test_result["details"].items():
                    if not result.get("success", False):
                        issues.append(f"{check}: {result.get('error', 'Failed')}")
                test_result["message"] = f"Environment issues: {'; '.join(issues)}"
                self.results["issues_found"].extend(issues)
                print(f"❌ Test environment validation failed")
                
        except Exception as e:
            test_result["message"] = f"Test environment validation error: {str(e)}"
            print(f"❌ Test environment validation error: {e}")
            
        test_result["duration"] = time.time() - start_time
        return test_result
    
    def _check_node_version(self) -> Dict[str, Any]:
        """Check Node.js version matches CI."""
        try:
            result = subprocess.run(["node", "--version"], capture_output=True, text=True)
            if result.returncode != 0:
                return {"success": False, "error": "Node.js not found"}
            
            version = result.stdout.strip()
            expected_major = "18"  # From CI configuration
            
            if not version.startswith(f"v{expected_major}"):
                return {
                    "success": False,
                    "error": f"Node.js version mismatch. Expected v{expected_major}.x, got {version}",
                    "current": version,
                    "expected": f"v{expected_major}.x"
                }
            
            return {"success": True, "version": version}
            
        except Exception as e:
            return {"success": False, "error": f"Error checking Node.js version: {str(e)}"}
    
    def _check_python_version(self) -> Dict[str, Any]:
        """Check Python version matches CI."""
        try:
            current_version = f"{sys.version_info.major}.{sys.version_info.minor}"
            expected_version = "3.12"  # From CI configuration
            
            if current_version != expected_version:
                return {
                    "success": False,
                    "error": f"Python version mismatch. Expected {expected_version}, got {current_version}",
                    "current": current_version,
                    "expected": expected_version
                }
            
            return {"success": True, "version": current_version}
            
        except Exception as e:
            return {"success": False, "error": f"Error checking Python version: {str(e)}"}
    
    def _run_frontend_tests_ci_mode(self) -> Dict[str, Any]:
        """Run frontend tests with CI configuration."""
        try:
            frontend_path = self.repo_root / "frontend"
            
            # Use same test command as CI
            result = subprocess.run([
                "npm", "run", "test:coverage", "--prefix", str(frontend_path)
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": "Frontend tests failed in CI mode",
                    "stdout": result.stdout[-1000:],  # Last 1000 chars
                    "stderr": result.stderr[-1000:]
                }
            
            return {"success": True, "message": "Frontend tests passed in CI mode"}
            
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Frontend tests timed out"}
        except Exception as e:
            return {"success": False, "error": f"Error running frontend tests: {str(e)}"}
    
    def _validate_test_configuration(self) -> Dict[str, Any]:
        """Validate test configuration files."""
        try:
            issues = []
            
            # Check for deprecated test utilities
            test_files = list((self.repo_root / "frontend" / "src").rglob("*.test.ts")) + \
                        list((self.repo_root / "frontend" / "src").rglob("*.test.tsx"))
            
            for test_file in test_files:
                try:
                    content = test_file.read_text()
                    if "ReactDOMTestUtils" in content and "act" in content:
                        issues.append(f"{test_file.name}: Uses deprecated ReactDOMTestUtils.act")
                except Exception:
                    continue
            
            # Check jest configuration
            jest_config = self.repo_root / "frontend" / "jest.config.js"
            package_json = self.repo_root / "frontend" / "package.json"
            
            if package_json.exists():
                try:
                    with open(package_json) as f:
                        package_data = json.load(f)
                        jest_config_in_package = package_data.get("jest", {})
                        if not jest_config_in_package and not jest_config.exists():
                            issues.append("No Jest configuration found")
                except Exception:
                    pass
            
            if issues:
                return {
                    "success": False,
                    "error": f"Test configuration issues: {'; '.join(issues)}",
                    "issues": issues
                }
            
            return {"success": True, "message": "Test configuration is valid"}
            
        except Exception as e:
            return {"success": False, "error": f"Error validating test configuration: {str(e)}"}
    
    def validate_api_contracts(self) -> Dict[str, Any]:
        """Validate API contracts and mock alignment."""
        print("\n🔌 API Contract Validation")
        
        test_result = {
            "name": "api_contract_validation",
            "passed": False,
            "duration": 0,
            "message": "",
            "details": {}
        }
        
        start_time = time.time()
        
        try:
            # Check spiritual guidance API endpoint
            spiritual_api_result = self._validate_spiritual_guidance_api()
            test_result["details"]["spiritual_guidance_api"] = spiritual_api_result
            
            # Validate test mocks against API contracts
            mock_validation_result = self._validate_test_mocks()
            test_result["details"]["mock_validation"] = mock_validation_result
            
            if spiritual_api_result["success"] and mock_validation_result["success"]:
                test_result["passed"] = True
                test_result["message"] = "API contracts and mocks are aligned"
                print("✅ API contract validation passed")
            else:
                issues = []
                if not spiritual_api_result["success"]:
                    issues.append(f"API: {spiritual_api_result['error']}")
                if not mock_validation_result["success"]:
                    issues.append(f"Mocks: {mock_validation_result['error']}")
                test_result["message"] = f"API contract issues: {'; '.join(issues)}"
                self.results["issues_found"].extend(issues)
                print(f"❌ API contract validation failed")
                
        except Exception as e:
            test_result["message"] = f"API contract validation error: {str(e)}"
            print(f"❌ API contract validation error: {e}")
            
        test_result["duration"] = time.time() - start_time
        return test_result
    
    def _validate_spiritual_guidance_api(self) -> Dict[str, Any]:
        """Validate spiritual guidance API contract."""
        try:
            # Check if backend directory exists
            backend_dir = self.repo_root / "backend"
            if not backend_dir.exists():
                return {"success": False, "error": "Backend directory not found"}
            
            # Check for function_app.py (main API file)
            function_app_path = backend_dir / "function_app.py"
            if not function_app_path.exists():
                return {"success": False, "error": "function_app.py not found"}
            
            # Check function_app.py for expected endpoints
            try:
                content = function_app_path.read_text()
                if "spiritual_guidance" not in content:
                    return {"success": False, "error": "spiritual_guidance endpoint not found"}
            except Exception as e:
                return {"success": False, "error": f"Error reading function_app.py: {str(e)}"}
            
            return {"success": True, "message": "API structure is valid"}
            
        except Exception as e:
            return {"success": False, "error": f"Error validating API: {str(e)}"}
    
    def _validate_test_mocks(self) -> Dict[str, Any]:
        """Validate test mocks align with API contracts."""
        try:
            issues = []
            
            # Find test files with fetch mocks
            test_files = list((self.repo_root / "frontend" / "src").rglob("*.test.ts")) + \
                        list((self.repo_root / "frontend" / "src").rglob("*.test.tsx"))
            
            for test_file in test_files:
                try:
                    content = test_file.read_text()
                    if "global.fetch" in content and "spiritual_guidance" in content:
                        # Check if mock responses match expected API contract
                        if '"ok": false' in content and '"status": 500' in content:
                            # This is the pattern that caused CI failure
                            issues.append(f"{test_file.name}: Mock returns 500 error which may cause test failures")
                except Exception:
                    continue
            
            if issues:
                return {
                    "success": False,
                    "error": f"Mock validation issues: {'; '.join(issues)}",
                    "issues": issues
                }
            
            return {"success": True, "message": "Test mocks are properly configured"}
            
        except Exception as e:
            return {"success": False, "error": f"Error validating mocks: {str(e)}"}
    
    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run all validation tests."""
        print("🚀 Starting Comprehensive E2E Validation")
        
        # Run all validation tests
        tests = [
            self.validate_dependencies,
            self.validate_test_environment,
            self.validate_api_contracts
        ]
        
        for test_func in tests:
            test_result = test_func()
            self.results["tests"][test_result["name"]] = test_result
        
        # Determine overall success
        all_passed = all(test["passed"] for test in self.results["tests"].values())
        self.results["overall_success"] = all_passed
        
        # Generate recommendations
        if not all_passed:
            self._generate_recommendations()
        
        # Print summary
        self._print_summary()
        
        # Save results
        self._save_results()
        
        return self.results
    
    def _generate_recommendations(self):
        """Generate actionable recommendations based on failures."""
        recommendations = []
        
        for test_name, test_result in self.results["tests"].items():
            if not test_result["passed"]:
                if test_name == "dependency_validation":
                    recommendations.append("Fix dependency issues in requirements.txt or package.json")
                    recommendations.append("Test dependencies in clean environment before CI")
                elif test_name == "test_environment_validation":
                    recommendations.append("Align local development environment with CI configuration")
                    recommendations.append("Update Node.js/Python versions to match CI")
                elif test_name == "api_contract_validation":
                    recommendations.append("Fix API contract mismatches")
                    recommendations.append("Update test mocks to match real API responses")
        
        if self.results["issues_found"]:
            recommendations.append("Address all identified issues before pushing to CI")
            recommendations.append("Consider adding pre-commit hooks for validation")
        
        self.results["recommendations"] = recommendations
    
    def _print_summary(self):
        """Print validation summary."""
        print("\n" + "="*60)
        print("📊 VALIDATION SUMMARY")
        print("="*60)
        
        for test_name, test_result in self.results["tests"].items():
            status = "✅ PASS" if test_result["passed"] else "❌ FAIL"
            duration = f"{test_result['duration']:.2f}s"
            print(f"{status} {test_name.replace('_', ' ').title()} ({duration})")
            if not test_result["passed"]:
                print(f"    → {test_result['message']}")
        
        print("\n" + "-"*60)
        overall_status = "✅ SUCCESS" if self.results["overall_success"] else "❌ FAILURE"
        print(f"Overall Status: {overall_status}")
        
        if self.results["issues_found"]:
            print(f"\n🔍 Issues Found ({len(self.results['issues_found'])}):")
            for issue in self.results["issues_found"]:
                print(f"  • {issue}")
        
        if self.results["recommendations"]:
            print(f"\n💡 Recommendations:")
            for rec in self.results["recommendations"]:
                print(f"  • {rec}")
    
    def _save_results(self):
        """Save validation results to file."""
        timestamp = int(time.time())
        results_file = self.repo_root / f"e2e_validation_results_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n📄 Results saved to: {results_file}")

def main():
    """Main execution function."""
    try:
        validator = ComprehensiveE2EValidator()
        results = validator.run_comprehensive_validation()
        
        # Exit with appropriate code
        sys.exit(0 if results["overall_success"] else 1)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Validation interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n💥 Validation failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
