# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    # Extended fields
    event_type_id = fields.Many2one(
        'calendar.event.type',
        string='Event Type',
        help='Categorize events by type'
    )
    
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Urgent')
    ], string='Priority', default='1')
    
    location_type = fields.Selection([
        ('physical', 'Physical Location'),
        ('online', 'Online Meeting'),
        ('hybrid', 'Hybrid')
    ], string='Location Type', default='physical')
    
    meeting_url = fields.Char(string='Meeting URL')
    meeting_id = fields.Char(string='Meeting ID')
    meeting_password = fields.Char(string='Meeting Password')
    
    resource_ids = fields.Many2many(
        'calendar.resource',
        string='Resources',
        help='Resources required for this event'
    )
    
    template_id = fields.Many2one(
        'calendar.template',
        string='Event Template',
        help='Template used to create this event'
    )
    
    is_template = fields.Boolean(
        string='Is Template',
        help='Mark this event as a template'
    )
    
    reminder_ids = fields.One2many(
        'calendar.reminder',
        'event_id',
        string='Reminders'
    )
    
    tags = fields.Char(string='Tags', help='Comma-separated tags')
    
    color_code = fields.Char(
        string='Color Code',
        help='Hex color code for event display'
    )
    
    estimated_duration = fields.Float(
        string='Estimated Duration (Hours)',
        help='Estimated duration in hours'
    )
    
    actual_duration = fields.Float(
        string='Actual Duration (Hours)',
        help='Actual duration in hours'
    )
    
    budget = fields.Monetary(
        string='Budget',
        currency_field='currency_id',
        help='Budget allocated for this event'
    )
    
    actual_cost = fields.Monetary(
        string='Actual Cost',
        currency_field='currency_id',
        help='Actual cost of the event'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )
    
    status = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('postponed', 'Postponed')
    ], string='Status', default='draft')
    
    is_public = fields.Boolean(
        string='Public Event',
        help='Make this event visible to all users'
    )
    
    max_attendees = fields.Integer(
        string='Maximum Attendees',
        help='Maximum number of attendees allowed'
    )
    
    current_attendees = fields.Integer(
        string='Current Attendees',
        compute='_compute_current_attendees',
        store=True
    )
    
    registration_deadline = fields.Datetime(
        string='Registration Deadline',
        help='Last date for registration'
    )
    
    requires_approval = fields.Boolean(
        string='Requires Approval',
        help='Event needs approval before confirmation'
    )
    
    approved_by = fields.Many2one(
        'res.users',
        string='Approved By'
    )
    
    approval_date = fields.Datetime(string='Approval Date')
    
    feedback_ids = fields.One2many(
        'calendar.event.feedback',
        'event_id',
        string='Feedback'
    )
    
    average_rating = fields.Float(
        string='Average Rating',
        compute='_compute_average_rating',
        store=True
    )
    
    # Computed fields
    @api.depends('partner_ids')
    def _compute_current_attendees(self):
        for event in self:
            event.current_attendees = len(event.partner_ids)
    
    @api.depends('feedback_ids.rating')
    def _compute_average_rating(self):
        for event in self:
            if event.feedback_ids:
                event.average_rating = sum(event.feedback_ids.mapped('rating')) / len(event.feedback_ids)
            else:
                event.average_rating = 0.0
    
    @api.constrains('max_attendees', 'current_attendees')
    def _check_attendees_limit(self):
        for event in self:
            if event.max_attendees > 0 and event.current_attendees > event.max_attendees:
                raise ValidationError(_('Number of attendees cannot exceed the maximum limit.'))
    
    @api.constrains('start', 'stop', 'registration_deadline')
    def _check_dates(self):
        for event in self:
            if event.start and event.stop and event.start >= event.stop:
                raise ValidationError(_('Start date must be before end date.'))
            if event.registration_deadline and event.start and event.registration_deadline >= event.start:
                raise ValidationError(_('Registration deadline must be before event start date.'))
    
    def action_confirm(self):
        """Confirm the event"""
        for event in self:
            if event.requires_approval and not event.approved_by:
                raise UserError(_('This event requires approval before confirmation.'))
            event.status = 'confirmed'
            event._send_confirmation_notification()
    
    def action_start(self):
        """Mark event as in progress"""
        for event in self:
            event.status = 'in_progress'
    
    def action_complete(self):
        """Mark event as completed"""
        for event in self:
            event.status = 'completed'
            event._create_feedback_requests()
    
    def action_cancel(self):
        """Cancel the event"""
        for event in self:
            event.status = 'cancelled'
            event._send_cancellation_notification()
    
    def action_postpone(self):
        """Postpone the event"""
        for event in self:
            event.status = 'postponed'
    
    def action_approve(self):
        """Approve the event"""
        for event in self:
            event.approved_by = self.env.user
            event.approval_date = fields.Datetime.now()
            if event.status == 'draft':
                event.status = 'confirmed'
    
    def _send_confirmation_notification(self):
        """Send confirmation notification to attendees"""
        template = self.env.ref('calendar_extended.email_template_event_confirmation', raise_if_not_found=False)
        if template:
            for partner in self.partner_ids:
                template.send_mail(self.id, force_send=True)
    
    def _send_cancellation_notification(self):
        """Send cancellation notification to attendees"""
        template = self.env.ref('calendar_extended.email_template_event_cancellation', raise_if_not_found=False)
        if template:
            for partner in self.partner_ids:
                template.send_mail(self.id, force_send=True)
    
    def _create_feedback_requests(self):
        """Create feedback requests for attendees"""
        feedback_obj = self.env['calendar.event.feedback']
        for partner in self.partner_ids:
            feedback_obj.create({
                'event_id': self.id,
                'partner_id': partner.id,
                'state': 'draft'
            })
    
    @api.model
    def create_from_template(self, template_id, values):
        """Create event from template"""
        template = self.env['calendar.template'].browse(template_id)
        event_values = template._get_event_values()
        event_values.update(values)
        return self.create(event_values)
    
    def duplicate_event(self, new_date=None):
        """Duplicate event with new date"""
        self.ensure_one()
        values = self.copy_data()[0]
        if new_date:
            duration = self.stop - self.start
            values.update({
                'start': new_date,
                'stop': new_date + duration,
            })
        return self.create(values)


class CalendarEventFeedback(models.Model):
    _name = 'calendar.event.feedback'
    _description = 'Calendar Event Feedback'
    _order = 'create_date desc'

    event_id = fields.Many2one(
        'calendar.event',
        string='Event',
        required=True,
        ondelete='cascade'
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Attendee',
        required=True
    )
    
    rating = fields.Selection([
        ('1', '1 - Poor'),
        ('2', '2 - Fair'),
        ('3', '3 - Good'),
        ('4', '4 - Very Good'),
        ('5', '5 - Excellent')
    ], string='Rating', required=True)
    
    comments = fields.Text(string='Comments')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted')
    ], string='State', default='draft')
    
    submit_date = fields.Datetime(string='Submit Date')
    
    def action_submit(self):
        """Submit feedback"""
        self.state = 'submitted'
        self.submit_date = fields.Datetime.now()
