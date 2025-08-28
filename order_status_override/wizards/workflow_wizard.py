from odoo import models, fields, api, _

class OrderStatusHistory(models.Model):
    _name = 'order.status.history'
    _description = 'Order Status History'
    _order = 'create_date desc'

    order_id = fields.Many2one('sale.order', required=True, ondelete='cascade', index=True)
    action_type = fields.Selection([
        ('advance', 'Advance Stage'),
        ('reject', 'Reject Order'),
        ('approve', 'Approve Order'),
        ('assign', 'Assign User')
    ], required=True)
    stage_name = fields.Char(string='Stage Name', required=True)
    assigned_user_id = fields.Many2one('res.users', string='Assigned User')
    notes = fields.Text('Notes')
    user_id = fields.Many2one('res.users', string='Action By', default=lambda self: self.env.user, required=True)
    create_date = fields.Datetime(string='Timestamp', readonly=True)
