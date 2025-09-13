#!/usr/bin/env python3
"""
Test script to validate XML ID references and loading order
"""

import logging
import os
import xml.etree.ElementTree as ET

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def validate_xml_id_references():
    """Check if all XML ID references exist in the correct order"""
    logger.info("🚀 Validating XML ID References...")
    
    module_path = "payment_account_enhanced"
    
    # Step 1: Extract all XML IDs from view files
    xml_ids = {}
    
    view_files = [
        'views/account_payment_views.xml',
        'views/payment_approval_history_views.xml',
        'views/payment_qr_verification_views.xml',
        'views/payment_dashboard_views.xml'
    ]
    
    logger.info("Step 1: Collecting XML IDs from view files...")
    
    for view_file in view_files:
        file_path = f"{module_path}/{view_file}"
        if os.path.exists(file_path):
            try:
                tree = ET.parse(file_path)
                root = tree.getroot()
                
                # Find all records with IDs
                for record in root.findall('.//record[@id]'):
                    xml_id = record.get('id')
                    xml_ids[xml_id] = view_file
                    
            except ET.ParseError as e:
                logger.error("XML parsing error in %s: %s", view_file, e)
                return False
    
    logger.info("Found %d XML IDs in view files", len(xml_ids))
    
    # Step 2: Check menu references
    logger.info("Step 2: Checking menu references...")
    
    menu_file = f"{module_path}/views/menus.xml"
    if os.path.exists(menu_file):
        try:
            tree = ET.parse(menu_file)
            root = tree.getroot()
            
            # Find all menu items with action references
            for menuitem in root.findall('.//menuitem[@action]'):
                action_ref = menuitem.get('action')
                menu_id = menuitem.get('id')
                
                # Skip empty actions (parent menu items)
                if not action_ref or action_ref.strip() == '':
                    continue
                
                # Extract the action ID (remove module prefix)
                if '.' in action_ref:
                    _, action_id = action_ref.split('.', 1)
                else:
                    action_id = action_ref
                
                if action_id in xml_ids:
                    logger.info("✅ Menu '%s' references existing action '%s' from %s", 
                              menu_id, action_id, xml_ids[action_id])
                else:
                    logger.error("❌ Menu '%s' references missing action '%s'", menu_id, action_id)
                    logger.error("Available actions: %s", list(xml_ids.keys()))
                    return False
                    
        except ET.ParseError as e:
            logger.error("XML parsing error in menus.xml: %s", e)
            return False
    
    # Step 3: Check manifest loading order
    logger.info("Step 3: Checking manifest loading order...")
    
    manifest_file = f"{module_path}/__manifest__.py"
    if os.path.exists(manifest_file):
        with open(manifest_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find data files section
        data_start = content.find("'data': [")
        data_end = content.find("],", data_start)
        data_section = content[data_start:data_end]
        
        # Check if views are loaded before menus
        views_pos = data_section.find("'views/account_payment_views.xml'")
        menus_pos = data_section.find("'views/menus.xml'")
        
        if views_pos < menus_pos and views_pos != -1 and menus_pos != -1:
            logger.info("✅ Loading order correct: views loaded before menus")
        else:
            logger.error("❌ Loading order incorrect: menus loaded before views")
            return False
    
    logger.info("=" * 65)
    logger.info("📊 XML ID VALIDATION SUMMARY")
    logger.info("=" * 65)
    logger.info("🎉 ALL XML ID REFERENCES VALIDATED!")
    logger.info("✅ All menu actions exist")
    logger.info("✅ Loading order is correct")
    logger.info("🔧 Module should install without XML ID errors")
    
    return True

if __name__ == "__main__":
    import sys
    try:
        success = validate_xml_id_references()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error("Validation failed: %s", e)
        sys.exit(1)