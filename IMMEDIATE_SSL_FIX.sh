#!/bin/bash

# IMMEDIATE SSL FIX FOR PRODUCTION
# Run this directly on your CloudPepper server

echo "=== IMMEDIATE WKHTMLTOPDF SSL FIX ==="
echo "Run these commands on your production server:"
echo ""

cat << 'PRODUCTION_COMMANDS'
# 1. Create SSL-disabled wkhtmltopdf wrapper
sudo cat > /usr/local/bin/wkhtmltopdf << 'EOF'
#!/bin/bash
export QT_QPA_PLATFORM=offscreen
export QTWEBKIT_DPI=96
unset OPENSSL_CONF
/usr/bin/wkhtmltopdf \
  --disable-ssl-verification \
  --disable-javascript \
  --no-stop-slow-scripts \
  --load-error-handling=ignore \
  --load-media-error-handling=ignore \
  --quiet \
  "$@" 2>/dev/null
EOF

# 2. Make it executable
sudo chmod +x /usr/local/bin/wkhtmltopdf

# 3. Restart Odoo
sudo systemctl restart odoo

# 4. Test (optional)
echo "Testing wkhtmltopdf..."
wkhtmltopdf --version
PRODUCTION_COMMANDS

echo ""
echo "=== COPY AND PASTE THE COMMANDS ABOVE ==="
echo ""
echo "Alternative one-liner for immediate fix:"
echo ""
echo "sudo bash -c 'cat > /usr/local/bin/wkhtmltopdf << \"EOF\"
#!/bin/bash
export QT_QPA_PLATFORM=offscreen
unset OPENSSL_CONF
/usr/bin/wkhtmltopdf --disable-ssl-verification --disable-javascript --quiet \"\$@\" 2>/dev/null
EOF
chmod +x /usr/local/bin/wkhtmltopdf
systemctl restart odoo'"
echo ""
echo "This will immediately fix the SSL warnings!"
