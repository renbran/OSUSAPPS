#!/bin/bash
# Test script for Payment Email Automation System
# =============================================
# This script helps validate the email automation system is working correctly

# Print colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}          PAYMENT EMAIL AUTOMATION SYSTEM TEST              ${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""

# 1. Check model registration
echo -e "${YELLOW}1. Checking model registration...${NC}"
docker-compose exec odoo odoo shell -d odoo -c /etc/odoo/odoo.conf << EOF
import sys
try:
    reminder_model = env['payment.reminder.manager']
    print("\033[0;32m✓ Payment reminder model registered successfully\033[0m")
except Exception as e:
    print(f"\033[0;31m✗ Error: {str(e)}\033[0m")
    sys.exit(1)
EOF

echo ""

# 2. Check email templates
echo -e "${YELLOW}2. Checking email templates...${NC}"
docker-compose exec odoo odoo shell -d odoo -c /etc/odoo/odoo.conf << EOF
templates = [
    'payment_account_enhanced.mail_template_payment_submitted',
    'payment_account_enhanced.mail_template_payment_approved_authorization',
    'payment_account_enhanced.mail_template_payment_fully_approved',
    'payment_account_enhanced.mail_template_payment_rejected',
    'payment_account_enhanced.mail_template_payment_posted',
    'payment_account_enhanced.mail_template_approval_reminder',
    'payment_account_enhanced.mail_template_approval_escalation'
]

success = True
for template_xml_id in templates:
    try:
        template = env.ref(template_xml_id, raise_if_not_found=False)
        if template:
            print(f"\033[0;32m✓ Template found: {template.name}\033[0m")
        else:
            print(f"\033[0;31m✗ Template not found: {template_xml_id}\033[0m")
            success = False
    except Exception as e:
        print(f"\033[0;31m✗ Error checking template {template_xml_id}: {str(e)}\033[0m")
        success = False

if not success:
    import sys
    sys.exit(1)
EOF

echo ""

# 3. Check cron job
echo -e "${YELLOW}3. Checking cron job...${NC}"
docker-compose exec odoo odoo shell -d odoo -c /etc/odoo/odoo.conf << EOF
try:
    cron = env.ref('payment_account_enhanced.cron_payment_approval_reminders', raise_if_not_found=False)
    if cron:
        print(f"\033[0;32m✓ Cron job found: {cron.name}\033[0m")
        print(f"  - Active: {cron.active}")
        print(f"  - Interval: Every {cron.interval_number} {cron.interval_type}")
        print(f"  - Next run: {cron.nextcall}")
    else:
        print("\033[0;31m✗ Cron job not found\033[0m")
        import sys
        sys.exit(1)
except Exception as e:
    print(f"\033[0;31m✗ Error checking cron job: {str(e)}\033[0m")
    import sys
    sys.exit(1)
EOF

echo ""

# 4. Check helper methods on payment model
echo -e "${YELLOW}4. Checking helper methods on payment model...${NC}"
docker-compose exec odoo odoo shell -d odoo -c /etc/odoo/odoo.conf << EOF
try:
    # Find a payment to test with
    payment = env['account.payment'].search([], limit=1)
    if not payment:
        print("\033[0;31m✗ No payments found to test with\033[0m")
        import sys
        sys.exit(1)
        
    # Test helper methods
    print(f"Testing payment: {payment.name}")
    
    # Test _get_pending_approver_emails
    try:
        emails = payment._get_pending_approver_emails()
        print(f"\033[0;32m✓ _get_pending_approver_emails method works: {emails}\033[0m")
    except Exception as e:
        print(f"\033[0;31m✗ Error with _get_pending_approver_emails: {str(e)}\033[0m")
    
    # Test _get_current_approver_name
    try:
        name = payment._get_current_approver_name()
        print(f"\033[0;32m✓ _get_current_approver_name method works: {name}\033[0m")
    except Exception as e:
        print(f"\033[0;31m✗ Error with _get_current_approver_name: {str(e)}\033[0m")
        
except Exception as e:
    print(f"\033[0;31m✗ Error checking helper methods: {str(e)}\033[0m")
    import sys
    sys.exit(1)
EOF

echo ""

# 5. Manually run reminder system once
echo -e "${YELLOW}5. Running reminder system manually...${NC}"
docker-compose exec odoo odoo shell -d odoo -c /etc/odoo/odoo.conf << EOF
try:
    reminder_manager = env['payment.reminder.manager']
    print("Sending payment reminders...")
    reminder_manager.send_approval_reminders()
    print("\033[0;32m✓ Reminder system executed successfully\033[0m")
except Exception as e:
    print(f"\033[0;31m✗ Error running reminder system: {str(e)}\033[0m")
    import sys
    sys.exit(1)
EOF

echo ""

# 6. Check recently sent emails
echo -e "${YELLOW}6. Checking recently sent emails...${NC}"
docker-compose exec odoo odoo shell -d odoo -c /etc/odoo/odoo.conf << EOF
# Check recently sent emails
recent_emails = env['mail.mail'].search([
    ('model', '=', 'account.payment'),
    ('create_date', '>=', (env.cr.now() - datetime.timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S'))
], order='create_date desc', limit=10)

if recent_emails:
    print("\033[0;32m✓ Recent emails found:\033[0m")
    for email in recent_emails:
        print(f"  - Subject: {email.subject}")
        print(f"    To: {email.email_to}")
        print(f"    Sent: {email.create_date}")
        print(f"    State: {email.state}")
        print("    ---")
else:
    print("\033[0;33m! No recent emails found in the last hour\033[0m")
EOF

echo ""
echo -e "${BLUE}============================================================${NC}"
echo -e "${GREEN}✓ EMAIL AUTOMATION SYSTEM TEST COMPLETED${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Create a test payment and run it through approval workflow"
echo "2. Check that emails are sent at each stage"
echo "3. Verify cron job is scheduled and running"
echo "4. Check email templates for correct formatting"
echo ""
echo -e "${BLUE}For manual email testing, run these commands:${NC}"
echo -e "  ${GREEN}docker-compose exec odoo odoo shell -d odoo -c /etc/odoo/odoo.conf${NC}"
echo -e "  ${YELLOW}payment = env['account.payment'].browse([PAYMENT_ID])${NC}"
echo -e "  ${YELLOW}payment._send_workflow_email('payment_account_enhanced.mail_template_payment_submitted')${NC}"
echo ""
