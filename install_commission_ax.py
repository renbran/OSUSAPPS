#!/usr/bin/env python3
import xmlrpc.client

# Odoo connection parameters
url = 'http://localhost:8090'
db = 'odoo'
username = 'admin'
password = 'admin'

# Connect to Odoo
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

if uid:
    print(f"Authenticated as user ID: {uid}")
    
    # Get models proxy
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    
    # Update module list
    print("Updating module list...")
    models.execute_kw(db, uid, password, 'ir.module.module', 'update_list', [])
    
    # Find commission_ax module
    module_ids = models.execute_kw(db, uid, password, 'ir.module.module', 'search', [
        [('name', '=', 'commission_ax')]
    ])
    
    if module_ids:
        print(f"Found commission_ax module with ID: {module_ids[0]}")
        
        # Get module info
        module_info = models.execute_kw(db, uid, password, 'ir.module.module', 'read', [
            module_ids, ['name', 'state', 'shortdesc']
        ])
        print(f"Module info: {module_info[0]}")
        
        if module_info[0]['state'] == 'uninstalled':
            print("Installing commission_ax module...")
            try:
                # Install the module
                models.execute_kw(db, uid, password, 'ir.module.module', 'button_immediate_install', [module_ids])
                print("Module installation initiated successfully!")
            except Exception as e:
                print(f"Error during installation: {e}")
        else:
            print(f"Module state: {module_info[0]['state']}")
    else:
        print("commission_ax module not found")
else:
    print("Authentication failed")