{
    'name': 'Advanced Commission Management',
    'version': '17.0.3.0.0',
    'category': 'Sales',
    'summary': 'World-class commission management with optimized performance, commission lines architecture, and unified monitoring dashboard',
    'description': """
World-Class Commission Management System
======================================

🚀 **PERFORMANCE OPTIMIZED** - Built for enterprise-scale commission processing

## Key Features

### 🏗️ **Modern Architecture**
- **Commission Lines Structure**: Scalable relational architecture replacing scattered fields
- **Unified Dashboard**: Real-time monitoring and analytics
- **Performance Metrics**: Sub-second commission calculations with timing metrics
- **Alert System**: Proactive monitoring with automated notifications

### 📊 **Business Intelligence**
- **Commission Dashboard**: Interactive analytics with graphs, pivot tables, and KPIs
- **Performance Reports**: Advanced filtering and grouping capabilities
- **Trend Analysis**: Historical commission data with forecasting
- **Top Performer Tracking**: Identify high-performing commission partners

### ⚡ **Performance Enhancements**
- **Optimized Queries**: Eliminated N+1 query problems
- **Batch Processing**: Efficient handling of bulk commission operations
- **Caching**: Smart caching for frequently accessed commission data
- **Database Indexing**: Proper indexing for fast searches and reports

### 🔧 **Advanced Commission Management**
- **Commission Lines**: Modern relational structure with full workflow support
- **Multiple Calculation Methods**: Fixed, Percentage (Unit/Total/Untaxed)
- **Category Management**: Internal, External, Management, and Bonus commissions
- **State Management**: Draft → Calculated → Confirmed → Processed → Paid
- **Legacy Migration**: Seamless migration from old commission structure

### 📈 **Monitoring & Analytics**
- **Real-time Dashboard**: Commission performance at a glance
- **Automated Alerts**: Overdue commissions, high amounts, threshold breaches
- **Commission Trends**: Monthly/quarterly analysis with growth metrics
- **Partner Performance**: Top performers and commission distribution

### 🔐 **Enhanced Security**
- **Role-based Access**: Granular permissions for users and managers
- **Audit Trail**: Complete tracking of commission changes
- **Data Integrity**: Validation rules and constraints

### 🔄 **Workflow Automation**
- **Automated PO Creation**: Streamlined purchase order generation
- **Status Tracking**: Visual workflow states with automatic transitions
- **Payment Monitoring**: Track invoiced, paid, and outstanding amounts
- **Scheduled Actions**: Automated commission processing and monitoring

### 📋 **Professional Reporting**
- **Commission Statements**: Agent-specific PDF/Excel reports
- **Comprehensive Reports**: Deal analysis with project and unit details
- **Export Capabilities**: PDF, Excel, and CSV formats
- **Custom Filtering**: Advanced search and grouping options

### 🔗 **Integration Features**
- **Purchase Order Integration**: Seamless PO creation and tracking
- **Project Management**: Link commissions to projects and units
- **Multi-currency Support**: Handle global commission structures
- **Company-wise Separation**: Multi-company environment support

### 🛠️ **Technical Excellence**
- **Modern Odoo 17 Standards**: Latest framework capabilities
- **Extensible Architecture**: Easy customization and module integration
- **Performance Monitoring**: Built-in metrics and optimization tools
- **Error Handling**: Robust exception management with logging
- **Data Migration Tools**: Safe migration from legacy structures
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'sale',
        'purchase', 
        'account',
        'stock',
        'portal',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/commission_types_data.xml',
        'data/cron_data.xml',
        'data/commission_report_wizard_action.xml',
        'data/commission_purchase_orders_action.xml',
        'data/commission_report_template.xml',
        'views/commission_type_views.xml',
        'views/sale_order.xml',
        'views/purchase_order.xml',
        'views/commission_line_views.xml',
        'views/commission_wizard_views.xml',
        'views/commission_statement_wizard_views.xml',
        'views/deals_commission_report_wizard_views.xml',
        'reports/commission_report.xml',
        'reports/commission_report_template.xml',
        'reports/commission_statement_report.xml',
        'reports/per_order_commission_report.xml',
        'reports/deals_commission_report.xml',
        'views/commission_menu.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
    'external_dependencies': {
        'python': ['xlsxwriter'],
    },
    'post_init_hook': 'post_init_hook',
}