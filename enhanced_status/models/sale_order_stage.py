from odoo import models, fields, api

class SaleOrderStage(models.Model):
    _name = 'sale.order.stage'
    _description = 'Sale Order Stages'
    _order = 'sequence, name'

    name = fields.Char('Stage Name', required=True)
    sequence = fields.Integer('Sequence', default=10)
    description = fields.Text('Description')
    responsible_user_id = fields.Many2one('res.users', string='Responsible User')
    responsible_group_id = fields.Many2one('res.groups', string='Responsible Group')
    fold = fields.Boolean('Folded in Kanban')
    stage_code = fields.Selection([
        ('draft', 'Draft'),
        ('documentation', 'Documentation'),
        ('calculation', 'Calculation'),
        ('approved', 'Approved'),
        ('completed', 'Completed'),
    ], string='Stage Code', required=True)
    
    @api.model
    def _get_default_stages(self):
        """Return default stages for sale orders"""
        return [
            {'name': 'Draft', 'sequence': 1, 'stage_code': 'draft'},
            {'name': 'Documentation', 'sequence': 2, 'stage_code': 'documentation'},
            {'name': 'Calculation', 'sequence': 3, 'stage_code': 'calculation'},
            {'name': 'Approved', 'sequence': 4, 'stage_code': 'approved'},
            {'name': 'Completed', 'sequence': 5, 'stage_code': 'completed'},
        ]