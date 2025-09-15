#!/bin/bash
# Production fix for payment verification landing page internal server error

echo "🔧 PAYMENT VERIFICATION LANDING PAGE FIX"
echo "Database: staging-erposus.com"
echo "Host: stagingosus.cloudpepper.site"
echo "=" * 50

echo ""
echo "Step 1: Update module with improved error handling..."
cd /var/odoo/staging-erposus.com && sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf --no-http --stop-after-init --update payment_account_enhanced

echo ""
echo "Step 2: Test simple debug endpoint..."

cat << 'EOF'
# Test the debug endpoint first
curl -i https://stagingosus.cloudpepper.site/payment/debug/test

# Expected response: 200 OK with payment count information
EOF

echo ""
echo "Step 3: Test simplified verification endpoint..."

cat << 'EOF'
# Get a test payment with access token
cd /var/odoo/staging-erposus.com && sudo -u odoo venv/bin/python3 src/odoo-bin shell -c odoo.conf << 'TOKEN_EOF'

# Find payment with access token
payment = env['account.payment'].search([('access_token', '!=', False)], limit=1)
if payment:
    print(f"Test URL: https://stagingosus.cloudpepper.site/payment/verify/simple/{payment.access_token}")
    print(f"Original URL: https://stagingosus.cloudpepper.site/payment/verify/{payment.access_token}")
else:
    print("No payment with access token found - generating one...")
    test_payment = env['account.payment'].search([], limit=1)
    if test_payment:
        test_payment.access_token = test_payment._generate_access_token()
        env.cr.commit()
        print(f"Generated token for payment {test_payment.id}")
        print(f"Test URL: https://stagingosus.cloudpepper.site/payment/verify/simple/{test_payment.access_token}")

TOKEN_EOF
EOF

echo ""
echo "Step 4: Check specific module dependencies..."

cat << 'EOF'
cd /var/odoo/staging-erposus.com && sudo -u odoo venv/bin/python3 src/odoo-bin shell -c odoo.conf << 'DEP_EOF'

print("🔍 CHECKING MODULE DEPENDENCIES")
print("=" * 30)

# Check website module
website_module = env['ir.module.module'].search([('name', '=', 'website')])
print(f"Website module: {website_module.state if website_module else 'NOT FOUND'}")

# Check portal module  
portal_module = env['ir.module.module'].search([('name', '=', 'portal')])
print(f"Portal module: {portal_module.state if portal_module else 'NOT FOUND'}")

# Check payment module
payment_module = env['ir.module.module'].search([('name', '=', 'payment_account_enhanced')])
print(f"Payment module: {payment_module.state if payment_module else 'NOT FOUND'}")

# Check if templates exist
try:
    templates = env['ir.ui.view'].search([('key', 'like', 'payment_account_enhanced.payment_%')])
    print(f"Found {len(templates)} payment templates")
    for template in templates:
        print(f"  - {template.key}")
except Exception as e:
    print(f"Template check error: {e}")

# Check QR verification model
try:
    qr_records = env['payment.qr.verification'].search_count([])
    print(f"QR verification records: {qr_records}")
except Exception as e:
    print(f"QR model error: {e}")

DEP_EOF
EOF

echo ""
echo "Step 5: Test original vs simplified endpoints side by side..."

cat << 'EOF'
# After getting the test URL from step 3, test both:

# Test simplified version (should work)
curl -i https://stagingosus.cloudpepper.site/payment/verify/simple/[ACCESS_TOKEN]

# Test original version (may have error)  
curl -i https://stagingosus.cloudpepper.site/payment/verify/[ACCESS_TOKEN]

# Compare responses to identify the issue
EOF

echo ""
echo "Step 6: Check Odoo error logs..."

cat << 'EOF'
# Check recent logs for verification errors
cd /var/odoo/staging-erposus.com
tail -100 odoo.log | grep -i verification
tail -100 odoo.log | grep -i "internal server"
tail -100 odoo.log | grep -A5 -B5 "payment.*verify"

# Check system logs
journalctl -u odoo --since "10 minutes ago" | grep -i error
EOF

echo ""
echo "📋 TROUBLESHOOTING STEPS"
echo "1. Update module (Step 1)"
echo "2. Test debug endpoint (Step 2)"  
echo "3. Get test URL (Step 3)"
echo "4. Check dependencies (Step 4)"
echo "5. Compare endpoints (Step 5)"
echo "6. Check logs (Step 6)"
echo ""
echo "If simplified version works but original fails, the issue is in the template rendering."
echo "If both fail, the issue is in the basic controller logic or dependencies."
