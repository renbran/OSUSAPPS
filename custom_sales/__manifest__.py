{
    'name': 'Custom Sales Dashboard Pro',
    'version': '17.0.1.0.0',
    'category': 'Sales',
    'summary': 'Advanced Sales Dashboard with Custom Analytics and Reporting',
    'description': """
Custom Sales Dashboard Pro
==========================

An advanced, branded sales dashboard for Odoo 17 featuring:

* Real-time sales analytics and KPIs
* Interactive charts and graphs with Chart.js
* Custom sales order management with additional fields
* Advanced reporting and data visualization
* Burgundy, gold, and light gold branded theme
* Multi-period comparison and forecasting
* Sales team performance tracking
* Customer analytics and insights
* Mobile-responsive design
* Export capabilities (PDF, Excel, CSV)

Features:
---------
* Custom sales order model with extended fields
* Real-time dashboard with live data updates
* Advanced filtering and date range selection
* Sales funnel visualization
* Revenue forecasting and trend analysis
* Top customers and products analytics
* Sales team leaderboards
* Custom reports and exports
* REST API endpoints for integration
* Comprehensive security and access controls

Business Intelligence:
----------------------
* Sales performance metrics
* Revenue tracking and forecasting
* Customer lifetime value analysis
* Product performance analytics
* Geographic sales distribution
* Sales conversion rates
* Pipeline management
* Goal tracking and achievements
    """,
    'author': 'OSUS Business Solutions',
    'website': 'https://www.osus.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
        'sale',
        'sale_management',
        'account',
        'crm',
        'mail',
        'portal',
        'web_tour',
    ],
    'external_dependencies': {
        'python': ['xlsxwriter', 'pandas', 'numpy'],
        'bin': [],
    },
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/dashboard_data.xml',
        'data/demo_data.xml',
        'data/cron_jobs.xml',
        'views/menu.xml',
        'views/custom_sales_order_views.xml',
        'views/dashboard_views.xml',
        'views/dashboard_config_views.xml',
        'views/sales_analytics_views.xml',
        'views/reports_views.xml',
        'views/dashboard_error_templates.xml',
        'wizard/sales_report_wizard_views.xml',
        'reports/sales_reports.xml',
    ],
    'demo': [
        'demo/demo_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'custom_sales/static/src/css/dashboard.css',
            'custom_sales/static/src/css/branded_theme.css',
            'custom_sales/static/src/js/dashboard.js',
            'custom_sales/static/src/js/chart_renderer.js',
            'custom_sales/static/src/js/kpi_widgets.js',
            'custom_sales/static/src/js/dashboard_utils.js',
            'custom_sales/static/src/xml/dashboard_templates.xml',
            'custom_sales/static/src/xml/kpi_templates.xml',
            'custom_sales/static/lib/chart.js/chart.min.js',
        ],
        'web.assets_frontend': [
            'custom_sales/static/src/css/portal.css',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 10,
    'images': ['static/description/banner.png'],
    'live_test_url': 'https://demo.osus.com/custom_sales',
    'support': 'support@osus.com',
    'maintainers': ['osus_team'],
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
}
