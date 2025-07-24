# -*- coding: utf-8 -*-
from odoo import models, fields, api

class CalendarDepartmentGroup(models.Model):
    _name = 'calendar.department.group'
    _description = 'Calendar Department Group'

    name = fields.Char('Name', required=True)
    department_ids = fields.Many2many('hr.department', string='Departments')
    active = fields.Boolean('Active', default=True)
