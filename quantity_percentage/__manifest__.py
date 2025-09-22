# -*- coding: utf-8 -*-
{
    'name': 'Quantity Percentage Display',
    'version': '17.0.1.0.0',
    'category': 'Sales/Accounting',
    'summary': 'Display quantities as percentages with precise decimal handling across sales and accounting',
    'description': """
        This module modifies quantity fields across sales orders and invoices to display as percentages
        without rounding, providing exact percentage representation with uniform interface.
        
        Features:
        - Displays quantities as percentages (e.g., 0.036 becomes 3.6%)
        - Preserves exact decimal precision without rounding
        - Clean user interface with percentage widget
        - Uniform interface across Sales Orders, Quotations, Invoices, and Bills
        - Compatible with Odoo 17 sales and accounting workflows
    """,
    'author': 'OSUSAPPS',
    'website': 'https://www.osusapps.com',
    'depends': ['account', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_move_views.xml',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}