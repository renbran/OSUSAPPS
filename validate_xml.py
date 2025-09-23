#!/usr/bin/env python3
"""
Simple XML validation script for quantity_percentage module views
"""
import os
import sys

def validate_xml_file(filename):
    """Check if XML file is well-formed"""
    try:
        import xml.etree.ElementTree as ET
        ET.parse(filename)
        print(f"✓ {filename} is valid XML")
        return True
    except ET.ParseError as e:
        print(f"✗ {filename} has XML syntax error: {e}")
        return False
    except FileNotFoundError:
        print(f"✗ {filename} not found")
        return False

def main():
    """Validate XML files in the quantity_percentage module"""
    print("Validating quantity_percentage module XML files...")
    
    files_to_check = [
        "quantity_percentage/views/account_move_views.xml",
        "quantity_percentage/views/sale_order_views.xml"
    ]
    
    all_valid = True
    for filename in files_to_check:
        if not validate_xml_file(filename):
            all_valid = False
    
    if all_valid:
        print("\n✓ All XML files are valid!")
        return 0
    else:
        print("\n✗ Some XML files have errors")
        return 1

if __name__ == "__main__":
    sys.exit(main())