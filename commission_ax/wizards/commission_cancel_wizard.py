from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class CommissionCancelWizard(models.TransientModel):
    """Wizard to handle commission cancellation with user confirmation"""
    _name = 'commission.cancel.wizard'
    _description = 'Commission Cancellation Wizard'

    sale_order_id = fields.Many2one(
        'sale.order',
        string='Sale Order',
        required=True,
        readonly=True,
        help="Sale order for which commissions will be cancelled"
    )
    
    message = fields.Html(
        string='Impact Message',
        readonly=True,
        compute='_compute_message',
        help="Description of the impact of cancellation"
    )

    @api.depends('sale_order_id')
    def _compute_message(self):
        """Compute the impact message based on the sale order state"""
        for wizard in self:
            if not wizard.sale_order_id:
                wizard.message = "<p>No sale order selected.</p>"
                continue
                
            order = wizard.sale_order_id
            po_count = len(order.commission_purchase_order_ids)
            
            message_parts = [
                "<p><strong>This action will:</strong></p>",
                "<ul>",
            ]
            
            if po_count > 0:
                message_parts.extend([
                    f"<li>Cancel <strong>{po_count} commission purchase order(s)</strong></li>",
                    "<li>Remove all commission calculations</li>",
                ])
            
            message_parts.extend([
                "<li>Set commission status back to <strong>Draft</strong></li>",
                "<li>Reset all commission-related fields</li>",
                "</ul>",
                "<p><strong>Note:</strong> This action cannot be undone. "
                "Any posted commission purchase orders will need to be manually handled.</p>"
            ])
            
            wizard.message = "".join(message_parts)

    def action_confirm_cancel(self):
        """Confirm and execute commission cancellation"""
        if not self.sale_order_id:
            raise UserError("No sale order specified for cancellation.")
            
        try:
            # Execute the reset to draft (which cancels draft POs)
            self.sale_order_id.action_reset_commissions()
            
            # Return action to close wizard and refresh view
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
            
        except Exception as e:
            _logger.error(f"Error during commission cancellation: {str(e)}")
            raise UserError(f"Failed to cancel commission: {str(e)}")

    def action_abort_cancel(self):
        """Abort the cancellation and close wizard"""
        return {'type': 'ir.actions.act_window_close'}


class CommissionDraftWizard(models.TransientModel):
    """Wizard to handle setting commission back to draft with user confirmation"""
    _name = 'commission.draft.wizard'
    _description = 'Commission Draft Wizard'

    sale_order_id = fields.Many2one(
        'sale.order',
        string='Sale Order',
        required=True,
        readonly=True,
        help="Sale order for which commissions will be set to draft"
    )
    
    message = fields.Html(
        string='Impact Message',
        readonly=True,
        compute='_compute_message',
        help="Description of the impact of setting to draft"
    )

    @api.depends('sale_order_id')
    def _compute_message(self):
        """Compute the impact message based on the sale order state"""
        for wizard in self:
            if not wizard.sale_order_id:
                wizard.message = "<p>No sale order selected.</p>"
                continue
                
            order = wizard.sale_order_id
            po_count = len(order.commission_purchase_order_ids)
            
            message_parts = [
                "<p><strong>This action will:</strong></p>",
                "<ul>",
                "<li>Set commission status to <strong>Draft</strong></li>",
                "<li>Allow modification of commission settings</li>",
            ]
            
            if po_count > 0:
                message_parts.append(
                    f"<li><strong>Warning:</strong> {po_count} commission purchase order(s) exist "
                    "and will remain unchanged</li>"
                )
            
            message_parts.extend([
                "</ul>",
                "<p><strong>Note:</strong> You will be able to recalculate commissions "
                "after modifying the settings.</p>"
            ])
            
            wizard.message = "".join(message_parts)

    def action_confirm_draft(self):
        """Confirm and execute setting to draft"""
        if not self.sale_order_id:
            raise UserError("No sale order specified.")
            
        try:
            # Set status to draft
            self.sale_order_id.commission_status = 'draft'
            
            # Return action to close wizard and refresh view
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
            
        except Exception as e:
            _logger.error(f"Error during setting commission to draft: {str(e)}")
            raise UserError(f"Failed to set commission to draft: {str(e)}")

    def action_abort_draft(self):
        """Abort the action and close wizard"""
        return {'type': 'ir.actions.act_window_close'}
