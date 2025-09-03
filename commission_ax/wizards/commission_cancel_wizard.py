import logging
from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)

class CommissionCancelWizard(models.TransientModel):
    """Wizard to confirm commission cancellation."""
    
    _name = 'commission.cancel.wizard'
    _description = 'Commission Cancel Wizard'
    
    sale_order_ids = fields.Many2many(
        'sale.order',
        string='Sale Orders',
        required=True,
        help="Sale orders to be cancelled"
    )
    
    message = fields.Text(
        string='Cancellation Impact',
        readonly=True,
        compute='_compute_message'
    )
    
    @api.depends('sale_order_ids')
    def _compute_message(self):
        """Compute warning message about cancellation impact."""
        for wizard in self:
            if not wizard.sale_order_ids:
                wizard.message = "No sale orders selected."
                continue
                
            po_count = sum(len(order.purchase_order_ids) for order in wizard.sale_order_ids)
            
            message_parts = [
                f"You are about to cancel {len(wizard.sale_order_ids)} sale order(s).",
            ]
            
            if po_count > 0:
                message_parts.append(
                    f"This will also cancel {po_count} related commission purchase order(s)."
                )
            
            message_parts.append("This action cannot be undone.")
            
            wizard.message = "\n".join(message_parts)
    
    def action_confirm_cancel(self):
        """Confirm and execute the cancellation."""
        self.ensure_one()
        
        for order in self.sale_order_ids:
            order._execute_cancellation()
        
        return {'type': 'ir.actions.act_window_close'}
    
    def action_abort_cancel(self):
        """Abort the cancellation."""
        return {'type': 'ir.actions.act_window_close'}
