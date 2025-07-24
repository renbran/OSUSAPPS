{
    'name': 'Automated Employee Announcements',
    'version': '17.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Automated birthday and work anniversary announcements',
    'description': """
        This module provides automated email notifications for:
        - Employee birthdays
        - Work anniversaries
        - Sale order notifications to agents
        
        Features:
        - Configurable mail templates
        - Automated cron jobs
        - Flexible rule-based system
        - Integration with HR and Sales modules
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'hr',
        'mail',
        'sale_management',
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/mail_templates.xml',
        'data/automated_mail_rule_data.xml',
        'data/cron_jobs.xml',
        'views/automated_mail_rule_views.xml',
        'views/hr_employee.xml',
        'views/menu.xml',
    ],
    'demo': [
        'demo/demo_data.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}