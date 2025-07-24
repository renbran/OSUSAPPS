from odoo import api, fields, models

class Property(models.Model):
    _name = 'property.property'
    _description = 'Property Details'
    _order = 'name'

    name = fields.Char(string="Property Name", required=True)
    partner_id = fields.Many2one('res.partner', string="Partner")
    currency_id = fields.Many2one('res.currency', string="Currency")
    property_price = fields.Monetary(string="Property Price", required=True)
    revenue_account_id = fields.Many2one('account.account', string="Revenue Account", required=True)
    address = fields.Text(string="Address")
    sale_rent = fields.Selection([
        ('for_sale', 'For Sale'),
        ('for_rent', 'For Rent'),
    ], string="Sale or Rent", required=True)
    state = fields.Selection([
        ('available', 'Available'),
        ('reserved', 'Reserved'),
        ('sold', 'Sold'),
    ], string="State", default='available', required=True)
    currency_id = fields.Many2one('res.currency', string="Currency", required=True, default=lambda self: self.env.company.currency_id)
    description = fields.Text(string="Description")
