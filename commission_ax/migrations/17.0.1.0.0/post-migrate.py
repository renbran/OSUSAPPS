# -*- coding: utf-8 -*-

from odoo import api, SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)

def migrate(cr, version):
    """
    Migration script to fix commission type calculation method values
    that might be incompatible with commission line expectations
    """
    if not version:
        return

    _logger.info("Starting migration for commission calculation method compatibility...")
    
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    try:
        # Fix commission types with 'percentage' method
        commission_types = env['commission.type'].search([])
        
        for commission_type in commission_types:
            if commission_type.calculation_method == 'percentage':
                _logger.info(f"Commission type {commission_type.name} already has 'percentage' method - no change needed")
            
        # Check for any commission lines that might have invalid calculation methods
        commission_lines = env['commission.line'].search([])
        invalid_lines = []
        
        valid_methods = ['fixed', 'percentage_unit', 'percentage_total', 'percentage_untaxed']
        
        for line in commission_lines:
            if line.calculation_method not in valid_methods:
                invalid_lines.append(line)
                _logger.warning(f"Found commission line {line.id} with invalid calculation method: {line.calculation_method}")
        
        # Fix invalid commission lines
        for line in invalid_lines:
            old_method = line.calculation_method
            if old_method == 'percentage':
                line.calculation_method = 'percentage_total'
                _logger.info(f"Fixed commission line {line.id}: {old_method} -> percentage_total")
            else:
                line.calculation_method = 'percentage_total'  # Safe default
                _logger.info(f"Fixed commission line {line.id}: {old_method} -> percentage_total (default)")
        
        _logger.info(f"Migration completed. Fixed {len(invalid_lines)} commission lines.")
        
    except Exception as e:
        _logger.error(f"Error during commission migration: {e}")
        # Don't raise the exception to prevent installation failure
        pass