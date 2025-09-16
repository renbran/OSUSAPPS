import xmlrpc.client
import time

# Define connection parameters
url = "http://localhost:8090"
db = "osusproperties"
username = "admin"
password = "admin"

print("Starting module update test...")

# Connect to Odoo
print("Connecting to Odoo...")
common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

# Update the module
print("Updating module 'commission_ax'...")
models.execute_kw(db, uid, password,
    'ir.module.module', 'button_immediate_upgrade', [[
        models.execute_kw(db, uid, password,
            'ir.module.module', 'search', [[
                ['name', '=', 'commission_ax']
            ]]
        )[0]
    ]]
)

print("Module update initiated. Waiting for update to complete...")
time.sleep(5)  # Wait for module to update

# Check if the menu exists
print("\nVerifying menu exists...")
menu_id = models.execute_kw(db, uid, password,
    'ir.model.data', 'search', [[
        ['module', '=', 'commission_ax'],
        ['name', '=', 'menu_commission_reports'],
    ]]
)

if menu_id:
    print("✅ Menu exists! Verification passed.")
    
    # Get menu details
    menu_data = models.execute_kw(db, uid, password,
        'ir.model.data', 'read', [menu_id],
        {'fields': ['res_id']}
    )
    
    # Get actual menu information
    if menu_data:
        menu_res_id = menu_data[0]['res_id']
        menu_info = models.execute_kw(db, uid, password,
            'ir.ui.menu', 'read', [menu_res_id],
            {'fields': ['name', 'parent_id']}
        )
        print(f"Menu name: {menu_info[0]['name']}")
        if menu_info[0]['parent_id']:
            parent_info = models.execute_kw(db, uid, password,
                'ir.ui.menu', 'read', [menu_info[0]['parent_id'][0]],
                {'fields': ['name']}
            )
            print(f"Parent menu: {parent_info[0]['name']}")
else:
    print("❌ Menu not found! Verification failed.")
    
    # List all menus in the module for debugging
    all_menus = models.execute_kw(db, uid, password,
        'ir.model.data', 'search_read', [[
            ['module', '=', 'commission_ax'],
            ['model', '=', 'ir.ui.menu'],
        ]],
        {'fields': ['name', 'res_id']}
    )
    
    print("\nAvailable menus in the module:")
    for menu in all_menus:
        menu_info = models.execute_kw(db, uid, password,
            'ir.ui.menu', 'read', [menu['res_id']],
            {'fields': ['name']}
        )
        print(f"- {menu['name']}: {menu_info[0]['name']}")

print("\nTest completed.")