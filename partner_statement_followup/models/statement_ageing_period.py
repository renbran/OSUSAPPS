# -*- coding: utf-8 -*-
from odoo import models, fields, api

class StatementAgeingPeriod(models.Model):
    _name = 'statement.ageing.period'
    _description = 'Statement Ageing Period'
    _order = 'sequence, id'

    name = fields.Char(string='Period Name', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    date_from = fields.Integer(string='From (days)', default=0,
                              help="Number of days from due date (negative for overdue)")
    date_to = fields.Integer(string='To (days)', default=0,
                            help="Number of days to due date (negative for overdue)")
    active = fields.Boolean(string='Active', default=True)

    @api.constrains('date_from', 'date_to')
    def _check_date_range(self):
        for record in self:
            if record.date_from > record.date_to:
                raise ValueError("From date must be less than or equal to To date")

class AgeingPeriod(models.Model):
    """Alias model for ageing.period references"""
    _name = 'ageing.period'
    _description = 'Ageing Period (Alias)'
    _order = 'sequence, id'

    name = fields.Char(string='Period Name', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    date_from = fields.Integer(string='From (days)', default=0)
    date_to = fields.Integer(string='To (days)', default=0)
    active = fields.Boolean(string='Active', default=True)