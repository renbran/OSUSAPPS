#!/usr/bin/env python3
"""
Script to check and fix commission calculation method issues
Run this script in the Odoo shell: odoo shell -d dbname
"""

# Check commission types
print("=== Checking Commission Types ===")
try:
    commission_types = env['commission.type'].search([])
    print(f"Found {len(commission_types)} commission types:")
    for ct in commission_types:
        print(f"  - {ct.name}: '{ct.calculation_method}'")
except Exception as e:
    print(f"Error checking commission types: {e}")

print("\n=== Checking Commission Lines ===")
try:
    commission_lines = env['commission.line'].search([])
    valid_methods = ['fixed', 'percentage_unit', 'percentage_total', 'percentage_untaxed']
    invalid_lines = []
    
    for line in commission_lines:
        if line.calculation_method not in valid_methods:
            invalid_lines.append(line)
    
    print(f"Found {len(commission_lines)} commission lines total")
    print(f"Found {len(invalid_lines)} lines with invalid calculation methods:")
    
    for line in invalid_lines:
        print(f"  - Line {line.id}: '{line.calculation_method}' (invalid)")
        
    # Fix invalid lines
    if invalid_lines:
        print("\n=== Fixing Invalid Lines ===")
        for line in invalid_lines:
            old_method = line.calculation_method
            if old_method == 'percentage':
                line.calculation_method = 'percentage_total'
                print(f"  - Fixed line {line.id}: '{old_method}' -> 'percentage_total'")
            else:
                line.calculation_method = 'percentage_total'
                print(f"  - Fixed line {line.id}: '{old_method}' -> 'percentage_total' (default)")
        
        env.cr.commit()
        print(f"Successfully fixed {len(invalid_lines)} commission lines")
    else:
        print("No invalid commission lines found")

except Exception as e:
    print(f"Error checking commission lines: {e}")

print("\n=== Summary ===")
print("Commission calculation method mapping:")
print("  Commission Type -> Commission Line")
print("  'percentage'    -> 'percentage_total'")
print("  'fixed'         -> 'fixed'")
print("  'tiered'        -> 'percentage_total'")