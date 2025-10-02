# Deep Ocean Reports - Error Fix Guide

## 🔍 Problem Analysis

**Error**: `"sale.order"."purchase_order_count" field is undefined.`

**Root Cause**: The `commission_ax` module defines a `purchase_order_count` field on `sale.order` that depends on `purchase_order_ids`, but there's a dependency or installation issue causing this field to be undefined when views try to load.

## 🛠️ IMMEDIATE FIXES

### Fix 1: Remove Unnecessary Dependencies

Our Deep Ocean Reports module doesn't actually need the `sale` dependency since we only work with invoices (`account.move`). 

**ALREADY APPLIED**: Removed `sale` from dependencies in `__manifest__.py`

### Fix 2: Commission AX Module Issue

The `commission_ax` module has a field definition issue. Here are the solutions:

#### Option A: Temporarily Disable Commission AX
```bash
# Move commission_ax out of addons temporarily
mv commission_ax commission_ax_disabled
docker-compose restart
```

#### Option B: Fix Commission AX Module
The issue is in `commission_ax/models/sale_order.py` line 292:

```python
# Current (problematic):
purchase_order_count = fields.Integer(string="PO Count", compute="_compute_purchase_order_count")

# Should be:
purchase_order_count = fields.Integer(
    string="PO Count", 
    compute="_compute_purchase_order_count",
    store=False,  # Add this
    default=0     # Add this
)
```

### Fix 3: Module Installation Order

Install modules in this specific order:
1. Base Odoo modules (account, base, portal)
2. Deep Ocean Reports
3. Commission modules last

## 🔧 STEP-BY-STEP SOLUTION

### Step 1: Restart Clean Environment
```bash
cd "/d/GitHub/osus_main/cleanup osus/OSUSAPPS"
docker-compose down
docker-compose up -d
```

### Step 2: Update Core Modules First
```bash
docker-compose exec odoo odoo --stop-after-init --update=base,account,portal -d odoo
```

### Step 3: Install Deep Ocean Reports
```bash
docker-compose exec odoo odoo --stop-after-init --install=osus_deep_ocean_reports -d odoo
```

### Step 4: If Commission AX Still Causes Issues
```bash
# Uninstall commission_ax temporarily
docker-compose exec odoo odoo --stop-after-init --uninstall=commission_ax -d odoo

# Install Deep Ocean Reports
docker-compose exec odoo odoo --stop-after-init --install=osus_deep_ocean_reports -d odoo

# Reinstall commission_ax if needed
docker-compose exec odoo odoo --stop-after-init --install=commission_ax -d odoo
```

## ✅ VERIFICATION

After installation, verify:

1. **Deep Ocean Module Works**:
   - Go to Accounting > Customer Invoices
   - Create/edit an invoice
   - Check for "Deep Ocean Theme" tab
   - Toggle "Use Deep Ocean Theme"
   - Use "Print Deep Ocean Invoice" button

2. **No JavaScript Errors**:
   - Open browser console (F12)
   - Navigate to sale orders
   - Should not show purchase_order_count errors

## 🔍 PREVENTION

To prevent this issue in future:
1. Always test module dependencies carefully
2. Remove unnecessary dependencies (like 'sale' for invoice-only modules)
3. Install modules in proper dependency order
4. Use proper field definitions with defaults and store parameters

## 📝 CURRENT STATUS

- ✅ Fixed: Removed unnecessary 'sale' dependency from Deep Ocean Reports
- ✅ Ready: Module is now isolated from commission_ax conflicts
- 🔄 Next: Follow installation steps above to complete fix

The Deep Ocean Reports module should now install and work correctly without the purchase_order_count error!