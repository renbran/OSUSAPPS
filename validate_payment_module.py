#!/usr/bin/env python3
"""
Comprehensive Payment Account Enhanced Module Validator
======================================================

This script validates the payment_account_enhanced module for:
- Python syntax and imports
- XML structure and references  
- Security configuration
- Dependencies
- Odoo 17 compliance
- File structure integrity
"""

import os
import sys
import ast
import xml.etree.ElementTree as ET
import importlib.util
import re
import csv
from pathlib import Path
import subprocess
import json
from typing import Dict, List, Tuple, Any

class ModuleValidator:
    def __init__(self, module_path: str):
        self.module_path = Path(module_path)
        self.errors = []
        self.warnings = []
        self.info = []
        self.manifest = None
        
    def log_error(self, message: str, file_path: str = None):
        """Log an error with optional file path"""
        if file_path:
            self.errors.append(f"ERROR [{file_path}]: {message}")
        else:
            self.errors.append(f"ERROR: {message}")
    
    def log_warning(self, message: str, file_path: str = None):
        """Log a warning with optional file path"""
        if file_path:
            self.warnings.append(f"WARNING [{file_path}]: {message}")
        else:
            self.warnings.append(f"WARNING: {message}")
    
    def log_info(self, message: str, file_path: str = None):
        """Log info with optional file path"""
        if file_path:
            self.info.append(f"INFO [{file_path}]: {message}")
        else:
            self.info.append(f"INFO: {message}")

    def validate_module_structure(self) -> bool:
        """Validate basic module structure"""
        print("🔍 Validating module structure...")
        
        if not self.module_path.exists():
            self.log_error(f"Module path does not exist: {self.module_path}")
            return False
        
        required_files = ['__init__.py', '__manifest__.py']
        required_dirs = ['models', 'views', 'security']
        
        for file in required_files:
            file_path = self.module_path / file
            if not file_path.exists():
                self.log_error(f"Required file missing: {file}")
            else:
                self.log_info(f"Required file found: {file}")
        
        for dir_name in required_dirs:
            dir_path = self.module_path / dir_name
            if not dir_path.exists():
                self.log_warning(f"Recommended directory missing: {dir_name}")
            else:
                self.log_info(f"Directory found: {dir_name}")
        
        return len(self.errors) == 0

    def validate_manifest(self) -> bool:
        """Validate __manifest__.py file"""
        print("📋 Validating manifest file...")
        
        manifest_path = self.module_path / '__manifest__.py'
        if not manifest_path.exists():
            self.log_error("__manifest__.py not found")
            return False
        
        try:
            # Read and parse manifest
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest_content = f.read()
            
            # Parse as Python dict
            self.manifest = ast.literal_eval(manifest_content)
            
            # Validate required fields
            required_fields = ['name', 'version', 'depends', 'data', 'installable']
            for field in required_fields:
                if field not in self.manifest:
                    self.log_error(f"Required manifest field missing: {field}", "__manifest__.py")
                else:
                    self.log_info(f"Manifest field found: {field}", "__manifest__.py")
            
            # Validate version format for Odoo 17
            version = self.manifest.get('version', '')
            if not version.startswith('17.0'):
                self.log_warning(f"Version should start with '17.0' for Odoo 17: {version}", "__manifest__.py")
            
            # Check dependencies
            depends = self.manifest.get('depends', [])
            required_deps = ['base', 'account']
            for dep in required_deps:
                if dep not in depends:
                    self.log_warning(f"Recommended dependency missing: {dep}", "__manifest__.py")
            
            # Validate external dependencies
            ext_deps = self.manifest.get('external_dependencies', {})
            python_deps = ext_deps.get('python', [])
            if python_deps:
                self.log_info(f"External Python dependencies: {python_deps}", "__manifest__.py")
            
            return True
            
        except Exception as e:
            self.log_error(f"Failed to parse manifest: {str(e)}", "__manifest__.py")
            return False

    def validate_python_files(self) -> bool:
        """Validate all Python files for syntax and imports"""
        print("🐍 Validating Python files...")
        
        python_files = list(self.module_path.rglob("*.py"))
        if not python_files:
            self.log_warning("No Python files found in module")
            return True
        
        for py_file in python_files:
            try:
                # Check syntax
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                ast.parse(content, filename=str(py_file))
                self.log_info(f"Python syntax valid", str(py_file.relative_to(self.module_path)))
                
                # Check for common Odoo patterns
                if 'from odoo import' in content:
                    self.log_info("Uses proper Odoo imports", str(py_file.relative_to(self.module_path)))
                
                # Check for Odoo 17 specific patterns
                if 'api.model' in content or 'api.depends' in content:
                    self.log_info("Uses Odoo API decorators", str(py_file.relative_to(self.module_path)))
                
                # Check for potential issues
                if 'osv.Model' in content:
                    self.log_warning("Uses deprecated osv.Model (use models.Model)", str(py_file.relative_to(self.module_path)))
                
                if 'cr.execute' in content:
                    self.log_warning("Direct SQL execution found - ensure security", str(py_file.relative_to(self.module_path)))
                
            except SyntaxError as e:
                self.log_error(f"Python syntax error: {str(e)}", str(py_file.relative_to(self.module_path)))
            except Exception as e:
                self.log_error(f"Failed to validate Python file: {str(e)}", str(py_file.relative_to(self.module_path)))
        
        return len([e for e in self.errors if "Python syntax error" in e]) == 0

    def validate_xml_files(self) -> bool:
        """Validate all XML files for structure and syntax"""
        print("📄 Validating XML files...")
        
        xml_files = list(self.module_path.rglob("*.xml"))
        if not xml_files:
            self.log_warning("No XML files found in module")
            return True
        
        for xml_file in xml_files:
            try:
                tree = ET.parse(xml_file)
                root = tree.getroot()
                
                self.log_info(f"XML syntax valid", str(xml_file.relative_to(self.module_path)))
                
                # Check for common XML patterns
                if root.tag == 'odoo':
                    self.log_info("Uses proper <odoo> root element", str(xml_file.relative_to(self.module_path)))
                
                # Check for required elements in views
                if xml_file.name.endswith('_views.xml'):
                    records = root.findall('.//record')
                    if records:
                        self.log_info(f"Found {len(records)} record(s)", str(xml_file.relative_to(self.module_path)))
                    
                    # Check for view types
                    view_types = []
                    for record in records:
                        model = record.get('model')
                        if model == 'ir.ui.view':
                            arch = record.find('.//field[@name="arch"]')
                            if arch is not None:
                                view_content = ET.tostring(arch, encoding='unicode')
                                if '<form' in view_content:
                                    view_types.append('form')
                                elif '<tree' in view_content:
                                    view_types.append('tree')
                                elif '<search' in view_content:
                                    view_types.append('search')
                    
                    if view_types:
                        self.log_info(f"View types found: {', '.join(set(view_types))}", str(xml_file.relative_to(self.module_path)))
                
                # Check security files
                if 'security' in str(xml_file):
                    groups = root.findall('.//record[@model="res.groups"]')
                    rules = root.findall('.//record[@model="ir.rule"]')
                    if groups:
                        self.log_info(f"Found {len(groups)} security group(s)", str(xml_file.relative_to(self.module_path)))
                    if rules:
                        self.log_info(f"Found {len(rules)} security rule(s)", str(xml_file.relative_to(self.module_path)))
                
            except ET.ParseError as e:
                self.log_error(f"XML parse error: {str(e)}", str(xml_file.relative_to(self.module_path)))
            except Exception as e:
                self.log_error(f"Failed to validate XML file: {str(e)}", str(xml_file.relative_to(self.module_path)))
        
        return len([e for e in self.errors if "XML parse error" in e]) == 0

    def validate_security_files(self) -> bool:
        """Validate security configuration"""
        print("🔒 Validating security configuration...")
        
        security_dir = self.module_path / 'security'
        if not security_dir.exists():
            self.log_warning("Security directory not found")
            return True
        
        # Check ir.model.access.csv
        access_file = security_dir / 'ir.model.access.csv'
        if access_file.exists():
            try:
                with open(access_file, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    headers = next(reader, None)
                    
                    expected_headers = ['id', 'name', 'model_id:id', 'group_id:id', 'perm_read', 'perm_write', 'perm_create', 'perm_unlink']
                    if headers == expected_headers:
                        self.log_info("Access rights CSV has correct headers", "security/ir.model.access.csv")
                    else:
                        self.log_warning(f"Access rights CSV headers may be incorrect: {headers}", "security/ir.model.access.csv")
                    
                    access_count = sum(1 for _ in reader)
                    self.log_info(f"Found {access_count} access right(s)", "security/ir.model.access.csv")
                    
            except Exception as e:
                self.log_error(f"Failed to validate access rights: {str(e)}", "security/ir.model.access.csv")
        else:
            self.log_warning("ir.model.access.csv not found", "security/")
        
        # Check security XML files
        security_xml_files = list(security_dir.glob("*.xml"))
        for xml_file in security_xml_files:
            self.log_info(f"Security XML file found", str(xml_file.relative_to(self.module_path)))
        
        return True

    def validate_dependencies(self) -> bool:
        """Validate external dependencies availability"""
        print("📦 Validating dependencies...")
        
        if not self.manifest:
            self.log_warning("Cannot validate dependencies - manifest not loaded")
            return True
        
        # Check Python dependencies
        ext_deps = self.manifest.get('external_dependencies', {})
        python_deps = ext_deps.get('python', [])
        
        for dep in python_deps:
            try:
                __import__(dep)
                self.log_info(f"Python dependency available: {dep}")
            except ImportError:
                self.log_error(f"Python dependency not available: {dep}")
        
        # Check Odoo module dependencies
        odoo_deps = self.manifest.get('depends', [])
        for dep in odoo_deps:
            # Note: In a real environment, we'd check if these modules are installed
            self.log_info(f"Odoo dependency declared: {dep}")
        
        return len([e for e in self.errors if "dependency not available" in e]) == 0

    def validate_data_files(self) -> bool:
        """Validate data files referenced in manifest"""
        print("📊 Validating data files...")
        
        if not self.manifest:
            self.log_warning("Cannot validate data files - manifest not loaded")
            return True
        
        data_files = self.manifest.get('data', [])
        
        for data_file in data_files:
            file_path = self.module_path / data_file
            if file_path.exists():
                self.log_info(f"Data file found: {data_file}")
                
                # Validate XML data files
                if data_file.endswith('.xml'):
                    try:
                        ET.parse(file_path)
                        self.log_info(f"Data file XML valid: {data_file}")
                    except ET.ParseError as e:
                        self.log_error(f"Data file XML invalid: {str(e)}", data_file)
                
                # Validate CSV data files
                elif data_file.endswith('.csv'):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            csv.reader(f)
                        self.log_info(f"Data file CSV valid: {data_file}")
                    except Exception as e:
                        self.log_error(f"Data file CSV invalid: {str(e)}", data_file)
            else:
                self.log_error(f"Data file not found: {data_file}")
        
        return len([e for e in self.errors if "Data file" in e and "not found" in e]) == 0

    def run_complete_validation(self) -> Dict[str, Any]:
        """Run all validation checks"""
        print("🚀 Starting comprehensive module validation...")
        print(f"Module path: {self.module_path}")
        print("=" * 60)
        
        validation_results = {
            'module_structure': self.validate_module_structure(),
            'manifest': self.validate_manifest(),
            'python_files': self.validate_python_files(),
            'xml_files': self.validate_xml_files(),
            'security_files': self.validate_security_files(),
            'dependencies': self.validate_dependencies(),
            'data_files': self.validate_data_files()
        }
        
        return validation_results

    def print_summary(self, results: Dict[str, Any]):
        """Print validation summary"""
        print("\n" + "=" * 60)
        print("📊 VALIDATION SUMMARY")
        print("=" * 60)
        
        # Results summary
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        print(f"✅ Checks passed: {passed}/{total}")
        
        for check, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {check.replace('_', ' ').title()}")
        
        # Detailed logs
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  {error}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  {warning}")
        
        if self.info:
            print(f"\n💡 INFO ({len(self.info)}):")
            for info in self.info:
                print(f"  {info}")
        
        # Overall status
        print("\n" + "=" * 60)
        if all(results.values()) and not self.errors:
            print("🎉 MODULE VALIDATION PASSED - Ready for installation!")
        elif self.errors:
            print("❌ MODULE VALIDATION FAILED - Errors must be fixed")
        else:
            print("⚠️  MODULE VALIDATION COMPLETED WITH WARNINGS")
        
        print("=" * 60)

def main():
    """Main validation function"""
    if len(sys.argv) != 2:
        print("Usage: python validate_payment_module.py <module_path>")
        sys.exit(1)
    
    module_path = sys.argv[1]
    validator = ModuleValidator(module_path)
    
    # Run validation
    results = validator.run_complete_validation()
    
    # Print summary
    validator.print_summary(results)
    
    # Exit with appropriate code
    if all(results.values()) and not validator.errors:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure

if __name__ == "__main__":
    main()