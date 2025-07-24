#!/bin/bash

# Script to deploy OSUS Executive Sales Dashboard
# This script prepares the module for deployment, ensuring all robustness improvements are applied

echo "OSUS Executive Sales Dashboard Deployment"
echo "=========================================="
echo "This script will prepare your module for deployment"

# Check if we're in the correct directory
if [ ! -d "./oe_sale_dashboard_17" ]; then
    echo "Error: oe_sale_dashboard_17 directory not found. Please run this script from your Odoo addons directory."
    exit 1
fi

# Create backup
echo "Creating backup..."
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="./oe_sale_dashboard_17_backup_${TIMESTAMP}"
cp -r ./oe_sale_dashboard_17 $BACKUP_DIR
echo "Backup created at: $BACKUP_DIR"

# Clear assets cache if available
if [ -d "../var/assets" ]; then
    echo "Clearing assets cache..."
    rm -rf ../var/assets/*
fi

# Create missing directories if needed
directories=(
    "./oe_sale_dashboard_17/static/src/js"
    "./oe_sale_dashboard_17/static/src/css"
    "./oe_sale_dashboard_17/static/src/xml"
    "./oe_sale_dashboard_17/views"
    "./oe_sale_dashboard_17/data"
)

for dir in "${directories[@]}"; do
    mkdir -p "$dir"
done

# JavaScript syntax validation for production readiness
echo "Validating JavaScript syntax..."
# Check if node is available
if command -v node &> /dev/null; then
    # Simple JavaScript syntax validation
    for jsfile in $(find ./oe_sale_dashboard_17 -name "*.js"); do
        echo "Checking $jsfile..."
        node --check "$jsfile"
        if [ $? -ne 0 ]; then
            echo "Syntax error in $jsfile. Please fix before deployment."
            echo "Deployment preparation aborted."
            exit 1
        fi
    done
    echo "All JavaScript files passed syntax validation."
else
    echo "Node.js not found. Skipping JavaScript syntax validation."
    echo "Recommend installing Node.js for syntax validation before production deployment."
fi

# Ensure correct permissions
echo "Setting correct permissions..."
find ./oe_sale_dashboard_17 -type f -exec chmod 644 {} \;
find ./oe_sale_dashboard_17 -type d -exec chmod 755 {} \;

echo "Deployment preparation complete!"
echo ""
echo "To install/update the module:"
echo "1. Restart your Odoo server"
echo "2. Update the module via the Apps menu or run:"
echo "   python3 odoo-bin -d YOUR_DATABASE -u oe_sale_dashboard_17"
echo ""
echo "If you encounter any issues:"
echo "1. Check browser console for JavaScript errors"
echo "2. Review Odoo server logs for Python errors"
echo "3. Consult the documentation in oe_sale_dashboard_17/docs/"
echo ""
echo "Rollback procedure:"
echo "If issues occur after deployment, restore from the backup:"
echo "1. Stop Odoo server"
echo "2. Run: rm -rf ./oe_sale_dashboard_17"
echo "3. Run: cp -r $BACKUP_DIR ./oe_sale_dashboard_17"
echo "4. Restart Odoo server"
echo "3. Consult the documentation in oe_sale_dashboard_17/docs/"
