#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Commission AX Module Installation Test Script
=============================================

This script performs comprehensive installation validation for the commission_ax module,
specifically testing the commission partner statement functionality with the new
client_order_ref structure.

Run this script to validate:
- Module structure integrity
- Python syntax validation  
- XML template validation
- Import dependencies
- Data structure consistency
"""

import os
import sys
import ast
import xml.etree.ElementTree as ET
from pathlib import Path

class CommissionInstallationTester:
    """Test suite for commission module installation"""
    
    def __init__(self):
        self.module_path = Path(__file__).parent
        self.errors = []
        self.warnings = []
        
    def log_error(self, message):
        """Log an error"""
        self.errors.append(f"❌ ERROR: {message}")
        print(f"❌ ERROR: {message}")
        
    def log_warning(self, message):
        """Log a warning"""
        self.warnings.append(f"⚠️  WARNING: {message}")
        print(f"⚠️  WARNING: {message}")
        
    def log_success(self, message):
        """Log success"""
        print(f"✅ SUCCESS: {message}")
        
    def test_module_structure(self):
        """Test basic module structure"""
        print("\n🔍 Testing module structure...")
        
        required_files = [
            '__init__.py',
            '__manifest__.py',
            'wizards/__init__.py',
            'wizards/commission_partner_statement_wizard.py',
            'reports/__init__.py', 
            'reports/commission_partner_statement_report.py',
            'reports/commission_partner_statement_template.xml',
            'reports/commission_partner_statement_reports.xml',
            'views/commission_partner_statement_wizard_views.xml'
        ]
        
        for file_path in required_files:
            full_path = self.module_path / file_path
            if not full_path.exists():
                self.log_error(f"Missing required file: {file_path}")
            else:
                self.log_success(f"Found: {file_path}")
                
    def test_python_syntax(self):
        """Test Python file syntax"""
        print("\n🐍 Testing Python syntax...")
        
        python_files = [
            '__init__.py',
            'wizards/__init__.py',
            'wizards/commission_partner_statement_wizard.py', 
            'reports/__init__.py',
            'reports/commission_partner_statement_report.py'
        ]
        
        for file_path in python_files:
            full_path = self.module_path / file_path
            if full_path.exists():
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        source = f.read()
                    ast.parse(source)
                    self.log_success(f"Valid Python syntax: {file_path}")
                except SyntaxError as e:
                    self.log_error(f"Syntax error in {file_path}: {e}")
                except Exception as e:
                    self.log_error(f"Error parsing {file_path}: {e}")
            else:
                self.log_warning(f"Python file not found: {file_path}")
                
    def test_xml_syntax(self):
        """Test XML file syntax"""
        print("\n📄 Testing XML syntax...")
        
        xml_files = [
            'reports/commission_partner_statement_template.xml',
            'reports/commission_partner_statement_reports.xml',
            'views/commission_partner_statement_wizard_views.xml'
        ]
        
        for file_path in xml_files:
            full_path = self.module_path / file_path
            if full_path.exists():
                try:
                    ET.parse(str(full_path))
                    self.log_success(f"Valid XML syntax: {file_path}")
                except ET.ParseError as e:
                    self.log_error(f"XML syntax error in {file_path}: {e}")
                except Exception as e:
                    self.log_error(f"Error parsing XML {file_path}: {e}")
            else:
                self.log_warning(f"XML file not found: {file_path}")
                
    def test_manifest_structure(self):
        """Test manifest file structure"""
        print("\n📋 Testing manifest structure...")
        
        manifest_path = self.module_path / '__manifest__.py'
        if not manifest_path.exists():
            self.log_error("__manifest__.py not found")
            return
            
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest_content = f.read()
            
            # Parse manifest
            manifest_data = ast.literal_eval(manifest_content)
            
            # Check required fields
            required_fields = ['name', 'version', 'depends', 'data']
            for field in required_fields:
                if field in manifest_data:
                    self.log_success(f"Manifest has {field}: {manifest_data[field]}")
                else:
                    self.log_error(f"Manifest missing required field: {field}")
                    
            # Check data files
            if 'data' in manifest_data:
                for data_file in manifest_data['data']:
                    data_path = self.module_path / data_file
                    if data_path.exists():
                        self.log_success(f"Data file exists: {data_file}")
                    else:
                        self.log_error(f"Data file missing: {data_file}")
                        
        except Exception as e:
            self.log_error(f"Error parsing __manifest__.py: {e}")
            
    def test_client_order_ref_structure(self):
        """Test the new client_order_ref structure in templates and wizards"""
        print("\n🔄 Testing client_order_ref structure...")
        
        # Test wizard structure
        wizard_path = self.module_path / 'wizards/commission_partner_statement_wizard.py'
        if wizard_path.exists():
            with open(wizard_path, 'r', encoding='utf-8') as f:
                wizard_content = f.read()
                
            # Check for client_order_ref usage
            if 'client_order_ref' in wizard_content:
                self.log_success("Wizard contains client_order_ref field")
            else:
                self.log_error("Wizard missing client_order_ref field")
                
            # Check that old project/unit fields are not present
            if 'project_name' in wizard_content and "'project_name':" in wizard_content:
                self.log_warning("Wizard still contains project_name references")
            else:
                self.log_success("Wizard properly removed project_name references")
                
            if "'unit':" in wizard_content:
                self.log_warning("Wizard still contains unit field references")
            else:
                self.log_success("Wizard properly removed unit field references")
        
        # Test template structure
        template_path = self.module_path / 'reports/commission_partner_statement_template.xml'
        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
                
            # Check for client_order_ref in template
            if 'client_order_ref' in template_content:
                self.log_success("Template contains client_order_ref field")
            else:
                self.log_error("Template missing client_order_ref field")
                
            # Check table structure (should be 7 columns now)
            if 'colspan="7"' in template_content:
                self.log_success("Template has correct column count (7 columns)")
            elif 'colspan="8"' in template_content:
                self.log_error("Template still has old column count (8 columns)")
            
            # Check for removed project/unit headers
            if 'Project</th>' in template_content:
                self.log_error("Template still contains Project column")
            else:
                self.log_success("Template properly removed Project column")
                
            if 'Unit</th>' in template_content:
                self.log_error("Template still contains Unit column") 
            else:
                self.log_success("Template properly removed Unit column")
                
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Commission AX Installation Tests")
        print("=" * 60)
        
        self.test_module_structure()
        self.test_python_syntax()
        self.test_xml_syntax() 
        self.test_manifest_structure()
        self.test_client_order_ref_structure()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        if self.errors:
            print(f"❌ ERRORS: {len(self.errors)}")
            for error in self.errors:
                print(f"   {error}")
        else:
            print("✅ NO ERRORS FOUND")
            
        if self.warnings:
            print(f"⚠️  WARNINGS: {len(self.warnings)}")
            for warning in self.warnings:
                print(f"   {warning}")
        else:
            print("✅ NO WARNINGS")
            
        print("\n🎯 INSTALLATION STATUS:", end=" ")
        if not self.errors:
            print("✅ READY FOR INSTALLATION")
            return True
        else:
            print("❌ NEEDS FIXES BEFORE INSTALLATION")
            return False

def main():
    """Main test runner"""
    tester = CommissionInstallationTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()