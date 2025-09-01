{
    'name': 'OSUS Invoice Report',
    'version': '17.0.1.0.0',
    'summary': 'Professional UAE Tax Invoice Reports for Real Estate Commission',
    'description': '''
        Professional Tax Invoice Reports
        ================================
        - UAE VAT compliant invoice layout
        - Real estate commission specific fields
        - UK date format support
        - Amount in words conversion
        - Professional styling with Bootstrap 5
        - Multi-company support
        - Inheritance-safe implementation
    ''',
    'category': 'Accounting/Accounting',
    'author': 'OSUS Real Estate',
    'website': 'https://www.osus.ae',
    'depends': ['account', 'base', 'sale', 'portal', 'project_unit_management'],
    'external_dependencies': {
        'python': ['qrcode', 'num2words'],
    },
    'data': [
        # Security
        'security/ir.model.access.csv',
        
        # Data
        'data/report_paperformat.xml',
        
        # Views
        'views/account_move_views.xml',
        'views/sale_order_views.xml',
        'views/portal_templates.xml',
        
        # Reports
        'report/report_action.xml',
        'report/bill_report_action.xml',
        'report/payment_report_action.xml',
        'report/invoice_report.xml',
        'report/bill_report.xml',
        'report/payment_report.xml',
    ],
    'assets': {
        'web.report_assets_pdf': [
            'osus_invoice_report/static/src/css/report_style.css',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
    'auto_install': False,
}