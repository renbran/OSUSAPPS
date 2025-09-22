# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    # Add a computed field for percentage display with high precision
    quantity_percentage = fields.Float(
        string='Quantity (%)',
        compute='_compute_quantity_percentage',
        inverse='_inverse_quantity_percentage',
        store=False,
        digits=(16, 6),  # Allow up to 6 decimal places for high precision
        help="Quantity displayed as percentage with exact precision"
    )
    
    @api.depends('quantity')
    def _compute_quantity_percentage(self):
        """Convert quantity to percentage display format without rounding"""
        for line in self:
            # Keep the exact value - no multiplication by 100 since 
            # percentage widget handles the display conversion
            line.quantity_percentage = line.quantity or 0.0
    
    def _inverse_quantity_percentage(self):
        """Set quantity from percentage input"""
        for line in self:
            # Store the exact value entered
            if line.quantity_percentage is not False:
                line.quantity = line.quantity_percentage
            else:
                line.quantity = 0.0
    
    @api.model
    def _get_quantity_precision(self):
        """Override to ensure high precision for quantity calculations"""
        return 6  # 6 decimal places for precise percentage calculations