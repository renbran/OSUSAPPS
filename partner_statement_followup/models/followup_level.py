# -*- coding: utf-8 -*-
from odoo import models, fields, api

class FollowupLevel(models.Model):
    _name = 'followup.level'
    _description = 'Follow-up Level'
    _order = 'sequence, id'

    name = fields.Char(string='Level Name', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    days = fields.Integer(string='Days after due date', required=True, default=1,
                         help="Number of days after due date to trigger this follow-up level")
    description = fields.Text(string='Follow-up Description')
    email_template_id = fields.Many2one('mail.template', string='Email Template')
    send_email = fields.Boolean(string='Send Email', default=True)
    send_letter = fields.Boolean(string='Print Letter', default=False)
    manual_action = fields.Boolean(string='Manual Action Required', default=False)
    manual_action_note = fields.Text(string='Manual Action Note')
    
    @api.constrains('days')
    def _check_days(self):
        for record in self:
            if record.days < 0:
                raise ValueError("Days must be positive")