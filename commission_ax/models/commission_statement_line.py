from odoo import models, fields

class CommissionStatementLine(models.TransientModel):
    _name = 'commission.statement.line'
    _description = 'Commission Statement Line'

    wizard_id = fields.Many2one('commission.statement.wizard', string='Wizard', help="Related commission statement wizard", required=True)
    agent_name = fields.Char(string='Agent Name', help="Name of the commission agent", tracking=True, required=True)
    booking_date = fields.Date(string='Booking Date', help="Date of the booking", tracking=True, required=True)
    commission_type = fields.Char(string='Commission Type', help="Type of commission", tracking=True)
    rate = fields.Char(string='Rate', help="Commission rate (%)", tracking=True)
    sale_value = fields.Float(string='Sale Value', help="Sale value for commission calculation", tracking=True)
    gross_commission = fields.Float(string='Gross Commission', help="Gross commission amount", tracking=True)
    vat_rate = fields.Char(string='VAT (%)', help="VAT rate (%)", tracking=True)
    net_commission = fields.Float(string='Net Commission', help="Net commission after VAT", tracking=True)
    status = fields.Char(string='Status', help="Commission status", tracking=True)
    po_number = fields.Char(string='PO Number', help="Related purchase order number", tracking=True)
    remarks = fields.Char(string='Remarks', help="Additional remarks", tracking=True)
    currency_id = fields.Many2one('res.currency', string='Currency', help="Currency for commission amounts", required=True)
