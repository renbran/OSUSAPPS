from odoo import models, fields, api, _

class SaleOrderStage(models.Model):
    _name = 'sale.order.stage'
    _description = 'Sale Order Stage'
    _order = 'sequence, name'

    name = fields.Char(string='Stage Name', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    is_active = fields.Boolean(string='Active', default=True)
    responsible_id = fields.Many2one('res.users', string='Responsible')
    show_in_kanban = fields.Boolean(string='Show in Kanban', default=True)
