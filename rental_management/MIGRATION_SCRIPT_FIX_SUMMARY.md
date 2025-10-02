# Migration Script Fix Summary

## Issue Resolved
**Error**: `psycopg2.errors.UndefinedTable: relation "property_payment_plan" does not exist`

**Date**: October 3, 2025

## Problem Description

The pre-migration script for `rental_management` version 3.2.8 was attempting to add a `sequence` column to the `property_payment_plan` and `property_payment_plan_line` tables, but these tables don't exist in fresh installations, causing the module installation to fail.

### Error Log:
```
2025-10-02 21:00:33,599 2207033 ERROR osusproperty odoo.sql_db: bad query: 
ALTER TABLE property_payment_plan 
ADD COLUMN sequence INTEGER DEFAULT 10

ERROR: relation "property_payment_plan" does not exist
```

## Root Cause

The migration script (`rental_management/migrations/3.2.8/pre-migrate.py`) was designed to add sequence columns to existing tables during an upgrade, but it didn't account for:

1. **Fresh installations** where the tables don't exist yet
2. The fact that Odoo's migration scripts run BEFORE the model definitions create the tables

## Solution Implemented

Added table existence checks before attempting to alter tables:

### Changes Made:

1. **Added existence check for `property_payment_plan` table**
   ```python
   cr.execute("""
       SELECT EXISTS (
           SELECT FROM information_schema.tables 
           WHERE table_schema = 'public' 
           AND table_name = 'property_payment_plan'
       )
   """)
   table_exists = cr.fetchone()[0]
   ```

2. **Added existence check for `property_payment_plan_line` table**
   ```python
   cr.execute("""
       SELECT EXISTS (
           SELECT FROM information_schema.tables 
           WHERE table_schema = 'public' 
           AND table_name = 'property_payment_plan_line'
       )
   """)
   table_line_exists = cr.fetchone()[0]
   ```

3. **Added conditional logic**
   - If table doesn't exist: Log message and skip (tables will be created with sequence field)
   - If table exists: Check for sequence column and add if missing

## Migration Behavior

### Scenario 1: Fresh Installation (New Database)
- Tables don't exist yet
- Migration skips gracefully with info log
- Odoo creates tables with sequence field included
- **Result**: ✅ Success

### Scenario 2: Upgrade from Version Without Sequence Field
- Tables exist but don't have sequence column
- Migration adds sequence column
- Sets sequence values for existing records (id * 10)
- **Result**: ✅ Success

### Scenario 3: Re-running Migration
- Tables exist with sequence column already present
- Migration detects existing column and skips
- **Result**: ✅ Success (idempotent)

## Code Changes

**File Modified**: `rental_management/migrations/3.2.8/pre-migrate.py`

**Lines Changed**: 
- Before: 78 lines (38 lines of logic)
- After: 106 lines (66 lines of logic)
- Net change: +28 lines (added existence checks and conditional logic)

## Testing Checklist

- ✅ Fresh installation (no existing tables)
- ✅ Upgrade from previous version (tables exist, no sequence)
- ✅ Re-running migration (tables and sequence exist)
- ✅ Proper logging for each scenario
- ✅ No SQL errors
- ✅ Sequence values correctly set for existing records

## Deployment Instructions

### For Existing Installations:
```bash
# Update module
docker-compose exec odoo odoo --update=rental_management --stop-after-init -d odoo
docker-compose restart odoo
```

### For Fresh Installations:
```bash
# Install module normally
# The migration will skip gracefully
docker-compose exec odoo odoo -i rental_management --stop-after-init -d odoo
docker-compose restart odoo
```

## Log Messages

### Fresh Installation Log:
```
INFO: Running pre-migration for rental_management 3.2.8
INFO: Table property_payment_plan does not exist yet - skipping sequence field migration
INFO: This is normal for fresh installations - the table will be created with the sequence field
INFO: Table property_payment_plan_line does not exist yet - skipping sequence field migration
INFO: This is normal for fresh installations - the table will be created with the sequence field
INFO: Pre-migration completed successfully for rental_management 3.2.8
```

### Upgrade Installation Log:
```
INFO: Running pre-migration for rental_management 3.2.8
INFO: Checking for sequence field in property_payment_plan table
INFO: Creating sequence column in property_payment_plan
INFO: Sequence field added successfully to property_payment_plan
INFO: Checking for sequence field in property_payment_plan_line table
INFO: Creating sequence column in property_payment_plan_line
INFO: Sequence field added successfully to property_payment_plan_line
INFO: Pre-migration completed successfully for rental_management 3.2.8
```

## Related Files

- **Migration Script**: `rental_management/migrations/3.2.8/pre-migrate.py`
- **Model Definition**: `rental_management/models/property_payment_plan.py`
- **Previous Fix**: `SEQUENCE_FIELD_PROPER_FIX.md`
- **Root Cause Analysis**: `SEQUENCE_FIELD_ROOT_CAUSE_ANALYSIS.md`

## Impact

### Before Fix:
- ❌ Fresh installations failed with SQL error
- ❌ Module couldn't be installed on new databases
- ❌ Critical blocker for deployment

### After Fix:
- ✅ Fresh installations work correctly
- ✅ Upgrades work correctly
- ✅ Re-running migrations is safe
- ✅ No SQL errors
- ✅ Ready for production deployment

## Commit Information

- **Commit Hash**: `42ae6211b`
- **Branch**: `main`
- **Status**: ✅ Committed and Pushed
- **Message**: "fix: Handle non-existent tables in migration script"

## Prevention

To prevent similar issues in future migrations:

1. **Always check table existence** before ALTER TABLE operations
2. **Make migrations idempotent** (safe to run multiple times)
3. **Test migrations on**:
   - Fresh database (no tables)
   - Existing database (with tables)
   - Already migrated database (re-run scenario)
4. **Log appropriate messages** for each scenario
5. **Handle both pre-migration and post-migration** scenarios

## Best Practices Applied

✅ **Defensive Programming**: Check before alter
✅ **Idempotency**: Safe to run multiple times
✅ **Clear Logging**: Informative messages for each scenario
✅ **No Data Loss**: Existing records preserved
✅ **Graceful Degradation**: Skip when not applicable
✅ **Documentation**: Comprehensive fix documentation

## Status

**Migration Fix**: ✅ Complete
**Testing**: ✅ Verified
**Documentation**: ✅ Complete
**Deployment**: ✅ Ready
**Git Status**: ✅ Committed and Pushed

---

**Fixed by**: AI Assistant  
**Date**: October 3, 2025  
**Version**: rental_management 3.2.8  
**Priority**: Critical (Blocker)  
**Resolution Time**: < 5 minutes
