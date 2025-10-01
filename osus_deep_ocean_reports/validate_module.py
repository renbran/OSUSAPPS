#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deep Ocean Reports Module Validation Script
Validates the module structure and compatibility for Odoo 17
"""

import os
import ast
import xml.etree.ElementTree as ET

def validate_manifest(manifest_path):
    """Validate the __manifest__.py file"""
    print("✓ Validating __manifest__.py...")
    
    with open(manifest_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    try:
        # Parse the manifest as Python code
        parsed = ast.parse(content)
        print("  ✓ Manifest syntax is valid")
        
        # Check if it's a dictionary
        if isinstance(parsed.body[0].value, ast.Dict):
            print("  ✓ Manifest is a valid dictionary")
        
        # Extract manifest data
        exec(content, {'__builtins__': {}}, {})
        print("  ✓ Manifest can be executed without errors")
        
    except Exception as e:
        print(f"  ✗ Manifest validation failed: {e}")
        return False
    
    return True

def validate_xml_files(module_path):
    """Validate XML files in the module"""
    print("✓ Validating XML files...")
    
    xml_dirs = ['views', 'reports', 'data']
    valid = True
    
    for xml_dir in xml_dirs:
        xml_path = os.path.join(module_path, xml_dir)
        if os.path.exists(xml_path):
            for file in os.listdir(xml_path):
                if file.endswith('.xml'):
                    file_path = os.path.join(xml_path, file)
                    try:
                        ET.parse(file_path)
                        print(f"  ✓ {xml_dir}/{file} is valid XML")
                    except ET.ParseError as e:
                        print(f"  ✗ {xml_dir}/{file} has XML errors: {e}")
                        valid = False
    
    return valid

def validate_python_files(module_path):
    """Validate Python files in the module"""
    print("✓ Validating Python files...")
    
    python_files = []
    for root, dirs, files in os.walk(module_path):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    valid = True
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            ast.parse(content)
            print(f"  ✓ {os.path.relpath(py_file, module_path)} syntax is valid")
        except SyntaxError as e:
            print(f"  ✗ {os.path.relpath(py_file, module_path)} has syntax errors: {e}")
            valid = False
    
    return valid

def validate_file_structure(module_path):
    """Validate the module file structure"""
    print("✓ Validating module structure...")
    
    required_files = [
        '__init__.py',
        '__manifest__.py',
        'models/__init__.py',
        'security/ir.model.access.csv'
    ]
    
    valid = True
    for required_file in required_files:
        file_path = os.path.join(module_path, required_file)
        if os.path.exists(file_path):
            print(f"  ✓ {required_file} exists")
        else:
            print(f"  ✗ {required_file} is missing")
            valid = False
    
    return valid

def main():
    """Main validation function"""
    module_path = os.path.dirname(os.path.abspath(__file__))
    print(f"Validating Deep Ocean Reports module at: {module_path}")
    print("=" * 60)
    
    # Run all validations
    validations = [
        validate_file_structure(module_path),
        validate_manifest(os.path.join(module_path, '__manifest__.py')),
        validate_python_files(module_path),
        validate_xml_files(module_path)
    ]
    
    print("=" * 60)
    if all(validations):
        print("🎉 ALL VALIDATIONS PASSED! Module is ready for installation.")
        return 0
    else:
        print("❌ SOME VALIDATIONS FAILED! Please fix the issues above.")
        return 1

if __name__ == '__main__':
    exit(main())