from odoo import models, fields, api
from datetime import datetime, timedelta


class CommissionStatementWizard(models.TransientModel):
    _name = 'commission.statement.wizard'
    _description = 'Commission Statement Generator'

    partner_id = fields.Many2one('res.partner', string='Commission Partner', required=True,
                                 domain=[('is_commission_agent', '=', True)])
    date_from = fields.Date(string='Date From', required=True, 
                           default=lambda self: datetime.now().replace(day=1))
    date_to = fields.Date(string='Date To', required=True, 
                         default=lambda self: datetime.now())
    state_filter = fields.Selection([
        ('all', 'All'),
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('paid', 'Paid')
    ], string='Status Filter', default='all', required=True)
    commission_type_filter = fields.Selection([
        ('all', 'All Types'),
        ('sale', 'Sales Commission'),
        ('referral', 'Referral Commission'),
        ('target', 'Target Achievement'),
        ('bonus', 'Bonus Commission')
    ], string='Commission Type Filter', default='all', required=True)

    def action_generate_statement(self):
        """Generate commission statement report"""
        self.ensure_one()
        
        domain = [
            ('partner_id', '=', self.partner_id.id),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to)
        ]
        
        if self.state_filter != 'all':
            domain.append(('state', '=', self.state_filter))
        
        if self.commission_type_filter != 'all':
            domain.append(('commission_type', '=', self.commission_type_filter))
        
        commission_lines = self.env['commission.line'].search(domain)
        
        if not commission_lines:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'No Data',
                    'message': 'No commission lines found for the selected criteria.',
                    'type': 'warning'
                }
            }
        
        return {
            'type': 'ir.actions.report',
            'report_name': 'commission_lines.report_commission_statement',
            'report_type': 'qweb-pdf',
            'data': {
                'partner_id': self.partner_id.id,
                'date_from': self.date_from,
                'date_to': self.date_to,
                'state_filter': self.state_filter,
                'commission_type_filter': self.commission_type_filter,
            },
            'context': self.env.context,
        }

    def action_view_commission_lines(self):
        """View commission lines based on filters"""
        self.ensure_one()
        
        domain = [
            ('partner_id', '=', self.partner_id.id),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to)
        ]
        
        if self.state_filter != 'all':
            domain.append(('state', '=', self.state_filter))
        
        if self.commission_type_filter != 'all':
            domain.append(('commission_type', '=', self.commission_type_filter))
        
        return {
            'type': 'ir.actions.act_window',
            'name': f'Commission Lines - {self.partner_id.name}',
            'view_mode': 'tree,form',
            'res_model': 'commission.line',
            'domain': domain,
            'context': {'default_partner_id': self.partner_id.id},
        }