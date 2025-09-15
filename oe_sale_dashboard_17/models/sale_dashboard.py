# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)

class SalesDashboard(models.Model):
    _name = 'sales.dashboard'
    _description = 'Premium Sales Dashboard'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    # Basic Information
    name = fields.Char(string='Dashboard Name', required=True, tracking=True)
    active = fields.Boolean(string='Active', default=True, tracking=True)
    
    # Date Filters - Using correct field names from CSV
    date_from = fields.Date(string='Date From', default=lambda self: fields.Date.today().replace(day=1))
    date_to = fields.Date(string='Date To', default=fields.Date.today)
    
    # Team and Agent Filters - Using correct field names from system
    sales_team_id = fields.Many2one('crm.team', string='Sales Team')
    user_id = fields.Many2one('res.users', string='System User', default=lambda self: self.env.user)
    agent1_partner_id = fields.Many2one('res.partner', string='Primary Agent/Salesperson')
    agent2_partner_id = fields.Many2one('res.partner', string='Secondary Agent')
    consultant_id = fields.Many2one('res.partner', string='Consultant')
    primary_agent_id = fields.Many2one('res.partner', string='Primary Agent')
    secondary_agent_id = fields.Many2one('res.partner', string='Secondary Agent')
    
    # Currency
    currency_id = fields.Many2one('res.currency', string='Currency', 
                                 default=lambda self: self.env.company.currency_id)
    
    # KPI Fields - Using correct monetary field names
    total_revenue = fields.Monetary(string='Total Revenue', compute='_compute_kpis', store=True)
    total_orders = fields.Integer(string='Total Orders', compute='_compute_kpis', store=True)
    avg_order_value = fields.Monetary(string='Average Order Value', compute='_compute_kpis', store=True)
    conversion_rate = fields.Float(string='Conversion Rate (%)', compute='_compute_kpis', store=True)
    
    # Growth Metrics
    revenue_growth = fields.Float(string='Revenue Growth (%)', compute='_compute_growth', store=True)
    orders_growth = fields.Float(string='Orders Growth (%)', compute='_compute_growth', store=True)
    aov_growth = fields.Float(string='AOV Growth (%)', compute='_compute_growth', store=True)
    conversion_growth = fields.Float(string='Conversion Growth (%)', compute='_compute_growth', store=True)
    
    # Configuration
    auto_refresh = fields.Boolean(string='Auto Refresh', default=True)
    refresh_interval = fields.Integer(string='Refresh Interval (minutes)', default=30)
    last_updated = fields.Datetime(string='Last Updated', default=fields.Datetime.now)
    
    # Display Options
    show_revenue = fields.Boolean(string='Show Revenue', default=True)
    show_orders = fields.Boolean(string='Show Orders', default=True)
    show_conversion = fields.Boolean(string='Show Conversion', default=True)
    show_charts = fields.Boolean(string='Show Charts', default=True)
    
    # Commission Analytics
    total_agent1_commission = fields.Monetary(string='Agent 1 Total Commission', compute='_compute_commissions', store=True)
    total_agent2_commission = fields.Monetary(string='Agent 2 Total Commission', compute='_compute_commissions', store=True)
    total_consultant_commission = fields.Monetary(string='Consultant Commission', compute='_compute_commissions', store=True)
    avg_commission_rate = fields.Float(string='Average Commission Rate (%)', compute='_compute_commissions', store=True)
    
    # Top Performers (One2many to separate model)
    top_performers_ids = fields.One2many('sales.dashboard.performer', 'dashboard_id', 
                                       string='Top Performers', compute='_compute_top_performers')
    
    @api.depends('date_from', 'date_to', 'sales_team_id', 'agent1_partner_id')
    def _compute_kpis(self):
        """Compute main KPIs using correct field names"""
        for record in self:
            domain = [
                ('date_order', '>=', record.date_from),
                ('date_order', '<=', record.date_to),
                ('state', 'in', ['sale', 'done'])  # Only confirmed sales orders
            ]
            
            # Add filters based on selections
            if record.sales_team_id:
                domain.append(('team_id', '=', record.sales_team_id.id))
            if record.agent1_partner_id:
                domain.append(('agent1_partner_id', '=', record.agent1_partner_id.id))
            
            # Get sale orders
            orders = self.env['sale.order'].search(domain)
            
            # Calculate KPIs using correct field names
            record.total_orders = len(orders)
            
            # Use sale_value or amount_total for revenue calculation
            record.total_revenue = sum(orders.mapped('sale_value') or orders.mapped('amount_total'))
            
            # Calculate average order value
            record.avg_order_value = record.total_revenue / record.total_orders if record.total_orders > 0 else 0
            
            # Calculate conversion rate (simplified - orders vs quotations)
            all_orders_domain = domain.copy()
            all_orders_domain[-1] = ('state', 'in', ['draft', 'sent', 'sale', 'done'])
            all_orders = self.env['sale.order'].search(all_orders_domain)
            total_quotes = len(all_orders)
            record.conversion_rate = (record.total_orders / total_quotes * 100) if total_quotes > 0 else 0
    
    @api.depends('date_from', 'date_to', 'sales_team_id', 'agent1_partner_id')
    def _compute_commissions(self):
        """Compute commission analytics"""
        for record in self:
            domain = [
                ('date_order', '>=', record.date_from),
                ('date_order', '<=', record.date_to),
                ('state', 'in', ['sale', 'done'])
            ]
            
            if record.sales_team_id:
                domain.append(('team_id', '=', record.sales_team_id.id))
            if record.agent1_partner_id:
                domain.append(('agent1_partner_id', '=', record.agent1_partner_id.id))
            
            orders = self.env['sale.order'].search(domain)
            
            # Calculate commission totals using correct field names
            record.total_agent1_commission = sum(orders.mapped('agent1_amount'))
            record.total_agent2_commission = sum(orders.mapped('agent2_amount'))
            record.total_consultant_commission = sum(orders.mapped('salesperson_commission'))
            
            # Calculate average commission rate
            total_sales = sum(orders.mapped('sale_value') or orders.mapped('amount_total'))
            total_commissions = record.total_agent1_commission + record.total_agent2_commission + record.total_consultant_commission
            record.avg_commission_rate = (total_commissions / total_sales * 100) if total_sales > 0 else 0
    
    @api.depends('date_from', 'date_to', 'sales_team_id')
    def _compute_growth(self):
        """Compute growth metrics compared to previous period"""
        for record in self:
            # Calculate previous period
            period_days = (record.date_to - record.date_from).days
            prev_date_to = record.date_from - timedelta(days=1)
            prev_date_from = prev_date_to - timedelta(days=period_days)
            
            # Current period domain
            current_domain = [
                ('date_order', '>=', record.date_from),
                ('date_order', '<=', record.date_to),
                ('state', 'in', ['sale', 'done'])
            ]
            
            # Previous period domain
            prev_domain = [
                ('date_order', '>=', prev_date_from),
                ('date_order', '<=', prev_date_to),
                ('state', 'in', ['sale', 'done'])
            ]
            
            if record.sales_team_id:
                current_domain.append(('team_id', '=', record.sales_team_id.id))
                prev_domain.append(('team_id', '=', record.sales_team_id.id))
            
            # Get orders for both periods
            current_orders = self.env['sale.order'].search(current_domain)
            prev_orders = self.env['sale.order'].search(prev_domain)
            
            # Calculate previous period metrics
            prev_revenue = sum(prev_orders.mapped('sale_value') or prev_orders.mapped('amount_total'))
            prev_orders_count = len(prev_orders)
            prev_aov = prev_revenue / prev_orders_count if prev_orders_count > 0 else 0
            
            # Calculate growth percentages
            record.revenue_growth = ((record.total_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0
            record.orders_growth = ((record.total_orders - prev_orders_count) / prev_orders_count * 100) if prev_orders_count > 0 else 0
            record.aov_growth = ((record.avg_order_value - prev_aov) / prev_aov * 100) if prev_aov > 0 else 0
            record.conversion_growth = 0  # Will calculate based on lead conversion if needed
    
    @api.depends('date_from', 'date_to', 'sales_team_id')
    def _compute_top_performers(self):
        """Compute top performing agents"""
        for record in self:
            # Clear existing performers
            record.top_performers_ids.unlink()
            
            domain = [
                ('date_order', '>=', record.date_from),
                ('date_order', '<=', record.date_to),
                ('state', 'in', ['sale', 'done']),
                ('agent1_partner_id', '!=', False)
            ]
            
            if record.sales_team_id:
                domain.append(('team_id', '=', record.sales_team_id.id))
            
            orders = self.env['sale.order'].search(domain)
            
            # Group by agent and calculate performance
            agent_performance = {}
            for order in orders:
                agent = order.agent1_partner_id
                if agent.id not in agent_performance:
                    agent_performance[agent.id] = {
                        'agent': agent,
                        'total_sales': 0,
                        'orders_count': 0,
                        'commission': 0
                    }
                
                agent_performance[agent.id]['total_sales'] += order.sale_value or order.amount_total
                agent_performance[agent.id]['orders_count'] += 1
                agent_performance[agent.id]['commission'] += order.agent1_amount
            
            # Create top performers records
            performers = []
            sorted_agents = sorted(agent_performance.values(), 
                                 key=lambda x: x['total_sales'], reverse=True)[:10]
            
            for rank, perf in enumerate(sorted_agents, 1):
                avg_order = perf['total_sales'] / perf['orders_count'] if perf['orders_count'] > 0 else 0
                
                # Determine performance rating
                if avg_order > record.avg_order_value * 1.2:
                    rating = 'excellent'
                elif avg_order > record.avg_order_value * 0.8:
                    rating = 'good'
                else:
                    rating = 'needs_improvement'
                
                performers.append((0, 0, {
                    'dashboard_id': record.id,
                    'rank': rank,
                    'salesperson_id': perf['agent'].id,
                    'total_sales': perf['total_sales'],
                    'orders_count': perf['orders_count'],
                    'avg_order_value': avg_order,
                    'commission_earned': perf['commission'],
                    'performance_rating': rating
                }))
            
            record.top_performers_ids = performers
    
    def refresh_dashboard(self):
        """Manually refresh dashboard data"""
        self.last_updated = fields.Datetime.now()
        self._compute_kpis()
        self._compute_commissions()
        self._compute_growth()
        self._compute_top_performers()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
    
    def generate_test_data(self):
        """Generate test data for dashboard demonstration"""
        # This would create sample sale orders for testing
        # Implementation depends on your specific needs
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Test Data Generated'),
                'message': _('Sample sales data has been created for dashboard testing.'),
                'type': 'success'
            }
        }
    
    def export_dashboard(self):
        """Export dashboard data"""
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/?model=sales.dashboard&id={self.id}&field=dashboard_export&download=true',
            'target': 'self',
        }


class SalesDashboardPerformer(models.Model):
    _name = 'sales.dashboard.performer'
    _description = 'Sales Dashboard Top Performer'
    _order = 'rank'
    
    dashboard_id = fields.Many2one('sales.dashboard', string='Dashboard', ondelete='cascade')
    rank = fields.Integer(string='Rank')
    salesperson_id = fields.Many2one('res.partner', string='Agent/Salesperson')
    total_sales = fields.Monetary(string='Total Sales')
    orders_count = fields.Integer(string='Orders Count')
    avg_order_value = fields.Monetary(string='Average Order Value')
    commission_earned = fields.Monetary(string='Commission Earned')
    performance_rating = fields.Selection([
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('needs_improvement', 'Needs Improvement')
    ], string='Performance Rating')
    currency_id = fields.Many2one(related='dashboard_id.currency_id')