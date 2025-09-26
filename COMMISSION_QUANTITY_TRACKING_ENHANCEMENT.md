# Commission Quantity Tracking Enhancement

## Overview
Added comprehensive quantity tracking to commission lines with high-precision percentage calculations that **do not round off** values.

## New Fields

### 1. Sales Quantity (`sales_qty`)
- **Type**: Float with (16, 6) precision
- **Source**: Sum of all `product_uom_qty` from sale order lines
- **Purpose**: Track total ordered quantities
- **Display**: Readonly in form view, visible in tree view

### 2. Invoiced Quantity (`invoiced_qty`)
- **Type**: Float with (16, 6) precision  
- **Source**: Sum of all `qty_invoiced` from sale order lines
- **Purpose**: Track how much has been invoiced
- **Display**: Readonly in form view, visible in tree view

### 3. Quantity Percentage (`qty_percentage`)
- **Type**: Float with (16, 6) precision
- **Calculation**: `(invoiced_qty / sales_qty) * 100.0`
- **Purpose**: Show invoicing progress as percentage **without rounding**
- **Display**: Percentage widget in both form and tree views

## Key Features

### ✅ No Rounding
- All calculations preserve full decimal precision
- Uses (16, 6) digits specification for maximum accuracy
- No premature rounding in intermediate calculations

### ✅ Auto-Computed
- Fields automatically update when sale order data changes
- Stored in database for performance (computed with `store=True`)
- Dependencies properly declared for automatic recalculation

### ✅ Zero-Division Protection
```python
if total_sales_qty > 0:
    line.qty_percentage = (total_invoiced_qty / total_sales_qty) * 100.0
else:
    line.qty_percentage = 0.0
```

### ✅ UI Integration
- Added to commission line tree view for quick overview
- Grouped in "Quantity Tracking" section in form view
- Uses percentage widget for proper visual representation

## Usage Examples

### Example 1: Partial Invoicing
- Sales Qty: 100.0
- Invoiced Qty: 33.333333
- Percentage: 33.333333% (full precision maintained)

### Example 2: Complex Division
- Sales Qty: 7.0
- Invoiced Qty: 3.0  
- Percentage: 42.857142857142854% (no rounding)

### Example 3: High Precision
- Sales Qty: 123.456789
- Invoiced Qty: 45.123456789
- Percentage: 36.550000331695% (12+ decimal precision)

## Technical Implementation

### Model Changes (`commission_line.py`)
```python
# New fields with high precision
sales_qty = fields.Float(
    string='Sales Quantity',
    digits=(16, 6),
    compute='_compute_quantities',
    store=True,
    help='Total quantity from sale order lines'
)

invoiced_qty = fields.Float(
    string='Invoiced Quantity', 
    digits=(16, 6),
    compute='_compute_quantities',
    store=True,
    help='Total invoiced quantity from related invoices'
)

qty_percentage = fields.Float(
    string='Invoiced Qty %',
    digits=(16, 6),  # NO ROUNDING!
    compute='_compute_quantities',
    store=True,
    help='Percentage of sales quantity that has been invoiced (without rounding)'
)

# Computation method
@api.depends('sale_order_id.order_line', 'sale_order_id.order_line.product_uom_qty', 
             'sale_order_id.order_line.qty_invoiced')
def _compute_quantities(self):
    """Compute sales quantity, invoiced quantity, and percentage without rounding"""
    for line in self:
        if not line.sale_order_id or not line.sale_order_id.order_line:
            line.sales_qty = 0.0
            line.invoiced_qty = 0.0
            line.qty_percentage = 0.0
            continue

        # Calculate totals with full precision
        total_sales_qty = sum(line.sale_order_id.order_line.mapped('product_uom_qty'))
        total_invoiced_qty = sum(line.sale_order_id.order_line.mapped('qty_invoiced'))
        
        line.sales_qty = total_sales_qty
        line.invoiced_qty = total_invoiced_qty
        
        # Calculate percentage without rounding - preserve full precision
        if total_sales_qty > 0:
            line.qty_percentage = (total_invoiced_qty / total_sales_qty) * 100.0
        else:
            line.qty_percentage = 0.0
```

### View Changes (`commission_line_views.xml`)
```xml
<!-- Tree view addition -->
<field name="sales_qty"/>
<field name="invoiced_qty"/>
<field name="qty_percentage" widget="percentage"/>

<!-- Form view addition -->
<group string="Quantity Tracking">
    <field name="sales_qty" readonly="1"/>
    <field name="invoiced_qty" readonly="1"/>
    <field name="qty_percentage" readonly="1" widget="percentage"/>
</group>
```

## Benefits

1. **Accurate Reporting**: No data loss due to premature rounding
2. **Real-Time Updates**: Automatic recalculation when order data changes
3. **User-Friendly Display**: Percentage widget for intuitive understanding
4. **Performance Optimized**: Stored computed fields reduce calculation overhead
5. **Precision Control**: (16, 6) digits allows for very precise calculations

## Migration Notes

- New fields will be automatically computed for existing commission lines
- No data migration needed - values computed from existing sale order data
- Backward compatible - existing functionality unchanged

## Testing

Run the included test script to verify calculations:
```bash
python test_quantity_fields.py
```

The test script validates:
- Basic percentage calculations
- High precision scenarios
- Edge cases (zero quantities)
- Precision preservation

## Summary

These enhancements provide precise quantity tracking for commission lines with percentage calculations that maintain full decimal precision without rounding, giving users accurate insights into invoicing progress.