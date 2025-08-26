from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError, ValidationError
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
import qrcode
import base64
from io import BytesIO
from PIL import Image, ImageDraw
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    # ============================================================================
    # FIELDS
    # ============================================================================

    # Enhanced approval workflow for invoices and bills
    approval_state = fields.Selection([
        ('draft', 'Draft'),
        ('under_review', 'Under Review'),
        ('for_approval', 'For Approval'),
        ('approved', 'Approved'),
        ('posted', 'Posted'),
        ('cancelled', 'Cancelled')
    ], string='Approval State', default='draft', tracking=True, copy=False,
       help="Current approval state of the invoice/bill")

    # Approval workflow fields
    reviewer_id = fields.Many2one(
        'res.users',
        string='Reviewed By',
        copy=False,
        help="User who reviewed the invoice/bill"
    )

    reviewer_date = fields.Datetime(
        string='Review Date',
        copy=False,
        help="Date when the invoice/bill was reviewed"
    )

    approver_id = fields.Many2one(
        'res.users',
        string='Approved By',
        copy=False,
        help="User who approved the invoice/bill"
    )

    approver_date = fields.Datetime(
        string='Approval Date',
        copy=False,
        help="Date when the invoice/bill was approved"
    )

    # ============================================================================
    # COMPUTED FIELDS FOR UI ENHANCEMENT
    # ============================================================================

    can_submit_for_review = fields.Boolean(
        string='Can Submit for Review',
        compute='_compute_workflow_buttons',
        help="Whether user can submit this document for review"
    )

    can_review = fields.Boolean(
        string='Can Review',
        compute='_compute_workflow_buttons',
        help="Whether user can review this document"
    )

    can_approve = fields.Boolean(
        string='Can Approve',
        compute='_compute_workflow_buttons',
        help="Whether user can approve this document"
    )

    can_post_manual = fields.Boolean(
        string='Can Post Manually',
        compute='_compute_workflow_buttons',
        help="Whether user can manually post this document"
    )

    @api.depends('approval_state', 'move_type', 'state')
    def _compute_workflow_buttons(self):
        """Compute button visibility and permissions"""
        for record in self:
            # Check if this is an invoice/bill
            is_invoice_bill = record.move_type in ['in_invoice', 'in_refund', 'out_invoice', 'out_refund']
            
            # Initialize all as False
            record.can_submit_for_review = False
            record.can_review = False
            record.can_approve = False
            record.can_post_manual = False
            
            if is_invoice_bill:
                # Can submit for review
                record.can_submit_for_review = (
                    record.approval_state == 'draft' and
                    record.state == 'draft'
                )
                
                # Can review
                record.can_review = (
                    record.approval_state == 'under_review' and
                    record._check_approval_permissions('review')
                )
                
                # Can approve
                record.can_approve = (
                    record.approval_state == 'for_approval' and
                    record._check_approval_permissions('approve')
                )
                
                # Can post manually
                record.can_post_manual = (
                    record.approval_state == 'approved' and
                    record.state == 'draft' and
                    record._check_posting_permissions()
                )

    @api.onchange('approval_state', 'move_type')
    def _onchange_approval_state(self):
        """Update UI when approval state changes"""
        if self.move_type in ['in_invoice', 'in_refund', 'out_invoice', 'out_refund']:
            # Trigger button recomputation
            self._compute_workflow_buttons()
            
            # Show helpful messages
            if self.approval_state == 'under_review':
                return {
                    'warning': {
                        'title': _('Under Review'),
                        'message': _('This invoice/bill is now under review. A reviewer will need to approve it before it can proceed.')
                    }
                }
            elif self.approval_state == 'approved':
                return {
                    'warning': {
                        'title': _('Approved'),
                        'message': _('This invoice/bill has been approved and is ready for posting.')
                    }
                }

    # ============================================================================
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
    # QR CODE GENERATION FOR INVOICE/BILL VERIFICATION
    # ============================================================================

    def generate_qr_code_invoice(self):
        """Generate QR code for invoice/bill verification"""
        try:
            # Create comprehensive verification data
            qr_data = {
                'type': 'invoice_verification',
                'number': self.name or '',
                'amount': str(self.amount_total),
                'currency': self.currency_id.name,
                'partner': self.partner_id.name,
                'date': str(self.invoice_date),
                'approval_state': self.approval_state,
                'company': self.company_id.name,
                'move_type': self.move_type,
                'reviewer': self.reviewer_id.name if self.reviewer_id else '',
                'approver': self.approver_id.name if self.approver_id else '',
                'verification_url': '%s/web#id=%s&model=account.move' % (
                    self.env['ir.config_parameter'].sudo().get_param('web.base.url', ''),
                    self.id
                )
            }
            
            # Convert to JSON string for QR code
            import json
            qr_text = json.dumps(qr_data, ensure_ascii=False)
            
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_text)
            qr.make(fit=True)
            
            # Create QR code image
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            # Add OSUS branding to QR code
            if hasattr(qr_img, 'size'):
                # Create a larger image with branding
                branded_size = (qr_img.size[0] + 40, qr_img.size[1] + 60)
                branded_img = Image.new('RGB', branded_size, 'white')
                
                # Paste QR code
                branded_img.paste(qr_img, (20, 20))
                
                # Add OSUS text
                draw = ImageDraw.Draw(branded_img)
                try:
                    # Use system font if available
                    font_size = 12
                    text = "OSUS VERIFIED"
                    text_bbox = draw.textbbox((0, 0), text)
                    text_width = text_bbox[2] - text_bbox[0]
                    text_x = (branded_size[0] - text_width) // 2
                    draw.text((text_x, branded_size[1] - 35), text, fill='black')
                    
                    # Add verification note
                    note = "Scan to verify"
                    note_bbox = draw.textbbox((0, 0), note)
                    note_width = note_bbox[2] - note_bbox[0]
                    note_x = (branded_size[0] - note_width) // 2
                    draw.text((note_x, branded_size[1] - 20), note, fill='gray')
                except Exception as e:
                    _logger.warning("Could not add text to QR code: %s", str(e))
                
                qr_img = branded_img
            
            # Convert to base64
            buffer = BytesIO()
            qr_img.save(buffer, format='PNG')
            qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            return qr_code_base64
            
        except Exception as e:
            _logger.error("Error generating QR code for invoice %s: %s", self.name, str(e))
            return False

    qr_code_invoice = fields.Text(
        string='Invoice QR Code',
        compute='_compute_qr_code_invoice',
        help="QR code for invoice/bill verification"
    )

    @api.depends('name', 'amount_total', 'approval_state', 'partner_id', 'invoice_date')
    def _compute_qr_code_invoice(self):
        """Compute QR code for invoice/bill"""
        for record in self:
            if record.move_type in ['in_invoice', 'in_refund', 'out_invoice', 'out_refund'] and record.name:
                record.qr_code_invoice = record.generate_qr_code_invoice()
            else:
                record.qr_code_invoice = False

    # ============================================================================
    # ENHANCED WORKFLOW CONSTRAINTS AND VALIDATION
    # ============================================================================
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
    # WORKFLOW METHODS
    # ============================================================================

    def action_submit_for_review(self):
        """Submit invoice/bill for review"""
        for record in self:
            if record.approval_state != 'draft':
                raise UserError(_("Only draft invoices/bills can be submitted for review."))
            
            if record.move_type not in ['in_invoice', 'in_refund', 'out_invoice', 'out_refund']:
                raise UserError(_("Only invoices and bills can use approval workflow."))
            
            record.approval_state = 'under_review'
            record._post_approval_message("submitted for review")
        
        return self._return_success_message(_('Invoice/Bill has been submitted for review.'))

    def action_review_approve(self):
        """Approve invoice/bill from review stage"""
        for record in self:
            if record.approval_state != 'under_review':
                raise UserError(_("Only invoices/bills under review can be approved."))
            
            # Check user permissions
            if not record._check_approval_permissions('review'):
                raise UserError(_("You do not have permission to review this invoice/bill."))
            
            record.reviewer_id = self.env.user
            record.reviewer_date = fields.Datetime.now()
            record.approval_state = 'for_approval'
            record._post_approval_message("reviewed and forwarded for approval")
        
        return self._return_success_message(_('Invoice/Bill has been reviewed and forwarded for approval.'))

    def action_final_approve(self):
        """Final approval and auto-post invoice/bill"""
        for record in self:
            if record.approval_state != 'for_approval':
                raise UserError(_("Only invoices/bills pending approval can be finally approved."))
            
            # Check user permissions
            if not record._check_approval_permissions('approve'):
                raise UserError(_("You do not have permission to approve this invoice/bill."))
            
            record.approver_id = self.env.user
            record.approver_date = fields.Datetime.now()
            record.approval_state = 'approved'
            record._post_approval_message("approved and ready for posting")
            
            # Auto-post the invoice/bill after approval
            try:
                record.action_post_invoice_bill()
                return self._return_success_message(_('Invoice/Bill has been approved and posted successfully.'))
            except Exception as e:
                # If auto-posting fails, keep it approved for manual posting
                _logger.warning(f"Auto-posting failed for invoice/bill {record.name}: {str(e)}")
                return self._return_success_message(_('Invoice/Bill has been approved. Please post manually due to technical issue.'))
        
        return self._return_success_message(_('Invoice/Bill has been approved and is ready for posting.'))

    def action_post_invoice_bill(self):
        """Post invoice/bill after approval (overrides default post button)"""
        for record in self:
            # Check if invoice/bill is approved
            if hasattr(record, 'approval_state') and record.approval_state != 'approved':
                raise UserError(_("Only approved invoices/bills can be posted. Current state: %s") % record.approval_state)
            
            # Check user permissions
            if not record._check_posting_permissions():
                raise UserError(_("You do not have permission to post invoices/bills."))
        
        try:
            # Call the original post method
            result = super(AccountMove, self).action_post()
            
            # Update approval state after successful posting
            for record in self:
                if hasattr(record, 'approval_state'):
                    record.approval_state = 'posted'
                    record._post_approval_message("posted to ledger")
            
            return result
            
        except Exception as e:
            # Rollback approval state if posting fails
            for record in self:
                if hasattr(record, 'approval_state'):
                    record.approval_state = 'approved'
            _logger.error(f"Failed to post invoice/bill: {str(e)}")
            raise UserError(_("Failed to post invoice/bill: %s") % str(e))

    def action_reject_invoice_bill(self):
        """Reject invoice/bill and return to draft"""
        for record in self:
            if record.approval_state not in ['under_review', 'for_approval']:
                raise UserError(_("Only invoices/bills in review/approval stages can be rejected."))
            
            # Clear approval fields
            record._clear_approval_fields()
            record.approval_state = 'draft'
            record._post_approval_message("rejected and returned to draft for revision")
        
        return self._return_success_message(_('Invoice/Bill has been rejected and returned to draft.'))

    # ============================================================================
    # OVERRIDE METHODS
    # ============================================================================

    def action_post(self):
        """Override core action_post to enforce approval workflow for invoices/bills"""
        for record in self:
            # Only apply approval workflow to invoices and bills
            if record.move_type in ['in_invoice', 'in_refund', 'out_invoice', 'out_refund']:
                # If this is an approved invoice/bill being posted through workflow
                if hasattr(record, 'approval_state') and record.approval_state == 'approved':
                    # Check if user has permission to post
                    if not record._check_posting_permissions():
                        raise UserError(_("You do not have permission to post this invoice/bill."))
                    
                    # Call the original post method and update state
                    result = super(AccountMove, record).action_post()
                    record.approval_state = 'posted'
                    record._post_approval_message("posted to ledger")
                    return result
                
                # If invoice/bill has approval workflow but is not approved
                elif hasattr(record, 'approval_state') and record.approval_state:
                    if record.approval_state == 'draft':
                        raise UserError(_("Invoice/Bill must go through approval workflow. Please submit for review first."))
                    elif record.approval_state in ['under_review', 'for_approval']:
                        raise UserError(_("Invoice/Bill is still under approval workflow. Current state: %s. Please complete the approval process first.") % record.approval_state)
                    elif record.approval_state == 'posted':
                        raise UserError(_("Invoice/Bill is already posted."))
                    elif record.approval_state == 'cancelled':
                        raise UserError(_("Cannot post cancelled invoice/bill."))
                    else:
                        raise UserError(_("Invoice/Bill state is invalid for posting: %s") % record.approval_state)
            
            # For other move types (journal entries, etc.), use default behavior
            else:
                return super(AccountMove, record).action_post()

    @api.model
    def create(self, vals):
        """Initialize approval state for new invoices/bills"""
        move = super(AccountMove, self).create(vals)
        
        # Initialize approval workflow for invoices and bills
        if move.move_type in ['in_invoice', 'in_refund', 'out_invoice', 'out_refund']:
            if not move.approval_state:
                move.approval_state = 'draft'
        
        return move

    # ============================================================================
    # HELPER METHODS
    # ============================================================================

    def _check_approval_permissions(self, stage):
        """Check if user has permission for specific approval stage"""
        if stage == 'review':
            return (self.env.user.has_group('account.group_account_user') or 
                   self.env.user.has_group('account_payment_final.group_payment_reviewer'))
        elif stage == 'approve':
            return (self.env.user.has_group('account.group_account_manager') or 
                   self.env.user.has_group('account_payment_final.group_payment_approver'))
        return False

    def _check_posting_permissions(self):
        """Check if user has permission to post invoices/bills"""
        return (self.env.user.has_group('account.group_account_manager') or 
               self.env.user.has_group('account_payment_final.group_payment_poster'))

    def _post_approval_message(self, action):
        """Post message to chatter about approval action"""
        if self.env.context.get('skip_approval_message'):
            return
        
        user_name = self.env.user.display_name
        message = _("Invoice/Bill %s by %s") % (action, user_name)
        
        self.message_post(
            body=message,
            message_type='notification',
            subtype_xmlid='mail.mt_note'
        )

    def _clear_approval_fields(self):
        """Clear approval workflow fields"""
        self.write({
            'reviewer_id': False,
            'reviewer_date': False,
            'approver_id': False,
            'approver_date': False,
        })

    def _return_success_message(self, message):
        """Return success message for UI feedback"""
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'message': message,
                'sticky': False,
            }
        }

    # ============================================================================
    # REGISTER PAYMENT INTEGRATION
    # ============================================================================

    def action_register_payment(self):
        """Override register payment to enforce approval workflow for all payments"""
        for record in self:
            # Only check approval for invoices and bills
            if record.move_type in ['in_invoice', 'in_refund', 'out_invoice', 'out_refund']:
                # Check if invoice/bill is posted
                if record.state != 'posted':
                    raise UserError(_("Cannot register payment for unposted invoice/bill. Please post the invoice/bill first."))
                
                # Check if invoice/bill went through approval workflow
                if hasattr(record, 'approval_state') and record.approval_state != 'posted':
                    raise UserError(_("Cannot register payment for unapproved invoice/bill. Current approval state: %s") % record.approval_state)
        
        # Get the original register payment action
        action = super(AccountMove, self).action_register_payment()
        
        # Modify context to ensure payment goes through approval workflow
        if isinstance(action, dict) and 'context' in action:
            # Add context flags to force approval workflow
            action['context'].update({
                'from_invoice_payment': True,
                'force_approval_workflow': True,
                'default_approval_state': 'draft',
                'payment_requires_approval': True,
            })
        
        return action

    @api.onchange('approval_state')
    def _onchange_approval_state_move(self):
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
        """Enhanced real-time status updates for invoice/bill approval workflow"""
        # Update approval timestamps in real-time
        now = fields.Datetime.now()
        current_user = self.env.user
        
        if self.approval_state == 'under_review' and not self.reviewer_id:
            self.reviewer_id = current_user.id
            self.reviewer_date = now
        elif self.approval_state == 'approved' and not self.approver_id:
            self.approver_id = current_user.id
            self.approver_date = now
        
        # Enhanced workflow validation
        if self.approval_state == 'posted' and self.state != 'posted':
            return {
                'warning': {
                    'title': _('Ready to Post'),
                    'message': _('This invoice/bill has been fully approved and is ready to be posted to the ledger. Use the Post button to complete the process.')
                }
            }
        
        # Real-time workflow constraints
        if self.approval_state == 'for_approval' and not self.reviewer_id:
            return {
                'warning': {
                    'title': _('Workflow Error'),
                    'message': _('This invoice/bill cannot proceed to approval stage without first being reviewed.')
                }
            }
        
        # Enhanced UI refresh with computed field updates
        return {
            'domain': {},
            'value': {
                'reviewer_id': self.reviewer_id.id if self.reviewer_id else False,
                'reviewer_date': self.reviewer_date,
                'approver_id': self.approver_id.id if self.approver_id else False,
                'approver_date': self.approver_date,
            },
=======
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
        """Real-time status updates for invoice/bill approval workflow"""
        if self.approval_state == 'posted' and self.state != 'posted':
            # Don't automatically post - require explicit action
            return {
                'warning': {
                    'title': _('Ready to Post'),
                    'message': _('This invoice/bill has been approved and is ready to be posted. Please use the Post button to complete the process.')
                }
            }
        
        # Trigger UI refresh for real-time updates
        return {
            'domain': {},
            'value': {},
<<<<<<< Updated upstream
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
        }

    @api.onchange('state')
    def _onchange_state_move_sync(self):
        """Synchronize move state with approval state"""
        if self.state == 'posted' and hasattr(self, 'approval_state') and self.approval_state != 'posted':
            if self.env.user.has_group('account.group_account_manager'):
                self.approval_state = 'posted'

<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
    @api.onchange('amount_total', 'partner_id', 'invoice_date', 'invoice_line_ids')
    def _onchange_invoice_validation_enhanced(self):
        """Enhanced real-time validation for invoice/bill amounts, partners, and workflow requirements"""
        if self.move_type in ['in_invoice', 'in_refund', 'out_invoice', 'out_refund']:
            warnings = []
            
            # Validate amount with enhanced thresholds
=======
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
    @api.onchange('amount_total', 'partner_id')
    def _onchange_invoice_validation(self):
        """Real-time validation for invoice/bill amounts and partners"""
        if self.move_type in ['in_invoice', 'in_refund', 'out_invoice', 'out_refund']:
            # Validate amount
<<<<<<< Updated upstream
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
            if self.amount_total <= 0:
                return {
                    'warning': {
                        'title': _('Invalid Amount'),
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
                        'message': _('Invoice/bill amount must be greater than zero. Please check the invoice lines.')
                    }
                }
            
            # Enhanced amount-based approval requirements
            if self.amount_total > 100000:  # Critical amount threshold
                warnings.append(_('CRITICAL: Amount exceeds $100,000 - requires enhanced approval workflow with additional documentation.'))
            elif self.amount_total > 50000:  # High amount threshold
                warnings.append(_('HIGH: Amount exceeds $50,000 - requires manager approval and verification.'))
            elif self.amount_total > 10000:  # Medium amount threshold
                warnings.append(_('MEDIUM: Amount exceeds $10,000 - standard approval workflow applies.'))
            
            # Validate partner with enhanced checks
=======
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
                        'message': _('Invoice/bill amount must be greater than zero.')
                    }
                }
            
            # Check if high amount requires special approval
            if self.amount_total > 50000:  # High amount threshold
                return {
                    'warning': {
                        'title': _('High Amount Invoice/Bill'),
                        'message': _('This invoice/bill amount is high and may require enhanced approval workflow.')
                    }
                }
            
            # Validate partner
<<<<<<< Updated upstream
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
            if not self.partner_id:
                return {
                    'warning': {
                        'title': _('Partner Required'),
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
                        'message': _('Please select a vendor/customer for this invoice/bill to proceed with approval workflow.')
                    }
                }
            
            # Check partner risk factors
            if hasattr(self.partner_id, 'is_blacklisted') and self.partner_id.is_blacklisted:
                warnings.append(_('WARNING: This partner is blacklisted. Special approval may be required.'))
            
            # Validate invoice date for workflow compliance
            if self.invoice_date and self.invoice_date > fields.Date.today():
                warnings.append(_('NOTICE: Future-dated invoice detected. Verify date accuracy before approval.'))
            
            # Check for missing invoice lines
            if not self.invoice_line_ids:
                return {
                    'warning': {
                        'title': _('Missing Invoice Lines'),
                        'message': _('Invoice/bill must have at least one line item before submission for approval.')
                    }
                }
            
            # Validate workflow state consistency
            if self.approval_state in ['under_review', 'for_approval', 'approved'] and self.state == 'draft':
                # This is normal workflow progression
                pass
            elif self.approval_state == 'posted' and self.state != 'posted':
                warnings.append(_('WORKFLOW: Invoice is approved but not yet posted to ledger.'))
            
            # Return consolidated warnings if any
            if warnings:
                return {
                    'warning': {
                        'title': _('Workflow Validation'),
                        'message': '\n'.join(warnings)
=======
                        'message': _('Please select a partner for this invoice/bill.')
>>>>>>> Stashed changes
=======
                        'message': _('Please select a partner for this invoice/bill.')
>>>>>>> Stashed changes
=======
                        'message': _('Please select a partner for this invoice/bill.')
>>>>>>> Stashed changes
                    }
                }
