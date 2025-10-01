# -*- coding: utf-8 -*-
{
    'name': 'OSUS Deep Ocean Invoice & Receipt Reports',
    'version': '17.0.1.0.0',
    'summary': 'Professional Deep Ocean themed invoice and receipt reports with navy/azure design',
    'description': '''
        Deep Ocean Invoice & Receipt Reports
        ===================================
        - Professional Deep Ocean color scheme with navy depths and azure highlights
        - Customized invoice and receipt templates with modern design
        - Corporate branding with trust, stability, and technical expertise focus
        - Responsive design with mobile-friendly layouts
        - UAE VAT compliant layouts
        - Bootstrap 5 integration for professional styling
        - Multi-company support with logo integration
        - Print and PDF optimized layouts
        
        Color Palette:
        - Deep Navy: #1e3a8a (Primary professional depths)
        - Ocean Blue: #3b82f6 (Secondary business blue)
        - Sky Blue: #0ea5e9 (Accent highlights)  
        - Ice White: #f8fafc (Clean backgrounds)
        
        Perfect for data analytics and enterprise consulting businesses.
    ''',
    'category': 'Accounting/Accounting',
    'author': 'OSUS Real Estate',
    'website': 'https://www.osus.ae',
    'depends': [
        'account', 
        'base', 
        'sale', 
        'portal'
    ],
    'external_dependencies': {
        'python': ['qrcode', 'num2words'],
    },
    'data': [
        # Security
        'security/ir.model.access.csv',
        
        # Data
        'data/report_paperformat.xml',
        
        # Views
        'views/account_move_views.xml',
        
        # Reports
        'reports/deep_ocean_invoice_report.xml',
        'reports/deep_ocean_receipt_report.xml',
        'reports/report_templates.xml',
        
        # Menus
        'views/deep_ocean_menus.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'osus_deep_ocean_reports/static/src/css/deep_ocean_reports.css',
            'osus_deep_ocean_reports/static/src/js/deep_ocean_reports.js',
        ],
    },
    'images': ['static/description/index.html'],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}