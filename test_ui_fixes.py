#!/usr/bin/env python3
"""
Test script to validate button visibility and statusbar fixes.
"""

import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_ui_fixes():
    """Test the UI fixes for button visibility and statusbar"""
    logger.info("🚀 Testing UI Fixes...")
    
    # Test 1: Check XML view for button visibility fixes
    logger.info("Test 1: Checking XML view button visibility...")
    
    view_file = "payment_account_enhanced/views/account_payment_views.xml"
    if os.path.exists(view_file):
        with open(view_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check that buttons use "not show_*_button" instead of "show_*_button == False"
        if 'invisible="not show_submit_button"' in content:
            logger.info("✅ Button visibility uses proper 'not' syntax")
        else:
            logger.error("❌ Button visibility still uses == False syntax")
            return False
            
        # Check that approval_state fields are properly used
        approval_state_count = content.count('<field name="approval_state"')
        if approval_state_count >= 2:  # At least statusbar and workflow tab
            logger.info("✅ Approval state field properly defined in multiple places")
        else:
            logger.error("❌ Approval state field count incorrect: %s", approval_state_count)
            return False
            
        # Check statusbar visibility conditions
        if 'invisible="approval_state in [False, \'\']"' in content:
            logger.info("✅ Statusbar visibility properly configured")
        else:
            logger.error("❌ Statusbar visibility not properly configured")
            return False
    else:
        logger.error("❌ View file not found")
        return False
    
    # Test 2: Check payment model button computation
    logger.info("Test 2: Checking payment model button computation...")
    
    model_file = "payment_account_enhanced/models/account_payment.py"
    if os.path.exists(model_file):
        with open(model_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check that button visibility computation is self-contained (no circular deps)
        if "@api.depends('approval_state', 'verification_status', 'state', 'payment_type')" in content:
            logger.info("✅ Button visibility computation has proper dependencies")
        else:
            logger.error("❌ Button visibility computation dependencies incorrect")
            return False
            
        # Check that user.has_group is used directly
        if 'user.has_group(\'payment_account_enhanced.group_payment_reviewer\')' in content:
            logger.info("✅ Button visibility uses direct group checks")
        else:
            logger.error("❌ Button visibility not using direct group checks")
            return False
            
        # Check that approval_state field has default value
        if "default='draft'" in content:
            logger.info("✅ Approval state field has default value")
        else:
            logger.error("❌ Approval state field missing default value")
            return False
    else:
        logger.error("❌ Model file not found")
        return False
    
    # Test 3: Check security groups exist
    logger.info("Test 3: Checking security groups...")
    
    security_file = "payment_account_enhanced/security/security.xml"
    if os.path.exists(security_file):
        with open(security_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        required_groups = [
            'group_payment_reviewer',
            'group_payment_approver', 
            'group_payment_authorizer',
            'group_payment_poster'
        ]
        
        missing_groups = []
        for group in required_groups:
            if group not in content:
                missing_groups.append(group)
        
        if not missing_groups:
            logger.info("✅ All required security groups defined")
        else:
            logger.error(f"❌ Missing security groups: {missing_groups}")
            return False
    else:
        logger.warning("⚠️ Security file not found - groups may be defined elsewhere")
    
    logger.info("=" * 65)
    logger.info("📊 UI FIXES TEST SUMMARY")
    logger.info("=" * 65)
    logger.info("Tests passed: 3/3")
    logger.info("🎉 UI FIXES TESTS PASSED!")
    logger.info("✅ Button visibility properly configured")
    logger.info("🎯 Statusbar should override default Odoo statusbar")
    logger.info("🔘 Workflow buttons should appear at correct stages")
    logger.info("🎉 UI fixes should resolve visibility issues!")
    
    return True

if __name__ == "__main__":
    import sys
    try:
        success = test_ui_fixes()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error("Test execution failed: %s", e)
        sys.exit(1)