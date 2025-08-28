from odoo import models, fields

class Project(models.Model):
    _name = 'project.project'
    _description = 'Project'

    name = fields.Char(string='Project Name', required=True)
    description = fields.Text(string='Description')
    unit_ids = fields.One2many('project.unit', 'project_id', string='Units')
