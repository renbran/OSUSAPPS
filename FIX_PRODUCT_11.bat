@echo off
echo ========================================
echo Fix Missing Product Record (ID: 11)
echo ========================================
echo.

echo Step 1: Checking if product 11 exists...
docker compose exec db psql -U odoo -d odoo -c "SELECT id, name, active FROM product_product WHERE id = 11;"
echo.

echo Step 2: Finding config parameters referencing product 11...
docker compose exec db psql -U odoo -d odoo -c "SELECT key, value FROM ir_config_parameter WHERE value = '11' AND key LIKE '%%rental_management%%';"
echo.

echo Step 3: Getting valid replacement products...
docker compose exec db psql -U odoo -d odoo -c "SELECT pp.id, pp.name FROM product_product pp JOIN ir_model_data imd ON imd.res_id = pp.id WHERE imd.module = 'rental_management' AND imd.model = 'product.product' AND imd.name IN ('property_product_1', 'property_product_2', 'property_product_3', 'property_product_4') ORDER BY pp.id;"
echo.

echo Step 4: Please note the product IDs above, then run the UPDATE commands below:
echo Example: If property_product_1 has ID 15, then run:
echo docker compose exec db psql -U odoo -d odoo -c "UPDATE ir_config_parameter SET value = '15' WHERE key LIKE '%%rental_management.account%%item_id' AND value = '11';"
echo.

pause
