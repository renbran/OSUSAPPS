# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class CalendarRecurrence(models.Model):
    _inherit = 'calendar.recurrence'

    # Extended recurrence patterns
    recurrence_pattern = fields.Selection(
        selection_add=[
            ('custom', 'Custom Pattern'),
            ('business_days', 'Business Days'),
            ('first_monday', 'First Monday of Month'),
            ('last_friday', 'Last Friday of Month'),
        ]
    )
    
    custom_pattern = fields.Char(
        string='Custom Pattern',
        help='Custom recurrence pattern in cron format'
    )
    
    exclude_weekends = fields.Boolean(
        string='Exclude Weekends',
        help='Skip weekends in recurrence'
    )
    
    exclude_holidays = fields.Boolean(
        string='Exclude Holidays',
        help='Skip public holidays in recurrence'
    )
    
    max_occurrences = fields.Integer(
        string='Max Occurrences',
        help='Maximum number of occurrences'
    )
    
    occurrence_count = fields.Integer(
        string='Current Occurrences',
        compute='_compute_occurrence_count'
    )
    
    @api.depends('calendar_event_ids')
    def _compute_occurrence_count(self):
        for recurrence in self:
            recurrence.occurrence_count = len(recurrence.calendar_event_ids)
    
    @api.constrains('max_occurrences', 'occurrence_count')
    def _check_max_occurrences(self):
        for recurrence in self:
            if (recurrence.max_occurrences > 0 and 
                recurrence.occurrence_count > recurrence.max_occurrences):
                raise ValidationError(
                    _('Number of occurrences cannot exceed the maximum limit.')
                )


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
    def _compute_reminder_time(self, event_start, minutes_before):
        """Compute reminder time based on event start and minutes before"""
        return event_start - timedelta(minutes=minutes_before)
    
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


class CalendarReminderTemplate(models.Model):
    _name = 'calendar.reminder.template'
    _description = 'Calendar Reminder Template'
    _order = 'name'

    name = fields.Char(string='Template Name', required=True)
    
    reminder_type = fields.Selection([
        ('email', 'Email'),
        ('popup', 'Popup'),
        ('sms', 'SMS'),
        ('push', 'Push Notification')
    ], string='Reminder Type', required=True, default='email')
    
    minutes_before = fields.Integer(
        string='Minutes Before Event',
        required=True,
        default=15
    )
    
    message_template = fields.Text(
        string='Message Template',
        help='Template for reminder message'
    )
    
    email_template_id = fields.Many2one(
        'mail.template',
        string='Email Template'
    )
    
    active = fields.Boolean(string='Active', default=True)
    
    def create_reminder(self, event_id):
        """Create reminder from template"""
        event = self.env['calendar.event'].browse(event_id)
        reminder_time = self.env['calendar.reminder']._compute_reminder_time(
            event.start, self.minutes_before
        )
        
        return self.env['calendar.reminder'].create({
            'event_id': event_id,
            'reminder_type': self.reminder_type,
            'reminder_time': reminder_time,
            'minutes_before': self.minutes_before,
            'message': self.message_template,
            'template_id': self.email_template_id.id if self.email_template_id else False,
        })
