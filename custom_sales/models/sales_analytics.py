# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools
from datetime import datetime, timedelta
import json
import logging

_logger = logging.getLogger(__name__)

class CustomSalesAnalytics(models.Model):
    _name = 'custom.sales.analytics'
    _description = 'Sales Analytics and Reporting'
    _auto = False
    
    # Date fields
    date = fields.Date(string='Date')
    month = fields.Char(string='Month')
    quarter = fields.Char(string='Quarter')
    year = fields.Char(string='Year')
    
    # Sales data
    order_count = fields.Integer(string='Order Count')
    total_revenue = fields.Monetary(string='Total Revenue', currency_field='currency_id')
    average_order_value = fields.Monetary(string='Average Order Value', currency_field='currency_id')
    
    # Customer data
    customer_id = fields.Many2one('res.partner', string='Customer')
    customer_type = fields.Selection([
        ('new', 'New Customer'),
        ('existing', 'Existing Customer'),
        ('vip', 'VIP Customer'),
        ('corporate', 'Corporate Customer'),
    ], string='Customer Type')
    
    # Sales team data
    sales_team_id = fields.Many2one('crm.team', string='Sales Team')
    salesperson_id = fields.Many2one('res.users', string='Salesperson')
    
    # Product data
    product_id = fields.Many2one('product.product', string='Product')
    category_id = fields.Many2one('product.category', string='Product Category')
    
    # Status and metrics
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Quotation Sent'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('delivered', 'Delivered'),
        ('invoiced', 'Invoiced'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ], string='Status')
    
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Very High'),
    ], string='Priority')
    
    profit_margin = fields.Float(string='Profit Margin (%)')
    currency_id = fields.Many2one('res.currency', string='Currency')
    
    def init(self):
        """Create the analytics view"""
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    ROW_NUMBER() OVER() as id,
                    DATE(cso.create_date) as date,
                    TO_CHAR(cso.create_date, 'YYYY-MM') as month,
                    TO_CHAR(cso.create_date, 'YYYY-Q') as quarter,
                    TO_CHAR(cso.create_date, 'YYYY') as year,
                    COUNT(cso.id) as order_count,
                    SUM(cso.actual_revenue) as total_revenue,
                    AVG(cso.actual_revenue) as average_order_value,
                    cso.custom_field_3 as customer_id,
                    cso.customer_type,
                    cso.sales_team_id,
                    cso.sales_person_id as salesperson_id,
                    NULL as product_id,
                    NULL as category_id,
                    cso.state,
                    cso.priority,
                    AVG(cso.profit_margin) as profit_margin,
                    cso.currency_id
                FROM custom_sales_order cso
                WHERE cso.create_date IS NOT NULL
                GROUP BY
                    DATE(cso.create_date),
                    TO_CHAR(cso.create_date, 'YYYY-MM'),
                    TO_CHAR(cso.create_date, 'YYYY-Q'),
                    TO_CHAR(cso.create_date, 'YYYY'),
                    cso.custom_field_3,
                    cso.customer_type,
                    cso.sales_team_id,
                    cso.sales_person_id,
                    cso.state,
                    cso.priority,
                    cso.currency_id
            )
        """ % self._table)


class SalesKPICalculator(models.TransientModel):
    _name = 'sales.kpi.calculator'
    _description = 'Sales KPI Calculator'
    
    @api.model
    def calculate_kpi(self, kpi_config, date_from=None, date_to=None, domain=None):
        """Calculate KPI value based on configuration"""
        try:
            model = self.env[kpi_config.model_name]
            
            # Build domain
            kpi_domain = []
            if domain:
                kpi_domain.extend(domain)
            
            # Add date filter if specified
            if date_from and date_to and kpi_config.date_field:
                kpi_domain.extend([
                    (kpi_config.date_field, '>=', date_from),
                    (kpi_config.date_field, '<=', date_to)
                ])
            
            # Add custom domain from KPI config
            if kpi_config.domain:
                try:
                    custom_domain = eval(kpi_config.domain)
                    if isinstance(custom_domain, list):
                        kpi_domain.extend(custom_domain)
                except Exception as e:
                    _logger.error(f"Error evaluating KPI domain: {e}")
            
            # Calculate value based on calculation type
            if kpi_config.calculation_type == 'count':
                value = model.search_count(kpi_domain)
            else:
                records = model.search(kpi_domain)
                if not records:
                    value = 0
                else:
                    field_values = records.mapped(kpi_config.field_name)
                    field_values = [v for v in field_values if v is not None]
                    
                    if not field_values:
                        value = 0
                    elif kpi_config.calculation_type == 'sum':
                        value = sum(field_values)
                    elif kpi_config.calculation_type == 'avg':
                        value = sum(field_values) / len(field_values)
                    elif kpi_config.calculation_type == 'max':
                        value = max(field_values)
                    elif kpi_config.calculation_type == 'min':
                        value = min(field_values)
                    else:
                        value = 0
            
            return value
        
        except Exception as e:
            _logger.error(f"Error calculating KPI {kpi_config.code}: {e}")
            return 0
    
    @api.model
    def get_dashboard_kpis(self, dashboard_config_id=None, date_from=None, date_to=None):
        """Get all KPIs for dashboard"""
        if not dashboard_config_id:
            dashboard_config = self.env['custom.sales.dashboard.config'].get_default_dashboard()
        else:
            dashboard_config = self.env['custom.sales.dashboard.config'].browse(dashboard_config_id)
        
        if not dashboard_config:
            return []
        
        kpis = []
        for kpi_config in dashboard_config.kpi_config_ids.filtered('is_active'):
            value = self.calculate_kpi(kpi_config, date_from, date_to)
            
            # Calculate comparison if enabled
            comparison_value = None
            comparison_percentage = None
            
            if kpi_config.enable_comparison and date_from and date_to:
                comparison_value = self._calculate_comparison_value(
                    kpi_config, date_from, date_to
                )
                if comparison_value and value:
                    comparison_percentage = ((value - comparison_value) / comparison_value) * 100
            
            kpis.append({
                'name': kpi_config.name,
                'code': kpi_config.code,
                'value': value,
                'format_type': kpi_config.format_type,
                'icon': kpi_config.icon,
                'color': kpi_config.color,
                'comparison_value': comparison_value,
                'comparison_percentage': comparison_percentage,
            })
        
        return kpis
    
    def _calculate_comparison_value(self, kpi_config, date_from, date_to):
        """Calculate comparison value for previous period"""
        try:
            date_from = fields.Date.from_string(date_from) if isinstance(date_from, str) else date_from
            date_to = fields.Date.from_string(date_to) if isinstance(date_to, str) else date_to
            
            period_length = (date_to - date_from).days
            
            if kpi_config.comparison_period == 'previous_period':
                comp_date_to = date_from - timedelta(days=1)
                comp_date_from = comp_date_to - timedelta(days=period_length)
            elif kpi_config.comparison_period == 'same_period_last_year':
                comp_date_from = date_from.replace(year=date_from.year - 1)
                comp_date_to = date_to.replace(year=date_to.year - 1)
            else:
                return None
            
            return self.calculate_kpi(
                kpi_config,
                comp_date_from.strftime('%Y-%m-%d'),
                comp_date_to.strftime('%Y-%m-%d')
            )
        
        except Exception as e:
            _logger.error(f"Error calculating comparison value: {e}")
            return None


class SalesChartGenerator(models.TransientModel):
    _name = 'sales.chart.generator'
    _description = 'Sales Chart Data Generator'
    
    @api.model
    def generate_chart_data(self, chart_config, date_from=None, date_to=None, domain=None):
        """Generate chart data based on configuration"""
        try:
            model = self.env[chart_config.model_name]
            
            # Build domain
            chart_domain = []
            if domain:
                chart_domain.extend(domain)
            
            # Add date filter if specified
            if date_from and date_to:
                chart_domain.extend([
                    ('create_date', '>=', date_from),
                    ('create_date', '<=', date_to)
                ])
            
            # Add custom domain from chart config
            if chart_config.domain:
                try:
                    custom_domain = eval(chart_config.domain)
                    if isinstance(custom_domain, list):
                        chart_domain.extend(custom_domain)
                except Exception as e:
                    _logger.error(f"Error evaluating chart domain: {e}")
            
            # Get records
            records = model.search(chart_domain, limit=chart_config.limit or 100)
            
            # Generate chart data based on chart type
            if chart_config.chart_type in ['pie', 'doughnut']:
                return self._generate_pie_chart_data(records, chart_config)
            else:
                return self._generate_xy_chart_data(records, chart_config)
        
        except Exception as e:
            _logger.error(f"Error generating chart data: {e}")
            return {'labels': [], 'datasets': []}
    
    def _generate_pie_chart_data(self, records, chart_config):
        """Generate pie chart data"""
        data = {}
        
        for record in records:
            label = getattr(record, chart_config.x_field, 'Unknown')
            if hasattr(label, 'name'):
                label = label.name
            
            value = getattr(record, chart_config.y_field, 0)
            
            if label in data:
                data[label] += value
            else:
                data[label] = value
        
        return {
            'labels': list(data.keys()),
            'datasets': [{
                'data': list(data.values()),
                'backgroundColor': self._get_chart_colors(len(data)),
            }]
        }
    
    def _generate_xy_chart_data(self, records, chart_config):
        """Generate XY chart data"""
        data = {}
        
        if chart_config.group_by_field:
            # Group data by field
            for record in records:
                group_value = getattr(record, chart_config.group_by_field, 'Unknown')
                if hasattr(group_value, 'name'):
                    group_value = group_value.name
                
                x_value = getattr(record, chart_config.x_field, '')
                y_value = getattr(record, chart_config.y_field, 0)
                
                if group_value not in data:
                    data[group_value] = {}
                
                if x_value in data[group_value]:
                    data[group_value][x_value] += y_value
                else:
                    data[group_value][x_value] = y_value
            
            # Convert to chart.js format
            labels = list(set().union(*[d.keys() for d in data.values()]))
            labels.sort()
            
            datasets = []
            colors = self._get_chart_colors(len(data))
            
            for i, (group, group_data) in enumerate(data.items()):
                datasets.append({
                    'label': str(group),
                    'data': [group_data.get(label, 0) for label in labels],
                    'backgroundColor': colors[i % len(colors)],
                    'borderColor': colors[i % len(colors)],
                })
            
            return {
                'labels': labels,
                'datasets': datasets
            }
        else:
            # Simple XY data
            labels = []
            values = []
            
            for record in records:
                x_value = getattr(record, chart_config.x_field, '')
                y_value = getattr(record, chart_config.y_field, 0)
                
                labels.append(str(x_value))
                values.append(y_value)
            
            return {
                'labels': labels,
                'datasets': [{
                    'label': chart_config.name,
                    'data': values,
                    'backgroundColor': self._get_chart_colors(1)[0],
                    'borderColor': self._get_chart_colors(1)[0],
                }]
            }
    
    def _get_chart_colors(self, count):
        """Get chart colors based on theme"""
        # Burgundy, gold, light gold color scheme
        base_colors = [
            '#8B0000',  # Burgundy
            '#FFD700',  # Gold
            '#F5DEB3',  # Light gold
            '#B8860B',  # Dark goldenrod
            '#CD853F',  # Peru
            '#D2691E',  # Chocolate
            '#A0522D',  # Sienna
            '#8B4513',  # Saddle brown
        ]
        
        colors = []
        for i in range(count):
            colors.append(base_colors[i % len(base_colors)])
        
        return colors
