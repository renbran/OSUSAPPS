#!/usr/bin/env python3
"""
Emergency Fix: Add missing sequence column to property_payment_plan tables

Run this via Odoo shell:
    docker compose exec odoo odoo shell -d odoo < rental_management/fix_payment_plan_sequence.py

Or copy-paste the code below into Odoo shell.
"""

def fix_payment_plan_sequence():
    """Add sequence column to property_payment_plan tables"""
    
    env = globals().get('env')
    if not env:
        print("ERROR: Must be run via Odoo shell")
        return
    
    cr = env.cr
    
    print("\n" + "="*70)
    print("FIX: Adding sequence column to payment plan tables")
    print("="*70)
    
    # Fix property_payment_plan table
    print("\n1. Checking property_payment_plan table...")
    cr.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='property_payment_plan' 
        AND column_name='sequence'
    """)
    
    if not cr.fetchone():
        print("   Adding sequence column...")
        cr.execute("""
            ALTER TABLE property_payment_plan 
            ADD COLUMN sequence INTEGER DEFAULT 10
        """)
        
        cr.execute("""
            UPDATE property_payment_plan 
            SET sequence = id * 10
        """)
        print("   ✅ Sequence column added to property_payment_plan")
    else:
        print("   ℹ️  Sequence column already exists")
    
    # Fix property_payment_plan_line table
    print("\n2. Checking property_payment_plan_line table...")
    cr.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='property_payment_plan_line' 
        AND column_name='sequence'
    """)
    
    if not cr.fetchone():
        print("   Adding sequence column...")
        cr.execute("""
            ALTER TABLE property_payment_plan_line 
            ADD COLUMN sequence INTEGER DEFAULT 10
        """)
        
        cr.execute("""
            UPDATE property_payment_plan_line 
            SET sequence = id * 10
        """)
        print("   ✅ Sequence column added to property_payment_plan_line")
    else:
        print("   ℹ️  Sequence column already exists")
    
    # Commit changes
    cr.commit()
    
    # Verify
    print("\n" + "="*70)
    print("VERIFICATION:")
    print("="*70)
    
    cr.execute("""
        SELECT COUNT(*) as total, COUNT(sequence) as with_sequence
        FROM property_payment_plan
    """)
    result = cr.fetchone()
    print(f"\nproperty_payment_plan:")
    print(f"  Total records: {result[0]}")
    print(f"  With sequence: {result[1]}")
    
    cr.execute("""
        SELECT COUNT(*) as total, COUNT(sequence) as with_sequence
        FROM property_payment_plan_line
    """)
    result = cr.fetchone()
    print(f"\nproperty_payment_plan_line:")
    print(f"  Total records: {result[0]}")
    print(f"  With sequence: {result[1]}")
    
    print("\n" + "="*70)
    print("✅ FIX COMPLETED!")
    print("="*70)
    print("\nNext steps:")
    print("1. Restart Odoo: docker compose restart odoo")
    print("2. Refresh your browser")
    print("3. The error should be resolved")
    print()

# Run the fix
if __name__ == '__main__':
    fix_payment_plan_sequence()
else:
    # When run via Odoo shell
    fix_payment_plan_sequence()
