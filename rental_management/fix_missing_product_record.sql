-- Fix Missing Product Record (ID: 11)
-- This SQL script identifies and fixes references to deleted product.product(11)

-- 1. Check if product 11 exists
SELECT id, name, active FROM product_product WHERE id = 11;

-- 2. Find references in configuration parameters
SELECT * FROM ir_config_parameter 
WHERE value = '11' 
  AND key LIKE '%rental_management%';

-- 3. Get valid replacement products
SELECT id, name FROM product_product 
WHERE id IN (
    SELECT res_id FROM ir_model_data 
    WHERE module = 'rental_management' 
      AND model = 'product.product'
      AND name IN ('property_product_1', 'property_product_2', 'property_product_3', 'property_product_4')
);

-- 4. Fix configuration parameters (update with correct product IDs from step 3)
-- Replace XXX with the actual product ID from step 3

-- UPDATE ir_config_parameter 
-- SET value = 'XXX' 
-- WHERE key = 'rental_management.account_installment_item_id' AND value = '11';

-- UPDATE ir_config_parameter 
-- SET value = 'XXX' 
-- WHERE key = 'rental_management.account_deposit_item_id' AND value = '11';

-- UPDATE ir_config_parameter 
-- SET value = 'XXX' 
-- WHERE key = 'rental_management.account_broker_item_id' AND value = '11';

-- UPDATE ir_config_parameter 
-- SET value = 'XXX' 
-- WHERE key = 'rental_management.account_maintenance_item_id' AND value = '11';
