# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    """
    Extended ResConfigSettings for Payment Verification and Workflow
    """
    _inherit = 'res.config.settings'
    
    # ============================================================================
    # WORKFLOW SETTINGS - Using config parameters for system-wide settings
    # ============================================================================
    
    enable_payment_approval_workflow = fields.Boolean(
        string='Enable Payment Approval Workflow',
        config_parameter='account_payment_final.enable_payment_approval_workflow',
        help="Enable multi-stage approval workflow for payments"
    )
    
    enable_payment_qr_verification = fields.Boolean(
        string='Enable QR Verification',
        config_parameter='account_payment_final.enable_payment_qr_verification',
        help="Generate QR codes for payment verification"
    )
    
    require_voucher_remarks = fields.Boolean(
        string='Require Voucher Remarks',
        config_parameter='account_payment_final.require_voucher_remarks',
        help="Make remarks mandatory for payment vouchers"
    )
    
    # ============================================================================
    # APPROVAL THRESHOLDS
    # ============================================================================
    
    approval_threshold_1 = fields.Float(
        string='First Approval Threshold',
        config_parameter='account_payment_final.approval_threshold_1',
        help="Amount threshold for first level approval"
    )

    approval_threshold_2 = fields.Float(
        string='Second Approval Threshold',
        config_parameter='account_payment_final.approval_threshold_2',
        help="Amount threshold for second level approval"
    )

    approval_threshold_3 = fields.Float(
        string='Authorization Threshold',
        config_parameter='account_payment_final.approval_threshold_3',
        help="Amount threshold for authorization level"
    )
    
    # ============================================================================
    # CURRENCY FIELD FOR MONETARY FIELDS
    # ============================================================================
    
    currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
        readonly=True,
        help="Company currency for monetary fields"
    )
    
    # ============================================================================
    # PAYMENT VERIFICATION SETTINGS (Company-related)
    # ============================================================================
    
    enable_payment_verification = fields.Boolean(
        string="Enable Payment Verification",
        related='company_id.enable_payment_verification',
        readonly=False,
        help="Globally enable payment verification via QR codes"
    )
    
    
    auto_post_approved_payments = fields.Boolean(
        related='company_id.auto_post_approved_payments',
        readonly=False,
        string='Auto-Post Approved Payments',
        help="Automatically post payments when approved"
    )
    
    enable_four_stage_approval = fields.Boolean(
        related='company_id.enable_four_stage_approval',
        readonly=False,
        string='Enable 4-Stage Approval',
        help="Enable the full 4-stage approval workflow for vendor payments"
    )
    
    send_approval_notifications = fields.Boolean(
        related='company_id.send_approval_notifications',
        readonly=False,
        string='Send Approval Notifications',
        help="Send email notifications for approval requests"
    )
    
    enable_qr_codes = fields.Boolean(
        related='company_id.enable_qr_codes',
        readonly=False,
        string='Enable QR Codes',
        help="Generate QR codes for payment vouchers"
    )
    
    use_osus_branding = fields.Boolean(
        related='company_id.use_osus_branding',
        readonly=False,
        string='Use OSUS Branding',
        help="Apply OSUS brand guidelines to payment vouchers"
    )
    
    # ============================================================================
    # COMPUTED FIELDS FOR DASHBOARD
    # ============================================================================
    
    payment_voucher_statistics = fields.Text(
        string='Payment Voucher Statistics',
        compute='_compute_payment_voucher_statistics',
        help="Current payment voucher statistics"
    )
    
    @api.depends('company_id')
    def _compute_payment_voucher_statistics(self):
        """Compute payment voucher statistics for the dashboard"""
        for record in self:
            try:
                if record.company_id:
                    payment_obj = self.env['account.payment']
                    domain = [
                        ('company_id', '=', record.company_id.id),
                        ('payment_type', 'in', ['outbound', 'inbound'])
                    ]
                    stats = {}
                    
                    # Count by approval states if available
                    if 'approval_state' in payment_obj._fields:
                        states = ['draft', 'under_review', 'for_approval', 'for_authorization', 'approved', 'posted', 'cancelled']
                        for state in states:
                            count = payment_obj.search_count(domain + [('approval_state', '=', state)])
                            if count > 0:
                                stats[state] = count
                    else:
                        # Fallback to verification status
                        if 'verification_status' in payment_obj._fields:
                            states = ['pending', 'verified', 'rejected']
                            for state in states:
                                count = payment_obj.search_count(domain + [('verification_status', '=', state)])
                                if count > 0:
                                    stats[state] = count
                        else:
                            # Standard state fallback
                            states = ['draft', 'posted', 'cancelled']
                            for state in states:
                                count = payment_obj.search_count(domain + [('state', '=', state)])
                                if count > 0:
                                    stats[state] = count
                    
                    total_payments = sum(stats.values()) if stats else 0
                    
                    # Format statistics
                    if total_payments > 0:
                        stats_lines = [_("Total Payments: %s") % total_payments]
                        for state, count in stats.items():
                            stats_lines.append(_("• %s: %s") % (state.replace('_', ' ').title(), count))
                        record.payment_voucher_statistics = '\n'.join(stats_lines)
                    else:
                        record.payment_voucher_statistics = _("No payments found")
                else:
                    record.payment_voucher_statistics = _("No company selected")
            except Exception as e:
                _logger.error("Error computing payment voucher statistics: %s", e)
                record.payment_voucher_statistics = _("Error computing statistics: %s") % str(e)
    
    # ============================================================================
    # VALIDATION METHODS
    # ============================================================================
    
    @api.constrains('approval_threshold_1', 'approval_threshold_2', 'approval_threshold_3')
    def _check_approval_thresholds(self):
        """Validate approval threshold sequence"""
        for record in self:
            if record.approval_threshold_1 and record.approval_threshold_2:
                if record.approval_threshold_1 >= record.approval_threshold_2:
                    raise ValidationError(_("Second approval threshold must be higher than first threshold"))
            
            if record.approval_threshold_2 and record.approval_threshold_3:
                if record.approval_threshold_2 >= record.approval_threshold_3:
                    raise ValidationError(_("Authorization threshold must be higher than second approval threshold"))
    
    # ============================================================================
    # ACTION METHODS
    # ============================================================================
    
    def action_view_payment_dashboard(self):
        """Open payment voucher dashboard"""
        self.ensure_one()
        payment_obj = self.env['account.payment']
        group_by_field = 'state'  # Default fallback
        
        # Determine best group by field
        if 'approval_state' in payment_obj._fields:
            group_by_field = 'approval_state'
        elif 'verification_status' in payment_obj._fields:
            group_by_field = 'verification_status'
            
        return {
            'type': 'ir.actions.act_window',
            'name': _('Payment Voucher Dashboard'),
            'res_model': 'account.payment',
            'view_mode': 'kanban,tree,form',
            'domain': [
                ('company_id', '=', self.company_id.id),
                ('payment_type', 'in', ['outbound', 'inbound'])
            ],
            'context': {
                'group_by': group_by_field,
                'search_default_group_by_%s' % group_by_field: 1,
            }
        }
    
    def action_test_qr_generation(self):
        """Test QR code generation functionality"""
        self.ensure_one()
        try:
            # Find a suitable journal
            journal = self.env['account.journal'].search([
                ('type', 'in', ['bank', 'cash']),
                ('company_id', '=', self.company_id.id)
            ], limit=1)
            
            if not journal:
                journal = self.env['account.journal'].search([('type', 'in', ['bank', 'cash'])], limit=1)
            
            if not journal:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('QR Code Test Failed'),
                        'message': _('No suitable journal found for test payment creation'),
                        'type': 'warning',
                        'sticky': False,
                    }
                }
            
            # Create test payment
            test_values = {
                'payment_type': 'outbound',
                'partner_id': self.env.ref('base.res_partner_1', raise_if_not_found=False).id or self.env['res.partner'].search([], limit=1).id,
                'amount': 1000.0,
                'currency_id': self.company_id.currency_id.id,
                'journal_id': journal.id,
                'date': fields.Date.today(),
            }
            
            # Add optional fields if they exist
            if 'remarks' in self.env['account.payment']._fields:
                test_values['remarks'] = 'QR Code Test Payment'
            if 'qr_in_report' in self.env['account.payment']._fields:
                test_values['qr_in_report'] = True
                
            test_payment = self.env['account.payment'].create(test_values)
            
            # Test QR code generation - only if payment was created successfully
            qr_generated = False
            if test_payment and test_payment.id:
                if hasattr(test_payment, '_compute_payment_qr_code'):
                    test_payment._compute_payment_qr_code()
                
                # Check if QR code was generated
                if hasattr(test_payment, 'qr_code') and test_payment.qr_code:
                    qr_generated = True
            
            # Clean up test payment
            if test_payment:
                test_payment.unlink()
            
            if qr_generated:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('QR Code Test Successful'),
                        'message': _('QR code generated successfully for test payment'),
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('QR Code Test Failed'),
                        'message': _('QR code was not generated. Please check your configuration and ensure the qrcode Python library is installed.'),
                        'type': 'warning',
                        'sticky': False,
                    }
                }
        except Exception as e:
            _logger.error("QR code test generation failed: %s", e)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('QR Code Test Error'),
                    'message': _('An error occurred during QR code test: %s') % str(e),
                    'type': 'danger',
                    'sticky': False,
                }
            }