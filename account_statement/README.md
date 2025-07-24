# Account Statement Module for Odoo 17

## 📋 Overview

The **Account Statement** module provides comprehensive account statement generation capabilities for partners, working seamlessly in both **Contacts** and **Accounting** applications.

## ✨ Key Features

### 🎯 Multi-App Integration
- **Contacts App**: Generate statements directly from partner records
- **Accounting App**: Full accounting integration with advanced features
- **Dual Menu Access**: Available in both app menus

### 📊 Advanced Statement Generation
- **Date Range Filtering**: Flexible date range selection
- **Account Type Filtering**: All accounts, receivables only, or payables only
- **Zero Balance Options**: Show/hide zero balance entries
- **Running Balance Calculation**: Real-time balance tracking

### 📁 Export Options
- **PDF Reports**: Professional formatted statements
- **Excel Export**: Detailed spreadsheet with formatting (when `report_xlsx` is available)
- **Graceful Degradation**: Excel features optional, module works without dependencies

### 🔐 Security & Access Control
- **Multi-Level Permissions**: Accounting users, Contact managers, and restricted users
- **Multi-Company Support**: Company-based access control
- **User-Based Record Rules**: Contact users see only their own statements

### 📋 Workflow Management
- **State Management**: Draft → Confirmed → Cancelled workflow
- **Message Tracking**: Full audit trail with chatter integration
- **Status Visualization**: Color-coded status indicators

## 🚀 Installation

### Prerequisites
- Odoo 17.0
- `base`, `account`, `contacts`, and `web` modules (auto-installed)
- `report_xlsx` module (optional, for Excel export)

### Installation Steps

1. **Copy Module**
   ```bash
   cp -r account_statement /path/to/odoo/addons/
   ```

2. **Update Module List**
   - Go to Apps → Update Apps List

3. **Install Module**
   - Search for "Account Statement"
   - Click Install

4. **Optional: Install Excel Support**
   ```bash
   pip install xlsxwriter
   ```
   Then install the `report_xlsx` module from Apps

## 🎯 Usage Guide

### From Contacts App

1. **Direct Partner Access**
   - Navigate to Contacts
   - Open any partner record
   - Click the "Account Statement" smart button

2. **Menu Access**
   - Go to Contacts → Account Statements
   - Choose "Generate Statement" or "View Statements"

### From Accounting App

1. **Menu Access**
   - Navigate to Accounting → Reporting → Account Statements
   - Choose "Generate Statement" or "View Statements"

2. **Advanced Features**
   - Full workflow management
   - Advanced filtering options
   - Bulk operations

### Statement Generation Wizard

1. **Select Partner**
   - Choose from customers and suppliers
   - Auto-filtered domain for active partners

2. **Configure Options**
   - Set date range (defaults to current month)
   - Choose account filter (All/Receivables/Payables)
   - Toggle zero balance lines

3. **Generate & Export**
   - Preview statement lines
   - Export to PDF or Excel
   - Save as permanent record

## 🔧 Configuration

### Security Groups

- **Account Users**: Full access to all features
- **Account Managers**: Full administrative access
- **Contact Users**: Limited access, own records only

### Permissions

| Group | Read | Write | Create | Delete |
|-------|------|-------|--------|--------|
| Account Users | ✅ | ✅ | ✅ | ✅ |
| Account Managers | ✅ | ✅ | ✅ | ✅ |
| Contact Users | ✅ | ✅ | ✅ | ❌ |

## 📁 Module Structure

```
account_statement/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── account_statement.py
│   └── account_statement_wizard.py
├── views/
│   ├── account_statement_views.xml
│   ├── account_statement_wizard_views.xml
│   └── res_partner_views.xml
├── security/
│   ├── account_statement_security.xml
│   └── ir.model.access.csv
├── data/
│   └── report_paperformat.xml
└── report/
    ├── account_statement_report_action.xml
    └── account_statement_report_template.xml
```

## 🎨 Key Enhancements Made

### 1. **Multi-App Compatibility**
- Added `contacts` dependency
- Dual menu structure
- Partner form integration

### 2. **Optional Dependencies**
- Graceful handling of missing `report_xlsx`
- Excel export only available when dependencies are met
- No installation failures due to missing packages

### 3. **Enhanced Security**
- Contact-specific security groups
- User-based record rules
- Multi-company compliance

### 4. **Improved UX**
- Smart buttons on partner forms
- Enhanced filtering options
- Better status visualization
- Message tracking integration

### 5. **Robust Data Handling**
- Better error handling
- Input validation
- Performance optimizations

## 🔍 Troubleshooting

### Common Issues

**1. Excel Export Not Available**
- Install `xlsxwriter`: `pip install xlsxwriter`
- Install `report_xlsx` module from Apps

**2. Permission Denied**
- Check user belongs to appropriate security groups
- Verify multi-company setup if applicable

**3. No Data in Statements**
- Ensure partner has posted journal entries
- Check date range covers transaction periods
- Verify account type filter settings

**4. Menu Items Missing**
- Refresh browser after installation
- Check user has appropriate app access rights

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Odoo logs for detailed error messages
3. Verify all prerequisites are met
4. Contact your system administrator

## 📄 License

LGPL-3 - See Odoo standard licensing terms

---

**Version**: 17.0.1.0.0  
**Author**: Your Company  
**Category**: Accounting/Contacts  
**Auto Install**: False  
**Installable**: True
