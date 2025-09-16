import xmlrpc.client

# Define connection parameters
url = "http://localhost:8090"
db = "osusproperties"
username = "admin"
password = "admin"

print("Checking module and menu status...")

# Connect to Odoo
print("Connecting to Odoo...")
common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

# Check module state
module_id = models.execute_kw(db, uid, password,
    'ir.module.module', 'search', [[
        ['name', '=', 'commission_ax']
    ]]
)

if module_id:
    module_state = models.execute_kw(db, uid, password,
        'ir.module.module', 'read', [module_id],
        {'fields': ['state']}
    )[0]['state']
    print(f"Module state: {module_state}")
else:
    print("❌ Module 'commission_ax' not found!")

# Check if the menu exists
print("\nChecking for menu 'menu_commission_reports'...")
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
    print("\nListing all menus in the module:")
    all_menus = models.execute_kw(db, uid, password,
        'ir.model.data', 'search_read', [[
            ['module', '=', 'commission_ax'],
            ['model', '=', 'ir.ui.menu'],
        ]],
        {'fields': ['name', 'res_id']}
    )
    
    for menu in all_menus:
        menu_info = models.execute_kw(db, uid, password,
            'ir.ui.menu', 'read', [menu['res_id']],
            {'fields': ['name']}
        )
        print(f"- {menu['name']}: {menu_info[0]['name']}")