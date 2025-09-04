#!/usr/bin/env python3
"""
Commission_AX Module Validation Script
=====================================

This script validates the commission_ax module for Odoo 17 compliance.
"""

import os
import sys
import ast
import xml.etree.ElementTree as ET
from pathlib import Path


def validate_commission_ax_module(module_path):
    """Validate the commission_ax module structure and files."""
    print("🚀 Validating Commission_AX Module at:", os.path.abspath(module_path))
    print("=" * 60)
    
    errors = []
    warnings = []
    
    # Required files
    required_files = [
        '__init__.py',
        '__manifest__.py',
        'models/__init__.py',
        'models/sale_order.py',
        'models/purchase_order.py',
        'views/sale_order.xml',
        'views/purchase_order.xml',
        'security/ir.model.access.csv',
    ]
    
    print("🔍 Validating module structure...")
    for file_path in required_files:
        full_path = os.path.join(module_path, file_path)
        if os.path.exists(full_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
            errors.append(f"Missing required file: {file_path}")
    
    # Validate Python files
    print("\n🔍 Validating Python files...")
    python_files = [
        '__manifest__.py',
        'models/sale_order.py', 
        'models/purchase_order.py'
    ]
    
    for py_file in python_files:
        full_path = os.path.join(module_path, py_file)
        if os.path.exists(full_path):
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    ast.parse(f.read())
                print(f"✅ {py_file}")
            except SyntaxError as e:
                print(f"❌ Syntax error in {py_file}: {e}")
                errors.append(f"Syntax error in {py_file}: {e}")
            except Exception as e:
                print(f"⚠️ Warning in {py_file}: {e}")
                warnings.append(f"Warning in {py_file}: {e}")
        else:
            print(f"❌ Missing: {py_file}")
            errors.append(f"Missing file: {py_file}")
    
    # Validate XML files
    print("\n🔍 Validating XML files...")
    xml_files = [
        'views/sale_order.xml',
        'views/purchase_order.xml'
    ]
    
    for xml_file in xml_files:
        full_path = os.path.join(module_path, xml_file)
        if os.path.exists(full_path):
            try:
                ET.parse(full_path)
                print(f"✅ {xml_file}")
            except ET.ParseError as e:
                print(f"❌ XML parse error in {xml_file}: {e}")
                errors.append(f"XML parse error in {xml_file}: {e}")
        else:
            print(f"❌ Missing: {xml_file}")
            errors.append(f"Missing file: {xml_file}")
    
    # Validate manifest
    print("\n🔍 Validating manifest file...")
    manifest_path = os.path.join(module_path, '__manifest__.py')
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = ast.literal_eval(f.read())
            
            required_keys = ['name', 'version', 'depends', 'data']
            for key in required_keys:
                if key in manifest:
                    print(f"✅ {key}: {manifest[key] if key != 'data' else f'{len(manifest[key])} files'}")
                else:
                    print(f"❌ Missing manifest key: {key}")
                    errors.append(f"Missing manifest key: {key}")
                    
            # Check version format
            if 'version' in manifest:
                if not manifest['version'].startswith('17.0'):
                    warnings.append("Version should start with '17.0' for Odoo 17")
                    
        except Exception as e:
            print(f"❌ Error reading manifest: {e}")
            errors.append(f"Error reading manifest: {e}")
    
    # Check for vendor reference implementation
    print("\n🔍 Checking vendor reference auto-population...")
    sale_order_path = os.path.join(module_path, 'models/sale_order.py')
    if os.path.exists(sale_order_path):
        with open(sale_order_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if "'partner_ref': self.client_order_ref" in content:
                print("✅ Vendor reference auto-population implemented")
            else:
                print("❌ Vendor reference auto-population missing")
                errors.append("Vendor reference auto-population not implemented")
    
    # Check purchase order override
    print("\n🔍 Checking purchase order model...")
    po_path = os.path.join(module_path, 'models/purchase_order.py')
    if os.path.exists(po_path):
        with open(po_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if "@api.model_create_multi" in content:
                print("✅ Purchase order create method properly overridden")
            else:
                print("❌ Purchase order create method not properly overridden")
                errors.append("Purchase order create method missing @api.model_create_multi")
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 VALIDATION SUMMARY")
    print("=" * 60)
    
    if not errors:
        print("✅ All critical validations passed!")
        print("🎉 Module appears ready for installation")
    else:
        print(f"❌ Found {len(errors)} critical error(s):")
        for error in errors:
            print(f"  • {error}")
    
    if warnings:
        print(f"\n⚠️ Found {len(warnings)} warning(s):")
        for warning in warnings:
            print(f"  • {warning}")
    
    print(f"\n📊 Module Quality Score: {max(0, 100 - len(errors) * 20 - len(warnings) * 5)}/100")
    
    return len(errors) == 0


if __name__ == "__main__":
    module_path = os.path.dirname(os.path.abspath(__file__))
    success = validate_commission_ax_module(module_path)
    sys.exit(0 if success else 1)
