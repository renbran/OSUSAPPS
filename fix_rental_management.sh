#!/bin/bash
# DIRECT FIX for rental_management External ID Issue
# For scholarixv17 server environment

echo "============================================================"
echo "DIRECT FIX: Updating rental_management module"
echo "Server: 139.84.163.11 (scholarixv17)"
echo "Database: scholarixv17"
echo "============================================================"
echo ""

# SSH to server and run update
echo "Connecting to server..."
ssh root@139.84.163.11 << 'ENDSSH'
cd /var/odoo/scholarixv17
echo "Running module update..."
sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf --no-http --stop-after-init -d scholarixv17 --update=rental_management
ENDSSH

# Check if successful
if [ $? -eq 0 ]; then
    echo ""
    echo "============================================================"
    echo "✅ SUCCESS! Module updated successfully."
    echo "The external ID has been recreated."
    echo ""
    echo "Next steps:"
    echo "1. Restart Odoo service"
    echo "2. Test the Payment Plans menu in Rental Management"
    echo "============================================================"
else
    echo ""
    echo "============================================================"
    echo "❌ ERROR! Update failed."
    echo ""
    echo "Alternative: Try from Odoo UI"
    echo "1. Go to Apps menu"
    echo "2. Remove 'Apps' filter"
    echo "3. Find rental_management"
    echo "4. Click Upgrade button"
    echo "============================================================"
fi
