# -*- coding: utf-8 -*-
{
    'name': "renbran - Remove Odoo promotion message",
    'summary': """Remove Odoo promotion message from website footer""",
    'description': """This module removes the Odoo promotion message from the website footer without modifying the core code.""",
    'sequence': 150,
    'author': "renbran",
    'company': 'renbran',
    'website': 'https://renbran.com/',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Website',
    'version': '17.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['website'],
    'license': 'AGPL-3',
    # always loaded
    'data': [
        'views/website_templates.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
}