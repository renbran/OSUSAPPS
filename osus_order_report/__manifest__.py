# -*- coding: utf-8 -*-
{
    'name': 'OSUS Professional Order Report',
    'version': '17.0.1.0.0',
    'category': 'Sales',
    'summary': 'Professional Sales Order Report with Modern Design',
    'description': """
        Professional Sales Order Report
        ================================
        * Modern, clean design
        * Professional layout with company branding
        * Clear order details and line items
        * Terms and conditions section
        * Signature section
        * Mobile responsive
        * Print optimized
    """,
    'author': 'OSUSAPPS',
    'website': 'https://www.osusapps.com',
    'depends': ['sale', 'web'],
    'data': [
        'views/report_sale_order_template.xml',
        'report/sale_order_report.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'osus_order_report/static/src/css/order_report_style.css',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
