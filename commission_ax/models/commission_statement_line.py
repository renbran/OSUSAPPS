from odoo import models, fields

class CommissionStatementLine(models.TransientModel):
    _name = 'commission.statement.line'
    _description = 'Commission Statement Line'

    wizard_id = fields.Many2one('commission.statement.wizard', string='Wizard')
    agent_name = fields.Char(string='Agent Name')
    deal_date = fields.Date(string='Deal Date')
    commission_type = fields.Char(string='Commission Type')
    rate = fields.Char(string='Rate')
    property_price = fields.Float(string='Property Price')
    gross_commission = fields.Float(string='Gross Commission')
    vat_rate = fields.Char(string='VAT (%)')
    net_commission = fields.Float(string='Net Commission')
    status = fields.Char(string='Status')
    po_number = fields.Char(string='PO Number')
    remarks = fields.Char(string='Remarks')
    currency_id = fields.Many2one('res.currency', string='Currency')
