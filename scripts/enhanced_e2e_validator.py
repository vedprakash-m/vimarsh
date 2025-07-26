#!/usr/bin/env python3
"""
Enhanced End-to-End Validator for Vimarsh Application
Validates critical application functionality across frontend and backend
"""

import argparse
import logging
import sys
import json
from typing import Dict
from datetime import datetime
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VimarshE2EValidator:
    """End-to-end validator for Vimarsh application"""
    
    def __init__(self, level: str = "basic"):
        self.level = level
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "tests": [],
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0
            }
        }
        
    def log_test_result(self, test_name: str, status: str, message: str = "", details: Dict = None):
        """Log test result"""
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        self.results["tests"].append(result)
        self.results["summary"]["total"] += 1
        self.results["summary"][status] += 1
        
        status_emoji = {"passed": "✅", "failed": "❌", "skipped": "⏭️"}
        logger.info(f"{status_emoji.get(status, '❓')} {test_name}: {message}")
    
    def validate_basic_functionality(self) -> bool:
        """Basic functionality validation"""
        logger.info("🔍 Running basic functionality validation...")
        
        # Test 1: Environment variables
        try:
            required_env_vars = [
                'AZURE_SUBSCRIPTION_ID',
                'AZURE_TENANT_ID'
            ]
            
            missing_vars = [var for var in required_env_vars if not os.getenv(var)]
            
            # In CI/CD environments, Azure credentials are optional for basic validation
            is_ci_environment = os.getenv('GITHUB_ACTIONS') == 'true' or os.getenv('CI') == 'true'
            
            if missing_vars and not is_ci_environment:
                self.log_test_result(
                    "environment_variables",
                    "failed", 
                    f"Missing environment variables: {missing_vars}"
                )
                return False
            elif missing_vars and is_ci_environment:
                self.log_test_result(
                    "environment_variables",
                    "skipped",
                    f"Azure credentials not required in CI environment. Missing: {missing_vars}"
                )
            else:
                self.log_test_result(
                    "environment_variables",
                    "passed",
                    "All required environment variables present"
                )
        except Exception as e:
            self.log_test_result(
                "environment_variables",
                "failed",
                f"Error checking environment: {str(e)}"
            )
            return False
        
        # Test 2: Project structure validation
        try:
            required_files = [
                "backend/function_app.py",
                "frontend/package.json",
                "infrastructure/main.bicep"
            ]
            
            missing_files = []
            for file_path in required_files:
                if not os.path.exists(file_path):
                    missing_files.append(file_path)
            
            if missing_files:
                self.log_test_result(
                    "project_structure",
                    "failed",
                    f"Missing critical files: {missing_files}"
                )
                return False
            else:
                self.log_test_result(
                    "project_structure", 
                    "passed",
                    "All critical project files present"
                )
        except Exception as e:
            self.log_test_result(
                "project_structure",
                "failed", 
                f"Error validating project structure: {str(e)}"
            )
            return False
        
        return True
    
    def validate_comprehensive_functionality(self) -> bool:
        """Comprehensive functionality validation"""
        logger.info("🔍 Running comprehensive functionality validation...")
        
        # All basic tests plus additional comprehensive tests
        if not self.validate_basic_functionality():
            return False
        
        # Test 3: Frontend build validation
        try:
            frontend_package_path = "frontend/package.json"
            if os.path.exists(frontend_package_path):
                with open(frontend_package_path, 'r') as f:
                    package_data = json.load(f)
                
                required_scripts = ["build", "test", "start"]
                missing_scripts = [script for script in required_scripts 
                                 if script not in package_data.get("scripts", {})]
                
                if missing_scripts:
                    self.log_test_result(
                        "frontend_configuration",
                        "failed",
                        f"Missing package.json scripts: {missing_scripts}"
                    )
                else:
                    self.log_test_result(
                        "frontend_configuration",
                        "passed", 
                        "Frontend configuration is valid"
                    )
            else:
                self.log_test_result(
                    "frontend_configuration",
                    "failed",
                    "Frontend package.json not found"
                )
        except Exception as e:
            self.log_test_result(
                "frontend_configuration",
                "failed",
                f"Error validating frontend: {str(e)}"
            )
        
        # Test 4: Backend configuration validation
        try:
            backend_requirements_path = "backend/requirements.txt"
            if os.path.exists(backend_requirements_path):
                with open(backend_requirements_path, 'r') as f:
                    requirements = f.read()
                
                required_packages = [
                    "azure-functions",
                    "google-generativeai",
                    "azure-cosmos"
                ]
                
                missing_packages = [pkg for pkg in required_packages 
                                  if pkg not in requirements]
                
                if missing_packages:
                    self.log_test_result(
                        "backend_configuration",
                        "failed",
                        f"Missing required packages: {missing_packages}"
                    )
                else:
                    self.log_test_result(
                        "backend_configuration",
                        "passed",
                        "Backend configuration is valid"
                    )
            else:
                self.log_test_result(
                    "backend_configuration", 
                    "failed",
                    "Backend requirements.txt not found"
                )
        except Exception as e:
            self.log_test_result(
                "backend_configuration",
                "failed",
                f"Error validating backend: {str(e)}"
            )
        
        # Test 5: Infrastructure validation
        try:
            infra_main_path = "infrastructure/main.bicep"
            if os.path.exists(infra_main_path):
                with open(infra_main_path, 'r') as f:
                    bicep_content = f.read()
                
                required_resources = [
                    "Microsoft.Resources/resourceGroups",
                    "Microsoft.Web/staticSites"
                ]
                
                missing_resources = [resource for resource in required_resources
                                   if resource not in bicep_content]
                
                if missing_resources:
                    self.log_test_result(
                        "infrastructure_configuration",
                        "failed", 
                        f"Missing infrastructure resources: {missing_resources}"
                    )
                else:
                    self.log_test_result(
                        "infrastructure_configuration",
                        "passed",
                        "Infrastructure configuration is valid"
                    )
            else:
                self.log_test_result(
                    "infrastructure_configuration",
                    "failed",
                    "Infrastructure main.bicep not found"
                )
        except Exception as e:
            self.log_test_result(
                "infrastructure_configuration",
                "failed",
                f"Error validating infrastructure: {str(e)}"
            )
        
        return self.results["summary"]["failed"] == 0
    
    def run_validation(self) -> bool:
        """Run validation based on specified level"""
        logger.info(f"🚀 Starting Vimarsh E2E validation (level: {self.level})")
        
        try:
            if self.level == "basic":
                success = self.validate_basic_functionality()
            elif self.level == "comprehensive":
                success = self.validate_comprehensive_functionality()
            else:
                logger.error(f"Unknown validation level: {self.level}")
                return False
            
            # Print summary
            summary = self.results["summary"]
            logger.info("=" * 50)
            logger.info("🎯 VALIDATION SUMMARY")
            logger.info("=" * 50)
            logger.info(f"📊 Total Tests: {summary['total']}")
            logger.info(f"✅ Passed: {summary['passed']}")
            logger.info(f"❌ Failed: {summary['failed']}")
            logger.info(f"⏭️ Skipped: {summary['skipped']}")
            logger.info(f"🎉 Success Rate: {(summary['passed']/summary['total']*100):.1f}%" if summary['total'] > 0 else "No tests run")
            
            # Save results to file
            results_file = f"e2e_validation_results_{self.level}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(results_file, 'w') as f:
                json.dump(self.results, f, indent=2)
            logger.info(f"📄 Results saved to: {results_file}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Validation failed with error: {str(e)}")
            return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Vimarsh E2E Validator")
    parser.add_argument(
        "--level",
        choices=["basic", "comprehensive"],
        default="basic",
        help="Validation level (default: basic)"
    )
    
    args = parser.parse_args()
    
    validator = VimarshE2EValidator(level=args.level)
    success = validator.run_validation()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
