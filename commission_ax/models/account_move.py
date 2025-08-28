from odoo import models, api

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    def _post(self, soft=True):
        res = super()._post(soft)
        for move in self:
            if move.purchase_id and move.purchase_id.is_commission_po:
                move.purchase_id.commission_posted = True
                move.purchase_id.message_post(
                    body=f"Commission posted via bill {move.name}"
                )
                # Auto-send notification
                if move.purchase_id.partner_id.email:
                    template = self.env.ref('commission_ax.commission_payout_notification_template')
                    template.send_mail(move.purchase_id.id)
        return res