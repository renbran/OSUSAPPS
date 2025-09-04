from odoo import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_open_commission_report_wizard(self):
        """Open commission statement wizard for this order"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Commission Statement Report',
            'res_model': 'commission.statement.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_sale_order_id': self.id,
                'default_date_from': self.date_order.date() if self.date_order else None,
                'default_date_to': self.date_order.date() if self.date_order else None,
            }
        }
