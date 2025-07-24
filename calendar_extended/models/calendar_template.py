# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class CalendarTemplate(models.Model):
    _name = 'calendar.template'
    _description = 'Calendar Event Template'
    _order = 'name'

    name = fields.Char(string='Template Name', required=True)
    
    description = fields.Text(string='Description')
    
    event_type_id = fields.Many2one(
        'calendar.event.type',
        string='Event Type',
        required=True
    )
    
    duration = fields.Float(
        string='Duration (Hours)',
        default=1.0,
        required=True
    )
    
    location = fields.Char(string='Default Location')
    
    location_type = fields.Selection([
        ('physical', 'Physical Location'),
        ('online', 'Online Meeting'),
        ('hybrid', 'Hybrid')
    ], string='Location Type', default='physical')
    
    default_attendee_ids = fields.Many2many(
        'res.partner',
        string='Default Attendees',
        help='Default attendees for events created from this template'
    )
    
    resource_ids = fields.Many2many(
        'calendar.resource',
        string='Required Resources'
    )
    
    agenda = fields.Html(string='Default Agenda')
    
    preparation_notes = fields.Text(string='Preparation Notes')
    
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Urgent')
    ], string='Default Priority', default='1')
    
    is_public = fields.Boolean(string='Public Template', default=False)
    
    category = fields.Selection([
        ('meeting', 'Meeting'),
        ('workshop', 'Workshop'),
        ('training', 'Training'),
        ('conference', 'Conference'),
        ('social', 'Social Event'),
        ('other', 'Other')
    ], string='Category', default='meeting')
    
    reminder_template_ids = fields.Many2many(
        'calendar.reminder.template',
        string='Reminder Templates'
    )
    
    checklist_ids = fields.One2many(
        'calendar.template.checklist',
        'template_id',
        string='Checklist Items'
    )
    
    usage_count = fields.Integer(
        string='Usage Count',
        compute='_compute_usage_count'
    )
    
    active = fields.Boolean(string='Active', default=True)
    
    @api.depends()
    def _compute_usage_count(self):
        for template in self:
            template.usage_count = self.env['calendar.event'].search_count([
                ('template_id', '=', template.id)
            ])
    
    def _get_event_values(self):
        """Get values for creating event from template"""
        self.ensure_one()
        return {
            'name': self.name,
            'description': self.description,
            'event_type_id': self.event_type_id.id,
            'location': self.location,
            'location_type': self.location_type,
            'partner_ids': [(6, 0, self.default_attendee_ids.ids)],
            'resource_ids': [(6, 0, self.resource_ids.ids)],
            'priority': self.priority,
            'is_public': self.is_public,
            'template_id': self.id,
        }
    
    def action_create_event(self):
        """Create event from template"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Create Event from Template'),
            'res_model': 'calendar.event.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_template_id': self.id,
                **self._get_event_values()
            }
        }
    
    def action_view_events(self):
        """View events created from this template"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Events from Template'),
            'res_model': 'calendar.event',
            'view_mode': 'calendar,tree,form',
            'domain': [('template_id', '=', self.id)],
            'context': {'default_template_id': self.id}
        }


class CalendarTemplateChecklist(models.Model):
    _name = 'calendar.template.checklist'
    _description = 'Calendar Template Checklist'
    _order = 'sequence, name'

    name = fields.Char(string='Item', required=True)
    
    description = fields.Text(string='Description')
    
    template_id = fields.Many2one(
        'calendar.template',
        string='Template',
        required=True,
        ondelete='cascade'
    )
    
    sequence = fields.Integer(string='Sequence', default=10)
    
    is_mandatory = fields.Boolean(string='Mandatory', default=False)
    
    responsible_role = fields.Selection([
        ('organizer', 'Organizer'),
        ('attendee', 'Attendee'),
        ('admin', 'Administrator'),
        ('any', 'Anyone')
    ], string='Responsible Role', default='organizer')
    
    deadline_before_event = fields.Integer(
        string='Deadline (Hours Before Event)',
        help='How many hours before the event this item should be completed'
    )
