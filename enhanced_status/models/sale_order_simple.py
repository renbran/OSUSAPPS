# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Custom workflow state field
    custom_state = fields.Selection([
        ('draft', 'Draft'),
        ('documentation', 'Documentation'),
        ('calculation', 'Calculation'),
        ('approved', 'Approved'),
        ('completed', 'Completed'),
    ], string='Custom State',
       default='draft',
       tracking=True,
       help="Custom workflow state for enhanced order tracking"
    )

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

    is_warning = fields.Boolean(
        string='Has Warnings',
        compute='_compute_is_warning',
        help="True if there are validation warnings for this order"
    )

    # Simple compute methods
    @api.depends('state', 'custom_state')
    def _compute_is_locked(self):
        """Simple lock computation"""
        for order in self:
            order.is_locked = order.state == 'done' or order.custom_state == 'completed'

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

    def _compute_is_warning(self):
        """Simple warning computation"""
        for order in self:
            # Simple warning checks
            has_warnings = False

            # Warning if no order lines
            if not order.order_line:
                has_warnings = True

            # Warning if customer has no payment terms and amount > 0
            if order.amount_total > 0 and not order.partner_id.property_payment_term_id:
                has_warnings = True

            order.is_warning = has_warnings

    # Simple workflow methods
    def action_move_to_documentation(self):
        """Move order to documentation stage"""
        self.custom_state = 'documentation'
        return True

    def action_move_to_calculation(self):
        """Move order to calculation stage"""
        self.custom_state = 'calculation'
        return True

    def action_move_to_approved(self):
        """Move order to approved stage"""
        self.custom_state = 'approved'
        return True

    def action_complete_order(self):
        """Mark order as completed"""
        if self.state == 'sale':
            self.write({'state': 'done'})
        self.custom_state = 'completed'
        return True

    def action_unlock_order(self):
        """Unlock order for editing (Admin only)"""
        if not self.can_unlock:
            raise UserError("You don't have permission to unlock orders.")

        if self.state == 'done':
            self.write({'state': 'sale'})
        return True
