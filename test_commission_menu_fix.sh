#!/bin/bash

# Test script for commission_ax menu fix
# This script updates the commission_ax module and checks for errors
# Author: GitHub Copilot
# Date: September 16, 2025

echo "Starting commission_ax menu fix test..."

# Navigate to the Odoo directory
cd /var/odoo/osusproperties

# Update the module
echo "Updating commission_ax module..."
./odoo-bin --update=commission_ax --stop-after-init -d osusproperties --log-level=debug

# Check for errors
if [ $? -eq 0 ]; then
    echo "✅ Module update successful!"
    echo "Menu fix appears to be working correctly."
else
    echo "❌ Module update failed!"
    echo "Please check the logs for more information."
    exit 1
fi

echo "Test completed successfully."