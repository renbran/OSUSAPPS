# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class CalendarEventWizard(models.TransientModel):
    _name = 'calendar.event.wizard'
    _description = 'Calendar Event Creation Wizard'

    template_id = fields.Many2one(
        'calendar.template',
        string='Event Template',
        help='Select a template to pre-fill event details'
    )
    
    name = fields.Char(string='Event Name', required=True)
    
    description = fields.Html(string='Description')
    
    start = fields.Datetime(string='Start Date', required=True)
    
    stop = fields.Datetime(string='End Date', required=True)
    
    duration = fields.Float(
        string='Duration (Hours)',
        compute='_compute_duration',
        inverse='_inverse_duration',
        store=True
    )
    
    event_type_id = fields.Many2one(
        'calendar.event.type',
        string='Event Type'
    )
    
    location = fields.Char(string='Location')
    
    location_type = fields.Selection([
        ('physical', 'Physical Location'),
        ('online', 'Online Meeting'),
        ('hybrid', 'Hybrid')
    ], string='Location Type', default='physical')
    
    meeting_url = fields.Char(string='Meeting URL')
    
    partner_ids = fields.Many2many(
        'res.partner',
        string='Attendees'
    )
    
    resource_ids = fields.Many2many(
        'calendar.resource',
        string='Resources'
    )
    
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Urgent')
    ], string='Priority', default='1')
    
    is_public = fields.Boolean(string='Public Event')
    
    recurrence_id = fields.Many2one(
        'calendar.recurrence',
        string='Recurrence'
    )
    
    create_recurrence = fields.Boolean(string='Create Recurrence')
    
    recurrence_type = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly')
    ], string='Recurrence Type')
    
    recurrence_interval = fields.Integer(
        string='Repeat Every',
        default=1
    )
    
    recurrence_end_type = fields.Selection([
        ('count', 'Number of repetitions'),
        ('end_date', 'End date')
    ], string='End Type', default='count')
    
    recurrence_count = fields.Integer(string='Repetitions', default=1)
    
    recurrence_end_date = fields.Date(string='Until')
    
    reminder_ids = fields.One2many(
        'calendar.event.wizard.reminder',
        'wizard_id',
        string='Reminders'
    )
    
    @api.depends('start', 'stop')
    def _compute_duration(self):
        for wizard in self:
            if wizard.start and wizard.stop:
                duration_delta = wizard.stop - wizard.start
                wizard.duration = duration_delta.total_seconds() / 3600
            else:
                wizard.duration = 1.0
    
    def _inverse_duration(self):
        for wizard in self:
            if wizard.start and wizard.duration:
                wizard.stop = wizard.start + timedelta(hours=wizard.duration)
    
    @api.onchange('template_id')
    def _onchange_template_id(self):
        if self.template_id:
            template_values = self.template_id._get_event_values()
            for field, value in template_values.items():
                if hasattr(self, field):
                    setattr(self, field, value)
    
    @api.onchange('event_type_id')
    def _onchange_event_type_id(self):
        if self.event_type_id:
            if self.event_type_id.default_duration:
                self.duration = self.event_type_id.default_duration
            if self.event_type_id.default_location:
                self.location = self.event_type_id.default_location
    
    @api.constrains('start', 'stop')
    def _check_dates(self):
        for wizard in self:
            if wizard.start and wizard.stop and wizard.start >= wizard.stop:
                raise ValidationError(_('Start date must be before end date.'))
    
    def action_create_event(self):
        """Create event from wizard"""
        self.ensure_one()
        
        # Check resource availability
        if self.resource_ids:
            for resource in self.resource_ids:
                if not resource.check_availability(self.start, self.stop):
                    raise ValidationError(
                        _('Resource "%s" is not available for the selected time.') % resource.name
                    )
        
        # Create event
        event_vals = {
            'name': self.name,
            'description': self.description,
            'start': self.start,
            'stop': self.stop,
            'event_type_id': self.event_type_id.id if self.event_type_id else False,
            'location': self.location,
            'location_type': self.location_type,
            'meeting_url': self.meeting_url,
            'partner_ids': [(6, 0, self.partner_ids.ids)],
            'resource_ids': [(6, 0, self.resource_ids.ids)],
            'priority': self.priority,
            'is_public': self.is_public,
            'template_id': self.template_id.id if self.template_id else False,
        }
        
        event = self.env['calendar.event'].create(event_vals)
        
        # Create recurrence if requested
        if self.create_recurrence and self.recurrence_type:
            recurrence_vals = {
                'rrule_type': self.recurrence_type,
                'interval': self.recurrence_interval,
                'calendar_event_ids': [(6, 0, [event.id])],
            }
            
            if self.recurrence_end_type == 'count':
                recurrence_vals['count'] = self.recurrence_count
            else:
                recurrence_vals['until'] = self.recurrence_end_date
            
            self.env['calendar.recurrence'].create(recurrence_vals)
        
        # Create reminders
        for reminder_line in self.reminder_ids:
            self.env['calendar.reminder'].create({
                'event_id': event.id,
                'reminder_type': reminder_line.reminder_type,
                'minutes_before': reminder_line.minutes_before,
                'message': reminder_line.message,
            })
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Event Created'),
            'res_model': 'calendar.event',
            'res_id': event.id,
            'view_mode': 'form',
            'target': 'current',
        }


class CalendarEventWizardReminder(models.TransientModel):
    _name = 'calendar.event.wizard.reminder'
    _description = 'Calendar Event Wizard Reminder'

    wizard_id = fields.Many2one(
        'calendar.event.wizard',
        string='Wizard',
        required=True,
        ondelete='cascade'
    )
    
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
    
    message = fields.Text(string='Custom Message')
