from odoo import models, fields

class SaleOrderReconciliation(models.Model):
    _name = 'sale.order.reconciliation'
    _description = 'Sales Order Reconciliation Remarks'

    invoice_remarks = fields.Char(string='Invoice Remarks')
    payment_remarks = fields.Char(string='Payment Remarks')
    invoiced_amount = fields.Float(string='Invoiced Amount')
    received_amount = fields.Float(string='Received Amount')
    balance = fields.Float(string='Balance')

    sale_order_id = fields.Many2one('sale.order', string='Sale Order', ondelete='cascade')

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    reconciliation_ids = fields.One2many('sale.order.reconciliation', 'sale_order_id', string="Reconciliation Remarks")
