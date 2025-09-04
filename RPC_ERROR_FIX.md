# 🚨 RPC Error Fix - Missing Report Reference

## Error Description
```
ValueError: External ID not found in the system: your_module.action_commission_statement_pdf
```

## Root Cause
The `commission_ax/wizards/commission_statement_wizard.py` file contained a placeholder reference `'your_module.action_commission_statement_pdf'` that was never replaced with the actual report XML ID.

## Fix Applied

### File: `commission_ax/wizards/commission_statement_wizard.py`

**Before (Line 46):**
```python
return self.env.ref('your_module.action_commission_statement_pdf').report_action(self, data=data)
```

**After:**
```python
return self.env.ref('commission_ax.action_report_commission_statement').report_action(self, data=data)
```

## Verification
- ✅ Correct XML ID exists in `commission_ax/reports/commission_statement_report.xml`
- ✅ Report model matches wizard model: `commission.partner.statement.wizard`
- ✅ No other instances of `your_module` placeholder found

## Deployment Instructions

1. **Update commission_ax module:**
   ```bash
   docker-compose exec odoo odoo --update=commission_ax --stop-after-init
   ```

2. **Restart Odoo:**
   ```bash
   docker-compose restart odoo
   ```

3. **Test PDF Generation:**
   - Navigate to commission report wizard
   - Click "Generate PDF Report" button
   - Should now work without RPC error

## Status
✅ **FIXED** - Placeholder reference replaced with correct XML ID

This fix resolves the RPC error that occurred when trying to generate PDF commission reports.
