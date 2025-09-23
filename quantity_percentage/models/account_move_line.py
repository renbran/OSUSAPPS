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
        help="Quantity displayed as percentage. Input 5 for 5% (0.05), input 0.05 for 0.05% (0.0005)"
    )
    
    @api.depends('quantity')
    def _compute_quantity_percentage(self):
        """Convert quantity to percentage display format"""
        for line in self:
            # Convert internal quantity to percentage for display
            # Internal 0.05 becomes 5% in the display
            line.quantity_percentage = (line.quantity or 0.0) * 100
    
    def _inverse_quantity_percentage(self):
        """Set quantity from percentage input - convert user input to decimal"""
        for line in self:
            if line.quantity_percentage is not False:
                # Convert percentage input to decimal for internal storage
                # User inputs 5 -> store as 0.05 (5%)
                line.quantity = line.quantity_percentage / 100
            else:
                line.quantity = 0.0
    
    @api.model
    def default_get(self, fields_list):
        """Override default get to set percentage UoM by default"""
        result = super().default_get(fields_list)
        
        # Find or create percentage UoM
        percentage_uom = self._get_or_create_percentage_uom()
        if percentage_uom and 'product_uom_id' in fields_list:
            result['product_uom_id'] = percentage_uom.id
            
        return result
    
    @api.model
    def _get_or_create_percentage_uom(self):
        """Get or create percentage Unit of Measure"""
        # Try to find existing percentage UoM
        percentage_uom = self.env['uom.uom'].search([
            ('name', 'ilike', '%'),
            ('category_id.name', '=', 'Percentage')
        ], limit=1)
        
        if not percentage_uom:
            # Create percentage UoM category if it doesn't exist
            percentage_category = self.env['uom.category'].search([
                ('name', '=', 'Percentage')
            ], limit=1)
            
            if not percentage_category:
                percentage_category = self.env['uom.category'].create({
                    'name': 'Percentage'
                })
            
            # Create percentage UoM
            percentage_uom = self.env['uom.uom'].create({
                'name': '%',
                'category_id': percentage_category.id,
                'factor': 1.0,
                'rounding': 0.000001,  # High precision for percentages
                'uom_type': 'reference',
            })
        
        return percentage_uom
    
    @api.model
    def _get_quantity_precision(self):
        """Override to ensure high precision for quantity calculations"""
        return 6  # 6 decimal places for precise percentage calculations
    
    @api.onchange('product_id')
    def _onchange_product_id_set_percentage_uom(self):
        """Automatically set percentage UoM when product changes unless specifically set"""
        result = super()._onchange_product_id() if hasattr(super(), '_onchange_product_id') else {}
        
        # Only set percentage UoM if not already set or if it's a different category
        if self.product_id and (not self.product_uom_id or self.product_uom_id.category_id.name != 'Percentage'):
            percentage_uom = self._get_or_create_percentage_uom()
            if percentage_uom:
                self.product_uom_id = percentage_uom
        
        return result