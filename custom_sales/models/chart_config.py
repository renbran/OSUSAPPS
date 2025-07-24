# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class CustomSalesChartConfig(models.Model):
    _name = 'custom.sales.chart.config'
    _description = 'Sales Chart Configuration'
    _order = 'sequence, name'
    
    name = fields.Char(
        string='Chart Name',
        required=True,
        help="Name of the chart configuration"
    )
    
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help="Sequence for ordering chart configurations"
    )
    
    dashboard_config_id = fields.Many2one(
        'custom.sales.dashboard.config',
        string='Dashboard Configuration',
        required=True,
        ondelete='cascade'
    )
    
    chart_type = fields.Selection([
        ('bar', 'Bar Chart'),
        ('line', 'Line Chart'),
        ('pie', 'Pie Chart'),
        ('doughnut', 'Doughnut Chart'),
        ('area', 'Area Chart'),
        ('scatter', 'Scatter Plot'),
    ], string='Chart Type', default='bar', required=True)
    
    data_source = fields.Selection([
        ('sales_orders', 'Sales Orders'),
        ('customers', 'Customers'),
        ('products', 'Products'),
        ('teams', 'Sales Teams'),
        ('custom', 'Custom Query'),
    ], string='Data Source', default='sales_orders', required=True)
    
    is_active = fields.Boolean(
        string='Active',
        default=True,
        help="Whether this chart is active and should be displayed"
    )
    
    show_legend = fields.Boolean(
        string='Show Legend',
        default=True,
        help="Whether to show the chart legend"
    )
    
    width = fields.Integer(
        string='Width',
        default=400,
        help="Chart width in pixels"
    )
    
    height = fields.Integer(
        string='Height',
        default=300,
        help="Chart height in pixels"
    )
    
    group_by_field = fields.Selection([
        ('month', 'Month'),
        ('quarter', 'Quarter'),
        ('year', 'Year'),
        ('customer_type', 'Customer Type'),
        ('sales_team_id', 'Sales Team'),
        ('state', 'Status'),
        ('priority', 'Priority'),
    ], string='Group By', default='month')
    
    value_field = fields.Selection([
        ('total_revenue', 'Total Revenue'),
        ('order_count', 'Order Count'),
        ('average_order_value', 'Average Order Value'),
        ('profit_margin', 'Profit Margin'),
    ], string='Value Field', default='total_revenue')
    
    color_scheme = fields.Selection([
        ('brand', 'Brand Colors'),
        ('blue', 'Blue Tones'),
        ('green', 'Green Tones'),
        ('red', 'Red Tones'),
        ('rainbow', 'Rainbow'),
    ], string='Color Scheme', default='brand')
    
    @api.constrains('width', 'height')
    def _check_dimensions(self):
        for record in self:
            if record.width < 100 or record.width > 1200:
                raise ValidationError("Chart width must be between 100 and 1200 pixels")
            if record.height < 100 or record.height > 800:
                raise ValidationError("Chart height must be between 100 and 800 pixels")
    
    def get_chart_data(self, date_from=None, date_to=None):
        """Get chart data based on configuration"""
        self.ensure_one()
        
        domain = []
        if date_from and date_to:
            domain.extend([
                ('create_date', '>=', date_from),
                ('create_date', '<=', date_to)
            ])
        
        if self.data_source == 'sales_orders':
            return self._get_sales_orders_data(domain)
        elif self.data_source == 'customers':
            return self._get_customers_data(domain)
        elif self.data_source == 'products':
            return self._get_products_data(domain)
        elif self.data_source == 'teams':
            return self._get_teams_data(domain)
        else:
            return {}
    
    def _get_sales_orders_data(self, domain):
        """Get sales orders data for chart"""
        orders = self.env['custom.sales.order'].search(domain)
        
        # Group data based on group_by_field
        grouped_data = {}
        
        for order in orders:
            if self.group_by_field == 'month':
                key = order.create_date.strftime('%Y-%m') if order.create_date else 'Unknown'
            elif self.group_by_field == 'quarter':
                key = order.create_date.strftime('%Y-Q%q') if order.create_date else 'Unknown'
            elif self.group_by_field == 'year':
                key = order.create_date.strftime('%Y') if order.create_date else 'Unknown'
            elif self.group_by_field == 'customer_type':
                key = order.customer_type or 'Unknown'
            elif self.group_by_field == 'state':
                key = dict(order._fields['state'].selection).get(order.state, order.state)
            else:
                key = 'All'
            
            if key not in grouped_data:
                grouped_data[key] = {'count': 0, 'revenue': 0, 'orders': []}
            
            grouped_data[key]['count'] += 1
            grouped_data[key]['revenue'] += order.actual_revenue or 0
            grouped_data[key]['orders'].append(order)
        
        # Extract values based on value_field
        labels = list(grouped_data.keys())
        values = []
        
        for key in labels:
            if self.value_field == 'order_count':
                values.append(grouped_data[key]['count'])
            elif self.value_field == 'total_revenue':
                values.append(grouped_data[key]['revenue'])
            elif self.value_field == 'average_order_value':
                count = grouped_data[key]['count']
                values.append(grouped_data[key]['revenue'] / count if count > 0 else 0)
            else:
                values.append(grouped_data[key]['revenue'])
        
        return {
            'labels': labels,
            'values': values,
            'datasets': [{
                'label': self.name,
                'data': values,
                'backgroundColor': self._get_colors(len(labels)),
                'borderColor': '#8B0000',
                'borderWidth': 1
            }]
        }
    
    def _get_customers_data(self, domain):
        """Get customer data for chart"""
        # Implementation for customer-based charts
        return {'labels': [], 'values': [], 'datasets': []}
    
    def _get_products_data(self, domain):
        """Get product data for chart"""
        # Implementation for product-based charts
        return {'labels': [], 'values': [], 'datasets': []}
    
    def _get_teams_data(self, domain):
        """Get sales team data for chart"""
        # Implementation for team-based charts
        return {'labels': [], 'values': [], 'datasets': []}
    
    def _get_colors(self, count):
        """Get colors based on color scheme"""
        if self.color_scheme == 'brand':
            base_colors = ['#8B0000', '#FFD700', '#F5DEB3', '#A0522D', '#CD853F', '#DEB887']
        elif self.color_scheme == 'blue':
            base_colors = ['#1f77b4', '#aec7e8', '#ffbb78', '#2ca02c', '#98df8a', '#d62728']
        elif self.color_scheme == 'green':
            base_colors = ['#2ca02c', '#98df8a', '#bcbd22', '#dbdb8d', '#17becf', '#9edae5']
        elif self.color_scheme == 'red':
            base_colors = ['#d62728', '#ff9896', '#e377c2', '#f7b6d3', '#7f7f7f', '#c7c7c7']
        else:  # rainbow
            base_colors = ['#ff0000', '#ff7f00', '#ffff00', '#00ff00', '#0000ff', '#4b0082', '#9400d3']
        
        colors = []
        for i in range(count):
            colors.append(base_colors[i % len(base_colors)])
        
        return colors
