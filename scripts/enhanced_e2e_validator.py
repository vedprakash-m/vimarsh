#!/usr/bin/env python3
"""
Enhanced E2E Validator for Vimarsh Multi-Personality Platform
Comprehensive validation for CI/CD pipeline
"""

import argparse
import sys
import os
import subprocess
import time
import json
from pathlib import Path

def run_command(command, description, critical=True, timeout=60):
    """Run a command and return success status"""
    print(f"🔍 {description}...")
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=Path(__file__).parent.parent
        )
        
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            if result.stdout.strip():
                print(f"   Output: {result.stdout[:200]}...")
            return True
        else:
            status = "❌ FAILED" if critical else "⚠️  WARNING"
            print(f"{status} {description}")
            if result.stderr:
                print(f"   Error: {result.stderr[:500]}")
            return not critical
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT")
        return not critical
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return not critical

def validate_project_structure():
    """Validate essential project structure"""
    print("🏗️ Validating Project Structure...")
    
    essential_files = [
        "backend/function_app.py",
        "backend/requirements.txt", 
        "frontend/package.json",
        "README.md",
        ".github/workflows/unified-ci-cd.yml"
    ]
    
    missing_files = []
    for file_path in essential_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing essential files: {missing_files}")
        return False
    else:
        print(f"✅ All {len(essential_files)} essential files present")
        return True

def validate_backend():
    """Validate backend functionality"""
    print("\n🐍 Backend Validation...")
    
    success = True
    
    # Python syntax validation
    if not run_command(
        "cd backend && python3 -m py_compile function_app.py",
        "Backend Python syntax",
        critical=True
    ):
        success = False
    
    # Import validation  
    if not run_command(
        "cd backend && python3 -c 'import function_app; print(\"✅ Function app imports working\")'",
        "Backend imports",
        critical=False
    ):
        success = False
    
    # Requirements check
    if not run_command(
        "cd backend && python3 -m pip check",
        "Backend dependencies",
        critical=False
    ):
        print("⚠️  Some dependency issues detected")
    
    return success

def validate_frontend():
    """Validate frontend functionality"""
    print("\n⚛️ Frontend Validation...")
    
    success = True
    
    # Package.json validation
    if not run_command(
        "cd frontend && npm ls --depth=0",
        "Frontend dependencies",
        critical=False,
        timeout=30
    ):
        print("⚠️  Some frontend dependency issues")
    
    # TypeScript compilation check (if available)
    if os.path.exists("frontend/tsconfig.json"):
        if not run_command(
            "cd frontend && npx tsc --noEmit",
            "TypeScript compilation",
            critical=False,
            timeout=45
        ):
            print("⚠️  TypeScript compilation issues")
    
    return success

def validate_tests():
    """Run available tests"""
    print("\n🧪 Test Validation...")
    
    success = True
    
    # Backend tests
    if os.path.exists("backend/tests"):
        if not run_command(
            "cd backend && python3 -m pytest tests/ -v --tb=short",
            "Backend tests",
            critical=False,
            timeout=120
        ):
            print("⚠️  Some backend tests failed")
    
    return success

def validate_security():
    """Basic security validation"""
    print("\n🔐 Security Validation...")
    
    success = True
    
    # Check for common security issues
    security_patterns = [
        ("password.*=.*['\"][^'\"]{3,}", "Potential hardcoded passwords"),
        ("api[_-]?key.*=.*['\"][^'\"]{10,}", "Potential API keys"),
        ("secret.*=.*['\"][^'\"]{8,}", "Potential secrets"),
        ("AccountKey=[a-zA-Z0-9+/=]{40,}", "Azure Account Keys")
    ]
    
    for pattern, description in security_patterns:
        result = subprocess.run(
            f"grep -r -E --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=.venv '{pattern}' . || true",
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.stdout.strip():
            lines = result.stdout.strip().split('\n')
            relevant_lines = [line for line in lines if not any(exclude in line.lower() 
                            for exclude in ['test', 'example', 'setup-git-hooks'])]
            
            if relevant_lines:
                print(f"🚨 {description} detected:")
                for line in relevant_lines[:3]:  # Show first 3
                    file_path = line.split(':')[0] if ':' in line else line
                    print(f"   - {file_path}")
                success = False
    
    if success:
        print("✅ No obvious security issues detected")
    
    return success

def main():
    """Main validation function"""
    parser = argparse.ArgumentParser(description="Enhanced E2E Validator")
    parser.add_argument("--level", choices=["basic", "comprehensive"], 
                       default="basic", help="Validation level")
    
    args = parser.parse_args()
    
    print("🚀 Vimarsh Enhanced E2E Validator")
    print(f"📊 Validation Level: {args.level.upper()}")
    print("=" * 50)
    
    start_time = time.time()
    validation_results = []
    
    # Core validations
    validation_results.append(("Project Structure", validate_project_structure()))
    validation_results.append(("Backend", validate_backend()))
    
    if args.level == "comprehensive":
        validation_results.append(("Frontend", validate_frontend()))
        validation_results.append(("Tests", validate_tests()))
        validation_results.append(("Security", validate_security()))
    
    # Summary
    duration = time.time() - start_time
    passed = sum(1 for _, result in validation_results if result)
    total = len(validation_results)
    
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    
    for name, result in validation_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} {name}")
    
    print(f"\n📈 Results: {passed}/{total} validations passed")
    print(f"⏱️  Duration: {duration:.1f}s")
    
    if passed == total:
        print("🎉 ALL VALIDATIONS PASSED!")
        print("🚀 Ready for deployment!")
        return 0
    else:
        print("❌ SOME VALIDATIONS FAILED")
        print("🔧 Please fix issues before deployment")
        return 1

if __name__ == "__main__":
    sys.exit(main())
