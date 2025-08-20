#!/usr/bin/env python3
"""
Simple validation script for partner_statement_followup module
"""

import xml.etree.ElementTree as ET
import os

def validate_xml_files():
    """Validate XML files in the module"""
    module_path = "partner_statement_followup"
    
    # XML files to check
    xml_files = [
        "data/followup_levels.xml",
        "views/statement_config_views.xml", 
        "views/partner_views.xml",
        "views/statement_menus.xml",
        "wizards/statement_wizard_views.xml",
        "wizards/batch_followup_wizard_views.xml"
    ]
    
    errors = []
    
    for xml_file in xml_files:
        file_path = os.path.join(module_path, xml_file)
        if not os.path.exists(file_path):
            errors.append(f"Missing file: {file_path}")
            continue
            
        try:
            ET.parse(file_path)
            print(f"✓ {xml_file} - Valid XML")
        except ET.ParseError as e:
            errors.append(f"XML Parse Error in {xml_file}: {e}")
        except Exception as e:
            errors.append(f"Error in {xml_file}: {e}")
    
    return errors

def validate_manifest():
    """Validate manifest file"""
    try:
        with open("partner_statement_followup/__manifest__.py", 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Basic syntax check
        compile(content, "__manifest__.py", "exec")
        print("✓ __manifest__.py - Valid Python syntax")
        return []
        
    except SyntaxError as e:
        return [f"Manifest syntax error: {e}"]
    except Exception as e:
        return [f"Manifest error: {e}"]

def main():
    print("=== Partner Statement Follow-up Module Validation ===\n")
    
    errors = []
    
    # Check XML files
    print("Checking XML files...")
    errors.extend(validate_xml_files())
    
    print("\nChecking manifest...")
    errors.extend(validate_manifest())
    
    print("\n" + "="*50)
    if errors:
        print("❌ VALIDATION FAILED")
        print("Errors found:")
        for error in errors:
            print(f"  - {error}")
        return 1
    else:
        print("✅ VALIDATION PASSED")
        print("No errors found. Module should be installable.")
        return 0

if __name__ == "__main__":
    exit(main())
