# -*- coding: utf-8 -*-
{
    'name': 'Sales Dashboard 17',
    'version': '17.0.1.0.0',
    'category': 'Sales',
    'summary': 'Comprehensive sales, invoice, payment & balance analytics dashboard',
    'description': """
Comprehensive Sales Analytics Dashboard for Odoo 17
==================================================

Complete business intelligence solution featuring:

🏢 **Sales Analytics**
- Real-time KPI tracking and growth metrics
- Sales trend analysis with interactive charts  
- Agent commission tracking and analytics
- Conversion rate monitoring

💰 **Financial Analytics**
- Invoice vs payment tracking
- Outstanding receivables monitoring
- Balance and cash flow analysis
- Overdue payment alerts

🏆 **Performance Rankings**
- Top sales performers by revenue
- Best agents by order volume
- Commission leaderboards
- Customer ranking analytics

📊 **Visual Dashboard Features**
- Beautiful responsive design
- Interactive charts and visualizations
- Mobile-friendly interface
- Real-time data updates
- Export functionality

🔧 **Integration Features**
- Works with payment_account_enhanced
- Integrates with accounting modules
- Dynamic reporting capabilities
- Customizable date ranges and filters

Installation:
1. Install from Apps menu
2. Go to Sales > 📊 Sales Analytics Hub
3. Explore different dashboard sections
4. Configure date ranges and filters as needed

Perfect for sales managers, finance teams, and executives who need 
comprehensive visibility into business performance.
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'sale',
        'sales_team',
        'web',
        'account'
    ],
    'external_dependencies': {
        'python': []
    },
    'optional_depends': [
        'payment_account_enhanced',
        'base_accounting_kit',
        'dynamic_accounts_report',
        'om_account_followup'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/dashboard_views.xml',
        'views/comprehensive_dashboard_views.xml',
        'views/dashboard_menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            ('include', 'web._assets_helpers'),
            'oe_sale_dashboard_17/static/src/css/dashboard_merged.css',
            'oe_sale_dashboard_17/static/src/js/chart.min.js',
            'oe_sale_dashboard_17/static/src/js/compatibility.js',
            'oe_sale_dashboard_17/static/src/js/field_mapping.js',
            'oe_sale_dashboard_17/static/src/js/dashboard_fixed.js',
            'oe_sale_dashboard_17/static/src/xml/dashboard_fixed_template.xml',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
}