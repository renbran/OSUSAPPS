# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    # Simple workflow control fields
    is_locked = fields.Boolean(
        string='Is Locked',
        compute='_compute_is_locked',
        help="True if order is locked for editing"
    )
    
    can_unlock = fields.Boolean(
        string='Can Unlock',
        compute='_compute_can_unlock',
        help="True if current user can unlock orders"
    )
    
    has_due = fields.Boolean(
        string='Has Due Amounts',
        compute='_compute_has_due',
        help="True if order has overdue amounts"
    )
    
    # Simple compute methods
    @api.depends('state')
    def _compute_is_locked(self):
        """Simple lock computation"""
        for order in self:
            order.is_locked = order.state == 'done'

    def _compute_can_unlock(self):
        """Check if user can unlock orders"""
        can_unlock = self.env.user.has_group('sales_team.group_sale_manager')
        for order in self:
            order.can_unlock = can_unlock

    def _compute_has_due(self):
        """Simple due amount computation"""
        for order in self:
            # Simple check for overdue invoices
            overdue_invoices = order.invoice_ids.filtered(
                lambda inv: inv.state == 'posted' and inv.amount_residual > 0
            )
            order.has_due = bool(overdue_invoices)

    # Simple workflow methods
    def action_complete_order(self):
        """Mark order as completed"""
        if self.state == 'sale':
            self.state = 'done'
        return True

    def action_unlock_order(self):
        """Unlock order for editing (Admin only)"""
        if not self.can_unlock:
            raise UserError("You don't have permission to unlock orders.")
        
        if self.state == 'done':
            self.state = 'sale'
        return True
