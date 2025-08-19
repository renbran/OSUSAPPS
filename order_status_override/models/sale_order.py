from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    custom_status_id = fields.Many2one('order.status', string='Custom Status', 
                                      tracking=True, copy=False)
    custom_status_history_ids = fields.One2many('order.status.history', 'order_id', 
                                            string='Status History', copy=False)
    
    documentation_user_id = fields.Many2one('res.users', string='Documentation Responsible')
    commission_user_id = fields.Many2one('res.users', string='Commission Responsible')
    final_review_user_id = fields.Many2one('res.users', string='Final Review Responsible')
    
    @api.model_create_multi
    def create(self, vals_list):
        records = super(SaleOrder, self).create(vals_list)
        initial_status = self.env['order.status'].search([('is_initial', '=', True)], limit=1)
        if initial_status:
            for record in records:
                record.custom_status_id = initial_status.id
                self.env['order.status.history'].create({
                    'order_id': record.id,
                    'status_id': initial_status.id,
                    'notes': _('Initial status automatically set to %s') % initial_status.name
                })
        return records
    
    def action_change_status(self):
        """
        Open the status change wizard
        :return: Action dictionary
        """
        self.ensure_one()
        return {
            'name': _('Change Order Status'),
            'type': 'ir.actions.act_window',
            'res_model': 'order.status.change.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_order_id': self.id,
                'default_current_status_id': self.custom_status_id.id,
            }
        }


    def action_approve_order(self):
        self.ensure_one()
        # Find the final status (approved)
        final_status = self.env['order.status'].search([('is_final', '=', True)], limit=1)
        if not final_status:
            raise UserError(_("No final status defined in the system."))
        
        # Change to final/approved status
        self._change_status(final_status.id, _("Order approved"))
        
        # Send approval notification
        template = self.env.ref('custom_sales_order_status.email_template_order_approved', False)
        if template:
            template.send_mail(self.id, force_send=True)
        
        return True
    
    def action_reject_order(self):
        self.ensure_one()
        # Find the initial status (draft)
        initial_status = self.env['order.status'].search([('is_initial', '=', True)], limit=1)
        if not initial_status:
            raise UserError(_("No initial status defined in the system."))
        
        # Change to initial/draft status
        self._change_status(initial_status.id, _("Order rejected and returned to draft"))
        
        # Send rejection notification
        template = self.env.ref('custom_sales_order_status.email_template_order_rejected', False)
        if template:
            template.send_mail(self.id, force_send=True)
        
        return True
    
    def _change_status(self, new_status_id, notes=False):
        """Helper method to change status and create history entry"""
        old_status_id = self.custom_status_id.id
        self.custom_status_id = new_status_id
        
        # Create history entry
        self.env['order.status.history'].create({
            'order_id': self.id,
            'status_id': new_status_id,
            'previous_status_id': old_status_id,
            'notes': notes or _('Status changed')
        })
        
        # Create activity based on the responsible type
        new_status = self.env['order.status'].browse(new_status_id)
        self._create_activity_for_status(new_status)
        
        return True
    
    def _create_activity_for_status(self, status):
        """Create an activity for the responsible user based on status"""
        user_id = False
        summary = _("Process Sale Order ") + self.name
        note = _("Please process the sale order as per the '%s' stage.") % status.name
        
        if status.responsible_type == 'documentation':
            user_id = self.documentation_user_id.id
        elif status.responsible_type == 'commission':
            user_id = self.commission_user_id.id
        elif status.responsible_type == 'final_review':
            user_id = self.final_review_user_id.id
        
        if user_id:
            self.activity_schedule(
                'mail.mail_activity_data_todo',
                summary=summary,
                note=note,
                user_id=user_id
            )