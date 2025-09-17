from odoo import models, fields, api


class ResPartner(models.Model):
    """Extended Partner with Commission Information"""
    _inherit = 'res.partner'
    
    # Commission Lines Relationship
    commission_line_ids = fields.One2many(
        'commission.line', 
        'partner_id', 
        string='Commission Lines'
    )
    
    # Statistics
    total_commission_amount = fields.Monetary(
        string='Total Commission Amount',
        compute='_compute_commission_stats',
        store=True
    )
    commission_count = fields.Integer(
        string='Commission Count',
        compute='_compute_commission_stats',
        store=True
    )
    last_commission_date = fields.Date(
        string='Last Commission Date',
        compute='_compute_commission_stats',
        store=True
    )
    
    @api.depends('commission_line_ids.commission_amount', 'commission_line_ids.date')
    def _compute_commission_stats(self):
        for partner in self:
            lines = partner.commission_line_ids
            partner.total_commission_amount = sum(lines.mapped('commission_amount'))
            partner.commission_count = len(lines)
            
            dates = lines.mapped('date')
            partner.last_commission_date = max(dates) if dates else False
    
    def action_view_commission_lines(self):
        """View partner's commission lines"""
        return {
            'name': f'Commission Lines - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'commission.line',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id},
        }
    
    def action_generate_commission_statement(self):
        """Generate commission statement"""
        return {
            'name': 'Commission Statement',
            'type': 'ir.actions.act_window',
            'res_model': 'commission.statement.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_partner_id': self.id},
        }