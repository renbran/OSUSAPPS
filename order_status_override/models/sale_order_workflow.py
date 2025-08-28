from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    custom_status_id = fields.Many2one(
        'order.status', 
        string='Custom Status', 
        tracking=True, 
        copy=False,
        group_expand='_read_group_status_ids'
    )
    custom_status_history_ids = fields.One2many(
        'order.status.history', 
        'order_id', 
        string='Status History', 
        copy=False
    )
    
    documentation_user_id = fields.Many2one('res.users', string='Documentation Responsible')
    commission_user_id = fields.Many2one('res.users', string='Commission Responsible')
    final_review_user_id = fields.Many2one('res.users', string='Final Review Responsible')
    final_review_date = fields.Datetime(string='Approval Date', readonly=True)
    commission_calculated_date = fields.Datetime(string='Commission Calculation Date', readonly=True)
    commission_percentage = fields.Float(string='Commission Percentage', compute='_compute_commission_percentage')
    
    @api.depends('total_commission_amount', 'amount_total')
    def _compute_commission_percentage(self):
        for order in self:
            if order.amount_total > 0:
                order.commission_percentage = (order.total_commission_amount / order.amount_total) * 100
            else:
                order.commission_percentage = 0.0

    @api.model
    def _read_group_status_ids(self, statuses, domain, order):
        return self.env['order.status'].search([], order=order)

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        initial_status = self.env['order.status'].search([('is_initial', '=', True)], limit=1)
        if initial_status:
            for record in records:
                record._change_status(initial_status.id, _('Initial status automatically set'))
        return records
    
    def action_change_status(self):
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
        final_status = self.env['order.status'].search([('is_final', '=', True)], limit=1)
        if not final_status:
            raise UserError(_("No final status defined in the system."))
        
        self.write({'final_review_date': fields.Datetime.now()})
        self._change_status(final_status.id, _("Order approved"))
        
        # Send approval notification
        template = self.env.ref('sale_order_workflow.email_template_order_approved', False)
        if template:
            template.with_context(lang=self.partner_id.lang).send_mail(self.id, force_send=True)
        
        return True
    
    def action_reject_order(self):
        self.ensure_one()
        initial_status = self.env['order.status'].search([('is_initial', '=', True)], limit=1)
        if not initial_status:
            raise UserError(_("No initial status defined in the system."))
        
        self._change_status(initial_status.id, _("Order rejected and returned to draft"))
        
        # Send rejection notification
        template = self.env.ref('sale_order_workflow.email_template_order_rejected', False)
        if template:
            template.with_context(lang=self.partner_id.lang).send_mail(self.id, force_send=True)
        
        return True
    
    def _change_status(self, new_status_id, notes=False):
        """Helper method to change status and create history entry"""
        self.ensure_one()
        new_status = self.env['order.status'].browse(new_status_id)
        old_status = self.custom_status_id
        
        # Validate transition
        if old_status and new_status.id not in old_status.next_status_ids.ids:
            raise UserError(_("Invalid status transition: %s → %s") % (old_status.name, new_status.name))
        
        # Update status
        self.custom_status_id = new_status
        
        # Set commission calculation date if moving to commission status
        if new_status.code == 'commission_calculation':
            self.commission_calculated_date = fields.Datetime.now()
        
        # Create history entry
        self.env['order.status.history'].create({
            'order_id': self.id,
            'status_id': new_status.id,
            'previous_status_id': old_status.id if old_status else False,
            'notes': notes or _('Status changed')
        })
        
        # Create activity for responsible user
        self._create_activity_for_status(new_status)
        
        # Send notifications
        self._send_status_notifications(new_status, old_status)
        
        return True
    
    def _create_activity_for_status(self, status):
        """Create an activity for the responsible user based on status"""
        user_id = False
        summary = _("Action Required: ") + self.name
        note = _("Order %s has moved to status '%s'. Please process accordingly.") % (self.name, status.name)
        
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
    
    def _send_status_notifications(self, new_status, old_status):
        """Send email notifications based on status change"""
        # General status change notification
        if new_status.notify_customer:
            template_general = self.env.ref('sale_order_workflow.email_template_order_status_change', False)
            if template_general:
                template_general.with_context(lang=self.partner_id.lang).send_mail(self.id, force_send=True)
        
        # Specific status notifications
        if new_status.code == 'commission_calculation':
            template_commission = self.env.ref('sale_order_workflow.email_template_commission_calculated', False)
            if template_commission:
                template_commission.send_mail(self.id, force_send=True)
        
        if new_status.is_final:
            template_approval = self.env.ref('sale_order_workflow.email_template_order_approved', False)
            if template_approval:
                template_approval.send_mail(self.id, force_send=True)
    
    def write(self, vals):
        """Handle status changes during write operations"""
        if 'custom_status_id' in vals:
            for order in self:
                order._change_status(vals['custom_status_id'], _("Status changed via update"))
        return super().write(vals)