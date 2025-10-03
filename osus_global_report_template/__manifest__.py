# -*- coding: utf-8 -*-
{
    'name': 'OSUS Global Report Template',
    'version': '17.0.1.0.0',
    'category': 'Reporting',
    'summary': 'Global Professional Report Template - Override All Odoo Reports',
    'description': """
        OSUS Global Report Template
        ============================
        * Override external_layout for all reports
        * Professional header and footer design
        * Consistent branding across all documents
        * Modern, clean design
        * Company logo and information
        * Custom color scheme
        * Professional typography
        * Print optimized
        * Mobile responsive
        
        Applies to ALL Reports:
        * Invoices & Bills
        * Sales Orders & Quotations
        * Purchase Orders
        * Delivery Orders & Receipts
        * Manufacturing Orders
        * Inventory Reports
        * Payment Receipts
        * And all other Odoo reports
    """,
    'author': 'OSUSAPPS',
    'website': 'https://www.osusapps.com',
    'depends': ['web', 'base'],
    'data': [
        'views/external_layout_template.xml',
        'views/report_assets.xml',
    ],
    'assets': {
        'web.report_assets_common': [
            'osus_global_report_template/static/src/scss/global_report_style.scss',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
