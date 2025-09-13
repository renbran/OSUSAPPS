# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    # ============================================================================
    # ESSENTIAL WORKFLOW FIELDS
    # ============================================================================

    # Enhanced 4-Stage Approval Workflow State
    approval_state = fields.Selection([
        ('draft', 'Draft'),
        ('under_review', 'Under Review'),
        ('for_approval', 'For Approval'),
        ('for_authorization', 'For Authorization'),
        ('approved', 'Approved'),
        ('posted', 'Posted'),
        ('cancelled', 'Cancelled')
    ], string='Approval State', default='draft', tracking=True, copy=False, index=True,
       help="Current approval state of the payment voucher")

    # Voucher number with automatic generation
    voucher_number = fields.Char(
        string='Voucher Number',
        copy=False,
        readonly=True,
        index=True,
        help="Unique voucher number generated automatically"
    )

    # Enhanced fields for workflow tracking
    remarks = fields.Text(
        string='Remarks/Memo',
        help="Additional remarks or memo for this payment voucher"
    )

    # ============================================================================
    # APPROVAL WORKFLOW TRACKING FIELDS
    # ============================================================================

    reviewer_id = fields.Many2one(
        'res.users',
        string='Reviewed By',
        copy=False,
        help="User who reviewed the payment (Stage 1)"
    )

    reviewer_date = fields.Datetime(
        string='Review Date',
        copy=False,
        help="Date when the payment was reviewed"
    )

    approver_id = fields.Many2one(
        'res.users',
        string='Approved By',
        copy=False,
        help="User who approved the payment (Stage 2)"
    )

    approver_date = fields.Datetime(
        string='Approval Date',
        copy=False,
        help="Date when the payment was approved"
    )

    authorizer_id = fields.Many2one(
        'res.users',
        string='Authorized By',
        copy=False,
        help="User who authorized the payment (Stage 3)"
    )

    authorizer_date = fields.Datetime(
        string='Authorization Date',
        copy=False,
        help="Date when the payment was authorized"
    )

    # ============================================================================
    # WORKFLOW METHODS
    # ============================================================================

    @api.model
    def create(self, vals):
        """Enhanced create method with voucher number generation"""
        # Generate voucher number immediately
        if not vals.get('voucher_number'):
            payment_type = vals.get('payment_type', 'outbound')
            sequence_code = 'receipt.voucher' if payment_type == 'inbound' else 'payment.voucher'
            vals['voucher_number'] = self.env['ir.sequence'].next_by_code(sequence_code) or 'PAY/DRAFT'
        
        # Set initial approval state
        if not vals.get('approval_state'):
            vals['approval_state'] = 'draft'
            
        return super(AccountPayment, self).create(vals)

    def action_submit_for_review(self):
        """Submit payment for review (Stage 1)"""
        for record in self:
            if record.approval_state != 'draft':
                raise UserError(_("Only draft payments can be submitted for review."))
            
            record.write({
                'approval_state': 'under_review',
            })
            
            # Log message
            record.message_post(
                body=_("Payment submitted for review by %s") % self.env.user.name,
                subtype_xmlid='mail.mt_note'
            )

    def action_review_payment(self):
        """Review payment (Stage 2)"""
        for record in self:
            if record.approval_state != 'under_review':
                raise UserError(_("Only payments under review can be reviewed."))
            
            record.write({
                'approval_state': 'for_approval',
                'reviewer_id': self.env.user.id,
                'reviewer_date': fields.Datetime.now(),
            })
            
            # Log message
            record.message_post(
                body=_("Payment reviewed by %s") % self.env.user.name,
                subtype_xmlid='mail.mt_note'
            )

    def action_approve_payment(self):
        """Approve payment (Stage 3)"""
        for record in self:
            if record.approval_state != 'for_approval':
                raise UserError(_("Only payments for approval can be approved."))
            
            record.write({
                'approval_state': 'for_authorization',
                'approver_id': self.env.user.id,
                'approver_date': fields.Datetime.now(),
            })
            
            # Log message
            record.message_post(
                body=_("Payment approved by %s") % self.env.user.name,
                subtype_xmlid='mail.mt_note'
            )

    def action_authorize_payment(self):
        """Authorize payment (Final Stage)"""
        for record in self:
            if record.approval_state != 'for_authorization':
                raise UserError(_("Only payments for authorization can be authorized."))
            
            record.write({
                'approval_state': 'approved',
                'authorizer_id': self.env.user.id,
                'authorizer_date': fields.Datetime.now(),
            })
            
            # Log message
            record.message_post(
                body=_("Payment authorized by %s") % self.env.user.name,
                subtype_xmlid='mail.mt_note'
            )

    def action_reject_payment(self):
        """Reject payment at any stage"""
        for record in self:
            if record.approval_state not in ['under_review', 'for_approval', 'for_authorization']:
                raise UserError(_("Only payments in workflow can be rejected."))
            
            record.write({
                'approval_state': 'draft',
            })
            
            # Log message
            record.message_post(
                body=_("Payment rejected by %s") % self.env.user.name,
                subtype_xmlid='mail.mt_note'
            )

    def action_post(self):
        """Override action_post to enforce workflow"""
        for record in self:
            # Check if payment is approved before posting
            if hasattr(record, 'approval_state') and record.approval_state != 'approved':
                raise UserError(_(
                    "Payment cannot be posted without completing the approval workflow.\n"
                    "Current state: %s\n"
                    "Required state: approved\n"
                    "Please complete the review → approve → authorize workflow steps."
                ) % record.approval_state.replace('_', ' ').title())
        
        # Call original post method
        result = super(AccountPayment, self).action_post()
        
        # Update approval state to posted
        for record in self:
            if hasattr(record, 'approval_state'):
                record.approval_state = 'posted'
        
        return result

    # ============================================================================
    # PRINT METHODS (Placeholder)
    # ============================================================================

    def action_print_osus_voucher(self):
        """Print OSUS payment voucher"""
        return {
            'type': 'ir.actions.report',
            'report_name': 'payment_account_enhanced.payment_voucher_report',
            'report_type': 'qweb-pdf',
        }