import logging
from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)

class CommissionDraftWizard(models.TransientModel):
    """Wizard to confirm setting commission to draft."""
    
    _name = 'commission.draft.wizard'
    _description = 'Commission Draft Wizard'
    
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
                wizard.message = "No sale order selected."
                continue
            
            order = wizard.sale_order_id
            po_count = len(order.purchase_order_ids)
            
            message_parts = [
                f"Setting sale order {order.name} to draft will:",
            ]
            
            if po_count > 0:
                message_parts.append(
                    f"• Cancel {po_count} related commission purchase order(s)"
                )
            
            message_parts.extend([
                "• Reset commission status to draft",
                "• Clear commission processed flag",
                "• Remove commission blocked reason",
            ])
            
            wizard.message = "\n".join(message_parts)
    
    def action_confirm_draft(self):
        """Confirm and execute setting to draft."""
        self.ensure_one()
        order = self.sale_order_id
        
        # Reset commission fields
        order.write({
            'commission_status': 'draft',
            'commission_processed': False,
            'commission_blocked_reason': False,
        })
        
        return {'type': 'ir.actions.act_window_close'}
    
    def action_abort_draft(self):
        """Abort setting to draft."""
        return {'type': 'ir.actions.act_window_close'}
