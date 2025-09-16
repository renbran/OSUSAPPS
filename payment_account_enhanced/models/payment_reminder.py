# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class PaymentReminderManager(models.Model):
    _name = 'payment.reminder.manager'
    _description = 'Payment Approval Reminder Manager'

    @api.model
    def send_approval_reminders(self):
        """Cron job method to send approval reminders"""
        try:
            # Get current time
            now = datetime.now()
            
            # Define reminder thresholds (in hours)
            reminder_after_hours = 24  # Send reminder after 24 hours
            escalation_after_hours = 72  # Send escalation after 72 hours
            
            # Calculate cutoff times
            reminder_cutoff = now - timedelta(hours=reminder_after_hours)
            escalation_cutoff = now - timedelta(hours=escalation_after_hours)
            
            # Find payments needing reminders
            pending_payments = self.env['account.payment'].search([
                ('approval_state', 'in', ['under_review', 'for_approval', 'for_authorization']),
                ('state', '!=', 'posted'),
            ])
            
            reminder_count = 0
            escalation_count = 0
            
            for payment in pending_payments:
                # Determine which date to use based on current state
                check_date = None
                
                if payment.approval_state == 'under_review':
                    # Check when it was submitted (created or state changed)
                    check_date = payment.create_date
                elif payment.approval_state == 'for_approval' and payment.reviewer_date:
                    check_date = payment.reviewer_date
                elif payment.approval_state == 'for_authorization' and payment.approver_date:
                    check_date = payment.approver_date
                
                if not check_date:
                    continue
                
                # Check if reminder is needed
                if check_date <= escalation_cutoff:
                    # Send escalation email
                    if self._should_send_escalation(payment):
                        payment._send_workflow_email('payment_account_enhanced.mail_template_approval_escalation')
                        self._log_reminder_sent(payment, 'escalation')
                        escalation_count += 1
                        
                elif check_date <= reminder_cutoff:
                    # Send reminder email
                    if self._should_send_reminder(payment):
                        payment._send_workflow_email('payment_account_enhanced.mail_template_approval_reminder')
                        self._log_reminder_sent(payment, 'reminder')
                        reminder_count += 1
            
            _logger.info(f"Sent {reminder_count} reminders and {escalation_count} escalations")
            
        except Exception as e:
            _logger.error(f"Error in send_approval_reminders: {str(e)}")

    def _should_send_reminder(self, payment):
        """Check if reminder should be sent (avoid spam)"""
        # Check if reminder was already sent today
        today = fields.Date.today()
        recent_reminders = self.env['mail.mail'].search([
            ('model', '=', 'account.payment'),
            ('res_id', '=', payment.id),
            ('subject', 'ilike', 'Approval Reminder'),
            ('date', '>=', today),
        ], limit=1)
        
        return not recent_reminders

    def _should_send_escalation(self, payment):
        """Check if escalation should be sent (avoid spam)"""
        # Check if escalation was already sent this week
        week_ago = fields.Date.today() - timedelta(days=7)
        recent_escalations = self.env['mail.mail'].search([
            ('model', '=', 'account.payment'),
            ('res_id', '=', payment.id),
            ('subject', 'ilike', 'Escalation'),
            ('date', '>=', week_ago),
        ], limit=1)
        
        return not recent_escalations

    def _log_reminder_sent(self, payment, reminder_type):
        """Log reminder in payment history"""
        payment.message_post(
            body=_("Automatic %s sent for pending approval") % reminder_type.title(),
            subtype_xmlid='mail.mt_note'
        )


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def get_pending_days(self):
        """Calculate how many days payment has been pending"""
        if not self.create_date:
            return 0
        
        check_date = self.create_date
        if self.approval_state == 'for_approval' and self.reviewer_date:
            check_date = self.reviewer_date
        elif self.approval_state == 'for_authorization' and self.approver_date:
            check_date = self.approver_date
        
        delta = datetime.now() - check_date
        return delta.days
