# -*- coding: utf-8 -*-
{
    'name': 'Calendar Extended',
    'version': '17.0.1.0.0',
    'category': 'Productivity',
    'summary': 'Extended Calendar functionality with advanced features',
    'description': """
Calendar Extended
=================

This module extends the default Odoo calendar with advanced features:

Features:
---------
* Enhanced calendar views (daily, weekly, monthly, yearly)
* Recurring events with custom patterns
* Event categories and color coding
* Event reminders and notifications
* Resource booking and availability
* Calendar sharing and permissions
* Event templates
* Advanced filtering and search
* Event analytics and reporting
* Integration with other modules

Technical Features:
-------------------
* Custom calendar views
* Enhanced event model
* Wizard for bulk operations
* API endpoints for external integration
* Mobile-responsive design
* Export/Import functionality
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'calendar',
        'mail',
        'web',
        'resource',
        'hr',
        'project',
    ],
    'data': [
        'security/calendar_extended_security.xml',
        'security/ir.model.access.csv',
        'data/calendar_data.xml',
        'data/email_templates.xml',
        'views/calendar_internal_meeting_views.xml',
        'views/calendar_department_group_views.xml',
        'views/calendar_event_type_views.xml',
        'views/calendar_resource_views.xml',
        'views/calendar_template_views.xml',
        'views/calendar_meeting_wizard_views.xml',
        'wizards/calendar_event_wizard_views.xml',
        'wizards/calendar_bulk_operation_views.xml',
        'wizards/calendar_report_wizard_views.xml',
        'wizards/calendar_quick_meeting_wizard_views.xml',
        'views/calendar_extended_menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'calendar_extended/static/src/js/calendar_extended_widget.js',
            'calendar_extended/static/src/js/calendar_extended_components.js',
            'calendar_extended/static/src/css/calendar_extended.css',
            'calendar_extended/static/src/xml/calendar_extended_templates.xml',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 10,
}
