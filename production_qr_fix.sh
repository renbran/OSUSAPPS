#!/bin/bash
# Production QR Code Fix Script
# For staging-erposus.com database

echo "🔧 PRODUCTION QR CODE FIX SCRIPT"
echo "Database: staging-erposus.com"
echo "Host: stagingosus.cloudpepper.site"
echo "=" * 50

echo ""
echo "Step 1: Update module to apply recursion fix..."
cd /var/odoo/staging-erposus.com && sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf --no-http --stop-after-init --update payment_account_enhanced

echo ""
echo "Step 2: Fix existing payments without QR codes..."

cat << 'EOF'
cd /var/odoo/staging-erposus.com && sudo -u odoo venv/bin/python3 src/odoo-bin shell -c odoo.conf << 'FIX_EOF'

print("🔧 FIXING EXISTING PAYMENTS WITHOUT QR CODES")
print("=" * 50)

# Find all payments without QR codes
payments_without_qr = env['account.payment'].search([
    ('qr_code', '=', False),
    ('voucher_number', '!=', False)
])

print(f"Found {len(payments_without_qr)} payments without QR codes")

fixed_count = 0
for payment in payments_without_qr:
    try:
        print(f"Processing Payment ID: {payment.id} ({payment.voucher_number})")
        
        # Step 1: Ensure access token (using write to avoid recursion)
        if not payment.access_token:
            access_token = payment._generate_access_token()
            payment.write({'access_token': access_token})
            print(f"  ✅ Generated access token: {access_token[:10]}...")
        else:
            print(f"  ✅ Access token exists: {payment.access_token[:10]}...")
        
        # Step 2: Force QR computation
        payment._compute_qr_code()
        
        if payment.qr_code:
            print(f"  ✅ QR code generated! Size: {len(payment.qr_code)} bytes")
            fixed_count += 1
        else:
            print(f"  ❌ QR code still missing")
            
    except Exception as e:
        print(f"  ❌ Error processing payment {payment.id}: {e}")

print(f"\n🎯 RESULTS: Fixed {fixed_count}/{len(payments_without_qr)} payments")

# Commit all changes
env.cr.commit()
print("✅ All changes committed to database")

# Test one payment to verify QR is working
if payments_without_qr:
    test_payment = payments_without_qr[0]
    test_payment_reloaded = env['account.payment'].browse(test_payment.id)
    print(f"\n🧪 TEST: Payment {test_payment.id} QR status: {'✅ WORKING' if test_payment_reloaded.qr_code else '❌ STILL BROKEN'}")

FIX_EOF
EOF

echo ""
echo "Step 3: Verify a specific payment manually..."

cat << 'EOF'
cd /var/odoo/staging-erposus.com && sudo -u odoo venv/bin/python3 src/odoo-bin shell -c odoo.conf << 'VERIFY_EOF'

print("🧪 MANUAL VERIFICATION TEST")
print("=" * 30)

# Get the first payment
payment = env['account.payment'].search([], limit=1)
if payment:
    print(f"Testing Payment ID: {payment.id}")
    print(f"  Voucher: {payment.voucher_number}")
    print(f"  Access Token: {'YES' if payment.access_token else 'NO'}")
    print(f"  QR Code: {'YES' if payment.qr_code else 'NO'}")
    
    if payment.qr_code:
        print(f"  QR Size: {len(payment.qr_code)} bytes")
        
        # Test the verification URL
        base_url = env['ir.config_parameter'].sudo().get_param('web.base.url')
        verification_url = f"{base_url}/payment/verify/{payment.access_token}"
        print(f"  Verification URL: {verification_url}")
    
    # Try the new safe method
    try:
        payment.action_ensure_access_token_and_qr()
        print("  ✅ Safe QR generation method worked")
    except Exception as e:
        print(f"  ❌ Safe method failed: {e}")

VERIFY_EOF
EOF

echo ""
echo "📋 COMMANDS READY TO COPY-PASTE ABOVE"
echo "Run each step to fix the recursion issue and generate QR codes"
