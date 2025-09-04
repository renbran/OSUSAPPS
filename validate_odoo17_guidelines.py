#!/usr/bin/env python3
"""
Comprehensive Odoo 17 Coding Guidelines Checker
Checks for compliance with Odoo 17 coding standards and best practices.
"""

import ast
import os
import re
import sys

class Odoo17GuidelinesChecker:
    def __init__(self):
        self.issues = []
        self.warnings = []
        
    def check_file(self, filepath):
        """Check a single Python file for Odoo 17 compliance"""
        self.issues = []
        self.warnings = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST for syntax validation
            tree = ast.parse(content)
            
            # Run all checks
            self._check_imports(content, filepath)
            self._check_model_definition(content, tree)
            self._check_field_definitions(content)
            self._check_method_definitions(content, tree)
            self._check_api_decorators(content)
            self._check_logging(content)
            self._check_string_formatting(content)
            self._check_deprecated_patterns(content)
            self._check_security_patterns(content)
            
            return True, self.issues, self.warnings
            
        except SyntaxError as e:
            return False, [f"Syntax Error: {e}"], []
        except Exception as e:
            return False, [f"Error: {e}"], []
    
    def _check_imports(self, content, filepath):
        """Check import patterns"""
        lines = content.split('\n')
        
        # Skip __init__.py and __manifest__.py files
        if os.path.basename(filepath) in ['__init__.py', '__manifest__.py']:
            return
            
        # Check for Odoo imports in model/wizard files
        is_model_file = any(x in filepath for x in ['/models/', '/wizards/', '/reports/'])
        if is_model_file and 'from odoo import' not in content and 'import odoo' not in content:
            self.issues.append("Missing Odoo imports (from odoo import models, fields, api)")
        
        # Check import order (should be: standard, third-party, odoo, local)
        odoo_import_seen = False
        local_import_seen = False
        
        for line in lines:
            line = line.strip()
            if line.startswith('from odoo'):
                odoo_import_seen = True
            elif line.startswith('from .') and odoo_import_seen:
                local_import_seen = True
            elif line.startswith('import ') and local_import_seen and not line.startswith('import odoo'):
                self.warnings.append("Import order issue: standard imports should come before local imports")
    
    def _check_model_definition(self, content, tree):
        """Check model definition patterns"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if it's an Odoo model
                for base in node.bases:
                    if isinstance(base, ast.Attribute) and isinstance(base.value, ast.Name):
                        if base.value.id == 'models' and base.attr in ['Model', 'TransientModel']:
                            self._check_model_class(node, content)
    
    def _check_model_class(self, class_node, content):
        """Check specific model class patterns"""
        class_content = ast.get_source_segment(content, class_node) or ""
        
        # Check for _name
        if '_name = ' not in class_content:
            self.issues.append(f"Model class {class_node.name} missing _name attribute")
        else:
            # Check _name format
            name_match = re.search(r"_name = ['\"]([^'\"]+)['\"]", class_content)
            if name_match:
                model_name = name_match.group(1)
                if '.' not in model_name:
                    self.issues.append(f"Model name '{model_name}' should contain dots (e.g., 'module.model')")
        
        # Check for _description
        if '_description = ' not in class_content:
            self.warnings.append(f"Model class {class_node.name} missing _description attribute")
        
        # Check for _inherit vs _name usage
        if '_inherit = ' in class_content and '_name = ' in class_content:
            self.warnings.append(f"Model {class_node.name} has both _inherit and _name (use one or the other)")
    
    def _check_field_definitions(self, content):
        """Check field definition patterns"""
        # Check for proper field definitions
        field_patterns = [
            r'fields\.(Char|Text|Html|Integer|Float|Boolean|Date|Datetime|Selection|Many2one|One2many|Many2many|Binary|Monetary)\s*\(',
        ]
        
        for pattern in field_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                # Extract the field definition
                start = match.start()
                line_start = content.rfind('\n', 0, start) + 1
                line_end = content.find('\n', start)
                if line_end == -1:
                    line_end = len(content)
                line = content[line_start:line_end]
                
                # Check for string parameter
                if 'string=' not in line and 'compute=' not in line:
                    self.warnings.append(f"Field definition missing 'string' parameter: {line.strip()}")
                
                # Check for help parameter on important fields
                if any(keyword in line.lower() for keyword in ['required=True', 'readonly=True']):
                    if 'help=' not in line:
                        self.warnings.append(f"Important field missing 'help' parameter: {line.strip()}")
    
    def _check_method_definitions(self, content, tree):
        """Check method definition patterns"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check for proper docstrings
                if not ast.get_docstring(node):
                    if not node.name.startswith('_') and node.name not in ['create', 'write', 'unlink']:
                        self.warnings.append(f"Public method '{node.name}' missing docstring")
                
                # Check for proper return statements in button methods
                if node.name.startswith('action_'):
                    method_content = ast.get_source_segment(content, node) or ""
                    if 'return {' not in method_content and 'return True' not in method_content:
                        self.warnings.append(f"Action method '{node.name}' should return action dict or True")
    
    def _check_api_decorators(self, content):
        """Check API decorator usage"""
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Check for deprecated decorators
            if '@api.one' in line or '@api.multi' in line:
                self.issues.append(f"Line {i+1}: Deprecated decorator {line} - use @api.model or remove")
            
            # Check for proper @api.depends usage
            if '@api.depends(' in line:
                next_line = lines[i+1].strip() if i+1 < len(lines) else ""
                if not next_line.startswith('def '):
                    self.warnings.append(f"Line {i+1}: @api.depends not followed by method definition")
    
    def _check_logging(self, content):
        """Check logging patterns"""
        if 'import logging' in content:
            if '_logger = logging.getLogger(__name__)' not in content:
                self.warnings.append("Using logging but missing proper logger initialization")
        
        # Check for print statements (should use logging)
        if re.search(r'\bprint\s*\(', content):
            self.warnings.append("Found print() statements - consider using logging instead")
    
    def _check_string_formatting(self, content):
        """Check string formatting patterns"""
        # Check for old-style string formatting
        if re.search(r'%[sd]', content):
            self.warnings.append("Found old-style string formatting (%) - use f-strings or .format()")
        
        # Check for proper f-string usage
        if re.search(r'\.format\(', content) and 'f"' not in content and "f'" not in content:
            self.warnings.append("Consider using f-strings for better performance")
    
    def _check_deprecated_patterns(self, content):
        """Check for deprecated patterns"""
        deprecated_patterns = [
            (r'\bstates\s*=', "Use 'invisible', 'readonly', 'required' attributes instead of 'states'"),
            (r'\battrs\s*=', "Use 'invisible', 'readonly', 'required' attributes instead of 'attrs'"),
            (r'\bmodifiers\s*=', "Use 'invisible', 'readonly', 'required' attributes instead of 'modifiers'"),
            (r'@api\.one', "Use @api.model or remove decorator"),
            (r'@api\.multi', "Use @api.model or remove decorator"),
            (r'\.sudo\(\)\.write\(', "Be careful with sudo() - ensure proper security"),
        ]
        
        for pattern, message in deprecated_patterns:
            if re.search(pattern, content):
                self.issues.append(f"Deprecated pattern found: {message}")
    
    def _check_security_patterns(self, content):
        """Check for security-related patterns"""
        # Check for SQL injection vulnerabilities
        if re.search(r'\.execute\s*\(\s*["\'].*%.*["\']', content):
            self.issues.append("Potential SQL injection vulnerability - use parameterized queries")
        
        # Check for unsafe eval usage
        if 'eval(' in content:
            self.warnings.append("Found eval() usage - ensure input is trusted")
        
        # Check for proper access control
        if 'sudo()' in content:
            self.warnings.append("Found sudo() usage - ensure proper access control")


def main():
    """Main function to check commission modules"""
    checker = Odoo17GuidelinesChecker()
    
    modules = ['commission_ax', 'commission_statement']
    total_files = 0
    total_issues = 0
    total_warnings = 0
    
    for module in modules:
        if not os.path.exists(module):
            continue
            
        print(f"\n{'='*50}")
        print(f"CHECKING MODULE: {module.upper()}")
        print(f"{'='*50}")
        
        for root, dirs, files in os.walk(module):
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    total_files += 1
                    
                    success, issues, warnings = checker.check_file(filepath)
                    
                    if success:
                        if not issues and not warnings:
                            print(f"✅ {filepath}: Fully compliant")
                        else:
                            print(f"⚠️  {filepath}:")
                            for issue in issues:
                                print(f"   ❌ ISSUE: {issue}")
                                total_issues += 1
                            for warning in warnings:
                                print(f"   ⚠️  WARNING: {warning}")
                                total_warnings += 1
                    else:
                        print(f"❌ {filepath}: SYNTAX ERROR")
                        for issue in issues:
                            print(f"   ❌ {issue}")
                            total_issues += 1
    
    print(f"\n{'='*50}")
    print(f"SUMMARY")
    print(f"{'='*50}")
    print(f"Total files checked: {total_files}")
    print(f"Total issues: {total_issues}")
    print(f"Total warnings: {total_warnings}")
    
    if total_issues == 0 and total_warnings == 0:
        print("🎉 All files are fully compliant with Odoo 17 guidelines!")
    elif total_issues == 0:
        print("✅ No critical issues found. Only warnings present.")
    else:
        print("❌ Critical issues found that should be addressed.")
    
    return total_issues

if __name__ == "__main__":
    sys.exit(main())
