# -*- coding: utf-8 -*-
"""
Pre-migration script for payment approval state sync
FIXED: Handle missing state column during migration
"""

import logging

_logger = logging.getLogger(__name__)

def migrate(cr, version):
    """Pre-migration: Log current state - SAFE VERSION"""
    _logger.info("Starting payment approval state migration from version %s", version)
    
    # Check if account_payment table and required columns exist before querying
    try:
        # First check if table exists
        cr.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'account_payment'
            )
        """)
        table_exists = cr.fetchone()[0]
        
        if not table_exists:
            _logger.info("account_payment table does not exist yet, skipping migration")
            return
            
        # Check if state column exists
        cr.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_name = 'account_payment' 
                AND column_name = 'state'
            )
        """)
        state_exists = cr.fetchone()[0]
        
        # Check if approval_state column exists
        cr.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_name = 'account_payment' 
                AND column_name = 'approval_state'
            )
        """)
        approval_state_exists = cr.fetchone()[0]
        
        if state_exists and approval_state_exists:
            # Both columns exist, run the migration query
            cr.execute("""
                SELECT 
                    state,
                    approval_state,
                    COUNT(*) as count
                FROM account_payment 
                WHERE (state = 'posted' AND approval_state != 'posted')
                   OR (state = 'cancel' AND approval_state != 'cancelled')
                   OR (state = 'draft' AND approval_state NOT IN ('draft', 'under_review'))
                GROUP BY state, approval_state
            """)
            results = cr.fetchall()
            _logger.info("Payments requiring migration: %s", results)
            
        elif approval_state_exists:
            # Only approval_state exists, check for inconsistencies within approval_state
            cr.execute("""
                SELECT 
                    approval_state,
                    COUNT(*) as count
                FROM account_payment 
                WHERE approval_state IS NOT NULL
                GROUP BY approval_state
            """)
            results = cr.fetchall()
            _logger.info("Current approval state distribution: %s", results)
            
        else:
            _logger.info("Required columns do not exist yet, migration will be handled in post-migrate")
            
    except Exception as e:
        _logger.warning("Error during pre-migration check: %s", e)
        _logger.info("Continuing with installation, migration will be handled in post-migrate")
