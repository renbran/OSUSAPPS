{
    'name': 'Commission Lines',
    'version': '17.0.1.0.0',
    'category': 'Sales',
    'summary': 'Manage commission lines and calculations',
    'description': """
Commission Lines Management
===========================

This module provides functionality for:

* Commission line management
* Commission calculations
* Integration with sales orders
* Reporting capabilities

Features:
---------
* Create and manage commission lines
* Calculate commission amounts
* Track commission status
* Generate commission reports

Installation:
-------------
1. Install the module from Apps menu
2. Configure commission settings
3. Start using commission features

Author: OSUS Properties Development Team
Website: https://www.osusproperties.com
    """,
    'author': 'OSUS Properties Development Team',
    'website': 'https://www.osusproperties.com',
    'depends': [
        'base',
        'sale',
        'account',
        'mail',
        'commission_ax',
    ],
    'data': [
        # Security
        'security/security.xml',
        'security/ir.model.access.csv',
        
        # Data
        'data/commission_data.xml',
        
        # Views
        'views/commission_lines_views.xml',
        'views/commission_menus.xml',
        'views/commission_reports.xml',
        'views/res_partner_views.xml',
        
        # Wizards
        'views/commission_statement_wizard_views.xml',
        
        # Reports
        'reports/commission_statement_report.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'commission_lines/static/src/css/commission_lines.css',
            'commission_lines/static/src/js/commission_lines.js',
            'commission_lines/static/src/js/commission_dashboard.js',
            'commission_lines/static/src/xml/commission_templates.xml',
        ],
    },
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
    'external_dependencies': {
        'python': [],
    },
}