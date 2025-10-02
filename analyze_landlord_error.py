#!/usr/bin/env python3
"""
Analyze the KeyError for landlord_id field reference
"""

# The error message:
# KeyError: 'Field landlord_id referenced in related field definition property.rental.owner_id does not exist.'

# This means:
# - There's a model called 'property.rental' (or it's being referenced)
# - This model has a field called 'owner_id'
# - owner_id is defined as: related="something.landlord_id"
# - But 'landlord_id' doesn't exist on 'something'

print("="*70)
print("ANALYZING: KeyError for landlord_id field reference")
print("="*70)

print("\nError Details:")
print("- Model: property.rental")
print("- Field: owner_id")
print("- Problem: Tries to relate to 'landlord_id' which doesn't exist")

print("\n" + "="*70)
print("POSSIBLE CAUSES:")
print("="*70)

print("\n1. Model name might be different")
print("   - Check if 'property.rental' is actually 'tenancy.details'")
print("   - Check for _inherits or _inherit")

print("\n2. Field might be in a different module")
print("   - Another installed module might be adding owner_id")
print("   - Check dependencies")

print("\n3. Model migration issue")
print("   - Old field reference not updated")
print("   - Database has old field definition")

print("\n" + "="*70)
print("SOLUTION:")
print("="*70)

print("\nNeed to find where 'owner_id' is defined with related='...landlord_id'")
print("This could be in:")
print("- XML view files (computed/related fields)")
print("- Other modules that extend rental_management")  
print("- Database (old field definitions)")

print("\n" + "="*70)
