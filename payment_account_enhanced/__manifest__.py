{
    'name': 'OSUS Payment Voucher Enhanced',
    'version': '17.0.1.0.0',
    'category': 'Accounting/Payments',
    'summary': 'Enhanced Payment Vouchers with OSUS Brand Identity',
    'description': '''
        Enhanced Payment Voucher System for OSUS Properties
        ==================================================
        
        Features:
        * OSUS branded payment voucher reports with wow factor design
        * Follows OSUS brand guidelines (Burgundy & Gold color scheme)
        * Enhanced payment tracking and authorization
        * Professional typography using Montserrat font
        * Responsive design for both print and digital viewing
        * Advanced signature sections with approval workflow
        * Gradient backgrounds and premium visual elements
        * Enhanced security and validation for large payments
        * Customizable company branding options
        
        Design Elements:
        * Primary colors: Burgundy (#8B1538) and Gold (#D4AF37)
        * Modern gradients and shadow effects
        * Sophisticated card-based layout
        * Professional signature sections
        * Responsive grid system
        * Print-optimized color management
        
        This module transforms standard Odoo payment vouchers into 
        premium, branded documents that reflect OSUS Properties' 
        luxury real estate excellence.
    ''',
    'author': 'OSUS Properties',
    'website': 'https://www.osusproperties.com',
    'license': 'LGPL-3',
    'depends': [
        'account',
        'web',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/payment_security.xml',
        'views/account_payment_views.xml',
        'reports/payment_voucher_reports.xml',
        'data/paper_format_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'payment_account_enhanced/static/src/css/osus_backend.css',
        ],
        'web.report_assets_pdf': [
            'payment_account_enhanced/static/src/css/osus_report.css',
        ],
    },
    'images': [
        'static/description/icon.png',
        'static/description/banner.png',
        'static/description/screenshot_1.png',
        'static/description/screenshot_2.png',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'sequence': 1,
    'price': 199.99,
    'currency': 'USD',
}