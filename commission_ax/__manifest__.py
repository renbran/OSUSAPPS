{
    'name': 'Advanced Commission Management',
    'version': '17.0.1.0.0',
    'category': 'Sales',
    'summary': 'Advanced commission management with business logic constraints and professional reporting',
    'description': """
Advanced Commission Management System
====================================

This module provides comprehensive commission management for sales orders with:

Business Logic Features:
- Commission processing only allowed for fully invoiced orders
- Automatic cascade cancellation of commission POs when sales orders are cancelled
- User confirmation dialogs for destructive operations
- Prerequisites validation before commission processing

Commission Features:
- Multiple commission types (External and Internal)
- Flexible commission calculation methods (Fixed, Percentage of Unit Price, Percentage of Total)
- Legacy commission support for backward compatibility
- Commission purchase order generation
- Commission status tracking (Draft → Calculated → Confirmed)

Reporting Features:
- Professional commission reports with clear formatting
- Export to PDF functionality matching company branding
- Comprehensive commission breakdowns
- VAT calculations and net company share

Technical Features:
- Robust error handling and logging
- Scheduled actions for commission monitoring
- Enhanced UI with status indicators
- Search filters for commission-related records
- Cascade operations with user confirmations
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'sale',
        'purchase', 
        'account',
        'stock',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/cron_data.xml',
    'data/commission_report_wizard_action.xml',
    'data/commission_purchase_orders_action.xml',
        'views/sale_order.xml',
        'views/purchase_order.xml',
        'views/commission_wizard_views.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
    'images': ['static/description/icon.png'],
}