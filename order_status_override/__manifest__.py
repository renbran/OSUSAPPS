{
    'name': 'Custom Sales Order Status Workflow',
    'version': '17.0',
    'summary': 'Custom status bar workflow for Sales Orders',
    'description': '''
        This module adds a custom status bar workflow to Sales Orders with the following stages:
        - Draft (initial stage)
        - Documentation In-progress
        - Commission Calculation In-progress
        - Final Review
        - Approved
        
        Features:
        - Each stage can be assigned to a specific user
        - Activities are created automatically when moving to a new stage
        - Final review stage has options to reject or approve
        - Rejection returns the order to draft stage
    ''',
    'category': 'Sales',
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['sale', 'mail'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/order_status_data.xml',
        'views/order_status_views.xml',
        'views/order_views_assignment.xml',
        'views/email_template_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}