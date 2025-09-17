# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    """Extend Partner to add commission statement functionality"""
    _inherit = 'res.partner'

    # Commission Lines Integration
    commission_line_ids = fields.One2many(
        'commission.line', 
        'partner_id', 
        string='Commission Lines',
        help='Commission lines for this partner'
    )
    
    commission_line_count = fields.Integer(
        string='Commission Lines Count',
        compute='_compute_commission_counts',
        help='Number of commission lines for this partner'
    )
    
    total_commission_amount = fields.Monetary(
        string='Total Commission Amount',
        compute='_compute_commission_counts',
        currency_field='currency_id',
        help='Total commission amount for this partner'
    )
    
    commission_lines_this_year = fields.Integer(
        string='Commission Lines This Year',
        compute='_compute_commission_counts',
        help='Number of commission lines this year'
    )
    
    commission_amount_this_year = fields.Monetary(
        string='Commission Amount This Year',
        compute='_compute_commission_counts',
        currency_field='currency_id',
        help='Commission amount this year'
    )
    
    # Commission Agent Fields
    is_commission_agent = fields.Boolean(
        string='Is Commission Agent',
        default=False,
        help='Check if this partner is a commission agent'
    )
    
    commission_rate = fields.Float(
        string='Default Commission Rate (%)',
        default=0.0,
        help='Default commission rate percentage for this agent'
    )

    # ============================================================================
    # COMPUTE METHODS
    # ============================================================================
    
    @api.depends('commission_line_ids', 'commission_line_ids.commission_amount', 
                 'commission_line_ids.state', 'commission_line_ids.booking_date')
    def _compute_commission_counts(self):
        """Compute commission statistics"""
        current_year = fields.Date.today().year
        
        for partner in self:
            commission_lines = partner.commission_line_ids.filtered(lambda l: l.state != 'cancelled')
            partner.commission_line_count = len(commission_lines)
            partner.total_commission_amount = sum(commission_lines.mapped('commission_amount'))
            
            # This year statistics
            this_year_lines = commission_lines.filtered(
                lambda l: l.booking_date and l.booking_date.year == current_year
            )
            partner.commission_lines_this_year = len(this_year_lines)
            partner.commission_amount_this_year = sum(this_year_lines.mapped('commission_amount'))

    # ============================================================================
    # ACTION METHODS
    # ============================================================================
    
    def action_view_commission_lines(self):
        """View commission lines for this partner"""
        self.ensure_one()
        action = self.env.ref('commission_lines.action_commission_line').read()[0]
        action['domain'] = [('partner_id', '=', self.id)]
        action['context'] = {
            'default_partner_id': self.id,
            'create': False,
        }
        return action
    
    def action_generate_commission_statement(self):
        """Generate commission statement for this partner"""
        self.ensure_one()
        
        # Check if partner has commission lines
        if not self.commission_line_ids:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Commission Lines'),
                    'message': _('This partner has no commission lines.'),
                    'type': 'warning',
                }
            }
        
        # Open commission statement wizard with this partner pre-selected
        context = {
            'default_partner_id': self.id,
            'default_date_from': fields.Date.today().replace(day=1),
            'default_date_to': fields.Date.today(),
        }
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Commission Statement'),
            'res_model': 'commission.statement.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': context,
        }
    
    def action_commission_summary(self):
        """Show commission summary for this partner"""
        self.ensure_one()
        
        summary_data = self._get_commission_summary()
        
        message = _("""
Commission Summary for %s:

Total Commission Lines: %d
Total Commission Amount: %.2f %s
Commission Lines This Year: %d  
Commission Amount This Year: %.2f %s

Status Breakdown:
- Draft: %d lines
- Calculated: %d lines
- Approved: %d lines
- Billed: %d lines
- Paid: %d lines
        """) % (
            self.name,
            self.commission_line_count,
            self.total_commission_amount,
            self.currency_id.name,
            self.commission_lines_this_year,
            self.commission_amount_this_year,
            self.currency_id.name,
            summary_data['draft_count'],
            summary_data['calculated_count'],
            summary_data['approved_count'],
            summary_data['billed_count'],
            summary_data['paid_count'],
        )
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Commission Summary'),
                'message': message,
                'type': 'info',
                'sticky': True,
            }
        }

    # ============================================================================
    # HELPER METHODS
    # ============================================================================
    
    def _get_commission_summary(self):
        """Get commission summary data"""
        commission_lines = self.commission_line_ids.filtered(lambda l: l.state != 'cancelled')
        
        return {
            'draft_count': len(commission_lines.filtered(lambda l: l.state == 'draft')),
            'calculated_count': len(commission_lines.filtered(lambda l: l.state == 'calculated')),
            'approved_count': len(commission_lines.filtered(lambda l: l.state == 'approved')),
            'billed_count': len(commission_lines.filtered(lambda l: l.state == 'billed')),
            'paid_count': len(commission_lines.filtered(lambda l: l.state == 'paid')),
        }