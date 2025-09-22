# -*- coding: utf-8 -*-
#############################################################################
#
#    Unified Commission Management System - Commission Calculator
#    The core calculation engine combining all commission types and methods
#
#############################################################################

import logging
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class CommissionCalculator(models.Model):
    """
    Unified Commission Calculator - The heart of the commission system
    Combines calculation methods from both sales_commission_users and commission_ax
    """
    _name = 'commission.calculator'
    _description = 'Commission Calculator Engine'

    name = fields.Char(string="Calculator Name", default="Unified Commission Calculator")
    active = fields.Boolean(string="Active", default=True)

    def calculate_all_commissions(self, sale_order):
        """
        Master method to calculate ALL commission types for a sale order
        Returns list of commission line data ready for creation
        """
        self.ensure_one()

        if not sale_order:
            raise UserError(_("Sale order is required for commission calculation"))

        _logger.info(f"Starting unified commission calculation for order {sale_order.name}")

        commission_lines_data = []

        try:
            # 1. Calculate Stakeholder-based commissions (from commission_ax)
            stakeholder_commissions = self._calculate_stakeholder_commissions(sale_order)
            commission_lines_data.extend(stakeholder_commissions)

            # 2. Calculate Rule-based commissions (from sales_commission_users)
            rule_commissions = self._calculate_rule_based_commissions(sale_order)
            commission_lines_data.extend(rule_commissions)

            # 3. Calculate Legacy commissions (backward compatibility)
            legacy_commissions = self._calculate_legacy_commissions(sale_order)
            commission_lines_data.extend(legacy_commissions)

            _logger.info(f"Commission calculation completed for {sale_order.name}: {len(commission_lines_data)} lines")

            return commission_lines_data

        except Exception as e:
            _logger.error(f"Commission calculation failed for {sale_order.name}: {str(e)}")
            raise UserError(_("Commission calculation failed: %s") % str(e))

    def _calculate_stakeholder_commissions(self, sale_order):
        """
        Calculate External and Internal stakeholder commissions (from commission_ax approach)
        """
        commission_lines = []

        # External Commissions
        external_partners = [
            ('broker_partner_id', 'external_broker', 'broker_commission_type', 'broker_rate'),
            ('referrer_partner_id', 'external_referrer', 'referrer_commission_type', 'referrer_rate'),
            ('cashback_partner_id', 'external_cashback', 'cashback_commission_type', 'cashback_rate'),
            ('other_external_partner_id', 'external_other', 'other_external_commission_type', 'other_external_rate'),
        ]

        for partner_field, commission_type, type_field, rate_field in external_partners:
            partner = getattr(sale_order, partner_field, None)
            commission_method = getattr(sale_order, type_field, 'percent_unit_price')
            rate = getattr(sale_order, rate_field, 0.0)

            if partner and rate > 0:
                amount = self._calculate_commission_amount(sale_order, commission_method, rate)
                if amount > 0:
                    commission_lines.append({
                        'sale_order_id': sale_order.id,
                        'partner_id': partner.id,
                        'commission_type': commission_type,
                        'calculation_method': commission_method,
                        'commission_rate': rate,
                        'commission_amount': amount,
                        'base_amount': self._get_base_amount(sale_order, commission_method),
                        'description': f"{commission_type.replace('_', ' ').title()} Commission for {sale_order.name}",
                        'status': 'calculated',
                        'date': sale_order.date_order or fields.Date.today(),
                        'sales_person_id': sale_order.user_id.id,
                    })

        # Internal Commissions
        internal_partners = [
            ('agent1_partner_id', 'internal_agent1', 'agent1_commission_type', 'agent1_rate'),
            ('agent2_partner_id', 'internal_agent2', 'agent2_commission_type', 'agent2_rate'),
            ('manager_partner_id', 'internal_manager', 'manager_commission_type', 'manager_rate'),
            ('director_partner_id', 'internal_director', 'director_commission_type', 'director_rate'),
        ]

        for partner_field, commission_type, type_field, rate_field in internal_partners:
            partner = getattr(sale_order, partner_field, None)
            commission_method = getattr(sale_order, type_field, 'percent_unit_price')
            rate = getattr(sale_order, rate_field, 0.0)

            if partner and rate > 0:
                amount = self._calculate_commission_amount(sale_order, commission_method, rate)
                if amount > 0:
                    commission_lines.append({
                        'sale_order_id': sale_order.id,
                        'partner_id': partner.id,
                        'commission_type': commission_type,
                        'calculation_method': commission_method,
                        'commission_rate': rate,
                        'commission_amount': amount,
                        'base_amount': self._get_base_amount(sale_order, commission_method),
                        'description': f"{commission_type.replace('_', ' ').title()} Commission for {sale_order.name}",
                        'status': 'calculated',
                        'date': sale_order.date_order or fields.Date.today(),
                        'sales_person_id': sale_order.user_id.id,
                    })

        _logger.info(f"Calculated {len(commission_lines)} stakeholder commissions for {sale_order.name}")
        return commission_lines

    def _calculate_legacy_commissions(self, sale_order):
        """
        Calculate Legacy percentage-based commissions (backward compatibility)
        """
        commission_lines = []

        # Legacy commission partners with percentage fields
        legacy_partners = [
            ('consultant_id', 'legacy_consultant', 'consultant_comm_percentage'),
            ('manager_id', 'legacy_manager', 'manager_comm_percentage'),
            ('second_agent_id', 'legacy_second_agent', 'second_agent_comm_percentage'),
            ('director_id', 'legacy_director', 'director_comm_percentage'),
        ]

        for partner_field, commission_type, percentage_field in legacy_partners:
            partner = getattr(sale_order, partner_field, None)
            percentage = getattr(sale_order, percentage_field, 0.0)

            if partner and percentage > 0:
                # Legacy commissions always use percentage of untaxed total
                amount = sale_order.amount_untaxed * (percentage / 100.0)
                if amount > 0:
                    commission_lines.append({
                        'sale_order_id': sale_order.id,
                        'partner_id': partner.id,
                        'commission_type': commission_type,
                        'calculation_method': 'percent_untaxed_total',
                        'commission_rate': percentage,
                        'commission_amount': amount,
                        'base_amount': sale_order.amount_untaxed,
                        'description': f"{commission_type.replace('_', ' ').title()} for {sale_order.name}",
                        'status': 'calculated',
                        'date': sale_order.date_order or fields.Date.today(),
                        'sales_person_id': sale_order.user_id.id,
                        'source_module': 'legacy_compatibility',
                    })

        _logger.info(f"Calculated {len(commission_lines)} legacy commissions for {sale_order.name}")
        return commission_lines

    def _calculate_rule_based_commissions(self, sale_order):
        """
        Calculate Rule-based commissions (from sales_commission_users approach)
        """
        commission_lines = []

        # Find applicable commission rules for this sale order
        commission_rules = self.env['commission.rules'].search([
            ('active', '=', True),
            '|', ('sales_person_ids', 'in', sale_order.user_id.id),
            ('sales_person_ids', '=', False)  # Global rules
        ])

        for rule in commission_rules:
            amount = 0.0
            description = ''

            if rule.commission_type == 'standard':
                description = f'Standard Commission - {rule.name}'
                amount = sale_order.amount_total * (rule.std_commission_perc / 100.0)

            elif rule.commission_type == 'partner_based':
                if hasattr(sale_order.partner_id, 'affiliated') and sale_order.partner_id.affiliated:
                    description = f'Partner Commission (Affiliated) - {rule.name}'
                    amount = sale_order.amount_total * (rule.affiliated_commission_perc / 100.0)
                else:
                    description = f'Partner Commission (Non-Affiliated) - {rule.name}'
                    amount = sale_order.amount_total * (rule.non_affiliated_commission_perc / 100.0)

            elif rule.commission_type == 'product_based':
                for product_rule in rule.product_based_ids:
                    order_lines = sale_order.order_line.filtered(
                        lambda line: line.product_id == product_rule.product_id
                    )
                    if order_lines:
                        description = f'Product Commission - {product_rule.product_id.name}'
                        amount += sum(order_lines.mapped('price_subtotal')) * (product_rule.commission / 100.0)

            elif rule.commission_type == 'discount_based':
                for discount_rule in rule.discount_based_ids:
                    order_lines = sale_order.order_line.filtered(
                        lambda line: line.discount >= discount_rule.discount
                    )
                    if order_lines:
                        description = f'Discount Commission - {discount_rule.discount}%'
                        amount += sale_order.amount_total * (discount_rule.commission / 100.0)

            if amount > 0 and description:
                # Use the sales person from the rule or the order
                sales_person = rule.sales_person_ids[0] if rule.sales_person_ids else sale_order.user_id

                commission_lines.append({
                    'sale_order_id': sale_order.id,
                    'partner_id': sales_person.partner_id.id if sales_person.partner_id else sales_person.id,
                    'commission_type': f'rule_{rule.commission_type}',
                    'calculation_method': 'rule_based',
                    'commission_rate': 0.0,  # Rate is embedded in the rule
                    'commission_amount': amount,
                    'base_amount': sale_order.amount_total,
                    'description': description,
                    'status': 'calculated',
                    'date': sale_order.date_order or fields.Date.today(),
                    'sales_person_id': sales_person.id,
                    'commission_rule_id': rule.id,
                    'source_module': 'sales_commission_users',
                })

        _logger.info(f"Calculated {len(commission_lines)} rule-based commissions for {sale_order.name}")
        return commission_lines

    def _calculate_commission_amount(self, sale_order, calculation_method, rate):
        """
        Calculate commission amount based on method and rate
        """
        if calculation_method == 'fixed':
            return rate

        elif calculation_method == 'percent_unit_price':
            if sale_order.order_line:
                unit_price = sum(line.price_unit * line.product_uom_qty for line in sale_order.order_line)
                return unit_price * (rate / 100.0)
            return 0.0

        elif calculation_method == 'percent_untaxed_total':
            return sale_order.amount_untaxed * (rate / 100.0)

        else:
            _logger.warning(f"Unknown calculation method: {calculation_method}")
            return 0.0

    def _get_base_amount(self, sale_order, calculation_method):
        """
        Get the base amount used for percentage calculations
        """
        if calculation_method == 'fixed':
            return 0.0
        elif calculation_method == 'percent_unit_price':
            if sale_order.order_line:
                return sum(line.price_unit * line.product_uom_qty for line in sale_order.order_line)
            return 0.0
        elif calculation_method == 'percent_untaxed_total':
            return sale_order.amount_untaxed
        else:
            return sale_order.amount_total

    @api.model
    def bulk_calculate_commissions(self, sale_order_ids):
        """
        Bulk calculate commissions for multiple sale orders
        Optimized for performance with large datasets
        """
        if not sale_order_ids:
            return []

        _logger.info(f"Starting bulk commission calculation for {len(sale_order_ids)} orders")

        sale_orders = self.env['sale.order'].browse(sale_order_ids)
        all_commission_data = []

        for order in sale_orders:
            try:
                commission_data = self.calculate_all_commissions(order)
                all_commission_data.extend(commission_data)
            except Exception as e:
                _logger.error(f"Failed to calculate commissions for order {order.name}: {str(e)}")
                # Continue with other orders even if one fails
                continue

        _logger.info(f"Bulk calculation completed: {len(all_commission_data)} commission lines")
        return all_commission_data

    def validate_commission_calculation(self, sale_order, commission_lines_data):
        """
        Validate commission calculations against business rules
        """
        if not commission_lines_data:
            return True

        total_commission = sum(line.get('commission_amount', 0) for line in commission_lines_data)

        # Check maximum commission percentage
        max_percentage = float(self.env['ir.config_parameter'].sudo().get_param(
            'commission.max_commission_percentage', '50.0'
        ))

        if sale_order.amount_total > 0:
            commission_percentage = (total_commission / sale_order.amount_total) * 100
            if commission_percentage > max_percentage:
                raise ValidationError(_(
                    "Total commission percentage (%.2f%%) exceeds maximum allowed (%.2f%%) for order %s"
                ) % (commission_percentage, max_percentage, sale_order.name))

        # Validate individual commission amounts
        for line_data in commission_lines_data:
            if line_data.get('commission_amount', 0) < 0:
                raise ValidationError(_(
                    "Negative commission amount detected for %s"
                ) % line_data.get('description', 'Unknown Commission'))

        return True

    def get_calculation_summary(self, sale_order):
        """
        Get a summary of what commissions would be calculated without creating them
        """
        commission_data = self.calculate_all_commissions(sale_order)

        summary = {
            'total_lines': len(commission_data),
            'total_amount': sum(line.get('commission_amount', 0) for line in commission_data),
            'by_type': {},
            'by_group': {},
        }

        for line in commission_data:
            commission_type = line.get('commission_type', 'unknown')
            amount = line.get('commission_amount', 0)

            # Group by commission type
            if commission_type not in summary['by_type']:
                summary['by_type'][commission_type] = {'count': 0, 'amount': 0}
            summary['by_type'][commission_type]['count'] += 1
            summary['by_type'][commission_type]['amount'] += amount

            # Group by commission group
            if commission_type.startswith('external_'):
                group = 'external'
            elif commission_type.startswith('internal_'):
                group = 'internal'
            elif commission_type.startswith('legacy_'):
                group = 'legacy'
            elif commission_type.startswith('rule_'):
                group = 'rule_based'
            else:
                group = 'other'

            if group not in summary['by_group']:
                summary['by_group'][group] = {'count': 0, 'amount': 0}
            summary['by_group'][group]['count'] += 1
            summary['by_group'][group]['amount'] += amount

        return summary