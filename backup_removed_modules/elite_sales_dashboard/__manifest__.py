{
    'name': 'Elite Sales Dashboard',
    'version': '17.0',
    'category': 'Sales',
    'summary': 'Advanced dashboard for sales agents performance',
    'description': """
Elite Sales Dashboard
====================
Advanced dashboard for tracking sales agent performance.
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['base', 'web', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/dashboard_views.xml',
        'views/dashboard_templates.xml',
        'views/menu_items.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'elite_sales_dashboard/static/src/js/elite_dashboard.js',
            'elite_sales_dashboard/static/src/scss/dashboard.scss',
            'elite_sales_dashboard/static/src/xml/dashboard.xml',
        ],
    },
    'application': True,
    'installable': True,
    'license': 'LGPL-3',
}