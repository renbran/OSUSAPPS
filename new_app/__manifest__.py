# -*- coding: utf-8 -*-
{
    'name': 'New App',
    'version': '17.0.1.0.0',
    'category': 'Customizations',
    'summary': 'Custom Odoo 17 Module',
    'description': """
        Custom Odoo 17 Module
        =====================
        This module provides custom functionality for your Odoo instance.
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
    ],
    'data': [
        # Security
        'security/ir.model.access.csv',

        # Data
        # 'data/data.xml',

        # Views
        'views/new_app_views.xml',
        'views/new_app_menus.xml',

        # Reports
        # 'reports/report_templates.xml',

        # Wizards
        # 'wizards/wizard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # 'new_app/static/src/css/custom.css',
            # 'new_app/static/src/js/custom.js',
        ],
    },
    'demo': [
        # 'demo/demo_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
