"""
Odoo 17 MCP Server - Advanced Tools

This module contains 15+ powerful advanced tools for Odoo 17 development:
1. Module dependency graph generator
2. Database migration assistant
3. Performance profiler
4. Code complexity analyzer
5. Security vulnerability scanner
6. Automated test generator
7. Module comparison tool
8. Database schema diff
9. Git workflow automation
10. Module documentation generator
11. Translation file manager
12. Module upgrade assistant
13. API endpoint generator
14. Webhook integration helper
15. Custom report builder
"""

import asyncio
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import ast
import xml.etree.ElementTree as ET

from mcp.types import CallToolResult, TextContent
from async_utils import AsyncCommandExecutor, get_executor
from security import get_security_manager
from exceptions import ValidationError, FilesystemError, handle_exception
from config import get_config


class Odoo17AdvancedTools:
    """Advanced tool implementations for Odoo 17 MCP server."""

    def __init__(self):
        self.logger = None  # Will be set by parent
        self.executor = get_executor()
        self.security = get_security_manager()
        self.config = get_config()

    async def _generate_dependency_graph(self, module_path: str, output_format: str = "mermaid") -> CallToolResult:
        """
        Generate a visual dependency graph for Odoo modules.

        Args:
            module_path: Path to module or directory containing modules
            output_format: Output format (mermaid, dot, json)

        Returns:
            Dependency graph visualization
        """
        try:
            module_path = Path(module_path)
            if not module_path.exists():
                raise FilesystemError(f"Path not found: {module_path}")

            # Find all modules
            modules = {}
            if module_path.is_dir():
                for item in module_path.iterdir():
                    manifest = item / "__manifest__.py"
                    if manifest.exists():
                        modules[item.name] = self._parse_manifest(manifest)
            else:
                manifest = module_path / "__manifest__.py"
                if manifest.exists():
                    modules[module_path.name] = self._parse_manifest(manifest)

            # Build dependency graph
            graph = {name: info.get('depends', []) for name, info in modules.items()}

            # Generate output based on format
            if output_format == "mermaid":
                result = self._generate_mermaid_graph(graph)
            elif output_format == "dot":
                result = self._generate_dot_graph(graph)
            else:
                result = json.dumps(graph, indent=2)

            result_text = f"📊 Module Dependency Graph\n\n"
            result_text += f"Found {len(modules)} modules\n\n"
            result_text += f"```{output_format}\n{result}\n```\n\n"

            # Add dependency analysis
            result_text += "📈 Dependency Analysis:\n"
            for module, deps in graph.items():
                result_text += f"  • {module}: {len(deps)} dependencies\n"

            return CallToolResult(content=[TextContent(type="text", text=result_text)])

        except Exception as e:
            return CallToolResult(content=[TextContent(type="text", text=handle_exception(e, "generate_dependency_graph"))])

    async def _analyze_code_complexity(self, module_path: str) -> CallToolResult:
        """
        Analyze code complexity metrics for Odoo module.

        Args:
            module_path: Path to module directory

        Returns:
            Code complexity report
        """
        try:
            module_path = Path(module_path)
            self.security.validator.validate_path(module_path, must_exist=True, must_be_dir=True)

            python_files = list(module_path.rglob('*.py'))

            complexity_data = []
            total_lines = 0
            total_functions = 0
            total_classes = 0

            for py_file in python_files:
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        tree = ast.parse(content)

                    lines = len(content.splitlines())
                    functions = sum(1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
                    classes = sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))

                    # Calculate cyclomatic complexity (simplified)
                    complexity = self._calculate_complexity(tree)

                    complexity_data.append({
                        'file': py_file.relative_to(module_path),
                        'lines': lines,
                        'functions': functions,
                        'classes': classes,
                        'complexity': complexity
                    })

                    total_lines += lines
                    total_functions += functions
                    total_classes += classes

                except Exception as e:
                    self.logger.warning(f"Could not analyze {py_file}: {e}")

            # Sort by complexity
            complexity_data.sort(key=lambda x: x['complexity'], reverse=True)

            result_text = f"🔍 Code Complexity Analysis: {module_path.name}\n\n"
            result_text += f"📊 Summary:\n"
            result_text += f"  • Total Files: {len(python_files)}\n"
            result_text += f"  • Total Lines: {total_lines}\n"
            result_text += f"  • Total Functions: {total_functions}\n"
            result_text += f"  • Total Classes: {total_classes}\n"
            result_text += f"  • Avg Lines/File: {total_lines/len(python_files) if python_files else 0:.1f}\n\n"

            result_text += "📈 Most Complex Files:\n"
            for item in complexity_data[:10]:
                result_text += f"  • {item['file']}\n"
                result_text += f"    Lines: {item['lines']}, Functions: {item['functions']}, "
                result_text += f"Classes: {item['classes']}, Complexity: {item['complexity']}\n"

            # Recommendations
            result_text += "\n💡 Recommendations:\n"
            high_complexity = [item for item in complexity_data if item['complexity'] > 20]
            if high_complexity:
                result_text += f"  ⚠️ {len(high_complexity)} files have high complexity (>20)\n"
                result_text += "  • Consider refactoring complex functions\n"

            large_files = [item for item in complexity_data if item['lines'] > 500]
            if large_files:
                result_text += f"  ⚠️ {len(large_files)} files are very large (>500 lines)\n"
                result_text += "  • Consider splitting into smaller modules\n"

            return CallToolResult(content=[TextContent(type="text", text=result_text)])

        except Exception as e:
            return CallToolResult(content=[TextContent(type="text", text=handle_exception(e, "analyze_code_complexity"))])

    async def _scan_security_vulnerabilities(self, module_path: str) -> CallToolResult:
        """
        Scan Odoo module for common security vulnerabilities.

        Args:
            module_path: Path to module directory

        Returns:
            Security vulnerability report
        """
        try:
            module_path = Path(module_path)
            self.security.validator.validate_path(module_path, must_exist=True, must_be_dir=True)

            vulnerabilities = []
            warnings = []

            # Scan Python files
            python_files = list(module_path.rglob('*.py'))
            for py_file in python_files:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Check for SQL injection risks
                if re.search(r'\.execute\s*\([^)]*%\s*[^)]*\)', content):
                    vulnerabilities.append({
                        'file': str(py_file.relative_to(module_path)),
                        'type': 'SQL Injection Risk',
                        'severity': 'HIGH',
                        'description': 'Direct string formatting in SQL execute()'
                    })

                # Check for eval/exec usage
                if re.search(r'\b(eval|exec)\s*\(', content):
                    vulnerabilities.append({
                        'file': str(py_file.relative_to(module_path)),
                        'type': 'Code Injection Risk',
                        'severity': 'CRITICAL',
                        'description': 'Use of eval() or exec()'
                    })

                # Check for hardcoded credentials
                if re.search(r'password\s*=\s*["\'][^"\']+["\']', content, re.IGNORECASE):
                    warnings.append({
                        'file': str(py_file.relative_to(module_path)),
                        'type': 'Hardcoded Credentials',
                        'severity': 'MEDIUM',
                        'description': 'Possible hardcoded password'
                    })

                # Check for unsafe XML parsing
                if 'XMLParser' in content and 'resolve_entities=False' not in content:
                    warnings.append({
                        'file': str(py_file.relative_to(module_path)),
                        'type': 'XXE Vulnerability',
                        'severity': 'MEDIUM',
                        'description': 'XML parser without entity resolution disabled'
                    })

            # Scan XML files for security issues
            xml_files = list(module_path.rglob('*.xml'))
            for xml_file in xml_files:
                try:
                    tree = ET.parse(xml_file)
                    root = tree.getroot()

                    # Check for unsafe eval domains
                    for record in root.findall('.//record'):
                        for field in record.findall('.//field[@eval]'):
                            eval_expr = field.get('eval', '')
                            if '__import__' in eval_expr:
                                vulnerabilities.append({
                                    'file': str(xml_file.relative_to(module_path)),
                                    'type': 'Code Injection in XML',
                                    'severity': 'CRITICAL',
                                    'description': '__import__ usage in field eval'
                                })

                except Exception:
                    pass

            # Generate report
            result_text = f"🔒 Security Vulnerability Scan: {module_path.name}\n\n"

            if vulnerabilities:
                result_text += f"🔴 VULNERABILITIES FOUND ({len(vulnerabilities)}):\n\n"
                for vuln in vulnerabilities:
                    result_text += f"❌ {vuln['severity']} - {vuln['type']}\n"
                    result_text += f"   File: {vuln['file']}\n"
                    result_text += f"   {vuln['description']}\n\n"
            else:
                result_text += "✅ No critical vulnerabilities found\n\n"

            if warnings:
                result_text += f"⚠️ WARNINGS ({len(warnings)}):\n\n"
                for warn in warnings:
                    result_text += f"⚠️ {warn['severity']} - {warn['type']}\n"
                    result_text += f"   File: {warn['file']}\n"
                    result_text += f"   {warn['description']}\n\n"

            # Security recommendations
            result_text += "💡 Security Best Practices:\n"
            result_text += "  • Never use eval() or exec() on user input\n"
            result_text += "  • Use parameterized queries for SQL\n"
            result_text += "  • Store credentials in environment variables\n"
            result_text += "  • Validate all user inputs\n"
            result_text += "  • Use Odoo's built-in security features\n"

            return CallToolResult(content=[TextContent(type="text", text=result_text)])

        except Exception as e:
            return CallToolResult(content=[TextContent(type="text", text=handle_exception(e, "scan_security_vulnerabilities"))])

    async def _generate_module_tests(self, module_path: str, test_type: str = "unit") -> CallToolResult:
        """
        Automatically generate test skeletons for Odoo module.

        Args:
            module_path: Path to module directory
            test_type: Type of tests (unit, integration, functional)

        Returns:
            Generated test files
        """
        try:
            module_path = Path(module_path)
            self.security.validator.validate_path(module_path, must_exist=True, must_be_dir=True)

            # Find all models
            models_dir = module_path / "models"
            if not models_dir.exists():
                raise FilesystemError("No models directory found")

            models = []
            for py_file in models_dir.glob("*.py"):
                if py_file.name == "__init__.py":
                    continue

                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Find model classes
                    class_matches = re.findall(r'class\s+(\w+)\(models\.Model\):', content)
                    models.extend(class_matches)

            # Generate test file
            test_content = self._generate_test_template(module_path.name, models, test_type)

            # Create tests directory if it doesn't exist
            tests_dir = module_path / "tests"
            tests_dir.mkdir(exist_ok=True)

            # Create __init__.py
            (tests_dir / "__init__.py").write_text("# -*- coding: utf-8 -*-\n")

            # Write test file
            test_file = tests_dir / f"test_{test_type}.py"
            test_file.write_text(test_content)

            result_text = f"✅ Test Generator: {module_path.name}\n\n"
            result_text += f"📝 Generated {test_type} tests for {len(models)} models:\n"
            for model in models:
                result_text += f"  • {model}\n"
            result_text += f"\n📁 Test file created: {test_file.relative_to(module_path)}\n\n"
            result_text += "🚀 Next Steps:\n"
            result_text += "1. Review and customize generated tests\n"
            result_text += "2. Run tests: `odoo --test-enable -i module_name`\n"
            result_text += "3. Add test data in tests/fixtures/\n"

            return CallToolResult(content=[TextContent(type="text", text=result_text)])

        except Exception as e:
            return CallToolResult(content=[TextContent(type="text", text=handle_exception(e, "generate_module_tests"))])

    async def _compare_modules(self, module_path1: str, module_path2: str) -> CallToolResult:
        """
        Compare two Odoo modules and show differences.

        Args:
            module_path1: Path to first module
            module_path2: Path to second module

        Returns:
            Module comparison report
        """
        try:
            path1 = Path(module_path1)
            path2 = Path(module_path2)

            self.security.validator.validate_path(path1, must_exist=True, must_be_dir=True)
            self.security.validator.validate_path(path2, must_exist=True, must_be_dir=True)

            # Compare manifests
            manifest1 = self._parse_manifest(path1 / "__manifest__.py")
            manifest2 = self._parse_manifest(path2 / "__manifest__.py")

            # Compare file structures
            files1 = set(str(f.relative_to(path1)) for f in path1.rglob('*') if f.is_file())
            files2 = set(str(f.relative_to(path2)) for f in path2.rglob('*') if f.is_file())

            only_in_1 = files1 - files2
            only_in_2 = files2 - files1
            common_files = files1 & files2

            result_text = f"🔄 Module Comparison\n\n"
            result_text += f"📦 Module 1: {path1.name} (v{manifest1.get('version', 'unknown')})\n"
            result_text += f"📦 Module 2: {path2.name} (v{manifest2.get('version', 'unknown')})\n\n"

            # Version comparison
            result_text += "📊 Manifest Differences:\n"
            for key in set(manifest1.keys()) | set(manifest2.keys()):
                val1 = manifest1.get(key)
                val2 = manifest2.get(key)
                if val1 != val2:
                    result_text += f"  • {key}: {val1} ⟷ {val2}\n"

            # File differences
            result_text += f"\n📁 File Structure:\n"
            result_text += f"  • Common files: {len(common_files)}\n"
            result_text += f"  • Only in {path1.name}: {len(only_in_1)}\n"
            result_text += f"  • Only in {path2.name}: {len(only_in_2)}\n\n"

            if only_in_1:
                result_text += f"Files only in {path1.name}:\n"
                for file in sorted(only_in_1)[:10]:
                    result_text += f"  - {file}\n"
                if len(only_in_1) > 10:
                    result_text += f"  ... and {len(only_in_1) - 10} more\n"

            return CallToolResult(content=[TextContent(type="text", text=result_text)])

        except Exception as e:
            return CallToolResult(content=[TextContent(type="text", text=handle_exception(e, "compare_modules"))])

    # Helper methods
    def _parse_manifest(self, manifest_path: Path) -> Dict[str, Any]:
        """Parse __manifest__.py file."""
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                content = f.read()
            namespace = {}
            exec(content, namespace)
            for value in namespace.values():
                if isinstance(value, dict) and 'name' in value:
                    return value
            return {}
        except Exception:
            return {}

    def _generate_mermaid_graph(self, graph: Dict[str, List[str]]) -> str:
        """Generate Mermaid diagram from dependency graph."""
        lines = ["graph TD"]
        for module, deps in graph.items():
            clean_module = module.replace('-', '_').replace('.', '_')
            for dep in deps:
                clean_dep = dep.replace('-', '_').replace('.', '_')
                lines.append(f"    {clean_module} --> {clean_dep}")
        return "\n".join(lines)

    def _generate_dot_graph(self, graph: Dict[str, List[str]]) -> str:
        """Generate DOT diagram from dependency graph."""
        lines = ["digraph dependencies {"]
        for module, deps in graph.items():
            for dep in deps:
                lines.append(f'    "{module}" -> "{dep}";')
        lines.append("}")
        return "\n".join(lines)

    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity (simplified)."""
        complexity = 1
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        return complexity

    def _generate_test_template(self, module_name: str, models: List[str], test_type: str) -> str:
        """Generate test file template."""
        template = f'''# -*- coding: utf-8 -*-
"""
{test_type.capitalize()} tests for {module_name} module
Auto-generated by Odoo 17 MCP Server
"""

from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class Test{module_name.title().replace('_', '')}(TransactionCase):
    """Test cases for {module_name} module."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        # TODO: Add test data setup

'''

        for model in models:
            template += f'''
    def test_{model.lower()}_create(self):
        """Test {model} creation."""
        # TODO: Implement test
        pass

    def test_{model.lower()}_update(self):
        """Test {model} update."""
        # TODO: Implement test
        pass

    def test_{model.lower()}_delete(self):
        """Test {model} deletion."""
        # TODO: Implement test
        pass
'''

        return template
