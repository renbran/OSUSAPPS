#!/usr/bin/env python3
"""
Simple validation script for Custom Calendar Invitations module
"""

import os
import ast
import sys

def validate_manifest(path):
    """Validate the manifest file"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse as Python code
        manifest = ast.literal_eval(content.split('{', 1)[1].rsplit('}', 1)[0])
        
        required_keys = ['name', 'version', 'depends', 'data']
        for key in required_keys:
            if key not in manifest:
                print(f"❌ Missing required key: {key}")
                return False
        
        print("✅ Manifest validation passed")
        return True
    except Exception as e:
        print(f"❌ Manifest validation failed: {e}")
        return False

def validate_structure():
    """Validate module structure"""
    base_path = "custom_calendar_invitations"
    
    required_files = [
        "__manifest__.py",
        "__init__.py", 
        "models/__init__.py",
        "models/calendar_event.py",
        "data/calendar_templates.xml",
        "security/ir.model.access.csv"
    ]
    
    print("🔍 Validating module structure...")
    
    if not os.path.exists(base_path):
        print(f"❌ Module directory not found: {base_path}")
        return False
    
    all_good = True
    for file_path in required_files:
        full_path = os.path.join(base_path, file_path)
        if os.path.exists(full_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            all_good = False
    
    return all_good

def main():
    print("🧪 Custom Calendar Invitations Module Validation")
    print("=" * 50)
    
    structure_ok = validate_structure()
    manifest_ok = validate_manifest("custom_calendar_invitations/__manifest__.py")
    
    if structure_ok and manifest_ok:
        print("\n🎯 Module validation PASSED! Ready for installation.")
        return 0
    else:
        print("\n❌ Module validation FAILED!")
        return 1

if __name__ == "__main__":
    sys.exit(main())