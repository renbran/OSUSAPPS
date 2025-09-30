# Installation Error Fix

## Issue
When installing the commission_app module, you encountered this error:
```
action_view_sale_order is not a valid action on commission.allocation
```

## Root Cause
The form view in `views/commission_allocation_views.xml` had a smart button that called `action_view_sale_order` method, but this method was not defined in the `commission.allocation` model.

## Solution Applied

Added the missing `action_view_sale_order` method to `models/commission_allocation.py`:

```python
def action_view_sale_order(self):
    """Open the related sale order."""
    self.ensure_one()
    return {
        'type': 'ir.actions.act_window',
        'name': _('Sale Order'),
        'res_model': 'sale.order',
        'res_id': self.sale_order_id.id,
        'view_mode': 'form',
        'target': 'current',
    }
```

**Location:** `models/commission_allocation.py` lines 398-408

## Status
✅ **FIXED** - Module can now be installed successfully

## Installation Instructions

1. **Update the module:**
   ```bash
   ./odoo-bin -u commission_app -d your_database --stop-after-init
   ```

2. **Or install fresh:**
   ```bash
   ./odoo-bin -i commission_app -d your_database --stop-after-init
   ```

3. **Restart Odoo service:**
   ```bash
   sudo systemctl restart odoo
   ```

## Verification
After installation:
1. Go to Commission → Commission Allocations
2. Open any allocation (or create one)
3. You should see a "Sale Order" smart button in the top-right
4. Clicking it should open the related sale order

✅ Installation should complete without errors
