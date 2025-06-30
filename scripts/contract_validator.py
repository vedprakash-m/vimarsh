#!/usr/bin/env python3
"""
Contract Validation Tool

This script systematically validates API contracts between tests and implementations
to identify mismatches that cause CI/CD failures.
"""

import os
import ast
import sys
import importlib
import inspect
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from dataclasses import dataclass
from collections import defaultdict
import re


@dataclass
class ContractMismatch:
    """Represents a contract mismatch between test and implementation"""
    test_file: str
    line_number: int
    issue_type: str  # 'import', 'class_name', 'method_signature', 'parameter'
    expected: str
    actual: str
    severity: str  # 'critical', 'high', 'medium', 'low'
    description: str


@dataclass
class ValidationResult:
    """Results of contract validation"""
    total_tests_scanned: int
    total_contracts_checked: int
    mismatches: List[ContractMismatch]
    import_issues: List[ContractMismatch]
    signature_issues: List[ContractMismatch]
    parameter_issues: List[ContractMismatch]


class ContractValidator:
    """Validates API contracts between tests and implementations"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.backend_root = self.project_root / "backend"
        self.test_root = self.backend_root / "tests"
        self.mismatches = []
        
        # Known mappings for contract analysis
        self.class_mappings = {
            'ResponseValidator': 'SpiritualResponseValidator',
            'SemanticChunker': 'SemanticChunker',  # Same name, but parameter differences
        }
        
        self.parameter_mappings = {
            'SemanticChunker': {
                'respect_boundaries': 'preserve_verses'
            }
        }
    
    def validate_all_contracts(self) -> ValidationResult:
        """Validate all API contracts in the project"""
        print("🔍 Starting comprehensive contract validation...")
        
        test_files = list(self.test_root.rglob("test_*.py"))
        total_tests = len(test_files)
        total_contracts = 0
        
        for test_file in test_files:
            print(f"  📄 Analyzing {test_file.relative_to(self.project_root)}")
            contracts_in_file = self._validate_test_file(test_file)
            total_contracts += contracts_in_file
        
        # Categorize mismatches
        import_issues = [m for m in self.mismatches if m.issue_type == 'import']
        signature_issues = [m for m in self.mismatches if m.issue_type == 'method_signature']
        parameter_issues = [m for m in self.mismatches if m.issue_type == 'parameter']
        
        return ValidationResult(
            total_tests_scanned=total_tests,
            total_contracts_checked=total_contracts,
            mismatches=self.mismatches,
            import_issues=import_issues,
            signature_issues=signature_issues,
            parameter_issues=parameter_issues
        )
    
    def _validate_test_file(self, test_file: Path) -> int:
        """Validate contracts in a single test file"""
        contracts_checked = 0
        
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST to analyze imports and usage
            tree = ast.parse(content)
            
            # Check imports
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    contracts_checked += self._validate_import(test_file, node, content)
                elif isinstance(node, ast.Call):
                    contracts_checked += self._validate_method_call(test_file, node, content)
                elif isinstance(node, ast.ClassDef):
                    contracts_checked += self._validate_class_usage(test_file, node, content)
                    
        except Exception as e:
            print(f"    ⚠️  Error parsing {test_file}: {e}")
        
        return contracts_checked
    
    def _validate_import(self, test_file: Path, node: ast.ImportFrom, content: str) -> int:
        """Validate import statements"""
        if not node.module:
            return 0
        
        contracts_checked = 0
        line_number = node.lineno
        
        # Check if imported module exists
        module_path = node.module.replace('.', '/')
        
        # Try to find the actual module
        possible_paths = [
            self.backend_root / f"{module_path}.py",
            self.backend_root / module_path / "__init__.py"
        ]
        
        module_exists = any(p.exists() for p in possible_paths)
        
        if not module_exists:
            self.mismatches.append(ContractMismatch(
                test_file=str(test_file),
                line_number=line_number,
                issue_type='import',
                expected=node.module,
                actual='Module not found',
                severity='critical',
                description=f"Module '{node.module}' not found at expected paths"
            ))
            contracts_checked += 1
        
        # Check imported names
        if node.names:
            for alias in node.names:
                imported_name = alias.name
                contracts_checked += 1
                
                # Check if class name exists in our mappings (known mismatches)
                if imported_name in self.class_mappings:
                    actual_name = self.class_mappings[imported_name]
                    if imported_name != actual_name:
                        self.mismatches.append(ContractMismatch(
                            test_file=str(test_file),
                            line_number=line_number,
                            issue_type='class_name',
                            expected=imported_name,
                            actual=actual_name,
                            severity='high',
                            description=f"Class '{imported_name}' should be '{actual_name}'"
                        ))
        
        return contracts_checked
    
    def _validate_method_call(self, test_file: Path, node: ast.Call, content: str) -> int:
        """Validate method calls and their parameters"""
        contracts_checked = 0
        
        # Look for constructor calls with known parameter issues
        if isinstance(node.func, ast.Name):
            class_name = node.func.id
            if class_name in self.parameter_mappings:
                contracts_checked += 1
                
                # Check for known parameter mismatches
                for keyword in node.keywords:
                    param_name = keyword.arg
                    if param_name in self.parameter_mappings[class_name]:
                        correct_param = self.parameter_mappings[class_name][param_name]
                        self.mismatches.append(ContractMismatch(
                            test_file=str(test_file),
                            line_number=node.lineno,
                            issue_type='parameter',
                            expected=param_name,
                            actual=correct_param,
                            severity='high',
                            description=f"Parameter '{param_name}' should be '{correct_param}' for {class_name}"
                        ))
        
        return contracts_checked
    
    def _validate_class_usage(self, test_file: Path, node: ast.ClassDef, content: str) -> int:
        """Validate class usage patterns in tests"""
        # This can be extended to check class usage patterns
        return 0
    
    def generate_report(self, result: ValidationResult) -> str:
        """Generate a comprehensive validation report"""
        report = []
        report.append("=" * 80)
        report.append("🔍 CONTRACT VALIDATION REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Summary
        report.append(f"📊 SUMMARY:")
        report.append(f"   Test files scanned: {result.total_tests_scanned}")
        report.append(f"   Contracts checked: {result.total_contracts_checked}")
        report.append(f"   Total mismatches: {len(result.mismatches)}")
        report.append("")
        
        # Breakdown by category
        report.append(f"🏷️  MISMATCH BREAKDOWN:")
        report.append(f"   Import issues: {len(result.import_issues)}")
        report.append(f"   Signature issues: {len(result.signature_issues)}")
        report.append(f"   Parameter issues: {len(result.parameter_issues)}")
        report.append("")
        
        # Detailed issues
        if result.mismatches:
            report.append("🚨 DETAILED ISSUES:")
            report.append("")
            
            for mismatch in sorted(result.mismatches, key=lambda x: (x.severity, x.test_file)):
                severity_emoji = {"critical": "🔥", "high": "⚠️", "medium": "📋", "low": "ℹ️"}
                emoji = severity_emoji.get(mismatch.severity, "❓")
                
                report.append(f"{emoji} {mismatch.severity.upper()}: {mismatch.issue_type}")
                report.append(f"   File: {mismatch.test_file}:{mismatch.line_number}")
                report.append(f"   Expected: {mismatch.expected}")
                report.append(f"   Actual: {mismatch.actual}")
                report.append(f"   Description: {mismatch.description}")
                report.append("")
        else:
            report.append("✅ No contract mismatches found!")
        
        return "\n".join(report)


def main():
    """Main contract validation entry point"""
    project_root = os.getcwd()
    
    print("🔍 Vimarsh Contract Validation Tool")
    print("=" * 50)
    print(f"Project root: {project_root}")
    print()
    
    validator = ContractValidator(project_root)
    result = validator.validate_all_contracts()
    
    report = validator.generate_report(result)
    print(report)
    
    # Save report to file
    report_file = Path(project_root) / "docs" / "CONTRACT_VALIDATION_REPORT.md"
    with open(report_file, 'w') as f:
        f.write(f"# Contract Validation Report\n\n")
        f.write(f"Generated on: {os.popen('date').read().strip()}\n\n")
        f.write(f"```\n{report}\n```\n")
    
    print(f"\n📄 Full report saved to: {report_file}")
    
    # Return exit code based on severity of issues
    critical_issues = [m for m in result.mismatches if m.severity == 'critical']
    high_issues = [m for m in result.mismatches if m.severity == 'high']
    
    if critical_issues:
        print("\n🔥 CRITICAL issues found - immediate action required!")
        return 1
    elif high_issues:
        print("\n⚠️  HIGH severity issues found - should be addressed!")
        return 1
    else:
        print("\n✅ No critical contract issues found!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
