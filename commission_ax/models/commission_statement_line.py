from odoo import models, fields

class CommissionStatementLine(models.TransientModel):
    _name = 'commission.statement.line'
    _description = 'Commission Statement Line'

    wizard_id = fields.Many2one('commission.statement.wizard', string='Wizard', help="Related commission statement wizard", required=True)
    agent_name = fields.Char(string='Agent Name', help="Name of the commission agent", tracking=True, required=True)
    deal_date = fields.Date(string='Deal Date', help="Date of the deal", tracking=True, required=True)
    commission_type = fields.Char(string='Commission Type', help="Type of commission", tracking=True)
    rate = fields.Char(string='Rate', help="Commission rate (%)", tracking=True)
    property_price = fields.Float(string='Property Price', help="Property price for commission calculation", tracking=True)
    gross_commission = fields.Float(string='Gross Commission', help="Gross commission amount", tracking=True)
    vat_rate = fields.Char(string='VAT (%)', help="VAT rate (%)", tracking=True)
    net_commission = fields.Float(string='Net Commission', help="Net commission after VAT", tracking=True)
    status = fields.Char(string='Status', help="Commission status", tracking=True)
    po_number = fields.Char(string='PO Number', help="Related purchase order number", tracking=True)
    remarks = fields.Char(string='Remarks', help="Additional remarks", tracking=True)
    currency_id = fields.Many2one('res.currency', string='Currency', help="Currency for commission amounts", required=True)
