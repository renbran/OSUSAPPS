{
    'name': 'Social Media Lead Capture',
    'version': '17.0.1.0.0',
    'category': 'CRM',
    'summary': 'Automated lead generation from social media and messaging apps',
    'description': """
        Complete solution for capturing leads from:
        - WhatsApp Business
        - Facebook Messenger & Lead Ads
        - Instagram DMs
        - Telegram
        - LinkedIn Messages
        - Twitter/X DMs
        
        Features:
        - Automated webhook handling
        - Real-time lead creation
        - Communication logging
        - Lead scoring
        - Multi-platform dashboard
        - Response automation
    """,
    'author': 'Your Company',
    'website': 'https://yourcompany.com',
    'depends': ['base', 'crm', 'mail', 'website', 'utm'],
    'data': [
        'data/models.xml',
        'security/ir.model.access.csv',
        'data/lead_sources.xml',
        'data/activity_types.xml',
        'data/utm_data.xml',
        'views/social_config_views.xml',
        'views/crm_lead_views.xml',
        'views/social_dashboard_views.xml',
        'views/message_log_views.xml',
        'views/menu_views.xml',
        'wizards/social_setup_wizard.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}