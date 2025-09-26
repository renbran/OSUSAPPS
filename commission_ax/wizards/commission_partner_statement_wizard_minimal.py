# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class CommissionPartnerStatementWizardMinimal(models.TransientModel):
    """Minimal version for testing imports"""
    _name = 'commission.partner.statement.wizard.minimal'
    _description = 'Minimal Commission Partner Statement Wizard'
    
    date_from = fields.Date(string='From Date', required=True)
    date_to = fields.Date(string='To Date', required=True)