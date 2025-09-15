# -*- coding: utf-8 -*-
{
    'name': 'Sales Dashboard 17',
    'version': '17.0.1.0.0',
    'category': 'Sales',
    'summary': 'Comprehensive sales dashboard with analytics',
    'description': """
Sales Dashboard for Odoo 17
===========================

Production-ready sales dashboard with:
- Real-time KPI tracking
- Interactive charts and visualizations  
- Field compatibility (booking_date, sale_value)
- Sales type filtering
- Top performers tracking
- Export functionality
- Mobile responsive design

Installation:
1. Install from Apps menu
2. Go to Sales > Sales Dashboard
3. Use Test Data button to verify
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'sale',
        'sales_team',
        'web'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/dashboard_views.xml',
        'views/dashboard_menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'oe_sale_dashboard_17/static/src/js/dashboard.js',
            'oe_sale_dashboard_17/static/src/css/dashboard.css',
            'oe_sale_dashboard_17/static/src/xml/dashboard_template.xml',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
}