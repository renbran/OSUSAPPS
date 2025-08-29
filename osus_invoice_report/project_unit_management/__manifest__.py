# -*- coding: utf-8 -*-
{
    'name': 'Project Unit Management',
    'version': '17.0.1.0.0',
    'category': 'Project',
    'summary': 'Adds project unit and project_id to sales orders and related models',
    'description': """
Project Unit Management
=======================

This module adds project unit and project_id fields to sales orders and related models for better project tracking and integration.
""",
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'sale',
        'project',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/project_unit_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
