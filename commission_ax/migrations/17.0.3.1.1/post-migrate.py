"""
Migration script to fix commission_processed field issues
This script should be run as part of the module update to clean up any orphaned field references
"""

from odoo import SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)

def migrate(cr, version):
    """Migration function to clean up commission_processed field issues"""
    _logger.info("Starting commission_processed field cleanup migration")
    
    try:
        # Check if commission.line model exists in the database
        cr.execute("""
            SELECT 1 FROM information_schema.tables 
            WHERE table_name = 'commission_line' 
            AND table_schema = current_schema()
        """)
        
        if not cr.fetchone():
            _logger.info("commission_line table does not exist yet, skipping migration")
            return
        
        # Check if commission_processed column exists in commission_line table
        cr.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'commission_line' 
            AND column_name = 'commission_processed'
            AND table_schema = current_schema()
        """)
        
        if cr.fetchone():
            _logger.warning("Found commission_processed column in commission_line table, removing it")
            try:
                cr.execute("ALTER TABLE commission_line DROP COLUMN commission_processed CASCADE")
                _logger.info("Successfully removed commission_processed column from commission_line table")
            except Exception as e:
                _logger.error(f"Failed to remove commission_processed column: {e}")
        
        # Clean up any orphaned ir.model.fields records
        cr.execute("""
            DELETE FROM ir_model_fields 
            WHERE model = 'commission.line' 
            AND name = 'commission_processed'
        """)
        
        deleted_fields = cr.rowcount
        if deleted_fields > 0:
            _logger.info(f"Cleaned up {deleted_fields} orphaned field records for commission_processed")
        
        # Clean up any orphaned ir.model.constraint records
        cr.execute("""
            DELETE FROM ir_model_constraint 
            WHERE model = (SELECT id FROM ir_model WHERE model = 'commission.line')
            AND name LIKE '%commission_processed%'
        """)
        
        deleted_constraints = cr.rowcount
        if deleted_constraints > 0:
            _logger.info(f"Cleaned up {deleted_constraints} orphaned constraint records")
        
        # Commit the changes
        cr.commit()
        
        _logger.info("Commission_processed field cleanup migration completed successfully")
        
    except Exception as e:
        _logger.error(f"Migration failed: {e}")
        cr.rollback()
        raise