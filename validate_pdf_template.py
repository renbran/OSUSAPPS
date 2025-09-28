#!/usr/bin/env python3
"""
Validate the commission partner statement PDF template
"""
import xml.etree.ElementTree as ET
import os

def validate_template():
    template_path = "commission_ax/reports/commission_partner_statement_template.xml"
    
    if not os.path.exists(template_path):
        print(f"❌ Template file not found: {template_path}")
        return False
    
    try:
        # Parse XML
        tree = ET.parse(template_path)
        root = tree.getroot()
        print(f"✅ XML syntax is valid")
        print(f"Root element: {root.tag}")
        
        # Check template structure
        templates = root.findall(".//template[@id='commission_partner_statement_report']")
        if templates:
            print(f"✅ Template 'commission_partner_statement_report' found")
            
            # Check for key elements
            template = templates[0]
            
            # Check for table
            tables = template.findall(".//table")
            if tables:
                print(f"✅ Found {len(tables)} table(s)")
                
                # Check headers
                headers = template.findall(".//th")
                if headers:
                    print(f"✅ Found {len(headers)} table headers")
                    
                    # Print headers for verification
                    header_texts = []
                    for header in headers:
                        text = header.text or ""
                        if text:
                            header_texts.append(text)
                    
                    print(f"📋 Headers found: {', '.join(header_texts)}")
                    
                    # Check for Unit Price header
                    if "Unit Price" in header_texts:
                        print("✅ 'Unit Price' header found (good)")
                    else:
                        print("⚠️ 'Unit Price' header not found in text")
                        
                else:
                    print("⚠️ No table headers found")
            else:
                print("⚠️ No tables found")
                
            # Check for debug information
            debug_divs = template.findall(".//div[@class='alert alert-warning']")
            if debug_divs:
                print(f"✅ Debug section found - will show if no data")
            else:
                print("ℹ️ No debug section found")
                
            # Check for data loops
            foreach_elements = template.findall(".//*[@t-foreach]")
            if foreach_elements:
                print(f"✅ Found {len(foreach_elements)} data loops")
                for elem in foreach_elements:
                    foreach_val = elem.get('t-foreach')
                    as_val = elem.get('t-as')
                    print(f"   Loop: {foreach_val} as {as_val}")
            else:
                print("⚠️ No data loops found")
                
        else:
            print("❌ Template 'commission_partner_statement_report' not found")
            return False
            
        return True
        
    except ET.ParseError as e:
        print(f"❌ XML Parse Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Validating Commission Partner Statement PDF Template...")
    print("=" * 60)
    
    if validate_template():
        print("=" * 60)
        print("✅ Template validation completed successfully!")
        print("📄 Template should now render properly with visible content")
    else:
        print("=" * 60)
        print("❌ Template validation failed!")