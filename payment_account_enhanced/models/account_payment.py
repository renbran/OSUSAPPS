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
            
        # Create the payment record
        payment = super(AccountPayment, self).create(vals)
        
        # Force QR code generation immediately after creation
        try:
            payment._compute_qr_code()
        except Exception as e:
            _logger.warning("Could not generate QR code immediately for payment %s: %s", payment.voucher_number, str(e))
            
        return payment

    def write(self, vals):
        """Override write to ensure access tokens and QR codes are generated"""
        result = super(AccountPayment, self).write(vals)
        
        # Generate access token if missing and force QR regeneration
        for record in self:
            needs_qr_update = False
            
            if not record.access_token:
                record.access_token = record._generate_access_token()
                needs_qr_update = True
            
            # Force QR regeneration if certain fields changed or QR is missing
            if not record.qr_code or needs_qr_update or any(field in vals for field in ['voucher_number', 'name', 'approval_state']):
                try:
                    record._compute_qr_code()
                except Exception as e:
                    _logger.warning("Could not update QR code for payment %s: %s", record.voucher_number or record.name, str(e))
        
        return result

    def _generate_access_token(self):
        """Generate secure access token for QR code validation"""
        # Create unique token based on current time, random UUID, and some payment data
        token_data = f"{uuid.uuid4().hex}-{fields.Datetime.now().isoformat()}"
        return hashlib.sha256(token_data.encode()).hexdigest()[:32]

    def _get_dynamic_base_url(self):
        """Get dynamic base URL from current request or fallback to system parameter"""
        try:
            # Try to get base URL from current HTTP request context
            from odoo.http import request
            if request and hasattr(request, 'httprequest') and request.httprequest:
                # Build dynamic URL from current request
                scheme = request.httprequest.scheme or 'http'
                host = request.httprequest.host
                if host:
                    # Handle port if not standard
                    if ':' not in host:
                        # Add default ports if needed
                        if scheme == 'https' and request.httprequest.environ.get('SERVER_PORT') != '443':
                            port = request.httprequest.environ.get('SERVER_PORT')
                            if port and port != '80':
                                host = f"{host}:{port}"
                        elif scheme == 'http' and request.httprequest.environ.get('SERVER_PORT') not in ['80', '443']:
                            port = request.httprequest.environ.get('SERVER_PORT')
                            if port and port != '443':
                                host = f"{host}:{port}"
                    
                    dynamic_url = f"{scheme}://{host}"
                    _logger.debug("Generated dynamic base URL from request: %s", dynamic_url)
                    return dynamic_url
        except Exception as e:
            _logger.debug("Could not get dynamic base URL from request context: %s", str(e))
        
        # Fallback to system parameter
        fallback_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url', 
            default='http://localhost:8069'
        )
        _logger.debug("Using fallback base URL: %s", fallback_url)
        return fallback_url

    @api.depends('voucher_number', 'amount', 'approval_state', 'partner_id', 'date', 'access_token', 'name')
    def _compute_qr_code(self):
        """Generate QR code for payment voucher verification with access token"""
        for record in self:
            # Generate QR if we have either voucher_number or name, and access_token
            payment_ref = record.voucher_number or record.name
            if payment_ref and record.id and record.access_token:
                try:
                    # Get company QR settings
                    company = record.company_id
                    
                    # Get dynamic base URL from current request or fallback to system parameter
                    base_url = self._get_dynamic_base_url()
                    
                    # Create verification URL for QR code (simple URL, not JSON)
                    verification_url = f"{base_url}/payment/verify/{record.access_token}"
                    
                    # Use custom verification URL if configured
                    if company.qr_code_verification_url:
                        verification_url = f"{company.qr_code_verification_url}/{record.access_token}"
                    
                    # Generate QR code with verification URL (always generate)
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_M,
                        box_size=10,
                        border=4,
                    )
                    qr.add_data(verification_url)
                    qr.make(fit=True)
                    
                    # Create image
                    qr_img = qr.make_image(fill_color="black", back_color="white")
                    buffer = BytesIO()
                    qr_img.save(buffer, format='PNG')
                    record.qr_code = base64.b64encode(buffer.getvalue())
                        
                except Exception as e:
                    _logger.error("Error generating QR code for payment %s: %s", payment_ref, str(e))
                    record.qr_code = False
            else:
                record.qr_code = False

    def action_regenerate_qr_code(self):
        """Force regenerate QR code for this payment"""
        self.ensure_one()
        if not self.access_token:
            self.access_token = self._generate_access_token()
        self._compute_qr_code()
        return True

    @api.model
    def generate_missing_qr_codes(self):
        """Generate QR codes for all payments missing them"""
        payments_without_qr = self.search([
            ('qr_code', '=', False),
            ('voucher_number', '!=', False),
            ('voucher_number', '!=', '')
        ])
        
        count = 0
        for payment in payments_without_qr:
            try:
                if not payment.access_token:
                    payment.access_token = payment._generate_access_token()
                payment._compute_qr_code()
                count += 1
            except Exception as e:
                _logger.error("Failed to generate QR for payment %s: %s", payment.voucher_number, str(e))
        
        return count

    @api.model
    def regenerate_all_qr_codes_with_dynamic_url(self):
        """Regenerate all QR codes with dynamic URL logic - useful after URL changes"""
        payments_with_tokens = self.search([
            ('access_token', '!=', False),
            ('access_token', '!=', '')
        ])
        
        count = 0
        errors = 0
        
        for payment in payments_with_tokens:
            try:
                # Force regenerate QR code with new dynamic URL logic
                payment._compute_qr_code()
                count += 1
                _logger.info("Regenerated QR code for payment %s with dynamic URL", payment.voucher_number or payment.name)
            except Exception as e:
                errors += 1
                _logger.error("Failed to regenerate QR for payment %s: %s", payment.voucher_number or payment.name, str(e))
        
        return {
            'regenerated': count,
            'errors': errors,
            'message': f"Regenerated {count} QR codes, {errors} errors"
        }

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