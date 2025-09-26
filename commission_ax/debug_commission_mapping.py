#!/usr/bin/env python3
"""
Commission Line Mapping Diagnostic Script
Checks for inconsistencies in commission line partner mapping
"""

def check_commission_mapping():
    """Check commission line partner mapping for inconsistencies"""
    print("Commission Line Mapping Diagnostic Report")
    print("=" * 50)
    
    # This script needs to be run from within Odoo environment
    print("""
This script needs to be run from within the Odoo shell environment.
To run this diagnostic:

1. Start Odoo shell:
   docker-compose exec odoo odoo shell

2. Run the following commands in the shell:

import logging
_logger = logging.getLogger(__name__)

# Check commission line mapping
commission_lines = env['commission.line'].search([], limit=20, order='id desc')

print("Recent Commission Lines Mapping Check:")
print("=" * 60)

issues_found = []

for line in commission_lines:
    try:
        sale_order = line.sale_order_id
        commission_partner = line.partner_id
        
        # Basic data validation
        if not sale_order:
            issues_found.append(f"Commission line {line.id}: No sale order linked")
            continue
            
        if not commission_partner:
            issues_found.append(f"Commission line {line.id}: No commission partner linked")
            continue
            
        # Check if commission partner exists
        if not commission_partner.exists():
            issues_found.append(f"Commission line {line.id}: Commission partner {commission_partner.name} does not exist")
            continue
            
        # Check if sale order exists  
        if not sale_order.exists():
            issues_found.append(f"Commission line {line.id}: Sale order {sale_order.name} does not exist")
            continue
            
        sale_order_customer = sale_order.partner_id
        
        print(f"Line ID: {line.id}")
        print(f"  Sale Order: {sale_order.name}")
        print(f"  Sale Order Customer: {sale_order_customer.name if sale_order_customer else 'N/A'}")
        print(f"  Commission Partner: {commission_partner.name}")
        print(f"  Commission Type: {line.commission_type_id.name if line.commission_type_id else 'N/A'}")
        print(f"  Role: {line.role}")
        print(f"  Category: {line.commission_category}")
        print(f"  Display Name: {line.display_name}")
        print(f"  Rate: {line.rate}%")
        print(f"  Amount: {line.commission_amount} {line.currency_id.name if line.currency_id else 'N/A'}")
        
        # Check for potential issues
        if commission_partner == sale_order_customer:
            print(f"  ⚠️  WARNING: Commission partner same as sale order customer!")
            
        print("-" * 40)
        
    except Exception as e:
        error_msg = f"Commission line {line.id}: Error checking data - {str(e)}"
        issues_found.append(error_msg)
        print(f"  ❌ ERROR: {error_msg}")

print("\nSUMMARY:")
if issues_found:
    print(f"Found {len(issues_found)} issues:")
    for issue in issues_found:
        print(f"  - {issue}")
else:
    print("No critical issues found in commission line mappings.")

# Additional check: Look for duplicate commission assignments
print("\nChecking for duplicate commission assignments...")
duplicates = env['commission.line'].read_group(
    domain=[],
    fields=['sale_order_id', 'partner_id', 'commission_type_id'],
    groupby=['sale_order_id', 'partner_id', 'commission_type_id'],
    having=[('__count', '>', 1)]
)

if duplicates:
    print(f"Found {len(duplicates)} potential duplicate commission assignments:")
    for dup in duplicates:
        print(f"  - Sale Order {dup['sale_order_id'][1]} has duplicate commission for partner {dup['partner_id'][1]}")
else:
    print("No duplicate commission assignments found.")

# Check commission line states
print("\nCommission Line States Summary:")
states = env['commission.line'].read_group(
    domain=[],
    fields=['state'],
    groupby=['state']
)
for state in states:
    print(f"  {state['state']}: {state['state_count']} lines")

print("\nDiagnostic complete!")

    """)

if __name__ == "__main__":
    check_commission_mapping()