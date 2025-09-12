{
    'name': 'Sale Order Type with Dynamic Filters',
    'version': '17.0.1.0.0',
    'author': 'Luna ERP Solutions / Enhanced by OSUS',
    'website': 'https://www.lunerpsolution.com',
    'license': 'LGPL-3',
    'support': 'support@lunerpsolution.com',
    'category': 'Sales',
    'summary': 'Enhanced sale order types with dynamic search filters and analytics',
    'description': '''
        Enhanced Sale Order Type Module for Odoo 17
        
        This module provides comprehensive sale order type management with:
        
        🔍 Dynamic Search Filters:
        - Automatically generated filters for each sale order type
        - Real-time filter updates when types are created/modified
        - Enhanced search capabilities
        
        📊 Analytics & Statistics:
        - Order count per type
        - Total amount calculations
        - Visual kanban view with statistics
        
        🎨 Enhanced Views:
        - Kanban view with color coding
        - Statistical dashboard
        - Quick action buttons
        
        ⚡ Advanced Features:
        - Sequence-based ordering
        - Automatic prefix assignment
        - Dynamic menu integration
        - RESTful API endpoints
        
        🔧 Technical Features:
        - JavaScript-based dynamic filter injection
        - Controller endpoints for AJAX calls
        - Model enhancements with computed fields
        - Optimized search performance
    ''',
    'depends': ['sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_type_views.xml',
        'views/sale_order_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'le_sale_type/static/src/js/dynamic_sale_type_filters.js',
        ],
    },
    'images': ["static/description/banner.png"],
    'installable': True,
    'application': False,
    'auto_install': False,
    'sequence': 20,
}
