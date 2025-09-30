# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, date
import logging

_logger = logging.getLogger(__name__)


class CommissionCalculationWizard(models.TransientModel):
    """
    Wizard for calculating commissions in batch
    """
    _name = 'commission.calculation.wizard'
    _description = 'Commission Calculation Wizard'

    # Date range for calculation
    date_from = fields.Date(
        string='From Date',
        required=True,
        default=lambda self: date.today().replace(day=1)
    )
    date_to = fields.Date(
        string='To Date',
        required=True,
        default=fields.Date.today
    )

    # Filters
    partner_ids = fields.Many2many(
        'res.partner',
        string='Partners',
        domain=[('is_commission_partner', '=', True)],
        help="Leave empty to calculate for all commission partners"
    )
    commission_rule_ids = fields.Many2many(
        'commission.rule',
        string='Commission Rules',
        domain=[('active', '=', True)],
        help="Leave empty to use all active rules"
    )
    commission_period_id = fields.Many2one(
        'commission.period',
        string='Commission Period',
        help="Leave empty to create allocations without period"
    )

    # Options
    recalculate_existing = fields.Boolean(
        string='Recalculate Existing',
        default=False,
        help="Recalculate commissions that are already calculated"
    )
    auto_confirm = fields.Boolean(
        string='Auto Confirm',
        default=False,
        help="Automatically confirm calculated commissions"
    )
    
    # Results summary
    sale_order_count = fields.Integer(
        string='Sale Orders Found',
        readonly=True
    )
    allocation_count = fields.Integer(
        string='Allocations to Create',
        readonly=True
    )
    estimated_amount = fields.Monetary(
        string='Estimated Total Amount',
        readonly=True,
        currency_field='currency_id'
    )
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id
    )

    @api.onchange('date_from', 'date_to', 'partner_ids', 'commission_rule_ids')
    def _onchange_calculation_params(self):
        """Update calculation preview when parameters change"""
        if self.date_from and self.date_to:
            self._calculate_preview()

    def _calculate_preview(self):
        """Calculate preview statistics"""
        try:
            domain = [
                ('date_order', '>=', self.date_from),
                ('date_order', '<=', self.date_to),
                ('state', 'in', ['sale', 'done'])
            ]

            # Filter by partners if specified
            if self.partner_ids:
                domain.append(('partner_id', 'in', self.partner_ids.ids))

            sale_orders = self.env['sale.order'].search(domain)
            self.sale_order_count = len(sale_orders)
            
            # Estimate allocations and amounts
            estimated_allocations = 0
            estimated_amount = 0.0
            
            for order in sale_orders:
                # Get applicable rules for this order
                applicable_rules = self._get_applicable_rules(order)
                estimated_allocations += len(applicable_rules)
                
                # Rough estimation of commission amount
                for rule in applicable_rules:
                    if rule.calculation_type == 'percentage':
                        estimated_amount += order.amount_total * (rule.default_rate / 100)
                    elif rule.calculation_type == 'fixed':
                        estimated_amount += rule.fixed_amount

            self.allocation_count = estimated_allocations
            self.estimated_amount = estimated_amount

        except Exception as e:
            _logger.warning("Error calculating preview: %s", str(e))
            self.sale_order_count = 0
            self.allocation_count = 0
            self.estimated_amount = 0.0

    def _get_applicable_rules(self, sale_order):
        """Get commission rules applicable to a sale order"""
        rules_domain = [('active', '=', True)]
        
        if self.commission_rule_ids:
            rules_domain.append(('id', 'in', self.commission_rule_ids.ids))

        all_rules = self.env['commission.rule'].search(rules_domain)
        applicable_rules = []

        for rule in all_rules:
            if self._is_rule_applicable(rule, sale_order):
                applicable_rules.append(rule)

        return applicable_rules

    def _is_rule_applicable(self, rule, sale_order):
        """Check if a commission rule is applicable to a sale order"""
        # Check partner conditions
        if rule.allowed_customer_ids and sale_order.partner_id not in rule.allowed_customer_ids:
            return False

        # Check category conditions
        if rule.allowed_category_ids:
            order_categories = sale_order.order_line.mapped('product_id.categ_id')
            if not any(cat in rule.allowed_category_ids for cat in order_categories):
                return False

        # Check amount conditions
        if rule.minimum_amount and sale_order.amount_total < rule.minimum_amount:
            return False
        if rule.maximum_amount and sale_order.amount_total > rule.maximum_amount:
            return False

        # Check date conditions
        if rule.date_start and sale_order.date_order.date() < rule.date_start:
            return False
        if rule.date_end and sale_order.date_order.date() > rule.date_end:
            return False

        return True

    def action_calculate_commissions(self):
        """Execute commission calculation"""
        self.ensure_one()
        
        # Validate date range
        if self.date_from > self.date_to:
            raise ValidationError(_("From Date cannot be later than To Date"))

        try:
            # Get sale orders in date range
            domain = [
                ('date_order', '>=', self.date_from),
                ('date_order', '<=', self.date_to),
                ('state', 'in', ['sale', 'done'])
            ]

            if self.partner_ids:
                # Filter by commission partners (not sale partners)
                commission_partner_sales = []
                for partner in self.partner_ids:
                    partner_sales = self.env['sale.order'].search(domain + [('partner_id', '=', partner.id)])
                    commission_partner_sales.extend(partner_sales.ids)
                domain.append(('id', 'in', commission_partner_sales))

            sale_orders = self.env['sale.order'].search(domain)
            
            created_allocations = self.env['commission.allocation']
            updated_allocations = self.env['commission.allocation']

            for order in sale_orders:
                allocations = self._create_allocations_for_order(order)
                created_allocations |= allocations.get('created', self.env['commission.allocation'])
                updated_allocations |= allocations.get('updated', self.env['commission.allocation'])

            # Auto-confirm if requested
            if self.auto_confirm:
                (created_allocations | updated_allocations).filtered(
                    lambda a: a.state == 'calculated'
                ).action_confirm()

            # Show results
            return self._show_results(created_allocations, updated_allocations)

        except Exception as e:
            _logger.error("Error calculating commissions: %s", str(e))
            raise ValidationError(_("Error calculating commissions: %s") % str(e))

    def _create_allocations_for_order(self, sale_order):
        """Create commission allocations for a sale order"""
        created = self.env['commission.allocation']
        updated = self.env['commission.allocation']
        
        # Get applicable commission rules
        applicable_rules = self._get_applicable_rules(sale_order)
        
        for rule in applicable_rules:
            # Check for existing allocation
            existing_allocation = self.env['commission.allocation'].search([
                ('sale_order_id', '=', sale_order.id),
                ('commission_rule_id', '=', rule.id)
            ], limit=1)

            if existing_allocation:
                if self.recalculate_existing and existing_allocation.state in ['draft', 'calculated']:
                    existing_allocation.action_calculate()
                    updated |= existing_allocation
            else:
                # Find commission partner
                commission_partners = self._get_commission_partners(rule, sale_order)
                
                for partner in commission_partners:
                    allocation_vals = {
                        'sale_order_id': sale_order.id,
                        'partner_id': partner.id,
                        'commission_rule_id': rule.id,
                        'commission_period_id': self.commission_period_id.id if self.commission_period_id else False,
                        'base_amount': sale_order.amount_total,
                    }
                    
                    allocation = self.env['commission.allocation'].create(allocation_vals)
                    allocation.action_calculate()
                    created |= allocation

        return {'created': created, 'updated': updated}

    def _get_commission_partners(self, rule, sale_order):
        """Get partners who should receive commission for this rule and order"""
        partners = self.env['res.partner']

        # Find partners based on rule category and sale context
        if rule.commission_category == 'sales':
            # Sales commission goes to salesperson
            if sale_order.user_id and sale_order.user_id.partner_id.is_commission_partner:
                partners |= sale_order.user_id.partner_id
        elif rule.commission_category in ['legacy', 'external', 'internal']:
            # These categories need specific partner assignment
            # Find partners with this rule as their default
            partners = self.env['res.partner'].search([
                ('is_commission_partner', '=', True),
                ('default_commission_rule_id', '=', rule.id)
            ])

        return partners

    def _show_results(self, created_allocations, updated_allocations):
        """Show calculation results"""
        total_created = len(created_allocations)
        total_updated = len(updated_allocations)
        
        message = _("Commission calculation completed:\n"
                   "- Created: %d allocations\n"
                   "- Updated: %d allocations") % (total_created, total_updated)

        if total_created > 0 or total_updated > 0:
            # Show allocations
            all_allocations = created_allocations | updated_allocations
            return {
                'type': 'ir.actions.act_window',
                'name': _('Calculated Commission Allocations'),
                'res_model': 'commission.allocation',
                'view_mode': 'tree,form',
                'domain': [('id', 'in', all_allocations.ids)],
                'target': 'current',
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Commission Calculation'),
                    'message': _('No commissions were calculated. Please check your criteria.'),
                    'type': 'warning'
                }
            }

    def action_preview_only(self):
        """Preview calculation without executing"""
        self._calculate_preview()
        return {'type': 'ir.actions.act_window_close'}