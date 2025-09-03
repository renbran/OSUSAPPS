{
    'name': 'Commission Statement Reports',
    'version': '17.0.1.0.0',
    'category': 'Sales',
    'summary': 'Generate detailed commission statement reports in PDF and Excel formats',
    'description': """
Commission Statement Reports
============================

This module extends the existing commission management system to provide comprehensive 
commission statement reporting capabilities.

Features:
---------
* Generate commission statements in PDF and Excel formats
* Filter by date range, commission partner, or specific sale orders
* Support for all commission types (internal, external, legacy)
* Detailed commission breakdown with partner, order, and customer information
* Preview functionality before generating reports
* Smart buttons for quick access from sale orders
* Security groups for commission users and managers

Report Columns:
---------------
* Commission Name - Partner receiving the commission
* Order Ref - Sale order reference number
* Customer Reference - Customer name from the sale order
* Commission Type - Type of commission calculation (Fixed, Unit Price %, Total %)
* Rate - Commission rate or fixed amount
* Total - Total commission amount
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'sale',
        'purchase',
        'web',
    ],
    'data': [
        'security/commission_security.xml',
        'security/ir.model.access.csv',
        'data/commission_data.xml',
        'views/commission_statement_views.xml',
        'views/commission_statement_pdf.xml',
    ],
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