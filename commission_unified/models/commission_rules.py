# -*- coding: utf-8 -*-
#############################################################################
#
#    Unified Commission Management System - Commission Rules Engine
#    Manages rule-based commission calculations and configurations
#
#############################################################################

import logging
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class CommissionRules(models.Model):
    """
    Commission Rules Engine - Manages rule-based commission calculations
    Based on sales_commission_users approach but enhanced for unified system
    """
    _name = "commission.rules"
    _description = "Commission Rules"
    _order = "sequence, name"

    name = fields.Char(string="Rule Name", required=True, help="Name of the commission rule")
    sequence = fields.Integer(string="Sequence", default=10, help="Sequence for rule application order")
    active = fields.Boolean(string="Active", default=True)

    # Sales Person Assignment
    sales_person_ids = fields.Many2many('res.users', string='Sales Persons',
                                        help="Sales persons this rule applies to. Leave empty for global rules")

    # Commission Type
    commission_type = fields.Selection([
        ('standard', 'Standard Commission'),
        ('partner_based', 'Partner Based Commission'),
        ('product_based', 'Product Based Commission'),
        ('discount_based', 'Discount Based Commission')
    ], string="Commission Type", required=True, help="Type of commission calculation")

    # Standard Commission
    std_commission_perc = fields.Float(string='Standard Commission %',
                                       help="Standard commission percentage", digits=(16, 4))

    # Partner-based Commission
    affiliated_commission_perc = fields.Float(string='Affiliated Partner Commission %',
                                              help="Commission % for affiliated partners", digits=(16, 4))
    non_affiliated_commission_perc = fields.Float(string='Non-Affiliated Partner Commission %',
                                                  help="Commission % for non-affiliated partners", digits=(16, 4))

    # Product-based Commission Rules
    product_based_ids = fields.One2many("commission.product.rule", 'commission_rule_id',
                                        string='Product Commission Rules',
                                        help="Product-specific commission rules")

    # Discount-based Commission Rules
    discount_based_ids = fields.One2many("commission.discount.rule", 'commission_rule_id',
                                         string='Discount Commission Rules',
                                         help="Discount-based commission rules")

    # Rule Conditions
    date_from = fields.Date(string="Valid From", help="Rule is valid from this date")
    date_to = fields.Date(string="Valid To", help="Rule is valid until this date")

    min_order_amount = fields.Monetary(string="Minimum Order Amount",
                                       help="Minimum order amount for rule to apply")
    max_order_amount = fields.Monetary(string="Maximum Order Amount",
                                       help="Maximum order amount for rule to apply")

    # Partner and Product Filters
    partner_ids = fields.Many2many('res.partner', string='Specific Partners',
                                   help="Rule applies only to these partners (empty = all)")
    product_category_ids = fields.Many2many('product.category', string='Product Categories',
                                            help="Rule applies only to these product categories (empty = all)")

    # Company and Currency
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id)

    # Rule Description and Notes
    description = fields.Text(string="Description", help="Detailed description of the rule")
    notes = fields.Text(string="Internal Notes", help="Internal notes for rule management")

    # Statistics
    usage_count = fields.Integer(string="Usage Count", readonly=True,
                                  help="Number of times this rule has been applied")
    last_used_date = fields.Datetime(string="Last Used", readonly=True)

    @api.constrains('std_commission_perc', 'affiliated_commission_perc', 'non_affiliated_commission_perc')
    def _check_commission_percentages(self):
        """Validate commission percentages"""
        for rule in self:
            percentages = [
                rule.std_commission_perc,
                rule.affiliated_commission_perc,
                rule.non_affiliated_commission_perc
            ]

            for perc in percentages:
                if perc < 0 or perc > 100:
                    raise ValidationError(_("Commission percentages must be between 0 and 100"))

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        """Validate date ranges"""
        for rule in self:
            if rule.date_from and rule.date_to and rule.date_from > rule.date_to:
                raise ValidationError(_("'Valid From' date must be before 'Valid To' date"))

    @api.constrains('min_order_amount', 'max_order_amount')
    def _check_amounts(self):
        """Validate amount ranges"""
        for rule in self:
            if rule.min_order_amount and rule.max_order_amount:
                if rule.min_order_amount > rule.max_order_amount:
                    raise ValidationError(_("Minimum order amount must be less than maximum order amount"))

    def check_rule_applicability(self, sale_order):
        """
        Check if this rule applies to the given sale order
        Returns True if rule should be applied, False otherwise
        """
        self.ensure_one()

        if not self.active:
            return False

        # Check sales person
        if self.sales_person_ids and sale_order.user_id not in self.sales_person_ids:
            return False

        # Check date range
        order_date = sale_order.date_order or fields.Date.today()
        if self.date_from and order_date < self.date_from:
            return False
        if self.date_to and order_date > self.date_to:
            return False

        # Check order amount range
        if self.min_order_amount and sale_order.amount_total < self.min_order_amount:
            return False
        if self.max_order_amount and sale_order.amount_total > self.max_order_amount:
            return False

        # Check specific partners
        if self.partner_ids and sale_order.partner_id not in self.partner_ids:
            return False

        # Check product categories
        if self.product_category_ids:
            order_categories = sale_order.order_line.mapped('product_id.categ_id')
            if not any(cat in self.product_category_ids for cat in order_categories):
                return False

        # Check company
        if self.company_id and sale_order.company_id != self.company_id:
            return False

        return True

    def calculate_commission(self, sale_order):
        """
        Calculate commission amount for this rule and sale order
        Returns the calculated commission amount
        """
        self.ensure_one()

        if not self.check_rule_applicability(sale_order):
            return 0.0

        commission_amount = 0.0

        try:
            if self.commission_type == 'standard':
                commission_amount = sale_order.amount_total * (self.std_commission_perc / 100.0)

            elif self.commission_type == 'partner_based':
                if hasattr(sale_order.partner_id, 'affiliated') and sale_order.partner_id.affiliated:
                    commission_amount = sale_order.amount_total * (self.affiliated_commission_perc / 100.0)
                else:
                    commission_amount = sale_order.amount_total * (self.non_affiliated_commission_perc / 100.0)

            elif self.commission_type == 'product_based':
                for product_rule in self.product_based_ids:
                    order_lines = sale_order.order_line.filtered(
                        lambda line: line.product_id == product_rule.product_id
                    )
                    for line in order_lines:
                        commission_amount += line.price_subtotal * (product_rule.commission_perc / 100.0)

            elif self.commission_type == 'discount_based':
                for discount_rule in self.discount_based_ids:
                    applicable_lines = sale_order.order_line.filtered(
                        lambda line: line.discount >= discount_rule.min_discount
                    )
                    if applicable_lines:
                        # Apply commission to the total order amount if any line meets discount criteria
                        commission_amount += sale_order.amount_total * (discount_rule.commission_perc / 100.0)
                        break  # Only apply highest matching rule

            # Update usage statistics
            self.usage_count += 1
            self.last_used_date = fields.Datetime.now()

            _logger.info(f"Rule {self.name} calculated commission: {commission_amount} for order {sale_order.name}")

        except Exception as e:
            _logger.error(f"Error calculating commission for rule {self.name}: {str(e)}")
            raise UserError(_("Error calculating commission for rule %s: %s") % (self.name, str(e)))

        return commission_amount

    @api.model
    def find_applicable_rules(self, sale_order):
        """
        Find all rules that apply to the given sale order
        Returns recordset of applicable rules
        """
        all_rules = self.search([('active', '=', True)], order='sequence, id')
        applicable_rules = self.env['commission.rules']

        for rule in all_rules:
            if rule.check_rule_applicability(sale_order):
                applicable_rules |= rule

        _logger.info(f"Found {len(applicable_rules)} applicable rules for order {sale_order.name}")
        return applicable_rules

    def action_test_rule(self):
        """
        Test this rule with recent sale orders
        """
        self.ensure_one()

        # Find recent sale orders for testing
        test_orders = self.env['sale.order'].search([
            ('state', 'in', ['sale', 'done']),
            ('date_order', '>=', fields.Date.subtract(fields.Date.today(), months=1))
        ], limit=10)

        test_results = []
        for order in test_orders:
            applicable = self.check_rule_applicability(order)
            commission = 0.0
            if applicable:
                commission = self.calculate_commission(order)

            test_results.append({
                'order_name': order.name,
                'order_amount': order.amount_total,
                'applicable': applicable,
                'commission_amount': commission,
            })

        return {
            'type': 'ir.actions.act_window',
            'name': f'Test Results - {self.name}',
            'view_mode': 'tree',
            'res_model': 'commission.rule.test.result',
            'target': 'new',
            'context': {
                'default_rule_id': self.id,
                'default_test_results': test_results
            }
        }

    def name_get(self):
        """Custom name display"""
        result = []
        for rule in self:
            name = rule.name
            if rule.commission_type:
                name += f" ({rule.commission_type.replace('_', ' ').title()})"
            if not rule.active:
                name += " [Inactive]"
            result.append((rule.id, name))
        return result


class CommissionProductRule(models.Model):
    """Product-specific commission rules"""
    _name = "commission.product.rule"
    _description = "Product Commission Rule"
    _order = "sequence, product_id"

    commission_rule_id = fields.Many2one("commission.rules", string='Commission Rule',
                                         required=True, ondelete='cascade')
    sequence = fields.Integer(string="Sequence", default=10)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    commission_perc = fields.Float(string='Commission %', required=True, digits=(16, 4))

    @api.constrains('commission_perc')
    def _check_commission_percentage(self):
        """Validate commission percentage"""
        for rule in self:
            if rule.commission_perc < 0 or rule.commission_perc > 100:
                raise ValidationError(_("Commission percentage must be between 0 and 100"))

    def name_get(self):
        """Custom name display"""
        result = []
        for rule in self:
            name = f"{rule.product_id.name} - {rule.commission_perc}%"
            result.append((rule.id, name))
        return result


class CommissionDiscountRule(models.Model):
    """Discount-based commission rules"""
    _name = "commission.discount.rule"
    _description = "Discount Commission Rule"
    _order = "min_discount desc"

    commission_rule_id = fields.Many2one("commission.rules", string='Commission Rule',
                                         required=True, ondelete='cascade')
    min_discount = fields.Float(string='Minimum Discount %', required=True, digits=(16, 4))
    max_discount = fields.Float(string='Maximum Discount %', digits=(16, 4))
    commission_perc = fields.Float(string='Commission %', required=True, digits=(16, 4))

    @api.constrains('min_discount', 'max_discount', 'commission_perc')
    def _check_percentages(self):
        """Validate percentages"""
        for rule in self:
            if rule.min_discount < 0 or rule.min_discount > 100:
                raise ValidationError(_("Minimum discount must be between 0 and 100"))
            if rule.max_discount and (rule.max_discount < 0 or rule.max_discount > 100):
                raise ValidationError(_("Maximum discount must be between 0 and 100"))
            if rule.max_discount and rule.min_discount > rule.max_discount:
                raise ValidationError(_("Minimum discount must be less than maximum discount"))
            if rule.commission_perc < 0 or rule.commission_perc > 100:
                raise ValidationError(_("Commission percentage must be between 0 and 100"))

    def name_get(self):
        """Custom name display"""
        result = []
        for rule in self:
            if rule.max_discount:
                name = f"Discount {rule.min_discount}%-{rule.max_discount}% → {rule.commission_perc}%"
            else:
                name = f"Discount ≥{rule.min_discount}% → {rule.commission_perc}%"
            result.append((rule.id, name))
        return result


class CommissionRuleTestResult(models.TransientModel):
    """Transient model for rule testing results"""
    _name = 'commission.rule.test.result'
    _description = 'Commission Rule Test Result'

    rule_id = fields.Many2one('commission.rules', string='Rule', readonly=True)
    order_name = fields.Char(string='Order', readonly=True)
    order_amount = fields.Monetary(string='Order Amount', readonly=True)
    applicable = fields.Boolean(string='Rule Applicable', readonly=True)
    commission_amount = fields.Monetary(string='Commission Amount', readonly=True)