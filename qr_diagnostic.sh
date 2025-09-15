#!/bin/bash
# QR Code Generation Diagnostic Script for Payment Module

echo "🔍 QR CODE GENERATION DIAGNOSTIC"
echo "=" * 50

# Check if ingenuity module conflicts with our module
echo "📋 Checking for module conflicts..."

if [ -d "./ingenuity_invoice_qr_code" ]; then
    echo "⚠️  FOUND: ingenuity_invoice_qr_code module"
    echo "   This module might conflict with payment QR generation"
    echo "   Consider disabling it temporarily to test"
else
    echo "✅ No ingenuity module conflicts found"
fi

echo ""
echo "🧪 QR GENERATION TEST COMMANDS FOR PRODUCTION SERVER"
echo "=" * 50

cat << 'EOF'
# Test QR generation in Odoo shell
cd /var/odoo/staging-erposus.com && sudo -u odoo venv/bin/python3 src/odoo-bin shell -c odoo.conf << 'SHELL_EOF'

# Test 1: Check if qrcode library is available
try:
    import qrcode
    print("✅ qrcode library is available")
except ImportError as e:
    print(f"❌ qrcode library missing: {e}")

# Test 2: Test basic QR generation
try:
    import qrcode
    import base64
    from io import BytesIO
    
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=20, border=4)
    qr.add_data("https://stagingosus.cloudpepper.site/test")
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    qr_data = base64.b64encode(buffer.getvalue())
    
    print(f"✅ Basic QR generation works, size: {len(qr_data)} bytes")
except Exception as e:
    print(f"❌ Basic QR generation failed: {e}")

# Test 3: Check payment records and their QR codes
payments = env['account.payment'].search([('voucher_number', '!=', False)], limit=5)
print(f"Found {len(payments)} payments with voucher numbers")

for payment in payments:
    print(f"Payment: {payment.voucher_number or payment.name}")
    print(f"  Access Token: {'YES' if payment.access_token else 'NO'}")
    print(f"  QR Code: {'YES' if payment.qr_code else 'NO'}")
    
    # Force regenerate QR for this payment
    if payment.access_token:
        try:
            payment._compute_qr_code()
            print(f"  QR Regeneration: {'SUCCESS' if payment.qr_code else 'FAILED'}")
        except Exception as e:
            print(f"  QR Regeneration: FAILED - {e}")
    else:
        print("  Generating access token...")
        payment.access_token = payment._generate_access_token()
        payment._compute_qr_code()
        print(f"  QR after token gen: {'SUCCESS' if payment.qr_code else 'FAILED'}")

# Test 4: Check base URL configuration
try:
    base_url = env['ir.config_parameter'].sudo().get_param('web.base.url')
    print(f"✅ Base URL configured: {base_url}")
except Exception as e:
    print(f"❌ Base URL issue: {e}")

print("🎯 QR diagnostic complete")

SHELL_EOF
EOF

echo ""
echo "🔧 MANUAL QR FIXES TO TRY"
echo "=" * 30

echo "1. Update payment_account_enhanced module:"
echo "   cd /var/odoo/staging-erposus.com && sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf --no-http --stop-after-init --update payment_account_enhanced"
echo ""

echo "2. Force regenerate QR codes for all payments:"
cat << 'EOF'
cd /var/odoo/staging-erposus.com && sudo -u odoo venv/bin/python3 src/odoo-bin shell -c odoo.conf << 'SHELL_EOF'
payments = env['account.payment'].search([])
for payment in payments:
    if not payment.access_token:
        payment.access_token = payment._generate_access_token()
    payment._compute_qr_code()
env.cr.commit()
print(f"Regenerated QR codes for {len(payments)} payments")
SHELL_EOF
EOF

echo ""
echo "3. Check if modules conflict:"
echo "   - Disable ingenuity_invoice_qr_code module if installed"
echo "   - Check for any custom QR code modules"
echo ""

echo "4. Verify report generation:"
echo "   - Create a test payment"
echo "   - Print payment voucher report"
echo "   - Check if QR appears in PDF"

echo ""
echo "🎯 Copy and paste the shell commands above to diagnose QR issues"
