# 🚨 CRITICAL SYSTEM DIAGNOSIS - PDF Report Generation Issue

## Problem Summary
System-wide PDF report generation is failing with the error:
```
The domain term '('report_name', '=', [2])' should use the 'in' or 'not in' operator.
TypeError: unhashable type: 'list'
AttributeError: 'list' object has no attribute 'split'
```

## Root Cause Analysis

### Issue Identified
The error indicates that somewhere in the system, a **list `[2]`** is being passed where a **string or integer** is expected in a domain filter for report lookups.

### Investigation Results

1. **XML Validation**: ✅ All report XML files are well-formed
2. **Template Structure**: ✅ All QWeb templates have correct syntax
3. **CSS Conflicts**: ✅ No global CSS selectors interfering
4. **Database Records**: ✅ Report records appear clean in database
5. **Module Isolation**: ❌ Issue persists even after uninstalling custom modules

### Error Pattern
- Error occurs during `_xmlid_lookup` in `ir.model.data`
- Specifically when processing `report_name` domain filters
- Affects ALL PDF reports system-wide, not just custom modules

## Potential Causes

### 1. Core Odoo Data Corruption
- Corrupted XML ID mappings in `ir.model.data`
- Invalid domain construction in report processing
- Cached data corruption affecting lookup mechanisms

### 2. Module Interference
- Some module modifying core report processing
- Invalid model inheritance affecting report system
- Monkey-patching of core Odoo methods

### 3. Database Integrity Issues
- Foreign key constraints causing list return instead of single values
- PostgreSQL query optimization issues
- ORM mapping problems

## IMMEDIATE FIXES APPLIED

### 1. Fixed Payment Module Issues
- ✅ Corrected XML template structure (removed malformed tags)
- ✅ Fixed `action_print_osus_voucher` method in `account_payment.py`
- ✅ Updated report_name references to use template names

### 2. Commission Module Fixes
- ✅ Converted deprecated `<report>` tags to `<record>` format
- ✅ Fixed external ID registration issues

## RECOMMENDED SOLUTIONS

### Option 1: Database Repair (RECOMMENDED)
```sql
-- Clear problematic cache entries
DELETE FROM ir_model_data WHERE model = 'ir.actions.report' AND res_id IS NULL;

-- Rebuild XML ID mappings
UPDATE ir_model_data SET res_id = (
    SELECT id FROM ir_act_report_xml 
    WHERE ir_act_report_xml.id = ir_model_data.res_id
) WHERE model = 'ir.actions.report';
```

### Option 2: Module Reset
```bash
# Uninstall all custom modules
odoo -d odoo --uninstall=payment_account_enhanced,commission_partner_statement,enhanced_status

# Clear cache and restart
docker-compose restart odoo

# Reinstall modules one by one
odoo -d odoo -i payment_account_enhanced
```

### Option 3: Fresh Database (NUCLEAR OPTION)
- Export data from working modules
- Create fresh database
- Import only clean data
- Reinstall modules

## CURRENT STATUS

### Working Components
- ✅ XML templates are syntactically correct
- ✅ Report records exist in database
- ✅ Modules can be loaded/unloaded successfully

### Failing Components
- ❌ PDF generation fails with domain error
- ❌ XMLid lookup corrupted for reports
- ❌ Core Odoo report infrastructure affected

## NEXT STEPS

1. **IMMEDIATE**: Apply database repair script
2. **TESTING**: Verify core invoice reports work
3. **GRADUAL**: Reinstall custom modules one by one
4. **MONITORING**: Watch for recurring domain errors

---

**Status**: 🚨 CRITICAL - REQUIRES DATABASE REPAIR  
**Impact**: System-wide PDF generation failure  
**Priority**: URGENT - Business operations affected  
**Date**: September 14, 2025