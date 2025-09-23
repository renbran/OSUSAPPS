# -*- coding: utf-8 -*-
{
    'name': 'Custom Calendar Invitations',
    'version': '17.0.1.0.0',
    'category': 'Calendar',
    'summary': 'Enhanced calendar invitation emails with Google Calendar integration',
    'description': """
Custom Calendar Invitations - Enhanced email templates with Google Calendar integration.

Features:
* Professional branded email templates
* Enhanced Google Calendar integration with proper URL encoding
* One-click calendar addition (Google Calendar + ICS download)
* Responsive design for desktop and mobile
* Visual calendar widget in emails
* RSVP buttons (Accept/Decline/Maybe)
* Proper timezone handling
* Video call link integration
* Location with map links
* Organizer information display

Technical:
* Overrides default Odoo calendar invitation template
* Extends calendar.event model for enhanced functionality
* Proper URL encoding for special characters
* Multi-language support
* Error handling and logging

Installation:
1. Install the module through Apps menu
2. Calendar invitations will automatically use the new template
3. No additional configuration required

Compatibility: Odoo 17.0+
    """,
    'author': 'OSUS Development Team',
    'website': 'https://osus.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'calendar',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/calendar_templates.xml',
    ],
    'demo': [],
    'images': [],
    'installable': True,
    'auto_install': False,
    'application': False,
    'sequence': 100,
    'pre_init_hook': None,
    'post_init_hook': None,
    'uninstall_hook': None,
}