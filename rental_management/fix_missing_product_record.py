#!/usr/bin/env python3
"""
Fix Missing Product Record Error
---------------------------------
This script identifies and fixes missing product.product(11) references
in the rental_management module.

Error: Record does not exist or has been deleted. (Record: product.product(11,), User: 2)

Run this script via Odoo shell:
    docker-compose exec odoo odoo shell -d odoo < fix_missing_product_record.py
"""

import logging

_logger = logging.getLogger(__name__)

def fix_missing_product_references():
    """Find and fix all references to missing product.product(11)"""
    
    env = globals().get('env')
    if not env:
        print("ERROR: This script must be run via Odoo shell")
        return
    
    print("\n" + "="*80)
    print("DIAGNOSTIC: Missing Product Record (ID: 11)")
    print("="*80)
    
    # 1. Check if product.product(11) exists
    product_11 = env['product.product'].browse(11)
    print(f"\n1. Product ID 11 exists: {product_11.exists()}")
    if product_11.exists():
        print(f"   Name: {product_11.name}")
        print(f"   Active: {product_11.active}")
    
    # 2. Check configuration settings
    print("\n2. Checking Rental Management Configuration Settings...")
    config_params = [
        'rental_management.account_installment_item_id',
        'rental_management.account_deposit_item_id',
        'rental_management.account_broker_item_id',
        'rental_management.account_maintenance_item_id',
    ]
    
    IrConfigParam = env['ir.config_parameter'].sudo()
    for param in config_params:
        value = IrConfigParam.get_param(param)
        print(f"   {param}: {value}")
        if value == '11':
            print(f"   ⚠️  FOUND REFERENCE TO PRODUCT 11 in {param}")
    
    # 3. Check wizards for product references
    print("\n3. Checking Wizard Records...")
    
    # Booking wizard
    try:
        booking_wizards = env['property.vendor.payment.wizard'].search([
            '|', ('booking_item_id', '=', 11), ('broker_item_id', '=', 11)
        ])
        if booking_wizards:
            print(f"   ⚠️  Found {len(booking_wizards)} booking wizard(s) referencing product 11")
    except Exception as e:
        print(f"   Booking wizard check: {e}")
    
    # Contract wizard
    try:
        contract_wizards = env['property.contract.wizard'].search([
            '|', '|', '|',
            ('installment_item_id', '=', 11),
            ('deposit_item_id', '=', 11),
            ('broker_item_id', '=', 11),
            ('maintenance_item_id', '=', 11)
        ])
        if contract_wizards:
            print(f"   ⚠️  Found {len(contract_wizards)} contract wizard(s) referencing product 11")
    except Exception as e:
        print(f"   Contract wizard check: {e}")
    
    # Payment wizard
    try:
        payment_wizards = env['property.payment.wizard'].search([
            ('service_id', '=', 11)
        ])
        if payment_wizards:
            print(f"   ⚠️  Found {len(payment_wizards)} payment wizard(s) referencing product 11")
    except Exception as e:
        print(f"   Payment wizard check: {e}")
    
    # 4. Suggest fixes
    print("\n" + "="*80)
    print("RECOMMENDED FIXES:")
    print("="*80)
    
    # Get valid default products
    default_products = {
        'property_product_1': env.ref('rental_management.property_product_1', raise_if_not_found=False),
        'property_product_2': env.ref('rental_management.property_product_2', raise_if_not_found=False),
        'property_product_3': env.ref('rental_management.property_product_3', raise_if_not_found=False),
        'property_product_4': env.ref('rental_management.property_product_4', raise_if_not_found=False),
    }
    
    print("\nAvailable Default Products:")
    for key, product in default_products.items():
        if product:
            print(f"   {key}: ID={product.id}, Name='{product.name}'")
    
    print("\n✅ To fix this issue, run the following commands in Odoo shell:\n")
    
    if default_products['property_product_1']:
        print(f"# Fix installment item")
        print(f"env['ir.config_parameter'].sudo().set_param('rental_management.account_installment_item_id', '{default_products['property_product_1'].id}')")
    
    if default_products['property_product_2']:
        print(f"\n# Fix deposit item")
        print(f"env['ir.config_parameter'].sudo().set_param('rental_management.account_deposit_item_id', '{default_products['property_product_2'].id}')")
    
    if default_products['property_product_3']:
        print(f"\n# Fix broker item")
        print(f"env['ir.config_parameter'].sudo().set_param('rental_management.account_broker_item_id', '{default_products['property_product_3'].id}')")
    
    if default_products['property_product_4']:
        print(f"\n# Fix maintenance item")
        print(f"env['ir.config_parameter'].sudo().set_param('rental_management.account_maintenance_item_id', '{default_products['property_product_4'].id}')")
    
    print("\nenv.cr.commit()")
    print("="*80)

# Execute the diagnostic
if __name__ == '__main__':
    fix_missing_product_references()
else:
    # When run via Odoo shell
    fix_missing_product_references()
