#!/usr/bin/env python3
"""
Pre-commit validation script for CI/CD failure prevention.
Runs lightweight checks before allowing commits.
"""

import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Quick dependency syntax check."""
    repo_root = Path(__file__).parent.parent
    
    # Check requirements.txt syntax
    requirements_file = repo_root / "backend" / "requirements.txt"
    if requirements_file.exists():
        try:
            with open(requirements_file) as f:
                lines = f.readlines()
                for i, line in enumerate(lines, 1):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Basic package name validation
                        if '==' in line:
                            package_name = line.split('==')[0]
                            if not package_name.replace('-', '').replace('_', '').replace('[', '').replace(']', '').isalnum():
                                print(f"❌ Invalid package name in requirements.txt line {i}: {package_name}")
                                return False
        except Exception as e:
            print(f"❌ Error reading requirements.txt: {e}")
            return False
    
    # Check package.json syntax
    package_json = repo_root / "frontend" / "package.json"
    if package_json.exists():
        try:
            import json
            with open(package_json) as f:
                json.load(f)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in package.json: {e}")
            return False
        except Exception as e:
            print(f"❌ Error reading package.json: {e}")
            return False
    
    return True

def check_test_syntax():
    """Check for common test issues."""
    repo_root = Path(__file__).parent.parent
    frontend_src = repo_root / "frontend" / "src"
    
    if not frontend_src.exists():
        return True
    
    test_files = list(frontend_src.rglob("*.test.ts")) + list(frontend_src.rglob("*.test.tsx"))
    
    for test_file in test_files:
        try:
            content = test_file.read_text()
            
            # Check for deprecated ReactDOMTestUtils
            if "ReactDOMTestUtils" in content and "import { act }" not in content:
                print(f"❌ {test_file.name}: Uses deprecated ReactDOMTestUtils without proper act import")
                return False
                
            # Check for problematic mock patterns
            if '"status": 500' in content and '"ok": false' in content:
                print(f"⚠️  {test_file.name}: Consider reviewing 500 error mocks - may cause CI failures")
                
        except Exception:
            continue
    
    return True

def check_api_endpoints():
    """Check API endpoint consistency."""
    repo_root = Path(__file__).parent.parent
    
    # Check backend endpoints
    function_app = repo_root / "backend" / "function_app.py"
    if function_app.exists():
        try:
            content = function_app.read_text()
            backend_endpoints = []
            for line in content.split('\n'):
                if 'route=' in line and '@app.route' in line:
                    # Extract route name
                    route_part = line.split('route=')[1].split(',')[0].strip('"\'')
                    backend_endpoints.append(route_part)
        except Exception:
            backend_endpoints = []
    else:
        backend_endpoints = []
    
    # Check frontend API calls
    frontend_src = repo_root / "frontend" / "src"
    if frontend_src.exists():
        frontend_api_calls = []
        for ts_file in frontend_src.rglob("*.ts"):
            try:
                content = ts_file.read_text()
                if "/api/" in content:
                    # Extract API paths, but skip commented sections
                    import re
                    lines = content.split('\n')
                    in_block_comment = False
                    for line in lines:
                        line = line.strip()
                        
                        # Track block comments
                        if '/*' in line:
                            in_block_comment = True
                        if '*/' in line:
                            in_block_comment = False
                            continue
                            
                        # Skip commented lines and block comments
                        if (line.startswith('//') or 
                            line.startswith('*') or 
                            in_block_comment or
                            'TODO' in line):
                            continue
                            
                        if "/api/" in line:
                            api_calls = re.findall(r'/api/([^"\'`\s\?]+)', line)
                            frontend_api_calls.extend(api_calls)
            except Exception:
                continue
    
    # Check for mismatches
    mismatches = []
    for api_call in set(frontend_api_calls):
        # Convert API call format to backend route format
        backend_route = api_call.replace('-', '_')
        if backend_route not in backend_endpoints and api_call not in backend_endpoints:
            mismatches.append(f"Frontend calls /api/{api_call} but backend has no matching route")
    
    if mismatches:
        print("⚠️  API endpoint mismatches found:")
        for mismatch in mismatches:
            print(f"   {mismatch}")
        return False
    
    return True

def main():
    """Run pre-commit validation."""
    print("🔍 Running pre-commit validation...")
    
    checks = [
        ("Dependencies", check_dependencies),
        ("Test Syntax", check_test_syntax), 
        ("API Endpoints", check_api_endpoints)
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        print(f"\n📋 {check_name}...")
        try:
            if check_func():
                print(f"✅ {check_name} passed")
            else:
                print(f"❌ {check_name} failed")
                all_passed = False
        except Exception as e:
            print(f"💥 {check_name} error: {e}")
            all_passed = False
    
    print("\n" + "="*50)
    if all_passed:
        print("✅ All pre-commit checks passed!")
        sys.exit(0)
    else:
        print("❌ Pre-commit validation failed!")
        print("Fix the issues above before committing.")
        sys.exit(1)

if __name__ == "__main__":
    main()
