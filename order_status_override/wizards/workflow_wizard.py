from odoo import models, fields, api, _
from odoo.exceptions import UserError

class WorkflowStageWizard(models.TransientModel):
    _name = 'sale.workflow.wizard'
    _description = 'Workflow Stage Wizard'

    order_id = fields.Many2one('sale.order', required=True)
    action_type = fields.Selection([
        ('advance', 'Advance Stage'),
        ('reject', 'Reject Order'),
        ('approve', 'Approve Order'),
        ('assign', 'Assign User')
    ], required=True, default='advance')
    
    assigned_user_id = fields.Many2one('res.users', string='Assign To')
    notes = fields.Text('Notes')
    
    # Display fields for context
    current_stage = fields.Selection(related='order_id.workflow_stage', readonly=True)
    order_name = fields.Char(string='Order', related='order_id.name', readonly=True)
    current_assigned_user = fields.Many2one('res.users', related='order_id.assigned_user_id', readonly=True)
    
    @api.onchange('action_type')
    def _onchange_action_type(self):
        """Update visibility and requirements based on action type"""
        if self.action_type == 'assign' and not self.assigned_user_id:
            self.assigned_user_id = self.env.user.id
        elif self.action_type in ['advance'] and not self.assigned_user_id:
            self.assigned_user_id = self.order_id.assigned_user_id.id if self.order_id.assigned_user_id else self.env.user.id
    
    def action_execute(self):
        """Execute the selected workflow action"""
        order = self.order_id
        
        # Create status history record
        self._create_status_history_record(order)
        
        if self.action_type == 'advance':
            if self.assigned_user_id:
                order.assigned_user_id = self.assigned_user_id
            if self.notes:
                self._append_workflow_notes(order, f"Stage Advanced: {self.notes}")
            order.action_next_stage()
            
        elif self.action_type == 'reject':
            if self.notes:
                self._append_workflow_notes(order, f"Order Rejected: {self.notes}")
            order.action_reject_order()
            
        elif self.action_type == 'approve':
            if self.notes:
                self._append_workflow_notes(order, f"Order Approved: {self.notes}")
            order.action_approve_order()
            
        elif self.action_type == 'assign':
            if not self.assigned_user_id:
                raise UserError(_('Please select a user to assign.'))
            old_user = order.assigned_user_id.name if order.assigned_user_id else 'Unassigned'
            order.assigned_user_id = self.assigned_user_id
            note_text = f"Assignment changed from {old_user} to {self.assigned_user_id.name}"
            if self.notes:
                note_text += f": {self.notes}"
            self._append_workflow_notes(order, note_text)
        
        return {'type': 'ir.actions.act_window_close'}
    
    def _append_workflow_notes(self, order, note):
        """Append timestamped note to workflow_notes"""
        timestamp = fields.Datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_note = f"[{timestamp}] {self.env.user.name}: {note}"
        
        if order.workflow_notes:
            order.workflow_notes = f"{order.workflow_notes}\n{new_note}"
        else:
            order.workflow_notes = new_note
    
    def _create_status_history_record(self, order):
        """Create a record in order status history"""
        # Get current stage name
        stage_dict = dict(order._fields['workflow_stage'].selection)
        current_stage_name = stage_dict.get(order.workflow_stage, order.workflow_stage)
        
        # This would work if you implement the OrderStatusHistory model
        # self.env['order.status.history'].create({
        #     'order_id': order.id,
        #     'action_type': self.action_type,
        #     'stage_name': current_stage_name,
        #     'assigned_user_id': self.assigned_user_id.id if self.assigned_user_id else False,
        #     'notes': self.notes or '',
        # })