from odoo import models, fields, api, _

class CommissionDraftWizard(models.TransientModel):
    _name = 'commission.draft.wizard'
    _description = 'Commission Draft Wizard'

    message = fields.Text(string='Message', readonly=True)

    def action_confirm_draft(self):
        # Implement draft logic here
        return {'type': 'ir.actions.act_window_close'}

    def action_abort_draft(self):
        # Closes the wizard without taking action
        return {'type': 'ir.actions.act_window_close'}
