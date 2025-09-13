# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'
    
    def _create_payment_vals_from_wizard(self, batch_result):
        """Override to ensure payments start in workflow"""
        payment_vals = super()._create_payment_vals_from_wizard(batch_result)
        
        # ENFORCE WORKFLOW: All payments start in draft state for approval workflow
        payment_vals.update({
            'approval_state': 'draft',  # Start in draft for workflow
        })
        
        return payment_vals

    def _post_payments(self, to_process, edit_mode=False):
        """Override to prevent immediate posting - enforce workflow"""
        # Skip posting - let workflow handle it
        return to_process