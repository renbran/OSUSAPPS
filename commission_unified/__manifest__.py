# -*- coding: utf-8 -*-
#############################################################################
#
#    Unified Commission Management System
#
#    Copyright (C) 2025-TODAY Commission Unified Team
#    Author: Unified Commission Development Team
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
{
    'name': 'Unified Commission Management System',
    'version': '17.0.1.0.0',
    'category': 'Sales/Commission',
    'summary': '''Comprehensive commission management combining rule-based,
        stakeholder-based, and legacy commission structures with advanced
        workflow management and multiple payment methods''',
    'description': '''
        Unified Commission Management System for Odoo 17

        This module combines the best features from multiple commission systems:

        🎯 COMMISSION TYPES:
        • Rule-Based: Standard, Partner-based, Product-based, Discount-based
        • Stakeholder-Based: External (Broker, Referrer, Cashback, Others)
                            Internal (Agent1, Agent2, Manager, Director)
        • Legacy: Consultant, Manager, Second Agent, Director (for backward compatibility)

        💰 CALCULATION METHODS:
        • Fixed Amount
        • Percentage of Unit Price
        • Percentage of Untaxed Total
        • Rule-Based Calculations

        🔄 WORKFLOW MANAGEMENT:
        • Draft → Calculated → Approved → Confirmed → Paid
        • Manual and automatic processing options
        • Status tracking and approval workflows

        💳 PAYMENT PROCESSING:
        • Customer Invoices (Traditional approach)
        • Purchase Orders (Vendor payment approach)
        • Journal Entries (Direct accounting approach)

        📊 ADVANCED REPORTING:
        • Comprehensive PDF reports
        • Excel analytics exports
        • Real-time dashboard
        • Commission analytics and insights

        🛡️ SECURITY & COMPLIANCE:
        • Role-based access control
        • Complete audit trail
        • Data validation and constraints
        • Multi-company support

        ⚙️ CONFIGURATION:
        • Flexible commission rules engine
        • Configurable calculation methods
        • System parameters for customization
        • Migration tools from existing systems

        This unified system provides enterprise-grade commission management
        suitable for complex business structures with multiple stakeholders.
    ''',
    'author': 'Unified Commission Team',
    'company': 'Commission Management Solutions',
    'maintainer': 'Unified Commission Team',
    'website': 'https://www.commission-unified.com',
    'depends': [
        'base',
        'sale_management',
        'account',
        'purchase',
        'hr',
        'contacts'
    ],
    'data': [
        # Security
        'security/commission_security.xml',
        'security/ir.model.access.csv',

        # Data
        'data/commission_sequences.xml',
        'data/commission_config.xml',
        'data/commission_cron.xml',

        # Views
        'views/commission_menus.xml',
        'views/commission_lines_views.xml',
        'views/sale_order_views.xml',
        'views/commission_rules_views.xml',
        'views/commission_workflow_views.xml',
        'views/commission_dashboard_views.xml',

        # Wizards
        'wizard/commission_calculator_wizard_views.xml',
        'wizard/commission_migration_wizard_views.xml',
        'wizard/commission_bulk_processor_views.xml',
        'wizard/commission_report_wizard_views.xml',

        # Reports
        'report/commission_action.xml',
        'report/commission_templates.xml',

        # Demo Data
        'data/commission_demo_data.xml',
    ],
    'demo': [
        'data/commission_demo_data.xml',
    ],
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 10,
    'external_dependencies': {
        'python': ['reportlab'],
    },
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
}