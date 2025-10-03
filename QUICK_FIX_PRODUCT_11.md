# QUICK FIX: Missing Product Record (ID: 11)

## Error
```
Missing Record
Record does not exist or has been deleted.
(Record: product.product(11,), User: 2)
```

## IMMEDIATE FIX - Choose ONE method:

### Method 1: Run the Fix Script (EASIEST) ✅
Double-click this file in Windows Explorer:
```
FIX_NOW_PRODUCT_11.bat
```

### Method 2: Manual Command Line
Open Command Prompt in this folder and run:
```bash
docker compose exec odoo odoo shell -d odoo
```

Then paste this code and press Enter:
```python
# Quick fix
p1 = env.ref('rental_management.property_product_1', raise_if_not_found=False)
p2 = env.ref('rental_management.property_product_2', raise_if_not_found=False)
p3 = env.ref('rental_management.property_product_3', raise_if_not_found=False)
p4 = env.ref('rental_management.property_product_4', raise_if_not_found=False)

ICP = env['ir.config_parameter'].sudo()
if p1: ICP.set_param('rental_management.account_installment_item_id', str(p1.id))
if p2: ICP.set_param('rental_management.account_deposit_item_id', str(p2.id))
if p3: ICP.set_param('rental_management.account_broker_item_id', str(p3.id))
if p4: ICP.set_param('rental_management.account_maintenance_item_id', str(p4.id))

env.cr.commit()
print("✅ Fixed!")
```

Press Ctrl+D to exit.

### Method 3: Via Odoo UI
1. Open Odoo
2. Enable Developer Mode (Settings → Activate Developer Mode)
3. Go to: Settings → Technical → Parameters → System Parameters
4. Find these parameters and delete them (they will be recreated automatically):
   - `rental_management.account_installment_item_id`
   - `rental_management.account_deposit_item_id`
   - `rental_management.account_broker_item_id`
   - `rental_management.account_maintenance_item_id`
5. Go to: Rental Management → Configuration → Settings
6. Click "Save" (this will recreate the parameters with correct values)

## What This Fix Does
It updates the system configuration to use the correct product IDs for:
- Property Payment
- Property Deposit  
- Broker Commission
- Property Maintenance

## After Fix
1. Refresh your browser (F5)
2. The error should be gone
3. Continue using Odoo normally

## Need Help?
If the error persists, restart Odoo:
```bash
docker compose restart odoo
```
