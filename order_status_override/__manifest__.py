{
    'name': 'Order Status Override',
    'version': '17.0.1.0.0',
    'summary': 'Enhanced workflow management for sale orders',
    'description': """
        Enhanced Order Workflow Management
        ==================================
        
        Features:
        * Custom workflow stages for sale orders
        * User assignment and tracking
        * Workflow action wizard
        * Status history tracking
        * Enhanced views and reporting
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'category': 'Sales',
    'depends': [
        'sale',
        'mail',  # For activities and messaging
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/order_status_data.xml',
        'data/email_templates.xml',
        'data/paperformat.xml',
        'data/workflow_data.xml',
        'views/order_status_history_views.xml',
        'views/order_views_enhanced.xml',
        'views/workflow_dashboards.xml',
        'wizards/workflow_wizard_views.xml',
    ],
    'demo': [
        # 'demo/demo_data.xml',  # Add demo data if needed
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}