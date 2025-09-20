from odoo import models, fields

class CommissionStatementLine(models.TransientModel):
    _name = 'commission.statement.line'
    _description = 'Commission Statement Line'

    wizard_id = fields.Many2one('commission.partner.statement.wizard', string='Wizard', help="Related commission statement wizard", required=True)
    agent_name = fields.Char(string='Agent Name', help="Name of the commission agent", required=True)
    booking_date = fields.Date(string='Booking Date', help="Date of the booking", required=True)
    commission_type = fields.Char(string='Commission Type', help="Type of commission")
    rate = fields.Char(string='Rate', help="Commission rate (%)")
    sale_value = fields.Float(string='Sale Value', help="Sale value for commission calculation")
    gross_commission = fields.Float(string='Gross Commission', help="Gross commission amount")
    vat_rate = fields.Char(string='VAT (%)', help="VAT rate (%)")
    net_commission = fields.Float(string='Net Commission', help="Net commission after VAT")
    status = fields.Char(string='Status', help="Commission status")
    po_number = fields.Char(string='PO Number', help="Related purchase order number")
    remarks = fields.Char(string='Remarks', help="Additional remarks")
    currency_id = fields.Many2one('res.currency', string='Currency', help="Currency for commission amounts", required=True)
