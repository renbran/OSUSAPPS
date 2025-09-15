#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Odoo Filestore Cleanup Script
Fixes missing attachment files that cause FileNotFoundError
"""

import psycopg2
import os
import sys

def fix_missing_filestore_files():
    """Fix missing filestore files by cleaning up orphaned database records"""
    
    print("🔧 FIXING MISSING FILESTORE FILES")
    print("=" * 50)
    
    # Database connection parameters
    DB_CONFIG = {
        'host': 'localhost',
        'port': 5432,
        'database': 'odoo',  # Change to your database name
        'user': 'odoo',
        'password': 'odoo'
    }
    
    try:
        # Connect to database
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("✅ Connected to database")
        
        # Find the specific missing file
        missing_hash = "abf07d417765a61ef36cdde9947cd6c37892fd3a"
        
        cursor.execute("""
            SELECT id, name, res_model, res_id, store_fname, create_date 
            FROM ir_attachment 
            WHERE store_fname LIKE %s
        """, (f'%{missing_hash}%',))
        
        records = cursor.fetchall()
        
        if records:
            print(f"📋 Found {len(records)} attachment record(s) with missing file:")
            
            for record in records:
                id, name, res_model, res_id, store_fname, create_date = record
                print(f"  ID: {id}")
                print(f"  Name: {name}")
                print(f"  Model: {res_model}")
                print(f"  Resource ID: {res_id}")
                print(f"  File: {store_fname}")
                print(f"  Created: {create_date}")
                print("-" * 30)
                
                # Check if file actually exists
                filestore_path = f"/var/odoo/.local/share/Odoo/filestore/staging-erposus.com/{store_fname[:2]}/{store_fname}"
                
                if not os.path.exists(filestore_path):
                    print(f"❌ File missing: {filestore_path}")
                    
                    # Ask for confirmation before deletion
                    response = input(f"Delete orphaned attachment record ID {id}? (y/N): ")
                    
                    if response.lower() == 'y':
                        cursor.execute("DELETE FROM ir_attachment WHERE id = %s", (id,))
                        conn.commit()
                        print(f"✅ Deleted orphaned record ID {id}")
                    else:
                        print(f"⏭️  Skipped record ID {id}")
                else:
                    print(f"✅ File exists: {filestore_path}")
        else:
            print(f"✅ No attachment records found for hash {missing_hash}")
            
        # General cleanup - find all orphaned attachments
        print("\n🧹 CHECKING FOR OTHER ORPHANED ATTACHMENTS")
        print("-" * 50)
        
        cursor.execute("""
            SELECT id, name, store_fname, res_model, res_id
            FROM ir_attachment 
            WHERE store_fname IS NOT NULL 
            AND store_fname != ''
            LIMIT 100
        """)
        
        all_attachments = cursor.fetchall()
        orphaned_count = 0
        
        for record in all_attachments:
            id, name, store_fname, res_model, res_id = record
            
            if store_fname:
                filestore_path = f"/var/odoo/.local/share/Odoo/filestore/staging-erposus.com/{store_fname[:2]}/{store_fname}"
                
                if not os.path.exists(filestore_path):
                    orphaned_count += 1
                    print(f"❌ Orphaned: ID {id}, File: {store_fname}")
        
        if orphaned_count > 0:
            print(f"\n⚠️  Found {orphaned_count} orphaned attachment records")
            print("To clean all orphaned records, run:")
            print("DELETE FROM ir_attachment WHERE store_fname IS NOT NULL AND store_fname != '';")
            print("-- Then check each file exists before running this!")
        else:
            print("✅ No orphaned attachments found in sample")
            
        cursor.close()
        conn.close()
        
        print("\n🎯 FILESTORE CLEANUP COMPLETE")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
        
    return True

if __name__ == "__main__":
    fix_missing_filestore_files()
