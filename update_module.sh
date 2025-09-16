#!/bin/bash
# update_module.sh
# Updates the OE Sale Dashboard 17 module after deprecation
# Created on: September 16, 2025

echo "========== UPDATING OE SALE DASHBOARD 17 MODULE =========="
echo "Started at $(date)"

# Check if Docker is running
echo "Checking Docker environment..."
if ! docker ps &>/dev/null; then
    echo "ERROR: Docker is not running or not accessible"
    exit 1
fi

# Restart Odoo container
echo "Restarting Odoo container..."
docker-compose restart odoo

# Wait for Odoo to start
echo "Waiting for Odoo to restart..."
sleep 10

# Update the module
echo "Updating the OE Sale Dashboard 17 module..."
docker-compose exec odoo odoo --update=oe_sale_dashboard_17 --stop-after-init

echo "Module update completed at $(date)"
echo "Please verify the dashboard functionality in Odoo UI"