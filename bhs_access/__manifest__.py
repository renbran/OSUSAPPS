# -*- coding: utf-8 -*-
{
    'name': 'Groups Access Management',
    'version': '1.0',
    'author': 'Bac Ha Software',
    'website': 'https://bachasoftware.com',
    'maintainer': 'Bac Ha Software',
    'category': 'Administration',
    'summary': "Manage User accesses.",
    'description': "Manage User's groups in a separated menu.",
    'depends': ['base'],
    'data': [
        'security/bhs_access_security.xml',
        'views/res_users.xml',
    ],
    'external_dependencies': {
    },
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'license': 'LGPL-3'
}