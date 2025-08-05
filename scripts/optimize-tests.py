#!/usr/bin/env python3
"""
Vimarsh Test Suite Optimization
Reduces test execution time by identifying and running only essential tests
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Set

class TestOptimizer:
    def __init__(self, backend_path: str = "backend", frontend_path: str = "frontend"):
        self.backend_path = Path(backend_path)
        self.frontend_path = Path(frontend_path)
        self.test_failures_limit = 5  # Fail fast
        
    def analyze_changed_files(self) -> Dict[str, List[str]]:
        """Detect changed files to run targeted tests"""
        try:
            # Get changed files from git
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
                capture_output=True, text=True, check=True
            )
            changed_files = result.stdout.strip().split('\n')
            
            changes = {
                'backend': [],
                'frontend': [],
                'docs_only': True
            }
            
            for file in changed_files:
                if file.startswith('backend/'):
                    changes['backend'].append(file)
                    changes['docs_only'] = False
                elif file.startswith('frontend/'):
                    changes['frontend'].append(file)
                    changes['docs_only'] = False
                elif not (file.endswith('.md') or file.startswith('docs/')):
                    changes['docs_only'] = False
                    
            return changes
            
        except subprocess.CalledProcessError:
            # Fallback: assume all changes
            return {
                'backend': ['backend/'],
                'frontend': ['frontend/'],
                'docs_only': False
            }
    
    def get_critical_tests(self) -> Dict[str, List[str]]:
        """Define critical tests that must always pass"""
        return {
            'backend': [
                'test_spiritual_guidance',
                'test_auth',
                'test_security',
                'test_api_basic',
            ],
            'frontend': [
                'test_app_loading',
                'test_spiritual_interface',
                'test_user_auth',
            ]
        }
    
    def run_backend_tests(self, test_type: str = "smart") -> bool:
        """Run optimized backend tests"""
        print(f"🐍 Running backend tests (mode: {test_type})")
        
        os.chdir(self.backend_path)
        
        if test_type == "critical":
            # Run only critical tests
            critical_tests = self.get_critical_tests()['backend']
            test_pattern = " or ".join(critical_tests)
            cmd = [
                "python", "-m", "pytest", "tests/", "-v",
                "-k", test_pattern,
                "--tb=short", "--disable-warnings",
                f"--maxfail={self.test_failures_limit}",
                "--no-header", "-q"
            ]
        elif test_type == "unit":
            # Skip slow integration tests
            cmd = [
                "python", "-m", "pytest", "tests/", "-v",
                "-k", "not integration and not e2e and not comprehensive",
                "--tb=short", "--disable-warnings",
                f"--maxfail={self.test_failures_limit}",
                "--durations=10", "--no-header", "-q"
            ]
        else:
            # Smart testing based on changes
            cmd = [
                "python", "-m", "pytest", "tests/", "-v",
                "--tb=short", "--disable-warnings",
                f"--maxfail={self.test_failures_limit}",
                "--no-header", "-q"
            ]
        
        try:
            result = subprocess.run(cmd, check=True)
            print("✅ Backend tests passed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Backend tests failed with exit code {e.returncode}")
            return False
        finally:
            os.chdir("..")
    
    def run_frontend_tests(self, test_type: str = "smart") -> bool:
        """Run optimized frontend tests"""
        print(f"🎨 Running frontend tests (mode: {test_type})")
        
        os.chdir(self.frontend_path)
        
        if test_type == "critical":
            # Run only critical tests
            critical_tests = self.get_critical_tests()['frontend']
            test_pattern = "|".join(critical_tests)
            cmd = [
                "npm", "run", "test:ci", "--",
                "--testNamePattern", test_pattern,
                "--runInBand", "--forceExit",
                "--silent", "--maxWorkers=1"
            ]
        else:
            # Optimized test run
            cmd = [
                "npm", "run", "test:ci", "--",
                "--runInBand", "--forceExit",
                "--detectOpenHandles=false",
                "--maxWorkers=2", "--silent",
                "--passWithNoTests"
            ]
        
        try:
            result = subprocess.run(cmd, check=True)
            print("✅ Frontend tests passed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Frontend tests failed with exit code {e.returncode}")
            return False
        finally:
            os.chdir("..")
    
    def optimize_test_execution(self):
        """Main optimization logic"""
        print("🚀 Starting optimized test execution")
        
        # Analyze changes
        changes = self.analyze_changed_files()
        
        # Skip all tests for docs-only changes
        if changes['docs_only']:
            print("📝 Docs-only changes detected, skipping tests")
            return True
        
        # Determine test mode based on branch
        is_main_branch = os.getenv('GITHUB_REF') == 'refs/heads/main'
        test_mode = "critical" if is_main_branch else "smart"
        
        success = True
        
        # Run backend tests if needed
        if changes['backend'] or is_main_branch:
            if not self.run_backend_tests(test_mode):
                success = False
        else:
            print("⏭️ Skipping backend tests (no changes)")
        
        # Run frontend tests if needed
        if changes['frontend'] or is_main_branch:
            if not self.run_frontend_tests(test_mode):
                success = False
        else:
            print("⏭️ Skipping frontend tests (no changes)")
        
        if success:
            print("🎉 All tests passed!")
        else:
            print("💥 Some tests failed!")
            sys.exit(1)

if __name__ == "__main__":
    optimizer = TestOptimizer()
    optimizer.optimize_test_execution()
