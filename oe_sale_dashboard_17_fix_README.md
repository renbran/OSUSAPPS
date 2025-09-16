# OE Sales Dashboard 17 Fix Script

This script fixes issues with the OE Sales Dashboard 17 module, specifically addressing problems with JavaScript component registration, missing functions, and external dependencies.

## Usage

```bash
# Make sure the script is executable
chmod +x oe_sale_dashboard_17_fix.sh

# Run the script
./oe_sale_dashboard_17_fix.sh
```

## What This Script Does

1. **Fixes Component Registration**
   - Updates the OWL component registration to match the XML views
   - Ensures proper action tag is used (`oe_sale_dashboard_17_action`)

2. **Adds Critical Missing Functions**
   - `renderChart`: Function to handle chart creation and management
   - `updateDashboard`: Function to refresh dashboard data
   - `fetchData`: Function to retrieve data from the server
   - Various helper functions for data processing and error handling

3. **Updates Manifest**
   - Removes external CDN dependencies
   - Ensures correct local asset references
   - Maintains proper asset loading order

4. **Applies Changes**
   - Restarts the Odoo service
   - Updates the module to apply changes

## Requirements

- Docker environment with Odoo container running
- Access to the Odoo container filesystem
- Write access to the module files

## Verification

After running the script, verify that:

1. The Sales Dashboard loads properly in the Odoo UI
2. Charts are rendered correctly
3. Data is fetched and displayed
4. Filters and controls work as expected

See `FIX_SUMMARY.md` for a detailed explanation of the issues and fixes.