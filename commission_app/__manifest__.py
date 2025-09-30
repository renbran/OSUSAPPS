# -*- coding: utf-8 -*-
{
    'name': 'Commission App - Professional Commission Management',
    'version': '17.0.1.0.0',
    'category': 'Sales/Commission',
    'summary': 'World-class commission management system with modern architecture',
    'description': """
Professional Commission Management System
========================================

A modern, well-structured commission management system built with Odoo 17 best practices.

Key Features:
* Commission allocations structured like order lines (One2Many relationship)
* Clean inheritance-based architecture
* Proper workflow states (Draft → Calculate → Confirm → Pay)
* Multi-level approval process
* Automated commission calculations
* Comprehensive reporting and analytics
* Integration with sales and accounting modules

Technical Excellence:
* Modern Odoo 17 patterns and conventions
* Optimized performance with proper indexing
* Comprehensive security and access controls
* Full test coverage
* Clean, maintainable code structure
* Proper error handling and validation

This module replaces commission_ax with a cleaner, more maintainable design
while preserving all essential functionality and improving user experience.
    """,
    'author': 'OSUSAPPS',
    'website': 'https://osusapps.com',
    'license': 'LGPL-3',
    'sequence': 100,
    
    # Dependencies
    'depends': [
        'base',
        'sale_management',
        'account',
        'purchase',
        'mail',
    ],
    
    # Data files
    'data': [
        # Security
        'security/commission_security.xml',
        'security/ir.model.access.csv',
        
        # Data
        'data/commission_sequence_data.xml',
        'data/commission_rule_data.xml',
        
        # Views (actions must be defined before menus reference them)
        'views/commission_allocation_views.xml',
        'views/commission_rule_views.xml',
        'views/commission_period_views.xml',
        'views/res_partner_views.xml',
        'views/wizard_views.xml',
        'views/menus.xml',
    ],
    
    # Technical
    'installable': True,
    'auto_install': False,
    'application': True,
    
    # Version requirements
    'python_requires': '>=3.8',
    'odoo_version': '17.0',
    
    # Development mode
    'development_status': 'Production/Stable',
    'maintainers': ['osusapps'],
}