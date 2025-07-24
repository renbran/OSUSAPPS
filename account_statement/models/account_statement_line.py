from odoo import models, fields, api, _

class AccountStatementLine(models.Model):
    _name = 'account.statement.line'
    _description = 'Account Statement Line'
    _order = 'date'

    statement_id = fields.Many2one('account.statement', string='Statement', required=True, ondelete='cascade')
    date = fields.Date(string='Date', required=True, index=True)
    name = fields.Char(string='Description', required=True)
    move_id = fields.Many2one('account.move', string='Journal Entry', index=True)
    partner_id = fields.Many2one('res.partner', related='statement_id.partner_id', store=True)
    company_id = fields.Many2one('res.company', related='statement_id.company_id', store=True)
    currency_id = fields.Many2one('res.currency', related='statement_id.currency_id', store=True)
    
    debit = fields.Monetary(string='Debit', currency_field='currency_id', default=0.0)
    credit = fields.Monetary(string='Credit', currency_field='currency_id', default=0.0)
    balance = fields.Monetary(string='Running Balance', currency_field='currency_id', compute='_compute_balance', store=True)
    
    @api.depends('statement_id.line_ids.debit', 'statement_id.line_ids.credit')
    def _compute_balance(self):
        for record in self:
            previous_lines = record.statement_id.line_ids.filtered(
                lambda r: r.date <= record.date and r.id <= record.id
            ).sorted('date')
            balance = 0.0
            for line in previous_lines:
                balance += line.credit - line.debit
            record.balance = balance
