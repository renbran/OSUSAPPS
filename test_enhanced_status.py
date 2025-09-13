#!/usr/bin/env python3
"""
Comprehensive Test Suite for Enhanced Status Module
Tests the module structure, syntax, and logic without requiring Docker
"""

import os
import sys
import ast
import xml.etree.ElementTree as ET
from pathlib import Path

class EnhancedStatusTester:
    def __init__(self, module_path):
        self.module_path = Path(module_path)
        self.errors = []
        self.warnings = []
        self.tests_passed = 0
        self.tests_failed = 0
        
    def log_error(self, test_name, message):
        self.errors.append(f"❌ {test_name}: {message}")
        self.tests_failed += 1
        
    def log_warning(self, test_name, message):
        self.warnings.append(f"⚠️ {test_name}: {message}")
        
    def log_success(self, test_name, message=""):
        print(f"✅ {test_name}: {message}")
        self.tests_passed += 1
        
    def test_module_structure(self):
        """Test 1: Verify module has required files and structure"""
        required_files = [
            '__manifest__.py',
            '__init__.py',
            'models/__init__.py',
            'models/sale_order_simple.py',
            'models/commission_report.py',
            'views/sale_order_simple_view.xml',
            'views/commission_menu.xml',
            'security/security.xml',
            'security/ir.model.access.csv',
            'reports/commission_report_template.xml'
        ]
        
        missing_files = []
        for file_path in required_files:
            full_path = self.module_path / file_path
            if not full_path.exists():
                missing_files.append(file_path)
                
        if missing_files:
            self.log_error("Module Structure", f"Missing files: {missing_files}")
        else:
            self.log_success("Module Structure", "All required files present")
            
    def test_manifest_syntax(self):
        """Test 2: Verify __manifest__.py syntax and required fields"""
        manifest_path = self.module_path / '__manifest__.py'
        
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse as Python
            ast.parse(content)
            
            # Simple check for required fields in content
            required_fields = ['name', 'version', 'depends', 'data']
            manifest_content = content.lower()
            
            missing_fields = []
            for field in required_fields:
                if f"'{field}'" not in manifest_content:
                    missing_fields.append(field)
            
            if missing_fields:
                self.log_error("Manifest Content", f"Missing required fields: {missing_fields}")
            else:
                # Extract version for display
                if "'version':" in content:
                    start = content.find("'version':") + 10
                    end = content.find(",", start)
                    version_line = content[start:end].strip().strip("'\"")
                    self.log_success("Manifest Syntax", f"Valid manifest with version {version_line}")
                else:
                    self.log_success("Manifest Syntax", "Valid manifest structure")
                
        except Exception as e:
            self.log_error("Manifest Syntax", f"Parse error: {str(e)}")
            
    def test_python_models_syntax(self):
        """Test 3: Verify Python model files syntax"""
        python_files = [
            'models/sale_order_simple.py',
            'models/commission_report.py',
            'models/__init__.py',
            '__init__.py'
        ]
        
        for file_path in python_files:
            full_path = self.module_path / file_path
            if not full_path.exists():
                continue
                
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Parse Python syntax
                ast.parse(content)
                self.log_success(f"Python Syntax", f"{file_path} - Valid")
                
            except Exception as e:
                self.log_error(f"Python Syntax", f"{file_path} - {str(e)}")
                
    def test_xml_views_syntax(self):
        """Test 4: Verify XML view files syntax"""
        xml_files = [
            'views/sale_order_simple_view.xml',
            'views/commission_menu.xml',
            'security/security.xml',
            'reports/commission_report_template.xml'
        ]
        
        for file_path in xml_files:
            full_path = self.module_path / file_path
            if not full_path.exists():
                continue
                
            try:
                ET.parse(full_path)
                self.log_success(f"XML Syntax", f"{file_path} - Valid")
                
            except Exception as e:
                self.log_error(f"XML Syntax", f"{file_path} - {str(e)}")
                
    def test_model_fields_and_methods(self):
        """Test 5: Verify model has required fields and methods"""
        model_path = self.module_path / 'models/sale_order_simple.py'
        
        try:
            with open(model_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            tree = ast.parse(content)
            
            # Find the SaleOrder class
            sale_order_class = None
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == 'SaleOrder':
                    sale_order_class = node
                    break
                    
            if not sale_order_class:
                self.log_error("Model Structure", "SaleOrder class not found")
                return
                
            # Check for required fields
            required_fields = [
                'custom_state', 'is_locked', 'can_unlock', 'has_due', 'is_warning'
            ]
            
            # Check for required methods
            required_methods = [
                'action_move_to_documentation',
                'action_move_to_calculation', 
                'action_move_to_approved',
                'action_complete_order',
                'action_unlock_order',
                '_compute_is_locked',
                '_compute_can_unlock'
            ]
            
            found_fields = []
            found_methods = []
            
            for node in sale_order_class.body:
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            found_fields.append(target.id)
                elif isinstance(node, ast.FunctionDef):
                    found_methods.append(node.name)
                    
            missing_fields = [f for f in required_fields if f not in found_fields]
            missing_methods = [m for m in required_methods if m not in found_methods]
            
            if missing_fields:
                self.log_error("Model Fields", f"Missing fields: {missing_fields}")
            else:
                self.log_success("Model Fields", f"All required fields present: {required_fields}")
                
            if missing_methods:
                self.log_error("Model Methods", f"Missing methods: {missing_methods}")
            else:
                self.log_success("Model Methods", f"All required methods present")
                
        except Exception as e:
            self.log_error("Model Analysis", f"Failed to analyze model: {str(e)}")
            
    def test_custom_state_field_definition(self):
        """Test 6: Verify custom_state field has correct selection values"""
        model_path = self.module_path / 'models/sale_order_simple.py'
        
        try:
            with open(model_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Look for custom_state field definition
            if 'custom_state = fields.Selection([' in content:
                # Extract the selection values
                start = content.find('custom_state = fields.Selection([')
                end = content.find(']', start) + 1
                field_def = content[start:end]
                
                expected_states = ['draft', 'documentation', 'calculation', 'approved', 'completed']
                
                missing_states = []
                for state in expected_states:
                    if f"('{state}'" not in field_def:
                        missing_states.append(state)
                        
                if missing_states:
                    self.log_error("Custom State Field", f"Missing states: {missing_states}")
                else:
                    self.log_success("Custom State Field", "All 5 workflow states present")
            else:
                self.log_error("Custom State Field", "custom_state field definition not found")
                
        except Exception as e:
            self.log_error("Custom State Field", f"Failed to analyze: {str(e)}")
            
    def test_view_structure(self):
        """Test 7: Verify view has required elements"""
        view_path = self.module_path / 'views/sale_order_simple_view.xml'
        
        try:
            tree = ET.parse(view_path)
            root = tree.getroot()
            
            # Check for statusbar
            statusbar_found = False
            buttons_found = []
            
            for elem in root.iter():
                if elem.tag == 'field' and elem.get('name') == 'custom_state':
                    if elem.get('widget') == 'statusbar':
                        statusbar_found = True
                        
                if elem.tag == 'button':
                    button_name = elem.get('name')
                    if button_name:
                        buttons_found.append(button_name)
                        
            if statusbar_found:
                self.log_success("View Structure", "Custom state statusbar found")
            else:
                self.log_warning("View Structure", "Custom state statusbar not found")
                
            required_buttons = [
                'action_move_to_documentation',
                'action_move_to_calculation',
                'action_move_to_approved', 
                'action_complete_order',
                'action_unlock_order'
            ]
            
            missing_buttons = [btn for btn in required_buttons if btn not in buttons_found]
            
            if missing_buttons:
                self.log_error("View Buttons", f"Missing buttons: {missing_buttons}")
            else:
                self.log_success("View Buttons", "All workflow buttons present")
                
        except Exception as e:
            self.log_error("View Structure", f"Failed to analyze view: {str(e)}")
            
    def test_security_configuration(self):
        """Test 8: Verify security configuration"""
        security_path = self.module_path / 'security/security.xml'
        access_path = self.module_path / 'security/ir.model.access.csv'
        
        # Test security.xml
        try:
            tree = ET.parse(security_path)
            root = tree.getroot()
            
            groups_found = []
            rules_found = []
            
            for record in root.findall('.//record'):
                if record.get('model') == 'res.groups':
                    groups_found.append(record.get('id'))
                elif record.get('model') == 'ir.rule':
                    rules_found.append(record.get('id'))
                    
            if groups_found:
                self.log_success("Security Groups", f"Found groups: {groups_found}")
            else:
                self.log_warning("Security Groups", "No security groups found")
                
            if rules_found:
                self.log_success("Security Rules", f"Found rules: {rules_found}")
            else:
                self.log_warning("Security Rules", "No security rules found")
                
        except Exception as e:
            self.log_error("Security XML", f"Failed to analyze: {str(e)}")
            
        # Test access CSV
        if access_path.exists():
            self.log_success("Access Rights", "ir.model.access.csv file exists")
        else:
            self.log_warning("Access Rights", "ir.model.access.csv file missing")
            
    def test_write_method_protection(self):
        """Test 9: Verify write method override for field protection"""
        model_path = self.module_path / 'models/sale_order_simple.py'
        
        try:
            with open(model_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if 'def write(self, vals):' in content:
                if '_get_readonly_fields_when_locked' in content:
                    self.log_success("Write Protection", "Write method override with field protection found")
                else:
                    self.log_warning("Write Protection", "Write method found but field protection unclear")
            else:
                self.log_warning("Write Protection", "Write method override not found")
                
        except Exception as e:
            self.log_error("Write Protection", f"Failed to analyze: {str(e)}")
            
    def run_all_tests(self):
        """Run all tests and generate report"""
        print("🚀 Starting Enhanced Status Module Comprehensive Test Suite")
        print("=" * 60)
        
        self.test_module_structure()
        self.test_manifest_syntax()
        self.test_python_models_syntax()
        self.test_xml_views_syntax()
        self.test_model_fields_and_methods()
        self.test_custom_state_field_definition()
        self.test_view_structure()
        self.test_security_configuration()
        self.test_write_method_protection()
        
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        print(f"✅ Tests Passed: {self.tests_passed}")
        print(f"❌ Tests Failed: {self.tests_failed}")
        print(f"⚠️ Warnings: {len(self.warnings)}")
        
        if self.errors:
            print("\n🔴 ERRORS:")
            for error in self.errors:
                print(f"  {error}")
                
        if self.warnings:
            print("\n🟡 WARNINGS:")
            for warning in self.warnings:
                print(f"  {warning}")
                
        if self.tests_failed == 0:
            print("\n🎉 ALL TESTS PASSED! Module is ready for deployment.")
        else:
            print(f"\n⚠️ {self.tests_failed} test(s) failed. Please review errors above.")
            
        return self.tests_failed == 0

if __name__ == "__main__":
    module_path = Path(__file__).parent / "enhanced_status"
    tester = EnhancedStatusTester(module_path)
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
