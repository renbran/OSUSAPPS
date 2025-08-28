{
    'name': 'Enhanced Commission Management System',
    'version': '17.0.3.0.0',
    'summary': 'Advanced commission calculation with dual-group structure',
    'description': '''
        Comprehensive commission management with external/internal stakeholders.
        Features: Multiple calculation methods, PO generation, reporting, and reconciliation.
    ''',
    'category': 'Sales/Commission',
    'author': 'OSUS Properties',
    'website': 'https://www.osusproperties.com',
    'depends': ['sale', 'purchase', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'data/commission_demo_data.xml',
        'data/commission_email_templates.xml',
        'data/commission_cron.xml',
        'views/purchase_order_views.xml',
        'views/sale_order_views.xml',
        'views/commission_dashboard.xml',
        'views/commission_report.xml'
    ],
    'demo': ['data/commission_demo_data.xml'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'images': ['static/description/banner.png'],
}