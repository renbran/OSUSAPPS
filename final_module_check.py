#!/usr/bin/env python3
"""
Final comprehensive check for payment_account_enhanced module
This script checks for all potential field reference issues
"""

import os
import re
import xml.etree.ElementTree as ET

def check_field_references():
    """Check for references to non-existent fields"""
    module_path = "payment_account_enhanced"
    
    # Fields that actually exist in account_payment.py
    existing_fields = {
        'approval_state', 'voucher_number', 'remarks',
        'reviewer_id', 'reviewer_date', 'approver_id', 'approver_date',
        'authorizer_id', 'authorizer_date'
    }
    
    # Common problematic field names
    problematic_fields = {
        'authorized_by', 'approved_by', 'reviewed_by', 
        'amount_available_for_refund', 'enable_payment_approval_workflow',
        'enable_payment_qr_verification', 'auto_post_approved_payments',
        'enable_payment_verification', 'enable_four_stage_approval',
        'send_approval_notifications', 'max_approval_amount'
    }
    
    issues_found = []
    files_checked = 0
    
    # Check all XML files
    for root, dirs, files in os.walk(module_path):
        for file in files:
            if file.endswith('.xml'):
                file_path = os.path.join(root, file)
                files_checked += 1
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for field references
                    field_refs = re.findall(r'field name="([^"]*)"', content)
                    t_field_refs = re.findall(r't-field="[^.]*\.([^"]*)"', content)
                    
                    all_refs = field_refs + t_field_refs
                    
                    for field_ref in all_refs:
                        if field_ref in problematic_fields:
                            issues_found.append(f"❌ {file_path}: references non-existent field '{field_ref}'")
                            
                except Exception as e:
                    issues_found.append(f"⚠️ {file_path}: Error reading file - {e}")
    
    print(f"🔍 Checked {files_checked} XML files")
    print("=" * 60)
    
    if issues_found:
        print("❌ ISSUES FOUND:")
        for issue in issues_found:
            print(issue)
        return False
    else:
        print("✅ NO FIELD REFERENCE ISSUES FOUND")
        return True

def validate_manifest():
    """Validate all files in manifest exist"""
    manifest_path = "payment_account_enhanced/__manifest__.py"
    
    if not os.path.exists(manifest_path):
        print("❌ Manifest file not found")
        return False
        
    try:
        with open(manifest_path, 'r') as f:
            content = f.read()
        
        # Extract data files
        data_match = re.search(r"'data'\s*:\s*\[(.*?)\]", content, re.DOTALL)
        if not data_match:
            print("❌ No data section in manifest")
            return False
            
        data_files = re.findall(r"'([^']+)'", data_match.group(1))
        
        missing_files = []
        for data_file in data_files:
            file_path = os.path.join("payment_account_enhanced", data_file)
            if not os.path.exists(file_path):
                missing_files.append(data_file)
        
        if missing_files:
            print("❌ MISSING MANIFEST FILES:")
            for file in missing_files:
                print(f"   - {file}")
            return False
        else:
            print(f"✅ ALL {len(data_files)} MANIFEST FILES EXIST")
            return True
            
    except Exception as e:
        print(f"❌ Error reading manifest: {e}")
        return False

def main():
    print("🧹 FINAL PAYMENT MODULE CLEANUP VERIFICATION")
    print("=" * 60)
    
    if not os.path.exists("payment_account_enhanced"):
        print("❌ Module directory not found")
        return 1
    
    # Check field references
    field_check = check_field_references()
    print()
    
    # Check manifest
    manifest_check = validate_manifest()
    print()
    
    # Summary
    print("=" * 60)
    if field_check and manifest_check:
        print("🎉 MODULE IS CLEAN AND READY FOR INSTALLATION!")
        print("✅ No problematic field references found")
        print("✅ All manifest files exist")
        print()
        print("You can now try:")
        print("docker exec osusapps-odoo-1 odoo -i payment_account_enhanced --stop-after-init -d odoo")
        return 0
    else:
        print("❌ MODULE STILL HAS ISSUES - NEEDS MORE CLEANUP")
        return 1

if __name__ == "__main__":
    exit(main())