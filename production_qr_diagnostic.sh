#!/bin/bash
# Comprehensive QR Code Production Diagnostic
# For staging-erposus.com database

echo "🔍 COMPREHENSIVE QR CODE PRODUCTION DIAGNOSTIC"
echo "Database: staging-erposus.com"
echo "Host: stagingosus.cloudpepper.site" 
echo "=" * 60

cat << 'EOF'
# STEP 1: Check if module is properly loaded
cd /var/odoo/staging-erposus.com && sudo -u odoo venv/bin/python3 src/odoo-bin shell -c odoo.conf << 'DIAGNOSTIC_EOF'

print("🔍 MODULE AND FIELD DIAGNOSTIC")
print("=" * 40)

# Check if payment_account_enhanced is installed
try:
    modules = env['ir.module.module'].search([('name', '=', 'payment_account_enhanced')])
    if modules:
        module = modules[0]
        print(f"✅ payment_account_enhanced module found: {module.state}")
    else:
        print("❌ payment_account_enhanced module NOT FOUND")
except Exception as e:
    print(f"❌ Error checking module: {e}")

# Check if qr_code field exists in account.payment model
try:
    payment_model = env['ir.model'].search([('model', '=', 'account.payment')])
    if payment_model:
        qr_field = env['ir.model.fields'].search([
            ('model_id', '=', payment_model.id),
            ('name', '=', 'qr_code')
        ])
        if qr_field:
            print("✅ qr_code field exists in account.payment model")
            print(f"   Field type: {qr_field.ttype}")
            print(f"   Compute: {qr_field.compute}")
        else:
            print("❌ qr_code field NOT FOUND in account.payment model")
    else:
        print("❌ account.payment model not found")
except Exception as e:
    print(f"❌ Error checking qr_code field: {e}")

# Check if access_token field exists
try:
    access_token_field = env['ir.model.fields'].search([
        ('model_id', '=', payment_model.id),
        ('name', '=', 'access_token')
    ])
    if access_token_field:
        print("✅ access_token field exists")
    else:
        print("❌ access_token field NOT FOUND")
except Exception as e:
    print(f"❌ Error checking access_token field: {e}")

print("\n🧪 TESTING QR CODE LIBRARIES")
print("=" * 40)

# Test qrcode library
try:
    import qrcode
    print("✅ qrcode library imported successfully")
    print(f"   qrcode version: {qrcode.__version__}")
except ImportError as e:
    print(f"❌ qrcode library import failed: {e}")

# Test Pillow library
try:
    from PIL import Image
    print("✅ Pillow (PIL) library imported successfully")
except ImportError as e:
    print(f"❌ Pillow library import failed: {e}")

# Test base64 and BytesIO
try:
    import base64
    from io import BytesIO
    print("✅ base64 and BytesIO available")
except ImportError as e:
    print(f"❌ base64/BytesIO import failed: {e}")

print("\n💾 CHECKING EXISTING PAYMENT RECORDS")
print("=" * 40)

# Check existing payments
try:
    total_payments = env['account.payment'].search_count([])
    print(f"Total payments in database: {total_payments}")
    
    # Get sample payments
    payments = env['account.payment'].search([
        ('voucher_number', '!=', False)
    ], limit=5, order='id desc')
    
    print(f"Sample payments with voucher numbers: {len(payments)}")
    
    for payment in payments:
        print(f"\nPayment ID: {payment.id}")
        print(f"  Voucher: {payment.voucher_number}")
        print(f"  Name: {payment.name}")
        print(f"  Access Token: {'YES' if payment.access_token else 'NO'}")
        print(f"  QR Code: {'YES' if payment.qr_code else 'NO'}")
        print(f"  State: {payment.state}")
        print(f"  Approval State: {payment.approval_state}")
        
        # Try to access the qr_code field directly
        try:
            qr_value = payment.qr_code
            if qr_value:
                print(f"  QR Code Size: {len(qr_value)} bytes")
            else:
                print("  QR Code: None/False")
        except Exception as e:
            print(f"  QR Code Access Error: {e}")

except Exception as e:
    print(f"❌ Error checking payments: {e}")

print("\n🔧 TESTING QR CODE GENERATION")
print("=" * 40)

# Test basic QR generation
try:
    import qrcode
    import base64
    from io import BytesIO
    
    # Create test QR
    test_url = "https://stagingosus.cloudpepper.site/test"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=20,
        border=4,
    )
    qr.add_data(test_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    qr_data = base64.b64encode(buffer.getvalue())
    
    print(f"✅ Test QR generation successful")
    print(f"   URL: {test_url}")
    print(f"   QR Size: {len(qr_data)} bytes")
    
except Exception as e:
    print(f"❌ Test QR generation failed: {e}")

print("\n🌐 CHECKING BASE URL CONFIGURATION")
print("=" * 40)

try:
    base_url = env['ir.config_parameter'].sudo().get_param('web.base.url')
    print(f"Configured base URL: {base_url}")
    
    # Check if it matches expected URL
    expected_url = "https://stagingosus.cloudpepper.site"
    if base_url == expected_url:
        print("✅ Base URL matches expected value")
    else:
        print(f"⚠️  Base URL mismatch. Expected: {expected_url}")
        
except Exception as e:
    print(f"❌ Error checking base URL: {e}")

print("\n🎯 DIAGNOSTIC COMPLETE")

DIAGNOSTIC_EOF
EOF

echo ""
echo "🔧 STEP 2: FORCE QR REGENERATION TEST"
echo "=" * 40

cat << 'EOF'
cd /var/odoo/staging-erposus.com && sudo -u odoo venv/bin/python3 src/odoo-bin shell -c odoo.conf << 'REGEN_EOF'

print("🔄 FORCE QR REGENERATION TEST")
print("=" * 30)

# Get first payment without QR code
payment = env['account.payment'].search([
    ('qr_code', '=', False)
], limit=1)

if not payment:
    # If no payment without QR, get any payment
    payment = env['account.payment'].search([], limit=1)

if payment:
    print(f"Testing with Payment ID: {payment.id}")
    print(f"  Voucher: {payment.voucher_number}")
    print(f"  Name: {payment.name}")
    
    # Step 1: Ensure access token exists
    if not payment.access_token:
        print("  Generating access token...")
        try:
            payment.access_token = payment._generate_access_token()
            print(f"  ✅ Access token generated: {payment.access_token[:10]}...")
        except Exception as e:
            print(f"  ❌ Access token generation failed: {e}")
    else:
        print(f"  Access token exists: {payment.access_token[:10]}...")
    
    # Step 2: Force QR code computation
    print("  Computing QR code...")
    try:
        payment._compute_qr_code()
        if payment.qr_code:
            print(f"  ✅ QR code generated successfully! Size: {len(payment.qr_code)} bytes")
        else:
            print("  ❌ QR code is still False after computation")
    except Exception as e:
        print(f"  ❌ QR computation failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Step 3: Save and commit
    try:
        env.cr.commit()
        print("  ✅ Changes committed to database")
    except Exception as e:
        print(f"  ❌ Commit failed: {e}")
        
    # Step 4: Re-read from database
    payment_reloaded = env['account.payment'].browse(payment.id)
    print(f"  Final QR status: {'YES' if payment_reloaded.qr_code else 'NO'}")
    
else:
    print("❌ No payment records found to test with")

REGEN_EOF
EOF

echo ""
echo "🚀 STEP 3: MODULE UPDATE AND FIELD CHECK"
echo "=" * 40

cat << 'EOF'
# Force update the module to ensure all fields are created
echo "Updating payment_account_enhanced module..."
cd /var/odoo/staging-erposus.com && sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf --no-http --stop-after-init --update payment_account_enhanced

# Check if update was successful
cd /var/odoo/staging-erposus.com && sudo -u odoo venv/bin/python3 src/odoo-bin shell -c odoo.conf << 'UPDATE_CHECK_EOF'

# Verify fields exist after update
payment_model = env['ir.model'].search([('model', '=', 'account.payment')])
qr_field = env['ir.model.fields'].search([
    ('model_id', '=', payment_model.id),
    ('name', '=', 'qr_code')
])

access_field = env['ir.model.fields'].search([
    ('model_id', '=', payment_model.id),
    ('name', '=', 'access_token')
])

print(f"After update - QR field exists: {'YES' if qr_field else 'NO'}")
print(f"After update - Access token field exists: {'YES' if access_field else 'NO'}")

# Try to create a new payment and check QR generation
try:
    partner = env['res.partner'].search([], limit=1)
    new_payment = env['account.payment'].create({
        'payment_type': 'outbound',
        'partner_id': partner.id,
        'amount': 100.0,
        'date': fields.Date.today(),
    })
    
    print(f"New payment created: {new_payment.voucher_number}")
    print(f"  Access token: {'YES' if new_payment.access_token else 'NO'}")
    print(f"  QR code: {'YES' if new_payment.qr_code else 'NO'}")
    
    if new_payment.qr_code:
        print(f"  QR size: {len(new_payment.qr_code)} bytes")
    
except Exception as e:
    print(f"❌ Failed to create test payment: {e}")

UPDATE_CHECK_EOF
EOF

echo ""
echo "📋 COPY-PASTE DIAGNOSTIC COMMANDS ABOVE"
echo "Run each step to identify the exact issue with QR generation"
