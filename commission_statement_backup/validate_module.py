#!/usr/bin/env python3
"""
Commission Statement Module Validation Script
This script validates the module structure and dependencies without requiring Odoo runtime.
"""

import os
import sys
import ast
import xml.etree.ElementTree as ET
from pathlib import Path

def validate_python_files(base_path):
    """Validate Python files for syntax errors"""
    print("🔍 Validating Python files...")
    python_files = list(Path(base_path).rglob("*.py"))
    
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            ast.parse(content)
            print(f"✅ {py_file.relative_to(base_path)}")
        except SyntaxError as e:
            print(f"❌ {py_file.relative_to(base_path)}: {e}")
            return False
        except Exception as e:
            print(f"⚠️  {py_file.relative_to(base_path)}: {e}")
    
    return True

def validate_xml_files(base_path):
    """Validate XML files for syntax errors"""
    print("\n🔍 Validating XML files...")
    xml_files = list(Path(base_path).rglob("*.xml"))
    
    for xml_file in xml_files:
        try:
            ET.parse(xml_file)
            print(f"✅ {xml_file.relative_to(base_path)}")
        except ET.ParseError as e:
            print(f"❌ {xml_file.relative_to(base_path)}: {e}")
            return False
        except Exception as e:
            print(f"⚠️  {xml_file.relative_to(base_path)}: {e}")
    
    return True

def validate_manifest(base_path):
    """Validate manifest file"""
    print("\n🔍 Validating manifest file...")
    manifest_path = base_path / "__manifest__.py"
    
    if not manifest_path.exists():
        print("❌ __manifest__.py not found")
        return False
    
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse as Python dict
        manifest = ast.literal_eval(content)
        
        # Check required fields
        required_fields = ['name', 'version', 'depends', 'data']
        for field in required_fields:
            if field not in manifest:
                print(f"❌ Missing required field: {field}")
                return False
            print(f"✅ {field}: {manifest[field]}")
        
        # Check if referenced files exist
        print("\n🔍 Checking referenced data files...")
        for data_file in manifest.get('data', []):
            file_path = base_path / data_file
            if file_path.exists():
                print(f"✅ {data_file}")
            else:
                print(f"❌ {data_file} (referenced in manifest but not found)")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error parsing manifest: {e}")
        return False

def validate_dependencies(base_path):
    """Check if dependency modules exist"""
    print("\n🔍 Checking dependencies...")
    manifest_path = base_path / "__manifest__.py"
    
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            content = f.read()
        manifest = ast.literal_eval(content)
        
        depends = manifest.get('depends', [])
        workspace_path = base_path.parent
        
        for dep in depends:
            if dep in ['base', 'web', 'sale', 'purchase']:
                print(f"✅ {dep} (core module)")
            else:
                dep_path = workspace_path / dep
                if dep_path.exists():
                    print(f"✅ {dep} (found in workspace)")
                else:
                    print(f"⚠️  {dep} (not found in workspace - should be available in Odoo)")
        
        return True
    except Exception as e:
        print(f"❌ Error checking dependencies: {e}")
        return False

def main():
    if len(sys.argv) > 1:
        module_path = Path(sys.argv[1])
    else:
        module_path = Path(__file__).parent
    
    print(f"🚀 Validating Commission Statement Module at: {module_path}")
    print("=" * 60)
    
    # Run validations
    validations = [
        validate_python_files(module_path),
        validate_xml_files(module_path),
        validate_manifest(module_path),
        validate_dependencies(module_path)
    ]
    
    print("\n" + "=" * 60)
    if all(validations):
        print("✅ All validations passed! Module appears to be properly structured.")
        print("\n📋 Next steps:")
        print("1. Ensure Docker is running")
        print("2. Start Odoo: docker-compose up -d")
        print("3. Update module: docker-compose exec odoo odoo --update=commission_statement -d odoo")
        return 0
    else:
        print("❌ Some validations failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
