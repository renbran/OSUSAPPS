# -*- coding: utf-8 -*-
#############################################################################
#
#    Unified Commission Management System - Workflow Management
#
#############################################################################

import logging
from odoo import fields, models, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class CommissionWorkflow(models.Model):
    """Commission Workflow Management"""
    _name = 'commission.workflow'
    _description = 'Commission Workflow Manager'

    name = fields.Char(string="Workflow Name", default="Commission Workflow")
    active = fields.Boolean(string="Active", default=True)

    @api.model
    def process_workflow_transition(self, commission_lines, target_status):
        """
        Process workflow transition for commission lines
        """
        if not commission_lines:
            return False

        valid_transitions = {
            'draft': ['calculated'],
            'calculated': ['approved', 'cancelled'],
            'approved': ['confirmed', 'cancelled'],
            'confirmed': ['paid'],
            'paid': [],  # Final status
            'cancelled': ['draft']  # Allow reactivation
        }

        for line in commission_lines:
            current_status = line.status

            if target_status not in valid_transitions.get(current_status, []):
                raise UserError(_(
                    "Invalid status transition from '%s' to '%s' for commission %s"
                ) % (current_status, target_status, line.name))

            # Validate permissions for specific transitions
            if target_status == 'approved':
                if not self.env.user.has_group('commission_unified.group_commission_manager'):
                    raise UserError(_("Only Commission Managers can approve commissions"))

            if target_status == 'confirmed':
                if not self.env.user.has_group('commission_unified.group_commission_manager'):
                    raise UserError(_("Only Commission Managers can confirm commissions"))

            # Update status
            line.status = target_status

            # Set appropriate date fields
            if target_status == 'calculated':
                line.date_calculated = fields.Datetime.now()
            elif target_status == 'approved':
                line.date_approved = fields.Datetime.now()
                line.approved_by = self.env.user
            elif target_status == 'confirmed':
                line.confirmed_by = self.env.user
            elif target_status == 'paid':
                line.date_paid = fields.Datetime.now()

            _logger.info(f"Commission {line.name} status changed from {current_status} to {target_status}")

        return True

    @api.model
    def auto_approve_commissions(self, commission_lines):
        """
        Auto-approve commissions based on rules
        """
        auto_approve_limit = float(self.env['ir.config_parameter'].sudo().get_param(
            'commission.auto_approve_limit', '0.0'
        ))

        if auto_approve_limit <= 0:
            return False

        auto_approved = 0
        for line in commission_lines.filtered(lambda l: l.status == 'calculated'):
            if line.commission_amount <= auto_approve_limit:
                line.write({
                    'status': 'approved',
                    'date_approved': fields.Datetime.now(),
                    'approved_by': self.env.ref('base.user_admin').id  # System approval
                })
                auto_approved += 1

        if auto_approved > 0:
            _logger.info(f"Auto-approved {auto_approved} commissions under {auto_approve_limit} limit")

        return auto_approved

    @api.model
    def send_approval_notifications(self, commission_lines):
        """
        Send notifications for commissions requiring approval
        """
        notify_emails = self.env['ir.config_parameter'].sudo().get_param(
            'commission.notification_emails', 'False'
        ).lower() == 'true'

        if not notify_emails:
            return False

        # Group commissions by sales person
        grouped_commissions = {}
        for line in commission_lines.filtered(lambda l: l.status == 'calculated'):
            sales_person = line.sales_person_id
            if sales_person not in grouped_commissions:
                grouped_commissions[sales_person] = []
            grouped_commissions[sales_person].append(line)

        # Send notifications
        for sales_person, lines in grouped_commissions.items():
            self._send_commission_notification(sales_person, lines)

        return True

    def _send_commission_notification(self, sales_person, commission_lines):
        """
        Send commission notification email
        """
        if not sales_person.email:
            return False

        try:
            template = self.env.ref('commission_unified.email_template_commission_calculated')

            total_amount = sum(line.commission_amount for line in commission_lines)

            template.with_context({
                'sales_person': sales_person,
                'commission_lines': commission_lines,
                'total_amount': total_amount,
                'commission_count': len(commission_lines)
            }).send_mail(sales_person.id, force_send=True)

            _logger.info(f"Commission notification sent to {sales_person.name}")
            return True

        except Exception as e:
            _logger.error(f"Failed to send commission notification to {sales_person.name}: {str(e)}")
            return False