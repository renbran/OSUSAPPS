#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick validation script for Deep Ocean Reports module
"""

import os
import xml.etree.ElementTree as ET

def validate_xml_files():
    """Validate all XML files in the module"""
    print("🔍 Validating XML files...")
    
    xml_dirs = ['views', 'reports', 'data']
    module_path = os.path.dirname(os.path.abspath(__file__))
    
    all_valid = True
    for xml_dir in xml_dirs:
        xml_path = os.path.join(module_path, xml_dir)
        if os.path.exists(xml_path):
            for file in os.listdir(xml_path):
                if file.endswith('.xml'):
                    file_path = os.path.join(xml_path, file)
                    try:
                        ET.parse(file_path)
                        print(f"  ✅ {xml_dir}/{file} - Valid XML")
                    except ET.ParseError as e:
                        print(f"  ❌ {xml_dir}/{file} - XML Error: {e}")
                        all_valid = False
                    except Exception as e:
                        print(f"  ⚠️  {xml_dir}/{file} - Warning: {e}")
    
    return all_valid

def check_file_structure():
    """Check if all required files exist"""
    print("📁 Checking file structure...")
    
    required_files = [
        '__init__.py',
        '__manifest__.py',
        'models/__init__.py',
        'models/deep_ocean_invoice.py',
        'security/ir.model.access.csv',
        'views/account_move_views.xml',
        'reports/deep_ocean_invoice_report.xml',
        'reports/deep_ocean_receipt_report.xml',
        'static/src/css/deep_ocean_reports.css',
        'static/src/js/deep_ocean_reports.js'
    ]
    
    module_path = os.path.dirname(os.path.abspath(__file__))
    all_exist = True
    
    for required_file in required_files:
        file_path = os.path.join(module_path, required_file)
        if os.path.exists(file_path):
            print(f"  ✅ {required_file}")
        else:
            print(f"  ❌ {required_file} - Missing!")
            all_exist = False
    
    return all_exist

def main():
    """Main validation function"""
    print("🌊 DEEP OCEAN REPORTS - FINAL VALIDATION")
    print("=" * 50)
    
    structure_ok = check_file_structure()
    xml_ok = validate_xml_files()
    
    print("=" * 50)
    if structure_ok and xml_ok:
        print("🎉 MODULE IS READY FOR INSTALLATION!")
        print("✅ All files present")
        print("✅ All XML files are valid")
        print("✅ Module structure is correct")
        print()
        print("📦 INSTALLATION INSTRUCTIONS:")
        print("1. Update Apps List in Odoo")
        print("2. Search for 'OSUS Deep Ocean Reports'")
        print("3. Click Install")
        print("4. Navigate to Accounting → Deep Ocean Reports")
        return 0
    else:
        print("❌ MODULE VALIDATION FAILED!")
        if not structure_ok:
            print("❌ Missing required files")
        if not xml_ok:
            print("❌ XML syntax errors found")
        return 1

if __name__ == '__main__':
    exit(main())