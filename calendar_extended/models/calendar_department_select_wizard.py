# -*- coding: utf-8 -*-
from odoo import models, fields

class CalendarDepartmentSelectWizard(models.TransientModel):
    _name = 'calendar.department.select.wizard'
    _description = 'Department Selection Wizard'

    department_ids = fields.Many2many('hr.department', string='Departments')
    
    def action_confirm(self):
        self.ensure_one()
        # Add your action implementation here
        return {'type': 'ir.actions.act_window_close'}
