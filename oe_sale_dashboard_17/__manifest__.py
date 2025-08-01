{
    'name': 'OSUS Executive Sales Dashboard - Enhanced & Merged',
    'version': '17.0.1.0.0',  # Major version bump for merged best practices
    'category': 'Sales',
    'summary': 'Advanced executive sales dashboard with merged best practices and enhanced analytics.',
    'description': """
        Enhanced Executive Sales Dashboard - Merged Best Practices Edition
        
        🚀 **New Merged Features:**
        - **Defensive Field Checking**: Compatible with different Odoo setups and field configurations
        - **Auto-refresh Capability**: Real-time data updates with configurable intervals
        - **Advanced Error Handling**: Comprehensive error management with user-friendly messages
        - **Performance Tracking**: Load time monitoring and performance metrics
        - **Enhanced KPIs**: Conversion rate, pipeline velocity, revenue growth, and average deal size
        - **Data Quality Indicators**: Real-time assessment of data completeness and accuracy
        - **Export Functionality**: CSV export capability for external analysis
        - **Responsive Design**: Mobile-first approach with adaptive layouts
        
        📊 **Core Features:**
        - **Smart Date & Category Filtering**: Automatic fallback from booking_date to create_date
        - **Category Scorecards**: Comprehensive performance metrics by sales categories
        - **Sub-category Analytics**: Draft, Sales Orders, and Invoice breakdowns with totals
        - **Interactive Visualizations**: Chart.js 4.4.0 with enhanced styling and animations
        - **Sales Type Distribution**: Professional pie charts with hover effects
        - **Trend Analysis**: Line charts showing revenue progression over time
        - **Comparison Analytics**: Side-by-side performance comparisons
        - **Ranking Tables**: Performance leaderboards with medal indicators
        - **Executive KPI Cards**: Modern card design with gradient styling
        
        🔧 **Technical Excellence:**
        - **Field Compatibility**: Automatic detection of booking_date, sale_value fields
        - **Graceful Degradation**: Works with and without sales type configurations
        - **Error Recovery**: Robust error handling with retry mechanisms
        - **Performance Optimization**: Efficient data loading and chart rendering
        - **Browser Compatibility**: Cross-browser support with fallbacks
        - **Accessibility**: ARIA labels and keyboard navigation support
        
        Transform your sales data into actionable business insights with this comprehensive
        dashboard that combines the best practices from multiple implementations.
    """,
    'author': 'RENBRAN - Enhanced with AI Best Practices',
    'website': 'WWW.TACHIMAO.COM',
    'depends': ['web', 'sale_management', 'osus_invoice_report', 'le_sale_type'],
    'data': [
        'data/sale_order_data.xml',
        'views/dashboard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # Enhanced merged assets with best practices
            'oe_sale_dashboard_17/static/src/css/dashboard_merged.css',
            'oe_sale_dashboard_17/static/src/js/dashboard_merged.js',
            'oe_sale_dashboard_17/static/src/xml/dashboard_merged_template.xml',
        ],
    },
    'images': ['static/description/banner.gif'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'AGPL-3',
}
