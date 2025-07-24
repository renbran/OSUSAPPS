#!/usr/bin/env python3
"""
Module validation script for automated_employee_announce
"""

import os
import json
from pathlib import Path

def validate_module():
    """Validate the automated_employee_announce module structure and files."""
    
    module_path = Path(__file__).parent
    print(f"Validating module at: {module_path}")
    
    # Check required files
    required_files = [
        '__init__.py',
        '__manifest__.py',
        'models/__init__.py',
        'models/automated_mail_rule.py',
        'models/hr_employee.py', 
        'models/sale_order_mail_automation.py',
        'views/automated_mail_rule_views.xml',
        'views/hr_employee.xml',
        'views/menu.xml',
        'data/mail_templates.xml',
        'data/cron_jobs.xml',
        'data/automated_mail_rule_data.xml',
        'security/ir.model.access.csv',
        'demo/demo_data.xml',
        'tests/__init__.py',
        'tests/test_automated_mails.py',
        'static/description/index.html',
        'static/description/icon.png',
        'README.md'
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = module_path / file_path
        if not full_path.exists():
            missing_files.append(file_path)
        else:
            print(f"✓ {file_path}")
    
    if missing_files:
        print(f"\n❌ Missing files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    
    print(f"\n✅ All required files present!")
    
    # Check manifest structure
    try:
        with open(module_path / '__manifest__.py', 'r') as f:
            manifest_content = f.read()
            
        # Basic checks
        required_manifest_keys = ['name', 'version', 'category', 'depends', 'data']
        for key in required_manifest_keys:
            if f"'{key}'" not in manifest_content:
                print(f"❌ Missing manifest key: {key}")
                return False
        
        print("✅ Manifest structure valid!")
        
    except Exception as e:
        print(f"❌ Error reading manifest: {e}")
        return False
    
    # Check XML syntax (basic)
    xml_files = [
        'views/automated_mail_rule_views.xml',
        'views/hr_employee.xml', 
        'views/menu.xml',
        'data/mail_templates.xml',
        'data/cron_jobs.xml',
        'data/automated_mail_rule_data.xml',
        'demo/demo_data.xml'
    ]
    
    for xml_file in xml_files:
        try:
            with open(module_path / xml_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if not content.strip().startswith('<?xml'):
                    print(f"❌ {xml_file}: Not a valid XML file")
                    return False
                if '</odoo>' not in content:
                    print(f"❌ {xml_file}: Missing closing </odoo> tag")
                    return False
            print(f"✓ {xml_file}: XML structure valid")
        except Exception as e:
            print(f"❌ Error reading {xml_file}: {e}")
            return False
    
    print(f"\n🎉 Module validation completed successfully!")
    print(f"📦 The automated_employee_announce module is ready for installation.")
    
    return True

if __name__ == '__main__':
    validate_module()
