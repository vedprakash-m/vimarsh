#!/usr/bin/env python3
"""
GitHub Actions Workflow Validator
Validates workflow files for deprecated actions, syntax issues, and best practices.
"""

import os
import sys
import yaml
import re
import requests
from pathlib import Path
from typing import List, Dict, Tuple, Any
import subprocess
import json

class WorkflowValidator:
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.workflows_path = self.repo_path / ".github" / "workflows"
        self.errors = []
        self.warnings = []
        
        # Known deprecated actions and their replacements
        self.deprecated_actions = {
            "actions/upload-artifact@v3": "actions/upload-artifact@v4",
            "actions/download-artifact@v3": "actions/download-artifact@v4", 
            "actions/setup-node@v3": "actions/setup-node@v4",
            "actions/cache@v3": "actions/cache@v4",
            "actions/checkout@v3": "actions/checkout@v4",
        }
        
        # GitHub API for checking latest action versions
        self.github_api_base = "https://api.github.com/repos"
        
    def validate_all_workflows(self) -> bool:
        """Validate all workflow files in .github/workflows/"""
        if not self.workflows_path.exists():
            self.warnings.append("No .github/workflows directory found")
            return True
            
        workflow_files = list(self.workflows_path.glob("*.yml")) + list(self.workflows_path.glob("*.yaml"))
        
        if not workflow_files:
            self.warnings.append("No workflow files found")
            return True
            
        success = True
        for workflow_file in workflow_files:
            if not self.validate_workflow_file(workflow_file):
                success = False
                
        return success
        
    def validate_workflow_file(self, workflow_file: Path) -> bool:
        """Validate a single workflow file"""
        print(f"🔍 Validating workflow: {workflow_file.name}")
        
        try:
            with open(workflow_file, 'r') as f:
                content = f.read()
                
            # Parse YAML
            try:
                workflow_data = yaml.safe_load(content)
            except yaml.YAMLError as e:
                self.errors.append(f"{workflow_file.name}: YAML syntax error - {e}")
                return False
                
            success = True
            
            # Check for deprecated actions
            if not self.check_deprecated_actions(workflow_file.name, content):
                success = False
                
            # Check workflow structure
            if not self.check_workflow_structure(workflow_file.name, workflow_data):
                success = False
                
            # Check for common issues
            if not self.check_common_issues(workflow_file.name, content, workflow_data):
                success = False
                
            return success
            
        except Exception as e:
            self.errors.append(f"{workflow_file.name}: Failed to read file - {e}")
            return False
            
    def check_deprecated_actions(self, filename: str, content: str) -> bool:
        """Check for deprecated GitHub Actions"""
        success = True
        
        for deprecated, replacement in self.deprecated_actions.items():
            if deprecated in content:
                self.errors.append(f"{filename}: Uses deprecated action '{deprecated}' - replace with '{replacement}'")
                success = False
                
        # Check for other patterns that might indicate deprecated actions
        deprecated_patterns = [
            (r"actions/\w+@v[12](?:\.\d+)?", "Consider updating to v4+ for better security and features"),
            (r"uses:\s*[\'\"]?([^@\s]+)@master[\'\"]?", "Avoid @master, use specific version tags"),
            (r"uses:\s*[\'\"]?([^@\s]+)@main[\'\"]?", "Avoid @main, use specific version tags"),
        ]
        
        for pattern, message in deprecated_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                self.warnings.append(f"{filename}: {message} - found: {match.group(0)}")
                
        return success
        
    def check_workflow_structure(self, filename: str, workflow_data: Dict[str, Any]) -> bool:
        """Check workflow structure and required fields"""
        success = True
        
        # Check required top-level fields
        required_fields = ['name', 'on']
        for field in required_fields:
            if field not in workflow_data:
                self.errors.append(f"{filename}: Missing required field '{field}'")
                success = False
                
        # Check if workflow has jobs
        if 'jobs' not in workflow_data:
            self.errors.append(f"{filename}: No jobs defined")
            success = False
        else:
            jobs = workflow_data['jobs']
            if not jobs:
                self.errors.append(f"{filename}: Jobs section is empty")
                success = False
            else:
                # Check each job structure
                for job_name, job_data in jobs.items():
                    if not self.check_job_structure(filename, job_name, job_data):
                        success = False
                        
        return success
        
    def check_job_structure(self, filename: str, job_name: str, job_data: Dict[str, Any]) -> bool:
        """Check individual job structure"""
        success = True
        
        # Check required job fields
        if 'runs-on' not in job_data:
            self.errors.append(f"{filename}: Job '{job_name}' missing 'runs-on'")
            success = False
            
        # Check steps if present
        if 'steps' in job_data:
            steps = job_data['steps']
            if isinstance(steps, list):
                for i, step in enumerate(steps):
                    if not isinstance(step, dict):
                        self.errors.append(f"{filename}: Job '{job_name}' step {i+1} is not a dictionary")
                        success = False
                    elif 'uses' not in step and 'run' not in step:
                        self.errors.append(f"{filename}: Job '{job_name}' step {i+1} missing 'uses' or 'run'")
                        success = False
                        
        return success
        
    def check_common_issues(self, filename: str, content: str, workflow_data: Dict[str, Any]) -> bool:
        """Check for common workflow issues and best practices"""
        success = True
        
        # Check for hardcoded secrets
        secret_patterns = [
            r'["\']sk-[a-zA-Z0-9]{48}["\']',  # OpenAI API keys
            r'["\']ghp_[a-zA-Z0-9]{36}["\']',  # GitHub personal access tokens
            r'["\']AKIA[0-9A-Z]{16}["\']',     # AWS access keys
        ]
        
        for pattern in secret_patterns:
            if re.search(pattern, content):
                self.errors.append(f"{filename}: Potential hardcoded secret detected")
                success = False
                
        # Check for missing timeout settings
        if 'jobs' in workflow_data:
            for job_name, job_data in workflow_data['jobs'].items():
                if 'timeout-minutes' not in job_data:
                    self.warnings.append(f"{filename}: Job '{job_name}' missing timeout-minutes")
                    
        # Check for overly broad triggers
        if 'on' in workflow_data:
            triggers = workflow_data['on']
            if isinstance(triggers, dict):
                if 'push' in triggers and not triggers['push']:
                    self.warnings.append(f"{filename}: Push trigger without branch restrictions")
                    
        return success
        
    def validate_action_versions(self) -> bool:
        """Check if action versions are up to date (requires internet)"""
        success = True
        
        try:
            # This is a basic check - in a full implementation, 
            # you'd query GitHub API for latest versions
            print("🌐 Checking action versions (basic validation)...")
            
            common_actions = [
                "actions/checkout",
                "actions/setup-python", 
                "actions/setup-node",
                "actions/upload-artifact",
                "actions/download-artifact",
                "actions/cache"
            ]
            
            for action in common_actions:
                # For now, just check if we're using reasonably recent versions
                # In a full implementation, this would query the GitHub API
                pass
                
        except Exception as e:
            self.warnings.append(f"Could not check action versions: {e}")
            
        return success
        
    def run_actionlint(self) -> bool:
        """Run actionlint if available for comprehensive workflow validation"""
        try:
            # Check if actionlint is installed
            result = subprocess.run(['which', 'actionlint'], 
                                 capture_output=True, text=True)
            if result.returncode != 0:
                self.warnings.append("actionlint not installed - install for enhanced validation")
                return True
                
            # Run actionlint on workflow directory
            result = subprocess.run(['actionlint', str(self.workflows_path)], 
                                 capture_output=True, text=True, cwd=self.repo_path)
            
            if result.returncode != 0:
                if result.stderr:
                    self.errors.append(f"actionlint errors: {result.stderr}")
                if result.stdout:
                    self.errors.append(f"actionlint output: {result.stdout}")
                return False
            else:
                print("✅ actionlint validation passed")
                
        except Exception as e:
            self.warnings.append(f"Could not run actionlint: {e}")
            
        return True
        
    def generate_report(self) -> Dict[str, Any]:
        """Generate validation report"""
        return {
            "workflow_validation": {
                "errors": self.errors,
                "warnings": self.warnings,
                "error_count": len(self.errors),
                "warning_count": len(self.warnings),
                "status": "PASS" if len(self.errors) == 0 else "FAIL"
            }
        }
        
    def print_summary(self):
        """Print validation summary"""
        print("\n" + "="*60)
        print("🔧 WORKFLOW VALIDATION SUMMARY")
        print("="*60)
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  • {error}")
                
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  • {warning}")
                
        if not self.errors and not self.warnings:
            print("\n✅ All workflow validations passed!")
        elif not self.errors:
            print(f"\n✅ No critical errors found ({len(self.warnings)} warnings)")
        else:
            print(f"\n❌ Validation failed with {len(self.errors)} errors")
            
        print("="*60)


def main():
    if len(sys.argv) > 1:
        repo_path = sys.argv[1]
    else:
        repo_path = os.getcwd()
        
    validator = WorkflowValidator(repo_path)
    
    print("🚀 Starting GitHub Actions workflow validation...")
    
    success = True
    
    # Validate all workflows
    if not validator.validate_all_workflows():
        success = False
        
    # Check action versions
    if not validator.validate_action_versions():
        success = False
        
    # Run actionlint if available
    if not validator.run_actionlint():
        success = False
        
    # Print summary
    validator.print_summary()
    
    # Generate report
    report = validator.generate_report()
    
    # Save report
    report_file = Path(repo_path) / "workflow_validation_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
        
    print(f"\n📊 Report saved to: {report_file}")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
