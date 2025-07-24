# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class CalendarReminder(models.Model):
    _name = 'calendar.reminder'
    _description = 'Calendar Event Reminder'
    _order = 'reminder_time desc'

    event_id = fields.Many2one(
        'calendar.event',
        string='Event',
        required=True,
        ondelete='cascade'
    )
    
    reminder_type = fields.Selection([
        ('email', 'Email'),
        ('popup', 'Popup'),
        ('sms', 'SMS'),
        ('push', 'Push Notification')
    ], string='Reminder Type', required=True, default='email')
    
    reminder_time = fields.Datetime(
        string='Reminder Time',
        required=True
    )
    
    minutes_before = fields.Integer(
        string='Minutes Before Event',
        help='Minutes before event to send reminder'
    )
    
    message = fields.Text(string='Custom Message')
    
    is_sent = fields.Boolean(string='Sent', default=False)
    
    sent_date = fields.Datetime(string='Sent Date')
    
    recipient_ids = fields.Many2many(
        'res.partner',
        string='Recipients',
        help='Specific recipients for this reminder'
    )
    
    template_id = fields.Many2one(
        'mail.template',
        string='Email Template'
    )
    
    @api.model
    def send_due_reminders(self):
        """Cron job to send due reminders"""
        now = fields.Datetime.now()
        due_reminders = self.search([
            ('reminder_time', '<=', now),
            ('is_sent', '=', False)
        ])
        
        for reminder in due_reminders:
            reminder._send_reminder()
    
    def _send_reminder(self):
        """Send the reminder"""
        self.ensure_one()
        
        if self.reminder_type == 'email':
            self._send_email_reminder()
        elif self.reminder_type == 'popup':
            self._send_popup_reminder()
        elif self.reminder_type == 'sms':
            self._send_sms_reminder()
        elif self.reminder_type == 'push':
            self._send_push_reminder()
        
        self.is_sent = True
        self.sent_date = fields.Datetime.now()
    
    def _send_email_reminder(self):
        """Send email reminder"""
        template = self.template_id or self.env.ref(
            'calendar_extended.email_template_event_reminder',
            raise_if_not_found=False
        )
        
        if template:
            recipients = self.recipient_ids or self.event_id.partner_ids
            for recipient in recipients:
                template.send_mail(self.event_id.id, force_send=True)
    
    def _send_popup_reminder(self):
        """Send popup reminder"""
        # Implementation for popup reminder
        pass
    
    def _send_sms_reminder(self):
        """Send SMS reminder"""
        # Implementation for SMS reminder
        pass
    
    def _send_push_reminder(self):
        """Send push notification reminder"""
        # Implementation for push notification
        pass
