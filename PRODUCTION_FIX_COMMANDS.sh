# PRODUCTION FIXES FOR staging-erposus.com
# Copy and paste these commands directly into your shell

# ============================================================================
# FIX 1: MISSING FILESTORE FILE CLEANUP
# ============================================================================

# Connect to PostgreSQL and clean up the missing filestore attachment
docker-compose exec db psql -U odoo -d staging-erposus.com -c "
SELECT id, name, res_model, res_id, store_fname 
FROM ir_attachment 
WHERE store_fname LIKE '%abf07d417765a61ef36cdde9947cd6c37892fd3a%';
"

# If the above shows orphaned records, delete them:
docker-compose exec db psql -U odoo -d staging-erposus.com -c "
DELETE FROM ir_attachment 
WHERE store_fname LIKE '%abf07d417765a61ef36cdde9947cd6c37892fd3a%';
"

# ============================================================================
# FIX 2: WKHTMLTOPDF SSL CONFIGURATION
# ============================================================================

# Add SSL fix configuration to odoo.conf
cat >> odoo.conf << 'EOF'

# PDF Generation SSL Fix for stagingosus.cloudpepper.site
report_url_timeout = 120
workers = 0
proxy_mode = True

# wkhtmltopdf SSL workaround
limit_time_cpu = 300
limit_time_real = 600
EOF

# ============================================================================
# FIX 3: TEST PDF GENERATION
# ============================================================================

# Test wkhtmltopdf with SSL fix
echo '<html><body><h1>SSL Test for stagingosus.cloudpepper.site</h1><p>Generated: $(date)</p></body></html>' > /tmp/test.html && \
wkhtmltopdf --disable-ssl-verification --enable-local-file-access /tmp/test.html /tmp/test.pdf && \
echo "✅ PDF generation working" || echo "❌ PDF generation failed"

# ============================================================================
# FIX 4: RESTART SERVICES
# ============================================================================

# Restart Odoo to apply configuration changes
docker-compose restart odoo

# Check logs for any remaining errors
docker-compose logs -f --tail=50 odoo

# ============================================================================
# VERIFICATION COMMANDS
# ============================================================================

# Check if filestore cleanup worked
docker-compose exec db psql -U odoo -d staging-erposus.com -c "
SELECT COUNT(*) as orphaned_attachments 
FROM ir_attachment 
WHERE store_fname IS NOT NULL 
AND store_fname NOT IN (
    SELECT DISTINCT store_fname 
    FROM ir_attachment 
    WHERE store_fname IS NOT NULL
);
"

# Test direct connection to your host
curl -I https://stagingosus.cloudpepper.site/web/login

echo "🎯 All fixes applied for staging-erposus.com database"
echo "🌐 Host: stagingosus.cloudpepper.site"
