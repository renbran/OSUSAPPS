from odoo import models, fields, api, _

class OsusSampleWizard(models.TransientModel):
    _name = 'osus.sample.wizard'
    _description = 'Sample Wizard for OSUS'

    name = fields.Char(string='Name')

    def action_do(self):
        return {'type': 'ir.actions.act_window_close'}
