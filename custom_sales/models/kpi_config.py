# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class SalesKPIConfig(models.Model):
    _name = 'custom.sales.kpi.config'
    _description = 'Sales KPI Configuration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, name'
    
    name = fields.Char(
        string='KPI Name',
        required=True,
        tracking=True,
        help="Display name of the KPI"
    )
    
    code = fields.Char(
        string='KPI Code',
        required=True,
        tracking=True,
        help="Unique code for the KPI"
    )
    
    description = fields.Text(
        string='Description',
        help="Detailed description of what this KPI measures"
    )
    
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help="Order of KPI display on dashboard"
    )
    
    is_active = fields.Boolean(
        string='Active',
        default=True,
        tracking=True,
        help="Whether this KPI is active and displayed"
    )
    
    # Configuration
    dashboard_config_id = fields.Many2one(
        'custom.sales.dashboard.config',
        string='Dashboard Configuration',
        ondelete='cascade'
    )
    
    # Data source configuration
    model_name = fields.Selection([
        ('custom.sales.order', 'Custom Sales Orders'),
        ('sale.order', 'Sale Orders'),
        ('account.move', 'Invoices'),
        ('crm.lead', 'CRM Leads'),
        ('res.partner', 'Customers'),
        ('product.product', 'Products'),
    ], string='Data Source Model', required=True, tracking=True)
    
    field_name = fields.Char(
        string='Field Name',
        required=True,
        help="Field to calculate KPI from (e.g., amount_total, id)"
    )
    
    calculation_type = fields.Selection([
        ('sum', 'Sum'),
        ('avg', 'Average'),
        ('count', 'Count'),
        ('max', 'Maximum'),
        ('min', 'Minimum'),
        ('distinct_count', 'Distinct Count'),
    ], string='Calculation Type', default='sum', required=True, tracking=True)
    
    # Filtering
    domain_filter = fields.Text(
        string='Domain Filter',
        help="Python domain filter for KPI calculation (e.g., [('state', '=', 'sale')])"
    )
    
    date_field = fields.Char(
        string='Date Field',
        default='create_date',
        help="Field to use for date filtering (e.g., create_date, date_order)"
    )
    
    # Display configuration
    icon = fields.Char(
        string='Icon Class',
        help="Font Awesome icon class (e.g., fa-chart-line, fa-dollar-sign)"
    )
    
    color = fields.Char(
        string='Color',
        default='#8B0000',
        help="Color for KPI display (hex color code)"
    )
    
    format_type = fields.Selection([
        ('number', 'Number'),
        ('currency', 'Currency'),
        ('percentage', 'Percentage'),
        ('duration', 'Duration'),
    ], string='Format Type', default='number', tracking=True)
    
    decimal_places = fields.Integer(
        string='Decimal Places',
        default=0,
        help="Number of decimal places to display"
    )
    
    # Size and positioning
    widget_size = fields.Selection([
        ('small', 'Small (3 columns)'),
        ('medium', 'Medium (4 columns)'),
        ('large', 'Large (6 columns)'),
        ('extra_large', 'Extra Large (12 columns)'),
    ], string='Widget Size', default='medium')
    
    # Target and goal settings
    target_value = fields.Float(
        string='Target Value',
        help="Target value for this KPI"
    )
    
    warning_threshold = fields.Float(
        string='Warning Threshold (%)',
        default=80.0,
        help="Percentage of target that triggers warning display"
    )
    
    critical_threshold = fields.Float(
        string='Critical Threshold (%)',
        default=60.0,
        help="Percentage of target that triggers critical display"
    )
    
    # Comparison settings
    enable_comparison = fields.Boolean(
        string='Enable Period Comparison',
        help="Show comparison with previous period"
    )
    
    comparison_period = fields.Selection([
        ('previous_period', 'Previous Period'),
        ('same_period_last_year', 'Same Period Last Year'),
        ('same_period_last_month', 'Same Period Last Month'),
        ('custom', 'Custom Period'),
    ], string='Comparison Period', default='previous_period')
    
    # Advanced settings
    group_by_field = fields.Char(
        string='Group By Field',
        help="Field to group results by (optional)"
    )
    
    having_filter = fields.Text(
        string='Having Filter',
        help="SQL HAVING clause for grouped results"
    )
    
    custom_calculation = fields.Text(
        string='Custom Calculation',
        help="Custom Python code for complex calculations"
    )
    
    # Access control
    user_ids = fields.Many2many(
        'res.users',
        string='Visible to Users',
        help="Users who can see this KPI (empty = all users)"
    )
    
    group_ids = fields.Many2many(
        'res.groups',
        string='Visible to Groups',
        help="Groups who can see this KPI (empty = all groups)"
    )
    
    # Computed fields
    current_value = fields.Float(
        string='Current Value',
        compute='_compute_current_value',
        help="Current KPI value"
    )
    
    achievement_percentage = fields.Float(
        string='Achievement %',
        compute='_compute_achievement_percentage',
        help="Percentage of target achieved"
    )
    
    status = fields.Selection([
        ('good', 'Good'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
    ], string='Status', compute='_compute_status')
    
    @api.depends('target_value', 'current_value')
    def _compute_achievement_percentage(self):
        for record in self:
            if record.target_value and record.target_value != 0:
                record.achievement_percentage = (record.current_value / record.target_value) * 100
            else:
                record.achievement_percentage = 0
    
    @api.depends('achievement_percentage', 'warning_threshold', 'critical_threshold')
    def _compute_status(self):
        for record in self:
            if record.achievement_percentage >= record.warning_threshold:
                record.status = 'good'
            elif record.achievement_percentage >= record.critical_threshold:
                record.status = 'warning'
            else:
                record.status = 'critical'
    
    def _compute_current_value(self):
        """Compute current KPI value"""
        kpi_calculator = self.env['sales.kpi.calculator']
        
        for record in self:
            try:
                value = kpi_calculator.calculate_kpi(record)
                record.current_value = value
            except Exception as e:
                _logger.error(f"Error computing KPI value for {record.code}: {e}")
                record.current_value = 0
    
    @api.model
    def get_user_kpis(self, user_id=None):
        """Get KPIs visible to a specific user"""
        if not user_id:
            user_id = self.env.user.id
        
        user = self.env['res.users'].browse(user_id)
        user_groups = user.groups_id.ids
        
        # Get KPIs visible to user or their groups
        kpis = self.search([
            ('is_active', '=', True),
            '|', '|',
            ('user_ids', '=', False),  # No specific users = visible to all
            ('user_ids', 'in', [user_id]),  # Specific to user
            ('group_ids', 'in', user_groups),  # Visible to user's groups
        ])
        
        return kpis
    
    def calculate_value(self, date_from=None, date_to=None, domain=None):
        """Calculate KPI value for given parameters"""
        self.ensure_one()
        calculator = self.env['sales.kpi.calculator']
        return calculator.calculate_kpi(self, date_from, date_to, domain)
    
    def get_chart_data(self, date_from=None, date_to=None):
        """Get historical chart data for this KPI"""
        self.ensure_one()
        
        # Generate data for the last 12 months
        from datetime import datetime, timedelta
        from dateutil.relativedelta import relativedelta
        
        end_date = date_to or fields.Date.today()
        start_date = date_from or (end_date - relativedelta(months=11))
        
        data = []
        current_date = start_date
        
        while current_date <= end_date:
            month_start = current_date.replace(day=1)
            month_end = (month_start + relativedelta(months=1)) - timedelta(days=1)
            
            value = self.calculate_value(
                date_from=month_start.strftime('%Y-%m-%d'),
                date_to=month_end.strftime('%Y-%m-%d')
            )
            
            data.append({
                'date': month_start.strftime('%Y-%m'),
                'value': value,
            })
            
            current_date = month_start + relativedelta(months=1)
        
        return {
            'labels': [item['date'] for item in data],
            'data': [item['value'] for item in data],
        }
    
    def action_preview_kpi(self):
        """Preview KPI calculation"""
        self.ensure_one()
        
        # Calculate current value
        current_value = self.calculate_value()
        
        # Calculate comparison value if enabled
        comparison_value = None
        if self.enable_comparison:
            from datetime import timedelta
            end_date = fields.Date.today()
            start_date = end_date - timedelta(days=30)  # Last 30 days
            
            comparison_value = self.calculate_value(
                date_from=start_date.strftime('%Y-%m-%d'),
                date_to=end_date.strftime('%Y-%m-%d')
            )
        
        return {
            'type': 'ir.actions.act_window',
            'name': f'KPI Preview: {self.name}',
            'res_model': 'custom.sales.kpi.preview',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_kpi_id': self.id,
                'default_current_value': current_value,
                'default_comparison_value': comparison_value,
            }
        }


class SalesKPIPreview(models.TransientModel):
    _name = 'custom.sales.kpi.preview'
    _description = 'KPI Preview'
    
    kpi_id = fields.Many2one(
        'custom.sales.kpi.config',
        string='KPI',
        required=True
    )
    
    current_value = fields.Float(string='Current Value')
    comparison_value = fields.Float(string='Comparison Value')
    
    formatted_current_value = fields.Char(
        string='Formatted Current Value',
        compute='_compute_formatted_values'
    )
    
    formatted_comparison_value = fields.Char(
        string='Formatted Comparison Value',
        compute='_compute_formatted_values'
    )
    
    @api.depends('current_value', 'comparison_value', 'kpi_id.format_type')
    def _compute_formatted_values(self):
        for record in self:
            if record.kpi_id.format_type == 'currency':
                record.formatted_current_value = f"${record.current_value:,.2f}"
                record.formatted_comparison_value = f"${record.comparison_value:,.2f}" if record.comparison_value else ""
            elif record.kpi_id.format_type == 'percentage':
                record.formatted_current_value = f"{record.current_value:.1f}%"
                record.formatted_comparison_value = f"{record.comparison_value:.1f}%" if record.comparison_value else ""
            else:
                record.formatted_current_value = f"{record.current_value:,.0f}"
                record.formatted_comparison_value = f"{record.comparison_value:,.0f}" if record.comparison_value else ""
