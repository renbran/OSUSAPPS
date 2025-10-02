# DIRECT FIX - rental_management External ID Issue

## Problem
`RPC_ERROR: External ID not found: rental_management.property_payment_plan_action`

## Root Cause
✅ **Code is 100% correct** - This is a database-only issue where the external ID is missing from `ir.model.data` table.

---

## ⚡ DIRECT FIX COMMANDS

### Option 1: Run on Server (RECOMMENDED)
```bash
# SSH to your server
ssh scholarixv17

# Navigate to Odoo directory
cd /var/odoo/scholarixv17

# Update the module (this recreates the external ID)
sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf --no-http --stop-after-init -d scholarixv17 --update=rental_management

# Restart Odoo service
sudo systemctl restart odoo
# OR if using supervisor:
sudo supervisorctl restart odoo
```

### Option 2: From Odoo UI (EASIEST)
1. Login to Odoo at your server URL
2. Go to **Apps** menu (top menu)
3. Click **Update Apps List** (if needed)
4. Remove the "Apps" filter to show all modules
5. Search for **rental_management**
6. Click the **⋮** (three dots) menu
7. Click **Upgrade**
8. Wait for completion

### Option 3: Use Shell Script
```bash
# Run from local machine (if SSH configured)
cd "/d/RUNNING APPS/ready production/latest/OSUSAPPS"
bash fix_rental_management.sh

# Or run FIX_NOW.bat on Windows
FIX_NOW.bat
```

---

## Verification After Fix

1. Go to **Rental Management** app
2. Click **Configurations** → **Payment Plans**
3. Should open without RPC_ERROR

---

## Server Environment Details

- **Source**: `/var/odoo/scholarixv17/src`
- **Config**: `/var/odoo/scholarixv17/odoo.conf`
- **Database**: `scholarixv17`
- **Python**: `/var/odoo/scholarixv17/venv/bin/python3`

---

## Why This Happened

External IDs can get lost when:
- Module was partially installed/uninstalled
- Database was restored from backup
- Manual database changes were made
- XML files were edited while module was installed

The fix simply reloads all XML data from your correct code files into the database.
