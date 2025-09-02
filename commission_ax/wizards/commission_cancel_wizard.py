from odoo import models, fields, api, _

class CommissionCancelWizard(models.TransientModel):
    _name = 'commission.cancel.wizard'
    _description = 'Commission Cancel Wizard'

    message = fields.Text(string='Message', readonly=True)

    def action_confirm_cancel(self):
        # Implement cancellation logic here
        return {'type': 'ir.actions.act_window_close'}
