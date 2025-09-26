"""
Commission Line Partner Mismatch Investigation
"""

def investigate_partner_mismatch():
    """
    This investigation script should be run in Odoo shell to identify 
    why commission lines might be showing wrong partner names.
    
    Possible causes:
    1. Commission partner field incorrectly mapped
    2. Display name computation error  
    3. Partner record corruption/deletion
    4. Cache issues
    5. Legacy data migration issues
    """
    
    print("""
Run this in Odoo shell:

import logging
_logger = logging.getLogger(__name__)

# 1. Check recent commission lines for partner mapping issues
print("1. CHECKING RECENT COMMISSION LINES")
print("=" * 40)

commission_lines = env['commission.line'].search([], limit=10, order='id desc')

for line in commission_lines:
    print(f"Commission Line ID: {line.id}")
    print(f"  Partner ID: {line.partner_id.id if line.partner_id else 'None'}")
    print(f"  Partner Name: '{line.partner_id.name if line.partner_id else 'None'}'")
    print(f"  Sale Order: {line.sale_order_id.name if line.sale_order_id else 'None'}")
    print(f"  Sale Customer: '{line.sale_order_id.partner_id.name if line.sale_order_id and line.sale_order_id.partner_id else 'None'}'")
    print(f"  Display Name: '{line.display_name}'")
    print(f"  Commission Type: '{line.commission_type_id.name if line.commission_type_id else 'None'}'")
    print("")

# 2. Check for cache/computation issues
print("\\n2. CHECKING DISPLAY NAME COMPUTATION")  
print("=" * 40)

# Force recompute display names
commission_lines._compute_display_name()

for line in commission_lines:
    expected_name = f"{line.partner_id.name} - {line.commission_type_id.name}" if line.partner_id and line.commission_type_id else 'Commission Line'
    actual_name = line.display_name
    
    if expected_name != actual_name:
        print(f"❌ MISMATCH Line {line.id}:")
        print(f"   Expected: '{expected_name}'")
        print(f"   Actual: '{actual_name}'")
    else:
        print(f"✅ OK Line {line.id}: '{actual_name}'")

# 3. Check partner existence and integrity
print("\\n3. CHECKING PARTNER INTEGRITY")
print("=" * 40)

for line in commission_lines:
    if line.partner_id:
        try:
            # Test partner access
            partner_name = line.partner_id.name
            partner_exists = line.partner_id.exists()
            supplier_rank = line.partner_id.supplier_rank
            
            print(f"Line {line.id} Partner Check:")
            print(f"  Partner exists: {partner_exists}")
            print(f"  Partner name: '{partner_name}'")  
            print(f"  Supplier rank: {supplier_rank}")
            
            if not partner_exists:
                print(f"  ❌ ISSUE: Partner does not exist!")
            elif supplier_rank <= 0:
                print(f"  ⚠️  WARNING: Partner not configured as supplier")
                
        except Exception as e:
            print(f"  ❌ ERROR accessing partner: {e}")
    else:
        print(f"Line {line.id}: No partner assigned")

# 4. Check if commission partner is showing as sale order customer
print("\\n4. CHECKING FOR PARTNER CONFUSION")
print("=" * 40)

for line in commission_lines:
    if line.partner_id and line.sale_order_id and line.sale_order_id.partner_id:
        commission_partner = line.partner_id.name
        sale_customer = line.sale_order_id.partner_id.name
        
        if commission_partner == sale_customer:
            print(f"❌ ISSUE Line {line.id}: Commission partner same as sale customer!")
            print(f"   Both are: '{commission_partner}'")
            print(f"   This might indicate incorrect commission assignment")
        else:
            print(f"✅ OK Line {line.id}:")
            print(f"   Commission Partner: '{commission_partner}'")
            print(f"   Sale Customer: '{sale_customer}'")

# 5. Check commission line creation audit trail
print("\\n5. CHECKING CREATION AUDIT")
print("=" * 40)

for line in commission_lines:
    print(f"Line {line.id} Audit:")
    print(f"  Created: {line.create_date}")
    print(f"  Created by: {line.create_uid.name if line.create_uid else 'Unknown'}")
    print(f"  Last modified: {line.write_date}")  
    print(f"  Modified by: {line.write_uid.name if line.write_uid else 'Unknown'}")
    print(f"  Is Legacy: {line.is_legacy if hasattr(line, 'is_legacy') else 'N/A'}")

print("\\nInvestigation complete!")
print("\\nIf you see issues above, the problem might be:")
print("- Incorrect commission line creation logic")
print("- Legacy data migration issues")  
print("- Partner record deletion/corruption")
print("- Cache/computation problems")
    """)

if __name__ == "__main__":
    investigate_partner_mismatch()