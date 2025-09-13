# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'
    
    # Add fields that will be transferred to payment
    remarks = fields.Text(
        string='Payment Remarks',
        help="Additional remarks that will be copied to the payment voucher"
    )
    
    qr_in_report = fields.Boolean(
        string='Include QR Code in Voucher',
        default=True,
        help="Whether to include QR code in payment voucher report"
    )
    
    def _create_payment_vals_from_wizard(self, batch_result):
        """Override to include additional fields and enforce workflow"""
        payment_vals = super()._create_payment_vals_from_wizard(batch_result)
        
        # Add our custom fields to payment values
        payment_vals.update({
            'remarks': self.remarks,
            'qr_in_report': self.qr_in_report,
            # ENFORCE WORKFLOW: All payments from invoices start at review stage
            'approval_state': 'under_review',
            'state': 'draft',  # Keep as draft until workflow completion
        })
        
        # Add workflow note to remarks
        workflow_note = "Payment created from invoice/bill - Enhanced workflow enforced"
        if payment_vals.get('remarks'):
            payment_vals['remarks'] = f"{payment_vals['remarks']} [{workflow_note}]"
        else:
            payment_vals['remarks'] = workflow_note
        
        return payment_vals
    
    def action_create_payments(self):
        """Override to create payments without posting them"""
        # Create payments using parent method with special context
        return super(AccountPaymentRegister, self.with_context(
            skip_immediate_posting=True,
            register_payment_wizard=True
        )).action_create_payments()
    
    def _post_payments(self, payments, edit_mode=False):
        """Override to prevent automatic posting"""
        # Don't post the payments - they should go through approval workflow
        # Just ensure they have the correct workflow state
        for payment in payments:
            if hasattr(payment, 'approval_state'):
                payment.write({
                    'approval_state': 'under_review',
                    'state': 'draft'
                })
        return payments
    
    def _create_payment_vals_from_batch(self, batch_result):
        """Alternative method name in some Odoo versions"""
        try:
            payment_vals = super()._create_payment_vals_from_batch(batch_result)
        except AttributeError:
            # Fallback for different method name
            payment_vals = super()._create_payment_vals_from_wizard(batch_result)
        
        # Add our custom fields to payment values and enforce workflow
        payment_vals.update({
            'remarks': self.remarks,
            'qr_in_report': self.qr_in_report,
            # ENFORCE WORKFLOW: All payments from invoices start at review stage
            'approval_state': 'under_review',
            'state': 'draft',  # Keep as draft until workflow completion
        })
        
        # Add workflow note to remarks
        workflow_note = "Payment created from invoice/bill - Enhanced workflow enforced"
        if payment_vals.get('remarks'):
            payment_vals['remarks'] = f"{payment_vals['remarks']} [{workflow_note}]"
        else:
            payment_vals['remarks'] = workflow_note
        
        return payment_vals