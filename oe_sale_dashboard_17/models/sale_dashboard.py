# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)

class SalesDashboard(models.Model):
    _name = 'sales.dashboard'
    _description = 'Comprehensive Sales Dashboard'
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
    
    # Invoice & Payment KPIs
    total_invoiced = fields.Monetary(string='Total Invoiced', compute='_compute_invoice_kpis', store=True)
    total_paid = fields.Monetary(string='Total Payments Received', compute='_compute_invoice_kpis', store=True)
    total_outstanding = fields.Monetary(string='Outstanding Invoices', compute='_compute_invoice_kpis', store=True)
    uninvoiced_amount = fields.Monetary(string='Uninvoiced Sales', compute='_compute_invoice_kpis', store=True)
    
    # Balance Analytics
    total_receivables = fields.Monetary(string='Total Receivables', compute='_compute_balance_kpis', store=True)
    total_payables = fields.Monetary(string='Total Payables', compute='_compute_balance_kpis', store=True)
    net_balance = fields.Monetary(string='Net Balance', compute='_compute_balance_kpis', store=True)
    overdue_amount = fields.Monetary(string='Overdue Amount', compute='_compute_balance_kpis', store=True)
    
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
                # Check if agent field exists
                if 'agent1_partner_id' in self.env['sale.order']._fields:
                    domain.append(('agent1_partner_id', '=', record.agent1_partner_id.id))
            
            # Get sale orders
            orders = self.env['sale.order'].search(domain)
            
            # Calculate KPIs using safe field access
            record.total_orders = len(orders)
            
            # Use amount_total as the primary field
            record.total_revenue = sum(orders.mapped('amount_total'))
            
            # Calculate average order value
            record.avg_order_value = record.total_revenue / record.total_orders if record.total_orders > 0 else 0
            
            # Calculate conversion rate (simplified - orders vs quotations)
            all_orders_domain = domain.copy()
            all_orders_domain[-1] = ('state', 'in', ['draft', 'sent', 'sale', 'done'])
            all_orders = self.env['sale.order'].search(all_orders_domain)
            total_quotes = len(all_orders)
            record.conversion_rate = (record.total_orders / total_quotes * 100) if total_quotes > 0 else 0
    
    @api.depends('date_from', 'date_to', 'sales_team_id')
    def _compute_invoice_kpis(self):
        """Compute invoice and payment KPIs"""
        for record in self:
            # Invoice analytics
            invoice_domain = [
                ('invoice_date', '>=', record.date_from),
                ('invoice_date', '<=', record.date_to),
                ('move_type', 'in', ['out_invoice', 'out_refund']),
                ('state', '=', 'posted')
            ]
            
            if record.sales_team_id:
                # Link invoices through sales orders if possible
                so_domain = [('team_id', '=', record.sales_team_id.id)]
                sales_orders = self.env['sale.order'].search(so_domain)
                if sales_orders:
                    invoice_domain.append(('partner_id', 'in', sales_orders.mapped('partner_id').ids))
            
            invoices = self.env['account.move'].search(invoice_domain)
            record.total_invoiced = sum(invoices.mapped('amount_total'))
            
            # Payment analytics
            paid_invoices = invoices.filtered(lambda inv: inv.payment_state == 'paid')
            record.total_paid = sum(paid_invoices.mapped('amount_total'))
            
            # Outstanding invoices
            outstanding_invoices = invoices.filtered(lambda inv: inv.payment_state in ['not_paid', 'partial'])
            record.total_outstanding = sum(outstanding_invoices.mapped('amount_residual'))
            
            # Uninvoiced sales orders
            uninvoiced_domain = [
                ('date_order', '>=', record.date_from),
                ('date_order', '<=', record.date_to),
                ('state', 'in', ['sale', 'done']),
                ('invoice_status', 'in', ['to invoice', 'no'])
            ]
            
            if record.sales_team_id:
                uninvoiced_domain.append(('team_id', '=', record.sales_team_id.id))
            
            uninvoiced_orders = self.env['sale.order'].search(uninvoiced_domain)
            record.uninvoiced_amount = sum(uninvoiced_orders.mapped('amount_total'))
    
    @api.depends('date_from', 'date_to', 'sales_team_id')
    def _compute_balance_kpis(self):
        """Compute balance and receivables KPIs"""
        for record in self:
            # Get partners related to sales team if specified
            partner_domain = []
            if record.sales_team_id:
                so_domain = [('team_id', '=', record.sales_team_id.id)]
                sales_orders = self.env['sale.order'].search(so_domain)
                if sales_orders:
                    partner_domain = [('id', 'in', sales_orders.mapped('partner_id').ids)]
            
            # Receivables analysis
            receivable_domain = [
                ('account_id.account_type', '=', 'asset_receivable'),
                ('reconciled', '=', False),
                ('company_id', '=', self.env.company.id)
            ]
            
            if partner_domain:
                receivable_domain.extend(partner_domain)
            
            receivable_lines = self.env['account.move.line'].search(receivable_domain)
            record.total_receivables = sum(receivable_lines.mapped('amount_residual'))
            
            # Payables analysis  
            payable_domain = [
                ('account_id.account_type', '=', 'liability_payable'),
                ('reconciled', '=', False),
                ('company_id', '=', self.env.company.id)
            ]
            
            if partner_domain:
                payable_domain.extend(partner_domain)
            
            payable_lines = self.env['account.move.line'].search(payable_domain)
            record.total_payables = sum(payable_lines.mapped('amount_residual'))
            
            # Net balance
            record.net_balance = record.total_receivables - record.total_payables
            
            # Overdue analysis
            today = fields.Date.today()
            overdue_domain = receivable_domain + [
                ('date_maturity', '<', today)
            ]
            overdue_lines = self.env['account.move.line'].search(overdue_domain)
            record.overdue_amount = sum(overdue_lines.mapped('amount_residual'))
    
    @api.depends('date_from', 'date_to', 'sales_team_id')
    def _compute_top_performers(self):
        """Compute top performing agents and revenue generators"""
        TopPerformer = self.env['sales.dashboard.performer']
        for record in self:
            # Clear existing performers
            record.top_performers_ids.unlink()
            
            domain = [
                ('date_order', '>=', record.date_from),
                ('date_order', '<=', record.date_to),
                ('state', 'in', ['sale', 'done'])
            ]
            
            if record.sales_team_id:
                domain.append(('team_id', '=', record.sales_team_id.id))
            
            # Check if agent field exists
            if 'agent1_partner_id' in self.env['sale.order']._fields:
                domain.append(('agent1_partner_id', '!=', False))
            
            # Get all orders
            orders = self.env['sale.order'].search(domain)
            
            # Analyze by sales person or agent
            agent_performance = {}
            for order in orders:
                agent = None
                commission = 0
                
                # Try different agent fields
                if hasattr(order, 'agent1_partner_id') and order.agent1_partner_id:
                    agent = order.agent1_partner_id
                    commission = getattr(order, 'agent1_amount', 0) or 0
                elif hasattr(order, 'user_id') and order.user_id.partner_id:
                    agent = order.user_id.partner_id
                    commission = 0
                
                if agent:
                    if agent.id not in agent_performance:
                        agent_performance[agent.id] = {
                            'partner': agent,
                            'total_revenue': 0,
                            'total_orders': 0,
                            'total_commission': 0
                        }
                    
                    agent_performance[agent.id]['total_revenue'] += order.amount_total
                    agent_performance[agent.id]['total_orders'] += 1
                    agent_performance[agent.id]['total_commission'] += commission
            
            # Create top performer records sorted by revenue
            sorted_performers = sorted(agent_performance.values(), 
                                     key=lambda x: x['total_revenue'], reverse=True)
            
            for i, performer_data in enumerate(sorted_performers[:10]):  # Top 10
                TopPerformer.create({
                    'dashboard_id': record.id,
                    'partner_id': performer_data['partner'].id,
                    'rank': i + 1,
                    'total_revenue': performer_data['total_revenue'],
                    'total_orders': performer_data['total_orders'],
                    'total_commission': performer_data['total_commission'],
                    'avg_order_value': performer_data['total_revenue'] / performer_data['total_orders'] if performer_data['total_orders'] > 0 else 0
                })
    
    # Helper methods for dashboard data
    def get_sales_trend_data(self):
        """Get sales trend data for charts"""
        self.ensure_one()
        
        # Calculate daily sales for the period
        daily_sales = {}
        current_date = self.date_from
        
        while current_date <= self.date_to:
            domain = [
                ('date_order', '=', current_date),
                ('state', 'in', ['sale', 'done'])
            ]
            
            if self.sales_team_id:
                domain.append(('team_id', '=', self.sales_team_id.id))
            
            orders = self.env['sale.order'].search(domain)
            daily_sales[current_date.strftime('%Y-%m-%d')] = sum(orders.mapped('amount_total'))
            current_date += timedelta(days=1)
        
        return daily_sales
    
    def get_invoice_payment_data(self):
        """Get invoice vs payment data for charts"""
        self.ensure_one()
        
        # Monthly invoice vs payment data
        monthly_data = {}
        start_date = self.date_from.replace(day=1)
        
        while start_date <= self.date_to:
            month_key = start_date.strftime('%Y-%m')
            
            # Get month end
            if start_date.month == 12:
                month_end = start_date.replace(year=start_date.year + 1, month=1) - timedelta(days=1)
            else:
                month_end = start_date.replace(month=start_date.month + 1) - timedelta(days=1)
            
            month_end = min(month_end, self.date_to)
            
            # Invoice data
            invoice_domain = [
                ('invoice_date', '>=', start_date),
                ('invoice_date', '<=', month_end),
                ('move_type', 'in', ['out_invoice', 'out_refund']),
                ('state', '=', 'posted')
            ]
            
            invoices = self.env['account.move'].search(invoice_domain)
            invoiced = sum(invoices.mapped('amount_total'))
            paid = sum(invoices.filtered(lambda inv: inv.payment_state == 'paid').mapped('amount_total'))
            
            monthly_data[month_key] = {
                'invoiced': invoiced,
                'paid': paid,
                'outstanding': invoiced - paid
            }
            
            # Move to next month
            if start_date.month == 12:
                start_date = start_date.replace(year=start_date.year + 1, month=1)
            else:
                start_date = start_date.replace(month=start_date.month + 1)
        
        return monthly_data
    
    # Action Methods for Dashboard Navigation
    def action_view_sales_details(self):
        """Action to view detailed sales orders"""
        self.ensure_one()
        
        domain = [
            ('date_order', '>=', self.date_from),
            ('date_order', '<=', self.date_to),
            ('state', 'in', ['sale', 'done'])
        ]
        
        if self.sales_team_id:
            domain.append(('team_id', '=', self.sales_team_id.id))
        if self.agent1_partner_id:
            domain.append(('agent1_partner_id', '=', self.agent1_partner_id.id))
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sales Orders - Details',
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'domain': domain,
            'context': {'search_default_group_by_date': 1}
        }
    
    def action_view_top_performers(self):
        """Action to view top performers"""
        self.ensure_one()
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Top Performers',
            'res_model': 'sales.dashboard.performer',
            'view_mode': 'kanban,tree,form',
            'domain': [('dashboard_id', '=', self.id)],
            'context': {'search_default_group_by_rank': 1}
        }
    
    def action_view_invoice_details(self):
        """Action to view invoice details"""
        self.ensure_one()
        
        domain = [
            ('invoice_date', '>=', self.date_from),
            ('invoice_date', '<=', self.date_to),
            ('move_type', 'in', ['out_invoice', 'out_refund']),
            ('state', '=', 'posted')
        ]
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoices - Details',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': domain,
            'context': {'search_default_group_by_date': 1}
        }
    
    def action_view_payment_details(self):
        """Action to view payment details"""
        self.ensure_one()
        
        # Get invoices in the period
        invoice_domain = [
            ('invoice_date', '>=', self.date_from),
            ('invoice_date', '<=', self.date_to),
            ('move_type', 'in', ['out_invoice', 'out_refund']),
            ('state', '=', 'posted'),
            ('payment_state', '=', 'paid')
        ]
        
        invoices = self.env['account.move'].search(invoice_domain)
        
        # Get payments related to these invoices
        payment_domain = [
            ('reconciled_invoice_ids', 'in', invoices.ids),
            ('state', '=', 'posted')
        ]
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Payments - Details',
            'res_model': 'account.payment',
            'view_mode': 'tree,form',
            'domain': payment_domain,
            'context': {'search_default_group_by_date': 1}
        }
    
    def action_view_receivables(self):
        """Action to view receivables details"""
        self.ensure_one()
        
        domain = [
            ('account_id.account_type', '=', 'asset_receivable'),
            ('reconciled', '=', False),
            ('company_id', '=', self.env.company.id)
        ]
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Receivables - Details',
            'res_model': 'account.move.line',
            'view_mode': 'tree,form',
            'domain': domain,
            'context': {'search_default_group_by_partner': 1}
        }
    
    def action_view_overdue(self):
        """Action to view overdue items"""
        self.ensure_one()
        
        today = fields.Date.today()
        domain = [
            ('account_id.account_type', '=', 'asset_receivable'),
            ('reconciled', '=', False),
            ('date_maturity', '<', today),
            ('company_id', '=', self.env.company.id)
        ]
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Overdue Items',
            'res_model': 'account.move.line',
            'view_mode': 'tree,form',
            'domain': domain,
            'context': {'search_default_group_by_partner': 1}
        }


class SalesDashboardPerformer(models.Model):
    _name = 'sales.dashboard.performer'
    _description = 'Sales Dashboard Top Performer'
    _order = 'rank asc'
    
    dashboard_id = fields.Many2one('sales.dashboard', string='Dashboard', required=True, ondelete='cascade')
    partner_id = fields.Many2one('res.partner', string='Salesperson/Agent', required=True)
    rank = fields.Integer(string='Rank')
    total_revenue = fields.Monetary(string='Total Revenue')
    total_orders = fields.Integer(string='Total Orders')
    total_commission = fields.Monetary(string='Total Commission')
    avg_order_value = fields.Monetary(string='Average Order Value')
    currency_id = fields.Many2one('res.currency', string='Currency', 
                                 default=lambda self: self.env.company.currency_id)
    
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
            if record.agent1_partner_id and 'agent1_partner_id' in self.env['sale.order']._fields:
                domain.append(('agent1_partner_id', '=', record.agent1_partner_id.id))
            
            orders = self.env['sale.order'].search(domain)
            
            # Calculate commission totals using safe field access
            so_fields = self.env['sale.order']._fields
            agent1_amount = 0
            agent2_amount = 0
            salesperson_commission = 0
            
            if 'agent1_amount' in so_fields:
                agent1_amount = sum(orders.mapped('agent1_amount'))
            if 'agent2_amount' in so_fields:
                agent2_amount = sum(orders.mapped('agent2_amount'))
            if 'salesperson_commission' in so_fields:
                salesperson_commission = sum(orders.mapped('salesperson_commission'))
            
            record.total_agent1_commission = agent1_amount
            record.total_agent2_commission = agent2_amount
            record.total_consultant_commission = salesperson_commission
            
            # Calculate average commission rate
            total_sales = sum(orders.mapped('amount_total'))
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