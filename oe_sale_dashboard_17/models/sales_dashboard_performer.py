# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class SalesDashboardPerformer(models.Model):
    _name = 'sales.dashboard.performer'
    _description = 'Sales Dashboard Performer'
    _order = 'performance_score desc'
    
    name = fields.Char(string='Name', compute='_compute_name', store=True)
    user_id = fields.Many2one('res.users', string='User')
    partner_id = fields.Many2one('res.partner', string='Partner')
    
    dashboard_id = fields.Many2one('sales.dashboard', string='Dashboard', ondelete='cascade')
    date_from = fields.Date(string='Date From', related='dashboard_id.date_from', store=True)
    date_to = fields.Date(string='Date To', related='dashboard_id.date_to', store=True)
    
    # Performance metrics
    total_orders = fields.Integer(string='Total Orders')
    total_revenue = fields.Monetary(string='Total Revenue')
    currency_id = fields.Many2one('res.currency', string='Currency', 
                                 default=lambda self: self.env.company.currency_id)
    average_order_value = fields.Monetary(string='Average Order Value', compute='_compute_averages', store=True)
    conversion_rate = fields.Float(string='Conversion Rate (%)')
    performance_score = fields.Float(string='Performance Score', compute='_compute_performance_score', store=True)
    
    # Rank display
    rank = fields.Integer(string='Rank')
    rank_icon = fields.Char(string='Rank Icon', compute='_compute_rank_icon')
    
    @api.depends('user_id', 'partner_id')
    def _compute_name(self):
        for performer in self:
            if performer.user_id:
                performer.name = performer.user_id.name
            elif performer.partner_id:
                performer.name = performer.partner_id.name
            else:
                performer.name = _('Unknown Performer')
    
    @api.depends('total_orders', 'total_revenue')
    def _compute_averages(self):
        for performer in self:
            performer.average_order_value = performer.total_revenue / performer.total_orders if performer.total_orders else 0.0
    
    @api.depends('total_revenue', 'total_orders', 'conversion_rate')
    def _compute_performance_score(self):
        for performer in self:
            # Weighted score calculation
            revenue_weight = 0.5  # 50% weight on revenue
            orders_weight = 0.3   # 30% weight on number of orders
            conv_weight = 0.2     # 20% weight on conversion rate
            
            # Normalize values (we'd need max values for proper normalization, but using a simplified approach here)
            max_revenue = 100000  # Placeholder - ideally dynamically calculated
            max_orders = 100      # Placeholder - ideally dynamically calculated
            
            norm_revenue = min(1.0, performer.total_revenue / max_revenue if max_revenue else 0)
            norm_orders = min(1.0, performer.total_orders / max_orders if max_orders else 0)
            norm_conv = min(1.0, performer.conversion_rate / 100)
            
            # Calculate weighted score
            performer.performance_score = (
                (norm_revenue * revenue_weight) + 
                (norm_orders * orders_weight) + 
                (norm_conv * conv_weight)
            ) * 100  # Scale to 0-100
    
    def _compute_rank_icon(self):
        for performer in self:
            if performer.rank == 1:
                performer.rank_icon = '🥇'  # Gold medal
            elif performer.rank == 2:
                performer.rank_icon = '🥈'  # Silver medal
            elif performer.rank == 3:
                performer.rank_icon = '🥉'  # Bronze medal
            else:
                performer.rank_icon = str(performer.rank)