# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, date
import logging

_logger = logging.getLogger(__name__)


class CommissionPaymentWizard(models.TransientModel):
    """
    Wizard for processing commission payments in batch
    """
    _name = 'commission.payment.wizard'
    _description = 'Commission Payment Wizard'

    # Payment details
    payment_date = fields.Date(
        string='Payment Date',
        required=True,
        default=fields.Date.today
    )
    journal_id = fields.Many2one(
        'account.journal',
        string='Payment Journal',
        required=True,
        domain=[('type', 'in', ['bank', 'cash'])]
    )
    payment_method = fields.Selection([
        ('manual', 'Manual Payment'),
        ('bank_transfer', 'Bank Transfer'),
        ('check', 'Check'),
        ('cash', 'Cash')
    ], string='Payment Method', required=True, default='bank_transfer')

    # Selection criteria
    partner_ids = fields.Many2many(
        'res.partner',
        string='Partners',
        domain=[('is_commission_partner', '=', True)],
        help="Leave empty to process for all partners"
    )
    commission_period_id = fields.Many2one(
        'commission.period',
        string='Commission Period',
        help="Leave empty to process all processed allocations"
    )
    commission_rule_ids = fields.Many2many(
        'commission.rule',
        string='Commission Rules',
        help="Leave empty to process all rules"
    )

    # Filters
    min_amount = fields.Monetary(
        string='Minimum Amount',
        currency_field='currency_id',
        help="Only process allocations above this amount"
    )
    max_amount = fields.Monetary(
        string='Maximum Amount',
        currency_field='currency_id',
        help="Only process allocations below this amount"
    )
    group_by_partner = fields.Boolean(
        string='Group by Partner',
        default=True,
        help="Create one payment per partner instead of per allocation"
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id
    )

    # Summary
    allocation_count = fields.Integer(
        string='Allocations to Pay',
        readonly=True
    )
    total_amount = fields.Monetary(
        string='Total Amount',
        readonly=True,
        currency_field='currency_id'
    )
    partner_count = fields.Integer(
        string='Partners',
        readonly=True
    )

    @api.onchange('partner_ids', 'commission_period_id', 'commission_rule_ids', 'min_amount', 'max_amount')
    def _onchange_payment_params(self):
        """Update payment preview when parameters change"""
        self._calculate_payment_summary()

    def _calculate_payment_summary(self):
        """Calculate payment summary"""
        try:
            domain = [('state', '=', 'processed')]
            
            # Apply filters
            if self.partner_ids:
                domain.append(('partner_id', 'in', self.partner_ids.ids))
            if self.commission_period_id:
                domain.append(('commission_period_id', '=', self.commission_period_id.id))
            if self.commission_rule_ids:
                domain.append(('commission_rule_id', 'in', self.commission_rule_ids.ids))
            if self.min_amount:
                domain.append(('commission_amount', '>=', self.min_amount))
            if self.max_amount:
                domain.append(('commission_amount', '<=', self.max_amount))

            allocations = self.env['commission.allocation'].search(domain)
            
            self.allocation_count = len(allocations)
            self.total_amount = sum(allocations.mapped('commission_amount'))
            self.partner_count = len(allocations.mapped('partner_id'))

        except Exception as e:
            _logger.warning("Error calculating payment summary: %s", str(e))
            self.allocation_count = 0
            self.total_amount = 0.0
            self.partner_count = 0

    def action_process_payments(self):
        """Process commission payments"""
        self.ensure_one()
        
        if not self.journal_id:
            raise ValidationError(_("Payment journal is required"))

        try:
            # Get allocations to pay
            allocations = self._get_allocations_to_pay()
            
            if not allocations:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Commission Payment'),
                        'message': _('No allocations found for payment processing.'),
                        'type': 'warning'
                    }
                }

            # Process payments
            if self.group_by_partner:
                payments = self._create_grouped_payments(allocations)
            else:
                payments = self._create_individual_payments(allocations)

            # Mark allocations as paid
            allocations.write({
                'state': 'paid',
                'payment_date': self.payment_date
            })

            # Update payment move references
            for allocation in allocations:
                if allocation.partner_id in payments:
                    allocation.payment_move_id = payments[allocation.partner_id].id

            return self._show_payment_results(payments, allocations)

        except Exception as e:
            _logger.error("Error processing payments: %s", str(e))
            raise ValidationError(_("Error processing payments: %s") % str(e))

    def _get_allocations_to_pay(self):
        """Get allocations ready for payment"""
        domain = [('state', '=', 'processed')]
        
        # Apply filters
        if self.partner_ids:
            domain.append(('partner_id', 'in', self.partner_ids.ids))
        if self.commission_period_id:
            domain.append(('commission_period_id', '=', self.commission_period_id.id))
        if self.commission_rule_ids:
            domain.append(('commission_rule_id', 'in', self.commission_rule_ids.ids))
        if self.min_amount:
            domain.append(('commission_amount', '>=', self.min_amount))
        if self.max_amount:
            domain.append(('commission_amount', '<=', self.max_amount))

        return self.env['commission.allocation'].search(domain)

    def _create_grouped_payments(self, allocations):
        """Create grouped payments by partner"""
        payments = {}
        partners_allocations = {}

        # Group allocations by partner
        for allocation in allocations:
            if allocation.partner_id not in partners_allocations:
                partners_allocations[allocation.partner_id] = self.env['commission.allocation']
            partners_allocations[allocation.partner_id] |= allocation

        # Create payment for each partner
        for partner, partner_allocations in partners_allocations.items():
            total_amount = sum(partner_allocations.mapped('commission_amount'))
            
            payment = self._create_payment_move(
                partner=partner,
                amount=total_amount,
                allocations=partner_allocations
            )
            payments[partner] = payment

        return payments

    def _create_individual_payments(self, allocations):
        """Create individual payments for each allocation"""
        payments = {}
        
        for allocation in allocations:
            payment = self._create_payment_move(
                partner=allocation.partner_id,
                amount=allocation.commission_amount,
                allocations=allocation
            )
            payments[allocation.partner_id] = payment

        return payments

    def _create_payment_move(self, partner, amount, allocations):
        """Create account move for payment"""
        # Get commission expense account
        commission_account = self.env['account.account'].search([
            ('code', 'like', '6%'),
            ('name', 'ilike', 'commission')
        ], limit=1)
        
        if not commission_account:
            commission_account = self.env['account.account'].search([
                ('code', 'like', '6%'),
                ('user_type_id.name', 'ilike', 'expense')
            ], limit=1)

        # Get partner payable account
        payable_account = partner.property_account_payable_id
        if not payable_account:
            payable_account = self.env['account.account'].search([
                ('user_type_id.name', 'ilike', 'payable')
            ], limit=1)

        # Prepare move lines
        line_vals = []
        
        # Commission expense line
        line_vals.append({
            'name': _('Commission Payment - %s') % partner.name,
            'account_id': commission_account.id,
            'partner_id': partner.id,
            'debit': amount,
            'credit': 0.0,
        })
        
        # Bank/Cash line
        line_vals.append({
            'name': _('Commission Payment - %s') % partner.name,
            'account_id': self.journal_id.default_account_id.id,
            'partner_id': partner.id,
            'debit': 0.0,
            'credit': amount,
        })

        # Create account move
        move_vals = {
            'journal_id': self.journal_id.id,
            'date': self.payment_date,
            'ref': _('Commission Payment - %s') % partner.name,
            'line_ids': [(0, 0, line) for line in line_vals],
        }

        move = self.env['account.move'].create(move_vals)
        move.action_post()
        
        return move

    def _show_payment_results(self, payments, allocations):
        """Show payment processing results"""
        payment_count = len(payments)
        allocation_count = len(allocations)
        total_amount = sum(allocations.mapped('commission_amount'))
        
        message = _("Commission payments processed:\n"
                   "- Payments created: %d\n"
                   "- Allocations paid: %d\n"
                   "- Total amount: %s") % (
                       payment_count, allocation_count, 
                       "{:,.2f} {}".format(total_amount, self.currency_id.name)
                   )

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Commission Payments'),
                'message': message,
                'type': 'success'
            }
        }

    def action_preview_payments(self):
        """Preview payments without processing"""
        self._calculate_payment_summary()
        return {'type': 'ir.actions.act_window_close'}