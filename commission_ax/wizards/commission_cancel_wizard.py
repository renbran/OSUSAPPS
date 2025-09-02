import logging
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class CommissionCancelWizard(models.TransientModel):
    """Wizard to confirm commission cancellation."""
    
    _name = 'commission.cancel.wizard'
    _description = 'Commission Cancel Wizard'
    _transient_max_hours = 1.0
    
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
                wizard.message = _("No sale orders selected.")
                continue
                
            po_count = sum(len(order.purchase_order_ids) for order in wizard.sale_order_ids)
            
            message_parts = [
                _("You are about to cancel %d sale order(s).") % len(wizard.sale_order_ids),
            ]
            
            if po_count > 0:
                message_parts.append(
                    _("This will also cancel %d related commission purchase order(s).") % po_count
                )
            
            message_parts.append(_("This action cannot be undone."))
            
            wizard.message = "\n".join(message_parts)
    
    def action_confirm_cancel(self):
        """Confirm and execute the cancellation."""
        self.ensure_one()
        _logger.info("Cancelling %d sale orders", len(self.sale_order_ids))
        
        for order in self.sale_order_ids:
            # Cancel related purchase orders first
            for po in order.purchase_order_ids:
                if po.state != 'cancel':
                    try:
                        po.button_cancel()
                        po.message_post(
                            body=_("Cancelled due to sale order %s cancellation") % order.name
                        )
                    except Exception as e:
                        _logger.warning("Could not cancel PO %s: %s", po.name, str(e))
            
            # Cancel the sale order
            order.action_cancel()
            order.commission_status = 'cancelled'
            order.message_post(body=_("Commission cancelled via wizard"))
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Cancelled'),
                'message': _('%d sale order(s) and related documents cancelled.') % len(self.sale_order_ids),
                'type': 'success',
                'sticky': False,
            }
        }
    
    def action_abort_cancel(self):
        """Abort the cancellation."""
        return {'type': 'ir.actions.act_window_close'}