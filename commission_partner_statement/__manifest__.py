# -*- coding: utf-8 -*-
{
    'name': 'SCHOLARIX Commission Statement System',
    'version': '17.0.2.0.0',
    'category': 'Sales',
    'summary': 'Comprehensive commission statement system for SCHOLARIX with multi-agent reporting',
    'description': """
SCHOLARIX Commission Statement System
=====================================

A comprehensive commission statement reporting system designed specifically for SCHOLARIX
that provides consolidated reports for all agents with professional PDF output.

Core Features:
--------------
* Multi-Agent Consolidated Reports - Generate reports for all agents in one document
* Professional SCHOLARIX-Branded Templates - Custom PDF layouts with company branding
* Advanced Filtering & Sorting - Date ranges, agent selection, commission types, payment status
* Commission Type Breakdown - Direct Sales (5%), Referral Bonus (2%), Team Override (1%)
* Executive Summary Dashboard - Overview statistics for management review
* Period-Based Filtering - Monthly, quarterly, yearly, and custom date ranges

Commission Calculation Logic:
-----------------------------
* Direct Sales: 5% commission rate on direct sales
* Referral Bonus: 2% commission rate on referrals  
* Team Override: 1% commission rate for team management
* Automatic commission categorization and calculation
* Integration with existing commission_ax module data

Report Formats:
---------------
* Professional PDF Reports - SCHOLARIX branded with signatures section
* Excel Spreadsheet Export - Detailed data export for analysis
* Individual Agent Statements - Personal commission statements
* Consolidated Multi-Agent Reports - All agents in single document

Security & Access Control:
--------------------------
* Sales Managers: Full access to all reports and agent data
* Agents: Access only to their own commission statements  
* Accounting Team: Read-only access for verification and payment processing
* Commission Analysts: Report generation and analysis capabilities

Integration:
------------
* Seamless integration with commission_ax module
* Compatible with enhanced_status module
* Extends res.partner model with SCHOLARIX-specific functionality
* Works with existing Odoo sales, accounting, and partner management

Performance & Scalability:
--------------------------
* Optimized for up to 1000+ agents
* Efficient database queries and report generation
* Background processing for large reports
* Memory-efficient data handling

Professional Output:
--------------------
* Print-ready PDF formats with proper page breaks
* Mobile-responsive design for tablet review
* Consistent SCHOLARIX branding across all documents
* Signature sections for approval workflow
* Terms and conditions integration
    """,
    'author': 'OSUS Properties Development Team',
    'website': 'https://www.osusproperties.com',
    'depends': [
        'base', 
        'sale', 
        'contacts',
        'commission_ax',  # Required for commission fields
        'enhanced_status',  # Required for order status
    ],
    'data': [
        'security/security.xml',  # Basic security groups first
        'security/ir.model.access.csv',
        'data/ir_cron_data.xml',
        'views/res_partner_views.xml',
        'views/scholarix_commission_views.xml',  # This creates the models
        'views/scholarix_commission_menus.xml',
        'security/model_security.xml',  # Model-dependent security rules AFTER models
        'reports/commission_partner_reports.xml',
        'reports/commission_partner_templates.xml',
        'reports/scholarix_consolidated_reports.xml',
        'reports/scholarix_consolidated_templates.xml',
        'reports/scholarix_agent_templates.xml',
        'wizards/scholarix_commission_report_wizard.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'commission_partner_statement/static/src/js/action_manager.js',
        ]
    },
    'demo': [],
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
    'application': True,  # This is now a full application
    'license': 'LGPL-3',
    'external_dependencies': {
        'python': ['xlsxwriter'],
    },
}
