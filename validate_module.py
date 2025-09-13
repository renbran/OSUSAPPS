#!/usr/bin/env python3
"""
Simple validation script to check if payment_account_enhanced module is properly structured
"""

import os
import sys
import xml.etree.ElementTree as ET

def validate_xml_file(filepath):
    """Validate an XML file can be parsed"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse XML
        root = ET.fromstring(content)
        return True, "Valid XML"
    except ET.ParseError as e:
        return False, f"XML Parse Error: {e}"
    except Exception as e:
        return False, f"Error: {e}"

def main():
    module_path = "/d/RUNNING APPS/ready production/latest/OSUSAPPS/payment_account_enhanced"
    if len(sys.argv) > 1:
        module_path = sys.argv[1]
    
    if not os.path.exists(module_path):
        print(f"❌ Module path not found: {module_path}")
        return 1
    
    print(f"🔍 Validating module: {module_path}")
    print("=" * 50)
    
    # Check manifest
    manifest_path = os.path.join(module_path, "__manifest__.py")
    if not os.path.exists(manifest_path):
        print("❌ __manifest__.py not found")
        return 1
    
    # Load manifest to get data files
    try:
        with open(manifest_path, 'r') as f:
            manifest_content = f.read()
        
        # Extract data files (simple approach)
        import re
        data_match = re.search(r"'data'\s*:\s*\[(.*?)\]", manifest_content, re.DOTALL)
        if not data_match:
            print("❌ No data section found in manifest")
            return 1
            
        data_section = data_match.group(1)
        data_files = re.findall(r"'([^']+)'", data_section)
        
        print(f"📋 Found {len(data_files)} data files in manifest")
        print()
        
        # Validate each data file
        missing_files = []
        invalid_xml = []
        
        for data_file in data_files:
            file_path = os.path.join(module_path, data_file)
            
            if not os.path.exists(file_path):
                missing_files.append(data_file)
                print(f"❌ MISSING: {data_file}")
                continue
                
            # Validate XML files
            if data_file.endswith('.xml'):
                is_valid, message = validate_xml_file(file_path)
                if is_valid:
                    print(f"✅ {data_file}")
                else:
                    invalid_xml.append((data_file, message))
                    print(f"❌ INVALID XML: {data_file} - {message}")
            else:
                print(f"✅ {data_file}")
        
        print()
        print("=" * 50)
        print("📊 SUMMARY:")
        print(f"Total files: {len(data_files)}")
        print(f"Missing files: {len(missing_files)}")
        print(f"Invalid XML files: {len(invalid_xml)}")
        
        if missing_files or invalid_xml:
            print()
            print("❌ MODULE VALIDATION FAILED")
            return 1
        else:
            print()
            print("✅ MODULE VALIDATION PASSED")
            return 0
            
    except Exception as e:
        print(f"❌ Error processing manifest: {e}")
        return 1

if __name__ == "__main__":
    exit(main())