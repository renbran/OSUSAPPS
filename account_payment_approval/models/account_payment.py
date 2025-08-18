# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Jumana Haseen (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import fields, models, _
from odoo.exceptions import ValidationError, UserError
from lxml import etree
from odoo import api
import logging

_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    """This class inherits model "account.payment" and adds required fields """
    _inherit = "account.payment"

    state = fields.Selection([
        ('draft', 'Draft'),
        ('reviewed', 'Reviewed'),
        ('approved', 'Approved'),
        ('authorized', 'Authorized'),
        ('posted', 'Posted'),
    ], default='draft', string='Status', tracking=True)

    reviewer_id = fields.Many2one('res.users', string='Reviewer', tracking=True)
    approver_id = fields.Many2one('res.users', string='Approver', tracking=True)
    authorizer_id = fields.Many2one('res.users', string='Authorizer', tracking=True)
    poster_id = fields.Many2one('res.users', string='Poster', tracking=True)

    reviewed_date = fields.Datetime(string='Reviewed Date', tracking=True)
    approved_date = fields.Datetime(string='Approved Date', tracking=True)
    authorized_date = fields.Datetime(string='Authorized Date', tracking=True)
    posted_date = fields.Datetime(string='Posted Date', tracking=True)

    qr_code = fields.Binary(string='QR Code', readonly=True)
    qr_token = fields.Char(string='QR Token', size=64, readonly=True)

    def _generate_qr_code(self):
        import qrcode
        import io
        import base64
        for rec in self:
            if not rec.qr_token:
                import secrets
                rec.qr_token = secrets.token_hex(32)
            url = f'https://my-odoo.com/verify/{rec.id}/{rec.qr_token}'
            qr = qrcode.QRCode(version=1, box_size=10, border=2)
            qr.add_data(url)
            qr.make(fit=True)
            img = qr.make_image(fill='black', back_color='white')
            buf = io.BytesIO()
            img.save(buf, format='PNG')
            rec.qr_code = base64.b64encode(buf.getvalue())

    def action_review(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('Only draft payments can be reviewed.'))
            rec.state = 'reviewed'
            rec.reviewer_id = self.env.user
            rec.reviewed_date = fields.Datetime.now()

    def action_approve(self):
        for rec in self:
            if rec.state != 'reviewed':
                raise UserError(_('Only reviewed payments can be approved.'))
            rec.state = 'approved'
            rec.approver_id = self.env.user
            rec.approved_date = fields.Datetime.now()

    def action_authorize(self):
        for rec in self:
            if rec.state != 'approved':
                raise UserError(_('Only approved payments can be authorized.'))
            rec.state = 'authorized'
            rec.authorizer_id = self.env.user
            rec.authorized_date = fields.Datetime.now()

    def action_post(self):
        for rec in self:
            if rec.payment_type == 'inbound':
                if rec.state != 'approved':
                    raise UserError(_('Receipts must be approved before posting.'))
            else:
                if rec.state != 'authorized':
                    raise UserError(_('Payments must be authorized before posting.'))
            res = super().action_post()
            rec.state = 'posted'
            rec.poster_id = self.env.user
            rec.posted_date = fields.Datetime.now()
            return res

    def _compute_is_approve_person(self):
        """This function checks if the current user is authorized to approve payments.
        It supports both single approver and multiple approvers configuration.
        Multiple approvers take precedence over single approver if both are configured."""
        for record in self:
            approval = self.env['ir.config_parameter'].sudo().get_param(
                'account_payment_approval.payment_approval')
            
            if not approval:
                record.is_approve_person = False
                continue
                
            # Check for multiple approvers first (takes precedence)
            multiple_approvers_param = self.env['ir.config_parameter'].sudo().get_param(
                'account_payment_approval.approval_user_ids', '')
            
            if multiple_approvers_param:
                try:
                    # Parse the comma-separated string of user IDs
                    approver_ids = [int(x.strip()) for x in multiple_approvers_param.split(',') if x.strip()]
                    if approver_ids:  # Only use if we actually have IDs
                        record.is_approve_person = self.env.user.id in approver_ids
                        continue
                except (ValueError, AttributeError):
                    # If parsing fails, fall back to single approver
                    pass
            
            # Fall back to single approver configuration
            single_approver_param = self.env['ir.config_parameter'].sudo().get_param(
                'account_payment_approval.approval_user_id', '')
            if single_approver_param:
                try:
                    approver_id = int(single_approver_param)
                    record.is_approve_person = self.env.user.id == approver_id
                except (ValueError, TypeError):
                    record.is_approve_person = False
            else:
                record.is_approve_person = False

    def _is_user_authorized_approver(self, user_id=None):
        """Helper method to check if a user is authorized to approve payments.
        Supports both single and multiple approver configurations.
        
        Args:
            user_id (int): User ID to check. If None, uses current user.
            
        Returns:
            bool: True if user is authorized to approve payments
        """
        if user_id is None:
            user_id = self.env.user.id
            
        approval = self.env['ir.config_parameter'].sudo().get_param(
            'account_payment_approval.payment_approval')
        
        if not approval:
            return False
            
        # Check for multiple approvers first (takes precedence)
        multiple_approvers_param = self.env['ir.config_parameter'].sudo().get_param(
            'account_payment_approval.approval_user_ids', '')
        
        if multiple_approvers_param:
            try:
                # Parse the comma-separated string of user IDs
                approver_ids = [int(x.strip()) for x in multiple_approvers_param.split(',') if x.strip()]
                if approver_ids:  # Only use if we actually have IDs
                    return user_id in approver_ids
            except (ValueError, AttributeError):
                # If parsing fails, fall back to single approver
                pass
        
        # Fall back to single approver configuration
        single_approver_param = self.env['ir.config_parameter'].sudo().get_param(
            'account_payment_approval.approval_user_id', '')
        if single_approver_param:
            try:
                approver_id = int(single_approver_param)
                return user_id == approver_id
            except (ValueError, TypeError):
                return False
        
        return False

    def get_authorized_approvers(self):
        """Get list of authorized approvers for this payment"""
        approval = self.env['ir.config_parameter'].sudo().get_param(
            'account_payment_approval.payment_approval')
        
        if not approval:
            return self.env['res.users']
            
        # Check for multiple approvers first
        multiple_approvers_param = self.env['ir.config_parameter'].sudo().get_param(
            'account_payment_approval.approval_user_ids', '')
        
        if multiple_approvers_param:
            try:
                approver_ids = [int(x.strip()) for x in multiple_approvers_param.split(',') if x.strip()]
                if approver_ids:  # Only use if we actually have IDs
                    return self.env['res.users'].browse(approver_ids).exists()
            except (ValueError, AttributeError):
                pass
        
        # Fall back to single approver
        single_approver_param = self.env['ir.config_parameter'].sudo().get_param(
            'account_payment_approval.approval_user_id', '')
        if single_approver_param:
            try:
                approver_id = int(single_approver_param)
                return self.env['res.users'].browse(approver_id).exists()
            except (ValueError, TypeError):
                pass
        
        return self.env['res.users']

    is_approve_person = fields.Boolean(string='Approving Person',
                                       compute=_compute_is_approve_person,
                                       readonly=True,
                                       help="Enable/disable if approving"
                                            " person")

    authorized_approvers_display = fields.Char(
        string='Authorized Approvers',
        compute='_compute_authorized_approvers_display',
        readonly=True,
        help="List of users authorized to approve this payment"
    )

    def _compute_authorized_approvers_display(self):
        """Compute display string for authorized approvers"""
        for record in self:
            approvers = record.get_authorized_approvers()
            if approvers:
                approver_names = approvers.mapped('name')
                record.authorized_approvers_display = ', '.join(approver_names)
            else:
                record.authorized_approvers_display = 'No approvers configured'

    is_locked = fields.Boolean(string='Locked', compute='_compute_is_locked', store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('cancel', 'Cancelled'),
        ('waiting_approval', 'Waiting for Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Status', required=True, readonly=True, copy=False, tracking=True,
        default='draft')

    @api.depends('state')
    def _compute_is_locked(self):
        for rec in self:
            # Allow editing only in draft and rejected states
            # Approved payments should be locked for editing but allow posting
            rec.is_locked = rec.state not in ['draft', 'rejected']

    def write(self, vals):
        """Override write to add workflow validation"""
        if 'state' in vals:
            for record in self:
                # Validate state transitions
                if record.state == 'posted' and vals['state'] != 'cancel':
                    raise UserError(_("Posted payments can only be cancelled."))
                if record.state == 'waiting_approval' and vals['state'] not in ['approved', 'rejected', 'cancel']:
                    raise UserError(_("Payments waiting for approval can only be approved, rejected, or cancelled."))
                if record.state == 'approved' and vals['state'] not in ['posted', 'cancel']:
                    raise UserError(_("Approved payments can only be posted or cancelled."))
        return super(AccountPayment, self).write(vals)

    def action_post(self):
        """Overwrites the action_post() to validate the payment in the 'approved'
         stage too.
        currently Odoo allows payment posting only in draft stage."""
        
        # Handle multiple records by processing each one individually
        for payment in self:
            # Skip approval check if called from approve_transfer or if already approved
            if not self.env.context.get('skip_approval_check') and payment.state == 'draft':
                validation = payment._check_payment_approval()
                if not validation:
                    return False
                    
            # Allow posting from both draft and approved states
            if payment.state in ('posted', 'cancel', 'waiting_approval', 'rejected'):
                raise UserError(
                    _("Only a draft or approved payment can be posted."))
            if any(inv.state != 'posted' for inv in
                   payment.reconciled_invoice_ids):
                raise ValidationError(_("The payment cannot be processed "
                                        "because the invoice is not open!"))
        
        # Call the parent's action_post method to ensure proper sequence generation
        # and all standard Odoo posting logic
        return super(AccountPayment, self).action_post()

    def _check_payment_approval(self):
        """This function checks the payment approval if payment_amount grater
         than amount,then state changed to waiting_approval """
        self.ensure_one()
        if self.state == "draft":
            first_approval = self.env['ir.config_parameter'].sudo().get_param(
                'account_payment_approval.payment_approval')
            if first_approval:
                amount = float(self.env['ir.config_parameter'].sudo().get_param(
                    'account_payment_approval.approval_amount'))
                payment_currency_id = int(
                    self.env['ir.config_parameter'].sudo().get_param(
                        'account_payment_approval.approval_currency_id'))
                payment_amount = self.amount
                if payment_currency_id:
                    if (self.currency_id and
                            self.currency_id.id != payment_currency_id):
                        currency_id = self.env['res.currency'].browse(
                            payment_currency_id)
                        payment_amount = (self.currency_id._convert(
                            self.amount, currency_id, self.company_id,
                            self.date or fields.Date.today(), round=True))
                if payment_amount > amount:
                    self.write({
                        'state': 'waiting_approval'
                    })
                    return False
        return True

    def action_submit_review(self):
        """Submit the payment for review"""
        for record in self:
            if record.state == 'draft':
                record.state = 'waiting_approval'

    def approve_transfer(self):
        """This function changes state to approved state if approving person
         approves payment and automatically posts the payment"""
        for record in self:
            if record.state == 'waiting_approval' and record._is_user_authorized_approver():
                # First, set state to approved
                record.write({
                    'state': 'approved'
                })
                # Ensure the record is refreshed before posting
                record.invalidate_recordset()
                # Automatically post the payment after approval
                try:
                    # Post the payment directly from approved state
                    result = record.with_context(skip_approval_check=True).action_post()
                    return result
                except Exception as e:
                    # If posting fails, keep approved state and log the error
                    _logger.error(f"Failed to auto-post payment after approval: {str(e)}")
                    # Raise a user-friendly error but keep the approved state
                    raise UserError(f"Payment approved successfully but failed to post automatically: {str(e)}. You can manually post it from the approved state.")

    def reject_transfer(self):
        """Reject the payment transfer"""
        for record in self:
            if record.state == 'waiting_approval' and record._is_user_authorized_approver():
                record.state = 'rejected'
                # Allow draft and cancel actions after rejection
                record.is_locked = False

    def bulk_approve_payments(self):
        """Bulk approve multiple payments that are waiting for approval.
        This method overrides singleton constraint and allows bulk processing."""
        # Check if current user is an authorized approver
        if not self._is_user_authorized_approver():
            raise UserError(_("You are not authorized to approve payments."))
        
        # Filter payments that can be approved
        approvable_payments = self.filtered(lambda p: p.state == 'waiting_approval')
        
        if not approvable_payments:
            raise UserError(_("No payments found that are waiting for approval."))
        
        approved_count = 0
        failed_payments = []
        
        # Process each payment individually to handle any errors gracefully
        for payment in approvable_payments:
            try:
                # Set state to approved first
                payment.write({'state': 'approved'})
                # Ensure the record is refreshed before posting
                payment.invalidate_recordset()
                # Automatically post the payment after approval
                payment.with_context(skip_approval_check=True).action_post()
                approved_count += 1
            except Exception as e:
                failed_payments.append({
                    'payment': payment,
                    'error': str(e)
                })
                # Keep the payment in approved state even if posting fails
                _logger.error(f"Failed to post payment {payment.name} after bulk approval: {str(e)}")
        
        # Prepare result message
        if approved_count > 0:
            message = _("%d payment(s) have been approved and posted successfully.") % approved_count
            if failed_payments:
                message += _(" %d payment(s) were approved but failed to post automatically and can be posted manually.") % len(failed_payments)
            
            # Show notification to user
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Bulk Approval Complete'),
                    'message': message,
                    'type': 'success' if not failed_payments else 'warning',
                    'sticky': False,
                }
            }
        else:
            raise UserError(_("No payments could be approved."))

    def bulk_reject_payments(self):
        """Bulk reject multiple payments that are waiting for approval.
        This method overrides singleton constraint and allows bulk processing."""
        # Check if current user is an authorized approver
        if not self._is_user_authorized_approver():
            raise UserError(_("You are not authorized to reject payments."))
        
        # Filter payments that can be rejected
        rejectable_payments = self.filtered(lambda p: p.state == 'waiting_approval')
        
        if not rejectable_payments:
            raise UserError(_("No payments found that are waiting for approval."))
        
        rejected_count = 0
        failed_payments = []
        
        # Process each payment individually to handle any errors gracefully
        for payment in rejectable_payments:
            try:
                # Set state to rejected and unlock
                payment.write({
                    'state': 'rejected',
                    'is_locked': False
                })
                rejected_count += 1
            except Exception as e:
                failed_payments.append({
                    'payment': payment,
                    'error': str(e)
                })
                _logger.error(f"Failed to reject payment {payment.name}: {str(e)}")
        
        # Prepare result message
        if rejected_count > 0:
            message = _("%d payment(s) have been rejected successfully.") % rejected_count
            if failed_payments:
                message += _(" %d payment(s) failed to be rejected.") % len(failed_payments)
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Bulk Rejection Complete'),
                    'message': message,
                    'type': 'success' if not failed_payments else 'warning',
                    'sticky': False,
                }
            }
        else:
            raise UserError(_("No payments could be rejected."))

    def bulk_draft_payments(self):
        """Bulk set multiple payments back to draft state.
        This method allows resetting rejected or cancelled payments to draft."""
        # Filter payments that can be set to draft
        draftable_payments = self.filtered(lambda p: p.state in ['rejected', 'cancel'])
        
        if not draftable_payments:
            raise UserError(_("No payments found that can be set to draft state. Only rejected or cancelled payments can be reset to draft."))
        
        drafted_count = 0
        failed_payments = []
        
        # Process each payment individually to handle any errors gracefully
        for payment in draftable_payments:
            try:
                # Set state to draft and unlock
                payment.write({
                    'state': 'draft',
                    'is_locked': False
                })
                drafted_count += 1
            except Exception as e:
                failed_payments.append({
                    'payment': payment,
                    'error': str(e)
                })
                _logger.error(f"Failed to set payment {payment.name} to draft: {str(e)}")
        
        # Prepare result message
        if drafted_count > 0:
            message = _("%d payment(s) have been set to draft successfully.") % drafted_count
            if failed_payments:
                message += _(" %d payment(s) failed to be set to draft.") % len(failed_payments)
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Bulk Draft Complete'),
                    'message': message,
                    'type': 'success' if not failed_payments else 'warning',
                    'sticky': False,
                }
            }
        else:
            raise UserError(_("No payments could be set to draft."))

    def bulk_submit_for_approval(self):
        """Bulk submit multiple payments for approval.
        This method submits draft payments that exceed the approval amount threshold."""
        
        # Filter payments that can be submitted for approval (draft state)
        submittable_payments = self.filtered(lambda p: p.state == 'draft')
        
        if not submittable_payments:
            raise UserError(_("No draft payments found that can be submitted for approval."))
        
        submitted_count = 0
        skipped_count = 0
        failed_payments = []
        
        # Process each payment individually to handle any errors gracefully
        for payment in submittable_payments:
            try:
                # Check if this payment needs approval based on amount threshold
                # _check_payment_approval returns False when approval is needed and sets state to waiting_approval
                approval_result = payment._check_payment_approval()
                
                if not approval_result:
                    # Payment was automatically set to waiting_approval by _check_payment_approval
                    submitted_count += 1
                else:
                    # Payment doesn't need approval (amount below threshold)
                    skipped_count += 1
                    
            except Exception as e:
                failed_payments.append({
                    'payment': payment,
                    'error': str(e)
                })
                _logger.error(f"Failed to submit payment {payment.name} for approval: {str(e)}")
        
        # Prepare result message
        message_parts = []
        notification_type = 'success'
        
        if submitted_count > 0:
            message_parts.append(_("%d payment(s) have been submitted for approval successfully.") % submitted_count)
        
        if skipped_count > 0:
            message_parts.append(_("%d payment(s) were skipped as they don't require approval (amount below threshold).") % skipped_count)
            notification_type = 'info'
        
        if failed_payments:
            message_parts.append(_("%d payment(s) failed to be submitted for approval.") % len(failed_payments))
            notification_type = 'warning'
        
        if submitted_count > 0 or skipped_count > 0:
            message = ' '.join(message_parts)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Bulk Submit Complete'),
                    'message': message,
                    'type': notification_type,
                    'sticky': False,
                }
            }
        else:
            raise UserError(_("No payments could be submitted for approval."))

    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(AccountPayment, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'form' and self:
            # Ensure we have a single record for state access
            self.ensure_one()
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//form"):
                # Allow editing only in draft and rejected states
                node.set('edit', "0" if self.state not in ['draft', 'rejected'] else "1")
            res['arch'] = etree.tostring(doc, encoding='unicode')
        return res
