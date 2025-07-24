{
    'name': 'Enhanced Commission Management System',
    'version': '17.0.2.0.0',
    'summary': 'Advanced commission calculation with dual-group structure and flexible calculation methods',
    'description': '''
        Enhanced Commission Management System for Odoo 17
        
        Features:
        - Dual Commission Groups: External (Broker, Referrer, Cashback, Others) and Internal (Agent 1, Agent 2, Manager, Director)
        - Multiple Calculation Methods: Price Unit, Untaxed Total, Fixed Amount
        - Auto-calculation with rate/amount conversion
        - Smart buttons and reference management
        - Commission workflow with status tracking
        - Automated purchase order generation for commission payments
        - Enhanced reporting and analysis views
        - Proper field grouping and sorting
        
        This module provides a comprehensive solution for managing complex commission structures
        with both external and internal stakeholders.
    ''',
    'category': 'Sales/Commission',
    'author': 'Enhanced Commission Team',
    'website': 'https://www.yourcompany.com',
    'depends': ['sale', 'purchase', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'data/commission_demo_data.xml',
        'views/sale_order.xml',
        'views/purchase_order.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
    'images': ['static/description/banner.png'],
}
