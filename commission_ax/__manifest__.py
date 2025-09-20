{
    'name': 'Advanced Commission Management',
    'version': '17.0.3.1.0',
    'category': 'Sales',
    'summary': 'World-class commission management with robust error handling and graceful degradation',
    'description': """
World-Class Commission Management System - ROBUST VERSION
========================================================

🚀 **ENTERPRISE-READY** - Built with robust error handling and graceful degradation

## Key Features

### 🛡️ **Robust Architecture**
- **Graceful Degradation**: Works with or without external dependencies
- **Error Handling**: Comprehensive error handling prevents installation failures
- **Modular Loading**: Models load independently with error recovery
- **Dependency Management**: Optional features based on available libraries

### 🔧 **Commission Management**
- **Commission Lines**: Modern relational structure with full workflow support
- **Multiple Calculation Methods**: Fixed, Percentage (Unit/Total/Untaxed)
- **Category Management**: Internal, External, Management, and Bonus commissions
- **State Management**: Draft → Calculated → Confirmed → Processed → Paid

### 📊 **Analytics & Reporting**
- **AI Analytics**: Advanced analytics with ML libraries (optional)
- **Basic Analytics**: Statistical analysis using Python built-ins
- **Performance Reports**: Comprehensive reporting system
- **Dashboard**: Real-time monitoring and KPIs

### 🔐 **Security & Access Control**
- **Role-based Access**: Granular permissions for users and managers
- **Data Integrity**: Validation rules and constraints
- **Audit Trail**: Complete tracking of commission changes

### 🔄 **Integration**
- **Purchase Order Integration**: Seamless PO creation and tracking
- **Multi-currency Support**: Handle global commission structures
- **Odoo 17 Compliance**: Latest framework standards

## Installation Notes

This module is designed to install successfully even if optional dependencies are missing:

- **Basic Functionality**: Always available with Python standard library
- **Enhanced Analytics**: Available with numpy, pandas, scikit-learn
- **Excel Export**: Available with xlsxwriter

Optional dependencies can be installed with:
```
pip install xlsxwriter numpy pandas scikit-learn
```

## Technical Excellence

- **Robust Error Handling**: No installation failures due to missing dependencies
- **Modular Design**: Features load independently
- **Performance Optimized**: Efficient database queries and caching
- **Future-Proof**: Easy to extend and maintain
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'sale',
        'purchase',
        'account',
    ],
    'data': [
        # Security (always load first)
        'security/security.xml',
        'security/ir.model.access.csv',

        # Core data
        'data/commission_types_data.xml',

        # Views (core functionality - must load in dependency order)
        'views/sale_order.xml',
        'views/purchase_order.xml',
        'views/res_partner_views.xml',
        'views/commission_line_views.xml',
        
        # Menu structure (must load after line views but before type views)
        'views/commission_menu.xml',
        
        # Views that reference menu items
        'views/commission_type_views.xml',

        # Reports (core)
        'reports/commission_report.xml',
        'reports/commission_report_template.xml',

        # Advanced features (load if files exist)
        'views/commission_wizard_views.xml',
        'views/commission_payment_wizard_views.xml',
        'views/commission_statement_wizard_views.xml',
        'data/cron_data.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
    'external_dependencies': {
        'python': [],  # No required dependencies - all optional
    },
    'post_init_hook': 'post_init_hook',
}