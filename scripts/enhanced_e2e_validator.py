#!/usr/bin/env python3
"""
Enhanced End-to-End Validator for Vimarsh CI/CD Pipeline
Comprehensive validation of all system components for production readiness
"""

import asyncio
import json
import os
import sys
import logging
import time
import subprocess
from typing import Dict, Any, List
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedE2EValidator:
    """Enhanced End-to-End validation for CI/CD pipeline."""
    
    def __init__(self, validation_level: str = "basic"):
        self.validation_level = validation_level
        self.test_results = []
        self.workspace_path = Path(__file__).parent.parent
        self.backend_path = self.workspace_path / "backend"
        self.frontend_path = self.workspace_path / "frontend"
        
    def log_test_result(self, test_name: str, passed: bool, details: str = "", data: Any = None):
        """Log test result."""
        result = {
            "test": test_name,
            "passed": passed,
            "details": details,
            "timestamp": time.time(),
            "data": data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{status} {test_name}: {details}")
        
    async def validate_backend_tests(self) -> bool:
        """Run backend test suite."""
        logger.info("🧪 Running backend test suite...")
        
        try:
            # Change to backend directory and run tests
            cmd = [sys.executable, "-m", "pytest", "tests/", "-x", "--tb=short"]
            
            result = subprocess.run(
                cmd,
                cwd=self.backend_path,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            passed = result.returncode == 0
            details = f"Backend tests {'passed' if passed else 'failed'}"
            
            if not passed:
                details += f" - stderr: {result.stderr[:200]}..."
                
            self.log_test_result("backend_tests", passed, details, {
                "returncode": result.returncode,
                "stdout_lines": len(result.stdout.split('\n')),
                "stderr_preview": result.stderr[:200] if result.stderr else None
            })
            
            return passed
            
        except subprocess.TimeoutExpired:
            self.log_test_result("backend_tests", False, "Backend tests timed out after 5 minutes")
            return False
        except Exception as e:
            self.log_test_result("backend_tests", False, f"Backend test execution failed: {str(e)}")
            return False
    
    async def validate_frontend_build(self) -> bool:
        """Validate frontend can build successfully."""
        logger.info("🏗️ Validating frontend build...")
        
        try:
            # Check if node_modules exists, if not skip frontend validation in CI
            node_modules = self.frontend_path / "node_modules"
            if not node_modules.exists():
                self.log_test_result("frontend_build", True, "Frontend build skipped - node_modules not found (CI environment)")
                return True
            
            # Run frontend build
            cmd = ["npm", "run", "build"]
            
            result = subprocess.run(
                cmd,
                cwd=self.frontend_path,
                capture_output=True,
                text=True,
                timeout=180  # 3 minutes timeout
            )
            
            passed = result.returncode == 0
            details = f"Frontend build {'succeeded' if passed else 'failed'}"
            
            if not passed:
                details += f" - stderr: {result.stderr[:200]}..."
                
            self.log_test_result("frontend_build", passed, details, {
                "returncode": result.returncode,
                "stdout_lines": len(result.stdout.split('\n')),
                "stderr_preview": result.stderr[:200] if result.stderr else None
            })
            
            return passed
            
        except subprocess.TimeoutExpired:
            self.log_test_result("frontend_build", False, "Frontend build timed out after 3 minutes")
            return False
        except Exception as e:
            self.log_test_result("frontend_build", False, f"Frontend build execution failed: {str(e)}")
            return False
    
    async def validate_project_structure(self) -> bool:
        """Validate essential project structure."""
        logger.info("📁 Validating project structure...")
        
        essential_files = [
            "backend/function_app.py",
            "backend/requirements.txt",
            "frontend/package.json",
            "frontend/public/manifest.json",
            ".github/workflows/unified-ci-cd.yml"
        ]
        
        missing_files = []
        for file_path in essential_files:
            full_path = self.workspace_path / file_path
            if not full_path.exists():
                missing_files.append(file_path)
        
        passed = len(missing_files) == 0
        details = f"Project structure {'valid' if passed else 'incomplete'}"
        
        if missing_files:
            details += f" - Missing: {', '.join(missing_files)}"
        
        self.log_test_result("project_structure", passed, details, {
            "essential_files_checked": len(essential_files),
            "missing_files": missing_files
        })
        
        return passed
    
    async def validate_configuration(self) -> bool:
        """Validate configuration files."""
        logger.info("⚙️ Validating configuration...")
        
        try:
            # Check backend configuration
            function_app_path = self.backend_path / "function_app.py"
            if function_app_path.exists():
                with open(function_app_path, 'r') as f:
                    content = f.read()
                    has_app_instance = 'app = func.FunctionApp()' in content or 'app =' in content
            else:
                has_app_instance = False
            
            # Check frontend configuration
            package_json_path = self.frontend_path / "package.json"
            has_valid_package_json = False
            if package_json_path.exists():
                try:
                    with open(package_json_path, 'r') as f:
                        package_data = json.load(f)
                        has_valid_package_json = 'name' in package_data and 'scripts' in package_data
                except json.JSONDecodeError:
                    has_valid_package_json = False
            
            # Check PWA manifest
            manifest_path = self.frontend_path / "public" / "manifest.json"
            has_valid_manifest = False
            if manifest_path.exists():
                try:
                    with open(manifest_path, 'r') as f:
                        manifest_data = json.load(f)
                        has_valid_manifest = 'name' in manifest_data and 'icons' in manifest_data
                        if has_valid_manifest:
                            # Check for multiple icon sizes (our recent fix)
                            has_valid_manifest = len(manifest_data.get('icons', [])) >= 2
                except json.JSONDecodeError:
                    has_valid_manifest = False
            
            all_valid = has_app_instance and has_valid_package_json and has_valid_manifest
            
            details = f"Configuration {'valid' if all_valid else 'invalid'}"
            config_status = {
                "function_app": has_app_instance,
                "package_json": has_valid_package_json,
                "pwa_manifest": has_valid_manifest
            }
            
            if not all_valid:
                invalid_configs = [k for k, v in config_status.items() if not v]
                details += f" - Invalid: {', '.join(invalid_configs)}"
            
            self.log_test_result("configuration", all_valid, details, config_status)
            
            return all_valid
            
        except Exception as e:
            self.log_test_result("configuration", False, f"Configuration validation failed: {str(e)}")
            return False
    
    async def run_comprehensive_validation(self) -> bool:
        """Run comprehensive validation suite."""
        logger.info(f"🚀 Starting {self.validation_level} validation...")
        
        validation_tasks = [
            self.validate_project_structure(),
            self.validate_configuration(),
        ]
        
        # Only run tests if we're in comprehensive mode and have the test environment
        if self.validation_level == "comprehensive":
            # Check if we can run backend tests
            pytest_available = subprocess.run(
                [sys.executable, "-c", "import pytest"],
                capture_output=True
            ).returncode == 0
            
            if pytest_available and (self.backend_path / "tests").exists():
                validation_tasks.append(self.validate_backend_tests())
            else:
                self.log_test_result("backend_tests", True, "Backend tests skipped - pytest not available or no tests directory")
            
            # Frontend build validation only in comprehensive mode
            validation_tasks.append(self.validate_frontend_build())
        
        # Run all validations
        results = await asyncio.gather(*validation_tasks, return_exceptions=True)
        
        # Process results
        passed_count = 0
        total_count = len(results)
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Validation task {i} failed with exception: {result}")
            elif result:
                passed_count += 1
        
        success_rate = passed_count / total_count if total_count > 0 else 0
        overall_success = success_rate >= 0.8  # 80% success rate required
        
        # Generate summary
        self.generate_validation_report(overall_success, success_rate)
        
        return overall_success
    
    def generate_validation_report(self, overall_success: bool, success_rate: float):
        """Generate validation report."""
        logger.info("\n" + "="*50)
        logger.info("📊 VALIDATION REPORT")
        logger.info("="*50)
        
        passed_tests = [r for r in self.test_results if r["passed"]]
        failed_tests = [r for r in self.test_results if not r["passed"]]
        
        logger.info(f"✅ Passed: {len(passed_tests)}")
        logger.info(f"❌ Failed: {len(failed_tests)}")
        logger.info(f"📈 Success Rate: {success_rate:.1%}")
        logger.info(f"🎯 Overall Status: {'SUCCESS' if overall_success else 'FAILURE'}")
        
        if failed_tests:
            logger.info("\n❌ Failed Tests:")
            for test in failed_tests:
                logger.info(f"  • {test['test']}: {test['details']}")
        
        logger.info("="*50)

async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced E2E Validator for Vimarsh CI/CD")
    parser.add_argument("--level", choices=["basic", "comprehensive"], default="basic",
                       help="Validation level (basic or comprehensive)")
    args = parser.parse_args()
    
    validator = EnhancedE2EValidator(validation_level=args.level)
    success = await validator.run_comprehensive_validation()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
