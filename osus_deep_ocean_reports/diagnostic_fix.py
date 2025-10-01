#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deep Ocean Reports - Diagnostic and Fix Script
==============================================

This script helps diagnose and fix issues with the Deep Ocean Reports module
and related dependency conflicts.
"""

import os
import sys
import json

def check_module_dependencies():
    """Check module dependencies and detect conflicts."""
    print("🔍 Checking Deep Ocean Reports Module Dependencies...")
    
    manifest_path = os.path.join(os.path.dirname(__file__), '__manifest__.py')
    
    if not os.path.exists(manifest_path):
        print("❌ __manifest__.py not found!")
        return False
        
    with open(manifest_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    print("✅ Manifest file found")
    
    # Check if 'sale' is in dependencies
    if "'sale'" in content:
        print("⚠️  WARNING: 'sale' dependency found - this may cause conflicts")
        print("   Deep Ocean Reports only needs: account, base, portal")
        return False
    else:
        print("✅ Dependencies look good (no sale dependency)")
        return True

def check_commission_ax_conflict():
    """Check for commission_ax module conflicts."""
    print("\n🔍 Checking for Commission AX Module Conflicts...")
    
    commission_ax_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 
        'commission_ax'
    )
    
    if os.path.exists(commission_ax_path):
        print("⚠️  Commission AX module found - checking for conflicts...")
        
        # Check sale_order.py
        sale_order_path = os.path.join(commission_ax_path, 'models', 'sale_order.py')
        if os.path.exists(sale_order_path):
            with open(sale_order_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if 'purchase_order_count' in content:
                print("✅ purchase_order_count field found in commission_ax")
                
                # Check if compute method exists
                if '_compute_purchase_order_count' in content:
                    print("✅ Compute method found")
                else:
                    print("❌ Compute method missing!")
                    return False
            else:
                print("❌ purchase_order_count field missing!")
                return False
        else:
            print("❌ sale_order.py not found in commission_ax!")
            return False
    else:
        print("ℹ️  Commission AX module not found - no conflict expected")
        
    return True

def generate_fix_recommendations():
    """Generate fix recommendations."""
    print("\n🔧 Fix Recommendations:")
    print("="*50)
    
    print("\n1. IMMEDIATE FIX - Remove sale dependency from Deep Ocean Reports:")
    print("   Edit __manifest__.py and change:")
    print("   FROM: 'depends': ['account', 'base', 'sale', 'portal']")
    print("   TO:   'depends': ['account', 'base', 'portal']")
    
    print("\n2. COMMISSION AX MODULE FIX:")
    print("   The error suggests commission_ax module has issues.")
    print("   Try these steps:")
    print("   a) Uninstall commission_ax module temporarily")
    print("   b) Install Deep Ocean Reports")
    print("   c) Reinstall commission_ax if needed")
    
    print("\n3. ODOO UPDATE SEQUENCE:")
    print("   Run these commands in order:")
    print("   docker-compose exec odoo odoo --stop-after-init --update=all -d odoo")
    print("   docker-compose restart")
    
    print("\n4. MODULE INSTALLATION ORDER:")
    print("   1. First install: base, account, portal")
    print("   2. Then install: Deep Ocean Reports")
    print("   3. Finally install: other modules")

def main():
    """Main diagnostic function."""
    print("🌊 Deep Ocean Reports - Diagnostic Tool")
    print("="*45)
    
    deps_ok = check_module_dependencies()
    commission_ok = check_commission_ax_conflict()
    
    if deps_ok and commission_ok:
        print("\n✅ All checks passed! Module should work correctly.")
    else:
        print("\n❌ Issues detected - see recommendations below.")
        
    generate_fix_recommendations()
    
    print("\n🔍 Next Steps:")
    print("1. Apply the recommended fixes above")
    print("2. Restart Odoo containers: docker-compose restart")
    print("3. Update modules: docker-compose exec odoo odoo --stop-after-init --update=osus_deep_ocean_reports -d odoo")
    print("4. Test the module installation")

if __name__ == "__main__":
    main()