#!/usr/bin/env python3
"""
Validation script for payment_account_enhanced wizard field fix
"""

import sys
import os
import xml.etree.ElementTree as ET

def validate_wizard_fix():
    """Validate that the wizard field reference issue is fixed"""
    
    module_path = "payment_account_enhanced"
    
    print("🔍 Validating Wizard Field Fix...")
    print("=" * 50)
    
    # Check 1: account_payment_register.py content
    register_file = f"{module_path}/models/account_payment_register.py"
    try:
        with open(register_file, 'r') as f:
            content = f.read()
            
        if 'class AccountPaymentRegister' in content:
            print("✅ account_payment_register.py contains AccountPaymentRegister model")
        else:
            print("❌ account_payment_register.py missing AccountPaymentRegister model")
            return False
            
        if 'remarks = fields.Text' in content:
            print("✅ AccountPaymentRegister has 'remarks' field")
        else:
            print("❌ AccountPaymentRegister missing 'remarks' field")
            return False
            
        if 'qr_in_report = fields.Boolean' in content:
            print("✅ AccountPaymentRegister has 'qr_in_report' field")
        else:
            print("❌ AccountPaymentRegister missing 'qr_in_report' field")
            return False
            
    except Exception as e:
        print(f"❌ Error reading {register_file}: {e}")
        return False
    
    # Check 2: payment_workflow_stage.py content
    stage_file = f"{module_path}/models/payment_workflow_stage.py"
    try:
        with open(stage_file, 'r') as f:
            content = f.read()
            
        if 'class PaymentWorkflowStage' in content:
            print("✅ payment_workflow_stage.py contains PaymentWorkflowStage model")
        else:
            print("❌ payment_workflow_stage.py missing PaymentWorkflowStage model")
            return False
            
    except Exception as e:
        print(f"❌ Error reading {stage_file}: {e}")
        return False
    
    # Check 3: register_payment.xml validity
    wizard_file = f"{module_path}/wizards/register_payment.xml"
    try:
        tree = ET.parse(wizard_file)
        print("✅ register_payment.xml is valid XML")
        
        with open(wizard_file, 'r') as f:
            xml_content = f.read()
            
        if 'name="remarks"' in xml_content:
            print("✅ Wizard XML references 'remarks' field")
        else:
            print("❌ Wizard XML missing 'remarks' field reference")
            return False
            
        if 'name="qr_in_report"' in xml_content:
            print("✅ Wizard XML references 'qr_in_report' field")
        else:
            print("❌ Wizard XML missing 'qr_in_report' field reference")
            return False
            
    except Exception as e:
        print(f"❌ Error parsing {wizard_file}: {e}")
        return False
    
    print("=" * 50)
    print("🎉 ALL WIZARD FIELD CHECKS PASSED!")
    print("\n📋 Summary:")
    print("✅ AccountPaymentRegister model has required fields")
    print("✅ PaymentWorkflowStage model in correct file")
    print("✅ Wizard XML references match model fields")
    print("✅ No field reference errors expected")
    
    return True

if __name__ == "__main__":
    if validate_wizard_fix():
        print("\n🚀 Module ready for installation!")
        sys.exit(0)
    else:
        print("\n❌ Validation failed!")
        sys.exit(1)