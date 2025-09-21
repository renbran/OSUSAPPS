# -*- coding: utf-8 -*-
#############################################################################
#
#    Unified Commission Management System
#
#    Copyright (C) 2025-TODAY Commission Unified Team
#
#############################################################################

import logging
from datetime import datetime
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class CommissionLines(models.Model):
    """Unified Commission Lines Model - Combines all commission types"""
    _name = "commission.lines"
    _description = "Unified Commission Lines"
    _order = "date desc, sequence, commission_type"
    _rec_name = "display_name"

    # Core Fields
    name = fields.Char(string="Reference", default=lambda self: _('New'), copy=False, readonly=True)
    sequence = fields.Integer(string="Sequence", default=10, help="Sequence for ordering")
    display_name = fields.Char(string="Display Name", compute="_compute_display_name", store=True)

    # Relationships
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', required=True, ondelete='cascade')
    partner_id = fields.Many2one('res.partner', string='Commission Partner', required=True)
    sales_person_id = fields.Many2one('res.users', string='Sales Person',
                                      default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  related='sale_order_id.currency_id', store=True)

    # Commission Classification
    commission_type = fields.Selection([
        # External Commissions (from commission_ax)
        ('external_broker', 'External - Broker'),
        ('external_referrer', 'External - Referrer'),
        ('external_cashback', 'External - Cashback'),
        ('external_other', 'External - Other'),

        # Internal Commissions (from commission_ax)
        ('internal_agent1', 'Internal - Agent 1'),
        ('internal_agent2', 'Internal - Agent 2'),
        ('internal_manager', 'Internal - Manager'),
        ('internal_director', 'Internal - Director'),

        # Legacy Commissions (from commission_ax - backward compatibility)
        ('legacy_consultant', 'Legacy - Consultant'),
        ('legacy_manager', 'Legacy - Manager'),
        ('legacy_second_agent', 'Legacy - Second Agent'),
        ('legacy_director', 'Legacy - Director'),

        # Rule-based Commissions (from sales_commission_users)
        ('rule_standard', 'Rule - Standard'),
        ('rule_partner', 'Rule - Partner Based'),
        ('rule_product', 'Rule - Product Based'),
        ('rule_discount', 'Rule - Discount Based'),
    ], string="Commission Type", required=True)

    commission_group = fields.Selection([
        ('external', 'External'),
        ('internal', 'Internal'),
        ('legacy', 'Legacy'),
        ('rule_based', 'Rule Based'),
    ], string="Commission Group", compute="_compute_commission_group", store=True)

    # Calculation Method
    calculation_method = fields.Selection([
        ('fixed', 'Fixed Amount'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total'),
        ('rule_based', 'Rule Based Calculation'),
    ], string="Calculation Method", required=True)

    # Amount Fields
    base_amount = fields.Monetary(string="Base Amount", currency_field='currency_id',
                                  help="Amount used for percentage calculations")
    commission_rate = fields.Float(string="Rate (%)", digits=(16, 4),
                                   help="Commission rate in percentage or fixed amount")
    commission_amount = fields.Monetary(string="Commission Amount", currency_field='currency_id',
                                        help="Final calculated commission amount")

    # Dates
    date = fields.Date(string="Date", default=fields.Date.today, required=True)
    date_calculated = fields.Datetime(string="Calculated Date", readonly=True)
    date_approved = fields.Datetime(string="Approved Date", readonly=True)
    date_paid = fields.Datetime(string="Paid Date", readonly=True)

    # Status and Workflow
    status = fields.Selection([
        ('draft', 'Draft'),
        ('calculated', 'Calculated'),
        ('approved', 'Approved'),
        ('confirmed', 'Confirmed'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ], string="Status", default='draft', tracking=True)

    # Description and Notes
    description = fields.Char(string="Description", required=True)
    notes = fields.Text(string="Notes")

    # Payment Processing
    payment_method = fields.Selection([
        ('invoice', 'Customer Invoice'),
        ('purchase_order', 'Purchase Order'),
        ('journal_entry', 'Journal Entry'),
    ], string="Payment Method")

    invoice_id = fields.Many2one('account.move', string='Generated Invoice', readonly=True)
    purchase_order_id = fields.Many2one('purchase.order', string='Generated Purchase Order', readonly=True)
    journal_entry_id = fields.Many2one('account.move', string='Generated Journal Entry', readonly=True)

    # Source Tracking (for migration)
    source_module = fields.Char(string="Source Module", help="Original module this data came from")
    original_record_id = fields.Integer(string="Original Record ID", help="ID in original module")
    migrated_date = fields.Datetime(string="Migration Date")

    # Rule-based specific fields (from sales_commission_users)
    commission_rule_id = fields.Many2one('commission.rules', string='Commission Rule')
    product_id = fields.Many2one('product.product', string='Product')

    # Workflow fields
    approved_by = fields.Many2one('res.users', string='Approved By', readonly=True)
    confirmed_by = fields.Many2one('res.users', string='Confirmed By', readonly=True)

    # Computed fields for reporting
    is_external = fields.Boolean(string="Is External", compute="_compute_commission_flags", store=True)
    is_internal = fields.Boolean(string="Is Internal", compute="_compute_commission_flags", store=True)
    is_legacy = fields.Boolean(string="Is Legacy", compute="_compute_commission_flags", store=True)
    is_rule_based = fields.Boolean(string="Is Rule Based", compute="_compute_commission_flags", store=True)

    @api.model
    def create(self, vals):
        """Override create to set sequence number"""
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('commission.lines.unified') or _('New')
        return super(CommissionLines, self).create(vals)

    @api.depends('name', 'commission_type', 'partner_id', 'commission_amount')
    def _compute_display_name(self):
        """Compute display name for commission lines"""
        for line in self:
            if line.partner_id and line.commission_amount:
                line.display_name = f"{line.name} - {line.partner_id.name} - {line.commission_amount:,.2f}"
            else:
                line.display_name = line.name or _('New Commission')

    @api.depends('commission_type')
    def _compute_commission_group(self):
        """Compute commission group based on commission type"""
        for line in self:
            if line.commission_type.startswith('external_'):
                line.commission_group = 'external'
            elif line.commission_type.startswith('internal_'):
                line.commission_group = 'internal'
            elif line.commission_type.startswith('legacy_'):
                line.commission_group = 'legacy'
            elif line.commission_type.startswith('rule_'):
                line.commission_group = 'rule_based'
            else:
                line.commission_group = False

    @api.depends('commission_group')
    def _compute_commission_flags(self):
        """Compute boolean flags for different commission types"""
        for line in self:
            line.is_external = line.commission_group == 'external'
            line.is_internal = line.commission_group == 'internal'
            line.is_legacy = line.commission_group == 'legacy'
            line.is_rule_based = line.commission_group == 'rule_based'

    @api.constrains('commission_rate')
    def _check_commission_rate(self):
        """Validate commission rate"""
        for line in self:
            if line.calculation_method in ['percent_unit_price', 'percent_untaxed_total']:
                if line.commission_rate < 0 or line.commission_rate > 100:
                    raise ValidationError(_("Commission rate must be between 0 and 100 percent"))
            elif line.calculation_method == 'fixed':
                if line.commission_rate < 0:
                    raise ValidationError(_("Fixed commission amount cannot be negative"))

    @api.constrains('commission_amount')
    def _check_commission_amount(self):
        """Validate commission amount"""
        for line in self:
            if line.commission_amount < 0:
                raise ValidationError(_("Commission amount cannot be negative"))

    @api.onchange('commission_type')
    def _onchange_commission_type(self):
        """Update fields when commission type changes"""
        if self.commission_type:
            # Set default calculation method based on commission type
            if self.commission_type.startswith('rule_'):
                self.calculation_method = 'rule_based'
            elif self.commission_type.startswith('legacy_'):
                self.calculation_method = 'percent_untaxed_total'
            else:
                self.calculation_method = 'percent_unit_price'

            # Set default description
            type_descriptions = {
                'external_broker': 'Broker Commission',
                'external_referrer': 'Referrer Commission',
                'external_cashback': 'Cashback Commission',
                'external_other': 'Other External Commission',
                'internal_agent1': 'Agent 1 Commission',
                'internal_agent2': 'Agent 2 Commission',
                'internal_manager': 'Manager Commission',
                'internal_director': 'Director Commission',
                'legacy_consultant': 'Consultant Commission (Legacy)',
                'legacy_manager': 'Manager Commission (Legacy)',
                'legacy_second_agent': 'Second Agent Commission (Legacy)',
                'legacy_director': 'Director Commission (Legacy)',
                'rule_standard': 'Standard Commission',
                'rule_partner': 'Partner-based Commission',
                'rule_product': 'Product-based Commission',
                'rule_discount': 'Discount-based Commission',
            }
            self.description = type_descriptions.get(self.commission_type, 'Commission')

    def action_calculate(self):
        """Calculate commission amount"""
        for line in self:
            if line.status != 'draft':
                raise UserError(_("Can only calculate draft commission lines"))

            line._calculate_commission_amount()
            line.status = 'calculated'
            line.date_calculated = fields.Datetime.now()

            _logger.info(f"Commission calculated: {line.name} - Amount: {line.commission_amount}")

    def action_approve(self):
        """Approve commission"""
        for line in self:
            if line.status != 'calculated':
                raise UserError(_("Can only approve calculated commission lines"))

            line.status = 'approved'
            line.date_approved = fields.Datetime.now()
            line.approved_by = self.env.user

            _logger.info(f"Commission approved: {line.name} by {self.env.user.name}")

    def action_confirm(self):
        """Confirm commission"""
        for line in self:
            if line.status != 'approved':
                raise UserError(_("Can only confirm approved commission lines"))

            line.status = 'confirmed'
            line.confirmed_by = self.env.user

            _logger.info(f"Commission confirmed: {line.name} by {self.env.user.name}")

    def action_process_payment(self):
        """Process commission payment"""
        for line in self:
            if line.status not in ['confirmed', 'approved']:
                raise UserError(_("Can only process payment for confirmed or approved commissions"))

            payment_processor = self.env['commission.payment.processor']

            if line.payment_method == 'invoice':
                payment_processor._create_commission_invoice(line)
            elif line.payment_method == 'purchase_order':
                payment_processor._create_commission_purchase_order(line)
            elif line.payment_method == 'journal_entry':
                payment_processor._create_commission_journal_entry(line)
            else:
                # Use default payment method from configuration
                default_method = self.env['ir.config_parameter'].sudo().get_param(
                    'commission.default_payment_method', 'invoice'
                )
                if default_method == 'invoice':
                    payment_processor._create_commission_invoice(line)
                elif default_method == 'purchase_order':
                    payment_processor._create_commission_purchase_order(line)
                else:
                    payment_processor._create_commission_journal_entry(line)

            line.status = 'paid'
            line.date_paid = fields.Datetime.now()

    def action_cancel(self):
        """Cancel commission"""
        for line in self:
            if line.status == 'paid':
                raise UserError(_("Cannot cancel paid commissions"))

            line.status = 'cancelled'
            _logger.info(f"Commission cancelled: {line.name}")

    def action_reset_to_draft(self):
        """Reset commission to draft"""
        for line in self:
            if line.status == 'paid':
                raise UserError(_("Cannot reset paid commissions to draft"))

            line.status = 'draft'
            line.date_calculated = False
            line.date_approved = False
            line.approved_by = False
            line.confirmed_by = False

    def _calculate_commission_amount(self):
        """Calculate commission amount based on method and rate"""
        self.ensure_one()

        if self.calculation_method == 'fixed':
            self.commission_amount = self.commission_rate

        elif self.calculation_method == 'percent_unit_price':
            if self.sale_order_id.order_line:
                unit_price = sum(line.price_unit * line.product_uom_qty for line in self.sale_order_id.order_line)
                self.commission_amount = unit_price * (self.commission_rate / 100.0)
                self.base_amount = unit_price
            else:
                self.commission_amount = 0.0

        elif self.calculation_method == 'percent_untaxed_total':
            self.commission_amount = self.sale_order_id.amount_untaxed * (self.commission_rate / 100.0)
            self.base_amount = self.sale_order_id.amount_untaxed

        elif self.calculation_method == 'rule_based':
            # Use commission rules engine
            if self.commission_rule_id:
                calculator = self.env['commission.calculator']
                self.commission_amount = calculator._calculate_rule_based_commission(
                    self.sale_order_id, self.commission_rule_id
                )
            else:
                self.commission_amount = 0.0

    def name_get(self):
        """Custom name display"""
        result = []
        for line in self:
            name = f"{line.name} - {line.partner_id.name if line.partner_id else 'No Partner'}"
            if line.commission_amount:
                name += f" ({line.commission_amount:,.2f} {line.currency_id.symbol if line.currency_id else ''})"
            result.append((line.id, name))
        return result

    def unlink(self):
        """Override unlink to prevent deletion of processed commissions"""
        if any(line.status in ['confirmed', 'paid'] for line in self):
            raise UserError(_("Cannot delete confirmed or paid commission lines"))
        return super(CommissionLines, self).unlink()

    @api.model
    def get_commission_summary(self, domain=None):
        """Get commission summary for dashboard/reporting"""
        if domain is None:
            domain = []

        lines = self.search(domain)

        summary = {
            'total_commissions': sum(lines.mapped('commission_amount')),
            'total_lines': len(lines),
            'by_type': {},
            'by_status': {},
            'by_group': {},
        }

        # Group by commission type
        for commission_type in lines.mapped('commission_type'):
            type_lines = lines.filtered(lambda l: l.commission_type == commission_type)
            summary['by_type'][commission_type] = {
                'count': len(type_lines),
                'amount': sum(type_lines.mapped('commission_amount'))
            }

        # Group by status
        for status in lines.mapped('status'):
            status_lines = lines.filtered(lambda l: l.status == status)
            summary['by_status'][status] = {
                'count': len(status_lines),
                'amount': sum(status_lines.mapped('commission_amount'))
            }

        # Group by commission group
        for group in lines.mapped('commission_group'):
            group_lines = lines.filtered(lambda l: l.commission_group == group)
            summary['by_group'][group] = {
                'count': len(group_lines),
                'amount': sum(group_lines.mapped('commission_amount'))
            }

        return summary