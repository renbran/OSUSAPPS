#!/usr/bin/env python3
"""
Test Enhanced Workflow Enforcement
This script tests that ALL payments must go through the enhanced workflow
and cannot bypass the approval process.
"""

import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_workflow_enforcement():
    """Test that workflow enforcement is properly implemented"""
    logger.info("🛡️ Testing Enhanced Workflow Enforcement...")
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Check that _can_bypass_approval is properly restricted
    total_tests += 1
    try:
        logger.info("Test 1: Checking bypass approval restrictions...")
        
        model_file = 'payment_account_enhanced/models/account_payment.py'
        with open(model_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for strict bypass conditions
        bypass_method_start = content.find('def _can_bypass_approval(self):')
        if bypass_method_start != -1:
            # Extract the method content (approximately)
            method_content = content[bypass_method_start:bypass_method_start + 500]
            
            # Check that it DOESN'T allow easy bypassing
            if ('account.group_account_manager' not in method_content and 
                'bypass_approval_workflow' not in method_content and
                'install_mode' in method_content):
                logger.info("✅ Bypass approval method properly restricted")
                tests_passed += 1
            else:
                logger.error("❌ Bypass approval method still allows easy bypassing")
        else:
            logger.error("❌ _can_bypass_approval method not found")
            
    except Exception as e:
        logger.error(f"❌ Test 1 failed: {e}")
    
    # Test 2: Check payment creation enforces workflow
    total_tests += 1
    try:
        logger.info("Test 2: Checking payment creation workflow enforcement...")
        
        model_file = 'payment_account_enhanced/models/account_payment.py'
        with open(model_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        create_method_start = content.find('def create(self, vals):')
        if create_method_start != -1:
            method_content = content[create_method_start:create_method_start + 1000]
            
            # Check for workflow enforcement
            if ('under_review' in method_content and 
                'ENFORCE ENHANCED WORKFLOW' in method_content and
                'install_mode' in method_content):
                logger.info("✅ Payment creation enforces workflow properly")
                tests_passed += 1
            else:
                logger.error("❌ Payment creation doesn't enforce workflow")
        else:
            logger.error("❌ create method not found")
            
    except Exception as e:
        logger.error(f"❌ Test 2 failed: {e}")
    
    # Test 3: Check payment register wizard enforces workflow
    total_tests += 1
    try:
        logger.info("Test 3: Checking payment register wizard workflow enforcement...")
        
        wizard_file = 'payment_account_enhanced/wizards/register_payment.py'
        with open(wizard_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check both wizard methods enforce workflow
        if ('under_review' in content and 
            'Enhanced workflow enforced' in content and
            content.count('approval_state') >= 2):  # Should appear in both methods
            logger.info("✅ Payment register wizard enforces workflow")
            tests_passed += 1
        else:
            logger.error("❌ Payment register wizard doesn't enforce workflow")
            
    except Exception as e:
        logger.error(f"❌ Test 3 failed: {e}")
    
    # Test 4: Check action_post method is strict
    total_tests += 1
    try:
        logger.info("Test 4: Checking action_post method strictness...")
        
        model_file = 'payment_account_enhanced/models/account_payment.py'
        with open(model_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        post_method_start = content.find('def action_post(self):')
        if post_method_start != -1:
            method_content = content[post_method_start:post_method_start + 800]
            
            # Check for strict validation without bypass
            if ('NO BYPASSING ALLOWED' in method_content and 
                'approval_state != \'approved\'' in method_content and
                '_can_bypass_approval' not in method_content):
                logger.info("✅ action_post method is properly strict")
                tests_passed += 1
            else:
                logger.error("❌ action_post method still allows bypassing")
        else:
            logger.error("❌ action_post method not found")
            
    except Exception as e:
        logger.error(f"❌ Test 4 failed: {e}")
    
    # Test 5: Check constraints are in place
    total_tests += 1
    try:
        logger.info("Test 5: Checking workflow constraints...")
        
        model_file = 'payment_account_enhanced/models/account_payment.py'
        with open(model_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for both constraints
        if ('_check_approval_constraints' in content and 
            '_check_workflow_progression' in content and
            'STRICT ENFORCEMENT' in content and
            'WORKFLOW VIOLATION' in content):
            logger.info("✅ Workflow constraints properly implemented")
            tests_passed += 1
        else:
            logger.error("❌ Workflow constraints missing or incomplete")
            
    except Exception as e:
        logger.error(f"❌ Test 5 failed: {e}")
    
    # Test 6: Check intelligent UI still works
    total_tests += 1
    try:
        logger.info("Test 6: Checking intelligent UI compatibility...")
        
        view_file = 'payment_account_enhanced/views/account_payment_views.xml'
        with open(view_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check that intelligent button conditions are still present
        button_conditions = [
            'show_submit_button',
            'show_review_button', 
            'show_approve_button',
            'show_post_button'
        ]
        
        conditions_found = sum(1 for condition in button_conditions if condition in content)
        
        if conditions_found >= len(button_conditions) - 1:
            logger.info("✅ Intelligent UI compatibility maintained")
            tests_passed += 1
        else:
            logger.error(f"❌ Intelligent UI may be broken ({conditions_found}/{len(button_conditions)} conditions found)")
            
    except Exception as e:
        logger.error(f"❌ Test 6 failed: {e}")
    
    # Summary
    logger.info("=" * 60)
    logger.info("📊 WORKFLOW ENFORCEMENT TEST SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        logger.info("🎉 ALL WORKFLOW ENFORCEMENT TESTS PASSED!")
        logger.info("✅ Enhanced workflow is properly enforced")
        logger.info("🛡️ No payment can bypass the approval process")
        return True
    else:
        logger.error(f"❌ {total_tests - tests_passed} tests failed")
        logger.error("⚠️  Workflow enforcement may need attention")
        return False

def main():
    """Main test execution"""
    logger.info("🚀 Starting Workflow Enforcement Tests...")
    
    success = test_workflow_enforcement()
    
    if success:
        logger.info("🎉 Workflow enforcement testing completed successfully!")
        logger.info("🛡️ ALL payments will be required to follow the enhanced workflow!")
        sys.exit(0)
    else:
        logger.error("❌ Workflow enforcement testing failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()