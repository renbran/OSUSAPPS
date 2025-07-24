{
    'name': 'Account Statement',
    'version': '17.0.1.0.0',
    'category': 'Accounting/Contacts',
    'summary': 'Generate Account Statements for Partners - Works in both Accounting and Contacts Apps',
    'description': """
        Account Statement Module
        ========================
        This module allows you to generate account statements for partners
        showing all invoices and payments within a date range.

        Features:
        - Generate PDF reports
        - Export to Excel (when report_xlsx is installed)
        - Filter by partner and date range
        - Show running balance
        - Comprehensive partner information
        - Access from both Accounting and Contacts apps
        - Direct access from partner form view
        - Multi-company support
        - State management workflow
    """,    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'account',
        'contacts',
        'web',
    ],
    'data': [
        'security/account_statement_security.xml',
        'security/ir.model.access.csv',
        'data/report_paperformat.xml',
        'report/account_statement_report_action.xml',
        'report/account_statement_report_template.xml',        'views/account_statement_views.xml',
        'wizard/account_statement_wizard_views.xml',
        'views/res_partner_views.xml',  # Add partner form integration
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}