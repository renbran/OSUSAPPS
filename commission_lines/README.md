# Commission Lines Management Module

A comprehensive Odoo module for managing sales commissions with a clean, normalized approach.

## Module Structure

```
commission_lines/
├── __init__.py                     # Main module init
├── __manifest__.py                 # Module manifest
├── models/                         # Data models
│   ├── __init__.py
│   ├── commission_line.py          # Main commission model
│   ├── sale_order.py              # Sale order extensions
│   └── res_partner.py             # Partner extensions
├── views/                          # XML views
│   ├── commission_line_views.xml   # Commission line views & menus
│   ├── sale_order_views.xml       # Sale order view extensions
│   ├── partner_views.xml          # Partner view extensions
│   └── commission_reports.xml     # Report actions & views
├── wizard/                         # Transient models
│   ├── __init__.py
│   ├── commission_statement_wizard.py
│   └── commission_statement_wizard_views.xml
├── report/                         # QWeb reports
│   └── commission_statement_report.xml
├── data/                           # Seed data
│   └── commission_types_data.xml
├── security/                       # Access rights
│   └── ir.model.access.csv
├── static/                         # Web assets
│   ├── description/
│   │   └── index.html
│   └── src/
│       ├── css/
│       │   └── commission_lines.css
│       └── js/
│           └── commission_dashboard.js
└── README.md                       # This file
```

## Features

### Core Functionality
- ✅ Centralized commission line management
- ✅ Multiple commission types (sales, referral, target, bonus)
- ✅ Workflow states (draft → confirmed → paid)
- ✅ Partner commission agent setup
- ✅ Sale order integration
- ✅ Automatic commission generation

### Views & UI
- ✅ Tree, form, kanban, and search views
- ✅ Statistical buttons and smart buttons
- ✅ Commission dashboard (basic structure)
- ✅ Graph and pivot views for analysis

### Reporting
- ✅ Commission statement wizard
- ✅ PDF commission statement report
- ✅ Commission analysis views
- ✅ Partner and sale order extensions

### Security
- ✅ Role-based access control
- ✅ User/Manager/Salesperson permissions
- ✅ Data validation and constraints

### Data Management
- ✅ Demo data for testing
- ✅ Email templates for notifications
- ✅ System configuration parameters
- ✅ Sequence generation for commission references

## Installation

1. Copy the module to your Odoo addons directory
2. Update the module list: Apps → Update Apps List
3. Install: Search for "Commission Lines Management" and install

## Quick Start

1. **Setup Commission Agents**:
   - Go to Contacts
   - Create/edit a contact
   - Enable "Is Commission Agent"
   - Set default commission rate

2. **Configure Auto-Generation** (optional):
   - The module auto-generates commissions when sale orders are confirmed
   - This is controlled by system parameters

3. **Create Commission Lines**:
   - Manual: Commissions → Commission Lines → Create
   - Auto: Confirm a sale order with a commission agent as salesperson

4. **Generate Reports**:
   - Go to Commissions → Reports → Commission Statement
   - Select filters and generate PDF or view lines

## Technical Notes

- **Python Compatibility**: Odoo 17.0+
- **Dependencies**: base, sale, account
- **Database Changes**: Adds new models and extends existing ones
- **Performance**: Optimized with proper indexing and computed fields

## Module Dependencies

```python
'depends': ['base', 'sale', 'account']
```

## Next Steps

Consider extending with:
- Multi-level commission structures
- Commission approval workflows
- Integration with payroll
- Advanced commission calculation rules
- API endpoints for external integrations

## Support

For questions or support, refer to the module documentation or contact the development team.