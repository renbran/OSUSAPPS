{
    'name': 'OSUS Enterprise Module',
    'version': '17.0.1.0.0',
    'category': 'Enterprise',
    'summary': 'Enterprise-grade custom module for OSUS',
    'description': """
        Advanced workflows, analytics, security, and UI for OSUS enterprise.
    """,
    'author': 'Your Company',
    'website': 'https://yourcompany.com',
    'depends': ['base', 'mail', 'web'],
    'data': [
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/menus.xml',
        'views/model_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'osus_enterprise_module/static/src/scss/**/*.scss',
            'osus_enterprise_module/static/src/js/**/*.js',
        ],
        'web.assets_frontend': [
            'osus_enterprise_module/static/src/scss/frontend.scss',
            'osus_enterprise_module/static/src/js/frontend.js',
        ],
        'web.qunit_suite_tests': [
            'osus_enterprise_module/static/tests/**/*.js',
        ],
    },
    'demo': [
        'data/demo_data.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}
