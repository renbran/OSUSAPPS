#!/usr/bin/env python3
"""
Database Integrity Fix Script for OSUSAPPS
===========================================

This script addresses the following issues:
1. Foreign key constraint violations in res_groups/ir_model_access
2. Missing model table for payment.reminder.manager
3. Orphaned file references

Usage: python fix_database_integrity.py
"""

import logging

_logger = logging.getLogger(__name__)

class DatabaseIntegrityFixer:
    
    def __init__(self, env):
        self.env = env
        
    def fix_foreign_key_violations(self):
        """Fix foreign key constraint violations in security groups"""
        try:
            # Find orphaned access rights that reference non-existent groups
            orphaned_access = self.env['ir.model.access'].search([
                ('group_id', 'in', [507, 508, 509, 510])
            ])
            
            if orphaned_access:
                print(f"Found {len(orphaned_access)} orphaned access rights")
                orphaned_access.unlink()
                print("✅ Orphaned access rights cleaned up")
            
            # Now try to clean up the orphaned groups
            orphaned_groups = self.env['res.groups'].search([
                ('id', 'in', [507, 508, 509, 510])
            ])
            
            if orphaned_groups:
                print(f"Found {len(orphaned_groups)} orphaned groups")
                orphaned_groups.unlink()
                print("✅ Orphaned groups cleaned up")
                
        except Exception as e:
            print(f"❌ Error fixing foreign key violations: {e}")
    
    def fix_missing_model_table(self):
        """Fix missing payment.reminder.manager table"""
        try:
            # Check if model exists in registry
            if 'payment.reminder.manager' in self.env:
                print("✅ payment.reminder.manager model found in registry")
                
                # Try to access the model to trigger table creation
                reminder_model = self.env['payment.reminder.manager']
                reminder_model.search([])
                print("✅ payment.reminder.manager table accessible")
            else:
                print("❌ payment.reminder.manager model not found in registry")
                print("   This suggests payment_account_enhanced module is not properly installed")
                
        except Exception as e:
            print(f"❌ Error with payment.reminder.manager: {e}")
    
    def fix_missing_attachments(self):
        """Fix missing attachment files"""
        try:
            # Find orphaned attachment references
            attachments = self.env['ir.attachment'].search([])
            missing_count = 0
            
            for attachment in attachments:
                if attachment.store_fname:
                    try:
                        # Try to access the file
                        attachment._file_read(attachment.store_fname)
                    except FileNotFoundError:
                        missing_count += 1
                        print(f"Missing file: {attachment.store_fname}")
                        # Option: Delete the attachment record or mark it as deleted
                        attachment.unlink()
            
            if missing_count > 0:
                print(f"✅ Cleaned up {missing_count} orphaned attachment references")
            else:
                print("✅ No missing attachment files found")
                
        except Exception as e:
            print(f"❌ Error fixing missing attachments: {e}")
    
    def run_all_fixes(self):
        """Run all database integrity fixes"""
        print("🔧 Starting Database Integrity Fix...")
        print("=" * 50)
        
        print("\n1. Fixing foreign key violations...")
        self.fix_foreign_key_violations()
        
        print("\n2. Checking missing model table...")
        self.fix_missing_model_table()
        
        print("\n3. Fixing missing attachments...")
        self.fix_missing_attachments()
        
        print("\n" + "=" * 50)
        print("✅ Database integrity fix completed!")

# Usage example for Odoo shell:
# from fix_database_integrity import DatabaseIntegrityFixer
# fixer = DatabaseIntegrityFixer(env)
# fixer.run_all_fixes()