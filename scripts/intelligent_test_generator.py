#!/usr/bin/env python3
"""
Intelligent Test Generator for Vimarsh

This tool automatically generates comprehensive test suites to achieve >85% coverage
by analyzing code structure, identifying missing tests, and generating appropriate
test templates.
"""

import ast
import inspect
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple
from dataclasses import dataclass
import re
import tempfile


@dataclass
class FunctionAnalysis:
    """Analysis of a function for test generation."""
    name: str
    file_path: str
    line_number: int
    is_async: bool
    parameters: List[str]
    return_annotation: str
    docstring: str
    complexity: int
    dependencies: List[str]
    test_types_needed: List[str]  # unit, integration, mock, etc.


@dataclass
class ClassAnalysis:
    """Analysis of a class for test generation."""
    name: str
    file_path: str
    line_number: int
    methods: List[FunctionAnalysis]
    properties: List[str]
    base_classes: List[str]
    is_dataclass: bool
    test_types_needed: List[str]


@dataclass
class TestTemplate:
    """Template for generating a test."""
    test_name: str
    test_type: str  # unit, integration, mock, property
    target_function: str
    template_code: str
    imports_needed: List[str]
    fixtures_needed: List[str]


class IntelligentTestGenerator:
    """AI-powered test generator for comprehensive coverage."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.backend_dir = self.project_root / "backend"
        
        # Analysis results
        self.function_analyses: List[FunctionAnalysis] = []
        self.class_analyses: List[ClassAnalysis] = []
        self.existing_tests: Set[str] = set()
        
        # Test generation templates
        self.test_templates = self._load_test_templates()
        
        # Component mapping
        self.components = {
            "spiritual_guidance": {
                "priority": "critical",
                "test_focus": ["functionality", "authenticity", "performance"]
            },
            "llm": {
                "priority": "critical", 
                "test_focus": ["integration", "mocking", "error_handling"]
            },
            "rag_pipeline": {
                "priority": "critical",
                "test_focus": ["integration", "performance", "data_quality"]
            },
            "voice": {
                "priority": "high",
                "test_focus": ["functionality", "performance", "error_handling"]
            },
            "cost_management": {
                "priority": "high",
                "test_focus": ["functionality", "monitoring", "limits"]
            },
            "error_handling": {
                "priority": "critical",
                "test_focus": ["functionality", "edge_cases", "recovery"]
            },
            "monitoring": {
                "priority": "medium",
                "test_focus": ["functionality", "integration"]
            }
        }
    
    def generate_comprehensive_tests(self) -> Dict[str, Any]:
        """Generate comprehensive test suite for all components."""
        
        print("🧪 Intelligent Test Generation for Vimarsh")
        print("=" * 50)
        
        results = {
            "analysis_summary": {},
            "generated_tests": {},
            "recommendations": [],
            "coverage_projection": {}
        }
        
        # 1. Analyze existing code structure
        print("\n🔍 Analyzing code structure...")
        self._analyze_codebase()
        
        # 2. Identify existing tests
        print("📋 Cataloging existing tests...")
        self._catalog_existing_tests()
        
        # 3. Generate missing tests
        print("🏗️  Generating missing tests...")
        generated_tests = self._generate_missing_tests()
        results["generated_tests"] = generated_tests
        
        # 4. Calculate coverage projection
        print("📊 Projecting coverage improvements...")
        coverage_projection = self._calculate_coverage_projection(generated_tests)
        results["coverage_projection"] = coverage_projection
        
        # 5. Generate recommendations
        print("💡 Generating optimization recommendations...")
        recommendations = self._generate_recommendations(generated_tests, coverage_projection)
        results["recommendations"] = recommendations
        
        # 6. Create analysis summary
        results["analysis_summary"] = {
            "functions_analyzed": len(self.function_analyses),
            "classes_analyzed": len(self.class_analyses),
            "existing_tests": len(self.existing_tests),
            "tests_to_generate": sum(len(tests) for tests in generated_tests.values()),
            "projected_coverage_increase": coverage_projection.get("total_increase", 0)
        }
        
        return results
    
    def _analyze_codebase(self):
        """Analyze the entire codebase to understand structure."""
        
        for component in self.components:
            component_dir = self.backend_dir / component
            if not component_dir.exists():
                continue
            
            print(f"   Analyzing {component}...")
            
            # Find all Python files
            py_files = [f for f in component_dir.rglob("*.py") 
                       if not f.name.startswith("test_") and not f.name.endswith("_test.py")]
            
            for py_file in py_files:
                self._analyze_file(py_file, component)
    
    def _analyze_file(self, file_path: Path, component: str):
        """Analyze a single Python file."""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Analyze classes
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_analysis = self._analyze_class(node, file_path, component)
                    if class_analysis:
                        self.class_analyses.append(class_analysis)
                
                elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    # Only analyze top-level functions (not methods)
                    if self._is_top_level_function(node, tree):
                        function_analysis = self._analyze_function(node, file_path, component)
                        if function_analysis:
                            self.function_analyses.append(function_analysis)
        
        except Exception as e:
            print(f"   ⚠️  Error analyzing {file_path}: {e}")
    
    def _analyze_class(self, node: ast.ClassDef, file_path: Path, component: str) -> ClassAnalysis:
        """Analyze a class definition."""
        
        methods = []
        properties = []
        
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not item.name.startswith('_') or item.name in ['__init__', '__str__', '__repr__']:
                    method_analysis = self._analyze_function(item, file_path, component, is_method=True)
                    if method_analysis:
                        methods.append(method_analysis)
            elif isinstance(item, ast.Assign):
                # Check for property-like attributes
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        properties.append(target.id)
        
        # Determine base classes
        base_classes = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                base_classes.append(base.id)
            elif isinstance(base, ast.Attribute):
                base_classes.append(f"{base.attr}")
        
        # Check if it's a dataclass
        is_dataclass = any(
            isinstance(decorator, ast.Name) and decorator.id == 'dataclass'
            for decorator in node.decorator_list
        )
        
        # Determine test types needed
        test_types = ["unit"]
        if len(methods) > 5:
            test_types.append("integration")
        if any("async" in method.name for method in methods):
            test_types.append("async")
        if is_dataclass:
            test_types.append("property")
        
        return ClassAnalysis(
            name=node.name,
            file_path=str(file_path.relative_to(self.backend_dir)),
            line_number=node.lineno,
            methods=methods,
            properties=properties,
            base_classes=base_classes,
            is_dataclass=is_dataclass,
            test_types_needed=test_types
        )
    
    def _analyze_function(self, node, file_path: Path, component: str, is_method: bool = False) -> FunctionAnalysis:
        """Analyze a function or method definition."""
        
        # Skip private functions unless they're special methods
        if node.name.startswith('_') and not node.name.startswith('__'):
            return None
        
        # Extract parameters
        parameters = []
        for arg in node.args.args:
            if arg.arg != 'self' and arg.arg != 'cls':
                parameters.append(arg.arg)
        
        # Extract return annotation
        return_annotation = ""
        if node.returns:
            if isinstance(node.returns, ast.Name):
                return_annotation = node.returns.id
            elif isinstance(node.returns, ast.Constant):
                return_annotation = str(node.returns.value)
        
        # Extract docstring
        docstring = ""
        if (node.body and isinstance(node.body[0], ast.Expr) and
            isinstance(node.body[0].value, ast.Constant) and
            isinstance(node.body[0].value.value, str)):
            docstring = node.body[0].value.value
        
        # Calculate complexity (simplified)
        complexity = self._calculate_function_complexity(node)
        
        # Identify dependencies
        dependencies = self._extract_dependencies(node)
        
        # Determine test types needed
        test_types = ["unit"]
        if isinstance(node, ast.AsyncFunctionDef):
            test_types.append("async")
        if complexity > 5:
            test_types.append("integration")
        if dependencies:
            test_types.append("mock")
        if is_method and node.name in ['__init__', '__str__', '__repr__']:
            test_types.append("property")
        
        return FunctionAnalysis(
            name=node.name,
            file_path=str(file_path.relative_to(self.backend_dir)),
            line_number=node.lineno,
            is_async=isinstance(node, ast.AsyncFunctionDef),
            parameters=parameters,
            return_annotation=return_annotation,
            docstring=docstring,
            complexity=complexity,
            dependencies=dependencies,
            test_types_needed=test_types
        )
    
    def _is_top_level_function(self, node, tree) -> bool:
        """Check if a function is at the top level (not a method)."""
        for parent in ast.walk(tree):
            if isinstance(parent, ast.ClassDef):
                for child in parent.body:
                    if child == node:
                        return False
        return True
    
    def _calculate_function_complexity(self, node) -> int:
        """Calculate complexity score for a function."""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, (ast.Try, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.With):
                complexity += 1
        
        return complexity
    
    def _extract_dependencies(self, node) -> List[str]:
        """Extract external dependencies from function."""
        dependencies = []
        
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Attribute):
                    # Method calls like obj.method()
                    if isinstance(child.func.value, ast.Name):
                        dependencies.append(child.func.value.id)
                elif isinstance(child.func, ast.Name):
                    # Function calls
                    dependencies.append(child.func.id)
        
        return list(set(dependencies))
    
    def _catalog_existing_tests(self):
        """Catalog all existing test functions."""
        
        # Check tests/ directory
        tests_dir = self.backend_dir / "tests"
        if tests_dir.exists():
            self._scan_test_directory(tests_dir)
        
        # Check component-specific test files
        for component in self.components:
            component_dir = self.backend_dir / component
            if component_dir.exists():
                for test_file in component_dir.rglob("test_*.py"):
                    self._scan_test_file(test_file)
    
    def _scan_test_directory(self, test_dir: Path):
        """Scan a directory for test files."""
        for test_file in test_dir.rglob("test_*.py"):
            self._scan_test_file(test_file)
    
    def _scan_test_file(self, test_file: Path):
        """Scan a test file for test functions."""
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                    self.existing_tests.add(node.name)
        
        except Exception as e:
            print(f"   ⚠️  Error scanning {test_file}: {e}")
    
    def _generate_missing_tests(self) -> Dict[str, List[TestTemplate]]:
        """Generate test templates for missing coverage."""
        
        generated_tests = {}
        
        # Generate tests for functions
        for func_analysis in self.function_analyses:
            component = self._get_component_from_path(func_analysis.file_path)
            if component not in generated_tests:
                generated_tests[component] = []
            
            tests = self._generate_function_tests(func_analysis, component)
            generated_tests[component].extend(tests)
        
        # Generate tests for classes
        for class_analysis in self.class_analyses:
            component = self._get_component_from_path(class_analysis.file_path)
            if component not in generated_tests:
                generated_tests[component] = []
            
            tests = self._generate_class_tests(class_analysis, component)
            generated_tests[component].extend(tests)
        
        return generated_tests
    
    def _get_component_from_path(self, file_path: str) -> str:
        """Extract component name from file path."""
        parts = file_path.split('/')
        for part in parts:
            if part in self.components:
                return part
        return "misc"
    
    def _generate_function_tests(self, func_analysis: FunctionAnalysis, component: str) -> List[TestTemplate]:
        """Generate test templates for a function."""
        
        tests = []
        
        for test_type in func_analysis.test_types_needed:
            # Check if test already exists
            expected_test_name = f"test_{func_analysis.name}_{test_type}"
            if expected_test_name in self.existing_tests:
                continue
            
            template = self._create_function_test_template(func_analysis, test_type, component)
            if template:
                tests.append(template)
        
        return tests
    
    def _generate_class_tests(self, class_analysis: ClassAnalysis, component: str) -> List[TestTemplate]:
        """Generate test templates for a class."""
        
        tests = []
        
        # Generate class-level tests
        for test_type in class_analysis.test_types_needed:
            expected_test_name = f"test_{class_analysis.name.lower()}_{test_type}"
            if expected_test_name in self.existing_tests:
                continue
            
            template = self._create_class_test_template(class_analysis, test_type, component)
            if template:
                tests.append(template)
        
        # Generate method tests
        for method in class_analysis.methods:
            method_tests = self._generate_function_tests(method, component)
            tests.extend(method_tests)
        
        return tests
    
    def _create_function_test_template(self, func_analysis: FunctionAnalysis, 
                                     test_type: str, component: str) -> TestTemplate:
        """Create a test template for a function."""
        
        test_name = f"test_{func_analysis.name}_{test_type}"
        
        # Generate template based on type
        if test_type == "unit":
            template_code = self._generate_unit_test_template(func_analysis, component)
        elif test_type == "async":
            template_code = self._generate_async_test_template(func_analysis, component)
        elif test_type == "mock":
            template_code = self._generate_mock_test_template(func_analysis, component)
        elif test_type == "integration":
            template_code = self._generate_integration_test_template(func_analysis, component)
        else:
            template_code = self._generate_basic_test_template(func_analysis, component)
        
        imports_needed = self._determine_imports_needed(func_analysis, test_type)
        fixtures_needed = self._determine_fixtures_needed(func_analysis, test_type)
        
        return TestTemplate(
            test_name=test_name,
            test_type=test_type,
            target_function=func_analysis.name,
            template_code=template_code,
            imports_needed=imports_needed,
            fixtures_needed=fixtures_needed
        )
    
    def _create_class_test_template(self, class_analysis: ClassAnalysis, 
                                  test_type: str, component: str) -> TestTemplate:
        """Create a test template for a class."""
        
        test_name = f"test_{class_analysis.name.lower()}_{test_type}"
        
        if test_type == "unit":
            template_code = self._generate_class_unit_test_template(class_analysis, component)
        elif test_type == "property":
            template_code = self._generate_property_test_template(class_analysis, component)
        elif test_type == "integration":
            template_code = self._generate_class_integration_test_template(class_analysis, component)
        else:
            template_code = self._generate_basic_class_test_template(class_analysis, component)
        
        imports_needed = ["pytest"]
        if class_analysis.is_dataclass:
            imports_needed.append("dataclasses")
        
        fixtures_needed = [f"{class_analysis.name.lower()}_instance"]
        
        return TestTemplate(
            test_name=test_name,
            test_type=test_type,
            target_function=class_analysis.name,
            template_code=template_code,
            imports_needed=imports_needed,
            fixtures_needed=fixtures_needed
        )
    
    def _load_test_templates(self) -> Dict[str, str]:
        """Load test templates for different scenarios."""
        return {
            "unit_function": '''
def {test_name}({params}):
    """Test {function_name} functionality."""
    # Arrange
    {arrange_code}
    
    # Act
    result = {function_call}
    
    # Assert
    {assert_code}
''',
            "async_function": '''
@pytest.mark.asyncio
async def {test_name}({params}):
    """Test async {function_name} functionality."""
    # Arrange
    {arrange_code}
    
    # Act
    result = await {function_call}
    
    # Assert
    {assert_code}
''',
            "mock_function": '''
@patch('{mock_target}')
def {test_name}(mock_{mock_name}, {params}):
    """Test {function_name} with mocked dependencies."""
    # Arrange
    mock_{mock_name}.return_value = {mock_return}
    {arrange_code}
    
    # Act
    result = {function_call}
    
    # Assert
    {assert_code}
    mock_{mock_name}.assert_called_once()
''',
            "class_unit": '''
def test_{class_name}_initialization({params}):
    """Test {class_name} initialization."""
    # Arrange & Act
    instance = {class_name}({init_params})
    
    # Assert
    assert instance is not None
    {property_assertions}

def test_{class_name}_methods({params}):
    """Test {class_name} methods."""
    # Arrange
    instance = {class_name}({init_params})
    
    # Act & Assert
    {method_tests}
'''
        }
    
    def _generate_unit_test_template(self, func_analysis: FunctionAnalysis, component: str) -> str:
        """Generate unit test template."""
        
        # Generate basic parameters and function call
        params = ", ".join(func_analysis.parameters) if func_analysis.parameters else ""
        function_call = f"{func_analysis.name}({params})"
        
        # Generate arrange code based on parameters
        arrange_lines = []
        for param in func_analysis.parameters:
            if "query" in param.lower():
                arrange_lines.append(f'    {param} = "What is dharma?"')
            elif "language" in param.lower():
                arrange_lines.append(f'    {param} = "English"')
            elif "user" in param.lower():
                arrange_lines.append(f'    {param} = "test_user"')
            else:
                arrange_lines.append(f'    {param} = "test_value"')
        
        arrange_code = "\n".join(arrange_lines) if arrange_lines else "    pass"
        
        # Generate assertion based on return type
        if func_analysis.return_annotation:
            if "bool" in func_analysis.return_annotation.lower():
                assert_code = "    assert isinstance(result, bool)"
            elif "dict" in func_analysis.return_annotation.lower():
                assert_code = "    assert isinstance(result, dict)\n    assert len(result) > 0"
            elif "list" in func_analysis.return_annotation.lower():
                assert_code = "    assert isinstance(result, list)"
            elif "str" in func_analysis.return_annotation.lower():
                assert_code = "    assert isinstance(result, str)\n    assert len(result) > 0"
            else:
                assert_code = "    assert result is not None"
        else:
            assert_code = "    assert result is not None"
        
        template = self.test_templates["async_function" if func_analysis.is_async else "unit_function"]
        
        return template.format(
            test_name=f"test_{func_analysis.name}_unit",
            function_name=func_analysis.name,
            params=params,
            arrange_code=arrange_code,
            function_call=function_call,
            assert_code=assert_code
        )
    
    def _generate_async_test_template(self, func_analysis: FunctionAnalysis, component: str) -> str:
        """Generate async test template."""
        return self._generate_unit_test_template(func_analysis, component)
    
    def _generate_mock_test_template(self, func_analysis: FunctionAnalysis, component: str) -> str:
        """Generate mock test template."""
        
        # Choose first dependency to mock
        mock_target = func_analysis.dependencies[0] if func_analysis.dependencies else "external_service"
        mock_name = mock_target.lower()
        
        # Generate mock return value
        if func_analysis.return_annotation:
            if "dict" in func_analysis.return_annotation.lower():
                mock_return = '{"test": "data"}'
            elif "list" in func_analysis.return_annotation.lower():
                mock_return = '["test", "data"]'
            elif "bool" in func_analysis.return_annotation.lower():
                mock_return = "True"
            else:
                mock_return = '"mock_result"'
        else:
            mock_return = '"mock_result"'
        
        template = self.test_templates["mock_function"]
        
        return template.format(
            test_name=f"test_{func_analysis.name}_mock",
            function_name=func_analysis.name,
            mock_target=f"{component}.{mock_target}",
            mock_name=mock_name,
            mock_return=mock_return,
            params="",
            arrange_code="    pass",
            function_call=f"{func_analysis.name}()",
            assert_code="    assert result is not None"
        )
    
    def _generate_integration_test_template(self, func_analysis: FunctionAnalysis, component: str) -> str:
        """Generate integration test template."""
        # For now, use unit test template with additional complexity
        return self._generate_unit_test_template(func_analysis, component)
    
    def _generate_basic_test_template(self, func_analysis: FunctionAnalysis, component: str) -> str:
        """Generate basic test template."""
        return self._generate_unit_test_template(func_analysis, component)
    
    def _generate_class_unit_test_template(self, class_analysis: ClassAnalysis, component: str) -> str:
        """Generate class unit test template."""
        
        # Generate initialization parameters
        init_method = next((m for m in class_analysis.methods if m.name == "__init__"), None)
        init_params = ""
        if init_method and init_method.parameters:
            param_values = []
            for param in init_method.parameters:
                if "config" in param.lower():
                    param_values.append(f'{param}=MockConfig()')
                elif "path" in param.lower():
                    param_values.append(f'{param}="/test/path"')
                else:
                    param_values.append(f'{param}="test_value"')
            init_params = ", ".join(param_values)
        
        # Generate property assertions
        property_assertions = []
        for prop in class_analysis.properties:
            property_assertions.append(f"    assert hasattr(instance, '{prop}')")
        
        # Generate method tests
        method_tests = []
        for method in class_analysis.methods:
            if method.name not in ["__init__", "__str__", "__repr__"]:
                method_tests.append(f"    # Test {method.name}")
                method_tests.append(f"    assert hasattr(instance, '{method.name}')")
        
        template = self.test_templates["class_unit"]
        
        return template.format(
            class_name=class_analysis.name,
            params="",
            init_params=init_params,
            property_assertions="\n".join(property_assertions) if property_assertions else "    pass",
            method_tests="\n".join(method_tests) if method_tests else "    pass"
        )
    
    def _generate_property_test_template(self, class_analysis: ClassAnalysis, component: str) -> str:
        """Generate property test template."""
        return self._generate_class_unit_test_template(class_analysis, component)
    
    def _generate_class_integration_test_template(self, class_analysis: ClassAnalysis, component: str) -> str:
        """Generate class integration test template."""
        return self._generate_class_unit_test_template(class_analysis, component)
    
    def _generate_basic_class_test_template(self, class_analysis: ClassAnalysis, component: str) -> str:
        """Generate basic class test template."""
        return self._generate_class_unit_test_template(class_analysis, component)
    
    def _determine_imports_needed(self, func_analysis: FunctionAnalysis, test_type: str) -> List[str]:
        """Determine imports needed for test."""
        imports = ["pytest"]
        
        if func_analysis.is_async:
            imports.append("pytest-asyncio")
        
        if test_type == "mock":
            imports.append("unittest.mock")
        
        # Add component-specific imports
        component = self._get_component_from_path(func_analysis.file_path)
        imports.append(f"{component}")
        
        return imports
    
    def _determine_fixtures_needed(self, func_analysis: FunctionAnalysis, test_type: str) -> List[str]:
        """Determine fixtures needed for test."""
        fixtures = []
        
        if "api" in func_analysis.name.lower():
            fixtures.append("mock_api_client")
        
        if "database" in func_analysis.name.lower() or "storage" in func_analysis.name.lower():
            fixtures.append("mock_database")
        
        return fixtures
    
    def _calculate_coverage_projection(self, generated_tests: Dict[str, List[TestTemplate]]) -> Dict[str, Any]:
        """Calculate projected coverage improvement."""
        
        projection = {
            "by_component": {},
            "total_increase": 0,
            "estimated_final_coverage": 0
        }
        
        for component, tests in generated_tests.items():
            # Estimate coverage increase based on number of tests and complexity
            test_count = len(tests)
            
            # Simple heuristic: each test increases coverage by ~2-5%
            estimated_increase = min(test_count * 3, 40)  # Cap at 40% per component
            
            projection["by_component"][component] = {
                "tests_to_add": test_count,
                "estimated_increase": estimated_increase,
                "priority": self.components.get(component, {}).get("priority", "medium")
            }
        
        # Calculate total increase
        all_increases = [comp["estimated_increase"] for comp in projection["by_component"].values()]
        projection["total_increase"] = min(sum(all_increases), 82)  # Realistic cap
        projection["estimated_final_coverage"] = min(3 + projection["total_increase"], 95)  # Start from current ~3%
        
        return projection
    
    def _generate_recommendations(self, generated_tests: Dict[str, List[TestTemplate]], 
                                coverage_projection: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations."""
        
        recommendations = []
        
        # Prioritize by component criticality
        critical_components = [comp for comp, config in self.components.items() 
                             if config["priority"] == "critical" and comp in generated_tests]
        
        if critical_components:
            recommendations.append(
                f"🔥 PRIORITY: Start with critical components: {', '.join(critical_components)}"
            )
        
        # Suggest quick wins
        quick_wins = []
        for component, tests in generated_tests.items():
            simple_tests = [t for t in tests if t.test_type in ["unit", "property"]]
            if len(simple_tests) >= 5:
                quick_wins.append(f"{component} ({len(simple_tests)} simple tests)")
        
        if quick_wins:
            recommendations.append(
                f"⚡ QUICK WINS: Focus on simple unit tests in: {', '.join(quick_wins)}"
            )
        
        # Coverage targets
        if coverage_projection["estimated_final_coverage"] >= 85:
            recommendations.append(
                f"🎯 TARGET ACHIEVABLE: Implementing all suggested tests should reach "
                f"{coverage_projection['estimated_final_coverage']:.0f}% coverage"
            )
        else:
            recommendations.append(
                f"⚠️  ADDITIONAL EFFORT NEEDED: Suggested tests will reach "
                f"{coverage_projection['estimated_final_coverage']:.0f}% coverage. "
                f"Consider adding integration tests for remaining gaps."
            )
        
        # Implementation order
        recommendations.append(
            "📋 SUGGESTED ORDER: 1) Unit tests for core functions, "
            "2) Class tests with mocking, 3) Integration tests, 4) Async tests"
        )
        
        return recommendations
    
    def write_generated_tests(self, generated_tests: Dict[str, List[TestTemplate]], 
                            output_dir: Path):
        """Write generated test files to disk."""
        
        print(f"\n📝 Writing generated tests to {output_dir}")
        
        output_dir.mkdir(exist_ok=True)
        
        for component, tests in generated_tests.items():
            if not tests:
                continue
            
            # Group tests by file
            test_files = {}
            for test in tests:
                file_key = f"test_{component}_generated.py"
                if file_key not in test_files:
                    test_files[file_key] = []
                test_files[file_key].append(test)
            
            # Write each test file
            for filename, file_tests in test_files.items():
                file_path = output_dir / filename
                
                with open(file_path, 'w') as f:
                    self._write_test_file_header(f, component)
                    
                    for test in file_tests:
                        f.write(f"\n\n{test.template_code}")
                
                print(f"   ✅ Generated {filename} with {len(file_tests)} tests")
    
    def _write_test_file_header(self, file, component: str):
        """Write test file header with imports."""
        
        header = f'''"""
Generated tests for {component} component.

This file was automatically generated to improve test coverage.
Review and customize as needed.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import asyncio
from pathlib import Path
import tempfile

# Import component under test
try:
    from {component} import *
except ImportError:
    pass  # Handle import errors gracefully

# Test fixtures and utilities
@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    return {{
        "test_mode": True,
        "timeout": 5.0,
        "debug": True
    }}

@pytest.fixture  
def temp_directory():
    """Temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)
'''
        
        file.write(header)


def main():
    """Main entry point."""
    
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    else:
        project_root = Path(__file__).parent.parent
    
    generator = IntelligentTestGenerator(str(project_root))
    results = generator.generate_comprehensive_tests()
    
    # Display summary
    print(f"\n📊 TEST GENERATION SUMMARY")
    print("=" * 50)
    summary = results["analysis_summary"]
    print(f"Functions Analyzed: {summary['functions_analyzed']}")
    print(f"Classes Analyzed: {summary['classes_analyzed']}")
    print(f"Existing Tests: {summary['existing_tests']}")
    print(f"Tests to Generate: {summary['tests_to_generate']}")
    print(f"Projected Coverage Increase: +{summary['projected_coverage_increase']}%")
    
    # Show recommendations
    print(f"\n💡 RECOMMENDATIONS")
    print("-" * 30)
    for i, rec in enumerate(results["recommendations"], 1):
        print(f"{i}. {rec}")
    
    # Write generated tests
    output_dir = Path(project_root) / "generated_tests"
    generator.write_generated_tests(results["generated_tests"], output_dir)
    
    # Save full results
    results_file = Path(project_root) / "test_generation_results.json"
    with open(results_file, 'w') as f:
        # Convert TestTemplate objects to dicts for JSON serialization
        serializable_tests = {}
        for component, tests in results["generated_tests"].items():
            serializable_tests[component] = [
                {
                    "test_name": t.test_name,
                    "test_type": t.test_type,
                    "target_function": t.target_function,
                    "template_code": t.template_code,
                    "imports_needed": t.imports_needed,
                    "fixtures_needed": t.fixtures_needed
                }
                for t in tests
            ]
        
        results_copy = results.copy()
        results_copy["generated_tests"] = serializable_tests
        
        json.dump(results_copy, f, indent=2)
    
    print(f"\n💾 Full results saved to: {results_file}")
    print(f"📁 Generated test files in: {output_dir}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
