# -*- coding: utf-8 -*-
"""
Commission calculation base models
This module provides standardized commission calculation functionality
"""

from odoo import api, fields, models
from odoo.exceptions import ValidationError

class CommissionCalculation(models.AbstractModel):
    """Abstract model for standardized commission calculation"""
    _name = 'commission.calculation'
    _description = 'Commission Calculation Base'
    
    @api.model
    def calculate_commission(self, base_amount, commission_type, rate=0.0, fixed_amount=0.0):
        """
        Unified commission calculation function
        
        Args:
            base_amount (float): Base amount for calculation
            commission_type (str): Type of commission calculation
            rate (float): Commission rate (percentage)
            fixed_amount (float): Fixed amount for 'fixed' type
            
        Returns:
            float: Calculated commission amount
        """
        if not base_amount:
            return 0.0
            
        if commission_type == 'fixed':
            return fixed_amount
        elif commission_type == 'percent_unit_price':
            return base_amount * (rate / 100.0)
        elif commission_type == 'percent_untaxed_total':
            return base_amount * (rate / 100.0)
        return 0.0
    
    @api.model
    def get_commission_types(self):
        """
        Get standard commission types
        
        Returns:
            list: List of tuples with commission types for selection fields
        """
        return [
            ('fixed', 'Fixed'),
            ('percent_unit_price', 'Percentage of Unit Price'),
            ('percent_untaxed_total', 'Percentage of Untaxed Total')
        ]

class CommissionBase(models.AbstractModel):
    """Abstract model with standard commission fields"""
    _name = 'commission.base'
    _description = 'Base Commission Fields'
    
    # Common commission fields for mixing into other models
    commission_partner_id = fields.Many2one(
        'res.partner',
        string='Commission Partner',
        help="Partner who receives the commission"
    )
    commission_type = fields.Selection(
        selection=lambda self: self.env['commission.calculation'].get_commission_types(),
        string='Commission Type',
        default='percent_untaxed_total',
        help="Method used to calculate the commission"
    )
    commission_rate = fields.Float(
        string='Commission Rate (%)',
        default=0.0,
        help="Commission percentage rate"
    )
    commission_amount = fields.Monetary(
        string='Commission Amount',
        store=True,
        help="Calculated commission amount"
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
        help="Currency for commission calculations"
    )
    
    def calculate_commission_amount(self, base_amount=None):
        """
        Calculate commission amount
        
        Args:
            base_amount (float, optional): Base amount for calculation.
                                          If not provided, tries to use amount_untaxed
                                          
        Returns:
            float: Calculated commission amount
        """
        self.ensure_one()
        if not base_amount:
            # Try to get base amount from common fields
            if hasattr(self, 'amount_untaxed'):
                base_amount = self.amount_untaxed
            elif hasattr(self, 'price_subtotal'):
                base_amount = self.price_subtotal
            else:
                return 0.0
                
        return self.env['commission.calculation'].calculate_commission(
            base_amount,
            self.commission_type,
            self.commission_rate,
            self.commission_amount if self.commission_type == 'fixed' else 0.0
        )