# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    calendar_preferences = fields.Text(
        string='Calendar Preferences',
        help='JSON data for calendar preferences'
    )
    
    default_event_duration = fields.Float(
        string='Default Event Duration (Hours)',
        default=1.0,
        help='Default duration for events created by this partner'
    )
    
    calendar_timezone = fields.Selection(
        related='tz',
        string='Calendar Timezone'
    )
    
    calendar_view_mode = fields.Selection([
        ('month', 'Month'),
        ('week', 'Week'),
        ('day', 'Day'),
        ('year', 'Year')
    ], string='Preferred Calendar View', default='month')
    
    calendar_notifications = fields.Boolean(
        string='Calendar Notifications',
        default=True,
        help='Receive calendar notifications'
    )
    
    calendar_reminder_default = fields.Integer(
        string='Default Reminder (Minutes)',
        default=15,
        help='Default reminder time in minutes'
    )
    
    calendar_working_hours = fields.Text(
        string='Working Hours',
        help='JSON data for working hours'
    )
    
    event_count = fields.Integer(
        string='Event Count',
        compute='_compute_event_count'
    )
    
    @api.depends()
    def _compute_event_count(self):
        for partner in self:
            partner.event_count = self.env['calendar.event'].search_count([
                ('partner_ids', 'in', partner.id)
            ])
    
    def action_view_calendar_events(self):
        """View calendar events for this partner"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Calendar Events',
            'res_model': 'calendar.event',
            'view_mode': 'calendar,tree,form',
            'domain': [('partner_ids', 'in', self.id)],
            'context': {'default_partner_ids': [(6, 0, [self.id])]}
        }
