-- Commission AX Module Database Cleanup Script
-- Run this to clean corrupted installation data

-- Remove module record (will force fresh installation)
DELETE FROM ir_module_module WHERE name = 'commission_ax';

-- Remove any orphaned model records
DELETE FROM ir_model WHERE model LIKE 'commission.%' AND modules = 'commission_ax';

-- Remove orphaned access rights
DELETE FROM ir_model_access WHERE name LIKE '%commission%' AND perm_read IS NULL;

-- Remove orphaned menu items
DELETE FROM ir_ui_menu WHERE module = 'commission_ax';

-- Remove orphaned views
DELETE FROM ir_ui_view WHERE module = 'commission_ax';

-- Remove orphaned actions
DELETE FROM ir_actions_act_window WHERE res_model LIKE 'commission.%';

-- Remove orphaned security groups (be careful with this)
-- DELETE FROM res_groups WHERE name LIKE '%Commission%' AND category_id IS NULL;

-- Clean up ir_model_data entries
DELETE FROM ir_model_data WHERE module = 'commission_ax';

-- Clean up any remaining foreign key references
-- (This is database-specific and may need adjustment)

-- Show what's left
SELECT 'Remaining commission tables:' as info;
SELECT tablename FROM pg_tables WHERE tablename LIKE 'commission_%';

SELECT 'Remaining commission models:' as info;
SELECT model FROM ir_model WHERE model LIKE 'commission.%';

SELECT 'Remaining commission menu items:' as info;
SELECT name FROM ir_ui_menu WHERE name LIKE '%Commission%';