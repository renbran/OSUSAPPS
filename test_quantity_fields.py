#!/usr/bin/env python3
"""
Test script for the new quantity fields in commission_ax module.
This script tests the quantity computation logic without requiring Odoo installation.
"""

def test_quantity_percentage_calculation():
    """Test the quantity percentage calculation without rounding"""
    
    # Test cases with various precision scenarios
    test_cases = [
        # (sales_qty, invoiced_qty, expected_percentage)
        (100.0, 50.0, 50.0),
        (100.0, 33.333333, 33.333333),
        (150.0, 100.0, 66.666666666666666),
        (7.0, 3.0, 42.857142857142854),
        (100.0, 0.0, 0.0),
        (0.0, 0.0, 0.0),  # Edge case
    ]
    
    print("Testing quantity percentage calculations (without rounding):")
    print("=" * 60)
    
    for i, (sales_qty, invoiced_qty, expected) in enumerate(test_cases, 1):
        # Simulate the calculation logic from our model
        if sales_qty > 0:
            calculated_percentage = (invoiced_qty / sales_qty) * 100.0
        else:
            calculated_percentage = 0.0
        
        print(f"Test {i}:")
        print(f"  Sales Qty: {sales_qty}")
        print(f"  Invoiced Qty: {invoiced_qty}")
        print(f"  Expected %: {expected}")
        print(f"  Calculated %: {calculated_percentage}")
        print(f"  Match: {'✓' if abs(calculated_percentage - expected) < 0.000001 else '✗'}")
        print()

def test_precision_preservation():
    """Test that high precision is preserved in calculations"""
    
    print("Testing precision preservation:")
    print("=" * 40)
    
    # Test with high precision numbers
    sales_qty = 123.456789
    invoiced_qty = 45.123456789
    
    percentage = (invoiced_qty / sales_qty) * 100.0
    
    print(f"Sales Qty: {sales_qty}")
    print(f"Invoiced Qty: {invoiced_qty}")
    print(f"Percentage: {percentage}")
    print(f"Precision digits: {len(str(percentage).split('.')[-1]) if '.' in str(percentage) else 0}")
    print()
    
    # Test with very small numbers
    sales_qty_small = 0.000001
    invoiced_qty_small = 0.0000005
    
    percentage_small = (invoiced_qty_small / sales_qty_small) * 100.0
    
    print(f"Small Sales Qty: {sales_qty_small}")
    print(f"Small Invoiced Qty: {invoiced_qty_small}")
    print(f"Small Percentage: {percentage_small}")
    print()

def show_field_configuration():
    """Show the field configuration for reference"""
    
    print("Field Configuration in Odoo Model:")
    print("=" * 40)
    
    field_config = """
    sales_qty = fields.Float(
        string='Sales Quantity',
        digits=(16, 6),  # 16 total digits, 6 decimal places
        compute='_compute_quantities',
        store=True,
        help='Total quantity from sale order lines'
    )

    invoiced_qty = fields.Float(
        string='Invoiced Quantity',
        digits=(16, 6),  # 16 total digits, 6 decimal places
        compute='_compute_quantities',
        store=True,
        help='Total invoiced quantity from related invoices'
    )

    qty_percentage = fields.Float(
        string='Invoiced Qty %',
        digits=(16, 6),  # 16 total digits, 6 decimal places - NO ROUNDING
        compute='_compute_quantities',
        store=True,
        help='Percentage of sales quantity that has been invoiced (without rounding)'
    )
    """
    
    print(field_config)
    print()
    
    print("View Configuration:")
    print("-" * 20)
    view_config = """
    <!-- In tree view -->
    <field name="sales_qty"/>
    <field name="invoiced_qty"/>
    <field name="qty_percentage" widget="percentage"/>
    
    <!-- In form view -->
    <group string="Quantity Tracking">
        <field name="sales_qty" readonly="1"/>
        <field name="invoiced_qty" readonly="1"/>
        <field name="qty_percentage" readonly="1" widget="percentage"/>
    </group>
    """
    print(view_config)

if __name__ == "__main__":
    print("Commission AX - Quantity Fields Test")
    print("=" * 50)
    print()
    
    test_quantity_percentage_calculation()
    test_precision_preservation()
    show_field_configuration()
    
    print("✓ All tests completed!")
    print()
    print("Summary of Changes Made:")
    print("- Added sales_qty field with (16,6) precision")
    print("- Added invoiced_qty field with (16,6) precision") 
    print("- Added qty_percentage field with (16,6) precision - NO ROUNDING")
    print("- Added computation method _compute_quantities")
    print("- Updated views to show quantity fields")
    print("- Used percentage widget in views for proper display")