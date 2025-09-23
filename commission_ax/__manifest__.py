{
    'name': 'Commission Management',
    'version': '17.0.1.0.0',
    'category': 'Sales',
    'summary': 'Simple and efficient commission management for sales orders',
    'description': """
Commission Management System
============================

Simple commission management with purchase order integration.

Features:
- Commission lines with flexible calculation methods
- Partner assignments for commission tracking
- Purchase order creation for commission payments
- Vendor reference auto-population from sales orders

""",
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'sale',
        'purchase',
        'account',
    ],
    'data': [
        # Security
        'security/security.xml',
        'security/ir.model.access.csv',

        # Core data
        'data/commission_types_data.xml',

        # Views
        'views/commission_type_views.xml',
        'views/commission_line_views.xml',
        'views/commission_assignment_views.xml',
        'views/sale_order.xml',
        'views/purchase_order.xml',
        'views/res_partner_views.xml',
        'views/commission_menu.xml',

        # Wizards
        'views/commission_payment_wizard_views.xml',

        # Reports
        'reports/commission_report.xml',
        'reports/commission_report_template.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}