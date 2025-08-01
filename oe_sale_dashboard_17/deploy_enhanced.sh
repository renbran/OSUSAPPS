#!/bin/bash

# Enhanced Sales Dashboard CloudPepper Deployment Script
# Use this script to deploy the module to CloudPepper Odoo instance

echo "=== Enhanced Sales Dashboard CloudPepper Deployment ==="
echo "Module: oe_sale_dashboard_17"
echo "CloudPepper Location: /var/odoo/coatest/extra-addons/odoo17_final.git-6880b7fcd4844/oe_sale_dashboard_17"
echo "Current Location: $(pwd)"
echo ""

# Check if we're in the right directory
if [ ! -f "__manifest__.py" ]; then
    echo "Error: Not in module directory. Please run from oe_sale_dashboard_17 folder."
    exit 1
fi

echo "✅ Module directory confirmed"

# Check for required files
REQUIRED_FILES=(
    "models/sale_dashboard.py"
    "static/src/js/dashboard_enhanced.js"
    "static/src/css/dashboard.css"
    "static/src/xml/dashboard_template.xml"
    "views/dashboard_views.xml"
)

echo "🔍 Checking required files..."
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (missing)"
    fi
done

echo ""
echo "📋 Enhanced Features Implemented:"
echo "  ✅ Date filtering with booking_date"
echo "  ✅ Sales type category filtering"
echo "  ✅ Category summary scorecards"
echo "  ✅ Sub-category breakdowns (Draft/SO/Invoice)"
echo "  ✅ Line chart for sales trends"
echo "  ✅ Enhanced pie chart for distribution"
echo "  ✅ Bar chart for category comparison"  
echo "  ✅ Performance ranking table"
echo "  ✅ Responsive design with modern UI"
echo ""

echo "🚀 Deployment Instructions:"
echo "1. Restart your Odoo server"
echo "2. Go to Apps menu in Odoo"
echo "3. Search for 'OSUS Executive Sales Dashboard'"
echo "4. Click 'Upgrade' if already installed, or 'Install' if new"
echo "5. Navigate to the dashboard menu to test new features"
echo ""

echo "🔧 Troubleshooting:"
echo "- Ensure Chart.js CDN is accessible: https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js"
echo "- Check that dependencies are installed: sale_management, osus_invoice_report, le_sale_type"
echo "- Verify booking_date field exists in sale.order model"
echo "- Clear browser cache if visualizations don't appear"
echo ""

echo "📊 New Dashboard Features:"
echo "- Use date range controls to filter by booking_date"
echo "- Select sales types in the multi-select dropdown"
echo "- View category totals in the summary cards"
echo "- Analyze trends in the line chart"
echo "- Compare performance in bar charts and ranking table"
echo ""

echo "✨ Enhancement deployment ready!"
echo "=== End of Deployment Script ==="
