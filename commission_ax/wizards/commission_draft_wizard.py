import logging
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class CommissionDraftWizard(models.TransientModel):
    """Wizard to confirm setting commission to draft."""
    
    _name = 'commission.draft.wizard'
    _description = 'Commission Draft Wizard'
    _transient_max_hours = 1.0
    
    sale_order_id = fields.Many2one(
        'sale.order',
        string='Sale Order',
        required=True,
        help="Sale order to reset to draft"
    )
    
    message = fields.Text(
        string='Draft Impact',
        readonly=True,
        compute='_compute_message'
    )
    
    @api.depends('sale_order_id')
    def _compute_message(self):
        """Compute warning message about reset to draft impact."""
        for wizard in self:
            if not wizard.sale_order_id:
                wizard.message = _("No sale order selected.")
                continue
            
            order = wizard.sale_order_id
            po_count = len(order.purchase_order_ids)
            
            message_parts = [
                _("Setting sale order %s to draft will:") % order.name,
            ]
            
            if po_count > 0:
                message_parts.append(
                    _("• Cancel %d related commission purchase order(s)") % po_count
                )
            
            message_parts.extend([
                _("• Reset commission status to draft"),
                _("• Clear commission processed flag"),
                _("• Remove commission blocked reason"),
            ])
            
            wizard.message = "\n".join(message_parts)
    
    def action_confirm_draft(self):
        """Confirm and execute setting to draft."""
        self.ensure_one()
        order = self.sale_order_id
        
        _logger.info("Setting sale order %s to draft", order.name)
        
        # Cancel related purchase orders
        for po in order.purchase_order_ids:
            if po.state not in ['draft', 'cancel']:
                try:
                    po.button_cancel()
                    po.message_post(
                        body=_("Cancelled due to sale order %s set to draft") % order.name
                    )
                except Exception as e:
                    _logger.warning("Could not cancel PO %s: %s", po.name, str(e))
        
        # Reset commission fields
        order.write({
            'commission_status': 'draft',
            'commission_processed': False,
            'commission_blocked_reason': False,
        })
        
        # Set to draft if method exists
        if hasattr(order, 'action_draft'):
            order.action_draft()
        
        order.message_post(body=_("Commission reset to draft via wizard"))
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Reset to Draft'),
                'message': _('Sale order reset to draft. Related documents cancelled.'),
                'type': 'success',
                'sticky': False,
            }
        }
    
    def action_abort_draft(self):
        """Abort setting to draft."""
        return {'type': 'ir.actions.act_window_close'}
