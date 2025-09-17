-- Database Cleanup Script for Foreign Key Violations
-- ====================================================
-- 
-- This script fixes the foreign key constraint violations by cleaning up
-- orphaned access rights and security groups.
--
-- Run this in the Odoo database (psql) as the database user.

-- Step 1: Clean up orphaned access rights that reference non-existent groups
DELETE FROM ir_model_access 
WHERE group_id IN (507, 508, 509, 510);

-- Step 2: Clean up orphaned security groups (if they still exist)
DELETE FROM res_groups 
WHERE id IN (507, 508, 509, 510);

-- Step 3: Clean up orphaned attachment files (optional - careful with this)
-- This removes database references to files that don't exist
-- DELETE FROM ir_attachment 
-- WHERE store_fname IS NOT NULL 
-- AND NOT EXISTS (
--     SELECT 1 FROM pg_stat_file('/var/odoo/.local/share/Odoo/filestore/staging-erposus.com/' || store_fname)
-- );

-- Step 4: Verify cleanup
SELECT 'Orphaned access rights remaining:' as check_type, COUNT(*) as count
FROM ir_model_access 
WHERE group_id IN (507, 508, 509, 510)
UNION ALL
SELECT 'Orphaned groups remaining:' as check_type, COUNT(*) as count
FROM res_groups 
WHERE id IN (507, 508, 509, 510);

-- Step 5: Check for any other foreign key constraint issues
SELECT 
    'ir_model_access referencing non-existent groups:' as issue,
    COUNT(*) as count
FROM ir_model_access ima
LEFT JOIN res_groups rg ON ima.group_id = rg.id
WHERE ima.group_id IS NOT NULL AND rg.id IS NULL;