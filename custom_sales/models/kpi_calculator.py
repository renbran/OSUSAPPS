# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)

class SalesKpiCalculator(models.TransientModel):
    _name = 'sales.kpi.calculator'
    _description = 'Sales KPI Calculator'
    
    def get_dashboard_kpis(self, dashboard_id=None, date_from=None, date_to=None):
        """Calculate KPIs for dashboard"""
        try:
            domain = []
            if date_from and date_to:
                domain.extend([
                    ('create_date', '>=', date_from),
                    ('create_date', '<=', date_to)
                ])
            
            # Get sales data
            sales_orders = self.env['custom.sales.order'].search(domain)
            
            # Calculate KPIs
            kpis = [
                {
                    'name': 'Total Sales Revenue',
                    'value': sum(sales_orders.mapped('actual_revenue')),
                    'format_type': 'currency',
                    'icon': 'fa-money',
                    'color': '#8B0000'
                },
                {
                    'name': 'Total Orders',
                    'value': len(sales_orders),
                    'format_type': 'integer',
                    'icon': 'fa-shopping-cart',
                    'color': '#FFD700'
                },
                {
                    'name': 'Average Order Value',
                    'value': sum(sales_orders.mapped('actual_revenue')) / len(sales_orders) if sales_orders else 0,
                    'format_type': 'currency',
                    'icon': 'fa-calculator',
                    'color': '#F5DEB3'
                },
                {
                    'name': 'Average Profit Margin',
                    'value': sum(sales_orders.mapped('profit_margin')) / len(sales_orders) if sales_orders else 0,
                    'format_type': 'percentage',
                    'icon': 'fa-percent',
                    'color': '#8B0000'
                }
            ]
            
            return kpis
            
        except Exception as e:
            _logger.error(f"Error calculating KPIs: {e}")
            return []


class SalesChartGenerator(models.TransientModel):
    _name = 'sales.chart.generator'
    _description = 'Sales Chart Generator'
    
    def generate_chart_data(self, chart_config, date_from=None, date_to=None):
        """Generate chart data based on configuration"""
        try:
            domain = []
            if date_from and date_to:
                domain.extend([
                    ('create_date', '>=', date_from),
                    ('create_date', '<=', date_to)
                ])
            
            sales_orders = self.env['custom.sales.order'].search(domain)
            
            if chart_config.chart_type == 'bar':
                return self._generate_bar_chart_data(sales_orders, chart_config)
            elif chart_config.chart_type == 'line':
                return self._generate_line_chart_data(sales_orders, chart_config)
            elif chart_config.chart_type == 'pie':
                return self._generate_pie_chart_data(sales_orders, chart_config)
            elif chart_config.chart_type == 'doughnut':
                return self._generate_doughnut_chart_data(sales_orders, chart_config)
            else:
                return {}
                
        except Exception as e:
            _logger.error(f"Error generating chart data: {e}")
            return {}
    
    def _generate_bar_chart_data(self, sales_orders, chart_config):
        """Generate bar chart data"""
        # Group by month
        monthly_data = {}
        for order in sales_orders:
            month = order.create_date.strftime('%Y-%m') if order.create_date else 'Unknown'
            if month not in monthly_data:
                monthly_data[month] = 0
            monthly_data[month] += order.actual_revenue or 0
        
        return {
            'labels': list(monthly_data.keys()),
            'datasets': [{
                'label': 'Sales Revenue',
                'data': list(monthly_data.values()),
                'backgroundColor': '#8B0000',
                'borderColor': '#FFD700',
                'borderWidth': 1
            }]
        }
    
    def _generate_line_chart_data(self, sales_orders, chart_config):
        """Generate line chart data"""
        return self._generate_bar_chart_data(sales_orders, chart_config)
    
    def _generate_pie_chart_data(self, sales_orders, chart_config):
        """Generate pie chart data"""
        # Group by customer type
        type_data = {}
        for order in sales_orders:
            customer_type = order.customer_type or 'Unknown'
            if customer_type not in type_data:
                type_data[customer_type] = 0
            type_data[customer_type] += order.actual_revenue or 0
        
        return {
            'labels': list(type_data.keys()),
            'datasets': [{
                'data': list(type_data.values()),
                'backgroundColor': ['#8B0000', '#FFD700', '#F5DEB3', '#A0522D'],
                'borderWidth': 1
            }]
        }
    
    def _generate_doughnut_chart_data(self, sales_orders, chart_config):
        """Generate doughnut chart data"""
        return self._generate_pie_chart_data(sales_orders, chart_config)
