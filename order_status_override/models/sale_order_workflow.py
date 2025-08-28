from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    workflow_stage = fields.Selection([
        ('draft', 'Draft'),
        ('documentation', 'Documentation'),
        ('commission', 'Commission'),
        ('review', 'Review'),
        ('approved', 'Approved')
    ], string='Workflow Stage', default='draft', tracking=True)
    
    assigned_user_id = fields.Many2one('res.users', string='Assigned To', tracking=True)
    workflow_notes = fields.Text('Workflow Notes', tracking=True)
    
    def action_next_stage(self):
        """Advance to the next workflow stage"""
        stage_order = ['draft', 'documentation', 'commission', 'review', 'approved']
        
        if not self.workflow_stage:
            self.workflow_stage = 'draft'
            return
            
        current_index = stage_order.index(self.workflow_stage)
        if current_index < len(stage_order) - 1:
            self.workflow_stage = stage_order[current_index + 1]
        else:
            raise UserError(_('Order is already at the final stage.'))
    
    def action_reject_order(self):
        """Reject the order and move back to draft"""
        self.workflow_stage = 'draft'
        self.state = 'cancel'  # Also cancel the sale order
    
    def action_approve_order(self):
        """Approve the order"""
        self.workflow_stage = 'approved'
        # Optionally confirm the sale order if not already confirmed
        if self.state in ['draft', 'sent']:
            self.action_confirm()
    
    @api.model
    def create(self, vals):
        """Set default workflow stage on creation"""
        if 'workflow_stage' not in vals:
            vals['workflow_stage'] = 'draft'
        return super().create(vals)