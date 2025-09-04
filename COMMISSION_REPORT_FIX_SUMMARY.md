# Commission Report Data Extraction Fix

## Problem Identified
The commission report was showing "No commission data found" even though commission data was visible in sale orders as product lines (e.g., "PRIMARY COMMISSION" products).

## Root Cause Analysis
The commission_ax module stores commission data in **two different ways**:
1. **Commission Fields**: Direct fields on sale.order (consultant_commission, manager_commission, etc.)
2. **Commission Products**: Order lines with commission products (PRIMARY COMMISSION, etc.)

The commission_statement module was only extracting data from **commission fields** but ignoring **commission product lines**.

## Solution Implemented

### 1. Enhanced Main Extraction Method
Updated `_extract_commission_lines()` method to use both extraction approaches:
- Extract from commission fields (original method)
- Extract from commission product lines (new method)

### 2. Added New Methods

#### `_extract_commission_from_order_lines(order)`
- Scans order lines for commission products
- Identifies commission products by name containing "commission"
- Maps commission products to partners based on product names
- Converts product data to commission line format

#### `_extract_partner_from_commission_line(line, order)`
- Maps commission product types to appropriate partners:
  - "PRIMARY COMMISSION" → consultant_id
  - "MANAGER COMMISSION" → manager_id
  - "BROKER COMMISSION" → broker_partner_id
  - etc.

#### `_extract_role_from_commission_line(line)`
- Determines role based on commission product name
- Returns human-readable role names

#### `_should_include_commission_line(commission_line)`
- Applies user filters to commission lines
- Handles zero commission filter
- Handles partner-specific filter
- Handles commission type filters

### 3. Enhanced Data Structure
Commission lines from products include additional fields:
- `product_name`: Name of commission product
- `description`: Product description
- `quantity`: Product quantity
- `unit_price`: Product unit price
- `category`: Set to 'product' for identification

## How It Works

### Before Fix
1. Search sale orders in date range ✓
2. For each order, look for commission fields (consultant_commission, manager_commission, etc.) ✗ **Data not found**
3. Generate report with no data

### After Fix
1. Search sale orders in date range ✓
2. For each order:
   - Extract from commission fields (if any) ✓
   - **NEW**: Extract from commission product lines ✓
   - Combine both data sources ✓
3. Generate report with complete data ✓

## Example Data Extraction

For a sale order with "PRIMARY COMMISSION" product line:
```
Product: PRIMARY COMMISSION
Description: KARMA 609
Quantity: 0.0475
Unit Price: 867,866.00
Subtotal: 41,223.64 AED
```

The system now extracts:
```
{
    'partner_name': 'John Smith',           # From order.consultant_id
    'partner_id': 123,
    'order_ref': 'SO001',
    'customer_ref': 'Customer ABC',
    'commission_type': 'fixed',
    'commission_type_display': 'Product Commission',
    'amount': 41223.64,                     # From line.price_subtotal
    'category': 'product',
    'product_name': 'PRIMARY COMMISSION',
    'description': 'KARMA 609',
    'quantity': 0.0475,
    'unit_price': 867866.00,
}
```

## Testing Instructions

1. **Update Module**: Update commission_statement module in Odoo
   ```bash
   docker-compose exec odoo odoo --update=commission_statement --stop-after-init
   ```

2. **Restart Odoo**: Restart the Odoo service
   ```bash
   docker-compose restart odoo
   ```

3. **Generate Report**: 
   - Go to Accounting → Reports → Commission Statement Report
   - Select date range that includes orders with commission products
   - Generate report

4. **Expected Results**:
   - Report should now show commission data from product lines
   - Lines will show "Product Commission" as commission type
   - Partner information extracted from order fields
   - Commission amounts from product line subtotals

## Files Modified

1. **commission_statement/models/commission_report_wizard.py**
   - Enhanced `_extract_commission_lines()` method
   - Added `_extract_commission_from_order_lines()` method
   - Added `_extract_partner_from_commission_line()` method  
   - Added `_extract_role_from_commission_line()` method
   - Added `_should_include_commission_line()` method

## Verification

The fix addresses the specific issue where:
- ✅ Commission products are visible in sale orders
- ✅ Commission reports now extract data from product lines
- ✅ Partners are correctly identified from order fields
- ✅ Commission amounts are taken from product line subtotals
- ✅ Existing field-based commission extraction continues to work
- ✅ Both data sources are combined in final report

This ensures comprehensive commission reporting that captures all commission data regardless of how it's stored in the system.
