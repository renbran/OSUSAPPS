# -*- coding: utf-8 -*-
"""
Commission Alert System
=======================

World-class commission monitoring with intelligent alerts:
- Automated threshold monitoring
- Real-time notification system
- Escalation workflows
- Performance alerts
- Exception tracking
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class CommissionAlert(models.Model):
    """Commission Alert Management System"""
    _name = 'commission.alert'
    _description = 'Commission Alert'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc, priority desc'
    _rec_name = 'display_name'

    # Core fields
    name = fields.Char(string='Alert Name', required=True, tracking=True)
    display_name = fields.Char(string='Display Name', compute='_compute_display_name', store=True)
    alert_type = fields.Selection([
        ('threshold', 'Threshold Alert'),
        ('overdue', 'Overdue Payment'),
        ('anomaly', 'Anomaly Detection'),
        ('performance', 'Performance Alert'),
        ('approval', 'Approval Required'),
        ('system', 'System Alert'),
    ], string='Alert Type', required=True, tracking=True)

    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ], string='Priority', default='medium', required=True, tracking=True)

    state = fields.Selection([
        ('new', 'New'),
        ('acknowledged', 'Acknowledged'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    ], string='Status', default='new', required=True, tracking=True)

    # Alert content
    description = fields.Text(string='Description', required=True)
    details = fields.Html(string='Detailed Information')

    # Relationships
    commission_line_id = fields.Many2one('commission.line', string='Commission Line', ondelete='cascade')
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', ondelete='cascade')
    partner_id = fields.Many2one('res.partner', string='Commission Partner', ondelete='cascade')
    user_id = fields.Many2one('res.users', string='Assigned To', tracking=True)

    # Alert configuration
    threshold_value = fields.Float(string='Threshold Value')
    actual_value = fields.Float(string='Actual Value')
    variance_percentage = fields.Float(string='Variance %', compute='_compute_variance')

    # Dates
    alert_date = fields.Datetime(string='Alert Date', default=fields.Datetime.now, required=True)
    due_date = fields.Datetime(string='Due Date')
    resolved_date = fields.Datetime(string='Resolved Date', readonly=True)

    # Actions taken
    action_taken = fields.Text(string='Action Taken')
    resolution_notes = fields.Text(string='Resolution Notes')

    # Notification settings
    notify_users = fields.Many2many('res.users', string='Notify Users')
    email_sent = fields.Boolean(string='Email Sent', default=False)
    auto_escalate = fields.Boolean(string='Auto Escalate', default=True)
    escalation_hours = fields.Integer(string='Escalation Hours', default=24)

    @api.depends('name', 'alert_type', 'priority')
    def _compute_display_name(self):
        """Compute display name for alerts"""
        for alert in self:
            priority_icon = {
                'low': '🟢',
                'medium': '🟡',
                'high': '🟠',
                'critical': '🔴'
            }.get(alert.priority, '')
            alert.display_name = f"{priority_icon} {alert.name}"

    @api.depends('threshold_value', 'actual_value')
    def _compute_variance(self):
        """Compute variance percentage"""
        for alert in self:
            if alert.threshold_value and alert.actual_value:
                alert.variance_percentage = ((alert.actual_value - alert.threshold_value) / alert.threshold_value) * 100
            else:
                alert.variance_percentage = 0.0

    def action_acknowledge(self):
        """Acknowledge the alert"""
        self.write({
            'state': 'acknowledged',
            'user_id': self.env.user.id
        })
        self.message_post(
            body=f"Alert acknowledged by {self.env.user.name}",
            message_type='notification'
        )

    def action_start_progress(self):
        """Start working on the alert"""
        self.write({
            'state': 'in_progress',
            'user_id': self.env.user.id
        })
        self.message_post(
            body=f"Alert investigation started by {self.env.user.name}",
            message_type='notification'
        )

    def action_resolve(self):
        """Resolve the alert"""
        self.write({
            'state': 'resolved',
            'resolved_date': fields.Datetime.now()
        })
        self.message_post(
            body=f"Alert resolved by {self.env.user.name}",
            message_type='notification'
        )

    def action_dismiss(self):
        """Dismiss the alert"""
        self.write({'state': 'dismissed'})
        self.message_post(
            body=f"Alert dismissed by {self.env.user.name}",
            message_type='notification'
        )

    @api.model
    def create_threshold_alert(self, commission_line, threshold_type, threshold_value, actual_value):
        """Create a threshold alert"""
        alert_data = {
            'name': f'Commission {threshold_type.title()} Threshold Exceeded',
            'alert_type': 'threshold',
            'priority': 'high' if actual_value > threshold_value * 1.5 else 'medium',
            'description': f'Commission {threshold_type} of {actual_value:,.2f} exceeds threshold of {threshold_value:,.2f}',
            'commission_line_id': commission_line.id,
            'sale_order_id': commission_line.sale_order_id.id,
            'partner_id': commission_line.partner_id.id,
            'threshold_value': threshold_value,
            'actual_value': actual_value,
        }
        return self.create(alert_data)

    @api.model
    def create_overdue_alert(self, commission_line):
        """Create an overdue payment alert"""
        days_overdue = (fields.Date.today() - commission_line.expected_payment_date).days
        alert_data = {
            'name': f'Overdue Commission Payment ({days_overdue} days)',
            'alert_type': 'overdue',
            'priority': 'critical' if days_overdue > 30 else 'high',
            'description': f'Commission payment is {days_overdue} days overdue',
            'commission_line_id': commission_line.id,
            'sale_order_id': commission_line.sale_order_id.id,
            'partner_id': commission_line.partner_id.id,
            'due_date': commission_line.expected_payment_date,
        }
        return self.create(alert_data)

    @api.model
    def check_commission_thresholds(self):
        """Automated method to check commission thresholds"""
        try:
            # Get company threshold settings
            company = self.env.company
            threshold_amount = company.sudo().get_param('commission_threshold_amount', 10000.0)

            # Find high-value commissions
            high_value_commissions = self.env['commission.line'].search([
                ('amount', '>', threshold_amount),
                ('state', 'in', ['calculated', 'confirmed']),
            ])

            for commission in high_value_commissions:
                # Check if alert already exists
                existing_alert = self.search([
                    ('commission_line_id', '=', commission.id),
                    ('alert_type', '=', 'threshold'),
                    ('state', 'not in', ['resolved', 'dismissed'])
                ])

                if not existing_alert:
                    self.create_threshold_alert(commission, 'amount', threshold_amount, commission.amount)

            _logger.info(f"Commission threshold check completed. Found {len(high_value_commissions)} high-value commissions")

        except Exception as e:
            _logger.error(f"Error in commission threshold check: {str(e)}")

    @api.model
    def check_overdue_payments(self):
        """Automated method to check overdue payments"""
        try:
            # Find overdue commission payments
            overdue_commissions = self.env['commission.line'].search([
                ('expected_payment_date', '<', fields.Date.today()),
                ('state', 'in', ['confirmed', 'processed']),
                ('payment_status', '!=', 'paid'),
            ])

            for commission in overdue_commissions:
                # Check if alert already exists
                existing_alert = self.search([
                    ('commission_line_id', '=', commission.id),
                    ('alert_type', '=', 'overdue'),
                    ('state', 'not in', ['resolved', 'dismissed'])
                ])

                if not existing_alert:
                    self.create_overdue_alert(commission)

            _logger.info(f"Overdue payment check completed. Found {len(overdue_commissions)} overdue payments")

        except Exception as e:
            _logger.error(f"Error in overdue payment check: {str(e)}")

    def send_notification_email(self):
        """Send notification email for the alert"""
        if self.email_sent:
            return

        try:
            template = self.env.ref('commission_ax.commission_alert_email_template', raise_if_not_found=False)
            if template:
                template.send_mail(self.id, force_send=True)
                self.email_sent = True
                _logger.info(f"Alert notification email sent for alert {self.name}")
        except Exception as e:
            _logger.error(f"Failed to send alert notification email: {str(e)}")

    @api.model
    def auto_escalate_alerts(self):
        """Auto-escalate alerts based on configuration"""
        try:
            escalation_time = fields.Datetime.now() - timedelta(hours=24)
            alerts_to_escalate = self.search([
                ('state', '=', 'new'),
                ('auto_escalate', '=', True),
                ('alert_date', '<', escalation_time)
            ])

            for alert in alerts_to_escalate:
                # Escalate priority
                if alert.priority == 'low':
                    alert.priority = 'medium'
                elif alert.priority == 'medium':
                    alert.priority = 'high'
                elif alert.priority == 'high':
                    alert.priority = 'critical'

                # Send escalation notification
                alert.message_post(
                    body=f"Alert auto-escalated to {alert.priority} priority due to no action taken",
                    message_type='notification'
                )

            _logger.info(f"Auto-escalated {len(alerts_to_escalate)} alerts")

        except Exception as e:
            _logger.error(f"Error in alert auto-escalation: {str(e)}")