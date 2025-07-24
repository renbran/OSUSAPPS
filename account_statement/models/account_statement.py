from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class AccountStatement(models.Model):
    _name = 'account.statement'
    _description = 'Account Statement'
    _order = 'date desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Statement Name', required=True, tracking=True)
    date = fields.Date(string='Date', required=True, default=fields.Date.context_today, index=True, tracking=True)
    partner_id = fields.Many2one('res.partner', string='Partner', required=True, index=True, tracking=True)
    date_from = fields.Date(string='Date From', required=True, index=True, tracking=True)
    date_to = fields.Date(string='Date To', required=True, index=True, tracking=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id, tracking=True)
    total_debit = fields.Monetary(string='Total Debit', currency_field='currency_id')
    total_credit = fields.Monetary(string='Total Credit', currency_field='currency_id')
    balance = fields.Monetary(string='Balance', currency_field='currency_id')
    line_ids = fields.One2many('account.statement.line', 'statement_id', string='Statement Lines')

    # Add status tracking
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, tracking=True)

    # Add user tracking
    user_id = fields.Many2one('res.users', string='Responsible', default=lambda self: self.env.user, tracking=True)
    
    @api.model
    def create(self, vals):
        """Override create to add creation message"""
        result = super(AccountStatement, self).create(vals)
        result.message_post(body=_("Account Statement created"))
        return result
    
    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for record in self:
            if record.date_from and record.date_to and record.date_from > record.date_to:
                raise ValidationError(_('Start date must be before end date'))

    _sql_constraints = [
        ('name_partner_date_uniq', 'unique(name,partner_id,date)', 
         'Statement name must be unique per partner and date!')
    ]

    def _compute_totals(self):
        """Compute statement totals from lines"""
        for record in self:
            record.total_debit = sum(record.line_ids.mapped('debit'))
            record.total_credit = sum(record.line_ids.mapped('credit'))
            record.balance = record.total_credit - record.total_debit
            
    def action_confirm(self):
        """Confirm the statement"""
        self.write({'state': 'confirmed'})
        self.message_post(body=_("Account Statement confirmed"))
        
    def action_cancel(self):
        """Cancel the statement"""
        self.write({'state': 'cancelled'})
        self.message_post(body=_("Account Statement cancelled"))
        
    def action_draft(self):
        """Reset to draft"""
        self.write({'state': 'draft'})
        self.message_post(body=_("Account Statement reset to draft"))


class AccountStatementLine(models.Model):
    _name = 'account.statement.line'
    _description = 'Account Statement Line'
    _order = 'date, id'

    statement_id = fields.Many2one('account.statement', string='Statement', ondelete='cascade')
    date = fields.Date(string='Date')
    account_name = fields.Char(string='Account')
    account_code = fields.Char(string='Account Code')
    label = fields.Char(string='Label')
    debit = fields.Monetary(string='Debit', currency_field='currency_id')
    credit = fields.Monetary(string='Credit', currency_field='currency_id')
    running_balance = fields.Monetary(string='Running Balance', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', related='statement_id.currency_id', store=True)