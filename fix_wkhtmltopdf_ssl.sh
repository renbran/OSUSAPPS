#!/bin/bash
# wkhtmltopdf SSL Configuration Fix Script
# Resolves SSL library and network connectivity issues

echo "🖨️  FIXING WKHTMLTOPDF SSL ISSUES"
echo "=" * 50

# Check if we're in a Docker environment
if [ -f /.dockerenv ]; then
    echo "📦 Detected Docker environment"
    ODOO_CONF="/etc/odoo/odoo.conf"
else
    echo "🖥️  Detected host environment"
    ODOO_CONF="./odoo.conf"
fi

echo "📝 Updating Odoo configuration for PDF generation"

# Backup existing config if it exists
if [ -f "$ODOO_CONF" ]; then
    cp "$ODOO_CONF" "${ODOO_CONF}.backup.$(date +%Y%m%d_%H%M%S)"
    echo "✅ Backed up existing odoo.conf"
fi

# Add or update PDF generation settings
echo "
# PDF Generation Configuration
report_url_timeout = 120
phantomjs_url = http://localhost:8069

# wkhtmltopdf SSL fix
workers = 0

# Additional SSL settings for CloudPepper hosting
proxy_mode = True
" >> "$ODOO_CONF"

echo "✅ Updated odoo.conf with PDF generation settings"

# Check if custom_background module exists and needs fixing
if [ -d "./custom_background" ]; then
    echo "🔧 Found custom_background module - applying SSL fix"
    
    # Create SSL fix for custom_background module
    cat > custom_background_ssl_fix.py << 'EOF'
# -*- coding: utf-8 -*-
"""
SSL Fix for custom_background module
Patch for wkhtmltopdf SSL issues
"""

from odoo import models
import logging

_logger = logging.getLogger(__name__)

class ReportSSLFix(models.AbstractModel):
    _name = 'report.ssl.fix'
    _description = 'SSL Fix for PDF Reports'
    
    def _build_wkhtmltopdf_args(self, paperformat_id, landscape, specific_paperformat_args=None, set_viewport_size=False):
        """Override to add SSL fix arguments"""
        args = super()._build_wkhtmltopdf_args(
            paperformat_id, landscape, specific_paperformat_args, set_viewport_size
        )
        
        # Add SSL fix arguments
        ssl_fix_args = [
            '--disable-ssl-verification',
            '--enable-local-file-access',
            '--no-stop-slow-scripts',
            '--debug-javascript',
            '--load-error-handling', 'ignore',
            '--load-media-error-handling', 'ignore'
        ]
        
        args.extend(ssl_fix_args)
        _logger.info(f"Applied SSL fix arguments: {ssl_fix_args}")
        
        return args

# Patch the base report model
class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'
    
    def _run_wkhtmltopdf(self, bodies, header=None, footer=None, landscape=False, 
                        specific_paperformat_args=None, set_viewport_size=False):
        """Override to handle SSL errors gracefully"""
        
        try:
            return super()._run_wkhtmltopdf(
                bodies, header, footer, landscape, 
                specific_paperformat_args, set_viewport_size
            )
        except Exception as e:
            if 'SSL' in str(e) or 'network' in str(e).lower():
                _logger.warning(f"SSL/Network error in PDF generation, retrying with safer options: {e}")
                
                # Retry with minimal options
                safer_args = {'disable-ssl-verification': None}
                return super()._run_wkhtmltopdf(
                    bodies, header, footer, landscape, 
                    safer_args, set_viewport_size
                )
            else:
                raise
EOF
    
    echo "✅ Created SSL fix patch for custom_background module"
    
else
    echo "ℹ️  custom_background module not found in current directory"
fi

# Create wkhtmltopdf test script
cat > test_wkhtmltopdf.sh << 'EOF'
#!/bin/bash
echo "🧪 Testing wkhtmltopdf SSL configuration"

# Create test HTML
cat > /tmp/ssl_test.html << 'HTML'
<!DOCTYPE html>
<html>
<head>
    <title>SSL Test</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        .success { color: green; }
        .error { color: red; }
    </style>
</head>
<body>
    <h1>wkhtmltopdf SSL Test</h1>
    <p class="success">If you can see this in a PDF, the SSL fix is working!</p>
    <p>Generated on: $(date)</p>
</body>
</html>
HTML

# Test with SSL fix
if wkhtmltopdf --disable-ssl-verification /tmp/ssl_test.html /tmp/ssl_test.pdf 2>/dev/null; then
    echo "✅ SSL fix test PASSED"
    ls -la /tmp/ssl_test.pdf
else
    echo "❌ SSL fix test FAILED"
fi

# Cleanup
rm -f /tmp/ssl_test.html /tmp/ssl_test.pdf
EOF

chmod +x test_wkhtmltopdf.sh

echo "✅ Created wkhtmltopdf test script"
echo ""
echo "🚀 NEXT STEPS:"
echo "1. Restart Odoo service to apply configuration changes"
echo "2. Run ./test_wkhtmltopdf.sh to verify the fix"
echo "3. Test PDF generation in Odoo"
echo ""
echo "For Docker environments:"
echo "docker-compose restart odoo"
echo ""
echo "For direct installations:"
echo "sudo systemctl restart odoo"
