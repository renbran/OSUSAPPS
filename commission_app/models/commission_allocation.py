# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class CommissionAllocation(models.Model):
    """
    Commission Allocation Model - Similar to Order Lines Structure
    
    This model represents individual commission allocations for sales transactions.
    Each sale can have multiple commission allocations for different partners,
    similar to how sales orders have multiple order lines.
    """
    _name = 'commission.allocation'
    _description = 'Commission Allocation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sale_order_id, sequence, id'
    _rec_name = 'display_name'

    # ================================
    # CORE FIELDS
    # ================================

    # Reference number
    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
        help='Unique reference number for commission allocation'
    )

    # Sequence for ordering (like order lines)
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Sequence for ordering commission allocations'
    )
    
    # Main relationship to sale order
    sale_order_id = fields.Many2one(
        comodel_name='sale.order',
        string='Sale Order',
        required=True,
        ondelete='cascade',
        index=True,
        tracking=True
    )
    
    # Commission partner (who gets the commission)
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Commission Partner',
        required=True,
        domain=[('is_commission_partner', '=', True)],
        ondelete='restrict',
        index=True,
        tracking=True
    )
    
    # Commission rule that defines calculation
    commission_rule_id = fields.Many2one(
        comodel_name='commission.rule',
        string='Commission Rule',
        required=True,
        ondelete='restrict',
        tracking=True
    )
    
    # ================================
    # CALCULATION FIELDS
    # ================================
    
    # Base amount for commission calculation
    base_amount = fields.Monetary(
        string='Base Amount',
        currency_field='currency_id',
        help='Amount on which commission is calculated',
        tracking=True
    )
    
    # Commission rate (percentage or fixed)
    commission_rate = fields.Float(
        string='Commission Rate (%)',
        digits=(16, 4),
        tracking=True,
        help='Commission rate in percentage'
    )
    
    # Fixed commission amount (alternative to percentage)
    fixed_amount = fields.Monetary(
        string='Fixed Amount',
        currency_field='currency_id',
        help='Fixed commission amount (if not percentage-based)',
        tracking=True
    )
    
    # Calculated commission amount
    commission_amount = fields.Monetary(
        string='Commission Amount',
        currency_field='currency_id',
        compute='_compute_commission_amount',
        store=True,
        tracking=True,
        help='Final calculated commission amount'
    )
    
    # ================================
    # STATE & WORKFLOW FIELDS
    # ================================
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('calculated', 'Calculated'),
        ('confirmed', 'Confirmed'),
        ('processed', 'Processed'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ], string='State', default='draft', tracking=True, copy=False)
    
    # Period for commission grouping
    commission_period_id = fields.Many2one(
        comodel_name='commission.period',
        string='Commission Period',
        ondelete='restrict',
        index=True
    )
    
    # ================================
    # REFERENCE & TRACKING FIELDS
    # ================================
    
    # Reference to generated payment/invoice
    payment_move_id = fields.Many2one(
        comodel_name='account.move',
        string='Payment Entry',
        ondelete='set null',
        help='Accounting entry for commission payment'
    )
    
    # Payment date
    payment_date = fields.Date(
        string='Payment Date',
        tracking=True
    )
    
    # Notes and description
    description = fields.Text(
        string='Description',
        help='Additional notes for this commission allocation'
    )
    
    # ================================
    # RELATED & COMPUTED FIELDS
    # ================================
    
    # Currency from sale order
    currency_id = fields.Many2one(
        related='sale_order_id.currency_id',
        string='Currency',
        store=True,
        readonly=True
    )
    
    # Sale order date
    sale_date = fields.Datetime(
        related='sale_order_id.date_order',
        string='Sale Date',
        store=True,
        readonly=True,
        index=True
    )
    
    # Customer from sale order
    customer_id = fields.Many2one(
        related='sale_order_id.partner_id',
        string='Customer',
        store=True,
        readonly=True
    )
    
    # Salesperson from sale order
    salesperson_id = fields.Many2one(
        related='sale_order_id.user_id',
        string='Salesperson',
        store=True,
        readonly=True
    )
    
    # Sale order total
    sale_amount_total = fields.Monetary(
        related='sale_order_id.amount_total',
        string='Sale Total',
        store=True,
        readonly=True
    )

    # Company from sale order
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        related='sale_order_id.company_id',
        store=True,
        readonly=True,
        index=True,
        help='Company associated with this commission allocation'
    )

    # Display name for the record
    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True
    )
    
    # ================================
    # COMPUTE METHODS
    # ================================
    
    @api.depends('commission_rule_id', 'base_amount', 'commission_rate', 'fixed_amount')
    def _compute_commission_amount(self):
        """Calculate commission amount based on rule and rate."""
        for allocation in self:
            if not allocation.commission_rule_id:
                allocation.commission_amount = 0.0
                continue
                
            rule = allocation.commission_rule_id
            
            if rule.calculation_type == 'percentage':
                # Percentage-based calculation
                rate = allocation.commission_rate or rule.default_rate
                allocation.commission_amount = (allocation.base_amount * rate) / 100.0
                
            elif rule.calculation_type == 'fixed':
                # Fixed amount
                allocation.commission_amount = allocation.fixed_amount or rule.fixed_amount
                
            elif rule.calculation_type == 'tiered':
                # Tiered calculation (implement based on rule tiers)
                allocation.commission_amount = allocation._calculate_tiered_commission()
                
            else:
                allocation.commission_amount = 0.0
    
    @api.depends('sale_order_id', 'partner_id', 'commission_amount')
    def _compute_display_name(self):
        """Generate display name for the allocation."""
        for allocation in self:
            if allocation.sale_order_id and allocation.partner_id:
                allocation.display_name = _('%s - %s (%s)') % (
                    allocation.sale_order_id.name,
                    allocation.partner_id.name,
                    allocation.commission_amount
                )
            else:
                allocation.display_name = _('Commission Allocation')
    
    def _calculate_tiered_commission(self):
        """Calculate tiered commission based on rule tiers."""
        # Implement tiered calculation logic here
        # This would read from commission_rule_id.tier_ids and calculate accordingly
        return 0.0
    
    # ================================
    # ONCHANGE METHODS
    # ================================
    
    @api.onchange('sale_order_id')
    def _onchange_sale_order_id(self):
        """Set base amount when sale order changes."""
        if self.sale_order_id:
            # Default base amount to sale order total
            self.base_amount = self.sale_order_id.amount_total
            
            # Auto-assign commission period
            period = self.env['commission.period'].get_period_for_date(
                self.sale_order_id.date_order
            )
            if period:
                self.commission_period_id = period
    
    @api.onchange('commission_rule_id')
    def _onchange_commission_rule_id(self):
        """Set default rate when rule changes."""
        if self.commission_rule_id:
            rule = self.commission_rule_id
            if rule.calculation_type == 'percentage':
                self.commission_rate = rule.default_rate
            elif rule.calculation_type == 'fixed':
                self.fixed_amount = rule.fixed_amount
    
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """Set default commission rule based on partner."""
        if self.partner_id and self.partner_id.default_commission_rule_id:
            self.commission_rule_id = self.partner_id.default_commission_rule_id
    
    # ================================
    # CONSTRAINT METHODS
    # ================================
    
    @api.constrains('commission_rate')
    def _check_commission_rate(self):
        """Validate commission rate."""
        for allocation in self:
            if allocation.commission_rate < 0:
                raise ValidationError(_('Commission rate cannot be negative.'))
            if allocation.commission_rate > 100:
                raise ValidationError(_('Commission rate cannot exceed 100%.'))
    
    @api.constrains('base_amount', 'fixed_amount', 'commission_amount')
    def _check_amounts(self):
        """Validate amounts."""
        for allocation in self:
            if allocation.base_amount < 0:
                raise ValidationError(_('Base amount cannot be negative.'))
            if allocation.fixed_amount < 0:
                raise ValidationError(_('Fixed amount cannot be negative.'))
            if allocation.commission_amount < 0:
                raise ValidationError(_('Commission amount cannot be negative.'))
    
    # ================================
    # ACTION METHODS
    # ================================
    
    def action_calculate(self):
        """Calculate commission amount and move to calculated state."""
        for allocation in self:
            if allocation.state != 'draft':
                raise UserError(_('Only draft allocations can be calculated.'))
            
            # Trigger computation
            allocation._compute_commission_amount()
            allocation.state = 'calculated'
            
        return True
    
    def action_confirm(self):
        """Confirm commission calculation."""
        for allocation in self:
            if allocation.state != 'calculated':
                raise UserError(_('Only calculated allocations can be confirmed.'))
            
            allocation.state = 'confirmed'
            
        return True
    
    def action_process(self):
        """Process commission for payment."""
        for allocation in self:
            if allocation.state != 'confirmed':
                raise UserError(_('Only confirmed allocations can be processed.'))
            
            allocation.state = 'processed'
            
        return True
    
    def action_pay(self):
        """Mark commission as paid and create payment entry."""
        for allocation in self:
            if allocation.state != 'processed':
                raise UserError(_('Only processed allocations can be paid.'))
            
            # Create payment entry
            allocation._create_payment_entry()
            allocation.state = 'paid'
            allocation.payment_date = fields.Date.today()
            
        return True
    
    def action_cancel(self):
        """Cancel commission allocation."""
        for allocation in self:
            if allocation.state == 'paid':
                raise UserError(_('Paid allocations cannot be cancelled.'))
            
            allocation.state = 'cancelled'
            
        return True
    
    def action_reset_to_draft(self):
        """Reset allocation to draft state."""
        for allocation in self:
            if allocation.state == 'paid':
                raise UserError(_('Paid allocations cannot be reset.'))
            
            allocation.state = 'draft'
            
        return True
    
    # ================================
    # BUSINESS METHODS
    # ================================
    
    def _create_payment_entry(self):
        """Create accounting entry for commission payment."""
        self.ensure_one()
        
        if not self.commission_amount:
            raise UserError(_('Cannot create payment entry with zero commission amount.'))
        
        # Get commission expense account
        expense_account = self.commission_rule_id.expense_account_id

        if not expense_account:
            raise UserError(_(
                'Please configure commission expense account in commission rule: %s'
            ) % self.commission_rule_id.name)
        
        # Get partner payable account
        payable_account = self.partner_id.property_account_payable_id
        
        if not payable_account:
            raise UserError(_('Partner %s has no payable account configured.') % self.partner_id.name)
        
        # Create journal entry
        move_vals = {
            'journal_id': self._get_commission_journal().id,
            'date': fields.Date.today(),
            'ref': _('Commission: %s') % self.display_name,
            'line_ids': [
                # Debit commission expense
                (0, 0, {
                    'account_id': expense_account.id,
                    'name': _('Commission: %s') % self.display_name,
                    'debit': self.commission_amount,
                    'credit': 0.0,
                    'partner_id': self.partner_id.id,
                }),
                # Credit partner payable
                (0, 0, {
                    'account_id': payable_account.id,
                    'name': _('Commission: %s') % self.display_name,
                    'debit': 0.0,
                    'credit': self.commission_amount,
                    'partner_id': self.partner_id.id,
                }),
            ]
        }
        
        move = self.env['account.move'].create(move_vals)
        move.action_post()
        
        self.payment_move_id = move
        
        return move
    
    def _get_commission_journal(self):
        """Get the commission journal."""
        journal = self.env['account.journal'].search([
            ('code', '=', 'COMM'),
            ('company_id', '=', self.company_id.id)
        ], limit=1)
        
        if not journal:
            # Fallback to miscellaneous journal
            journal = self.env['account.journal'].search([
                ('type', '=', 'general'),
                ('company_id', '=', self.company_id.id)
            ], limit=1)
        
        if not journal:
            raise UserError(_('No suitable journal found for commission entries.'))
        
        return journal
    
    # ================================
    # UTILITY METHODS
    # ================================
    
    @api.model
    def create_from_sale_order(self, sale_order):
        """Create commission allocations for a sale order."""
        allocations = self.env['commission.allocation']
        
        # Get commission partners for this sale
        partners = sale_order._get_commission_partners()
        
        for partner_data in partners:
            allocation_vals = {
                'sale_order_id': sale_order.id,
                'partner_id': partner_data['partner_id'],
                'commission_rule_id': partner_data['rule_id'],
                'base_amount': partner_data.get('base_amount', sale_order.amount_total),
                'sequence': partner_data.get('sequence', 10),
            }
            
            allocation = self.create(allocation_vals)
            allocations |= allocation
        
        return allocations
    
    @api.model
    def calculate_pending_commissions(self):
        """Calculate all pending commission allocations."""
        pending_allocations = self.search([('state', '=', 'draft')])
        pending_allocations.action_calculate()
        
        return len(pending_allocations)
    
    # ================================
    # REPORTING METHODS
    # ================================
    
    def get_commission_summary(self):
        """Get commission summary for reporting."""
        return {
            'total_commission': sum(self.mapped('commission_amount')),
            'count': len(self),
            'by_partner': self._group_by_partner(),
            'by_period': self._group_by_period(),
        }
    
    def _group_by_partner(self):
        """Group commissions by partner."""
        result = {}
        for allocation in self:
            partner = allocation.partner_id
            if partner.id not in result:
                result[partner.id] = {
                    'partner': partner.name,
                    'count': 0,
                    'amount': 0.0
                }
            result[partner.id]['count'] += 1
            result[partner.id]['amount'] += allocation.commission_amount
        return result
    
    # ================================
    # ORM OVERRIDE METHODS
    # ================================

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to assign sequence numbers."""
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'commission.allocation'
                ) or _('New')
        return super(CommissionAllocation, self).create(vals_list)

    def _group_by_period(self):
        """Group commissions by period."""
        result = {}
        for allocation in self:
            period = allocation.commission_period_id
            if not period:
                continue
                
            if period.id not in result:
                result[period.id] = {
                    'period': period.name,
                    'count': 0,
                    'amount': 0.0
                }
            result[period.id]['count'] += 1
            result[period.id]['amount'] += allocation.commission_amount
        return result