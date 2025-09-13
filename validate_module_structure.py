#!/usr/bin/env python3
"""
Comprehensive module structure validation for payment_account_enhanced
"""

import logging
import os
import xml.etree.ElementTree as ET

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def validate_module_structure():
    """Validate the complete module structure"""
    logger.info("🚀 Starting Comprehensive Module Structure Validation...")
    
    module_path = "payment_account_enhanced"
    issues_found = []
    
    # Test 1: Check manifest file
    logger.info("Test 1: Validating manifest file...")
    manifest_file = f"{module_path}/__manifest__.py"
    if os.path.exists(manifest_file):
        try:
            with open(manifest_file, 'r', encoding='utf-8') as f:
                manifest_content = f.read()
            
            # Check for proper dependencies
            required_deps = ['base', 'account', 'mail', 'website', 'portal']
            for dep in required_deps:
                if f"'{dep}'" not in manifest_content:
                    issues_found.append(f"Missing dependency: {dep}")
            
            # Check data files in manifest
            data_files = [
                'security/payment_security.xml',
                'security/ir.model.access.csv',
                'data/sequence.xml',
                'views/menus.xml',
                'views/account_payment_views.xml'
            ]
            
            for data_file in data_files:
                if data_file not in manifest_content:
                    issues_found.append(f"Manifest missing data file: {data_file}")
                elif not os.path.exists(f"{module_path}/{data_file}"):
                    issues_found.append(f"Data file referenced but doesn't exist: {data_file}")
            
            logger.info("✅ Manifest file structure validated")
        except Exception as e:
            issues_found.append(f"Error reading manifest: {e}")
    else:
        issues_found.append("Manifest file not found")
    
    # Test 2: Check model files
    logger.info("Test 2: Validating model files...")
    model_files = [
        'models/__init__.py',
        'models/account_payment.py'
    ]
    
    for model_file in model_files:
        if not os.path.exists(f"{module_path}/{model_file}"):
            issues_found.append(f"Missing model file: {model_file}")
    
    # Check account_payment.py inheritance
    if os.path.exists(f"{module_path}/models/account_payment.py"):
        with open(f"{module_path}/models/account_payment.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "_inherit = 'account.payment'" not in content:
            issues_found.append("account_payment.py missing proper inheritance")
        
        if "approval_state = fields.Selection" not in content:
            issues_found.append("account_payment.py missing approval_state field")
    
    logger.info("✅ Model files validated")
    
    # Test 3: Check view files
    logger.info("Test 3: Validating view files...")
    view_files = [
        'views/menus.xml',
        'views/account_payment_views.xml'
    ]
    
    for view_file in view_files:
        if not os.path.exists(f"{module_path}/{view_file}"):
            issues_found.append(f"Missing view file: {view_file}")
        else:
            # Validate XML syntax
            try:
                ET.parse(f"{module_path}/{view_file}")
            except ET.ParseError as e:
                issues_found.append(f"XML syntax error in {view_file}: {e}")
    
    # Check for required actions in view files
    if os.path.exists(f"{module_path}/views/account_payment_views.xml"):
        with open(f"{module_path}/views/account_payment_views.xml", 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "action_account_payment_tree" not in content:
            issues_found.append("Missing action_account_payment_tree in account_payment_views.xml")
    
    logger.info("✅ View files validated")
    
    # Test 4: Check security files
    logger.info("Test 4: Validating security files...")
    security_files = [
        'security/payment_security.xml',
        'security/ir.model.access.csv'
    ]
    
    for security_file in security_files:
        if not os.path.exists(f"{module_path}/{security_file}"):
            issues_found.append(f"Missing security file: {security_file}")
    
    # Check for required groups
    if os.path.exists(f"{module_path}/security/payment_security.xml"):
        with open(f"{module_path}/security/payment_security.xml", 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_groups = [
            'group_payment_reviewer',
            'group_payment_approver',
            'group_payment_authorizer',
            'group_payment_poster'
        ]
        
        for group in required_groups:
            if group not in content:
                issues_found.append(f"Missing security group: {group}")
    
    logger.info("✅ Security files validated")
    
    # Test 5: Check wizard files
    logger.info("Test 5: Validating wizard files...")
    if not os.path.exists(f"{module_path}/wizards/__init__.py"):
        issues_found.append("Missing wizards/__init__.py")
    
    if not os.path.exists(f"{module_path}/wizards/register_payment.py"):
        issues_found.append("Missing wizards/register_payment.py")
    
    if not os.path.exists(f"{module_path}/wizards/register_payment.xml"):
        issues_found.append("Missing wizards/register_payment.xml")
    
    logger.info("✅ Wizard files validated")
    
    # Summary
    logger.info("=" * 80)
    logger.info("📊 MODULE STRUCTURE VALIDATION SUMMARY")
    logger.info("=" * 80)
    
    if not issues_found:
        logger.info("🎉 ALL STRUCTURE VALIDATION TESTS PASSED!")
        logger.info("✅ Module structure appears to be complete and correct")
        logger.info("🔧 Module should install and function properly")
        return True
    else:
        logger.error(f"❌ Found {len(issues_found)} structural issues:")
        for issue in issues_found:
            logger.error(f"  • {issue}")
        logger.error("🔧 Please fix these issues for proper module functionality")
        return False

if __name__ == "__main__":
    import sys
    try:
        success = validate_module_structure()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error("Validation failed: %s", e)
        sys.exit(1)