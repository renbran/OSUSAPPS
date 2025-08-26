# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    # Enhanced workflow fields
    approval_state = fields.Selection([
        ('draft', 'Draft'),
        ('under_review', 'Under Review'),
        ('for_approval', 'For Approval'),
        ('for_authorization', 'For Authorization'),
        ('approved', 'Approved')
    ], string='Initial Approval State', default='draft',
       help="Set the initial approval state for the payment")

    submit_for_approval = fields.Boolean(
        string='Submit for Approval',
        default=False,
        help="Automatically submit payment for approval workflow"
    )

    skip_approval_workflow = fields.Boolean(
        string='Skip Approval Workflow',
        default=False,
        help="Bypass approval workflow (Manager only)"
    )

    # Enhanced voucher fields
    remarks = fields.Text(
        string='Remarks/Memo',
        help="Additional remarks for this payment"
    )

    generate_qr_code = fields.Boolean(
        string='Generate QR Code',
        default=True,
        help="Generate QR code for payment verification"
    )

    voucher_number = fields.Char(
        string='Voucher Number',
        readonly=True,
        help="Auto-generated voucher number"
    )

    # Workflow assignment fields
    reviewer_id = fields.Many2one(
        'res.users',
        string='Assign Reviewer',
        domain="[('groups_id', 'in', [group_payment_reviewer])]",
        help="Assign specific user for review stage"
    )

    approver_id = fields.Many2one(
        'res.users',
        string='Assign Approver', 
        domain="[('groups_id', 'in', [group_payment_approver])]",
        help="Assign specific user for approval stage"
    )

    authorizer_id = fields.Many2one(
        'res.users',
        string='Assign Authorizer',
        domain="[('groups_id', 'in', [group_payment_authorizer])]",
        help="Assign specific user for authorization stage"
    )

    # Computed fields for workflow permissions
    can_skip_workflow = fields.Boolean(
        compute='_compute_workflow_permissions',
        help="Whether current user can skip approval workflow"
    )

    workflow_required = fields.Boolean(
        compute='_compute_workflow_requirements',
        help="Whether approval workflow is required for this payment"
    )

    # Multi-payment batch fields
    batch_payment = fields.Boolean(
        string='Batch Payment',
        default=False,
        help="Create multiple payments in batch"
    )

    batch_description = fields.Text(
        string='Batch Description',
        help="Description for batch payment processing"
    )

    @api.depends('amount', 'payment_type')
    def _compute_workflow_requirements(self):
        """Determine if workflow is required based on amount thresholds"""
        for wizard in self:
            # Get approval thresholds from settings
            threshold_1 = float(self.env['ir.config_parameter'].sudo().get_param(
                'account_payment_final.approval_threshold_1', 0))
            
            workflow_enabled = self.env['ir.config_parameter'].sudo().get_param(
                'account_payment_final.enable_payment_approval_workflow', False)
            
            wizard.workflow_required = (
                workflow_enabled and 
                wizard.amount >= threshold_1 and
                wizard.payment_type == 'outbound'
            )

    @api.depends('amount')
    def _compute_workflow_permissions(self):
        """Compute workflow permissions for current user"""
        for wizard in self:
            user = self.env.user
            wizard.can_skip_workflow = (
                user.has_group('account.group_account_manager') or
                user.has_group('account_payment_final.group_payment_manager')
            )

    @api.onchange('submit_for_approval')
    def _onchange_submit_for_approval(self):
        """Update approval state when submit for approval is changed"""
        if self.submit_for_approval:
            self.approval_state = 'under_review'
        else:
            self.approval_state = 'draft'

    @api.onchange('skip_approval_workflow')
    def _onchange_skip_approval_workflow(self):
        """Handle skip workflow toggle"""
        if self.skip_approval_workflow and not self.can_skip_workflow:
            raise ValidationError(_("You don't have permission to skip approval workflow"))
        
        if self.skip_approval_workflow:
            self.approval_state = 'approved'
            self.submit_for_approval = False

    @api.onchange('payment_type', 'amount')
    def _onchange_payment_details(self):
        """Update workflow requirements when payment details change"""
        self._compute_workflow_requirements()
        
        # Auto-assign users based on amount thresholds
        if self.workflow_required and self.payment_type == 'outbound':
            self._auto_assign_workflow_users()

    def _auto_assign_workflow_users(self):
        """Auto-assign users to workflow stages based on company settings"""
        try:
            # Get default reviewers/approvers from company settings
            company = self.env.company
            
            # Auto-assign reviewer if not set
            if not self.reviewer_id:
                default_reviewers = self.env['res.users'].search([
                    ('groups_id', 'in', [self.env.ref('account_payment_final.group_payment_reviewer').id]),
                    ('company_ids', 'in', [company.id])
                ], limit=1)
                if default_reviewers:
                    self.reviewer_id = default_reviewers[0]

            # Auto-assign approver for higher amounts
            threshold_2 = float(self.env['ir.config_parameter'].sudo().get_param(
                'account_payment_final.approval_threshold_2', 0))
            
            if self.amount >= threshold_2 and not self.approver_id:
                default_approvers = self.env['res.users'].search([
                    ('groups_id', 'in', [self.env.ref('account_payment_final.group_payment_approver').id]),
                    ('company_ids', 'in', [company.id])
                ], limit=1)
                if default_approvers:
                    self.approver_id = default_approvers[0]

        except Exception as e:
            _logger.warning("Error auto-assigning workflow users: %s", e)

    def _generate_voucher_number(self, payment_type):
        """Generate voucher number for payment"""
        sequence_code = 'receipt.voucher' if payment_type == 'inbound' else 'payment.voucher'
        return self.env['ir.sequence'].next_by_code(sequence_code) or '/'

    def _create_payment_vals_list(self, to_process):
        """Override to add enhanced fields to payment values"""
        payment_vals_list = super()._create_payment_vals_list(to_process)
        
        for payment_vals in payment_vals_list:
            # Add voucher number
            payment_vals['voucher_number'] = self._generate_voucher_number(payment_vals.get('payment_type', 'outbound'))
            
            # Add workflow fields
            payment_vals.update({
                'approval_state': self.approval_state,
                'remarks': self.remarks,
                'qr_in_report': self.generate_qr_code,
                'reviewer_id': self.reviewer_id.id if self.reviewer_id else False,
                'approver_id': self.approver_id.id if self.approver_id else False,
                'authorizer_id': self.authorizer_id.id if self.authorizer_id else False,
            })
            
            # Set verification status
            payment_vals['verification_status'] = 'pending'

        return payment_vals_list

    def action_create_payments(self):
        """Enhanced payment creation with workflow integration"""
        
        # Validate workflow requirements
        if self.workflow_required and not self.skip_approval_workflow and not self.submit_for_approval:
            raise UserError(_(
                'This payment amount (%.2f) requires approval workflow. '
                'Please check "Submit for Approval" or contact your manager.'
            ) % self.amount)
        
        # Validate mandatory fields if enabled
        require_remarks = self.env['ir.config_parameter'].sudo().get_param(
            'account_payment_final.require_voucher_remarks', False)
        
        if require_remarks and not self.remarks:
            raise ValidationError(_('Remarks are mandatory for payment vouchers'))

        # Create payments with enhanced functionality
        payments = super().action_create_payments()
        
        # Post-creation processing
        if isinstance(payments, dict) and payments.get('res_id'):
            payment_ids = [payments['res_id']]
        else:
            payment_ids = payments.mapped('id') if hasattr(payments, 'mapped') else []

        if payment_ids:
            created_payments = self.env['account.payment'].browse(payment_ids)
            self._post_process_payments(created_payments)

        return payments

    def _post_process_payments(self, payments):
        """Post-process created payments"""
        for payment in payments:
            try:
                # Create approval history entry
                self._create_approval_history(payment)
                
                # Send notifications if enabled
                self._send_creation_notifications(payment)
                
                # Auto-submit for approval if requested
                if self.submit_for_approval and hasattr(payment, 'action_submit_for_review'):
                    payment.action_submit_for_review()
                
            except Exception as e:
                _logger.warning("Error post-processing payment %s: %s", payment.voucher_number, e)

    def _create_approval_history(self, payment):
        """Create initial approval history record"""
        try:
            approval_history_model = self.env.get('payment.approval.history')
            if approval_history_model:
                approval_history_model.create({
                    'payment_id': payment.id,
                    'action_type': 'create',
                    'stage_from': 'draft',
                    'stage_to': payment.approval_state,
                    'user_id': self.env.user.id,
                    'comments': f'Payment created through wizard with voucher number {payment.voucher_number}'
                })
        except Exception as e:
            _logger.warning("Could not create approval history: %s", e)

    def _send_creation_notifications(self, payment):
        """Send email notifications for payment creation"""
        try:
            send_notifications = self.env['ir.config_parameter'].sudo().get_param(
                'account_payment_final.send_approval_notifications', False)
            
            if not send_notifications:
                return

            # Send notification to assigned reviewer
            if payment.reviewer_id:
                template = self.env.ref('account_payment_final.mail_template_payment_assigned', False)
                if template:
                    template.send_mail(payment.id, force_send=True)

            # Post message on payment record
            payment.message_post(
                body=_("Payment %s created and ready for workflow processing") % payment.voucher_number,
                message_type='notification'
            )
            
        except Exception as e:
            _logger.warning("Error sending notifications for payment %s: %s", payment.voucher_number, e)

    def action_create_batch_payments(self):
        """Create multiple payments in batch"""
        if not self.batch_payment:
            return self.action_create_payments()

        # Validate batch requirements
        if not self.batch_description:
            raise ValidationError(_('Batch description is required for batch payments'))

        # Create payments with batch processing
        payments = self.action_create_payments()
        
        # Create batch record if multiple payments
        if hasattr(payments, 'mapped') and len(payments) > 1:
            self._create_batch_record(payments)

        return payments

    def _create_batch_record(self, payments):
        """Create batch payment record for tracking"""
        try:
            batch_model = self.env.get('payment.batch')
            if batch_model:
                batch_model.create({
                    'name': f'Batch Payment - {fields.Datetime.now().strftime("%Y%m%d-%H%M")}',
                    'description': self.batch_description,
                    'payment_ids': [(6, 0, payments.ids)],
                    'total_amount': sum(payments.mapped('amount')),
                    'currency_id': payments[0].currency_id.id if payments else False,
                    'create_uid': self.env.user.id,
                })
        except Exception as e:
            _logger.warning("Could not create batch record: %s", e)

    @api.model
    def default_get(self, fields_list):
        """Set default values with enhanced logic"""
        defaults = super().default_get(fields_list)
        
        # Auto-generate voucher number preview
        if 'voucher_number' in fields_list:
            payment_type = defaults.get('payment_type', 'outbound')
            defaults['voucher_number'] = self._generate_voucher_number(payment_type)
        
        # Set QR code generation based on company settings
        if 'generate_qr_code' in fields_list:
            qr_enabled = self.env['ir.config_parameter'].sudo().get_param(
                'account_payment_final.enable_payment_qr_verification', True)
            defaults['generate_qr_code'] = qr_enabled

        return defaults