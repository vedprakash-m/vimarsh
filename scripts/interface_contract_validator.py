#!/usr/bin/env python3
"""
Interface Contract Validator for Vimarsh

This script systematically analyzes test files to identify all method calls
and compares them against actual implementations to find interface gaps.
"""

import ast
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
import importlib.util

class InterfaceContractValidator:
    """Validates that test interfaces match actual implementations"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.backend_root = project_root / "backend"
        self.test_method_calls = {}
        self.implementation_methods = {}
        self.interface_gaps = []
        
    def analyze_test_files(self) -> Dict[str, Set[str]]:
        """Extract method calls from test files"""
        test_files = list(self.backend_root.glob("**/test_*.py"))
        
        for test_file in test_files:
            try:
                with open(test_file, 'r') as f:
                    content = f.read()
                
                # Parse AST to find method calls
                tree = ast.parse(content)
                method_calls = self._extract_method_calls(tree)
                
                # Group by class/module
                for class_name, methods in method_calls.items():
                    if class_name not in self.test_method_calls:
                        self.test_method_calls[class_name] = set()
                    self.test_method_calls[class_name].update(methods)
                    
            except Exception as e:
                print(f"Error analyzing {test_file}: {e}")
                
        return self.test_method_calls
    
    def _extract_method_calls(self, tree: ast.AST) -> Dict[str, Set[str]]:
        """Extract method calls from AST"""
        method_calls = {}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute):
                # Look for patterns like self.processor.method_name()
                if isinstance(node.value, ast.Attribute):
                    class_attr = node.value.attr
                    method_name = node.attr
                    
                    if class_attr not in method_calls:
                        method_calls[class_attr] = set()
                    method_calls[class_attr].add(method_name)
                    
                # Look for direct method calls
                elif isinstance(node.value, ast.Name):
                    obj_name = node.value.id
                    method_name = node.attr
                    
                    if obj_name not in method_calls:
                        method_calls[obj_name] = set()
                    method_calls[obj_name].add(method_name)
        
        return method_calls
    
    def analyze_implementations(self) -> Dict[str, Set[str]]:
        """Extract actual method implementations"""
        impl_files = []
        
        # Find all Python implementation files
        for pattern in ["**/*.py"]:
            impl_files.extend(self.backend_root.glob(pattern))
        
        # Filter out test files
        impl_files = [f for f in impl_files if not f.name.startswith("test_")]
        
        for impl_file in impl_files:
            try:
                with open(impl_file, 'r') as f:
                    content = f.read()
                
                # Parse AST to find class definitions and methods
                tree = ast.parse(content)
                classes_methods = self._extract_class_methods(tree)
                
                for class_name, methods in classes_methods.items():
                    if class_name not in self.implementation_methods:
                        self.implementation_methods[class_name] = set()
                    self.implementation_methods[class_name].update(methods)
                    
            except Exception as e:
                print(f"Error analyzing {impl_file}: {e}")
                
        return self.implementation_methods
    
    def _extract_class_methods(self, tree: ast.AST) -> Dict[str, Set[str]]:
        """Extract class definitions and their methods"""
        classes_methods = {}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name
                methods = set()
                
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        methods.add(item.name)
                
                classes_methods[class_name] = methods
        
        return classes_methods
    
    def find_interface_gaps(self) -> List[Dict]:
        """Find gaps between test expectations and implementations"""
        gaps = []
        
        # Map common class name patterns
        class_mappings = {
            'processor': 'AudioProcessor',
            'speech_processor': 'SpeechProcessor', 
            'tts_optimizer': 'SpiritualTTSOptimizer',
            'sanskrit_optimizer': 'SanskritRecognitionOptimizer'
        }
        
        for test_class, test_methods in self.test_method_calls.items():
            # Try to find matching implementation class
            impl_class = class_mappings.get(test_class, test_class)
            
            if impl_class in self.implementation_methods:
                impl_methods = self.implementation_methods[impl_class]
                missing_methods = test_methods - impl_methods
                
                if missing_methods:
                    gaps.append({
                        'test_class': test_class,
                        'impl_class': impl_class,
                        'missing_methods': missing_methods,
                        'existing_methods': impl_methods,
                        'gap_count': len(missing_methods)
                    })
            else:
                gaps.append({
                    'test_class': test_class,
                    'impl_class': impl_class,
                    'missing_methods': test_methods,
                    'existing_methods': set(),
                    'gap_count': len(test_methods),
                    'note': 'Implementation class not found'
                })
        
        return gaps
    
    def generate_report(self) -> str:
        """Generate comprehensive interface gap report"""
        report = []
        report.append("# Interface Contract Validation Report")
        report.append(f"**Generated**: {os.popen('date').read().strip()}")
        report.append("")
        
        # Analyze test files
        print("Analyzing test files...")
        self.analyze_test_files()
        
        # Analyze implementations  
        print("Analyzing implementations...")
        self.analyze_implementations()
        
        # Find gaps
        print("Finding interface gaps...")
        gaps = self.find_interface_gaps()
        
        # Summary
        total_gaps = sum(gap['gap_count'] for gap in gaps)
        report.append(f"## Summary")
        report.append(f"- **Total Classes Analyzed**: {len(self.test_method_calls)}")
        report.append(f"- **Classes with Gaps**: {len(gaps)}")
        report.append(f"- **Total Missing Methods**: {total_gaps}")
        report.append("")
        
        # Detailed gaps
        report.append("## Interface Gaps by Priority")
        
        # Sort by gap count (highest priority first)
        gaps.sort(key=lambda x: x['gap_count'], reverse=True)
        
        for i, gap in enumerate(gaps, 1):
            report.append(f"### {i}. {gap['impl_class']} (Test: {gap['test_class']})")
            report.append(f"**Missing Methods**: {gap['gap_count']}")
            
            if gap.get('note'):
                report.append(f"**Note**: {gap['note']}")
            
            if gap['missing_methods']:
                report.append("**Methods to Implement**:")
                for method in sorted(gap['missing_methods']):
                    report.append(f"- `{method}()`")
            
            if gap['existing_methods']:
                report.append("**Existing Methods**:")
                for method in sorted(list(gap['existing_methods'])[:5]):  # Show first 5
                    report.append(f"- `{method}()`")
                if len(gap['existing_methods']) > 5:
                    report.append(f"- ... and {len(gap['existing_methods']) - 5} more")
            
            report.append("")
        
        return "\n".join(report)

def main():
    """Run interface contract validation"""
    project_root = Path(__file__).parent.parent
    validator = InterfaceContractValidator(project_root)
    
    report = validator.generate_report()
    
    # Save report
    report_file = project_root / "INTERFACE_CONTRACT_GAPS.md"
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"Interface contract analysis complete!")
    print(f"Report saved to: {report_file}")
    print("\nTop 3 Priority Issues:")
    
    # Show top issues
    gaps = validator.find_interface_gaps()
    gaps.sort(key=lambda x: x['gap_count'], reverse=True)
    
    for i, gap in enumerate(gaps[:3], 1):
        print(f"{i}. {gap['impl_class']}: {gap['gap_count']} missing methods")

if __name__ == "__main__":
    main()
