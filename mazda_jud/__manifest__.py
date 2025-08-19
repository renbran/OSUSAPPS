{
    'name': 'Mazda Jud',
    'version': '17.0.1.0.0',
    'category': 'Custom',
    'summary': 'Mazda Jud custom workflow and reporting',
    'description': 'Implements custom workflow and reporting for Mazda Jud.',
    'author': 'Your Company',
    'website': 'https://yourcompany.com',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'security/mazda_jud_security.xml',
        'data/sequences.xml',
        'data/groups.xml',
        'data/ir_cron.xml',
        'views/mazda_jud_views.xml',
        'views/mazda_jud_order_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'mazda_jud/static/description/icon.png',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
}
