# -*- coding: utf-8 -*-

{
    'name': 'Online Appointment Booking System',
    'version': '17.0.1.0.0',
    'author': 'OSUSAPPS',
    'maintainer': 'OSUSAPPS Development Team',
    'support': 'support@osusapps.com',
    'images': ['static/description/app_logo.jpg'],
    'license': 'LGPL-3',
    'website': 'https://www.osusapps.com',
    'category': 'Website/eCommerce',
    'summary': 'Professional online appointment booking system for website visitors',
    'description': """
    Professional Online Appointment Booking System
    =============================================
    
    Allow website visitors to book appointments seamlessly through your website with this comprehensive booking system.
    
    Key Features:
    * Interactive calendar with availability display
    * Flexible time slot management per user
    * Customizable appointment options with duration
    * Integration with Odoo Calendar
    * Portal access for appointment management
    * Email notifications and confirmations
    * Mobile-responsive design
    * Multi-user support with individual schedules
    
    Perfect for:
    * Healthcare providers
    * Professional services
    * Consultancy businesses
    * Service-based companies
    * Any business requiring appointment scheduling
    
    Technical Features:
    * Timezone-aware scheduling
    * Conflict detection and prevention
    * Comprehensive security controls
    * Performance optimized
    * Fully integrated with Odoo ecosystem
    """,
    'depends': [
        'base',
        'calendar',
        'website',
        'portal',
        'mail',
        'contacts'
    ],
    'external_dependencies': {
        'python': ['pytz']
    },
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/appointment_data.xml',
        'views/appointment_template.xml',
        'views/appointment_portal_template.xml',
        'views/menus.xml',
        'views/appointment_slot_view.xml',
        'views/appointment_option_view.xml',
        'views/appointment_registration_view.xml',
        'views/s_daterange.xml',
    ],
    'demo': [
        'demo/appointment_demo.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'online_appointment/static/src/scss/daterange.scss',
            'online_appointment/static/src/js/daterange.js',
            'online_appointment/static/src/js/main.js',
        ],
        'web.assets_backend': [
            'online_appointment/static/src/css/appointment_backend.css',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 10,
    'price': 0.0,
    'currency': 'USD',
}

