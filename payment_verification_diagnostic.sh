#!/bin/bash
# Diagnostic script for payment verification landing page error

echo "🔍 PAYMENT VERIFICATION LANDING PAGE DIAGNOSTIC"
echo "=" * 50

cat << 'EOF'
# Step 1: Test controller routing
cd /var/odoo/staging-erposus.com && sudo -u odoo venv/bin/python3 src/odoo-bin shell -c odoo.conf << 'TEST_EOF'

print("🔧 TESTING PAYMENT VERIFICATION CONTROLLER")
print("=" * 40)

# Test if website module is installed
website_module = env['ir.module.module'].search([('name', '=', 'website')])
if website_module and website_module.state == 'installed':
    print("✅ Website module: INSTALLED")
else:
    print("❌ Website module: NOT INSTALLED or BROKEN")

# Test if portal module is installed  
portal_module = env['ir.module.module'].search([('name', '=', 'portal')])
if portal_module and portal_module.state == 'installed':
    print("✅ Portal module: INSTALLED")
else:
    print("❌ Portal module: NOT INSTALLED or BROKEN")

# Check if payment_account_enhanced is properly installed
payment_module = env['ir.module.module'].search([('name', '=', 'payment_account_enhanced')])
if payment_module and payment_module.state == 'installed':
    print("✅ Payment module: INSTALLED")
else:
    print("❌ Payment module: NOT INSTALLED or BROKEN")

# Test if payment.qr.verification model exists
try:
    qr_model = env['ir.model'].search([('model', '=', 'payment.qr.verification')])
    if qr_model:
        print("✅ QR Verification model: EXISTS")
    else:
        print("❌ QR Verification model: NOT FOUND")
except Exception as e:
    print(f"❌ QR Verification model error: {e}")

# Check if templates exist
try:
    success_template = env['ir.ui.view'].search([('key', '=', 'payment_account_enhanced.payment_verification_success')])
    if success_template:
        print("✅ Success template: EXISTS")
    else:
        print("❌ Success template: NOT FOUND")
        
    error_template = env['ir.ui.view'].search([('key', '=', 'payment_account_enhanced.payment_verification_error')])
    if error_template:
        print("✅ Error template: EXISTS")
    else:
        print("❌ Error template: NOT FOUND")
        
    not_found_template = env['ir.ui.view'].search([('key', '=', 'payment_account_enhanced.payment_not_found')])
    if not_found_template:
        print("✅ Not found template: EXISTS")
    else:
        print("❌ Not found template: NOT FOUND")
        
except Exception as e:
    print(f"❌ Template check error: {e}")

# Get a test payment with access token
try:
    test_payment = env['account.payment'].search([
        ('access_token', '!=', False)
    ], limit=1)
    
    if test_payment:
        print(f"✅ Test payment found: {test_payment.voucher_number}")
        print(f"   Access token: {test_payment.access_token[:10]}...")
        print(f"   Verification URL: /payment/verify/{test_payment.access_token}")
    else:
        print("❌ No payment with access token found")
        
        # Check for any payment
        any_payment = env['account.payment'].search([], limit=1)
        if any_payment:
            print(f"   Found payment without token: {any_payment.voucher_number}")
        else:
            print("   No payments found at all")
            
except Exception as e:
    print(f"❌ Payment search error: {e}")

TEST_EOF
EOF

echo ""
echo "Step 2: Test simple verification URL"

cat << 'EOF'
# Test basic controller endpoint
curl -i http://localhost:8069/payment/test
# or
curl -i https://stagingosus.cloudpepper.site/payment/test

# Test with actual access token (replace with real token)
curl -i http://localhost:8069/payment/verify/TEST_TOKEN
# or  
curl -i https://stagingosus.cloudpepper.site/payment/verify/TEST_TOKEN
EOF

echo ""
echo "Step 3: Check Odoo logs for specific error"

cat << 'EOF'
# Check recent error logs
cd /var/odoo/staging-erposus.com
tail -50 odoo.log | grep -i error
tail -50 odoo.log | grep -i verification
tail -50 odoo.log | grep -i "internal server"

# Or check system logs
journalctl -u odoo --since "1 hour ago" | grep -i error
EOF

echo ""
echo "📋 COPY-PASTE DIAGNOSTIC COMMANDS ABOVE"
echo "Run each step to identify the exact verification error"
