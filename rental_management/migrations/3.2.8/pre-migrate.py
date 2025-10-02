# -*- coding: utf-8 -*-
"""
Pre-migration script for rental_management 3.2.8

Adds 'sequence' field to property.payment.plan and property.payment.plan.line
models before Odoo loads the new model definitions.

This prevents view validation errors during module upgrade.
"""

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """
    Add sequence columns to payment plan tables before module update.
    
    This runs BEFORE Odoo loads the Python models, ensuring the database
    schema is ready when views are validated.
    """
    _logger.info("Running pre-migration for rental_management 3.2.8")
    
    # Check if property_payment_plan table exists
    cr.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'property_payment_plan'
        )
    """)
    table_exists = cr.fetchone()[0]
    
    if not table_exists:
        _logger.info("Table property_payment_plan does not exist yet - skipping sequence field migration")
        _logger.info("This is normal for fresh installations - the table will be created with the sequence field")
    else:
        # Add sequence to property.payment.plan
        _logger.info("Checking for sequence field in property_payment_plan table")
        cr.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='property_payment_plan' 
            AND column_name='sequence'
        """)
        
        if not cr.fetchone():
            _logger.info("Creating sequence column in property_payment_plan")
            cr.execute("""
                ALTER TABLE property_payment_plan 
                ADD COLUMN sequence INTEGER DEFAULT 10
            """)
            
            # Set sequence values for existing records
            cr.execute("""
                UPDATE property_payment_plan 
                SET sequence = id * 10
                WHERE sequence IS NULL
            """)
            _logger.info("Sequence field added successfully to property_payment_plan")
        else:
            _logger.info("Sequence field already exists in property_payment_plan")
    
    # Check if property_payment_plan_line table exists
    cr.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'property_payment_plan_line'
        )
    """)
    table_line_exists = cr.fetchone()[0]
    
    if not table_line_exists:
        _logger.info("Table property_payment_plan_line does not exist yet - skipping sequence field migration")
        _logger.info("This is normal for fresh installations - the table will be created with the sequence field")
    else:
        # Add sequence to property.payment.plan.line
        _logger.info("Checking for sequence field in property_payment_plan_line table")
        cr.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='property_payment_plan_line' 
            AND column_name='sequence'
        """)
        
        if not cr.fetchone():
            _logger.info("Creating sequence column in property_payment_plan_line")
            cr.execute("""
                ALTER TABLE property_payment_plan_line 
                ADD COLUMN sequence INTEGER DEFAULT 10
            """)
            
            # Set sequence values for existing records
            cr.execute("""
                UPDATE property_payment_plan_line 
                SET sequence = id * 10
                WHERE sequence IS NULL
            """)
            _logger.info("Sequence field added successfully to property_payment_plan_line")
        else:
            _logger.info("Sequence field already exists in property_payment_plan_line")
    
    _logger.info("Pre-migration completed successfully for rental_management 3.2.8")
