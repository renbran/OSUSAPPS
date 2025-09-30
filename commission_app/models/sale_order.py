# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SaleOrder(models.Model):
    """Additional sale order extensions (if needed beyond res_partner.py)."""
    _inherit = 'sale.order'
    
    # Additional commission-related functionality can be added here
    # The main functionality is already in res_partner.py
    pass