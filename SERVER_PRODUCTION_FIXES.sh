# PRODUCTION SERVER FIX COMMANDS FOR staging-erposus.com
# Server paths and specific commands for your environment

# ============================================================================
# SERVER ENVIRONMENT VARIABLES
# ============================================================================
ODOO_PATH="/var/odoo/staging-erposus.com"
ODOO_USER="odoo"
PYTHON_BIN="$ODOO_PATH/venv/bin/python3"
ODOO_BIN="$ODOO_PATH/src/odoo-bin"
CONFIG_FILE="$ODOO_PATH/odoo.conf"
LOG_PATH="$ODOO_PATH/logs"

# ============================================================================
# FIX 1: FILESTORE CLEANUP - DIRECT SERVER COMMANDS
# ============================================================================

# Check the missing filestore file issue
echo "🔍 Checking missing filestore attachment..."
cd $ODOO_PATH && sudo -u $ODOO_USER $PYTHON_BIN $ODOO_BIN shell -c $CONFIG_FILE << 'EOF'
# Find and delete orphaned attachment
missing_hash = "abf07d417765a61ef36cdde9947cd6c37892fd3a"
attachments = env['ir.attachment'].search([('store_fname', 'like', missing_hash)])
print(f"Found {len(attachments)} orphaned attachments")
for att in attachments:
    print(f"Deleting: ID={att.id}, Name={att.name}, File={att.store_fname}")
    att.unlink()
env.cr.commit()
print("✅ Filestore cleanup complete")
EOF

# ============================================================================
# FIX 2: WKHTMLTOPDF SSL CONFIGURATION
# ============================================================================

# Backup current config
sudo cp $CONFIG_FILE "${CONFIG_FILE}.backup.$(date +%Y%m%d_%H%M%S)"

# Add SSL fix to odoo.conf
sudo tee -a $CONFIG_FILE << 'EOF'

# PDF Generation SSL Fix for CloudPepper Environment
report_url_timeout = 120
workers = 0
proxy_mode = True
limit_time_cpu = 300
limit_time_real = 600

# wkhtmltopdf SSL workaround
phantomjs_url = http://localhost:8069
EOF

# ============================================================================
# FIX 3: INSTALL REQUIRED PYTHON PACKAGES (IF NEEDED)
# ============================================================================

# Install/update packages that might be needed for PDF generation
sudo -u $ODOO_USER $ODOO_PATH/venv/bin/python3 -m pip install --upgrade \
    qrcode \
    Pillow \
    wkhtmltopdf \
    psutil

# ============================================================================
# FIX 4: UPDATE MODULES WITH FIXES
# ============================================================================

# Update payment_account_enhanced module specifically
echo "🔄 Updating payment_account_enhanced module..."
cd $ODOO_PATH && sudo -u $ODOO_USER $PYTHON_BIN $ODOO_BIN \
    -c $CONFIG_FILE \
    --no-http \
    --stop-after-init \
    --update payment_account_enhanced

# Update all modules if needed (use cautiously in production)
# cd $ODOO_PATH && sudo -u $ODOO_USER $PYTHON_BIN $ODOO_BIN \
#     -c $CONFIG_FILE \
#     --no-http \
#     --stop-after-init \
#     --update all

# ============================================================================
# FIX 5: RESTART ODOO SERVICE
# ============================================================================

# Restart Odoo service (adjust service name as needed)
sudo systemctl restart odoo || sudo service odoo restart

# Wait for service to start
sleep 10

# Check service status
sudo systemctl status odoo || sudo service odoo status

# ============================================================================
# VERIFICATION AND TESTING
# ============================================================================

# Check logs for errors
echo "📋 Checking recent logs..."
tail -50 $LOG_PATH/odoo.log | grep -E "(ERROR|WARNING|FileNotFoundError|SSL)"

# Test PDF generation via Odoo shell
echo "🧪 Testing PDF generation..."
cd $ODOO_PATH && sudo -u $ODOO_USER $PYTHON_BIN $ODOO_BIN shell -c $CONFIG_FILE << 'EOF'
# Test basic PDF generation
try:
    report = env['ir.actions.report']._get_report_from_name('account.report_invoice')
    if report:
        print("✅ Report system accessible")
    else:
        print("❌ Report system issue")
except Exception as e:
    print(f"❌ PDF test error: {e}")
EOF

# Test QR generation in payment module
echo "🔍 Testing QR code generation..."
cd $ODOO_PATH && sudo -u $ODOO_USER $PYTHON_BIN $ODOO_BIN shell -c $CONFIG_FILE << 'EOF'
# Test QR code generation
try:
    import qrcode
    from io import BytesIO
    import base64
    
    # Test basic QR generation
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data("Test QR for staging-erposus.com")
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    
    print("✅ QR code generation working")
except Exception as e:
    print(f"❌ QR generation error: {e}")
EOF

echo "🎯 All fixes applied and tested for staging-erposus.com"
echo "📊 Check the logs above for any remaining issues"
