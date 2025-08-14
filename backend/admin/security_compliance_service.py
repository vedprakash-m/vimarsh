#!/usr/bin/env python3
"""
Security & Compliance Service for Vimarsh Admin Panel
Comprehensive security auditing and compliance checking
"""

import asyncio
import json
import logging
import subprocess
import requests
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import re

logger = logging.getLogger(__name__)

@dataclass
class SecurityIssue:
    """Individual security issue"""
    issue_id: str
    category: str  # 'vulnerability', 'misconfiguration', 'compliance', 'best_practice'
    severity: str  # 'critical', 'high', 'medium', 'low', 'info'
    title: str
    description: str
    affected_component: str
    recommendation: str
    cve_id: Optional[str] = None
    cvss_score: Optional[float] = None

@dataclass
class SecurityAuditResult:
    """Security audit result"""
    audit_id: str
    audit_type: str  # 'vulnerability_scan', 'compliance_check', 'configuration_audit'
    started_at: str
    completed_at: Optional[str] = None
    status: str = "running"  # 'running', 'completed', 'failed'
    total_issues: int = 0
    critical_issues: int = 0
    high_issues: int = 0
    medium_issues: int = 0
    low_issues: int = 0
    info_issues: int = 0
    issues: Optional[List[SecurityIssue]] = None
    recommendations: Optional[List[str]] = None

class SecurityComplianceService:
    """Comprehensive security and compliance service"""
    
    def __init__(self):
        """Initialize the security service"""
        self.active_audits: Dict[str, SecurityAuditResult] = {}
        self.workspace_path = Path(__file__).parent.parent.parent
        self.backend_path = self.workspace_path / "backend"
        self.frontend_path = self.workspace_path / "frontend"
        
        # Security check configurations
        self.audit_types = {
            "vulnerability_scan": {
                "name": "Vulnerability Scanning",
                "description": "Scan for known vulnerabilities in dependencies",
                "checks": [
                    "npm_audit",
                    "python_safety_check",
                    "docker_security_scan",
                    "known_cve_check"
                ]
            },
            "compliance_check": {
                "name": "Compliance Verification",
                "description": "Verify compliance with security standards",
                "checks": [
                    "gdpr_compliance",
                    "azure_security_baseline",
                    "authentication_requirements",
                    "data_protection_compliance"
                ]
            },
            "configuration_audit": {
                "name": "Security Configuration Audit",
                "description": "Audit security configurations",
                "checks": [
                    "https_enforcement",
                    "security_headers",
                    "cors_configuration",
                    "authentication_config",
                    "azure_key_vault_config",
                    "cosmos_db_security"
                ]
            }
        }

    async def start_security_audit(self, audit_type: str, environment: str = "production", 
                                 options: Optional[Dict[str, Any]] = None) -> str:
        """Start a security audit"""
        audit_id = f"{audit_type}_{environment}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create audit result
        audit_result = SecurityAuditResult(
            audit_id=audit_id,
            audit_type=audit_type,
            started_at=datetime.now(timezone.utc).isoformat(),
            issues=[],
            recommendations=[]
        )
        
        self.active_audits[audit_id] = audit_result
        
        # Start audit in background
        asyncio.create_task(self._run_security_audit_async(audit_result, environment, options or {}))
        
        return audit_id

    async def _run_security_audit_async(self, audit: SecurityAuditResult, environment: str, options: Dict[str, Any]):
        """Run security audit asynchronously"""
        try:
            logger.info(f"Starting security audit: {audit.audit_type} for {environment}")
            
            # Get checks for this audit type
            audit_config = self.audit_types.get(audit.audit_type, {})
            checks = audit_config.get("checks", [])
            
            all_issues = []
            all_recommendations = []
            
            # Run security checks
            for check_name in checks:
                try:
                    issues, recommendations = await self._run_security_check(check_name, environment, options)
                    all_issues.extend(issues)
                    all_recommendations.extend(recommendations)
                except Exception as e:
                    logger.error(f"Security check {check_name} failed: {e}")
                    # Add error as an issue
                    all_issues.append(SecurityIssue(
                        issue_id=f"check_error_{check_name}",
                        category="misconfiguration",
                        severity="medium",
                        title=f"Security check failed: {check_name}",
                        description=f"Failed to execute security check: {str(e)}",
                        affected_component="security_scanner",
                        recommendation="Review security check configuration and dependencies"
                    ))
            
            # Categorize issues by severity
            audit.issues = all_issues
            audit.recommendations = list(set(all_recommendations))  # Remove duplicates
            audit.total_issues = len(all_issues)
            
            for issue in all_issues:
                if issue.severity == "critical":
                    audit.critical_issues += 1
                elif issue.severity == "high":
                    audit.high_issues += 1
                elif issue.severity == "medium":
                    audit.medium_issues += 1
                elif issue.severity == "low":
                    audit.low_issues += 1
                else:
                    audit.info_issues += 1
            
            # Complete audit
            audit.status = "completed"
            audit.completed_at = datetime.now(timezone.utc).isoformat()
            
            logger.info(f"Security audit completed: {audit.audit_id}, Issues: {audit.total_issues}")
            
        except Exception as e:
            logger.error(f"Security audit failed: {e}")
            audit.status = "failed"
            audit.completed_at = datetime.now(timezone.utc).isoformat()

    async def _run_security_check(self, check_name: str, environment: str, 
                                options: Dict[str, Any]) -> tuple[List[SecurityIssue], List[str]]:
        """Run an individual security check"""
        issues = []
        recommendations = []
        
        try:
            if check_name == "npm_audit":
                npm_issues, npm_recommendations = await self._run_npm_audit()
                issues.extend(npm_issues)
                recommendations.extend(npm_recommendations)
            
            elif check_name == "python_safety_check":
                python_issues, python_recommendations = await self._run_python_safety_check()
                issues.extend(python_issues)
                recommendations.extend(python_recommendations)
            
            elif check_name == "https_enforcement":
                https_issues, https_recommendations = await self._check_https_enforcement(environment, options)
                issues.extend(https_issues)
                recommendations.extend(https_recommendations)
            
            elif check_name == "security_headers":
                header_issues, header_recommendations = await self._check_security_headers(environment, options)
                issues.extend(header_issues)
                recommendations.extend(header_recommendations)
            
            elif check_name == "cors_configuration":
                cors_issues, cors_recommendations = await self._check_cors_configuration(environment, options)
                issues.extend(cors_issues)
                recommendations.extend(cors_recommendations)
            
            elif check_name == "authentication_config":
                auth_issues, auth_recommendations = await self._check_authentication_config(environment, options)
                issues.extend(auth_issues)
                recommendations.extend(auth_recommendations)
            
            else:
                # Placeholder for other checks
                issues.append(SecurityIssue(
                    issue_id=f"check_not_implemented_{check_name}",
                    category="best_practice",
                    severity="info",
                    title=f"Security check not implemented: {check_name}",
                    description=f"The security check '{check_name}' is not yet implemented",
                    affected_component="security_scanner",
                    recommendation=f"Implement security check for {check_name}"
                ))
        
        except Exception as e:
            logger.error(f"Security check {check_name} failed: {e}")
            issues.append(SecurityIssue(
                issue_id=f"check_error_{check_name}",
                category="misconfiguration",
                severity="medium",
                title=f"Security check error: {check_name}",
                description=f"Security check failed with error: {str(e)}",
                affected_component="security_scanner",
                recommendation="Review check implementation and fix errors"
            ))
        
        return issues, recommendations

    async def _run_npm_audit(self) -> tuple[List[SecurityIssue], List[str]]:
        """Run npm audit for frontend dependencies"""
        issues = []
        recommendations = []
        
        try:
            # Check if package.json exists
            package_json = self.frontend_path / "package.json"
            if not package_json.exists():
                return issues, recommendations
            
            # Run npm audit
            result = subprocess.run(
                ["npm", "audit", "--json", "--audit-level=moderate"],
                cwd=self.frontend_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.stdout:
                try:
                    audit_data = json.loads(result.stdout)
                    vulnerabilities = audit_data.get("vulnerabilities", {})
                    
                    for vuln_name, vuln_data in vulnerabilities.items():
                        severity = vuln_data.get("severity", "unknown").lower()
                        
                        # Map npm severity to our severity levels
                        if severity == "critical":
                            mapped_severity = "critical"
                        elif severity == "high":
                            mapped_severity = "high"
                        elif severity == "moderate":
                            mapped_severity = "medium"
                        elif severity == "low":
                            mapped_severity = "low"
                        else:
                            mapped_severity = "info"
                        
                        issues.append(SecurityIssue(
                            issue_id=f"npm_vuln_{vuln_name}",
                            category="vulnerability",
                            severity=mapped_severity,
                            title=f"NPM Vulnerability: {vuln_name}",
                            description=vuln_data.get("title", "No description available"),
                            affected_component=f"Frontend dependency: {vuln_name}",
                            recommendation=f"Update {vuln_name} to a secure version",
                            cve_id=vuln_data.get("cve", None)
                        ))
                    
                    if vulnerabilities:
                        recommendations.append("Update vulnerable npm dependencies")
                        recommendations.append("Run 'npm audit fix' to automatically fix vulnerabilities")
                        recommendations.append("Consider using npm-audit-resolver for complex dependency conflicts")
                
                except json.JSONDecodeError:
                    logger.warning("Failed to parse npm audit output")
        
        except subprocess.TimeoutExpired:
            issues.append(SecurityIssue(
                issue_id="npm_audit_timeout",
                category="misconfiguration",
                severity="medium",
                title="NPM audit timeout",
                description="npm audit command timed out after 60 seconds",
                affected_component="Frontend dependencies",
                recommendation="Check npm configuration and network connectivity"
            ))
        
        except Exception as e:
            logger.error(f"NPM audit failed: {e}")
        
        return issues, recommendations

    async def _run_python_safety_check(self) -> tuple[List[SecurityIssue], List[str]]:
        """Run safety check for Python dependencies"""
        issues = []
        recommendations = []
        
        try:
            # Check if requirements.txt exists
            requirements_file = self.backend_path / "requirements.txt"
            if not requirements_file.exists():
                return issues, recommendations
            
            # Try to run safety check (if available)
            try:
                result = subprocess.run(
                    ["safety", "check", "--json", "--file", str(requirements_file)],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.stdout:
                    try:
                        safety_data = json.loads(result.stdout)
                        
                        for vuln in safety_data:
                            issues.append(SecurityIssue(
                                issue_id=f"python_vuln_{vuln.get('id', 'unknown')}",
                                category="vulnerability",
                                severity="high",  # Safety typically reports serious issues
                                title=f"Python Vulnerability: {vuln.get('package', 'Unknown package')}",
                                description=vuln.get("advisory", "No description available"),
                                affected_component=f"Backend dependency: {vuln.get('package', 'Unknown')}",
                                recommendation=f"Update {vuln.get('package')} to version {vuln.get('safe_versions', 'latest')}",
                                cve_id=vuln.get("cve", None)
                            ))
                        
                        if safety_data:
                            recommendations.append("Update vulnerable Python dependencies")
                            recommendations.append("Use pip-audit as an alternative vulnerability scanner")
                    
                    except json.JSONDecodeError:
                        logger.warning("Failed to parse safety check output")
            
            except FileNotFoundError:
                # Safety not installed - add as info issue
                issues.append(SecurityIssue(
                    issue_id="safety_not_installed",
                    category="best_practice",
                    severity="info",
                    title="Python vulnerability scanner not available",
                    description="Safety package is not installed for Python vulnerability scanning",
                    affected_component="Backend dependencies",
                    recommendation="Install safety package: pip install safety"
                ))
        
        except Exception as e:
            logger.error(f"Python safety check failed: {e}")
        
        return issues, recommendations

    async def _check_https_enforcement(self, environment: str, options: Dict[str, Any]) -> tuple[List[SecurityIssue], List[str]]:
        """Check HTTPS enforcement"""
        issues = []
        recommendations = []
        
        base_url = options.get("base_url", "https://vimarsh-functions.azurewebsites.net")
        
        try:
            # Test HTTP to HTTPS redirect
            http_url = base_url.replace("https://", "http://")
            
            response = requests.get(f"{http_url}/api/health", allow_redirects=False, timeout=10)
            
            if response.status_code not in [301, 302, 308]:
                issues.append(SecurityIssue(
                    issue_id="https_not_enforced",
                    category="misconfiguration",
                    severity="high",
                    title="HTTPS not properly enforced",
                    description=f"HTTP requests are not being redirected to HTTPS (status: {response.status_code})",
                    affected_component="Web server configuration",
                    recommendation="Configure automatic HTTP to HTTPS redirects"
                ))
                recommendations.append("Enable HTTPS enforcement in Azure App Service")
            
            # Check HSTS header
            https_response = requests.get(f"{base_url}/api/health", timeout=10)
            hsts_header = https_response.headers.get("Strict-Transport-Security")
            
            if not hsts_header:
                issues.append(SecurityIssue(
                    issue_id="missing_hsts_header",
                    category="misconfiguration",
                    severity="medium",
                    title="Missing HSTS header",
                    description="Strict-Transport-Security header not present",
                    affected_component="Web server configuration",
                    recommendation="Add HSTS header to enforce HTTPS connections"
                ))
                recommendations.append("Configure HSTS header with appropriate max-age value")
        
        except Exception as e:
            logger.error(f"HTTPS enforcement check failed: {e}")
            issues.append(SecurityIssue(
                issue_id="https_check_failed",
                category="misconfiguration",
                severity="medium",
                title="HTTPS enforcement check failed",
                description=f"Could not verify HTTPS enforcement: {str(e)}",
                affected_component="Network connectivity",
                recommendation="Check network connectivity and service availability"
            ))
        
        return issues, recommendations

    async def _check_security_headers(self, environment: str, options: Dict[str, Any]) -> tuple[List[SecurityIssue], List[str]]:
        """Check security headers"""
        issues = []
        recommendations = []
        
        base_url = options.get("base_url", "https://vimarsh-functions.azurewebsites.net")
        
        try:
            response = requests.get(f"{base_url}/api/health", timeout=10)
            headers = response.headers
            
            # Required security headers
            required_headers = {
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": ["DENY", "SAMEORIGIN"],
                "X-XSS-Protection": "1; mode=block",
                "Content-Security-Policy": None,  # Should exist but value varies
                "Referrer-Policy": None
            }
            
            for header_name, expected_value in required_headers.items():
                header_value = headers.get(header_name)
                
                if not header_value:
                    issues.append(SecurityIssue(
                        issue_id=f"missing_header_{header_name.lower().replace('-', '_')}",
                        category="misconfiguration",
                        severity="medium",
                        title=f"Missing security header: {header_name}",
                        description=f"The {header_name} security header is not present",
                        affected_component="Web server configuration",
                        recommendation=f"Add {header_name} header to HTTP responses"
                    ))
                elif expected_value and isinstance(expected_value, list):
                    if header_value not in expected_value:
                        issues.append(SecurityIssue(
                            issue_id=f"weak_header_{header_name.lower().replace('-', '_')}",
                            category="misconfiguration",
                            severity="low",
                            title=f"Weak security header: {header_name}",
                            description=f"{header_name} header value '{header_value}' might not be optimal",
                            affected_component="Web server configuration",
                            recommendation=f"Consider using a stronger {header_name} value: {', '.join(expected_value)}"
                        ))
                elif expected_value and header_value != expected_value:
                    issues.append(SecurityIssue(
                        issue_id=f"incorrect_header_{header_name.lower().replace('-', '_')}",
                        category="misconfiguration",
                        severity="low",
                        title=f"Incorrect security header: {header_name}",
                        description=f"{header_name} header has value '{header_value}', expected '{expected_value}'",
                        affected_component="Web server configuration",
                        recommendation=f"Set {header_name} header to '{expected_value}'"
                    ))
            
            if issues:
                recommendations.append("Configure security headers in Azure App Service or application middleware")
                recommendations.append("Use Azure Front Door or Application Gateway for additional security header control")
        
        except Exception as e:
            logger.error(f"Security headers check failed: {e}")
        
        return issues, recommendations

    async def _check_cors_configuration(self, environment: str, options: Dict[str, Any]) -> tuple[List[SecurityIssue], List[str]]:
        """Check CORS configuration"""
        issues = []
        recommendations = []
        
        base_url = options.get("base_url", "https://vimarsh-functions.azurewebsites.net")
        
        try:
            # Test CORS headers
            response = requests.get(f"{base_url}/api/health", timeout=10)
            cors_origin = response.headers.get("Access-Control-Allow-Origin")
            
            if cors_origin == "*":
                issues.append(SecurityIssue(
                    issue_id="permissive_cors",
                    category="misconfiguration",
                    severity="medium",
                    title="Permissive CORS configuration",
                    description="Access-Control-Allow-Origin is set to '*' which allows any origin",
                    affected_component="CORS configuration",
                    recommendation="Configure specific allowed origins instead of using wildcard"
                ))
                recommendations.append("Restrict CORS to specific frontend domains")
            
            # Check for credentials with wildcard origin
            cors_credentials = response.headers.get("Access-Control-Allow-Credentials")
            if cors_origin == "*" and cors_credentials == "true":
                issues.append(SecurityIssue(
                    issue_id="cors_credentials_wildcard",
                    category="vulnerability",
                    severity="high",
                    title="CORS credentials with wildcard origin",
                    description="Access-Control-Allow-Credentials is true with wildcard origin",
                    affected_component="CORS configuration",
                    recommendation="Never use credentials with wildcard CORS origin"
                ))
        
        except Exception as e:
            logger.error(f"CORS configuration check failed: {e}")
        
        return issues, recommendations

    async def _check_authentication_config(self, environment: str, options: Dict[str, Any]) -> tuple[List[SecurityIssue], List[str]]:
        """Check authentication configuration"""
        issues = []
        recommendations = []
        
        # This would check authentication configuration
        # For now, add placeholder checks
        
        issues.append(SecurityIssue(
            issue_id="auth_config_placeholder",
            category="best_practice",
            severity="info",
            title="Authentication configuration check",
            description="Authentication configuration verification not yet implemented",
            affected_component="Authentication system",
            recommendation="Implement comprehensive authentication security checks"
        ))
        
        recommendations.append("Verify Azure Entra ID configuration")
        recommendations.append("Check token validation and expiration settings")
        
        return issues, recommendations

    async def get_audit_status(self, audit_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a security audit"""
        audit = self.active_audits.get(audit_id)
        if not audit:
            return None
        
        return asdict(audit)

    async def get_all_audits(self, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all security audits with optional status filter"""
        audits = list(self.active_audits.values())
        
        if status_filter:
            audits = [a for a in audits if a.status == status_filter]
        
        return [asdict(audit) for audit in audits]

    async def get_audit_types(self) -> Dict[str, Any]:
        """Get available audit types"""
        return self.audit_types

    async def get_security_summary(self) -> Dict[str, Any]:
        """Get security summary across all audits"""
        all_audits = list(self.active_audits.values())
        completed_audits = [a for a in all_audits if a.status == "completed"]
        
        if not completed_audits:
            return {
                "total_audits": len(all_audits),
                "completed_audits": 0,
                "total_issues": 0,
                "critical_issues": 0,
                "high_issues": 0,
                "medium_issues": 0,
                "low_issues": 0,
                "last_audit": None
            }
        
        # Aggregate statistics from completed audits
        total_issues = sum(a.total_issues for a in completed_audits)
        critical_issues = sum(a.critical_issues for a in completed_audits)
        high_issues = sum(a.high_issues for a in completed_audits)
        medium_issues = sum(a.medium_issues for a in completed_audits)
        low_issues = sum(a.low_issues for a in completed_audits)
        
        # Get most recent audit
        latest_audit = max(completed_audits, key=lambda a: a.started_at)
        
        return {
            "total_audits": len(all_audits),
            "completed_audits": len(completed_audits),
            "total_issues": total_issues,
            "critical_issues": critical_issues,
            "high_issues": high_issues,
            "medium_issues": medium_issues,
            "low_issues": low_issues,
            "last_audit": {
                "audit_id": latest_audit.audit_id,
                "audit_type": latest_audit.audit_type,
                "completed_at": latest_audit.completed_at,
                "issues_found": latest_audit.total_issues
            }
        }

# Initialize service instance
security_service = SecurityComplianceService()
