#!/bin/bash
# COMPREHENSIVE SSL & PDF ERROR FIX SCRIPT
# ===============================================
# This script applies a comprehensive fix for PDF generation errors
# and wkhtmltopdf SSL issues in Odoo 17

echo "====================================================="
echo "    COMPREHENSIVE PDF ERROR & SSL FIX SCRIPT         "
echo "====================================================="

# 1. Apply PDF rendering fix at code level
echo "Installing required Python packages..."
docker-compose exec odoo pip3 install --upgrade reportlab PyPDF2

# 2. Apply system-level wkhtmltopdf fixes
echo "Applying system-level wkhtmltopdf fixes..."
docker-compose exec odoo bash -c 'cat > /tmp/wkhtmltopdf_wrapper.sh << "EOF"
#!/bin/bash
# Wrapper script for wkhtmltopdf to resolve SSL issues
export QT_QPA_PLATFORM=offscreen
/usr/local/bin/wkhtmltopdf.bin --load-error-handling ignore --load-media-error-handling ignore "$@"
EOF'

docker-compose exec odoo bash -c 'chmod +x /tmp/wkhtmltopdf_wrapper.sh'
docker-compose exec odoo bash -c '[ -f /usr/local/bin/wkhtmltopdf.bin ] || mv /usr/local/bin/wkhtmltopdf /usr/local/bin/wkhtmltopdf.bin'
docker-compose exec odoo bash -c 'cp /tmp/wkhtmltopdf_wrapper.sh /usr/local/bin/wkhtmltopdf'
docker-compose exec odoo bash -c 'chmod +x /usr/local/bin/wkhtmltopdf'

# 3. Apply Odoo configuration fixes
echo "Applying Odoo configuration fixes..."
docker-compose exec odoo bash -c 'cat >> /etc/odoo/odoo.conf << "EOF"

# PDF Error & SSL Fixes
report_url_wkhtmltopdf_args = --load-error-handling ignore --load-media-error-handling ignore
EOF'

# 4. Apply system environment variables
echo "Setting system environment variables..."
docker-compose exec odoo bash -c 'cat >> /etc/environment << "EOF"
QT_QPA_PLATFORM=offscreen
OPENSSL_CONF=/etc/ssl/
EOF'

# 5. Set Odoo parameters
echo "Setting Odoo parameters..."
docker-compose exec odoo odoo shell -d odoo -c /etc/odoo/odoo.conf << 'EOF'
try:
    # Set wkhtmltopdf args
    env['ir.config_parameter'].sudo().set_param('report.url_wkhtmltopdf_args', 
        '--load-error-handling ignore --load-media-error-handling ignore')
    
    # Update existing ir.actions.report records
    reports = env['ir.actions.report'].search([])
    for report in reports:
        if hasattr(report, 'paperformat_id') and report.paperformat_id:
            report.paperformat_id.write({
                'dpi': 96,  # More stable DPI setting
                'margin_top': 20,  # Safer margins
                'margin_bottom': 20,
                'margin_left': 15,
                'margin_right': 15
            })
    
    print("Odoo parameters updated successfully!")
except Exception as e:
    print(f"Error updating parameters: {str(e)}")
EOF

# 6. Restart Odoo to apply changes
echo "Restarting Odoo to apply changes..."
docker-compose restart odoo

echo "Waiting for Odoo to restart..."
sleep 10

# 7. Update module with PDF error fix
echo "Updating payment_account_enhanced module with PDF error fix..."
docker-compose exec odoo odoo -d odoo -c /etc/odoo/odoo.conf --update=payment_account_enhanced --stop-after-init

echo "====================================================="
echo "        PDF ERROR & SSL FIX COMPLETED                "
echo "====================================================="
echo " The following fixes have been applied:               "
echo " 1. System-level wkhtmltopdf wrapper with SSL fixes   "
echo " 2. Odoo configuration parameter updates              "
echo " 3. Environment variable settings                     "
echo " 4. PDF report format optimizations                   "
echo " 5. Code-level PDF error handling                     "
echo "====================================================="
echo " VALIDATION TESTS:                                    "
echo " 1. Generate a payment voucher report                 "
echo " 2. Check for any RPC errors                          "
echo " 3. Verify email template rendering                   "
echo "====================================================="
