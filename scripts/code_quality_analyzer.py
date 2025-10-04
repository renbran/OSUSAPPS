#!/usr/bin/env python3
"""
OSUSAPPS Odoo 17 - Automated Code Quality & Security Assessment Tool

This comprehensive script analyzes Odoo modules for:
- Code quality and best practices
- Security vulnerabilities
- Performance issues
- OSUSAPPS-specific pattern compliance
- Module structure validation
"""

import os
import sys
import json
import re
import ast
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict
import argparse
from datetime import datetime

@dataclass
class CodeIssue:
    """Represents a code quality or security issue"""
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    category: str  # SECURITY, PERFORMANCE, STRUCTURE, STYLE, etc.
    file_path: str
    line_number: int
    issue_type: str
    description: str
    recommendation: str
    osusapps_pattern: str = ""

@dataclass
class ModuleAnalysis:
    """Complete analysis result for a module"""
    module_name: str
    module_path: str
    structure_score: float
    security_score: float
    performance_score: float
    style_score: float
    overall_score: float
    issues: List[CodeIssue]
    dependencies: List[str]
    missing_files: List[str]
    
class OdooCodeAnalyzer:
    """Main analyzer class for Odoo 17 modules"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.issues: List[CodeIssue] = []
        self.analyzed_modules: List[ModuleAnalysis] = []
        
        # OSUSAPPS-specific patterns
        self.required_structure = {
            '__manifest__.py': True,
            'models/': False,
            'views/': False,
            'security/': False,
            'data/': False,
            'static/': False,
            'reports/': False,
            'wizards/': False,
            'tests/': False,
        }
        
        # Security patterns to check
        self.security_patterns = [
            r'eval\(',
            r'exec\(',
            r'os\.system',
            r'subprocess\.call',
            r'shell=True',
            r'dangerous_eval',
            r'safe_eval',
        ]
        
        # Performance anti-patterns
        self.performance_patterns = [
            r'\.search\(\[\]\)',  # Search all records
            r'for.*in.*\.search\(',  # Loop with search
            r'\.browse\(.*\)\..*\.browse\(',  # Nested browse
        ]
        
    def analyze_module(self, module_path: Path) -> ModuleAnalysis:
        """Analyze a single Odoo module"""
        module_name = module_path.name
        print(f"🔍 Analyzing module: {module_name}")
        
        # Reset issues for this module
        module_issues = []
        
        # Check module structure
        structure_score, missing_files = self._check_module_structure(module_path)
        
        # Analyze Python files
        security_score, performance_score = self._analyze_python_files(module_path, module_issues)
        
        # Analyze XML files
        view_score = self._analyze_xml_files(module_path, module_issues)
        
        # Check manifest
        manifest_score, dependencies = self._analyze_manifest(module_path, module_issues)
        
        # Check security files
        security_file_score = self._check_security_files(module_path, module_issues)
        
        # Calculate overall scores
        style_score = (view_score + manifest_score) / 2
        security_score = (security_score + security_file_score) / 2
        overall_score = (structure_score + security_score + performance_score + style_score) / 4
        
        analysis = ModuleAnalysis(
            module_name=module_name,
            module_path=str(module_path),
            structure_score=structure_score,
            security_score=security_score,
            performance_score=performance_score,
            style_score=style_score,
            overall_score=overall_score,
            issues=module_issues,
            dependencies=dependencies,
            missing_files=missing_files
        )
        
        self.analyzed_modules.append(analysis)
        return analysis
    
    def _check_module_structure(self, module_path: Path) -> Tuple[float, List[str]]:
        """Check if module follows OSUSAPPS structure standards"""
        score = 100.0
        missing_files = []
        
        for item, required in self.required_structure.items():
            item_path = module_path / item
            if not item_path.exists():
                if required:
                    score -= 20.0
                    missing_files.append(item)
                    self.issues.append(CodeIssue(
                        severity="HIGH",
                        category="STRUCTURE",
                        file_path=str(module_path),
                        line_number=0,
                        issue_type="MISSING_REQUIRED_FILE",
                        description=f"Missing required file/directory: {item}",
                        recommendation=f"Create {item} following OSUSAPPS patterns",
                        osusapps_pattern="All modules must have __manifest__.py"
                    ))
                else:
                    score -= 5.0
                    missing_files.append(item)
        
        return max(score, 0.0), missing_files
    
    def _analyze_python_files(self, module_path: Path, issues: List[CodeIssue]) -> Tuple[float, float]:
        """Analyze Python files for security and performance issues"""
        security_score = 100.0
        performance_score = 100.0
        
        python_files = list(module_path.rglob("*.py"))
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Security analysis
                for pattern in self.security_patterns:
                    matches = re.finditer(pattern, content, re.MULTILINE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        security_score -= 10.0
                        issues.append(CodeIssue(
                            severity="HIGH",
                            category="SECURITY",
                            file_path=str(py_file),
                            line_number=line_num,
                            issue_type="DANGEROUS_FUNCTION",
                            description=f"Dangerous function usage: {match.group()}",
                            recommendation="Use safe alternatives or proper validation",
                            osusapps_pattern="Follow security patterns from payment_account_enhanced"
                        ))
                
                # Performance analysis
                for pattern in self.performance_patterns:
                    matches = re.finditer(pattern, content, re.MULTILINE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        performance_score -= 5.0
                        issues.append(CodeIssue(
                            severity="MEDIUM",
                            category="PERFORMANCE",
                            file_path=str(py_file),
                            line_number=line_num,
                            issue_type="PERFORMANCE_ISSUE",
                            description=f"Performance anti-pattern: {match.group()}",
                            recommendation="Optimize query or use proper search domains",
                            osusapps_pattern="Use efficient ORM patterns as in custom_sales module"
                        ))
                
                # AST analysis for deeper inspection
                try:
                    tree = ast.parse(content)
                    self._analyze_ast(tree, py_file, issues)
                except SyntaxError as e:
                    issues.append(CodeIssue(
                        severity="CRITICAL",
                        category="SYNTAX",
                        file_path=str(py_file),
                        line_number=e.lineno or 0,
                        issue_type="SYNTAX_ERROR",
                        description=f"Syntax error: {e.msg}",
                        recommendation="Fix syntax error",
                        osusapps_pattern=""
                    ))
                    
            except Exception as e:
                print(f"⚠️  Error analyzing {py_file}: {e}")
        
        return max(security_score, 0.0), max(performance_score, 0.0)
    
    def _analyze_ast(self, tree: ast.AST, file_path: Path, issues: List[CodeIssue]):
        """Deep AST analysis for code quality"""
        class CodeVisitor(ast.NodeVisitor):
            def __init__(self, file_path: Path, issues: List[CodeIssue]):
                self.file_path = file_path
                self.issues = issues
            
            def visit_FunctionDef(self, node):
                # Check for overly complex functions
                complexity = self._calculate_complexity(node)
                if complexity > 10:
                    self.issues.append(CodeIssue(
                        severity="MEDIUM",
                        category="COMPLEXITY",
                        file_path=str(self.file_path),
                        line_number=node.lineno,
                        issue_type="HIGH_COMPLEXITY",
                        description=f"Function '{node.name}' has high complexity ({complexity})",
                        recommendation="Break down into smaller functions",
                        osusapps_pattern="Keep functions simple as in commission_ax module"
                    ))
                
                # Check for missing docstrings in public methods
                if not node.name.startswith('_') and not ast.get_docstring(node):
                    self.issues.append(CodeIssue(
                        severity="LOW",
                        category="DOCUMENTATION",
                        file_path=str(self.file_path),
                        line_number=node.lineno,
                        issue_type="MISSING_DOCSTRING",
                        description=f"Public method '{node.name}' missing docstring",
                        recommendation="Add comprehensive docstring",
                        osusapps_pattern="Follow docstring patterns from existing modules"
                    ))
                
                self.generic_visit(node)
            
            def visit_ClassDef(self, node):
                # Check for proper Odoo model inheritance
                if any(base.attr == 'Model' for base in node.bases if isinstance(base, ast.Attribute)):
                    # Check for _name attribute
                    has_name = any(
                        isinstance(stmt, ast.Assign) and 
                        any(target.id == '_name' for target in stmt.targets if isinstance(target, ast.Name))
                        for stmt in node.body if isinstance(stmt, ast.Assign)
                    )
                    
                    if not has_name:
                        self.issues.append(CodeIssue(
                            severity="HIGH",
                            category="STRUCTURE",
                            file_path=str(self.file_path),
                            line_number=node.lineno,
                            issue_type="MISSING_MODEL_NAME",
                            description=f"Model class '{node.name}' missing _name attribute",
                            recommendation="Add _name = 'module.model' attribute",
                            osusapps_pattern="Follow model naming from payment_account_enhanced"
                        ))
                
                self.generic_visit(node)
            
            def _calculate_complexity(self, node):
                """Calculate cyclomatic complexity"""
                complexity = 1
                for child in ast.walk(node):
                    if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                        complexity += 1
                    elif isinstance(child, ast.BoolOp):
                        complexity += len(child.values) - 1
                return complexity
        
        visitor = CodeVisitor(file_path, issues)
        visitor.visit(tree)
    
    def _analyze_xml_files(self, module_path: Path, issues: List[CodeIssue]) -> float:
        """Analyze XML files for view and data issues"""
        score = 100.0
        xml_files = list(module_path.rglob("*.xml"))
        
        for xml_file in xml_files:
            try:
                tree = ET.parse(xml_file)
                root = tree.getroot()
                
                # Check for proper XML structure
                if root.tag != 'odoo':
                    score -= 5.0
                    issues.append(CodeIssue(
                        severity="MEDIUM",
                        category="STRUCTURE",
                        file_path=str(xml_file),
                        line_number=1,
                        issue_type="INVALID_XML_ROOT",
                        description="XML file should have <odoo> as root element",
                        recommendation="Wrap content in <odoo> tags",
                        osusapps_pattern="Follow XML structure from existing views"
                    ))
                
                # Check for missing external IDs
                for record in root.findall(".//record"):
                    if not record.get('id'):
                        score -= 2.0
                        issues.append(CodeIssue(
                            severity="LOW",
                            category="STRUCTURE",
                            file_path=str(xml_file),
                            line_number=1,
                            issue_type="MISSING_EXTERNAL_ID",
                            description="Record missing external ID",
                            recommendation="Add unique id attribute to record",
                            osusapps_pattern="Use descriptive IDs following module_name.record_name pattern"
                        ))
                
            except ET.ParseError as e:
                score -= 20.0
                issues.append(CodeIssue(
                    severity="CRITICAL",
                    category="SYNTAX",
                    file_path=str(xml_file),
                    line_number=e.position[0] if hasattr(e, 'position') else 0,
                    issue_type="XML_PARSE_ERROR",
                    description=f"XML parsing error: {e}",
                    recommendation="Fix XML syntax",
                    osusapps_pattern=""
                ))
            except Exception as e:
                print(f"⚠️  Error analyzing {xml_file}: {e}")
        
        return max(score, 0.0)
    
    def _analyze_manifest(self, module_path: Path, issues: List[CodeIssue]) -> Tuple[float, List[str]]:
        """Analyze __manifest__.py file"""
        score = 100.0
        dependencies = []
        
        manifest_path = module_path / '__manifest__.py'
        if not manifest_path.exists():
            return 0.0, dependencies
        
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse manifest as Python dict
            manifest_dict = ast.literal_eval(content)
            
            # Check required fields
            required_fields = ['name', 'version', 'author', 'category', 'depends']
            for field in required_fields:
                if field not in manifest_dict:
                    score -= 10.0
                    issues.append(CodeIssue(
                        severity="MEDIUM",
                        category="STRUCTURE",
                        file_path=str(manifest_path),
                        line_number=0,
                        issue_type="MISSING_MANIFEST_FIELD",
                        description=f"Missing required field: {field}",
                        recommendation=f"Add '{field}' field to manifest",
                        osusapps_pattern="Follow manifest structure from successful modules"
                    ))
            
            # Extract dependencies
            dependencies = manifest_dict.get('depends', [])
            
            # Check for proper version format
            version = manifest_dict.get('version', '')
            if not re.match(r'^\d+\.\d+\.\d+\.\d+\.\d+$', version):
                score -= 5.0
                issues.append(CodeIssue(
                    severity="LOW",
                    category="STRUCTURE",
                    file_path=str(manifest_path),
                    line_number=0,
                    issue_type="INVALID_VERSION_FORMAT",
                    description="Version should follow x.y.z.w.v format",
                    recommendation="Use proper version format like 17.0.1.0.0",
                    osusapps_pattern="Follow versioning from existing modules"
                ))
            
        except Exception as e:
            score = 0.0
            issues.append(CodeIssue(
                severity="CRITICAL",
                category="SYNTAX",
                file_path=str(manifest_path),
                line_number=0,
                issue_type="MANIFEST_PARSE_ERROR",
                description=f"Error parsing manifest: {e}",
                recommendation="Fix manifest syntax",
                osusapps_pattern=""
            ))
        
        return max(score, 0.0), dependencies
    
    def _check_security_files(self, module_path: Path, issues: List[CodeIssue]) -> float:
        """Check security-related files"""
        score = 100.0
        
        security_dir = module_path / 'security'
        if not security_dir.exists():
            score -= 30.0
            issues.append(CodeIssue(
                severity="HIGH",
                category="SECURITY",
                file_path=str(module_path),
                line_number=0,
                issue_type="MISSING_SECURITY_DIR",
                description="Missing security directory",
                recommendation="Create security/ directory with access rights",
                osusapps_pattern="All modules should have security definitions"
            ))
            return max(score, 0.0)
        
        # Check for access rights file
        access_file = security_dir / 'ir.model.access.csv'
        if not access_file.exists():
            score -= 20.0
            issues.append(CodeIssue(
                severity="HIGH",
                category="SECURITY",
                file_path=str(security_dir),
                line_number=0,
                issue_type="MISSING_ACCESS_RIGHTS",
                description="Missing ir.model.access.csv file",
                recommendation="Create access rights file for all models",
                osusapps_pattern="Follow access patterns from payment_account_enhanced"
            ))
        
        return max(score, 0.0)
    
    def generate_report(self, output_file: Optional[str] = None) -> Dict[str, Any]:
        """Generate comprehensive analysis report"""
        
        # Calculate overall statistics
        total_issues = sum(len(module.issues) for module in self.analyzed_modules)
        avg_score = sum(module.overall_score for module in self.analyzed_modules) / len(self.analyzed_modules) if self.analyzed_modules else 0
        
        # Group issues by severity
        severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        category_counts = {}
        
        for module in self.analyzed_modules:
            for issue in module.issues:
                severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1
                category_counts[issue.category] = category_counts.get(issue.category, 0) + 1
        
        report = {
            "analysis_date": datetime.now().isoformat(),
            "workspace_path": str(self.workspace_path),
            "summary": {
                "total_modules": len(self.analyzed_modules),
                "total_issues": total_issues,
                "average_score": round(avg_score, 2),
                "severity_breakdown": severity_counts,
                "category_breakdown": category_counts
            },
            "modules": [asdict(module) for module in self.analyzed_modules],
            "recommendations": self._generate_recommendations()
        }
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"📊 Report saved to: {output_file}")
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate top-level recommendations based on analysis"""
        recommendations = []
        
        # Analyze common issues
        all_issues = []
        for module in self.analyzed_modules:
            all_issues.extend(module.issues)
        
        # Group by issue type
        issue_types = {}
        for issue in all_issues:
            issue_types[issue.issue_type] = issue_types.get(issue.issue_type, 0) + 1
        
        # Generate recommendations for most common issues
        sorted_issues = sorted(issue_types.items(), key=lambda x: x[1], reverse=True)
        
        for issue_type, count in sorted_issues[:5]:
            if issue_type == "MISSING_SECURITY_DIR":
                recommendations.append(f"🔒 {count} modules missing security definitions - Implement comprehensive access control")
            elif issue_type == "PERFORMANCE_ISSUE":
                recommendations.append(f"⚡ {count} performance issues found - Optimize ORM queries and database operations")
            elif issue_type == "MISSING_DOCSTRING":
                recommendations.append(f"📝 {count} functions missing documentation - Add comprehensive docstrings")
            elif issue_type == "HIGH_COMPLEXITY":
                recommendations.append(f"🔧 {count} overly complex functions - Refactor for better maintainability")
            else:
                recommendations.append(f"⚠️  {count} instances of {issue_type.replace('_', ' ').lower()}")
        
        # Add general recommendations
        if len(self.analyzed_modules) > 0:
            avg_score = sum(module.overall_score for module in self.analyzed_modules) / len(self.analyzed_modules)
            if avg_score < 70:
                recommendations.append("🚨 Overall code quality below acceptable threshold - Prioritize critical issues")
            elif avg_score < 85:
                recommendations.append("📈 Good progress, focus on security and performance optimizations")
            else:
                recommendations.append("✅ Excellent code quality - Maintain current standards")
        
        return recommendations
    
    def print_summary(self):
        """Print analysis summary to console"""
        print("\n" + "="*80)
        print("🔍 OSUSAPPS ODOO 17 - CODE QUALITY ANALYSIS SUMMARY")
        print("="*80)
        
        if not self.analyzed_modules:
            print("❌ No modules analyzed")
            return
        
        # Overall statistics
        total_issues = sum(len(module.issues) for module in self.analyzed_modules)
        avg_score = sum(module.overall_score for module in self.analyzed_modules) / len(self.analyzed_modules)
        
        print(f"📊 Analyzed Modules: {len(self.analyzed_modules)}")
        print(f"📊 Total Issues Found: {total_issues}")
        print(f"📊 Average Quality Score: {avg_score:.1f}/100")
        
        # Severity breakdown
        severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for module in self.analyzed_modules:
            for issue in module.issues:
                severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1
        
        print(f"\n🚨 Issue Breakdown:")
        print(f"   CRITICAL: {severity_counts['CRITICAL']}")
        print(f"   HIGH:     {severity_counts['HIGH']}")
        print(f"   MEDIUM:   {severity_counts['MEDIUM']}")
        print(f"   LOW:      {severity_counts['LOW']}")
        
        # Top modules by score
        print(f"\n🏆 Top Performing Modules:")
        sorted_modules = sorted(self.analyzed_modules, key=lambda x: x.overall_score, reverse=True)
        for i, module in enumerate(sorted_modules[:5], 1):
            print(f"   {i}. {module.module_name}: {module.overall_score:.1f}/100")
        
        # Modules needing attention
        print(f"\n⚠️  Modules Needing Attention:")
        attention_modules = [m for m in sorted_modules if m.overall_score < 70]
        for module in attention_modules[:5]:
            critical_issues = len([i for i in module.issues if i.severity == "CRITICAL"])
            high_issues = len([i for i in module.issues if i.severity == "HIGH"])
            print(f"   • {module.module_name}: {module.overall_score:.1f}/100 ({critical_issues} critical, {high_issues} high)")
        
        print("="*80)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="OSUSAPPS Odoo 17 Code Quality Analyzer")
    parser.add_argument("workspace", help="Path to OSUSAPPS workspace")
    parser.add_argument("--module", help="Analyze specific module only")
    parser.add_argument("--output", help="Output JSON report file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.workspace):
        print(f"❌ Workspace not found: {args.workspace}")
        sys.exit(1)
    
    analyzer = OdooCodeAnalyzer(args.workspace)
    
    if args.module:
        # Analyze specific module
        module_path = Path(args.workspace) / args.module
        if not module_path.exists():
            print(f"❌ Module not found: {args.module}")
            sys.exit(1)
        analyzer.analyze_module(module_path)
    else:
        # Analyze all modules
        workspace_path = Path(args.workspace)
        for item in workspace_path.iterdir():
            if item.is_dir() and not item.name.startswith('.') and (item / '__manifest__.py').exists():
                try:
                    analyzer.analyze_module(item)
                except Exception as e:
                    if args.verbose:
                        print(f"⚠️  Error analyzing {item.name}: {e}")
    
    # Generate and display results
    analyzer.print_summary()
    
    # Generate detailed report
    output_file = args.output or f"code_quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    analyzer.generate_report(output_file)
    
    print(f"\n📄 Detailed report generated: {output_file}")
    print("💡 Use this report to prioritize code improvements and security fixes")

if __name__ == "__main__":
    main()