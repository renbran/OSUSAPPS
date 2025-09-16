#!/bin/bash
# update_sale_dashboard.sh
# Updates the OE Sale Dashboard 17 module manually
# Created on: September 16, 2025

echo "========== MANUAL UPDATE FOR OE SALE DASHBOARD 17 =========="
echo "Started at $(date)"

# Make sure Docker is running
docker ps > /dev/null
if [ $? -ne 0 ]; then
  echo "Docker is not running. Please start Docker and try again."
  exit 1
fi

# 1. Update component registration in JS file
echo "1. Updating component registration..."
sed -i 's/registry.category("actions").add("oe_sale_dashboard_17_tag", SaleDashboardMerged)/registry.category("actions").add("oe_sale_dashboard_17_action", SaleDashboardMerged)/g' \
  "d:/RUNNING APPS/ready production/latest/OSUSAPPS/oe_sale_dashboard_17/static/src/js/dashboard_merged.js"

# 2. Remove CDN URL from manifest
echo "2. Removing CDN URL from manifest..."
sed -i '/https:\/\/cdn.jsdelivr.net\/npm\/chart.js@4.4.0\/dist\/chart.umd.js/d' \
  "d:/RUNNING APPS/ready production/latest/OSUSAPPS/oe_sale_dashboard_17/__manifest__.py"

# 3. Restart the Odoo container
echo "3. Restarting Odoo container..."
docker-compose restart odoo

# Wait for Odoo to restart
echo "   Waiting for Odoo to restart..."
sleep 10

# 4. Update the module
echo "4. Updating the module..."
docker-compose exec odoo odoo --update=oe_sale_dashboard_17 --stop-after-init

echo "Manual update completed at $(date)"
echo "Please run the test script to verify the fixes."