# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResPartner(models.Model):
    """Extend res.partner with commission functionality."""
    _inherit = 'res.partner'

    # ================================
    # COMMISSION FIELDS
    # ================================
    
    is_commission_partner = fields.Boolean(
        string='Is Commission Partner',
        default=False,
        help='Check if this partner receives commissions'
    )
    
    commission_partner_type = fields.Selection([
        ('salesperson', 'Salesperson'),
        ('agent', 'Sales Agent'),
        ('referrer', 'Referrer'),
        ('manager', 'Manager'),
    ], string='Commission Partner Type')
    
    default_commission_rule_id = fields.Many2one(
        comodel_name='commission.rule',
        string='Default Commission Rule',
        help='Default commission rule for this partner'
    )
    
    commission_rate = fields.Float(
        string='Default Commission Rate (%)',
        digits=(16, 4),
        help='Default commission rate for this partner'
    )
    
    # ================================
    # COMPUTED FIELDS
    # ================================
    
    commission_allocation_ids = fields.One2many(
        comodel_name='commission.allocation',
        inverse_name='partner_id',
        string='Commission Allocations'
    )
    
    total_commission_earned = fields.Monetary(
        string='Total Commission Earned',
        currency_field='currency_id',
        compute='_compute_commission_stats'
    )
    
    total_commission_paid = fields.Monetary(
        string='Total Commission Paid',
        currency_field='currency_id',
        compute='_compute_commission_stats'
    )
    
    pending_commission = fields.Monetary(
        string='Pending Commission',
        currency_field='currency_id',
        compute='_compute_commission_stats'
    )
    
    commission_count = fields.Integer(
        string='Commission Count',
        compute='_compute_commission_stats'
    )
    
    # ================================
    # COMPUTE METHODS
    # ================================
    
    @api.depends('commission_allocation_ids.commission_amount', 'commission_allocation_ids.state')
    def _compute_commission_stats(self):
        """Compute commission statistics."""
        for partner in self:
            allocations = partner.commission_allocation_ids
            
            partner.commission_count = len(allocations)
            partner.total_commission_earned = sum(allocations.mapped('commission_amount'))
            
            # Paid commissions
            paid_allocations = allocations.filtered(lambda a: a.state == 'paid')
            partner.total_commission_paid = sum(paid_allocations.mapped('commission_amount'))
            
            # Pending commissions
            pending_allocations = allocations.filtered(lambda a: a.state not in ('paid', 'cancelled'))
            partner.pending_commission = sum(pending_allocations.mapped('commission_amount'))
    
    # ================================
    # BUSINESS METHODS
    # ================================
    
    def get_applicable_commission_rule(self, sale_order):
        """
        Get applicable commission rule for this partner and sale order.
        
        Args:
            sale_order: Sale order record
            
        Returns:
            commission.rule: Applicable commission rule or False
        """
        self.ensure_one()
        
        # Start with default rule
        rule = self.default_commission_rule_id
        
        if not rule:
            return False
        
        # Check if rule is applicable
        base_amount = rule.get_base_amount(sale_order)
        if rule.is_applicable(base_amount, sale_order):
            return rule
        
        return False
    
    def calculate_commission_for_sale(self, sale_order):
        """
        Calculate commission amount for a sale order.
        
        Args:
            sale_order: Sale order record
            
        Returns:
            dict: Commission calculation details
        """
        self.ensure_one()
        
        rule = self.get_applicable_commission_rule(sale_order)
        if not rule:
            return {
                'applicable': False,
                'amount': 0.0,
                'rule': False,
                'base_amount': 0.0,
            }
        
        base_amount = rule.get_base_amount(sale_order)
        commission_amount = rule.calculate_commission(base_amount, sale_order)
        
        return {
            'applicable': True,
            'amount': commission_amount,
            'rule': rule,
            'base_amount': base_amount,
            'rate': rule.default_rate if rule.calculation_type == 'percentage' else 0.0,
        }
    
    # ================================
    # ACTION METHODS
    # ================================
    
    def action_view_commissions(self):
        """View partner's commission allocations."""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Commission Allocations - %s') % self.name,
            'res_model': 'commission.allocation',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id}
        }
    
    def action_create_commission_payment(self):
        """Create commission payment for this partner."""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Create Commission Payment'),
            'res_model': 'commission.payment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_partner_id': self.id,
                'default_partner_ids': [(4, self.id)],
            }
        }


class SaleOrder(models.Model):
    """Extend sale.order with commission functionality."""
    _inherit = 'sale.order'

    # ================================
    # COMMISSION FIELDS
    # ================================
    
    commission_allocation_ids = fields.One2many(
        comodel_name='commission.allocation',
        inverse_name='sale_order_id',
        string='Commission Allocations'
    )
    
    has_commissions = fields.Boolean(
        string='Has Commissions',
        compute='_compute_has_commissions',
        store=True
    )
    
    total_commission = fields.Monetary(
        string='Total Commission',
        compute='_compute_commission_totals',
        store=True
    )
    
    commission_partners = fields.Char(
        string='Commission Partners',
        compute='_compute_commission_totals',
        store=True
    )
    
    # ================================
    # COMPUTE METHODS
    # ================================
    
    @api.depends('commission_allocation_ids')
    def _compute_has_commissions(self):
        """Check if order has commission allocations."""
        for order in self:
            order.has_commissions = bool(order.commission_allocation_ids)
    
    @api.depends('commission_allocation_ids.commission_amount', 'commission_allocation_ids.partner_id')
    def _compute_commission_totals(self):
        """Compute commission totals and partners."""
        for order in self:
            allocations = order.commission_allocation_ids
            order.total_commission = sum(allocations.mapped('commission_amount'))
            
            # Get partner names
            partners = allocations.mapped('partner_id.name')
            order.commission_partners = ', '.join(partners) if partners else ''
    
    # ================================
    # BUSINESS METHODS
    # ================================
    
    def _get_commission_partners(self):
        """
        Get commission partners for this sale order.
        
        Returns:
            list: List of partner data for commission creation
        """
        self.ensure_one()
        
        partners = []
        
        # Get commission partner from salesperson
        if self.user_id and self.user_id.partner_id.is_commission_partner:
            partner = self.user_id.partner_id
            rule = partner.get_applicable_commission_rule(self)
            if rule:
                partners.append({
                    'partner_id': partner.id,
                    'rule_id': rule.id,
                    'base_amount': rule.get_base_amount(self),
                    'sequence': 10,
                })
        
        # Get commission partners from order lines (if any product-specific logic needed)
        # This can be extended for more complex commission structures
        
        return partners
    
    def create_commission_allocations(self):
        """Create commission allocations for this order."""
        self.ensure_one()
        
        if self.commission_allocation_ids:
            # Allocations already exist
            return self.commission_allocation_ids
        
        if self.state not in ('sale', 'done'):
            # Order not confirmed yet
            return self.env['commission.allocation']
        
        return self.env['commission.allocation'].create_from_sale_order(self)
    
    # ================================
    # OVERRIDE METHODS
    # ================================
    
    def action_confirm(self):
        """Override to create commission allocations on confirmation."""
        result = super().action_confirm()
        
        # Create commission allocations for confirmed orders
        for order in self:
            if order.state == 'sale':
                order.create_commission_allocations()
        
        return result
    
    # ================================
    # ACTION METHODS
    # ================================
    
    def action_view_commissions(self):
        """View order's commission allocations."""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Commission Allocations - %s') % self.name,
            'res_model': 'commission.allocation',
            'view_mode': 'tree,form',
            'domain': [('sale_order_id', '=', self.id)],
            'context': {'default_sale_order_id': self.id}
        }