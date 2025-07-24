#!/bin/bash

# Script to update OSUS Executive Sales Dashboard module in Odoo
# Usage: ./update_module.sh <database_name>

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <database_name>"
    exit 1
fi

DATABASE=$1
ODOO_BIN=${ODOO_BIN:-odoo-bin}

echo "Updating OSUS Executive Sales Dashboard module in database: $DATABASE"

# Stop Odoo service if running as a service
if command -v systemctl &> /dev/null && systemctl is-active --quiet odoo; then
    echo "Stopping Odoo service..."
    sudo systemctl stop odoo
fi

# Clear assets cache if it exists
if [ -d "./var/assets" ]; then
    echo "Clearing assets cache..."
    rm -rf ./var/assets/*
fi

# Run module update
echo "Running module update..."
$ODOO_BIN -d $DATABASE -u oe_sale_dashboard_17 --stop-after-init

# Restart Odoo service if it was running
if command -v systemctl &> /dev/null && systemctl is-enabled --quiet odoo; then
    echo "Restarting Odoo service..."
    sudo systemctl start odoo
fi

echo "Update complete. Check Odoo logs for any errors."
