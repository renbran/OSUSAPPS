# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class CalendarQuickMeetingWizard(models.TransientModel):
    _name = 'calendar.quick.meeting.wizard'
    _description = 'Quick Meeting Creation Wizard'

    name = fields.Char(string='Meeting Subject', required=True)
    
    description = fields.Html(string='Description')
    
    start_datetime = fields.Datetime(
        string='Start Date & Time',
        required=True,
        default=fields.Datetime.now
    )
    
    duration = fields.Float(
        string='Duration (Hours)',
        default=1.0,
        required=True
    )
    
    meeting_type = fields.Selection([
        ('team_meeting', 'Team Meeting'),
        ('department_meeting', 'Department Meeting'),
        ('project_review', 'Project Review'),
        ('training', 'Training Session'),
        ('brainstorming', 'Brainstorming'),
        ('one_on_one', 'One-on-One'),
        ('all_hands', 'All Hands Meeting'),
        ('other', 'Other')
    ], string='Meeting Type', default='team_meeting', required=True)
    
    location = fields.Char(string='Location')
    
    room_id = fields.Many2one(
        'calendar.resource',
        string='Meeting Room',
        domain=[('resource_type', '=', 'room')]
    )
    
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Urgent')
    ], string='Priority', default='1')
    
    # Quick selection options
    department_group_id = fields.Many2one(
        'calendar.department.group',
        string='Department Group',
        help='Select a predefined group'
    )
    
    department_ids = fields.Many2many(
        'hr.department',
        string='Departments'
    )
    
    employee_ids = fields.Many2many(
        'hr.employee',
        string='Employees'
    )
    
    requires_approval = fields.Boolean(
        string='Requires Approval',
        compute='_compute_requires_approval'
    )
    
    @api.depends('meeting_type', 'department_ids', 'employee_ids')
    def _compute_requires_approval(self):
        for wizard in self:
            # Simple approval logic
            attendee_count = len(wizard.employee_ids)
            for dept in wizard.department_ids:
                attendee_count += len(dept.member_ids)
            
            wizard.requires_approval = (
                attendee_count > 10 or 
                wizard.meeting_type in ['all_hands', 'department_meeting']
            )
    
    @api.onchange('department_group_id')
    def _onchange_department_group_id(self):
        if self.department_group_id:
            self.department_ids = [(6, 0, self.department_group_id.department_ids.ids)]
            self.employee_ids = [(6, 0, self.department_group_id.employee_ids.ids)]
    
    def action_create_meeting(self):
        """Create internal meeting from wizard"""
        self.ensure_one()
        
        end_datetime = self.start_datetime + timedelta(hours=self.duration)
        
        meeting_vals = {
            'name': self.name,
            'description': self.description,
            'start_datetime': self.start_datetime,
            'end_datetime': end_datetime,
            'meeting_type': self.meeting_type,
            'location': self.location,
            'room_id': self.room_id.id if self.room_id else False,
            'priority': self.priority,
            'department_ids': [(6, 0, self.department_ids.ids)],
            'attendee_ids': [(6, 0, self.employee_ids.ids)],
        }
        
        # Set approver if needed
        if self.requires_approval and self.department_group_id and self.department_group_id.manager_id:
            meeting_vals['approver_id'] = self.department_group_id.manager_id.user_id.id
        
        meeting = self.env['calendar.internal.meeting'].create(meeting_vals)
        
        # Auto-submit for approval or approve
        if self.requires_approval:
            meeting.action_submit_for_approval()
        else:
            meeting.action_approve()
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Internal Meeting'),
            'res_model': 'calendar.internal.meeting',
            'res_id': meeting.id,
            'view_mode': 'form',
            'target': 'current',
        }
