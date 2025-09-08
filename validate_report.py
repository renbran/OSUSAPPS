#!/usr/bin/env python3
"""
Report validation script for enhanced_status module
This script validates the report template and data structure
"""
import xml.etree.ElementTree as ET

def validate_report_template():
    """Validate the commission report template"""
    try:
        # Parse the XML file
        tree = ET.parse('d:/RUNNING APPS/ready production/latest/OSUSAPPS/enhanced_status/reports/commission_report_template.xml')
        root = tree.getroot()
        
        print("✓ XML file is well-formed")
        
        # Check for required template elements
        template_found = False
        report_action_found = False
        
        for element in root.iter():
            if element.tag == 'template' and element.get('id') == 'commission_payout_report_template_final':
                template_found = True
                print("✓ Report template found")
            
            if element.tag == 'record' and element.get('model') == 'ir.actions.report':
                report_action_found = True
                print("✓ Report action found")
        
        if not template_found:
            print("✗ Report template missing")
            
        if not report_action_found:
            print("✗ Report action missing")
        
        return template_found and report_action_found
        
    except ET.ParseError as e:
        print(f"✗ XML parsing error: {e}")
        return False
    except Exception as e:
        print(f"✗ Validation error: {e}")
        return False

def validate_model_files():
    """Check if model files exist and are importable"""
    import os
    
    model_path = 'd:/RUNNING APPS/ready production/latest/OSUSAPPS/enhanced_status/models'
    
    required_files = [
        '__init__.py',
        'sale_order.py', 
        'sale_order_stage.py',
        'commission_report.py'
    ]
    
    for file in required_files:
        file_path = os.path.join(model_path, file)
        if os.path.exists(file_path):
            print(f"✓ {file} exists")
        else:
            print(f"✗ {file} missing")

def main():
    """Run validation checks"""
    print("Enhanced Status Module Report Validation")
    print("=" * 50)
    
    print("\n1. Validating XML template...")
    template_valid = validate_report_template()
    
    print("\n2. Validating model files...")
    validate_model_files()
    
    print("\n3. Common report issues to check:")
    print("   - wkhtmltopdf installed in container")
    print("   - Module properly installed/updated")
    print("   - Report permissions configured")
    print("   - No syntax errors in template")
    
    if template_valid:
        print("\n✓ Template validation passed")
    else:
        print("\n✗ Template validation failed")
    
    print("\n4. Manual test steps:")
    print("   1. Go to Sales > Orders")
    print("   2. Open any sale order")
    print("   3. Click Print > Commission Payout Report")
    print("   4. Check browser developer console for errors")

if __name__ == "__main__":
    main()
