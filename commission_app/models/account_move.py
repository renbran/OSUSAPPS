# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountMove(models.Model):
    """Extend account.move with commission functionality."""
    _inherit = 'account.move'

    # ================================
    # COMMISSION FIELDS
    # ================================
    
    commission_allocation_ids = fields.One2many(
        comodel_name='commission.allocation',
        inverse_name='payment_move_id',
        string='Related Commission Allocations',
        help='Commission allocations paid by this move'
    )
    
    is_commission_payment = fields.Boolean(
        string='Is Commission Payment',
        compute='_compute_is_commission_payment',
        store=True,
        help='True if this move is for commission payments'
    )
    
    # ================================
    # COMPUTE METHODS
    # ================================
    
    @api.depends('commission_allocation_ids')
    def _compute_is_commission_payment(self):
        """Check if this move is for commission payments."""
        for move in self:
            move.is_commission_payment = bool(move.commission_allocation_ids)
    
    # ================================
    # ACTION METHODS
    # ================================
    
    def action_view_commission_allocations(self):
        """View related commission allocations."""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Commission Allocations'),
            'res_model': 'commission.allocation',
            'view_mode': 'tree,form',
            'domain': [('payment_move_id', '=', self.id)],
        }