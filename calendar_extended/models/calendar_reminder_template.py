# -*- coding: utf-8 -*-
from odoo import models, fields

class CalendarReminderTemplate(models.Model):
    _name = 'calendar.reminder.template'
    _description = 'Calendar Reminder Template'

    name = fields.Char('Template Name', required=True)
    reminder_type = fields.Selection([
        ('email', 'Email'),
        ('notification', 'Notification')
    ], string='Reminder Type', required=True)
    minutes = fields.Integer('Minutes Before', default=30)
    active = fields.Boolean('Active', default=True)
