from odoo import models, fields, api, _

class OrderStatusHistory(models.Model):
    _name = 'order.status.history'
    _description = 'Order Workflow Status History'
    _order = 'create_date desc'
    _rec_name = 'display_name'
    
    order_id = fields.Many2one('sale.order', string='Sale Order', required=True, ondelete='cascade')
    action_type = fields.Selection([
        ('advance', 'Stage Advanced'),
        ('reject', 'Order Rejected'),
        ('approve', 'Order Approved'),
        ('assign', 'User Assigned'),
        ('create', 'Order Created'),
    ], string='Action Type', required=True)
    
    stage_name = fields.Char(string='Stage', required=True)
    previous_stage = fields.Char(string='Previous Stage')
    assigned_user_id = fields.Many2one('res.users', string='Assigned User')
    previous_user_id = fields.Many2one('res.users', string='Previous User')
    
    user_id = fields.Many2one('res.users', string='Action By', 
                            default=lambda self: self.env.user.id, readonly=True)
    notes = fields.Text(string='Notes')
    create_date = fields.Datetime(string='Date', readonly=True)
    
    # Computed fields
    display_name = fields.Char(string='Display Name', compute='_compute_display_name', store=True)
    duration_days = fields.Float(string='Duration (Days)', compute='_compute_duration')
    
    @api.depends('action_type', 'stage_name', 'create_date')
    def _compute_display_name(self):
        for record in self:
            action_labels = dict(record._fields['action_type'].selection)
            action_name = action_labels.get(record.action_type, record.action_type)
            record.display_name = f"{action_name} - {record.stage_name} ({record.create_date.strftime('%Y-%m-%d %H:%M') if record.create_date else ''})"
    
    def _compute_duration(self):
        for record in self:
            if record.create_date:
                # Find the previous record for the same order
                previous_record = self.search([
                    ('order_id', '=', record.order_id.id),
                    ('create_date', '<', record.create_date)
                ], limit=1, order='create_date desc')
                
                if previous_record:
                    duration = record.create_date - previous_record.create_date
                    record.duration_days = duration.total_seconds() / (24 * 3600)  # Convert to days
                else:
                    record.duration_days = 0.0
            else:
                record.duration_days = 0.0

class OrderStatusHistoryWizard(models.TransientModel):
    _name = 'order.status.history.wizard'
    _description = 'Order Status History Wizard'
    
    order_id = fields.Many2one('sale.order', string='Sale Order', required=True)
    history_ids = fields.One2many('order.status.history', 'order_id', string='Status History', readonly=True)
    
    def action_refresh(self):
        """Refresh the history view"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'order.status.history.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'context': self.env.context,
        }