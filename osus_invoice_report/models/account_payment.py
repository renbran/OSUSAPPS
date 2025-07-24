# -*- coding: utf-8 -*-

from odoo import models, fields, api
from num2words import num2words


class PaymentReportExtension(models.Model):
    _inherit = 'account.payment'
    
    def _get_amount_in_words(self):
        """Convert the amount to words"""
        self.ensure_one()
        try:
            amount_in_words = num2words(abs(self.amount), lang=self.partner_id.lang or 'en')
            currency_name = self.currency_id.name or 'AED'
            return amount_in_words.title() + ' ' + currency_name
        except NotImplementedError:
            return "Amount in words not available"
        
    def get_report_type_name(self):
        """Return the type of payment voucher"""
        self.ensure_one()
        if self.payment_type == 'inbound':
            return "Receipt Voucher"
        else:
            return "Payment Voucher"
