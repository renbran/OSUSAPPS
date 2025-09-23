# -*- coding: utf-8 -*-
{
    'name': 'Quantity Percentage Display',
    'version': '17.0.1.0.0',
    'category': 'Sales/Accounting',
    'summary': 'Enhanced quantity field with percentage input conversion and default % UoM',
    'description': """
        This module modifies quantity fields across sales orders and invoices to work with percentage logic:
        
        Key Features:
        - Smart percentage input: When user types "5", it's converted to 0.05 (5%)
        - Default percentage UoM: Automatically sets Unit of Measure to % unless specified
        - High precision: Maintains up to 6 decimal places for exact calculations
        - Displays quantities as percentages (e.g., 0.036 becomes 3.6%)
        - Preserves exact decimal precision without rounding
        - Clean user interface with percentage widget
        - Uniform interface across Sales Orders, Quotations, Invoices, and Bills
        - Compatible with Odoo 17 sales and accounting workflows
        
        Usage:
        - User inputs "5" -> System stores 0.05 and displays "5%"
        - User inputs "0.5" -> System stores 0.005 and displays "0.5%"
        - Default UoM is automatically set to percentage (%) for new lines
    """,
    'author': 'OSUSAPPS',
    'website': 'https://www.osusapps.com',
    'depends': ['account', 'sale', 'uom'],
    'data': [
        'data/uom_data.xml',
        'security/ir.model.access.csv',
        'views/account_move_views.xml',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}