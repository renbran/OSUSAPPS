from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CommissionType(models.Model):
    """Commission Type Configuration"""
    _name = 'commission.type'
    _description = 'Commission Type'
    _order = 'sequence, name'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    description = fields.Text(string='Description')
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(string='Active', default=True)
    
    # Categories
    category = fields.Selection([
        ('internal', 'Internal'),
        ('external', 'External'),
        ('management', 'Management'),
        ('referral', 'Referral'),
    ], string='Category', required=True)
    
    # Default settings
    default_rate = fields.Float(string='Default Rate (%)', digits=(16, 4))
    
    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'Commission type code must be unique!'),
    ]