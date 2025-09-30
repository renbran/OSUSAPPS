# -*- coding: utf-8 -*-

{
    'name': 'Videographer Resource Booking',
    'version': '17.0.2.0',
    'author': 'Ubbels.com',
    'price': 0.0,
    'currency': 'EUR',
    'maintainer': 'Ubbels.com',
    'support': 'info@ubbels.com',
    'images': ['static/description/app_logo.jpg'],
    'license': 'OPL-1',
    'website': 'https://www.ubbels.com',
    'category':  'Services/Booking',
    'summary': 'Professional videographer booking system with availability management, packages, and payments',
    'description':
        """
        World-Class Videographer Resource Booking System
        ================================================

        Complete solution for managing videographer bookings with:
        - Videographer profiles with portfolios and skills
        - Service packages (Wedding, Corporate, Events)
        - Advanced availability management with buffer times
        - Dynamic pricing and seasonal rates
        - Equipment and resource allocation
        - Payment integration with deposits
        - Client reviews and ratings
        - Automated notifications (Email/SMS)
        - Analytics dashboard
        - Mobile-responsive interface

        Keywords: videographer, booking, resource scheduling, photography,
        video production, appointment, calendar, online booking, service booking

        """,
    'depends': [
        'calendar',
        'website',
        'portal',
        'mail',
        'payment',
        'hr'
    ],
    'data': [
        # Security
        'security/ir.model.access.csv',

        # Data
        'data/ir_sequence_data.xml',
        'data/default_data.xml',
        'data/mail_template_data.xml',

        # Views - Backend (Load actions before menus that reference them)
        'views/videographer_profile_view.xml',
        'views/service_package_view.xml',
        'views/appointment_slot_view.xml',
        'views/appointment_option_view.xml',
        'views/booking_view.xml',
        'views/menus.xml',

        # Views - Frontend
        'views/appointment_template.xml',
        'views/appointment_portal_template.xml',
        'views/s_daterange.xml',
    ],
    'qweb': [
    ],
    'assets': {
        'web.assets_frontend': [
            '/s2u_online_appointment/static/src/scss/daterange.scss',
            '/s2u_online_appointment/static/src/js/daterange.js',
            '/s2u_online_appointment/static/src/js/main.js',
        ]
    },
    'installable': True,
    'auto_install': False,
}

