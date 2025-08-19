# -*- coding: utf-8 -*-
{
    'name': 'OSUS Payment Approval System',
    'version': '17.0.1.1.0',
    'category': 'Accounting/Payments',
    'summary': 'OSUS Properties - Professional Payment Voucher System with Multi-Stage Approval Workflow',
    'description': """
        OSUS Properties Payment Approval System
        ======================================
        
        Professional payment voucher management system designed specifically for 
        OSUS Properties with comprehensive approval workflows and security features.
        
        Key Features:
        -------------
        * 4-Stage Approval Workflow: Reviewer -> Approver -> Authorizer -> Final Approval
        * QR Code Verification: Secure payment authentication system
        * OSUS Branding: Professional styling with OSUS Properties brand colors
        * Role-Based Security: Granular access control for different user roles
        * Digital Signatures: Electronic signature capture for each approval stage
        * Professional Reports: OSUS-branded voucher reports with QR verification
        * Automated Sequences: Smart voucher numbering system
        * Email Notifications: Workflow status updates for stakeholders
        * Mobile Responsive: Optimized for desktop, tablet, and mobile devices
        * Audit Trail: Complete payment history and approval tracking
        
        Technical Excellence:
        -------------------
        * Odoo 17 Native: Built with latest ORM patterns and OWL framework
        * CloudPepper Ready: Optimized for CloudPepper hosting environment
        * Security First: Implements Odoo security best practices
        * Performance Optimized: Efficient database queries and caching
        * API Integration: REST endpoints for external system integration
        * Test Coverage: Comprehensive automated testing suite
        
        Perfect for organizations requiring professional payment processing
        with strong approval controls and comprehensive audit capabilities.
    """,
    'author': 'OSUS Properties Development Team',
    'website': 'https://www.osusproperties.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'account',
        'web',
        'mail',
        'portal',
        'website',
    ],
    'data': [
        # Security (Load First)
        'security/payment_security.xml',
        'security/ir.model.access.csv',
        
        # Data and Sequences
        'data/payment_sequences.xml',
        'data/email_templates.xml',
        'data/system_parameters.xml',
        
        # Main Views
        'views/account_payment_views.xml',
        'views/account_move_views.xml',
        'views/invoice_bill_report_template.xml',
        'views/res_company_views.xml',
        'views/res_config_settings_views.xml',
        'views/menus.xml',
        
        # Reports
        'reports/payment_voucher_report.xml',
        'reports/payment_voucher_actions.xml',
        'reports/payment_voucher_template.xml',
        
        # Enhanced Reports
        'views/payment_voucher_report_enhanced.xml',
        
        # Website/Portal Views
        'views/payment_verification_templates.xml',
        'views/payment_voucher_template.xml',
        'views/payment_voucher_enhanced_template.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # OSUS Branding & Core Styles (Load First)
            'account_payment_final/static/src/scss/osus_branding.scss',
            'account_payment_final/static/src/scss/professional_payment_ui.scss',
            'account_payment_final/static/src/scss/enhanced_form_styling.scss',
            
            # CloudPepper Emergency Fix (Single Optimized Version)
            'account_payment_final/static/src/js/emergency_error_fix.js',
            'account_payment_final/static/src/js/cloudpepper_compatibility_patch.js',
            
            # Core Payment Functionality
            'account_payment_final/static/src/js/payment_dashboard.js',
            'account_payment_final/static/src/js/payment_workflow_safe.js',
            
            # Component-specific styles
            'account_payment_final/static/src/scss/components/payment_widget.scss',
            'account_payment_final/static/src/scss/components/table_enhancements.scss',
            'account_payment_final/static/src/scss/views/form_view.scss',
            'account_payment_final/static/src/scss/payment_voucher.scss',

            # XML templates
            'account_payment_final/static/src/xml/payment_templates.xml',
        ],
        'web.assets_web_dark': [
            # CloudPepper compatibility for dark theme
            'account_payment_final/static/src/js/emergency_error_fix.js',
            'account_payment_final/static/src/js/cloudpepper_compatibility_patch.js',
            
            # Dark theme specific styles
            'account_payment_final/static/src/scss/osus_branding.scss',
            
            # XML templates for dark theme
            'account_payment_final/static/src/xml/payment_templates.xml',
        ],
        'web.assets_common': [
            # Report-specific styles for PDF generation
            'account_payment_final/static/src/scss/responsive_report_styles.scss',
        ],
        'web.assets_frontend': [
            # Frontend verification portal
            'account_payment_final/static/src/scss/frontend/verification_portal.scss',
            'account_payment_final/static/src/js/frontend/qr_verification.js',
            
            # Emergency fix for frontend
            'account_payment_final/static/src/js/emergency_error_fix.js',
        ],
        'web.qunit_suite_tests': [
            'account_payment_final/static/tests/payment_widgets_tests.js',
        ],
    },
    'external_dependencies': {
        'python': ['qrcode', 'pillow'],
    },
    'demo': [
        'demo/demo_payments.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'sequence': 10,
}