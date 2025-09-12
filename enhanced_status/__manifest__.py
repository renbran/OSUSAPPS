# -*- coding: utf-8 -*-
{
    'name': 'Sale Order Enhanced Workflow',
    'version': '17.0.1.0.0',
    'summary': 'Sale order workflow with custom states and commission reporting',
    'description': '''
        Enhanced Sale Order Workflow Module for Odoo 17
        
        This module provides enhanced sale order workflow with:
        
        🔄 Custom Workflow States:
        - Draft: Initial state for order creation
        - Confirmed: Order confirmed and ready for processing
        - Completed: Final locked state with administrative override
        
        💰 Commission Reporting:
        - Professional commission payout reports
        - OSUS Properties branded templates
        - PDF generation with detailed calculations
        
        🔒 Order Security:
        - Field locking in completed state
        - Administrative override capabilities
        - Workflow-based access controls
        
        📊 Enhanced Views:
        - Clean workflow button integration
        - Commission report generation
        - User-friendly status management
        
        ✨ Key Features:
        - Simplified workflow without complex dependencies
        - Professional commission reporting system
        - Compatible with standard Odoo installation
    ''',
    'author': 'OSUS Properties',
    'website': 'https://osus.properties',
    'category': 'Sales',
    'depends': ['sale'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/sale_order_simple_view.xml',
        'views/commission_menu.xml',
        'reports/commission_report_template.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
