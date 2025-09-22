# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    # Add a computed field for percentage display with high precision
    product_uom_qty_percentage = fields.Float(
        string='Quantity (%)',
        compute='_compute_product_uom_qty_percentage',
        inverse='_inverse_product_uom_qty_percentage',
        store=False,
        digits=(16, 6),  # Allow up to 6 decimal places for high precision
        help="Quantity displayed as percentage with exact precision"
    )
    
    @api.depends('product_uom_qty')
    def _compute_product_uom_qty_percentage(self):
        """Convert quantity to percentage display format without rounding"""
        for line in self:
            # Keep the exact value - no multiplication by 100 since 
            # percentage widget handles the display conversion
            line.product_uom_qty_percentage = line.product_uom_qty or 0.0
    
    def _inverse_product_uom_qty_percentage(self):
        """Set quantity from percentage input"""
        for line in self:
            # Store the exact value entered
            if line.product_uom_qty_percentage is not False:
                line.product_uom_qty = line.product_uom_qty_percentage
            else:
                line.product_uom_qty = 0.0
    
    @api.model
    def _get_quantity_precision(self):
        """Override to ensure high precision for quantity calculations"""
        return 6  # 6 decimal places for precise percentage calculations