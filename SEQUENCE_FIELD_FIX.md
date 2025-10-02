# SEQUENCE FIELD ERROR - FIXED ✅

## New Error Found
```
ValueError: Invalid field 'sequence' on model 'property.payment.plan'
```

## Root Cause
The `PropertyPaymentPlan` model had `_order = 'sequence, id'` defined, but the `sequence` field was missing from the model definition.

## Files Fixed

### 1. rental_management/models/property_payment_plan.py
**Added**: `sequence` field to PropertyPaymentPlan model
```python
sequence = fields.Integer(string='Sequence', default=10, help='Used to order payment plans')
```

### 2. rental_management/views/property_payment_plan_view.xml
**Updated Tree View**: Added sequence field with handle widget for drag-and-drop reordering
```xml
<field name="sequence" widget="handle"/>
```

**Updated Form View**: Added sequence field (visible only to technical users)
```xml
<field name="sequence" groups="base.group_no_one"/>
```

## Update Command

Run this to apply the fix:

```bash
ssh root@139.84.163.11 "cd /var/odoo/scholarixv17 && sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf --no-http --stop-after-init -d scholarixv17 --update=rental_management"
```

Or double-click: **FIX_SEQUENCE_ERROR.bat**

## What This Enables

1. ✅ Payment Plans menu will now open without error
2. ✅ Users can drag-and-drop rows to reorder payment plans in tree view
3. ✅ System can properly sort payment plans by sequence
4. ✅ Database will have proper sequence column added automatically

## Expected Behavior After Fix

- Navigate to: Rental Management → Configurations → Payment Plans
- List view will show payment plans ordered by sequence
- Drag the handle icon (☰) to reorder plans
- Order is preserved in the database

## Technical Details

- **Field Type**: Integer
- **Default Value**: 10
- **Widget**: handle (for drag-and-drop)
- **Visibility**: Normal in tree, technical users only in form
- **Database**: Column will be added automatically during module update

---

**Status**: Code fixed, ready to update on server
**Time to fix**: 30 seconds (just run the update command)
