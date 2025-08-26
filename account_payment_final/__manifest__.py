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
<<<<<<< Updated upstream
        'views/invoice_bill_report_template.xml',
=======
>>>>>>> Stashed changes
        'views/res_company_views.xml',
        'views/res_config_settings_views.xml',
        'views/menus.xml',
        
        # Reports
        'reports/payment_voucher_report.xml',
        'reports/payment_voucher_actions.xml',
        'reports/payment_voucher_template.xml',
        
<<<<<<< Updated upstream
        # Enhanced Reports
        'views/payment_voucher_report_enhanced.xml',
        
=======
>>>>>>> Stashed changes
        # Website/Portal Views
        'views/payment_verification_templates.xml',
        'views/payment_voucher_template.xml',
        'views/payment_voucher_enhanced_template.xml',
    ],
    'assets': {
        'web.assets_backend': [
<<<<<<< Updated upstream
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
=======
            # IMMEDIATE EMERGENCY FIX: Must load FIRST before anything else
            ('prepend', 'account_payment_final/static/src/js/immediate_emergency_fix.js'),
            # NUCLEAR FIX: Load nuclear fix FIRST to prevent ALL JavaScript crashes
            ('prepend', 'account_payment_final/static/src/js/cloudpepper_nuclear_fix.js'),
            ('prepend', 'account_payment_final/static/src/js/cloudpepper_enhanced_handler.js'),
            ('prepend', 'account_payment_final/static/src/js/cloudpepper_critical_interceptor.js'),
            ('prepend', 'account_payment_final/static/src/js/cloudpepper_js_error_handler.js'),
            ('prepend', 'account_payment_final/static/src/js/emergency_error_fix.js'),
            ('prepend', 'account_payment_final/static/src/js/cloudpepper_compatibility_patch.js'),
            
            # NEW COMPREHENSIVE CLOUDPEPPER FIXES
            ('prepend', 'account_payment_final/static/src/js/cloudpepper_owl_fix.js'),
            ('prepend', 'account_payment_final/static/src/js/cloudpepper_payment_fix.js'),
            
            # Real-time workflow enhancements (NEW)
            'account_payment_final/static/src/js/payment_workflow_realtime.js',
            
            # CloudPepper optimization and console fixes (REMOVED problematic import files)
            # DISABLED: 'account_payment_final/static/src/js/cloudpepper_console_optimizer.js', # Contains import statements
            # DISABLED: 'account_payment_final/static/src/js/unknown_action_handler.js', # Contains import statements
            
            # OSUS Branding & Core Styles (priority loading)
            'account_payment_final/static/src/scss/osus_branding.scss',
            'account_payment_final/static/src/scss/professional_payment_ui.scss',
            'account_payment_final/static/src/scss/enhanced_form_styling.scss',
            'account_payment_final/static/src/scss/realtime_workflow.scss',
>>>>>>> Stashed changes
            
            # Component-specific styles
            'account_payment_final/static/src/scss/components/payment_widget.scss',
            'account_payment_final/static/src/scss/components/table_enhancements.scss',
<<<<<<< Updated upstream
            'account_payment_final/static/src/scss/views/form_view.scss',
            'account_payment_final/static/src/scss/payment_voucher.scss',

=======
            
            # View-specific styles
            'account_payment_final/static/src/scss/views/form_view.scss',
            'account_payment_final/static/src/scss/payment_voucher.scss',

            # Core JavaScript functionality (REMOVED files with import statements)
            # DISABLED: 'account_payment_final/static/src/js/error_handler.js', # Contains import statements
            'account_payment_final/static/src/js/payment_workflow_safe.js', # Safe non-module version
            # DISABLED: 'account_payment_final/static/src/js/components/payment_approval_widget_enhanced.js', # Contains import statements
            # DISABLED: 'account_payment_final/static/src/js/fields/qr_code_field.js', # Contains import statements
            # DISABLED: 'account_payment_final/static/src/js/views/payment_list_view.js', # Contains import statements

>>>>>>> Stashed changes
            # XML templates
            'account_payment_final/static/src/xml/payment_templates.xml',
        ],
        'web.assets_web_dark': [
<<<<<<< Updated upstream
            # CloudPepper compatibility for dark theme
            'account_payment_final/static/src/js/emergency_error_fix.js',
            'account_payment_final/static/src/js/cloudpepper_compatibility_patch.js',
            
            # Dark theme specific styles
            'account_payment_final/static/src/scss/osus_branding.scss',
=======
            # IMMEDIATE EMERGENCY FIX for dark theme
            ('prepend', 'account_payment_final/static/src/js/immediate_emergency_fix.js'),
            # Nuclear fix and critical error handlers for dark theme (MUST LOAD FIRST)
            ('prepend', 'account_payment_final/static/src/js/cloudpepper_nuclear_fix.js'),
            ('prepend', 'account_payment_final/static/src/js/cloudpepper_enhanced_handler.js'),
            ('prepend', 'account_payment_final/static/src/js/cloudpepper_critical_interceptor.js'),
            ('prepend', 'account_payment_final/static/src/js/cloudpepper_js_error_handler.js'),
            
            # Additional dark theme JavaScript (REMOVED problematic files)
            # DISABLED: 'account_payment_final/static/src/js/views/payment_list_view.js', # Contains import statements
>>>>>>> Stashed changes
            
            # XML templates for dark theme
            'account_payment_final/static/src/xml/payment_templates.xml',
        ],
        'web.assets_common': [
            # Report-specific styles for PDF generation
            'account_payment_final/static/src/scss/responsive_report_styles.scss',
        ],
        'web.assets_frontend': [
<<<<<<< Updated upstream
            # Frontend verification portal
            'account_payment_final/static/src/scss/frontend/verification_portal.scss',
            'account_payment_final/static/src/js/frontend/qr_verification.js',
            
            # Emergency fix for frontend
            'account_payment_final/static/src/js/emergency_error_fix.js',
=======
            # IMMEDIATE EMERGENCY FIX for frontend
            ('prepend', 'account_payment_final/static/src/js/immediate_emergency_fix.js'),
            # Frontend verification portal
            'account_payment_final/static/src/scss/frontend/verification_portal.scss',
            'account_payment_final/static/src/js/frontend/qr_verification.js',
>>>>>>> Stashed changes
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