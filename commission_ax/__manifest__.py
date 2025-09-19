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
- **Automated Commission Creation**: Smart commission generation from sales orders
- **Bulk Payment Processing**: Efficient payment workflow for multiple commissions
- **Report Generation**: Automated commission statements and reports
- **Email Notifications**: Automated alerts and status updates

## Technical Excellence

### 🎯 **Odoo 17 Compliance**
- **Modern Field Syntax**: Latest Odoo 17 field definitions and attributes
- **Optimized ORM**: Efficient use of Odoo ORM with performance considerations
- **Security Framework**: Proper access control and record rules
- **Integration Ready**: Seamless integration with standard Odoo modules

### 🔧 **Developer Features**
- **Clean Code Architecture**: Well-structured, maintainable codebase
- **Comprehensive Documentation**: Detailed inline documentation and guides
- **Extensible Design**: Easy to extend and customize
- **API Support**: RESTful endpoints for external integrations
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
        'data/commission_payment_cron.xml',
        'data/commission_report_wizard_action.xml',
        'data/commission_purchase_orders_action.xml',
        'data/commission_report_template.xml',
        'views/sale_order.xml',
        'views/purchase_order.xml',
        'views/res_partner_views.xml',
        'views/commission_line_views.xml',
        'views/commission_payment_wizard_views.xml',
        'views/commission_lines_replace_wizard_views.xml',
        'views/commission_wizard_views.xml',
        'views/commission_statement_wizard_views.xml',
        'views/deals_commission_report_wizard_views.xml',
        'reports/commission_report.xml',
        'reports/commission_report_template.xml',
        'reports/commission_statement_report.xml',
        'reports/per_order_commission_report.xml',
        'reports/deals_commission_report.xml',
        'views/commission_menu.xml',
        'views/commission_type_views.xml',
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