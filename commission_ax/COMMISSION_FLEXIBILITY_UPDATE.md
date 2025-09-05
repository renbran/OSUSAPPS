# Commission Module Flexibility Update

## Issue Resolution: Overly Restrictive Commission Processing

### Problem
The `commission_ax` module was being too restrictive and preventing purchase order creation for commissions even when orders were invoiced and fully paid. The module had these rigid requirements:

1. **Sale order must be fully invoiced** with posted invoices
2. **Only one order line allowed** per sale order
3. **No flexibility** for edge cases or manual overrides

### Solution Implemented

#### 1. **Flexible Prerequisites Check** (`_check_commission_prerequisites`)

**Before:** Only allowed commission processing if order was fully invoiced with posted invoices.

**After:** Now allows commission processing if ANY of these conditions are met:
- ✅ Fully invoiced with posted invoices (original strict requirement)
- ✅ Has invoices AND is fully paid
- ✅ Order is in 'done' state (delivered orders)

#### 2. **Force Process Option** (`action_force_process_commissions`)

Added a new "Force Process (Skip Checks)" button that allows managers to bypass prerequisites when needed:
- Only requires confirmed sale order and positive amount
- Bypasses invoice and payment requirements
- Includes confirmation dialog for safety
- Creates commission purchase orders immediately

#### 3. **Relaxed Single Order Line Constraint**

**Before:** Hard block preventing any sale order with multiple lines.

**After:** Smart constraint that:
- ✅ Allows multiple lines for commission managers
- ✅ Allows multiple lines for confirmed orders  
- ✅ Shows warning message instead of blocking
- ⚠️ Optional: Can still enforce strict mode by uncommenting one line

### How to Use

#### Regular Processing
1. Go to Sale Order → Commission tab
2. Click "Process Commissions" (uses flexible prerequisites)
3. System will create purchase orders if order meets any of the flexible criteria

#### Force Processing (When Needed)
1. Go to Sale Order → Commission tab  
2. Click "Force Process (Skip Checks)" (red button)
3. Confirm the action
4. Commission purchase orders are created immediately

### Benefits

- **Improved Workflow:** Users can process commissions for paid orders even if invoicing isn't complete
- **Manager Override:** Commission managers can force processing when business needs require it
- **Better User Experience:** Warning messages instead of hard blocks for order lines
- **Backward Compatibility:** Original strict mode still works for organizations that need it

### Safety Features

- Force process includes confirmation dialog
- All actions are logged and auditable
- Original validation logic is preserved as option
- Commission managers get additional permissions

### Technical Details

**Files Modified:**
- `models/sale_order.py`: Updated prerequisites and added force methods
- `views/sale_order.xml`: Added force process button

**New Methods:**
- `action_force_process_commissions()`: Force commission processing
- `_force_create_commission_purchase_orders()`: Bypass prerequisites creation

**Updated Methods:**
- `_check_commission_prerequisites()`: More flexible validation
- `_check_single_order_line()`: Warning instead of error
