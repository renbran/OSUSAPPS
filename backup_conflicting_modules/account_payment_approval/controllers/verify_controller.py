# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.tools.safe_eval import safe_eval
from odoo.addons.web.controllers.main import Home

class PaymentVerifyController(http.Controller):
    @http.route(['/verify/<int:payment_id>/<string:token>'], type='http', auth='public', csrf=False)
    def verify_payment(self, payment_id, token, **kw):
        payment = request.env['account.payment'].sudo().browse(payment_id)
        valid = payment and payment.qr_token == token
        return request.render('account_payment_approval.verify_payment_template', {
            'payment': payment,
            'valid': valid,
        })
