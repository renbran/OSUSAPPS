#!/bin/bash
# Update rental_management module after Sales Offer Report enhancement
# Run this script to apply the changes to Odoo

set -e

echo "======================================================================="
echo "  Rental Management - Sales Offer Report Update"
echo "======================================================================="
echo ""
echo "This script will update the rental_management module with the new"
echo "Sales Offer Report enhancements."
echo ""
echo "Changes include:"
echo "  ✓ Biltmore Sufouh color scheme (Bronze/Gold)"
echo "  ✓ Three-column layout on Page 1"
echo "  ✓ Comprehensive payment plan breakdown"
echo "  ✓ Registration fees section"
echo "  ✓ Booking amount section"
echo "  ✓ 'Developer' label (changed from 'Landlord')"
echo "  ✓ Bank details section"
echo "  ✓ Enhanced visual design"
echo ""
echo "======================================================================="
echo ""

# Check if Docker is running
if ! docker ps > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running"
    echo "Please start Docker and try again"
    exit 1
fi

echo "✓ Docker is running"
echo ""

# Check if Odoo container exists
if ! docker-compose ps | grep -q "odoo"; then
    echo "❌ Error: Odoo container not found"
    echo "Please ensure docker-compose.yml is configured correctly"
    exit 1
fi

echo "✓ Odoo container found"
echo ""

# Update the module
echo "Updating rental_management module..."
echo ""

docker-compose exec -T odoo odoo \
    --update=rental_management \
    --stop-after-init \
    --log-level=info

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Module updated successfully"
    echo ""
else
    echo ""
    echo "❌ Module update failed"
    echo "Check the logs above for errors"
    exit 1
fi

# Restart Odoo
echo "Restarting Odoo to apply changes..."
docker-compose restart odoo

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Odoo restarted successfully"
    echo ""
else
    echo ""
    echo "❌ Odoo restart failed"
    exit 1
fi

echo "======================================================================="
echo "  Update Complete!"
echo "======================================================================="
echo ""
echo "Next steps:"
echo "  1. Open Odoo in your browser: http://localhost:8069"
echo "  2. Clear your browser cache (Ctrl+Shift+R)"
echo "  3. Navigate to a property record"
echo "  4. Click 'Print' → 'Sales Offer' to view the new report"
echo ""
echo "For detailed changes, see:"
echo "  rental_management/SALES_OFFER_ENHANCEMENT_SUMMARY.md"
echo ""
echo "Backup file created:"
echo "  rental_management/report/property_brochure_enhanced_report.xml.backup"
echo ""
echo "======================================================================="
