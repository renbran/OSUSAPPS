# -*- coding: utf-8 -*-

from . import models
from . import controllers
from . import wizard
from . import reports

def post_init_hook(cr, registry):
    """Post installation hook to setup initial data"""
    from odoo import api, SUPERUSER_ID
    
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Create default dashboard configuration
    dashboard_config = env['custom.sales.dashboard.config'].search([])
    if not dashboard_config:
        env['custom.sales.dashboard.config'].create({
            'name': 'Default Sales Dashboard',
            'is_default': True,
            'show_kpis': True,
            'show_charts': True,
            'show_tables': True,
            'refresh_interval': 300,  # 5 minutes
        })
    
    # Setup default KPI configurations
    kpi_configs = [
        {
            'name': 'Total Sales',
            'code': 'total_sales',
            'model_name': 'sale.order',
            'field_name': 'amount_total',
            'calculation_type': 'sum',
            'is_active': True,
            'sequence': 1,
        },
        {
            'name': 'Sales Count',
            'code': 'sales_count',
            'model_name': 'sale.order',
            'field_name': 'id',
            'calculation_type': 'count',
            'is_active': True,
            'sequence': 2,
        },
        {
            'name': 'Average Sale Value',
            'code': 'avg_sale_value',
            'model_name': 'sale.order',
            'field_name': 'amount_total',
            'calculation_type': 'avg',
            'is_active': True,
            'sequence': 3,
        },
        {
            'name': 'Sales Pipeline',
            'code': 'sales_pipeline',
            'model_name': 'crm.lead',
            'field_name': 'expected_revenue',
            'calculation_type': 'sum',
            'is_active': True,
            'sequence': 4,
        },
    ]
    
    for kpi_data in kpi_configs:
        existing_kpi = env['custom.sales.kpi.config'].search([('code', '=', kpi_data['code'])])
        if not existing_kpi:
            env['custom.sales.kpi.config'].create(kpi_data)

def uninstall_hook(cr, registry):
    """Cleanup hook when uninstalling the module"""
    pass
