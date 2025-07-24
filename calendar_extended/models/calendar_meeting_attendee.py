# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class CalendarMeetingAttendee(models.Model):
    _name = 'calendar.meeting.attendee'
    _description = 'Internal Meeting Attendee'
    _rec_name = 'employee_id'

    meeting_id = fields.Many2one(
        'calendar.internal.meeting',
        string='Meeting',
        required=True,
        ondelete='cascade'
    )
    
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True
    )
    
    status = fields.Selection([
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('tentative', 'Tentative')
    ], string='Status', default='pending')
    
    response_date = fields.Datetime(string='Response Date')
    
    notes = fields.Text(string='Notes')
    
    is_required = fields.Boolean(string='Required Attendee', default=True)
    
    def action_accept(self):
        """Accept meeting invitation"""
        self.status = 'accepted'
        self.response_date = fields.Datetime.now()
    
    def action_decline(self):
        """Decline meeting invitation"""
        self.status = 'declined'
        self.response_date = fields.Datetime.now()
    
    def action_tentative(self):
        """Mark as tentative"""
        self.status = 'tentative'
        self.response_date = fields.Datetime.now()


class CalendarDepartmentGroup(models.Model):
    _name = 'calendar.department.group'
    _description = 'Department Group for Meeting Invitations'
    _order = 'name'

    name = fields.Char(string='Group Name', required=True)
    
    description = fields.Text(string='Description')
    
    department_ids = fields.Many2many(
        'hr.department',
        string='Departments'
    )
    
    employee_ids = fields.Many2many(
        'hr.employee',
        string='Additional Employees',
        help='Additional employees not covered by departments'
    )
    
    manager_id = fields.Many2one(
        'hr.employee',
        string='Group Manager',
        help='Manager responsible for this group'
    )
    
    is_active = fields.Boolean(string='Active', default=True)
    
    auto_approve = fields.Boolean(
        string='Auto Approve',
        help='Meetings for this group are auto-approved'
    )
    
    def get_all_employees(self):
        """Get all employees in this group"""
        employees = self.employee_ids
        
        # Add employees from departments
        for dept in self.department_ids:
            employees |= dept.member_ids
        
        return employees
    
    def action_create_meeting(self):
        """Create meeting for this group"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Create Meeting for %s') % self.name,
            'res_model': 'calendar.internal.meeting',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_department_ids': [(6, 0, self.department_ids.ids)],
                'default_attendee_ids': [(6, 0, self.employee_ids.ids)],
                'default_approver_id': self.manager_id.user_id.id if self.manager_id and self.manager_id.user_id else False,
            }
        }
