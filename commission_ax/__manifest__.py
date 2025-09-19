{
    'name': 'Advanced Commission Management',
    'version': '17.0.3.0.0',
    'category': 'Sales',
    'summary': 'Commission management system - SAFE MODE',
    'description': """
    Commission Management System - Safe Mode
    ======================================
    Basic commission functionality without advanced features.
    This version loads only core components to ensure system stability.
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
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/commission_menu.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}