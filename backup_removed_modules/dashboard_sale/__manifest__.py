# -*- coding: utf-8 -*-
# Copyright 2024 RL Software Development ApS. See LICENSE file for full copyright and licensing details.
{
    'name': "Dashboard for Sale",

    'summary': """
    
    """,

    'description': """
        Contact Mads Christensen for more information
    """,

    'author': "RL Software Development ApS",
    'website': "https://www.rlsd.dk/model/apps/dashboard-for-sale-2",

    'category': 'Sales/Sales',
    'version': '17.0.1.0.7',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'web',
        'sale',
        'board',
        'dashboard_custom',
    ],

    # always loaded
    'data': [        
        'views/menu.xml',        
    ],
    'assets': {
        'web.assets_backend': [
            'dashboard_sale/static/src/components/**/*.xml',
            'dashboard_sale/static/src/components/**/*.js',
            'dashboard_sale/static/src/components/**/*.scss',            
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
