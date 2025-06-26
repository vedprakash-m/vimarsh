#!/usr/bin/env python3
"""
Vimarsh Compliance Verification System
Automated compliance checking for GDPR, SOC2, and spiritual content standards
"""

import json
import os
import re
import logging
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import yaml

@dataclass
class ComplianceResult:
    """Represents the result of a compliance check"""
    name: str
    category: str
    status: str  # PASS, FAIL, WARNING, NOT_APPLICABLE
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    description: str
    evidence: List[str]
    remediation: str
    timestamp: datetime
    
    def __post_init__(self):
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp.replace('Z', '+00:00'))

class ComplianceChecker:
    """Main compliance verification system"""
    
    def __init__(self, project_root: str, verbose: bool = False):
        self.project_root = Path(project_root)
        self.verbose = verbose
        self.results: List[ComplianceResult] = []
        
        # Setup logging
        logging.basicConfig(
            level=logging.DEBUG if verbose else logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all compliance checks"""
        self.logger.info("Starting comprehensive compliance verification")
        
        # GDPR Compliance
        self._check_gdpr_compliance()
        
        # Data Protection
        self._check_data_protection()
        
        # Spiritual Content Standards
        self._check_spiritual_content_standards()
        
        # Technical Security
        self._check_technical_security()
        
        # Documentation Compliance
        self._check_documentation_compliance()
        
        return self._generate_summary()
    
    def _check_gdpr_compliance(self):
        """Check GDPR compliance requirements"""
        self.logger.info("Checking GDPR compliance")
        
        # Privacy Policy Check
        privacy_files = list(self.project_root.glob("**/privacy*.md")) + \
                       list(self.project_root.glob("**/PRIVACY*")) + \
                       list(self.project_root.glob("**/privacy*.txt"))
        
        if privacy_files:
            content = self._read_files(privacy_files)
            gdpr_terms = [
                "data protection", "personal data", "data subject",
                "right to be forgotten", "data portability", "consent",
                "legitimate interest", "data processor", "data controller"
            ]
            
            found_terms = [term for term in gdpr_terms if term.lower() in content.lower()]
            
            if len(found_terms) >= 6:
                self.results.append(ComplianceResult(
                    name="GDPR Privacy Policy",
                    category="GDPR",
                    status="PASS",
                    severity="HIGH",
                    description="Privacy policy contains sufficient GDPR terminology",
                    evidence=[f"Found {len(found_terms)} GDPR terms: {', '.join(found_terms[:5])}..."],
                    remediation="Continue maintaining comprehensive privacy policy",
                    timestamp=datetime.now()
                ))
            else:
                self.results.append(ComplianceResult(
                    name="GDPR Privacy Policy",
                    category="GDPR",
                    status="FAIL",
                    severity="CRITICAL",
                    description="Privacy policy lacks sufficient GDPR coverage",
                    evidence=[f"Only found {len(found_terms)} GDPR terms: {', '.join(found_terms)}"],
                    remediation="Enhance privacy policy with comprehensive GDPR terms and rights",
                    timestamp=datetime.now()
                ))
        else:
            self.results.append(ComplianceResult(
                name="GDPR Privacy Policy",
                category="GDPR",
                status="FAIL",
                severity="CRITICAL",
                description="No privacy policy found",
                evidence=["No privacy policy files detected"],
                remediation="Create comprehensive privacy policy addressing GDPR requirements",
                timestamp=datetime.now()
            ))
        
        # Consent Management Check
        consent_patterns = [
            r"user.*consent", r"cookie.*consent", r"data.*consent",
            r"opt.*in", r"opt.*out", r"consent.*management"
        ]
        
        consent_evidence = self._find_patterns_in_code(consent_patterns, ["*.py", "*.ts", "*.tsx"])
        
        if consent_evidence:
            self.results.append(ComplianceResult(
                name="Consent Management Implementation",
                category="GDPR",
                status="PASS",
                severity="HIGH",
                description="Consent management patterns found in code",
                evidence=consent_evidence[:3],
                remediation="Ensure consent mechanisms are user-friendly and compliant",
                timestamp=datetime.now()
            ))
        else:
            self.results.append(ComplianceResult(
                name="Consent Management Implementation",
                category="GDPR",
                status="WARNING",
                severity="MEDIUM",
                description="No explicit consent management found in code",
                evidence=["No consent management patterns detected"],
                remediation="Implement user consent mechanisms for data processing",
                timestamp=datetime.now()
            ))
    
    def _check_data_protection(self):
        """Check data protection implementation"""
        self.logger.info("Checking data protection measures")
        
        # Encryption Check
        encryption_patterns = [
            r"encrypt", r"decrypt", r"bcrypt", r"scrypt", r"argon2",
            r"AES", r"RSA", r"TLS", r"SSL", r"HTTPS"
        ]
        
        encryption_evidence = self._find_patterns_in_code(encryption_patterns, ["*.py", "*.ts", "*.tsx"])
        
        if len(encryption_evidence) >= 3:
            self.results.append(ComplianceResult(
                name="Data Encryption Implementation",
                category="Data Protection",
                status="PASS",
                severity="HIGH",
                description="Strong encryption patterns found in codebase",
                evidence=encryption_evidence[:3],
                remediation="Continue using strong encryption for sensitive data",
                timestamp=datetime.now()
            ))
        else:
            self.results.append(ComplianceResult(
                name="Data Encryption Implementation",
                category="Data Protection",
                status="WARNING",
                severity="HIGH",
                description="Limited encryption implementation detected",
                evidence=encryption_evidence,
                remediation="Implement comprehensive encryption for all sensitive data",
                timestamp=datetime.now()
            ))
        
        # Data Retention Check
        retention_patterns = [
            r"data.*retention", r"delete.*after", r"expire.*data",
            r"cleanup.*old", r"purge.*data", r"retention.*policy"
        ]
        
        retention_evidence = self._find_patterns_in_code(retention_patterns, ["*.py", "*.ts", "*.tsx", "*.md"])
        
        if retention_evidence:
            self.results.append(ComplianceResult(
                name="Data Retention Policy",
                category="Data Protection",
                status="PASS",
                severity="MEDIUM",
                description="Data retention mechanisms found",
                evidence=retention_evidence[:2],
                remediation="Ensure retention periods align with legal requirements",
                timestamp=datetime.now()
            ))
        else:
            self.results.append(ComplianceResult(
                name="Data Retention Policy",
                category="Data Protection",
                status="FAIL",
                severity="MEDIUM",
                description="No data retention policy implementation found",
                evidence=["No retention patterns detected"],
                remediation="Implement automated data retention and deletion policies",
                timestamp=datetime.now()
            ))
    
    def _check_spiritual_content_standards(self):
        """Check spiritual content handling standards"""
        self.logger.info("Checking spiritual content standards")
        
        # Sacred Text Attribution
        attribution_patterns = [
            r"attribution", r"source.*text", r"copyright", r"public.*domain",
            r"sacred.*text", r"spiritual.*content", r"bhagavad.*gita",
            r"mahabharata", r"vedic", r"sanskrit"
        ]
        
        attribution_evidence = self._find_patterns_in_code(attribution_patterns, ["*.py", "*.ts", "*.tsx", "*.md"])
        
        if len(attribution_evidence) >= 5:
            self.results.append(ComplianceResult(
                name="Sacred Text Attribution",
                category="Spiritual Standards",
                status="PASS",
                severity="HIGH",
                description="Comprehensive sacred text attribution found",
                evidence=attribution_evidence[:3],
                remediation="Continue proper attribution of all spiritual content",
                timestamp=datetime.now()
            ))
        else:
            self.results.append(ComplianceResult(
                name="Sacred Text Attribution",
                category="Spiritual Standards",
                status="WARNING",
                severity="HIGH",
                description="Limited sacred text attribution found",
                evidence=attribution_evidence,
                remediation="Enhance attribution system for all sacred texts and sources",
                timestamp=datetime.now()
            ))
        
        # Expert Review System
        expert_patterns = [
            r"expert.*review", r"spiritual.*expert", r"sanskrit.*scholar",
            r"review.*queue", r"expert.*validation", r"cultural.*sensitivity"
        ]
        
        expert_evidence = self._find_patterns_in_code(expert_patterns, ["*.py", "*.ts", "*.tsx"])
        
        if expert_evidence:
            self.results.append(ComplianceResult(
                name="Expert Review System",
                category="Spiritual Standards",
                status="PASS",
                severity="MEDIUM",
                description="Expert review system implementation found",
                evidence=expert_evidence[:2],
                remediation="Ensure expert review covers all spiritual content",
                timestamp=datetime.now()
            ))
        else:
            self.results.append(ComplianceResult(
                name="Expert Review System",
                category="Spiritual Standards",
                status="FAIL",
                severity="HIGH",
                description="No expert review system found",
                evidence=["No expert review patterns detected"],
                remediation="Implement expert review system for spiritual content validation",
                timestamp=datetime.now()
            ))
        
        # Cultural Sensitivity
        sensitivity_patterns = [
            r"cultural.*sensitivity", r"respectful", r"reverent", r"sacred",
            r"divine", r"spiritual.*respect", r"dharmic", r"vedic.*tradition"
        ]
        
        sensitivity_evidence = self._find_patterns_in_code(sensitivity_patterns, ["*.py", "*.ts", "*.tsx", "*.md"])
        
        if len(sensitivity_evidence) >= 3:
            self.results.append(ComplianceResult(
                name="Cultural Sensitivity Implementation",
                category="Spiritual Standards",
                status="PASS",
                severity="MEDIUM",
                description="Cultural sensitivity patterns found in implementation",
                evidence=sensitivity_evidence[:3],
                remediation="Continue maintaining cultural sensitivity in all content",
                timestamp=datetime.now()
            ))
        else:
            self.results.append(ComplianceResult(
                name="Cultural Sensitivity Implementation",
                category="Spiritual Standards",
                status="WARNING",
                severity="MEDIUM",
                description="Limited cultural sensitivity implementation",
                evidence=sensitivity_evidence,
                remediation="Enhance cultural sensitivity throughout the application",
                timestamp=datetime.now()
            ))
    
    def _check_technical_security(self):
        """Check technical security compliance"""
        self.logger.info("Checking technical security compliance")
        
        # HTTPS/TLS Configuration
        tls_files = list(self.project_root.glob("infrastructure/*.bicep"))
        tls_evidence = []
        
        for file in tls_files:
            content = file.read_text()
            if "httpsOnly" in content and "true" in content:
                tls_evidence.append(f"HTTPS enforcement in {file.name}")
            if "minTlsVersion" in content and "1.2" in content:
                tls_evidence.append(f"TLS 1.2+ requirement in {file.name}")
        
        if len(tls_evidence) >= 2:
            self.results.append(ComplianceResult(
                name="TLS/HTTPS Configuration",
                category="Technical Security",
                status="PASS",
                severity="HIGH",
                description="Proper TLS/HTTPS configuration found",
                evidence=tls_evidence,
                remediation="Maintain strong TLS configuration",
                timestamp=datetime.now()
            ))
        else:
            self.results.append(ComplianceResult(
                name="TLS/HTTPS Configuration",
                category="Technical Security",
                status="FAIL",
                severity="CRITICAL",
                description="Insufficient TLS/HTTPS configuration",
                evidence=tls_evidence,
                remediation="Configure HTTPS-only and TLS 1.2+ for all services",
                timestamp=datetime.now()
            ))
        
        # Authentication Security
        auth_patterns = [
            r"authentication", r"authorization", r"jwt", r"token",
            r"msal", r"oauth", r"entra", r"azure.*ad"
        ]
        
        auth_evidence = self._find_patterns_in_code(auth_patterns, ["*.py", "*.ts", "*.tsx"])
        
        if len(auth_evidence) >= 3:
            self.results.append(ComplianceResult(
                name="Authentication Implementation",
                category="Technical Security",
                status="PASS",
                severity="HIGH",
                description="Comprehensive authentication system found",
                evidence=auth_evidence[:3],
                remediation="Continue using strong authentication mechanisms",
                timestamp=datetime.now()
            ))
        else:
            self.results.append(ComplianceResult(
                name="Authentication Implementation",
                category="Technical Security",
                status="WARNING",
                severity="HIGH",
                description="Limited authentication implementation",
                evidence=auth_evidence,
                remediation="Implement comprehensive authentication and authorization",
                timestamp=datetime.now()
            ))
    
    def _check_documentation_compliance(self):
        """Check documentation compliance"""
        self.logger.info("Checking documentation compliance")
        
        # Required Documentation Files
        required_docs = {
            "README.md": "Project documentation",
            "privacy": "Privacy policy",
            "terms": "Terms of service",
            "security": "Security documentation",
            "api": "API documentation"
        }
        
        found_docs = []
        missing_docs = []
        
        for doc_type, description in required_docs.items():
            matching_files = list(self.project_root.glob(f"**/*{doc_type}*"))
            if matching_files:
                found_docs.append(f"{description}: {matching_files[0].name}")
            else:
                missing_docs.append(f"{description}")
        
        if len(found_docs) >= 3:
            self.results.append(ComplianceResult(
                name="Required Documentation",
                category="Documentation",
                status="PASS",
                severity="MEDIUM",
                description="Most required documentation found",
                evidence=found_docs,
                remediation="Complete any missing documentation",
                timestamp=datetime.now()
            ))
        else:
            self.results.append(ComplianceResult(
                name="Required Documentation",
                category="Documentation",
                status="WARNING",
                severity="MEDIUM",
                description="Insufficient documentation coverage",
                evidence=found_docs,
                remediation=f"Create missing documentation: {', '.join(missing_docs)}",
                timestamp=datetime.now()
            ))
        
        # Code Documentation
        doc_patterns = [
            r'""".*"""', r"'''.*'''", r"//.*@param", r"//.*@returns",
            r"/\*\*.*\*/", r"#.*docstring", r"@doc"
        ]
        
        doc_evidence = self._find_patterns_in_code(doc_patterns, ["*.py", "*.ts", "*.tsx"])
        
        if len(doc_evidence) >= 10:
            self.results.append(ComplianceResult(
                name="Code Documentation",
                category="Documentation",
                status="PASS",
                severity="LOW",
                description="Good code documentation coverage",
                evidence=[f"Found {len(doc_evidence)} documentation patterns"],
                remediation="Continue maintaining good code documentation",
                timestamp=datetime.now()
            ))
        else:
            self.results.append(ComplianceResult(
                name="Code Documentation",
                category="Documentation",
                status="WARNING",
                severity="LOW",
                description="Limited code documentation",
                evidence=[f"Found {len(doc_evidence)} documentation patterns"],
                remediation="Improve code documentation with docstrings and comments",
                timestamp=datetime.now()
            ))
    
    def _find_patterns_in_code(self, patterns: List[str], file_extensions: List[str]) -> List[str]:
        """Find patterns in code files"""
        evidence = []
        
        for ext in file_extensions:
            for file in self.project_root.glob(f"**/{ext}"):
                if self._should_skip_file(file):
                    continue
                    
                try:
                    content = file.read_text(encoding='utf-8')
                    for pattern in patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        if matches:
                            evidence.append(f"{pattern} in {file.relative_to(self.project_root)}")
                            break  # One match per file per pattern is enough
                except (UnicodeDecodeError, PermissionError):
                    continue
        
        return evidence
    
    def _read_files(self, files: List[Path]) -> str:
        """Read content from multiple files"""
        content = ""
        for file in files:
            try:
                content += file.read_text(encoding='utf-8') + "\n"
            except (UnicodeDecodeError, PermissionError):
                continue
        return content
    
    def _should_skip_file(self, file: Path) -> bool:
        """Check if file should be skipped"""
        skip_dirs = {'.git', '__pycache__', 'node_modules', '.pytest_cache', 'logs'}
        skip_files = {'.DS_Store', 'Thumbs.db'}
        
        return (any(skip_dir in file.parts for skip_dir in skip_dirs) or
                file.name in skip_files or
                file.suffix in {'.pyc', '.log', '.tmp'})
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate compliance summary"""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_checks": len(self.results),
            "passed": len([r for r in self.results if r.status == "PASS"]),
            "failed": len([r for r in self.results if r.status == "FAIL"]),
            "warnings": len([r for r in self.results if r.status == "WARNING"]),
            "critical_issues": len([r for r in self.results if r.severity == "CRITICAL"]),
            "high_issues": len([r for r in self.results if r.severity == "HIGH"]),
            "medium_issues": len([r for r in self.results if r.severity == "MEDIUM"]),
            "low_issues": len([r for r in self.results if r.severity == "LOW"]),
            "compliance_score": 0.0,
            "categories": {}
        }
        
        # Calculate compliance score
        if summary["total_checks"] > 0:
            base_score = (summary["passed"] / summary["total_checks"]) * 100
            penalty = (summary["critical_issues"] * 25 + 
                      summary["high_issues"] * 15 + 
                      summary["medium_issues"] * 5)
            summary["compliance_score"] = max(0, base_score - penalty)
        
        # Category breakdown
        categories = {}
        for result in self.results:
            if result.category not in categories:
                categories[result.category] = {
                    "total": 0, "pass": 0, "fail": 0, "warning": 0, "not_applicable": 0
                }
            categories[result.category]["total"] += 1
            status_key = result.status.lower()
            if status_key in categories[result.category]:
                categories[result.category][status_key] += 1
        
        summary["categories"] = categories
        
        return summary
    
    def save_report(self, output_file: str, format: str = "json"):
        """Save compliance report"""
        summary = self._generate_summary()
        
        if format.lower() == "json":
            report = {
                "summary": summary,
                "results": [asdict(result) for result in self.results]
            }
            
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
        
        elif format.lower() == "yaml":
            report = {
                "summary": summary,
                "results": [asdict(result) for result in self.results]
            }
            
            with open(output_file, 'w') as f:
                yaml.dump(report, f, default_flow_style=False)
        
        self.logger.info(f"Compliance report saved to {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Vimarsh Compliance Verification System")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--output", default="compliance-report.json", help="Output file")
    parser.add_argument("--format", choices=["json", "yaml"], default="json", help="Output format")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--category", help="Check specific category only")
    
    args = parser.parse_args()
    
    checker = ComplianceChecker(args.project_root, args.verbose)
    
    if args.category:
        # Run specific category checks (implementation would filter by category)
        summary = checker.run_all_checks()
    else:
        summary = checker.run_all_checks()
    
    # Save report
    checker.save_report(args.output, args.format)
    
    # Print summary
    print(f"\n🔍 Compliance Verification Summary:")
    print(f"Total Checks: {summary['total_checks']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Warnings: {summary['warnings']}")
    print(f"Compliance Score: {summary['compliance_score']:.1f}%")
    
    if summary['critical_issues'] > 0:
        print(f"🚨 Critical Issues: {summary['critical_issues']}")
        exit(3)
    elif summary['high_issues'] > 0:
        print(f"⚠️  High Priority Issues: {summary['high_issues']}")
        exit(2)
    elif summary['failed'] > 0:
        print(f"❌ Some checks failed: {summary['failed']}")
        exit(1)
    else:
        print("✅ All compliance checks passed!")
        exit(0)

if __name__ == "__main__":
    main()
