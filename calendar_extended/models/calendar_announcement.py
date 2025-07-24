# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class CalendarAnnouncement(models.Model):
    _name = 'calendar.announcement'
    _description = 'Calendar Meeting Announcement'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(string='Meeting Title', required=True, tracking=True)
    description = fields.Html(string='Description')
    
    # Approval workflow states
    state = fields.Selection([
        ('draft', 'Draft'),
        ('review', 'Under Review'),
        ('approved', 'Approved'),
        ('sent', 'Invitations Sent'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    
    # Meeting details
    start_datetime = fields.Datetime(string='Start Date', required=True)
    end_datetime = fields.Datetime(string='End Date', required=True)
    location = fields.Char(string='Location')
    
    # Attendee management
    attendee_ids = fields.Many2many(
        'hr.employee',
        'calendar_announcement_attendee_rel',
        'announcement_id',
        'employee_id',
        string='Attendees'
    )
    
    department_ids = fields.Many2many(
        'hr.department',
        string='Departments',
        help='Select departments to include all employees'
    )
    
    all_employees = fields.Boolean(
        string='All Employees',
        help='Include all company employees'
    )
    
    # Invitation control
    invitation_sent = fields.Boolean(string='Invitations Sent', default=False)
    invitation_sent_date = fields.Datetime(string='Invitations Sent On')
    scheduled_send_date = fields.Datetime(string='Scheduled Send Date')
    
    # Approval tracking
    submitted_by = fields.Many2one('res.users', string='Submitted By', default=lambda self: self.env.user)
    reviewed_by = fields.Many2one('res.users', string='Reviewed By')
    approved_by = fields.Many2one('res.users', string='Approved By')
    
    review_date = fields.Datetime(string='Review Date')
    approval_date = fields.Datetime(string='Approval Date')
    
    review_notes = fields.Text(string='Review Notes')
    approval_notes = fields.Text(string='Approval Notes')
    
    # Related calendar event (created when sent)
    calendar_event_id = fields.Many2one('calendar.event', string='Calendar Event')
    
    # Computed fields
    attendee_count = fields.Integer(string='Attendee Count', compute='_compute_attendee_count')
    total_employees = fields.Integer(string='Total Employees', compute='_compute_total_employees')
    
    @api.depends('attendee_ids', 'department_ids', 'all_employees')
    def _compute_attendee_count(self):
        for record in self:
            count = len(record.attendee_ids)
            
            # Add department employees
            for dept in record.department_ids:
                count += len(dept.member_ids)
            
            # Add all employees if selected
            if record.all_employees:
                count = self.env['hr.employee'].search_count([])
            
            record.attendee_count = count
    
    @api.depends('all_employees')
    def _compute_total_employees(self):
        total = self.env['hr.employee'].search_count([])
        for record in self:
            record.total_employees = total
    
    @api.constrains('start_datetime', 'end_datetime')
    def _check_dates(self):
        for record in self:
            if record.start_datetime and record.end_datetime:
                if record.start_datetime >= record.end_datetime:
                    raise ValidationError(_('End date must be after start date.'))
    
    def action_submit_for_review(self):
        """Submit announcement for review"""
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_('Only draft announcements can be submitted for review.'))
        
        self.write({
            'state': 'review',
            'review_date': fields.Datetime.now()
        })
        
        self.message_post(
            body=_('Announcement submitted for review by %s') % self.env.user.name,
            message_type='notification'
        )
    
    def action_approve(self):
        """Approve the announcement"""
        self.ensure_one()
        if self.state != 'review':
            raise UserError(_('Only announcements under review can be approved.'))
        
        self.write({
            'state': 'approved',
            'approved_by': self.env.user.id,
            'approval_date': fields.Datetime.now()
        })
        
        self.message_post(
            body=_('Announcement approved by %s') % self.env.user.name,
            message_type='notification'
        )
    
    def action_reject(self):
        """Reject and send back to draft"""
        self.ensure_one()
        if self.state != 'review':
            raise UserError(_('Only announcements under review can be rejected.'))
        
        self.write({
            'state': 'draft',
            'reviewed_by': self.env.user.id
        })
        
        self.message_post(
            body=_('Announcement rejected by %s') % self.env.user.name,
            message_type='notification'
        )
    
    def action_send_invitations(self):
        """Send invitations now"""
        self.ensure_one()
        if self.state != 'approved':
            raise UserError(_('Only approved announcements can send invitations.'))
        
        self._send_invitations()
    
    def action_schedule_invitations(self):
        """Open wizard to schedule invitations"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Schedule Invitations'),
            'res_model': 'calendar.send.invitation.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_announcement_id': self.id}
        }
    
    def action_select_attendees(self):
        """Open wizard to select attendees by department"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Select Attendees'),
            'res_model': 'calendar.department.select.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_announcement_id': self.id}
        }
    
    def _send_invitations(self):
        """Internal method to send invitations"""
        self.ensure_one()
        
        # Collect all attendees
        attendees = self._get_all_attendees()
        
        if not attendees:
            raise UserError(_('No attendees selected for this announcement.'))
        
        # Create calendar event
        event_vals = {
            'name': self.name,
            'description': self.description,
            'start': self.start_datetime,
            'stop': self.end_datetime,
            'location': self.location,
            'partner_ids': [(6, 0, attendees.mapped('user_id.partner_id').ids)],
        }
        
        calendar_event = self.env['calendar.event'].create(event_vals)
        
        # Update announcement
        self.write({
            'state': 'sent',
            'invitation_sent': True,
            'invitation_sent_date': fields.Datetime.now(),
            'calendar_event_id': calendar_event.id
        })
        
        self.message_post(
            body=_('Invitations sent to %d attendees') % len(attendees),
            message_type='notification'
        )
    
    def _get_all_attendees(self):
        """Get all attendees including from departments and all employees"""
        attendees = self.attendee_ids
        
        # Add department employees
        for dept in self.department_ids:
            attendees |= dept.member_ids
        
        # Add all employees if selected
        if self.all_employees:
            attendees = self.env['hr.employee'].search([])
        
        return attendees
    
    @api.model
    def _cron_send_scheduled_invitations(self):
        """Cron job to send scheduled invitations"""
        now = fields.Datetime.now()
        scheduled_announcements = self.search([
            ('state', '=', 'approved'),
            ('scheduled_send_date', '<=', now),
            ('invitation_sent', '=', False)
        ])
        
        for announcement in scheduled_announcements:
            try:
                announcement._send_invitations()
            except Exception as e:
                announcement.message_post(
                    body=_('Failed to send scheduled invitations: %s') % str(e),
                    message_type='notification'
                )
