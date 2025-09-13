#!/usr/bin/env python3
"""
Test script for enhanced_status module custom_state field
"""

def test_custom_state_field():
    """Test that custom_state field is properly added"""
    print("Testing enhanced_status module...")
    
    # Test field definition
    try:
        from odoo.addons.enhanced_status.models.sale_order_simple import SaleOrder
        print("✅ SaleOrder model imported successfully")
        
        # Check if custom_state field exists in the model
        if hasattr(SaleOrder, '_fields') and 'custom_state' in SaleOrder._fields:
            print("✅ custom_state field found in model")
            
            # Check field type and options
            field = SaleOrder._fields['custom_state']
            if hasattr(field, 'selection'):
                print("✅ custom_state is Selection field")
                print(f"   Selection options: {field.selection}")
            else:
                print("❌ custom_state is not a Selection field")
                
            if hasattr(field, 'default'):
                print(f"✅ Default value: {field.default}")
            else:
                print("❌ No default value set")
                
        else:
            print("❌ custom_state field not found")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_custom_state_field()
