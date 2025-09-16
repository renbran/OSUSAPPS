import xmlrpc.client
import time

# Define connection parameters
url = "http://localhost:8090"
db = "osusproperties"
username = "admin"
password = "admin"

print("Starting module installation test...")

# Connect to Odoo
print("Connecting to Odoo...")
common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

# Find the module
module_id = models.execute_kw(db, uid, password,
    'ir.module.module', 'search', [[
        ['name', '=', 'commission_ax']
    ]]
)

if not module_id:
    print("❌ Module 'commission_ax' not found!")
    exit(1)

# Get module state
module_state = models.execute_kw(db, uid, password,
    'ir.module.module', 'read', [module_id],
    {'fields': ['state']}
)[0]['state']

print(f"Current module state: {module_state}")

if module_state == 'installed':
    print("Module already installed. Upgrading...")
    try:
        models.execute_kw(db, uid, password,
            'ir.module.module', 'button_immediate_upgrade', [module_id]
        )
    except Exception as e:
        print(f"Error during upgrade: {e}")
else:
    print("Installing module...")
    try:
        models.execute_kw(db, uid, password,
            'ir.module.module', 'button_immediate_install', [module_id]
        )
    except Exception as e:
        print(f"Error during installation: {e}")

print("Module operation initiated. Waiting for completion...")
time.sleep(10)  # Wait for module operation to complete

print("\nTest completed.")