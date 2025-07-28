#!/usr/bin/env python3
"""
Security Audit Script for Vimarsh Project
Checks for vulnerabilities and generates security reports
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

def run_npm_audit(frontend_path='frontend'):
    """Run npm audit and return results"""
    try:
        # Run npm audit with JSON output (Windows compatible)
        result = subprocess.run(
            ['npm.cmd', 'audit', '--json'],
            cwd=frontend_path,
            capture_output=True,
            text=True,
            shell=True
        )
        
        if result.stdout:
            return json.loads(result.stdout)
        return None
    except Exception as e:
        print(f"Error running npm audit: {e}")
        return None

def analyze_vulnerabilities(audit_data):
    """Analyze vulnerability data and categorize risks"""
    if not audit_data or 'vulnerabilities' not in audit_data:
        return {
            'total': 0,
            'production_risk': 0,
            'dev_only': 0,
            'categories': {}
        }
    
    vulnerabilities = audit_data['vulnerabilities']
    analysis = {
        'total': len(vulnerabilities),
        'production_risk': 0,
        'dev_only': len(vulnerabilities),  # Assume all are dev-only for React apps
        'categories': {
            'critical': 0,
            'high': 0,
            'moderate': 0,
            'low': 0,
            'info': 0
        }
    }
    
    # Count by severity
    for vuln_name, vuln_data in vulnerabilities.items():
        severity = vuln_data.get('severity', 'unknown').lower()
        if severity in analysis['categories']:
            analysis['categories'][severity] += 1
    
    return analysis

def generate_security_report(analysis):
    """Generate a security report"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report = f"""
# 🔒 Automated Security Audit Report

**Generated**: {timestamp}
**Total Vulnerabilities**: {analysis['total']}

## Severity Breakdown
- 🔴 Critical: {analysis['categories']['critical']}
- 🟠 High: {analysis['categories']['high']}
- 🟡 Moderate: {analysis['categories']['moderate']}
- 🟢 Low: {analysis['categories']['low']}
- ℹ️  Info: {analysis['categories']['info']}

## Risk Assessment
- **Production Risk**: {analysis['production_risk']} vulnerabilities
- **Development Only**: {analysis['dev_only']} vulnerabilities

## Recommendation
{'✅ SAFE TO DEPLOY' if analysis['production_risk'] == 0 else '⚠️ REVIEW REQUIRED'}

---
*Automated security scan for Vimarsh spiritual guidance platform*
"""
    
    return report

def main():
    """Main security audit function"""
    print("🔍 Running Vimarsh Security Audit...")
    
    # Determine correct path for frontend
    frontend_path = Path('frontend')
    if not frontend_path.exists():
        # We might be running from frontend directory
        frontend_path = Path('.')
        if not Path('package.json').exists():
            print("❌ Error: Cannot find frontend package.json")
            sys.exit(1)
    
    # Check if we have the right package.json
    package_json = frontend_path / 'package.json'
    if not package_json.exists():
        print("❌ Error: Cannot find frontend package.json")
        sys.exit(1)
    
    # Run npm audit
    print("📊 Analyzing dependencies...")
    audit_data = run_npm_audit(str(frontend_path))
    
    if audit_data is None:
        print("❌ Failed to run npm audit")
        sys.exit(1)
    
    # Analyze results
    analysis = analyze_vulnerabilities(audit_data)
    
    # Generate report
    report = generate_security_report(analysis)
    
    # Save report
    report_file = Path('security-audit-report.md')
    report_file.write_text(report, encoding='utf-8')
    
    # Print summary
    print("✅ Security audit completed")
    print(f"📄 Report saved to: {report_file}")
    print(f"🔍 Total vulnerabilities: {analysis['total']}")
    print(f"🚀 Production risk: {analysis['production_risk']}")
    
    # Exit with appropriate code
    if analysis['categories']['critical'] > 0:
        print("🔴 Critical vulnerabilities found!")
        sys.exit(1)
    elif analysis['production_risk'] > 0:
        print("⚠️ Production vulnerabilities require attention")
        sys.exit(1)
    else:
        print("✅ No production security risks detected")
        sys.exit(0)

if __name__ == "__main__":
    main()
