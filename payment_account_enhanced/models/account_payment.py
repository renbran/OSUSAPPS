# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging
import qrcode
import base64
import json
import uuid
import hashlib
from io import BytesIO

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

    # Approval History relationship
    approval_history_ids = fields.One2many(
        'payment.approval.history',
        'payment_id',
        string='Approval History',
        help="Complete approval workflow history"
    )

    # ============================================================================
    # QR CODE AND ACCESS TOKEN FIELDS
    # ============================================================================

    # QR Code for payment verification
    qr_code = fields.Binary(
        string='Payment QR Code',
        compute='_compute_qr_code',
        store=True,
        help="QR code for payment voucher verification with access token"
    )

    # Secure access token for QR validation
    access_token = fields.Char(
        string='Access Token',
        copy=False,
        index=True,
        help="Secure token for QR code validation and public access"
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
        
        # Generate access token for QR verification
        if not vals.get('access_token'):
            vals['access_token'] = self._generate_access_token()
            
        return super(AccountPayment, self).create(vals)

    def _generate_access_token(self):
        """Generate secure access token for QR code validation"""
        # Create unique token based on current time, random UUID, and some payment data
        token_data = f"{uuid.uuid4().hex}-{fields.Datetime.now().isoformat()}"
        return hashlib.sha256(token_data.encode()).hexdigest()[:32]

    @api.depends('voucher_number', 'amount', 'approval_state', 'partner_id', 'payment_date', 'access_token')
    def _compute_qr_code(self):
        """Generate QR code for payment voucher verification with access token"""
        for record in self:
            if record.voucher_number and record.id and record.access_token:
                try:
                    # Get company QR settings
                    company = record.company_id
                    base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', default='')
                    
                    # Create comprehensive verification data with access token
                    qr_data = {
                        'type': 'payment_verification',
                        'voucher_number': record.voucher_number,
                        'amount': str(record.amount),
                        'currency': record.currency_id.name,
                        'partner': record.partner_id.name if record.partner_id else '',
                        'date': str(record.payment_date) if record.payment_date else '',
                        'approval_state': record.approval_state,
                        'company': record.company_id.name,
                        'payment_type': record.payment_type,
                        'access_token': record.access_token,
                        'verification_url': f"{base_url}/payment/verify/{record.access_token}" if base_url else '',
                        'payment_id': record.id,
                        'generated_at': fields.Datetime.now().isoformat(),
                    }
                    
                    # Use custom verification URL if configured
                    if company.qr_code_verification_url:
                        qr_data['verification_url'] = f"{company.qr_code_verification_url}/{record.access_token}"
                    
                    # Convert to JSON for QR code
                    qr_text = json.dumps(qr_data, ensure_ascii=False)
                    
                    # Generate QR code only if QR codes are enabled
                    if company.enable_qr_codes:
                        qr = qrcode.QRCode(
                            version=1,
                            error_correction=qrcode.constants.ERROR_CORRECT_L,
                            box_size=10,
                            border=4,
                        )
                        qr.add_data(qr_text)
                        qr.make(fit=True)
                        
                        # Create image
                        qr_img = qr.make_image(fill_color="black", back_color="white")
                        buffer = BytesIO()
                        qr_img.save(buffer, format='PNG')
                        record.qr_code = base64.b64encode(buffer.getvalue())
                    else:
                        record.qr_code = False
                        
                except Exception as e:
                    _logger.error("Error generating QR code for payment %s: %s", record.voucher_number, str(e))
                    record.qr_code = False
            else:
                record.qr_code = False

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
    # ENHANCED METHODS
    # ============================================================================

    def action_print_payment_voucher(self):
        """Print payment voucher - simplified without report file"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Payment Voucher',
            'res_model': 'account.payment',
            'res_id': self.id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
        }