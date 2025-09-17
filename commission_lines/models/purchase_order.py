# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    """Extend Purchase Order to handle commission line status updates"""
    _inherit = 'purchase.order'

    # Commission Lines Integration
    commission_line_ids = fields.One2many(
        'commission.line', 
        'purchase_order_id', 
        string='Commission Lines',
        help='Commission lines linked to this purchase order'
    )
    
    commission_line_count = fields.Integer(
        string='Commission Lines Count',
        compute='_compute_commission_line_count',
        help='Number of commission lines linked to this PO'
    )

    # ============================================================================
    # COMPUTE METHODS
    # ============================================================================
    
    @api.depends('commission_line_ids')
    def _compute_commission_line_count(self):
        """Compute commission line count"""
        for order in self:
            order.commission_line_count = len(order.commission_line_ids)

    # ============================================================================
    # ACTION METHODS
    # ============================================================================
    
    def action_view_commission_lines(self):
        """View commission lines for this purchase order"""
        self.ensure_one()
        action = self.env.ref('commission_lines.action_commission_line').read()[0]
        action['domain'] = [('purchase_order_id', '=', self.id)]
        action['context'] = {
            'default_purchase_order_id': self.id,
            'create': False,
        }
        return action

    # ============================================================================
    # OVERRIDE METHODS
    # ============================================================================
    
    def button_confirm(self):
        """Override to update commission line status when PO is confirmed"""
        result = super(PurchaseOrder, self).button_confirm()
        
        # Update commission lines to billed status
        for commission_line in self.commission_line_ids:
            if commission_line.state == 'approved':
                commission_line.action_bill()
        
        return result
    
    def button_cancel(self):
        """Override to update commission line status when PO is cancelled"""
        result = super(PurchaseOrder, self).button_cancel()
        
        # Reset commission lines back to approved status
        for commission_line in self.commission_line_ids:
            if commission_line.state == 'billed':
                commission_line.state = 'approved'
                commission_line.purchase_order_id = False
        
        return result
    
    def _create_stock_moves(self, picking):
        """Override to track commission payment when goods are received"""
        result = super(PurchaseOrder, self)._create_stock_moves(picking)
        
        # Check if this is a commission PO and update status accordingly
        if self.commission_line_ids:
            # When goods are received, commission can be marked as paid
            for commission_line in self.commission_line_ids:
                if commission_line.state == 'billed':
                    # Don't auto-mark as paid, keep it billed until manual confirmation
                    pass
        
        return result