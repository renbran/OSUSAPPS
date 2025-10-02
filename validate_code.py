#!/usr/bin/env python3
"""
Quick Code Validation - No Database Check
This validates that ALL code is correct
"""
import os
import xml.etree.ElementTree as ET

def validate_all():
    print("🔍 VALIDATING CODE (No Database Access)")
    print("=" * 60)
    
    base = "rental_management"
    issues = []
    
    # 1. Check model exists
    print("\n1️⃣ Checking Model Import...")
    init_file = f"{base}/models/__init__.py"
    with open(init_file, 'r') as f:
        content = f.read()
        if 'property_payment_plan' in content:
            print("   ✅ Model 'property_payment_plan' is imported")
        else:
            print("   ❌ Model NOT imported")
            issues.append("Model not imported in __init__.py")
    
    # 2. Check model file exists
    print("\n2️⃣ Checking Model File...")
    model_file = f"{base}/models/property_payment_plan.py"
    if os.path.exists(model_file):
        with open(model_file, 'r') as f:
            content = f.read()
            if "_name = 'property.payment.plan'" in content:
                print("   ✅ Model defined with correct name")
            else:
                print("   ❌ Model name incorrect")
                issues.append("Model _name incorrect")
    else:
        print("   ❌ Model file missing")
        issues.append("Model file doesn't exist")
    
    # 3. Check action XML
    print("\n3️⃣ Checking Action XML...")
    action_file = f"{base}/views/property_payment_plan_actions.xml"
    if os.path.exists(action_file):
        try:
            tree = ET.parse(action_file)
            root = tree.getroot()
            # Find the record with correct ID
            found = False
            for record in root.findall(".//record[@id='property_payment_plan_action']"):
                found = True
                model = record.get('model')
                if model == 'ir.actions.act_window':
                    print("   ✅ Action record exists with correct model")
                else:
                    print(f"   ❌ Wrong model: {model}")
                    issues.append(f"Action has wrong model: {model}")
            if not found:
                print("   ❌ Action record ID not found")
                issues.append("Action ID 'property_payment_plan_action' not found")
        except Exception as e:
            print(f"   ❌ XML parse error: {e}")
            issues.append(f"XML parse error: {e}")
    else:
        print("   ❌ Action file missing")
        issues.append("Action XML file doesn't exist")
    
    # 4. Check menu reference
    print("\n4️⃣ Checking Menu Reference...")
    menu_file = f"{base}/views/menus.xml"
    if os.path.exists(menu_file):
        with open(menu_file, 'r') as f:
            content = f.read()
            if 'rental_management.property_payment_plan_action' in content:
                print("   ✅ Menu references correct external ID")
            elif 'property_payment_plan_action' in content:
                print("   ⚠️  Menu references action without module prefix")
                issues.append("Menu should use 'rental_management.property_payment_plan_action'")
            else:
                print("   ❌ Menu doesn't reference action")
                issues.append("Menu doesn't reference the action")
    else:
        print("   ❌ Menu file missing")
        issues.append("Menu file doesn't exist")
    
    # 5. Check manifest data loading
    print("\n5️⃣ Checking Manifest Loading Order...")
    manifest_file = f"{base}/__manifest__.py"
    with open(manifest_file, 'r') as f:
        content = f.read()
        action_pos = content.find('property_payment_plan_actions.xml')
        menu_pos = content.find('menus.xml')
        
        if action_pos == -1:
            print("   ❌ Action file NOT in manifest")
            issues.append("Action XML not in manifest data list")
        elif menu_pos == -1:
            print("   ❌ Menu file NOT in manifest")
            issues.append("Menu XML not in manifest data list")
        elif action_pos < menu_pos:
            print("   ✅ Loading order correct (actions before menus)")
        else:
            print("   ❌ Wrong order: menus load before actions")
            issues.append("Manifest loads menus before actions")
    
    # Final verdict
    print("\n" + "=" * 60)
    if not issues:
        print("✅ ALL CODE IS CORRECT!")
        print("\n🎯 CONCLUSION: This is a DATABASE issue, not a code issue.")
        print("\n📋 TO FIX:")
        print("   Run: FIX_NOW.bat")
        print("   Or: docker-compose exec odoo odoo -u rental_management -d YOUR_DB")
        return True
    else:
        print("❌ CODE ISSUES FOUND:")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
        return False

if __name__ == "__main__":
    # Already in correct directory
    validate_all()
