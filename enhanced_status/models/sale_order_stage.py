from odoo import models, fields

class SaleOrderStage(models.Model):
    _name = 'sale.order.stage'
    _description = 'Sale Order Stages'
    _order = 'sequence, name'

    name = fields.Char('Stage Name', required=True)
    sequence = fields.Integer('Sequence', default=10)
    description = fields.Text('Description')
    fold = fields.Boolean('Folded in Kanban', default=False)
    stage_code = fields.Selection([
        ('draft', 'Draft'),
        ('documentation', 'Documentation'),
        ('calculation', 'Calculation'),
        ('approved', 'Approved'),
        ('completed', 'Completed'),
    ], string='Stage Code', required=True)