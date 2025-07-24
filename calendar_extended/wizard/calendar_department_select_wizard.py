# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class CalendarDepartmentSelectWizard(models.TransientModel):
    _name = 'calendar.department.select.wizard'
    _description = 'Department Employee Selection Wizard'

    announcement_id = fields.Many2one('calendar.announcement', string='Announcement', required=True)
    
    # Selection options
    selection_mode = fields.Selection([
        ('departments', 'Select by Departments'),
        ('individuals', 'Select Individual Employees'),
        ('all', 'All Employees')
    ], string='Selection Mode', default='departments', required=True)
    
    # Department selection
    department_ids = fields.Many2many(
        'hr.department',
        string='Departments',
        help='Select departments to include all their employees'
    )
    
    # Individual employee selection
    employee_ids = fields.Many2many(
        'hr.employee',
        string='Employees',
        help='Select specific employees'
    )
    
    # Quick actions
    select_all_departments = fields.Boolean(string='Select All Departments')
    
    # Preview information
    total_employees = fields.Integer(string='Total Employees', compute='_compute_total_employees')
    selected_count = fields.Integer(string='Selected Count', compute='_compute_selected_count')
    
    @api.depends('selection_mode')
    def _compute_total_employees(self):
        total = self.env['hr.employee'].search_count([])
        for wizard in self:
            wizard.total_employees = total
    
    @api.depends('selection_mode', 'department_ids', 'employee_ids', 'select_all_departments')
    def _compute_selected_count(self):
        for wizard in self:
            count = 0
            
            if wizard.selection_mode == 'all':
                count = wizard.total_employees
            elif wizard.selection_mode == 'departments':
                if wizard.select_all_departments:
                    count = wizard.total_employees
                else:
                    for dept in wizard.department_ids:
                        count += len(dept.member_ids)
            elif wizard.selection_mode == 'individuals':
                count = len(wizard.employee_ids)
            
            wizard.selected_count = count
    
    @api.onchange('select_all_departments')
    def _onchange_select_all_departments(self):
        if self.select_all_departments:
            all_departments = self.env['hr.department'].search([])
            self.department_ids = [(6, 0, all_departments.ids)]
        else:
            self.department_ids = [(5, 0, 0)]
    
    def action_quick_select_all(self):
        """Quick action to select all employees"""
        self.selection_mode = 'all'
        return {'type': 'ir.actions.do_nothing'}
    
    def action_quick_select_department(self, department_id):
        """Quick action to select a specific department"""
        self.selection_mode = 'departments'
        self.department_ids = [(6, 0, [department_id])]
        return {'type': 'ir.actions.do_nothing'}
    
    def action_apply_selection(self):
        """Apply the selection to the announcement"""
        self.ensure_one()
        
        announcement = self.announcement_id
        
        # Clear existing selections
        announcement.write({
            'department_ids': [(5, 0, 0)],
            'attendee_ids': [(5, 0, 0)],
            'all_employees': False
        })
        
        # Apply new selection based on mode
        if self.selection_mode == 'all':
            announcement.all_employees = True
        elif self.selection_mode == 'departments':
            announcement.department_ids = [(6, 0, self.department_ids.ids)]
        elif self.selection_mode == 'individuals':
            announcement.attendee_ids = [(6, 0, self.employee_ids.ids)]
        
        # Show confirmation message
        message = _('Selected %d employees for the announcement.') % self.selected_count
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': message,
                'type': 'success',
                'sticky': False,
            }
        }
    
    @api.model
    def get_department_tree(self):
        """Get department hierarchy for tree view"""
        departments = self.env['hr.department'].search([])
        dept_tree = []
        
        for dept in departments:
            dept_info = {
                'id': dept.id,
                'name': dept.name,
                'employee_count': len(dept.member_ids),
                'parent_id': dept.parent_id.id if dept.parent_id else False,
                'employees': [{'id': emp.id, 'name': emp.name} for emp in dept.member_ids]
            }
            dept_tree.append(dept_info)
        
        return dept_tree
