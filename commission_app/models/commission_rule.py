# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class CommissionRule(models.Model):
    """
    Commission Rule Model
    
    Defines the rules for commission calculations including rates,
    calculation methods, and conditions.
    """
    _name = 'commission.rule'
    _description = 'Commission Rule'
    _order = 'sequence, name'
    _rec_name = 'name'

    # ================================
    # CORE FIELDS
    # ================================
    
    name = fields.Char(
        string='Rule Name',
        required=True,
        help='Name of the commission rule'
    )
    
    code = fields.Char(
        string='Code',
        required=True,
        help='Unique code for the commission rule'
    )
    
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Sequence for ordering rules'
    )
    
    active = fields.Boolean(
        string='Active',
        default=True
    )
    
    description = fields.Text(
        string='Description',
        help='Detailed description of the commission rule'
    )
    
    # ================================
    # CALCULATION FIELDS
    # ================================
    
    calculation_type = fields.Selection([
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
        ('tiered', 'Tiered Percentage'),
    ], string='Calculation Type', default='percentage', required=True)
    
    default_rate = fields.Float(
        string='Default Rate (%)',
        digits=(16, 4),
        help='Default commission rate in percentage'
    )
    
    fixed_amount = fields.Monetary(
        string='Fixed Amount',
        currency_field='currency_id',
        help='Fixed commission amount'
    )
    
    # Base calculation field
    base_calculation = fields.Selection([
        ('total', 'Order Total'),
        ('untaxed', 'Untaxed Amount'),
        ('margin', 'Profit Margin'),
        ('custom', 'Custom Calculation'),
    ], string='Base Calculation', default='total', required=True)
    
    # ================================
    # CATEGORY & TYPE FIELDS
    # ================================
    
    commission_category = fields.Selection([
        ('legacy', 'Legacy Commission'),
        ('external', 'External Commission'),  
        ('internal', 'Internal Commission'),
        ('management', 'Management Override'),
        ('bonus', 'Bonus Commission'),
        ('referral', 'Referral Commission'),
        ('sales', 'Sales Commission'),
        ('other', 'Other'),
    ], string='Category', default='internal', required=True)
    
    partner_type = fields.Selection([
        ('salesperson', 'Salesperson'),
        ('agent', 'Sales Agent'),
        ('referrer', 'Referrer'),
        ('manager', 'Manager'),
        ('any', 'Any Partner Type'),
    ], string='Partner Type', default='any')
    
    # ================================
    # CONDITION FIELDS
    # ================================
    
    minimum_amount = fields.Monetary(
        string='Minimum Sale Amount',
        currency_field='currency_id',
        help='Minimum sale amount for commission eligibility'
    )
    
    maximum_amount = fields.Monetary(
        string='Maximum Sale Amount',
        currency_field='currency_id',
        help='Maximum sale amount for commission (0 = no limit)'
    )
    
    # Product category restriction
    allowed_category_ids = fields.Many2many(
        comodel_name='product.category',
        relation='commission_rule_category_rel',
        column1='rule_id',
        column2='category_id',
        string='Allowed Product Categories',
        help='Restrict commission to specific product categories'
    )
    
    # Customer restriction
    allowed_customer_ids = fields.Many2many(
        comodel_name='res.partner',
        relation='commission_rule_customer_rel',
        column1='rule_id',
        column2='customer_id',
        string='Allowed Customers',
        help='Restrict commission to specific customers'
    )
    
    # Date range
    date_start = fields.Date(
        string='Start Date',
        help='Rule effective start date'
    )
    
    date_end = fields.Date(
        string='End Date',
        help='Rule effective end date'
    )
    
    # ================================
    # ACCOUNTING FIELDS
    # ================================
    
    expense_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Commission Expense Account',
        domain=[('account_type', 'in', ['expense', 'expense_depreciation'])],
        help='Account for commission expenses'
    )
    
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )
    
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        default=lambda self: self.env.company
    )
    
    # ================================
    # TIERED CALCULATION FIELDS
    # ================================
    
    tier_ids = fields.One2many(
        comodel_name='commission.rule.tier',
        inverse_name='rule_id',
        string='Commission Tiers',
        help='Tiered commission rates for different amount ranges'
    )
    
    # ================================
    # COMPUTED FIELDS
    # ================================
    
    partner_count = fields.Integer(
        string='Partners Using This Rule',
        compute='_compute_partner_count'
    )
    
    allocation_count = fields.Integer(
        string='Active Allocations',
        compute='_compute_allocation_count'
    )
    
    # ================================
    # COMPUTE METHODS
    # ================================
    
    @api.depends('name')
    def _compute_partner_count(self):
        """Count partners using this rule."""
        for rule in self:
            rule.partner_count = self.env['res.partner'].search_count([
                ('default_commission_rule_id', '=', rule.id)
            ])
    
    @api.depends('name')
    def _compute_allocation_count(self):
        """Count active allocations using this rule."""
        for rule in self:
            rule.allocation_count = self.env['commission.allocation'].search_count([
                ('commission_rule_id', '=', rule.id),
                ('state', '!=', 'cancelled')
            ])
    
    # ================================
    # CONSTRAINT METHODS
    # ================================
    
    @api.constrains('code')
    def _check_code_unique(self):
        """Ensure rule code is unique."""
        for rule in self:
            if self.search_count([('code', '=', rule.code), ('id', '!=', rule.id)]):
                raise ValidationError(_('Commission rule code must be unique.'))
    
    @api.constrains('default_rate')
    def _check_default_rate(self):
        """Validate default rate."""
        for rule in self:
            if rule.calculation_type == 'percentage' and rule.default_rate < 0:
                raise ValidationError(_('Commission rate cannot be negative.'))
            if rule.calculation_type == 'percentage' and rule.default_rate > 100:
                raise ValidationError(_('Commission rate cannot exceed 100%.'))
    
    @api.constrains('fixed_amount')
    def _check_fixed_amount(self):
        """Validate fixed amount."""
        for rule in self:
            if rule.calculation_type == 'fixed' and rule.fixed_amount <= 0:
                raise ValidationError(_('Fixed commission amount must be positive.'))
    
    @api.constrains('minimum_amount', 'maximum_amount')
    def _check_amount_limits(self):
        """Validate amount limits."""
        for rule in self:
            if rule.minimum_amount < 0:
                raise ValidationError(_('Minimum amount cannot be negative.'))
            if rule.maximum_amount > 0 and rule.maximum_amount <= rule.minimum_amount:
                raise ValidationError(_('Maximum amount must be greater than minimum amount.'))
    
    @api.constrains('date_start', 'date_end')
    def _check_date_range(self):
        """Validate date range."""
        for rule in self:
            if rule.date_start and rule.date_end and rule.date_start > rule.date_end:
                raise ValidationError(_('End date must be after start date.'))
    
    # ================================
    # BUSINESS METHODS
    # ================================
    
    def calculate_commission(self, base_amount, sale_order=None):
        """
        Calculate commission amount for given base amount.
        
        Args:
            base_amount (float): Base amount for calculation
            sale_order (sale.order): Optional sale order for context
            
        Returns:
            float: Calculated commission amount
        """
        self.ensure_one()
        
        # Check if rule is applicable
        if not self.is_applicable(base_amount, sale_order):
            return 0.0
        
        if self.calculation_type == 'percentage':
            return (base_amount * self.default_rate) / 100.0
            
        elif self.calculation_type == 'fixed':
            return self.fixed_amount
            
        elif self.calculation_type == 'tiered':
            return self._calculate_tiered_commission(base_amount)
        
        return 0.0
    
    def _calculate_tiered_commission(self, base_amount):
        """Calculate tiered commission."""
        total_commission = 0.0
        remaining_amount = base_amount
        
        for tier in self.tier_ids.sorted('amount_from'):
            if remaining_amount <= 0:
                break
                
            # Calculate amount in this tier
            tier_amount = min(
                remaining_amount,
                (tier.amount_to - tier.amount_from) if tier.amount_to else remaining_amount
            )
            
            # Calculate commission for this tier
            tier_commission = (tier_amount * tier.rate) / 100.0
            total_commission += tier_commission
            
            # Reduce remaining amount
            remaining_amount -= tier_amount
        
        return total_commission
    
    def is_applicable(self, base_amount, sale_order=None):
        """
        Check if rule is applicable for given conditions.
        
        Args:
            base_amount (float): Base amount
            sale_order (sale.order): Optional sale order
            
        Returns:
            bool: True if rule is applicable
        """
        self.ensure_one()
        
        # Check if rule is active
        if not self.active:
            return False
        
        # Check amount limits
        if self.minimum_amount > 0 and base_amount < self.minimum_amount:
            return False
        
        if self.maximum_amount > 0 and base_amount > self.maximum_amount:
            return False
        
        # Check date range
        current_date = fields.Date.today()
        if self.date_start and current_date < self.date_start:
            return False
        
        if self.date_end and current_date > self.date_end:
            return False
        
        # Check sale order conditions if provided
        if sale_order:
            # Check customer restriction
            if self.allowed_customer_ids and sale_order.partner_id not in self.allowed_customer_ids:
                return False
            
            # Check product category restriction
            if self.allowed_category_ids:
                order_categories = sale_order.order_line.mapped('product_id.categ_id')
                if not any(cat in self.allowed_category_ids for cat in order_categories):
                    return False
        
        return True
    
    def get_base_amount(self, sale_order):
        """
        Get base amount for commission calculation.
        
        Args:
            sale_order (sale.order): Sale order
            
        Returns:
            float: Base amount for calculation
        """
        self.ensure_one()
        
        if self.base_calculation == 'total':
            return sale_order.amount_total
        elif self.base_calculation == 'untaxed':
            return sale_order.amount_untaxed
        elif self.base_calculation == 'margin':
            # Calculate profit margin
            return sum(line.margin for line in sale_order.order_line)
        else:
            # Custom calculation - implement as needed
            return sale_order.amount_total
    
    # ================================
    # ACTION METHODS
    # ================================
    
    def action_view_partners(self):
        """View partners using this rule."""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Partners Using Rule: %s') % self.name,
            'res_model': 'res.partner',
            'view_mode': 'tree,form',
            'domain': [('default_commission_rule_id', '=', self.id)],
            'context': {'default_default_commission_rule_id': self.id}
        }
    
    def action_view_allocations(self):
        """View allocations using this rule."""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Allocations for Rule: %s') % self.name,
            'res_model': 'commission.allocation',
            'view_mode': 'tree,form',
            'domain': [('commission_rule_id', '=', self.id)],
            'context': {'default_commission_rule_id': self.id}
        }


class CommissionRuleTier(models.Model):
    """Commission Rule Tier for tiered commission calculations."""
    _name = 'commission.rule.tier'
    _description = 'Commission Rule Tier'
    _order = 'rule_id, amount_from'
    
    rule_id = fields.Many2one(
        comodel_name='commission.rule',
        string='Commission Rule',
        required=True,
        ondelete='cascade'
    )
    
    amount_from = fields.Monetary(
        string='Amount From',
        currency_field='currency_id',
        required=True
    )
    
    amount_to = fields.Monetary(
        string='Amount To',
        currency_field='currency_id',
        help='Leave empty for unlimited upper range'
    )
    
    rate = fields.Float(
        string='Rate (%)',
        digits=(16, 4),
        required=True,
        help='Commission rate for this tier'
    )
    
    currency_id = fields.Many2one(
        related='rule_id.currency_id',
        string='Currency',
        store=True,
        readonly=True
    )
    
    @api.constrains('amount_from', 'amount_to')
    def _check_amount_range(self):
        """Validate amount range."""
        for tier in self:
            if tier.amount_from < 0:
                raise ValidationError(_('Amount from cannot be negative.'))
            if tier.amount_to and tier.amount_to <= tier.amount_from:
                raise ValidationError(_('Amount to must be greater than amount from.'))
    
    @api.constrains('rate')
    def _check_rate(self):
        """Validate commission rate."""
        for tier in self:
            if tier.rate < 0:
                raise ValidationError(_('Commission rate cannot be negative.'))
            if tier.rate > 100:
                raise ValidationError(_('Commission rate cannot exceed 100%.'))