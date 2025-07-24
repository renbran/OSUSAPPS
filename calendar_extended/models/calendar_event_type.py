# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class CalendarEventType(models.Model):
    _name = 'calendar.event.type'
    _description = 'Calendar Event Type'
    _order = 'sequence, name'

    name = fields.Char(string='Name', required=True, translate=True)
    
    description = fields.Text(string='Description', translate=True)
    
    color = fields.Integer(string='Color', default=0, help='Color index for calendar display')
    
    color_code = fields.Char(string='Color Code', help='Hex color code')
    
    sequence = fields.Integer(string='Sequence', default=10)
    
    active = fields.Boolean(string='Active', default=True)
    
    icon = fields.Char(string='Icon', help='Font Awesome icon class')
    
    default_duration = fields.Float(
        string='Default Duration (Hours)',
        default=1.0,
        help='Default duration for events of this type'
    )
    
    requires_approval = fields.Boolean(
        string='Requires Approval',
        help='Events of this type require approval'
    )
    
    approver_ids = fields.Many2many(
        'res.users',
        string='Approvers',
        help='Users who can approve events of this type'
    )
    
    default_location = fields.Char(string='Default Location')
    
    max_attendees = fields.Integer(
        string='Max Attendees',
        help='Maximum number of attendees for this event type'
    )
    
    reminder_template_ids = fields.Many2many(
        'calendar.reminder.template',
        string='Default Reminders',
        help='Default reminder templates for this event type'
    )
    
    is_public = fields.Boolean(
        string='Public by Default',
        help='Events of this type are public by default'
    )
    
    event_count = fields.Integer(
        string='Event Count',
        compute='_compute_event_count'
    )
    
    @api.depends()
    def _compute_event_count(self):
        for event_type in self:
            event_type.event_count = self.env['calendar.event'].search_count([
                ('event_type_id', '=', event_type.id)
            ])
    
    def action_view_events(self):
        """View events of this type"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Events'),
            'res_model': 'calendar.event',
            'view_mode': 'calendar,tree,form',
            'domain': [('event_type_id', '=', self.id)],
            'context': {'default_event_type_id': self.id}
        }
