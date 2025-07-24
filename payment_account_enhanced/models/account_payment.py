# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def action_print_voucher(self):
        """Print payment voucher with custom format"""
        return self.env.ref('payment_account_enhanced.action_report_payment_voucher').report_action(self)

    @api.model
    def get_voucher_number(self):
        """Generate voucher number"""
        return self.env['ir.sequence'].next_by_code('payment.voucher') or _('New')

    def get_payment_type_label(self):
        """Get human-readable payment type"""
        if self.payment_type == 'outbound':
            return 'Payment'
        elif self.payment_type == 'inbound':
            return 'Receipt'
        return 'Payment'

    def get_amount_in_words(self):
        """Convert payment amount to words"""
        try:
            from num2words import num2words
            currency = self.currency_id.name or 'USD'
            return num2words(self.amount, to='currency', currency=currency).title()
        except ImportError:
            # Fallback if num2words is not available
            return f"{self.currency_id.symbol or ''} {self.amount:,.2f}"

    def get_formatted_amount(self):
        """Get formatted amount with currency"""
        return f"{self.currency_id.symbol or ''} {self.amount:,.2f}"
