# -*- coding: utf-8 -*-
{
    'name': 'Project & Unit Management',
    'version': '17.0.1.0.0',
    'category': 'Sales',
    'summary': 'Manage projects, units, and pricing',
    'description': """
Project & Unit Management
=========================

Comprehensive project and unit management for real estate and construction projects.

Features:
* Project management with unit tracking
* Pricing management per unit
* Integration with sales and accounting

    """,
    'author': 'OSUSAPPS',
    'website': 'https://osusapps.com',
    'license': 'LGPL-3',
    'depends': ['base', 'sale_management'],
    'data': [
        'security/ir.model.access.csv',
        'views/project_unit_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
