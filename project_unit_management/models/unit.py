from odoo import models, fields

class Unit(models.Model):
    _name = 'project.unit'
    _description = 'Unit'

    name = fields.Char(string='Unit Name', required=True)
    project_id = fields.Many2one('project.project', string='Project', required=True)
    price = fields.Float(string='Price', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency')
    status = fields.Selection([
        ('available', 'Available'),
        ('reserved', 'Reserved'),
        ('sold', 'Sold')
    ], string='Status', default='available')
