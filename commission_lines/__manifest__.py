{
    'name': 'Commission Lines Management',
    'version': '17.0.1.0.0',
    'category': 'Sales',
    'summary': 'Clean commission management with normalized commission lines',
    'description': """
Commission Lines Management System
==================================

This module provides a clean, normalized approach to commission management:

Core Features:
- Centralized commission lines model
- Easy reporting and statement generation  
- Clean separation of concerns
- Flexible commission structures
- Audit trail and history tracking

Architecture Benefits:
- One commission = One record
- Easy filtering and reporting
- Simple data relationships
- Scalable and maintainable
- Clear audit trail
    """,
    'author': 'Your Company',
    'depends': ['base', 'sale', 'account', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/commission_line_views.xml',
        'views/sale_order_views.xml',
        'views/partner_views.xml',
        'views/commission_reports.xml',
        'wizard/commission_statement_wizard_views.xml',
        'report/commission_statement_report.xml',
        'data/commission_types_data.xml',
    ],
    'installable': True,
    'application': True,
}