# Unified Commission Management System

## 📋 Overview

The Unified Commission Management System is a comprehensive Odoo 17 module that combines the best features from multiple commission management approaches into a single, enterprise-grade solution.

## 🚀 Location Path

```
D:\RUNNING APPS\ready production\latest\OSUSAPPS\commission_unified\
```

## 🎯 Key Features

### Commission Types
- **Rule-Based**: Standard, Partner-based, Product-based, Discount-based
- **Stakeholder-Based**: External (Broker, Referrer, Cashback, Others) + Internal (Agent1, Agent2, Manager, Director)
- **Legacy**: Backward compatibility with existing commission structures

### Calculation Methods
- Fixed Amount
- Percentage of Unit Price
- Percentage of Untaxed Total
- Rule-Based Calculations

### Workflow Management
- Status tracking: Draft → Calculated → Approved → Confirmed → Paid
- Manual and automatic processing
- Approval workflows

### Payment Processing
- Customer Invoices
- Purchase Orders
- Journal Entries

### Reporting & Analytics
- Comprehensive PDF reports
- Excel exports
- Real-time dashboard
- Advanced analytics

## 📁 Module Structure

```
commission_unified/
├── __manifest__.py           # Module configuration
├── __init__.py              # Module initialization
├── README.md                # This file
├── models/                  # Core business logic
│   ├── commission_lines.py  # Main commission records
│   ├── sale_order.py       # Sales order integration
│   ├── commission_rules.py # Commission rules engine
│   └── ...
├── views/                   # User interface
├── security/               # Access rights and security
├── data/                   # Configuration and demo data
├── wizard/                 # User interaction wizards
├── report/                 # Reporting engine
└── static/                 # Static assets
```

## 🔧 Installation

1. **Copy Module**
   ```bash
   cp -r commission_unified /path/to/odoo/addons/
   ```

2. **Update Module List**
   ```bash
   odoo-bin -c config.conf -d database -u all --stop-after-init
   ```

3. **Install Module**
   - Go to Apps menu in Odoo
   - Search for "Unified Commission Management"
   - Click Install

## 🔄 Migration from Existing Modules

### From sales_commission_users
1. Use the Migration Wizard: `Commission → Tools → Migration Wizard`
2. Select "Migrate from sales_commission_users"
3. Follow the migration steps

### From commission_ax
1. Use the Migration Wizard: `Commission → Tools → Migration Wizard`
2. Select "Migrate from commission_ax"
3. Follow the migration steps

### Merge Both Modules
1. Use the Migration Wizard: `Commission → Tools → Migration Wizard`
2. Select "Merge data from both modules"
3. Follow the migration steps

## ⚙️ Configuration

### System Parameters
Access via Settings → Technical → Parameters → System Parameters

- `commission.auto_calculate_on_confirm`: Auto-calculate commissions on order confirmation
- `commission.default_payment_method`: Default payment processing method
- `commission.require_approval`: Require approval for commission processing
- `commission.max_commission_percentage`: Maximum allowed commission percentage
- `commission.enable_audit_log`: Enable detailed audit logging

### Security Groups
- **Commission Manager**: Full access to all commission features
- **Commission User**: Limited access for sales users
- **Commission Viewer**: Read-only access for reporting

## 📊 Usage

### Basic Commission Setup
1. Go to `Sales → Commission → Commission Rules`
2. Create commission rules for different scenarios
3. Configure commission rates and calculation methods

### Processing Commissions
1. Confirm a sale order
2. Go to the Commission tab
3. Use "Calculate Commissions" button
4. Review and approve commissions
5. Process payments using preferred method

### Reporting
1. Go to `Sales → Commission → Reports`
2. Select report type and filters
3. Generate and download reports

## 🛠️ Development

### Adding Custom Commission Types
1. Extend the `commission_type` selection field in `commission_lines.py`
2. Add calculation logic in `commission_calculator.py`
3. Update views and security as needed

### Custom Payment Methods
1. Extend the `commission_payment.py` model
2. Add new payment processing methods
3. Update workflow and user interface

## 🔍 Troubleshooting

### Common Issues
1. **Commission not calculating**: Check user permissions and commission rules
2. **Payment processing fails**: Verify accounting configuration
3. **Migration errors**: Ensure data backup before migration

### Logs
Check Odoo logs for detailed error information:
```bash
tail -f /var/log/odoo/odoo.log | grep commission
```

## 📞 Support

For support and customizations, contact the development team or refer to the module documentation.

## 📄 License

This module is licensed under LGPL-3. See the license file for details.

## 🚀 Version History

- **1.0.0**: Initial unified commission system
  - Combined features from sales_commission_users and commission_ax
  - Enhanced workflow management
  - Advanced reporting capabilities
  - Migration tools included