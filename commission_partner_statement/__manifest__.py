# -*- coding: utf-8 -*-
{
    'name': 'Commission Partner Statement Report',
    'version': '17.0.1.0.0',
    'category': 'Sales',
    'summary': 'Commission statement reports for partners based on sale orders',
    'description': """
Commission Partner Statement Report
===================================

This module extends the partner management system to provide comprehensive 
commission statement reporting capabilities based on sale order commissions.

Features:
---------
* Generate commission statements for partners in PDF and Excel formats
* Extract commission data from sale orders (External, Internal, Legacy)
* Filter by date range and partner
* Automatic monthly statement generation
* Commission summary and analytics
* Professional report templates

Integration:
------------
* Works with commission_ax module
* Extends res.partner model
* Compatible with enhanced_status module

Report Columns:
---------------
* Order Reference - Sale order number
* Order Date - Date when order was placed
* Customer - Customer name from sale order
* Commission Type - Type of commission (External/Internal/Legacy)
* Commission Category - Specific category (Broker, Agent, etc.)
* Rate - Commission rate percentage
* Amount - Commission amount
* Status - Order and commission status
    """,
    'author': 'OSUS Properties Development Team',
    'website': 'https://www.osusproperties.com',
    'depends': [
        'base', 
        'sale', 
        'contacts',
        'commission_ax',  # Required for commission fields
        'enhanced_status',  # Required for order status
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_cron_data.xml',
        'views/res_partner_views.xml',
        'reports/commission_partner_reports.xml',
        'reports/commission_partner_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'commission_partner_statement/static/src/js/action_manager.js',
        ]
    },
    'demo': [],
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
    'external_dependencies': {
        'python': ['xlsxwriter'],
    },
}
