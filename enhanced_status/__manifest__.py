{
    'name': 'Sale Order Enhanced Status',
    'version': '17.0.1.0.0',
    'summary': 'Enhanced sale order status workflow with comprehensive financial tracking',
    'description': '''
        This module extends the sale order workflow with:
        - Custom status: Draft, Documentation, Calculation, Approved, Completed
        - Responsible person/group for each stage
        - Billing status tracking (Fully Invoiced, Unraised, Partially Invoiced)
        - Payment status tracking (Fully Paid, Partially Paid, Unpaid)
        - Invoiced, Paid amounts and Balance tracking
        - Stage-responsive button visibility
        - Field locking in completed state (admin override)
    ''',
    'category': 'Sales',
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['sale', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/sale_order_stage_views.xml',
        'views/sale_order_views.xml',
        'data/ir_cron_data.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
