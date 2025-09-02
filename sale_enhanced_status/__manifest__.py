{
    'name': 'Sale Enhanced Status',
    'version': '17.0.1.0.0',
    'category': 'Sales',
    'summary': 'Advanced sales order workflow and status automation',
    'description': """
        Enhanced workflow for sales orders with custom stages, automated status, financial tracking, and reporting.
    """,
    'author': 'Your Company',
    'website': 'https://yourcompany.com',
    'depends': ['sale'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/sale_order_views.xml',
        'views/sale_order_stage_views.xml',
        'data/sale_order_stages.xml',
        'data/ir_cron_data.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}
