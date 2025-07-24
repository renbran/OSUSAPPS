# -*- coding: utf-8 -*-
# Copyright 2024 RL Software Development ApS. See LICENSE file for full copyright and licensing details.
{
    'name': "Dashboard Custom",

    'summary': """

        This is a base module for other modules, that are dependent on the components in this module. It is not meant to be installed on its own.
    
    """,

    'description': """
        Contact Mads Christensen for more information
    """,

    'author': "RL Software Development ApS",
    'website': "https://www.rlsd.dk/model/apps/dashboard-custom-1",

    'category': 'Sales/Sales',
    'version': '17.0.1.0.4',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'web',
        'sale',
        'spreadsheet_dashboard', #Odoo 16 - to get menu
        'board',        
    ],

    # always loaded
    'data': [        
        'views/menu.xml',        
    ],

    'assets': {
        'web.assets_backend': [
            'dashboard_custom/static/src/components/**/*.xml',
            'dashboard_custom/static/src/components/**/*.js',
            'dashboard_custom/static/src/components/**/*.scss',            
        ],        
    },
    'demo': [
    
    ],
    # 'sequence': 90,
    'price': 0,
    'currency': 'EUR',
    'support': 'support@rlsd.dk',
    # 'live_test_url': '',
    "images":[
        'static/description/icon.png',
        # 'static/description/banner.png',
        'static/description/logo.png',
        # 'static/description/settings.png',        
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'OPL-1',
}
