#!/bin/bash
# Production Issues Diagnostic and Fix Script
# Addresses FileNotFoundError and wkhtmltopdf SSL issues

echo "🔍 ODOO PRODUCTION ISSUES DIAGNOSTIC"
echo "=" * 60

# Issue 1: Missing Filestore File
echo "📁 CHECKING FILESTORE ISSUES"
echo "-" * 30

MISSING_FILE="/var/odoo/.local/share/Odoo/filestore/staging-erposus.com/ab/abf07d417765a61ef36cdde9947cd6c37892fd3a"

echo "Missing file: $MISSING_FILE"

if [[ -f "$MISSING_FILE" ]]; then
    echo "✅ File exists now"
else
    echo "❌ File still missing - needs cleanup"
    
    # Find the attachment record that references this missing file
    echo "🔍 Finding database references..."
    
    # Extract the file hash from the path
    FILE_HASH="abf07d417765a61ef36cdde9947cd6c37892fd3a"
    echo "File hash: $FILE_HASH"
    
    echo "📋 RECOMMENDED ACTIONS:"
    echo "1. Connect to Odoo database and run:"
    echo "   SELECT id, name, res_model, res_id, store_fname FROM ir_attachment WHERE store_fname LIKE '%$FILE_HASH%';"
    echo ""
    echo "2. If record found but file missing, either:"
    echo "   a) Re-upload the attachment, OR"
    echo "   b) Delete the orphaned record: DELETE FROM ir_attachment WHERE store_fname LIKE '%$FILE_HASH%';"
fi

echo ""
echo "🖨️  CHECKING WKHTMLTOPDF SSL ISSUES"
echo "-" * 30

# Check if wkhtmltopdf is installed
if command -v wkhtmltopdf &> /dev/null; then
    echo "✅ wkhtmltopdf is installed"
    wkhtmltopdf --version
    
    echo ""
    echo "🔧 TESTING SSL CONFIGURATION"
    
    # Test basic PDF generation
    echo "<html><body><h1>SSL Test</h1></body></html>" > /tmp/test.html
    
    if wkhtmltopdf --disable-ssl-verification /tmp/test.html /tmp/test.pdf 2>/dev/null; then
        echo "✅ PDF generation works with --disable-ssl-verification"
    else
        echo "❌ PDF generation fails even with SSL disabled"
    fi
    
    rm -f /tmp/test.html /tmp/test.pdf
    
else
    echo "❌ wkhtmltopdf not found"
fi

echo ""
echo "🚀 RECOMMENDED FIXES"
echo "=" * 60

echo "For FileNotFoundError:"
echo "1. Run database cleanup: docker-compose exec odoo odoo shell -d staging-erposus.com"
echo "   >>> env['ir.attachment'].search([('store_fname', 'like', 'abf07d417765a61ef36cdde9947cd6c37892fd3a')]).unlink()"
echo ""

echo "For wkhtmltopdf SSL issues:"
echo "1. Add to odoo.conf:"
echo "   report_url_timeout = 120"
echo "   phantomjs_url = http://localhost:8069"
echo ""
echo "2. Or in custom_background module, modify report generation to use:"
echo "   options = {'disable-ssl-verification': None}"
echo ""

echo "🏥 HEALTH CHECK COMPLETE"
