#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Script for Payment Email Automation System
==============================================

This script provides a comprehensive test suite to validate the payment
email automation system. It includes tests for all workflow emails,
reminder emails, and email helper functions.

Usage:
------
Execute this script within the Odoo shell:
python odoo-bin shell -c /etc/odoo/odoo.conf -d database_name < test_payment_email_system.py

Or run from Odoo shell:
exec(open('test_payment_email_system.py').read())
"""

import logging
import time
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

def color_print(message, color='white'):
    """Print colored text"""
    colors = {
        'green': '\033[92m',
        'yellow': '\033[93m',
        'red': '\033[91m',
        'blue': '\033[94m',
        'purple': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'bold': '\033[1m',
        'underline': '\033[4m',
        'end': '\033[0m'
    }
    
    print(f"{colors.get(color, colors['white'])}{message}{colors['end']}")

def run_test():
    """Run all email automation tests"""
    color_print("\n" + "="*80, 'bold')
    color_print(" PAYMENT EMAIL AUTOMATION SYSTEM TEST", 'bold')
    color_print("="*80 + "\n", 'bold')
    
    env = self.env
    
    # Get test data
    test_payment = _get_test_payment(env)
    if not test_payment:
        color_print("✘ ERROR: No test payment found. Create a payment first.", 'red')
        return False
    
    color_print(f"✓ Using test payment: {test_payment.voucher_number or test_payment.name}", 'green')
    
    # Run tests
    _test_helper_methods(env, test_payment)
    _test_workflow_emails(env, test_payment)
    _test_reminder_system(env, test_payment)
    
    # Summary
    color_print("\n" + "="*80, 'bold')
    color_print(" TEST SUMMARY", 'bold')
    color_print("="*80, 'bold')
    
    if all([
        test_results['helper_methods'],
        test_results['workflow_emails'],
        test_results['reminder_system']
    ]):
        color_print("✓ ALL TESTS PASSED!", 'green')
        color_print("The email automation system is functioning correctly.", 'green')
    else:
        color_print("✘ SOME TESTS FAILED", 'red')
        color_print("Please review the test results above and fix any issues.", 'red')
    
    color_print("\nNote: Check the mail.mail model for sent emails.", 'yellow')
    color_print("      Settings > Technical > Emails > Emails\n", 'yellow')

def _get_test_payment(env):
    """Get or create a test payment"""
    # Try to find an existing draft payment
    payment = env['account.payment'].search([
        ('state', '=', 'draft'),
        ('approval_state', '=', 'draft')
    ], limit=1)
    
    if payment:
        return payment
    
    # Find all payments
    payments = env['account.payment'].search([], limit=1)
    if payments:
        return payments[0]
    
    return None

def _test_helper_methods(env, test_payment):
    """Test email helper methods"""
    color_print("\n" + "-"*80, 'bold')
    color_print(" TESTING EMAIL HELPER METHODS", 'bold')
    color_print("-"*80, 'bold')
    
    success = True
    
    # Test _get_pending_approver_emails
    try:
        color_print("\nTesting _get_pending_approver_emails()...", 'cyan')
        emails = test_payment._get_pending_approver_emails()
        color_print(f"✓ Got approver emails: {emails}", 'green')
    except Exception as e:
        color_print(f"✘ Error getting approver emails: {str(e)}", 'red')
        success = False
    
    # Test _get_current_approver_name
    try:
        color_print("\nTesting _get_current_approver_name()...", 'cyan')
        approver_name = test_payment._get_current_approver_name()
        color_print(f"✓ Got approver name: {approver_name}", 'green')
    except Exception as e:
        color_print(f"✘ Error getting approver name: {str(e)}", 'red')
        success = False
    
    # Test _send_workflow_email
    try:
        color_print("\nTesting _send_workflow_email()...", 'cyan')
        # Use a test template
        test_payment._send_workflow_email('payment_account_enhanced.mail_template_payment_submitted', ['test@example.com'])
        color_print(f"✓ Test email sent successfully", 'green')
    except Exception as e:
        color_print(f"✘ Error sending test email: {str(e)}", 'red')
        success = False
    
    test_results['helper_methods'] = success
    if success:
        color_print("\n✓ All helper methods tests PASSED", 'green')
    else:
        color_print("\n✘ Some helper methods tests FAILED", 'red')
    
    return success

def _test_workflow_emails(env, test_payment):
    """Test workflow email automation"""
    color_print("\n" + "-"*80, 'bold')
    color_print(" TESTING WORKFLOW EMAILS", 'bold')
    color_print("-"*80, 'bold')
    
    success = True
    
    # Get initial state
    original_state = test_payment.approval_state
    original_state_name = original_state.replace('_', ' ').title()
    color_print(f"\nInitial payment state: {original_state_name}", 'cyan')
    
    # Test submit for review email
    if test_payment.approval_state == 'draft':
        try:
            color_print("\nTesting action_submit_for_review() email...", 'cyan')
            
            # Count emails before
            email_count_before = env['mail.mail'].search_count([
                ('model', '=', 'account.payment'),
                ('res_id', '=', test_payment.id),
                ('subject', 'ilike', 'Submitted for Review')
            ])
            
            # Submit for review
            test_payment.action_submit_for_review()
            
            # Count emails after
            email_count_after = env['mail.mail'].search_count([
                ('model', '=', 'account.payment'),
                ('res_id', '=', test_payment.id),
                ('subject', 'ilike', 'Submitted for Review')
            ])
            
            if email_count_after > email_count_before:
                color_print(f"✓ Submit for review email sent", 'green')
            else:
                color_print(f"✘ Submit for review email not sent", 'red')
                success = False
                
        except Exception as e:
            color_print(f"✘ Error testing submit for review: {str(e)}", 'red')
            success = False
    else:
        color_print(f"ℹ Skipping submit for review test (payment state: {original_state_name})", 'yellow')
    
    # Test review payment email
    if test_payment.approval_state == 'under_review':
        try:
            color_print("\nTesting action_review_payment() email...", 'cyan')
            
            # Count emails before
            email_count_before = env['mail.mail'].search_count([
                ('model', '=', 'account.payment'),
                ('res_id', '=', test_payment.id),
                ('subject', 'ilike', 'Authorization Required')
            ])
            
            # Review payment
            test_payment.action_review_payment()
            
            # Count emails after
            email_count_after = env['mail.mail'].search_count([
                ('model', '=', 'account.payment'),
                ('res_id', '=', test_payment.id),
                ('subject', 'ilike', 'Authorization Required')
            ])
            
            if email_count_after > email_count_before:
                color_print(f"✓ Review payment email sent", 'green')
            else:
                color_print(f"✘ Review payment email not sent", 'red')
                success = False
                
        except Exception as e:
            color_print(f"✘ Error testing review payment: {str(e)}", 'red')
            success = False
    else:
        color_print(f"ℹ Skipping review payment test (payment state: {test_payment.approval_state})", 'yellow')
    
    # Test approve payment email
    if test_payment.approval_state == 'for_approval':
        try:
            color_print("\nTesting action_approve_payment() email...", 'cyan')
            
            # Count emails before
            email_count_before = env['mail.mail'].search_count([
                ('model', '=', 'account.payment'),
                ('res_id', '=', test_payment.id),
                ('subject', 'ilike', 'Authorization Required')
            ])
            
            # Approve payment
            test_payment.action_approve_payment()
            
            # Count emails after
            email_count_after = env['mail.mail'].search_count([
                ('model', '=', 'account.payment'),
                ('res_id', '=', test_payment.id),
                ('subject', 'ilike', 'Authorization Required')
            ])
            
            if email_count_after > email_count_before:
                color_print(f"✓ Approve payment email sent", 'green')
            else:
                color_print(f"✘ Approve payment email not sent", 'red')
                success = False
                
        except Exception as e:
            color_print(f"✘ Error testing approve payment: {str(e)}", 'red')
            success = False
    else:
        color_print(f"ℹ Skipping approve payment test (payment state: {test_payment.approval_state})", 'yellow')
    
    # Test authorize payment email
    if test_payment.approval_state == 'for_authorization':
        try:
            color_print("\nTesting action_authorize_payment() email...", 'cyan')
            
            # Count emails before
            email_count_before = env['mail.mail'].search_count([
                ('model', '=', 'account.payment'),
                ('res_id', '=', test_payment.id),
                ('subject', 'ilike', 'Fully Approved')
            ])
            
            # Authorize payment
            test_payment.action_authorize_payment()
            
            # Count emails after
            email_count_after = env['mail.mail'].search_count([
                ('model', '=', 'account.payment'),
                ('res_id', '=', test_payment.id),
                ('subject', 'ilike', 'Fully Approved')
            ])
            
            if email_count_after > email_count_before:
                color_print(f"✓ Authorize payment email sent", 'green')
            else:
                color_print(f"✘ Authorize payment email not sent", 'red')
                success = False
                
        except Exception as e:
            color_print(f"✘ Error testing authorize payment: {str(e)}", 'red')
            success = False
    else:
        color_print(f"ℹ Skipping authorize payment test (payment state: {test_payment.approval_state})", 'yellow')
    
    # Test reject payment email
    if test_payment.approval_state in ['under_review', 'for_approval', 'for_authorization']:
        try:
            color_print("\nTesting action_reject_payment() email...", 'cyan')
            
            # Count emails before
            email_count_before = env['mail.mail'].search_count([
                ('model', '=', 'account.payment'),
                ('res_id', '=', test_payment.id),
                ('subject', 'ilike', 'Rejected')
            ])
            
            # Reject payment
            test_payment.action_reject_payment()
            
            # Count emails after
            email_count_after = env['mail.mail'].search_count([
                ('model', '=', 'account.payment'),
                ('res_id', '=', test_payment.id),
                ('subject', 'ilike', 'Rejected')
            ])
            
            if email_count_after > email_count_before:
                color_print(f"✓ Reject payment email sent", 'green')
            else:
                color_print(f"✘ Reject payment email not sent", 'red')
                success = False
                
        except Exception as e:
            color_print(f"✘ Error testing reject payment: {str(e)}", 'red')
            success = False
    else:
        color_print(f"ℹ Skipping reject payment test (payment state: {test_payment.approval_state})", 'yellow')
    
    # Reset payment to original state
    try:
        color_print(f"\nResetting payment to original state: {original_state_name}...", 'cyan')
        test_payment.write({'approval_state': original_state})
        color_print(f"✓ Payment reset to {original_state_name}", 'green')
    except Exception as e:
        color_print(f"✘ Error resetting payment state: {str(e)}", 'red')
    
    test_results['workflow_emails'] = success
    if success:
        color_print("\n✓ All workflow email tests PASSED", 'green')
    else:
        color_print("\n✘ Some workflow email tests FAILED", 'red')
    
    return success

def _test_reminder_system(env, test_payment):
    """Test reminder system"""
    color_print("\n" + "-"*80, 'bold')
    color_print(" TESTING REMINDER SYSTEM", 'bold')
    color_print("-"*80, 'bold')
    
    success = True
    
    # Test reminder manager
    try:
        color_print("\nTesting PaymentReminderManager.send_approval_reminders()...", 'cyan')
        reminder_manager = env['payment.reminder.manager']
        if not reminder_manager:
            color_print(f"✘ PaymentReminderManager model not found", 'red')
            return False
        
        # Run reminder method
        reminder_manager.send_approval_reminders()
        color_print(f"✓ Reminder system executed successfully", 'green')
    except Exception as e:
        color_print(f"✘ Error testing reminder system: {str(e)}", 'red')
        success = False
    
    # Check cron job
    try:
        color_print("\nChecking reminder cron job...", 'cyan')
        cron_job = env.ref('payment_account_enhanced.cron_payment_approval_reminders', raise_if_not_found=False)
        
        if cron_job:
            color_print(f"✓ Cron job found: {cron_job.name}", 'green')
            color_print(f"  - Active: {cron_job.active}", 'blue')
            color_print(f"  - Interval: Every {cron_job.interval_number} {cron_job.interval_type}", 'blue')
            color_print(f"  - Next execution: {cron_job.nextcall}", 'blue')
        else:
            color_print(f"✘ Cron job not found", 'red')
            success = False
    except Exception as e:
        color_print(f"✘ Error checking cron job: {str(e)}", 'red')
        success = False
    
    # Check templates
    try:
        color_print("\nChecking reminder email templates...", 'cyan')
        reminder_template = env.ref('payment_account_enhanced.mail_template_approval_reminder', raise_if_not_found=False)
        escalation_template = env.ref('payment_account_enhanced.mail_template_approval_escalation', raise_if_not_found=False)
        
        if reminder_template:
            color_print(f"✓ Reminder template found: {reminder_template.name}", 'green')
        else:
            color_print(f"✘ Reminder template not found", 'red')
            success = False
            
        if escalation_template:
            color_print(f"✓ Escalation template found: {escalation_template.name}", 'green')
        else:
            color_print(f"✘ Escalation template not found", 'red')
            success = False
    except Exception as e:
        color_print(f"✘ Error checking email templates: {str(e)}", 'red')
        success = False
    
    test_results['reminder_system'] = success
    if success:
        color_print("\n✓ All reminder system tests PASSED", 'green')
    else:
        color_print("\n✘ Some reminder system tests FAILED", 'red')
    
    return success

# Initialize test results
test_results = {
    'helper_methods': False,
    'workflow_emails': False,
    'reminder_system': False
}

# Run tests
run_test()
