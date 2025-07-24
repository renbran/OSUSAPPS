{
    'name': 'OSUS Executive Sales Dashboard',
    'version': '17.0.0.3.0',  # Bumped version to add deployment robustness improvements
    'category': 'Sales',
    'summary': 'Custom dashboard for yearly sales report.',
    'description': """
        Enhanced Executive Sales Dashboard with modern visualizations and business intelligence.
        
        Key Features:
        - Interactive Chart.js powered visualizations
        - Executive-level KPI cards with gradient designs
        - Real-time sales funnel analysis
        - Enhanced date range filtering with booking_date reference
        - Beautiful modern UI with animated components
        - Responsive design optimized for all devices
        - Advanced revenue distribution charts
        - Sales performance trend analysis
        - Professional color-coded tables and cards
        
        Transform your sales data into beautiful, actionable insights with this comprehensive
        executive dashboard using booking_date and sale_value fields from the osus_invoice_report module.
    """,
    'author': 'RENBRAN',
    'website': 'WWW.TACHIMAO.COM',
    'depends': ['web', 'sale_management', 'osus_invoice_report', 'le_sale_type'],
    'data': [
        'data/sale_order_data.xml',
        'views/dashboard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # Primary CDN loading for Chart.js
            'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js',
            # Module assets in proper loading order
            'oe_sale_dashboard_17/static/src/css/dashboard.css',
            'oe_sale_dashboard_17/static/src/js/chart.fallback.js',    # Must load before any chart usage
            'oe_sale_dashboard_17/static/src/js/field_mapping.js',     # Field validation and mapping
            'oe_sale_dashboard_17/static/src/js/compatibility.js',     # Compatibility layer and error handling
            'oe_sale_dashboard_17/static/src/js/dashboard.js',         # Main dashboard component
        ],
        'web.assets_web': [
            'oe_sale_dashboard_17/static/src/xml/dashboard_template.xml',
        ],
        'web.assets_web_dark': [
            'oe_sale_dashboard_17/static/src/xml/dashboard_template.xml',
        ],
    },
    'images': ['static/description/banner.gif'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'AGPL-3',
}
