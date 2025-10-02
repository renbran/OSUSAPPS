# ❌ NEW ERROR: landlord_id Field Reference Issue

## Error Details
```
KeyError: 'Field landlord_id referenced in related field definition property.rental.owner_id does not exist.'
```

## Analysis

**Problem**: A model called `property.rental` has a field `owner_id` that tries to use `related="...landlord_id"`, but the `landlord_id` field doesn't exist on the target model.

**Issue**: The model `property.rental` doesn't exist in the current codebase - this appears to be:
1. An old model name that was changed
2. A field definition left in the database from a previous version
3. Or from another module extending rental_management

## Investigation Results

✅ Searched all Python files - NO `property.rental` model found
✅ Searched all XML files - NO `property.rental` references
✅ All current models using `landlord_id` are correct
✅ No `owner_id` field definitions found in code

## Root Cause

This is a **DATABASE INCONSISTENCY** issue where:
- Old model definitions exist in `ir.model` or `ir.model.fields` tables
- The field `property.rental.owner_id` is defined in database
- But the actual model/field doesn't exist in code anymore

## Solution Options

### Option 1: Clean Module Update (RECOMMENDED)
```bash
# Update with init to recreate all model definitions
ssh root@139.84.163.11 "cd /var/odoo/scholarixv17 && sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf --no-http --stop-after-init -d scholarixv17 -i rental_management"
```

### Option 2: Database Cleanup
```sql
-- Connect to database
psql -U odoo -d scholarixv17

-- Find the problematic field
SELECT id, name, model FROM ir_model_fields WHERE name='owner_id' AND model='property.rental';

-- Delete the field (if found)
DELETE FROM ir_model_fields WHERE name='owner_id' AND model='property.rental';

-- Find the problematic model
SELECT id, model FROM ir_model WHERE model='property.rental';

-- Delete the model (if found)
DELETE FROM ir_model WHERE model='property.rental';
```

### Option 3: Full Reinstall (SAFEST)
```bash
1. Backup database
2. Uninstall rental_management from Odoo UI
3. Restart Odoo
4. Install rental_management fresh
```

## Recommended Action

**Try Option 1 first** - Clean module reinstall with `-i` flag:

```bash
ssh root@139.84.163.11 "cd /var/odoo/scholarixv17 && sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf --no-http --stop-after-init -d scholarixv17 -i rental_management"
```

This will:
- Reinstall the module
- Recreate all model definitions
- Clean up old/invalid fields
- Fix the sequence field issue at the same time

## Alternative: Database Direct Fix

If reinstall doesn't work, clean the database manually:

```bash
ssh root@139.84.163.11
su - postgres
psql scholarixv17

-- Clean up old model
DELETE FROM ir_model_fields WHERE model='property.rental';
DELETE FROM ir_model WHERE model='property.rental';

-- Then update module
cd /var/odoo/scholarixv17
sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf --no-http --stop-after-init -d scholarixv17 --update=rental_management
```

## Status

- ✅ Sequence field fixed in code
- ✅ Cache cleaned
- ❌ Database has old field references
- ⏳ Needs module reinstall or database cleanup

## Files to Deploy

When database is clean, deploy these fixes:
- rental_management/models/property_payment_plan.py (sequence field added)
- rental_management/views/property_payment_plan_view.xml (handle widget added)
