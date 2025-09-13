{
    'name': 'Account Payment Final - Professional Payment Management',
    'version': '17.0.1.0.0',
    'category': 'Accounting/Accounting',
    'summary': 'Complete payment workflow with QR verification, 4-stage approval, and professional vouchers',
    'description': """
        Professional Payment Management System for Odoo 17
        ==================================================
        
        **Key Features:**
        • 4-stage approval workflow (Draft → Review → Approval → Authorization → Posted)
        • QR code generation and public verification portal
        • Professional payment and receipt voucher templates
        • Invoice/Bill approval integration
        • Comprehensive audit trail and approval history
        • Role-based security and permissions
        • Company-level configuration and branding
        
        **Business Benefits:**
        • Enhanced security through QR verification
        • Streamlined approval processes
        • Professional document generation
        • Complete audit compliance
        • Flexible workflow configuration
        
        This module provides enterprise-grade payment management with complete
        workflow control, security, and professional reporting capabilities.
    """,
    'author': 'OSUS Properties',
    'website': 'https://www.osusproperties.com',
    'depends': [
        'base',
        'account',
        'mail',
        'website',
        'portal'
    ],
    'external_dependencies': {
        'python': ['qrcode', 'Pillow']
    },
    'data': [
        # Security (Load first)
        'security/payment_security.xml',
        'security/ir.model.access.csv',
        
        # Data
        'data/sequence.xml',
        'data/mail_template_data.xml',
        
        # Views (Load in dependency order)
        'views/menus.xml',
        'views/account_payment_views.xml',
        'views/account_move_views.xml',
        'views/payment_approval_history_views.xml',
        'views/payment_qr_verification_views.xml',
        'views/payment_workflow_stage_views.xml',
        'views/res_config_settings_views.xml',
        'views/website_verification_templates.xml',
        'views/payment_dashboard_views.xml',
        
        # Reports
        'reports/payment_voucher_report.xml',
        'reports/payment_voucher_template.xml',
        'reports/payment_voucher_template_fixed.xml',
        
        # Wizards
        'wizards/register_payment.xml',
    ],
    'demo': [],
    'assets': {
        'web.assets_backend': [
            'payment_account_enhanced/static/src/css/osus_backend.css',
            'payment_account_enhanced/static/src/css/osus_report.css',
            'payment_account_enhanced/static/src/css/payment_voucher_style.css',
            'payment_account_enhanced/static/src/scss/payment_voucher_report.scss',
            # Add JS widgets/components if present
            # 'payment_account_enhanced/static/src/js/payment_widget.js',
        ],
        'web.assets_frontend': [
            # Add portal/website CSS/SCSS if present
            # 'payment_account_enhanced/static/src/css/verification_portal.css',
        ],
        # QWeb templates (if any)
        # 'payment_account_enhanced/static/src/xml/payment_templates.xml',
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'sequence': 15,
}
