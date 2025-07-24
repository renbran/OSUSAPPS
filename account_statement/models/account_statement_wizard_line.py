from odoo import models, fields

class AccountStatementWizardLine(models.TransientModel):
    _name = 'account_statement.wizard.line'
    _description = 'Account Statement Wizard Line'
    # Add your fields here as needed
    name = fields.Char(string='Description')
