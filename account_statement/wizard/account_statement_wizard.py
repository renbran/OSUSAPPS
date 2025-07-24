from odoo import api, fields, models
from datetime import date


class AccountStatementWizard(models.TransientModel):
    _name = 'account.statement.wizard'
    _description = 'Account Statement Generator'

    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    date_from = fields.Date(string='From Date', required=True, default=fields.Date.context_today)
    date_to = fields.Date(string='To Date', required=True, default=fields.Date.context_today)
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                default=lambda self: self.env.company)
    
    def action_generate_statement(self):
        """Generate the account statement."""
        self.ensure_one()        # Prepare statement values
        vals = {
            'name': f"{self.partner_id.name} - {fields.Date.to_string(self.date_from)} to {fields.Date.to_string(self.date_to)}",
            'partner_id': self.partner_id.id,
            'date': fields.Date.today(),
            'date_from': self.date_from,
            'date_to': self.date_to,
            'company_id': self.company_id.id,
        }
        
        # Create statement
        statement = self.env['account.statement'].create(vals)
        
        # Generate lines from account moves
        moves = self.env['account.move.line'].search([
            ('partner_id', '=', self.partner_id.id),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('parent_state', '=', 'posted'),
            ('account_id.internal_type', 'in', ['receivable', 'payable']),
            ('company_id', '=', self.company_id.id),
        ], order='date')
        
        # Create statement lines
        line_vals = []
        for move in moves:
            line_vals.append({
                'statement_id': statement.id,
                'date': move.date,
                'name': move.name or move.move_id.name,
                'move_id': move.move_id.id,
                'debit': move.debit,
                'credit': move.credit,
            })
        
        if line_vals:
            self.env['account.statement.line'].create(line_vals)
            
        # Update statement totals
        statement._compute_totals()
        return {
            'name': 'Account Statement',
            'type': 'ir.actions.act_window',
            'res_model': 'account.statement',
            'res_id': statement.id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'current',
        }
