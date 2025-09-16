#!/bin/bash

# Script to verify the commission menu fix is working
# Author: GitHub Copilot
# Date: September 16, 2025

# Set variables
DB_NAME="osusproperties"
MODULE_NAME="commission_ax"
MENU_XML_ID="commission_ax.menu_commission_reports"

echo "Starting commission menu verification test..."

# Check if the menu exists in ir.model.data
docker exec osusapps-odoo-1 odoo shell -d $DB_NAME <<EOF
env = env(context=dict(active_test=False))
# Check if the menu ID exists
menu_data = env['ir.model.data'].search([('module', '=', '$MODULE_NAME'), ('name', '=', 'menu_commission_reports')])
if menu_data:
    menu = env['ir.ui.menu'].browse(menu_data.res_id)
    print(f"\n\n✅ MENU EXISTS: '{menu.name}' (ID: {menu.id})")
    print(f"   Parent menu: {menu.parent_id.name}")
    print(f"   Complete path: {menu.parent_id.parent_id.name} > {menu.parent_id.name} > {menu.name}")
    
    # Check for child menus
    child_menus = env['ir.ui.menu'].search([('parent_id', '=', menu.id)])
    if child_menus:
        print(f"   Child menus:")
        for child in child_menus:
            print(f"   - {child.name}")
    else:
        print("   No child menus found.")
    
    print("\nMENU VERIFICATION: PASSED ✅")
else:
    print("\n\n❌ ERROR: Menu 'menu_commission_reports' not found in ir.model.data!")
    print("\nMENU VERIFICATION: FAILED ❌")
    
    # Debug: List all menus in the module
    print("\nDebug: Available menus in the module:")
    module_menus = env['ir.model.data'].search([('module', '=', '$MODULE_NAME'), ('model', '=', 'ir.ui.menu')])
    for m in module_menus:
        menu = env['ir.ui.menu'].browse(m.res_id)
        print(f"- {m.name}: {menu.name}")
EOF

echo -e "\nTest completed."