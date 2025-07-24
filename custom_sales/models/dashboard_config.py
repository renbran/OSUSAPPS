# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class CustomSalesDashboardConfig(models.Model):
    _name = 'custom.sales.dashboard.config'
    _description = 'Sales Dashboard Configuration'
    _order = 'sequence, name'
    
    name = fields.Char(
        string='Dashboard Name',
        required=True,
        help="Name of the dashboard configuration"
    )
    
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help="Sequence for ordering dashboard configurations"
    )
    
    is_default = fields.Boolean(
        string='Is Default',
        help="Mark this as the default dashboard configuration"
    )
    
    is_active = fields.Boolean(
        string='Active',
        default=True,
        help="Whether this dashboard configuration is active"
    )
    
    # Display settings
    show_kpis = fields.Boolean(
        string='Show KPIs',
        default=True,
        help="Display KPI widgets on the dashboard"
    )
    
    show_charts = fields.Boolean(
        string='Show Charts',
        default=True,
        help="Display charts on the dashboard"
    )
    
    show_tables = fields.Boolean(
        string='Show Tables',
        default=True,
        help="Display data tables on the dashboard"
    )
    
    show_filters = fields.Boolean(
        string='Show Filters',
        default=True,
        help="Display filter options on the dashboard"
    )
    
    # Refresh settings
    refresh_interval = fields.Integer(
        string='Refresh Interval (seconds)',
        default=300,
        help="Auto-refresh interval in seconds (0 to disable)"
    )
    
    auto_refresh = fields.Boolean(
        string='Auto Refresh',
        default=True,
        help="Enable automatic dashboard refresh"
    )
    
    # Color scheme
    primary_color = fields.Char(
        string='Primary Color',
        default='#8B0000',  # Burgundy
        help="Primary color for the dashboard theme"
    )
    
    secondary_color = fields.Char(
        string='Secondary Color',
        default='#FFD700',  # Gold
        help="Secondary color for the dashboard theme"
    )
    
    accent_color = fields.Char(
        string='Accent Color',
        default='#F5DEB3',  # Light gold
        help="Accent color for the dashboard theme"
    )
    
    # Layout settings
    layout_type = fields.Selection([
        ('grid', 'Grid Layout'),
        ('masonry', 'Masonry Layout'),
        ('fluid', 'Fluid Layout'),
    ], string='Layout Type', default='grid')
    
    columns_count = fields.Integer(
        string='Columns Count',
        default=4,
        help="Number of columns in grid layout"
    )
    
    # User access
    user_ids = fields.Many2many(
        'res.users',
        string='Allowed Users',
        help="Users who can access this dashboard configuration"
    )
    
    group_ids = fields.Many2many(
        'res.groups',
        string='Allowed Groups',
        help="Groups who can access this dashboard configuration"
    )
    
    # KPI configurations
    kpi_config_ids = fields.One2many(
        'custom.sales.kpi.config',
        'dashboard_config_id',
        string='KPI Configurations'
    )
    
    # Chart configurations
    chart_config_ids = fields.One2many(
        'custom.sales.chart.config',
        'dashboard_config_id',
        string='Chart Configurations'
    )
    
    @api.constrains('is_default')
    def _check_default_dashboard(self):
        """Ensure only one default dashboard exists"""
        if self.is_default:
            other_defaults = self.search([
                ('is_default', '=', True),
                ('id', '!=', self.id)
            ])
            if other_defaults:
                raise ValidationError("Only one default dashboard configuration is allowed.")
    
    @api.constrains('refresh_interval')
    def _check_refresh_interval(self):
        """Validate refresh interval"""
        for record in self:
            if record.refresh_interval < 0:
                raise ValidationError("Refresh interval must be positive.")
            if record.refresh_interval > 0 and record.refresh_interval < 30:
                raise ValidationError("Refresh interval must be at least 30 seconds.")
    
    @api.model
    def get_default_dashboard(self):
        """Get the default dashboard configuration"""
        default_dashboard = self.search([('is_default', '=', True)], limit=1)
        if not default_dashboard:
            default_dashboard = self.search([('is_active', '=', True)], limit=1)
        return default_dashboard
    
    def get_user_dashboard(self, user_id=None):
        """Get dashboard configuration for a specific user"""
        if not user_id:
            user_id = self.env.user.id
        
        # Check for user-specific dashboard
        user_dashboard = self.search([
            ('user_ids', 'in', [user_id]),
            ('is_active', '=', True)
        ], limit=1)
        
        if user_dashboard:
            return user_dashboard
        
        # Check for group-based dashboard
        user_groups = self.env.user.groups_id.ids
        group_dashboard = self.search([
            ('group_ids', 'in', user_groups),
            ('is_active', '=', True)
        ], limit=1)
        
        if group_dashboard:
            return group_dashboard
        
        # Return default dashboard
        return self.get_default_dashboard()


class CustomSalesKPIConfig(models.Model):
    _name = 'custom.sales.kpi.config'
    _description = 'Sales KPI Configuration'
    _order = 'sequence, name'
    
    name = fields.Char(
        string='KPI Name',
        required=True,
        help="Display name of the KPI"
    )
    
    code = fields.Char(
        string='KPI Code',
        required=True,
        help="Unique code for the KPI"
    )
    
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help="Order of KPI display"
    )
    
    is_active = fields.Boolean(
        string='Active',
        default=True,
        help="Whether this KPI is active"
    )
    
    dashboard_config_id = fields.Many2one(
        'custom.sales.dashboard.config',
        string='Dashboard Configuration',
        ondelete='cascade'
    )
    
    # Data source
    model_name = fields.Char(
        string='Model Name',
        required=True,
        help="Model to calculate KPI from"
    )
    
    field_name = fields.Char(
        string='Field Name',
        required=True,
        help="Field to calculate KPI from"
    )
    
    calculation_type = fields.Selection([
        ('sum', 'Sum'),
        ('avg', 'Average'),
        ('count', 'Count'),
        ('max', 'Maximum'),
        ('min', 'Minimum'),
    ], string='Calculation Type', default='sum', required=True)
    
    # Filters
    domain = fields.Text(
        string='Domain Filter',
        help="Domain filter for KPI calculation (Python expression)"
    )
    
    date_field = fields.Char(
        string='Date Field',
        help="Field to use for date filtering"
    )
    
    # Display settings
    icon = fields.Char(
        string='Icon',
        help="Font Awesome icon class"
    )
    
    color = fields.Char(
        string='Color',
        help="Color for KPI display"
    )
    
    format_type = fields.Selection([
        ('number', 'Number'),
        ('currency', 'Currency'),
        ('percentage', 'Percentage'),
    ], string='Format Type', default='number')
    
    # Comparison settings
    enable_comparison = fields.Boolean(
        string='Enable Comparison',
        help="Enable period comparison for this KPI"
    )
    
    comparison_period = fields.Selection([
        ('previous_period', 'Previous Period'),
        ('same_period_last_year', 'Same Period Last Year'),
        ('custom', 'Custom Period'),
    ], string='Comparison Period')
    
    @api.constrains('code')
    def _check_unique_code(self):
        """Ensure KPI code is unique"""
        for record in self:
            duplicate = self.search([
                ('code', '=', record.code),
                ('id', '!=', record.id)
            ])
            if duplicate:
                raise ValidationError(f"KPI code '{record.code}' already exists.")


class CustomSalesChartConfig(models.Model):
    _name = 'custom.sales.chart.config'
    _description = 'Sales Chart Configuration'
    _order = 'sequence, name'
    
    name = fields.Char(
        string='Chart Name',
        required=True,
        help="Display name of the chart"
    )
    
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help="Order of chart display"
    )
    
    is_active = fields.Boolean(
        string='Active',
        default=True,
        help="Whether this chart is active"
    )
    
    dashboard_config_id = fields.Many2one(
        'custom.sales.dashboard.config',
        string='Dashboard Configuration',
        ondelete='cascade'
    )
    
    # Chart type
    chart_type = fields.Selection([
        ('bar', 'Bar Chart'),
        ('line', 'Line Chart'),
        ('pie', 'Pie Chart'),
        ('doughnut', 'Doughnut Chart'),
        ('area', 'Area Chart'),
        ('scatter', 'Scatter Plot'),
        ('radar', 'Radar Chart'),
    ], string='Chart Type', default='bar', required=True)
    
    # Data source
    model_name = fields.Char(
        string='Model Name',
        required=True,
        help="Model to get chart data from"
    )
    
    x_field = fields.Char(
        string='X-Axis Field',
        required=True,
        help="Field for X-axis data"
    )
    
    y_field = fields.Char(
        string='Y-Axis Field',
        required=True,
        help="Field for Y-axis data"
    )
    
    group_by_field = fields.Char(
        string='Group By Field',
        help="Field to group data by"
    )
    
    # Filters
    domain = fields.Text(
        string='Domain Filter',
        help="Domain filter for chart data (Python expression)"
    )
    
    limit = fields.Integer(
        string='Record Limit',
        default=10,
        help="Maximum number of records to display"
    )
    
    # Display settings
    width = fields.Integer(
        string='Width',
        default=6,
        help="Chart width in grid columns (1-12)"
    )
    
    height = fields.Integer(
        string='Height (px)',
        default=400,
        help="Chart height in pixels"
    )
    
    show_legend = fields.Boolean(
        string='Show Legend',
        default=True,
        help="Display chart legend"
    )
    
    show_labels = fields.Boolean(
        string='Show Labels',
        default=True,
        help="Display data labels"
    )
    
    colors = fields.Text(
        string='Color Palette',
        help="JSON array of colors for the chart"
    )
