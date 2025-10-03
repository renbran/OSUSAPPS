# Fix: Missing Product Record Error

## Error Description
```
Missing Record
Record does not exist or has been deleted.
(Record: product.product(11,), User: 2)
```

## Root Cause
The system is trying to access `product.product` with ID 11, which no longer exists in the database. This typically happens when:
- A product was deleted manually
- Database was restored from a backup
- Configuration parameters still reference the old product ID

## Solution Options

### Option 1: Via Odoo Shell (Recommended)

1. **Access Odoo Shell:**
   ```bash
   docker-compose exec odoo odoo shell -d odoo
   ```

2. **Run Diagnostic Script:**
   ```bash
   docker-compose exec odoo odoo shell -d odoo < rental_management/fix_missing_product_record.py
   ```

3. **Manual Fix in Shell:**
   ```python
   # Get valid default products
   product_1 = env.ref('rental_management.property_product_1', raise_if_not_found=False)
   product_2 = env.ref('rental_management.property_product_2', raise_if_not_found=False)
   product_3 = env.ref('rental_management.property_product_3', raise_if_not_found=False)
   product_4 = env.ref('rental_management.property_product_4', raise_if_not_found=False)
   
   # Print IDs
   print(f"Property Payment ID: {product_1.id if product_1 else 'Not found'}")
   print(f"Property Deposit ID: {product_2.id if product_2 else 'Not found'}")
   print(f"Broker Commission ID: {product_3.id if product_3 else 'Not found'}")
   print(f"Property Maintenance ID: {product_4.id if product_4 else 'Not found'}")
   
   # Fix config parameters (replace with actual IDs from above)
   IrConfigParam = env['ir.config_parameter'].sudo()
   if product_1:
       IrConfigParam.set_param('rental_management.account_installment_item_id', str(product_1.id))
   if product_2:
       IrConfigParam.set_param('rental_management.account_deposit_item_id', str(product_2.id))
   if product_3:
       IrConfigParam.set_param('rental_management.account_broker_item_id', str(product_3.id))
   if product_4:
       IrConfigParam.set_param('rental_management.account_maintenance_item_id', str(product_4.id))
   
   # Commit changes
   env.cr.commit()
   print("✅ Configuration parameters updated successfully!")
   ```

### Option 2: Via PostgreSQL

1. **Connect to Database:**
   ```bash
   docker-compose exec db psql -U odoo -d odoo
   ```

2. **Run Diagnostic Queries:**
   ```sql
   -- Check if product 11 exists
   SELECT id, name, active FROM product_product WHERE id = 11;
   
   -- Find config parameters referencing product 11
   SELECT * FROM ir_config_parameter 
   WHERE value = '11' 
     AND key LIKE '%rental_management%';
   
   -- Get valid replacement product IDs
   SELECT pp.id, pp.name 
   FROM product_product pp
   JOIN ir_model_data imd ON imd.res_id = pp.id
   WHERE imd.module = 'rental_management' 
     AND imd.model = 'product.product'
     AND imd.name IN ('property_product_1', 'property_product_2', 
                      'property_product_3', 'property_product_4');
   ```

3. **Update Configuration (replace XXX with actual product ID):**
   ```sql
   UPDATE ir_config_parameter 
   SET value = 'XXX' 
   WHERE key LIKE '%rental_management.account_%_item_id' 
     AND value = '11';
   ```

### Option 3: Via Odoo UI

1. **Go to Settings → Technical → Parameters → System Parameters**
2. **Search for:** `rental_management.account`
3. **Find parameters with value = 11:**
   - `rental_management.account_installment_item_id`
   - `rental_management.account_deposit_item_id`
   - `rental_management.account_broker_item_id`
   - `rental_management.account_maintenance_item_id`
4. **Update each to valid product ID** (get from Sales → Products)

### Option 4: Reinstall Module Data

```bash
# Update module and force reinstall data
docker-compose exec odoo odoo -d odoo -u rental_management --load-language=en_US --stop-after-init

# Or reset to default products
docker-compose exec odoo odoo shell -d odoo
```

Then in shell:
```python
# Reset default products
env['ir.config_parameter'].sudo().set_param('rental_management.account_installment_item_id', False)
env['ir.config_parameter'].sudo().set_param('rental_management.account_deposit_item_id', False)
env['ir.config_parameter'].sudo().set_param('rental_management.account_broker_item_id', False)
env['ir.config_parameter'].sudo().set_param('rental_management.account_maintenance_item_id', False)
env.cr.commit()

# Trigger default values
config = env['res.config.settings'].create({})
config.execute()
```

## Verification

After applying the fix, verify:

1. **Check Configuration:**
   ```bash
   docker-compose exec odoo odoo shell -d odoo
   ```
   ```python
   params = ['rental_management.account_installment_item_id',
             'rental_management.account_deposit_item_id',
             'rental_management.account_broker_item_id',
             'rental_management.account_maintenance_item_id']
   
   for param in params:
       value = env['ir.config_parameter'].sudo().get_param(param)
       if value:
           product = env['product.product'].browse(int(value))
           print(f"{param}: {value} - {product.name if product.exists() else 'NOT FOUND!'}")
   ```

2. **Test in UI:**
   - Go to: **Rental Management → Configuration → Settings**
   - Check that product fields show valid products
   - Try creating a new rental contract or payment

## Prevention

To prevent this issue in the future:

1. **Never delete system products** created by modules
2. **Archive instead of delete** - Set `active = False` on products
3. **Check dependencies** before deleting records
4. **Backup database** before major changes

## Files Created

- `rental_management/fix_missing_product_record.py` - Python diagnostic script
- `rental_management/fix_missing_product_record.sql` - SQL queries
- `rental_management/FIX_MISSING_PRODUCT_RECORD.md` - This guide

## Related Files

- `rental_management/models/res_config.py` - Configuration settings
- `rental_management/data/property_product_data.xml` - Default products definition

## Support

If the issue persists:
1. Check Odoo logs: `docker-compose logs -f odoo | grep "product.product(11"`
2. Review any custom modifications to product records
3. Consider restoring from a backup if data integrity is compromised
