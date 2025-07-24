# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, timedelta


class CalendarReportWizard(models.TransientModel):
    _name = 'calendar.report.wizard'
    _description = 'Calendar Report Wizard'

    report_type = fields.Selection([
        ('attendance', 'Attendance Report'),
        ('utilization', 'Resource Utilization'),
        ('event_summary', 'Event Summary'),
        ('analytics', 'Event Analytics'),
        ('feedback', 'Feedback Report')
    ], string='Report Type', required=True)
    
    date_from = fields.Date(
        string='From Date',
        required=True,
        default=fields.Date.today
    )
    
    date_to = fields.Date(
        string='To Date',
        required=True,
        default=lambda self: fields.Date.today() + timedelta(days=30)
    )
    
    partner_ids = fields.Many2many(
        'res.partner',
        string='Attendees',
        help='Filter by specific attendees'
    )
    
    event_type_ids = fields.Many2many(
        'calendar.event.type',
        string='Event Types',
        help='Filter by event types'
    )
    
    resource_ids = fields.Many2many(
        'calendar.resource',
        string='Resources',
        help='Filter by resources'
    )
    
    status_filter = fields.Selection([
        ('all', 'All'),
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status Filter', default='all')
    
    group_by = fields.Selection([
        ('day', 'Day'),
        ('week', 'Week'),
        ('month', 'Month'),
        ('type', 'Event Type'),
        ('attendee', 'Attendee'),
        ('resource', 'Resource')
    ], string='Group By', default='month')
    
    include_private = fields.Boolean(
        string='Include Private Events',
        default=False
    )
    
    output_format = fields.Selection([
        ('pdf', 'PDF'),
        ('xlsx', 'Excel'),
        ('csv', 'CSV')
    ], string='Output Format', default='pdf')
    
    def action_generate_report(self):
        """Generate the selected report"""
        self.ensure_one()
        
        data = self._prepare_report_data()
        
        if self.report_type == 'attendance':
            return self._generate_attendance_report(data)
        elif self.report_type == 'utilization':
            return self._generate_utilization_report(data)
        elif self.report_type == 'event_summary':
            return self._generate_event_summary_report(data)
        elif self.report_type == 'analytics':
            return self._generate_analytics_report(data)
        elif self.report_type == 'feedback':
            return self._generate_feedback_report(data)
    
    def _prepare_report_data(self):
        """Prepare data for report generation"""
        domain = [
            ('start', '>=', self.date_from),
            ('stop', '<=', self.date_to)
        ]
        
        if self.partner_ids:
            domain.append(('partner_ids', 'in', self.partner_ids.ids))
        
        if self.event_type_ids:
            domain.append(('event_type_id', 'in', self.event_type_ids.ids))
        
        if self.resource_ids:
            domain.append(('resource_ids', 'in', self.resource_ids.ids))
        
        if self.status_filter != 'all':
            domain.append(('status', '=', self.status_filter))
        
        if not self.include_private:
            domain.append(('is_public', '=', True))
        
        events = self.env['calendar.event'].search(domain)
        
        return {
            'events': events,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'group_by': self.group_by,
            'output_format': self.output_format
        }
    
    def _generate_attendance_report(self, data):
        """Generate attendance report"""
        return {
            'type': 'ir.actions.report',
            'report_name': 'calendar_extended.attendance_report',
            'report_type': 'qweb-pdf',
            'data': data,
            'context': self.env.context
        }
    
    def _generate_utilization_report(self, data):
        """Generate resource utilization report"""
        return {
            'type': 'ir.actions.report',
            'report_name': 'calendar_extended.utilization_report',
            'report_type': 'qweb-pdf',
            'data': data,
            'context': self.env.context
        }
    
    def _generate_event_summary_report(self, data):
        """Generate event summary report"""
        return {
            'type': 'ir.actions.report',
            'report_name': 'calendar_extended.event_summary_report',
            'report_type': 'qweb-pdf',
            'data': data,
            'context': self.env.context
        }
    
    def _generate_analytics_report(self, data):
        """Generate analytics report"""
        return {
            'type': 'ir.actions.report',
            'report_name': 'calendar_extended.analytics_report',
            'report_type': 'qweb-pdf',
            'data': data,
            'context': self.env.context
        }
    
    def _generate_feedback_report(self, data):
        """Generate feedback report"""
        return {
            'type': 'ir.actions.report',
            'report_name': 'calendar_extended.feedback_report',
            'report_type': 'qweb-pdf',
            'data': data,
            'context': self.env.context
        }
