#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Commission AX Simple Installation Validator
===========================================

Simple validation script without Unicode characters for Windows compatibility.
"""

import os
import ast
import xml.etree.ElementTree as ET
from pathlib import Path

class SimpleValidator:
    def __init__(self):
        self.module_path = Path(__file__).parent
        self.errors = 0
        self.passed = 0

    def test_file_exists(self, filepath, description):
        """Test if a file exists"""
        full_path = self.module_path / filepath
        if full_path.exists():
            print(f"PASS: {description}")
            self.passed += 1
            return True
        else:
            print(f"FAIL: {description} - {filepath} not found")
            self.errors += 1
            return False

    def test_python_syntax(self, filepath):
        """Test Python file syntax"""
        full_path = self.module_path / filepath
        if not full_path.exists():
            print(f"SKIP: {filepath} - file not found")
            return False
            
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                source = f.read()
            ast.parse(source)
            print(f"PASS: Python syntax valid - {filepath}")
            self.passed += 1
            return True
        except SyntaxError as e:
            print(f"FAIL: Python syntax error in {filepath} - {e}")
            self.errors += 1
            return False

    def test_xml_syntax(self, filepath):
        """Test XML file syntax"""
        full_path = self.module_path / filepath
        if not full_path.exists():
            print(f"SKIP: {filepath} - file not found")
            return False
            
        try:
            ET.parse(str(full_path))
            print(f"PASS: XML syntax valid - {filepath}")
            self.passed += 1
            return True
        except ET.ParseError as e:
            print(f"FAIL: XML syntax error in {filepath} - {e}")
            self.errors += 1
            return False

    def test_client_order_ref_implementation(self):
        """Test client_order_ref implementation"""
        print("\nTesting client_order_ref implementation...")
        
        # Test wizard
        wizard_path = self.module_path / 'wizards/commission_partner_statement_wizard.py'
        if wizard_path.exists():
            with open(wizard_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'client_order_ref' in content:
                print("PASS: Wizard contains client_order_ref")
                self.passed += 1
            else:
                print("FAIL: Wizard missing client_order_ref")
                self.errors += 1
                
            if "'project_name':" not in content:
                print("PASS: Wizard removed project_name references")
                self.passed += 1
            else:
                print("WARN: Wizard still has project_name references")
        
        # Test template
        template_path = self.module_path / 'reports/commission_partner_statement_template.xml'
        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'client_order_ref' in content:
                print("PASS: Template contains client_order_ref")
                self.passed += 1
            else:
                print("FAIL: Template missing client_order_ref")
                self.errors += 1
                
            if 'colspan="7"' in content:
                print("PASS: Template has correct column count (7)")
                self.passed += 1
            elif 'colspan="8"' in content:
                print("WARN: Template still has old column count (8)")
                
            if 'Project</th>' not in content and 'Unit</th>' not in content:
                print("PASS: Template removed Project and Unit columns")
                self.passed += 1
            else:
                print("WARN: Template still has Project or Unit columns")

    def run_validation(self):
        """Run all validation tests"""
        print("Commission AX Installation Validation")
        print("=====================================")
        
        print("\n1. Testing required files...")
        
        files_to_test = [
            ('__init__.py', 'Main module init'),
            ('__manifest__.py', 'Module manifest'),
            ('wizards/__init__.py', 'Wizards init'),
            ('wizards/commission_partner_statement_wizard.py', 'Partner statement wizard'),
            ('reports/__init__.py', 'Reports init'),
            ('reports/commission_partner_statement_report.py', 'Report model'),
            ('reports/commission_partner_statement_template.xml', 'Report template'),
            ('reports/commission_partner_statement_reports.xml', 'Report definition'),
            ('views/commission_partner_statement_wizard_views.xml', 'Wizard views')
        ]
        
        for filepath, description in files_to_test:
            self.test_file_exists(filepath, description)
            
        print("\n2. Testing Python syntax...")
        
        python_files = [
            '__init__.py',
            'wizards/__init__.py',
            'wizards/commission_partner_statement_wizard.py',
            'reports/__init__.py',
            'reports/commission_partner_statement_report.py'
        ]
        
        for filepath in python_files:
            self.test_python_syntax(filepath)
            
        print("\n3. Testing XML syntax...")
        
        xml_files = [
            'reports/commission_partner_statement_template.xml',
            'reports/commission_partner_statement_reports.xml',
            'views/commission_partner_statement_wizard_views.xml'
        ]
        
        for filepath in xml_files:
            self.test_xml_syntax(filepath)
            
        print("\n4. Testing client_order_ref implementation...")
        self.test_client_order_ref_implementation()
        
        # Summary
        print("\n" + "="*50)
        print("VALIDATION SUMMARY")
        print("="*50)
        print(f"Tests passed: {self.passed}")
        print(f"Tests failed: {self.errors}")
        
        if self.errors == 0:
            print("\nSTATUS: READY FOR INSTALLATION")
            print("\nInstallation Instructions:")
            print("1. Restart Odoo server")  
            print("2. Update commission_ax module")
            print("3. Test commission partner statement report")
            print("4. Verify Client Order Ref column appears")
            return True
        else:
            print(f"\nSTATUS: NEEDS FIXES ({self.errors} issues)")
            return False

def main():
    validator = SimpleValidator()
    success = validator.run_validation()
    return 0 if success else 1

if __name__ == '__main__':
    import sys
    sys.exit(main())