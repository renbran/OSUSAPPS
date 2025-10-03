@echo off
REM Complete Fix for Missing Product Record (ID: 11)
echo ========================================
echo COMPLETE FIX: Missing Product Record
echo ========================================
echo.

echo Connecting to database and applying fix...
echo.

REM Execute all-in-one fix via Odoo shell
docker compose exec odoo odoo shell -d odoo << 'PYTHON_SCRIPT'

# Get valid default products
product_1 = env.ref('rental_management.property_product_1', raise_if_not_found=False)
product_2 = env.ref('rental_management.property_product_2', raise_if_not_found=False)
product_3 = env.ref('rental_management.property_product_3', raise_if_not_found=False)
product_4 = env.ref('rental_management.property_product_4', raise_if_not_found=False)

print("="*60)
print("Valid Products Found:")
print("="*60)
if product_1:
    print(f"Property Payment ID: {product_1.id} - {product_1.name}")
if product_2:
    print(f"Property Deposit ID: {product_2.id} - {product_2.name}")
if product_3:
    print(f"Broker Commission ID: {product_3.id} - {product_3.name}")
if product_4:
    print(f"Property Maintenance ID: {product_4.id} - {product_4.name}")
print("")

# Fix config parameters
IrConfigParam = env['ir.config_parameter'].sudo()
print("Updating configuration parameters...")

if product_1:
    IrConfigParam.set_param('rental_management.account_installment_item_id', str(product_1.id))
    print(f"✓ Set installment_item_id to {product_1.id}")

if product_2:
    IrConfigParam.set_param('rental_management.account_deposit_item_id', str(product_2.id))
    print(f"✓ Set deposit_item_id to {product_2.id}")

if product_3:
    IrConfigParam.set_param('rental_management.account_broker_item_id', str(product_3.id))
    print(f"✓ Set broker_item_id to {product_3.id}")

if product_4:
    IrConfigParam.set_param('rental_management.account_maintenance_item_id', str(product_4.id))
    print(f"✓ Set maintenance_item_id to {product_4.id}")

# Commit changes
env.cr.commit()
print("")
print("="*60)
print("✅ FIX COMPLETED SUCCESSFULLY!")
print("="*60)
print("All configuration parameters have been updated.")
print("The missing product record error should now be resolved.")
print("")

PYTHON_SCRIPT

echo.
echo ========================================
echo Fix completed! Please refresh your Odoo browser.
echo ========================================
pause
