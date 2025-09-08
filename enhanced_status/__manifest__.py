# -*- coding: utf-8 -*-
{
    'name': 'Sale Order Enhanced Workflow',
    'version': '17.0.2.0.0',
    'summary': 'Complete sale order workflow override with custom stages and financial tracking',
    'description': '''
        Enhanced Sale Order Workflow Module for Odoo 17
        
        This module completely overrides the default sale order workflow with:
        
        🔄 Custom Workflow Stages:
        - Documentation: Initial requirement gathering and documentation
        - Calculation: Pricing and technical calculations  
        - Approved: Final approval before execution
        - Completed: Locked final state with administrative override
        
        💰 Financial Tracking:
        - Real-time billing status (Unraised, Partially Invoiced, Fully Invoiced)
        - Payment status tracking (Unpaid, Partially Paid, Fully Paid)
        - Live invoiced amounts, paid amounts, and balance calculations
        
        🔒 Advanced Security:
        - Field locking in completed state
        - Administrative override capabilities
        - Stage-based access controls
        
        📊 Enhanced Views:
        - Kanban board by custom stages
        - Dynamic button visibility based on workflow state
        - Comprehensive financial dashboards
        - Automated workflow progression based on business rules
        
        🚀 Business Intelligence:
        - Automated completion detection
        - Financial reconciliation tracking
        - Purchase order and delivery completion monitoring
        - Notification system for stage changes
    ''',
    'category': 'Sales/Sales',
    'author': 'OSUSAPPS',
    'website': 'https://www.osusapps.com',
    'license': 'LGPL-3',
    'depends': ['sale', 'account', 'stock', 'purchase'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/sale_order_stage.xml',
        'views/sale_order_stage_views.xml',
        'views/sale_order_views.xml',
        'views/commission_menu.xml',
        'data/ir_cron_data.xml',
        'reports/commission_report_template.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'enhanced_status/static/src/css/sale_order_enhanced.css',
            'enhanced_status/static/src/js/sale_order_enhanced.js',
            'enhanced_status/static/src/xml/sale_order_templates.xml',
        ],
        'web.assets_backend': [
            'enhanced_status/static/src/css/sale_order_enhanced.css',
            'enhanced_status/static/src/js/sale_order_enhanced.js',
            'enhanced_status/static/src/xml/sale_order_templates.xml',
        ],
    },
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'sequence': 20,
}
