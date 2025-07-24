# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class CalendarInternalMeeting(models.Model):
    _name = 'calendar.internal.meeting'
    _description = 'Internal Meeting Booking'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(string='Meeting Subject', required=True, tracking=True)
    
    description = fields.Html(string='Meeting Description', tracking=True)
    
    organizer_id = fields.Many2one(
        'res.users',
        string='Organizer',
        required=True,
        default=lambda self: self.env.user,
        tracking=True
    )
    
    start_datetime = fields.Datetime(
        string='Start Date & Time',
        required=True,
        tracking=True
    )
    
    end_datetime = fields.Datetime(
        string='End Date & Time',
        required=True,
        tracking=True
    )
    
    duration = fields.Float(
        string='Duration (Hours)',
        compute='_compute_duration',
        store=True
    )
    
    location = fields.Char(string='Location', tracking=True)
    
    meeting_type = fields.Selection([
        ('team_meeting', 'Team Meeting'),
        ('department_meeting', 'Department Meeting'),
        ('project_review', 'Project Review'),
        ('training', 'Training Session'),
        ('brainstorming', 'Brainstorming'),
        ('one_on_one', 'One-on-One'),
        ('all_hands', 'All Hands Meeting'),
        ('other', 'Other')
    ], string='Meeting Type', default='team_meeting', tracking=True)
    
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Urgent')
    ], string='Priority', default='1', tracking=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending_approval', 'Pending Approval'),
        ('approved', 'Approved'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rejected', 'Rejected')
    ], string='Status', default='draft', tracking=True)
    
    # Attendees
    attendee_ids = fields.Many2many(
        'hr.employee',
        'calendar_internal_meeting_attendee_rel',
        'meeting_id',
        'employee_id',
        string='Attendees',
        tracking=True
    )
    
    department_ids = fields.Many2many(
        'hr.department',
        'calendar_internal_meeting_department_rel',
        'meeting_id',
        'department_id',
        string='Departments',
        help='Select departments to invite all employees',
        tracking=True
    )
    
    job_position_ids = fields.Many2many(
        'hr.job',
        'calendar_internal_meeting_job_rel',
        'meeting_id',
        'job_id',
        string='Job Positions',
        help='Select job positions to invite employees',
        tracking=True
    )
    
    # Approval workflow
    requires_approval = fields.Boolean(
        string='Requires Approval',
        compute='_compute_requires_approval',
        store=True
    )
    
    approver_id = fields.Many2one(
        'res.users',
        string='Approver',
        tracking=True
    )
    
    approval_date = fields.Datetime(string='Approval Date')
    
    approval_notes = fields.Text(string='Approval Notes')
    
    # Resources
    room_id = fields.Many2one(
        'calendar.resource',
        string='Meeting Room',
        domain=[('resource_type', '=', 'room')],
        tracking=True
    )
    
    equipment_ids = fields.Many2many(
        'calendar.resource',
        'calendar_internal_meeting_equipment_rel',
        'meeting_id',
        'resource_id',
        string='Required Equipment',
        domain=[('resource_type', '=', 'equipment')]
    )
    
    # Additional fields
    agenda = fields.Html(string='Agenda')
    
    preparation_notes = fields.Text(string='Preparation Notes')
    
    max_attendees = fields.Integer(string='Maximum Attendees')
    
    current_attendees_count = fields.Integer(
        string='Current Attendees',
        compute='_compute_attendees_count',
        store=True
    )
    
    is_recurring = fields.Boolean(string='Recurring Meeting')
    
    recurrence_pattern = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly')
    ], string='Recurrence Pattern')
    
    recurrence_count = fields.Integer(string='Number of Occurrences', default=1)
    
    # Calendar event reference
    calendar_event_id = fields.Many2one(
        'calendar.event',
        string='Calendar Event',
        readonly=True
    )
    
    # Computed fields
    @api.depends('start_datetime', 'end_datetime')
    def _compute_duration(self):
        for meeting in self:
            if meeting.start_datetime and meeting.end_datetime:
                delta = meeting.end_datetime - meeting.start_datetime
                meeting.duration = delta.total_seconds() / 3600
            else:
                meeting.duration = 0.0
    
    @api.depends('attendee_ids', 'department_ids', 'job_position_ids')
    def _compute_attendees_count(self):
        for meeting in self:
            count = len(meeting.attendee_ids)
            
            # Add department employees
            for dept in meeting.department_ids:
                count += len(dept.member_ids)
            
            # Add job position employees
            for job in meeting.job_position_ids:
                count += len(job.employee_ids)
            
            meeting.current_attendees_count = count
    
    @api.depends('meeting_type', 'current_attendees_count', 'room_id')
    def _compute_requires_approval(self):
        for meeting in self:
            # Define approval rules
            approval_needed = False
            
            # Large meetings need approval
            if meeting.current_attendees_count > 10:
                approval_needed = True
            
            # Certain meeting types need approval
            if meeting.meeting_type in ['all_hands', 'department_meeting']:
                approval_needed = True
            
            # Meetings requiring expensive resources need approval
            if meeting.room_id and meeting.room_id.hourly_rate > 50:
                approval_needed = True
            
            meeting.requires_approval = approval_needed
    
    @api.constrains('start_datetime', 'end_datetime')
    def _check_meeting_dates(self):
        for meeting in self:
            if meeting.start_datetime and meeting.end_datetime:
                if meeting.start_datetime >= meeting.end_datetime:
                    raise ValidationError(_('Start date must be before end date.'))
    
    @api.constrains('max_attendees', 'current_attendees_count')
    def _check_attendees_limit(self):
        for meeting in self:
            if (meeting.max_attendees > 0 and 
                meeting.current_attendees_count > meeting.max_attendees):
                raise ValidationError(
                    _('Number of attendees (%d) exceeds maximum limit (%d).') % 
                    (meeting.current_attendees_count, meeting.max_attendees)
                )
    
    @api.onchange('department_ids')
    def _onchange_department_ids(self):
        """Auto-set approver based on department manager"""
        if self.department_ids:
            # Get the manager of the first department as default approver
            dept = self.department_ids[0]
            if dept.manager_id and dept.manager_id.user_id:
                self.approver_id = dept.manager_id.user_id
    
    def action_submit_for_approval(self):
        """Submit meeting for approval"""
        for meeting in self:
            if not meeting.requires_approval:
                # Auto-approve if no approval needed
                meeting.action_approve()
            else:
                if not meeting.approver_id:
                    raise UserError(_('Please select an approver for this meeting.'))
                meeting.state = 'pending_approval'
                meeting._send_approval_request()
    
    def action_approve(self):
        """Approve the meeting"""
        for meeting in self:
            if meeting.requires_approval and self.env.user != meeting.approver_id:
                raise UserError(_('Only the designated approver can approve this meeting.'))
            
            meeting.state = 'approved'
            meeting.approval_date = fields.Datetime.now()
            meeting._create_calendar_event()
            meeting._send_meeting_invitations()
    
    def action_reject(self):
        """Reject the meeting"""
        for meeting in self:
            if meeting.requires_approval and self.env.user != meeting.approver_id:
                raise UserError(_('Only the designated approver can reject this meeting.'))
            
            meeting.state = 'rejected'
            meeting._send_rejection_notification()
    
    def action_confirm(self):
        """Confirm the meeting"""
        for meeting in self:
            if meeting.state not in ['approved']:
                raise UserError(_('Only approved meetings can be confirmed.'))
            meeting.state = 'confirmed'
    
    def action_start(self):
        """Start the meeting"""
        for meeting in self:
            meeting.state = 'in_progress'
    
    def action_complete(self):
        """Complete the meeting"""
        for meeting in self:
            meeting.state = 'completed'
    
    def action_cancel(self):
        """Cancel the meeting"""
        for meeting in self:
            meeting.state = 'cancelled'
            if meeting.calendar_event_id:
                meeting.calendar_event_id.unlink()
            meeting._send_cancellation_notification()
    
    def _create_calendar_event(self):
        """Create calendar event from internal meeting"""
        self.ensure_one()
        
        # Get all attendees
        attendees = self._get_all_attendees()
        partner_ids = attendees.mapped('user_id.partner_id').ids
        
        event_vals = {
            'name': self.name,
            'description': self.description,
            'start': self.start_datetime,
            'stop': self.end_datetime,
            'location': self.location,
            'partner_ids': [(6, 0, partner_ids)],
            'user_id': self.organizer_id.id,
        }
        
        if self.room_id:
            event_vals['resource_ids'] = [(6, 0, [self.room_id.id])]
        
        calendar_event = self.env['calendar.event'].create(event_vals)
        self.calendar_event_id = calendar_event.id
        
        return calendar_event
    
    def _get_all_attendees(self):
        """Get all attendees including department and job position employees"""
        attendees = self.attendee_ids
        
        # Add department employees
        for dept in self.department_ids:
            attendees |= dept.member_ids
        
        # Add job position employees
        for job in self.job_position_ids:
            attendees |= job.employee_ids
        
        return attendees
    
    def _send_approval_request(self):
        """Send approval request notification"""
        template = self.env.ref(
            'calendar_extended.email_template_meeting_approval_request',
            raise_if_not_found=False
        )
        if template and self.approver_id:
            template.send_mail(self.id, force_send=True)
    
    def _send_meeting_invitations(self):
        """Send meeting invitations to attendees"""
        template = self.env.ref(
            'calendar_extended.email_template_meeting_invitation',
            raise_if_not_found=False
        )
        if template:
            attendees = self._get_all_attendees()
            for attendee in attendees:
                if attendee.user_id:
                    template.send_mail(self.id, force_send=True)
    
    def _send_rejection_notification(self):
        """Send rejection notification"""
        template = self.env.ref(
            'calendar_extended.email_template_meeting_rejection',
            raise_if_not_found=False
        )
        if template:
            template.send_mail(self.id, force_send=True)
    
    def _send_cancellation_notification(self):
        """Send cancellation notification"""
        template = self.env.ref(
            'calendar_extended.email_template_meeting_cancellation',
            raise_if_not_found=False
        )
        if template:
            attendees = self._get_all_attendees()
            for attendee in attendees:
                if attendee.user_id:
                    template.send_mail(self.id, force_send=True)
    
    @api.model
    def create_recurring_meetings(self):
        """Create recurring meetings based on pattern"""
        recurring_meetings = self.search([
            ('is_recurring', '=', True),
            ('state', 'in', ['approved', 'confirmed'])
        ])
        
        for meeting in recurring_meetings:
            meeting._create_next_occurrence()
    
    def _create_next_occurrence(self):
        """Create next occurrence of recurring meeting"""
        self.ensure_one()
        
        if not self.is_recurring or self.recurrence_count <= 1:
            return
        
        # Calculate next occurrence date
        next_start = self._calculate_next_occurrence_date()
        duration = self.end_datetime - self.start_datetime
        next_end = next_start + duration
        
        # Create new meeting
        new_vals = {
            'name': self.name,
            'description': self.description,
            'organizer_id': self.organizer_id.id,
            'start_datetime': next_start,
            'end_datetime': next_end,
            'location': self.location,
            'meeting_type': self.meeting_type,
            'priority': self.priority,
            'attendee_ids': [(6, 0, self.attendee_ids.ids)],
            'department_ids': [(6, 0, self.department_ids.ids)],
            'job_position_ids': [(6, 0, self.job_position_ids.ids)],
            'room_id': self.room_id.id if self.room_id else False,
            'equipment_ids': [(6, 0, self.equipment_ids.ids)],
            'agenda': self.agenda,
            'preparation_notes': self.preparation_notes,
            'max_attendees': self.max_attendees,
            'is_recurring': True,
            'recurrence_pattern': self.recurrence_pattern,
            'recurrence_count': self.recurrence_count - 1,
        }
        
        new_meeting = self.create(new_vals)
        
        # Auto-submit for approval if needed
        if new_meeting.requires_approval:
            new_meeting.approver_id = self.approver_id
            new_meeting.action_submit_for_approval()
        else:
            new_meeting.action_approve()
    
    def _calculate_next_occurrence_date(self):
        """Calculate next occurrence date based on pattern"""
        from datetime import timedelta
        
        if self.recurrence_pattern == 'daily':
            return self.start_datetime + timedelta(days=1)
        elif self.recurrence_pattern == 'weekly':
            return self.start_datetime + timedelta(weeks=1)
        elif self.recurrence_pattern == 'monthly':
            return self.start_datetime + timedelta(days=30)  # Simplified
        elif self.recurrence_pattern == 'quarterly':
            return self.start_datetime + timedelta(days=90)  # Simplified
        
        return self.start_datetime
