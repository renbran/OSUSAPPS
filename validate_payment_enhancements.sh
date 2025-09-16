#!/bin/bash
# PAYMENT SYSTEM ENHANCEMENT VALIDATION SCRIPT
# ============================================
# This script performs comprehensive validation of all enhanced features

echo "====================================================="
echo "    PAYMENT SYSTEM ENHANCEMENT VALIDATION SCRIPT     "
echo "====================================================="

# Define colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create validation results file
RESULTS_FILE="validation_results.txt"
echo "PAYMENT SYSTEM ENHANCEMENT VALIDATION RESULTS" > $RESULTS_FILE
echo "Date: $(date)" >> $RESULTS_FILE
echo "----------------------------------------" >> $RESULTS_FILE

# 1. Test Email Templates
echo -e "${BLUE}1. Testing Email Templates...${NC}"
echo "1. EMAIL TEMPLATES VALIDATION" >> $RESULTS_FILE

docker-compose exec odoo odoo shell -d odoo -c /etc/odoo/odoo.conf << EOF >> $RESULTS_FILE 2>&1
templates = [
    'payment_account_enhanced.mail_template_payment_submitted',
    'payment_account_enhanced.mail_template_payment_approved_authorization',
    'payment_account_enhanced.mail_template_payment_fully_approved',
    'payment_account_enhanced.mail_template_payment_rejected',
    'payment_account_enhanced.mail_template_payment_posted',
    'payment_account_enhanced.mail_template_approval_reminder',
    'payment_account_enhanced.mail_template_approval_escalation'
]

print("\nEMAIL TEMPLATES:")
success = True
for template_xml_id in templates:
    try:
        template = env.ref(template_xml_id, raise_if_not_found=False)
        if template:
            print(f"✓ Found: {template.name}")
        else:
            print(f"✗ Missing: {template_xml_id}")
            success = False
    except Exception as e:
        print(f"✗ Error with {template_xml_id}: {str(e)}")
        success = False

if success:
    print("\n✓ All email templates correctly registered")
else:
    print("\n✗ Some email templates are missing")
EOF

# 2. Test Reminder System
echo -e "${BLUE}2. Testing Reminder System...${NC}"
echo -e "\n2. REMINDER SYSTEM VALIDATION" >> $RESULTS_FILE

docker-compose exec odoo odoo shell -d odoo -c /etc/odoo/odoo.conf << EOF >> $RESULTS_FILE 2>&1
print("\nREMINDER SYSTEM:")

# Check model existence
reminder_model = env.registry.get('payment.reminder.manager')
if reminder_model:
    print("✓ Payment reminder model exists")
else:
    print("✗ Payment reminder model does not exist")

# Check cron job
try:
    cron = env.ref('payment_account_enhanced.cron_payment_approval_reminders', raise_if_not_found=False)
    if cron:
        print(f"✓ Cron job exists: {cron.name}")
        print(f"  - Active: {cron.active}")
        print(f"  - Interval: Every {cron.interval_number} {cron.interval_type}")
        print(f"  - Next execution: {cron.nextcall}")
    else:
        print("✗ Reminder cron job not found")
except Exception as e:
    print(f"✗ Error checking cron job: {str(e)}")

# Try running reminder system
try:
    reminder_manager = env['payment.reminder.manager']
    print("\nAttempting to run reminder system...")
    reminder_manager.send_approval_reminders()
    print("✓ Reminder system executed successfully")
except Exception as e:
    print(f"✗ Error running reminder system: {str(e)}")
EOF

# 3. Test PDF Generation
echo -e "${BLUE}3. Testing PDF Generation...${NC}"
echo -e "\n3. PDF GENERATION VALIDATION" >> $RESULTS_FILE

docker-compose exec odoo odoo shell -d odoo -c /etc/odoo/odoo.conf << EOF >> $RESULTS_FILE 2>&1
print("\nPDF ERROR HANDLING:")

# Check model existence
model = env.registry.get('ir.actions.report')
if not model:
    print("✗ Report model not found")
    exit(1)

# Check method override
from odoo.addons.payment_account_enhanced.models.fix_pdf_error import FixPDFError
if hasattr(FixPDFError, '_render_qweb_pdf'):
    print("✓ PDF error handling override exists")
else:
    print("✗ PDF error handling override not found")

# Check config parameter
param = env['ir.config_parameter'].sudo().get_param('report.url_wkhtmltopdf_args', False)
if param and 'load-error-handling ignore' in param:
    print(f"✓ wkhtmltopdf args configured: {param}")
else:
    print(f"✗ wkhtmltopdf args not properly configured: {param}")

# Test PDF generation with a payment report
try:
    payment = env['account.payment'].search([], limit=1)
    if not payment:
        print("✗ No payments found to test report generation")
    else:
        print(f"Testing report generation for payment {payment.name}...")
        report = env.ref('payment_account_enhanced.action_report_payment_voucher')
        pdf, _ = report._render_qweb_pdf([payment.id])
        if pdf and len(pdf) > 100:  # Simple size check
            print(f"✓ PDF generated successfully ({len(pdf)} bytes)")
        else:
            print(f"✗ PDF generation failed or empty ({len(pdf) if pdf else 0} bytes)")
except Exception as e:
    print(f"✗ Error testing PDF generation: {str(e)}")
EOF

# 4. Test Email Automation
echo -e "${BLUE}4. Testing Email Automation...${NC}"
echo -e "\n4. EMAIL AUTOMATION VALIDATION" >> $RESULTS_FILE

docker-compose exec odoo odoo shell -d odoo -c /etc/odoo/odoo.conf << EOF >> $RESULTS_FILE 2>&1
print("\nEMAIL AUTOMATION:")

# Find a payment to test with
payment = env['account.payment'].search([], limit=1)
if not payment:
    print("✗ No payments found to test email automation")
    exit(1)

# Check email helper methods
try:
    print(f"Testing helper methods on payment {payment.name}...")
    
    # Test _get_pending_approver_emails
    if hasattr(payment, '_get_pending_approver_emails'):
        emails = payment._get_pending_approver_emails()
        print(f"✓ _get_pending_approver_emails method works: {emails}")
    else:
        print("✗ _get_pending_approver_emails method not found")
    
    # Test _get_current_approver_name
    if hasattr(payment, '_get_current_approver_name'):
        name = payment._get_current_approver_name()
        print(f"✓ _get_current_approver_name method works: {name}")
    else:
        print("✗ _get_current_approver_name method not found")
        
    # Test _send_workflow_email
    if hasattr(payment, '_send_workflow_email'):
        # Just test if the method exists, don't actually send email
        print(f"✓ _send_workflow_email method exists")
    else:
        print("✗ _send_workflow_email method not found")
    
except Exception as e:
    print(f"✗ Error testing helper methods: {str(e)}")

# Check if email methods are integrated in workflow actions
workflow_actions = [
    'action_submit_for_review',
    'action_review_payment',
    'action_approve_payment',
    'action_authorize_payment',
    'action_reject_payment',
    'action_post'
]

print("\nChecking workflow email integration:")
payment_model = env['account.payment']
for action in workflow_actions:
    if hasattr(payment_model, action):
        # Check if the method contains _send_workflow_email
        method = getattr(type(payment_model), action)
        method_code = method.__code__.co_consts
        
        # Simple check for _send_workflow_email string in method constants
        email_integration = False
        for const in method_code:
            if isinstance(const, str) and '_send_workflow_email' in const:
                email_integration = True
                break
        
        if email_integration:
            print(f"✓ {action} has email integration")
        else:
            # Check function source as backup
            import inspect
            source = inspect.getsource(method)
            if '_send_workflow_email' in source:
                print(f"✓ {action} has email integration")
            else:
                print(f"✗ {action} missing email integration")
    else:
        print(f"✗ {action} method not found")
EOF

# 5. Summary
echo -e "${BLUE}5. Generating Summary...${NC}"

# Count successes and failures
SUCCESSES=$(grep -c "✓" $RESULTS_FILE)
FAILURES=$(grep -c "✗" $RESULTS_FILE)

echo -e "\n-----------------------------------------" >> $RESULTS_FILE
echo "VALIDATION SUMMARY:" >> $RESULTS_FILE
echo "- Successful checks: $SUCCESSES" >> $RESULTS_FILE
echo "- Failed checks: $FAILURES" >> $RESULTS_FILE

if [ $FAILURES -eq 0 ]; then
    echo -e "✅ ${GREEN}ALL SYSTEMS OPERATIONAL${NC}" >> $RESULTS_FILE
    echo -e "The payment system enhancements are working correctly." >> $RESULTS_FILE
else
    echo -e "⚠️ ${RED}SOME CHECKS FAILED${NC}" >> $RESULTS_FILE
    echo -e "Please review the failures above." >> $RESULTS_FILE
fi

echo -e "\n====================================================="
echo -e "${GREEN}Validation complete!${NC}"
echo -e "Results saved to ${YELLOW}validation_results.txt${NC}"
echo -e "====================================================="

# Print summary to console
echo -e "${BLUE}VALIDATION SUMMARY:${NC}"
echo -e "${GREEN}Successful checks:${NC} $SUCCESSES"
echo -e "${RED}Failed checks:${NC} $FAILURES"

if [ $FAILURES -eq 0 ]; then
    echo -e "${GREEN}ALL SYSTEMS OPERATIONAL${NC}"
    echo -e "The payment system enhancements are working correctly."
else
    echo -e "${RED}SOME CHECKS FAILED${NC}"
    echo -e "Please review ${YELLOW}validation_results.txt${NC} for details."
fi
