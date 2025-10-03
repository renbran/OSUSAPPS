@echo off
echo Fixing Missing Product Record (ID: 11)...
echo.
docker compose exec odoo odoo shell -d odoo -c "p1=env.ref('rental_management.property_product_1',raise_if_not_found=False);p2=env.ref('rental_management.property_product_2',raise_if_not_found=False);p3=env.ref('rental_management.property_product_3',raise_if_not_found=False);p4=env.ref('rental_management.property_product_4',raise_if_not_found=False);ICP=env['ir.config_parameter'].sudo();ICP.set_param('rental_management.account_installment_item_id',str(p1.id)) if p1 else None;ICP.set_param('rental_management.account_deposit_item_id',str(p2.id)) if p2 else None;ICP.set_param('rental_management.account_broker_item_id',str(p3.id)) if p3 else None;ICP.set_param('rental_management.account_maintenance_item_id',str(p4.id)) if p4 else None;env.cr.commit();print('✅ Fixed successfully!')"
echo.
echo Done! Please refresh your browser.
pause
