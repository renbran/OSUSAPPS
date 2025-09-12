# Enhanced Status - Sale Order Workflow Module

## Overview

The Enhanced Status module provides a comprehensive workflow enhancement for Odoo 17 sale orders, featuring custom stages, financial tracking, and professional commission reporting.

## Features

### 🔄 Custom Workflow Stages
- **Documentation**: Initial requirement gathering and documentation
- **Calculation**: Pricing and technical calculations  
- **Approved**: Final approval before execution
- **Completed**: Locked final state with administrative override

### 💰 Financial Tracking
- Real-time billing status (Unraised, Partially Invoiced, Fully Invoiced)
- Payment status tracking (Unpaid, Partially Paid, Fully Paid)
- Live invoiced amounts, paid amounts, and balance calculations

### 🔒 Advanced Security
- Field locking in completed state
- Administrative override capabilities
- Stage-based access controls

### 📊 Enhanced Views
- Kanban board by custom stages
- Dynamic button visibility based on workflow state
- Comprehensive financial dashboards
- Automated workflow progression based on business rules

### 🚀 Business Intelligence
- Automated completion detection
- Financial reconciliation tracking
- Purchase order and delivery completion monitoring
- Notification system for stage changes

### 📋 Professional Commission Reports
- **Deal Summary**: Comprehensive order overview with unit pricing
- **External Commissions**: Broker, referrer, cashback, and other external commissions
- **Internal Commissions**: Manager, director, and agent commissions
- **Legacy Commissions**: Support for historical commission structures
- **Commission Summary**: Detailed breakdown with VAT calculations and net profits
- **Professional Styling**: OSUS Properties branded reports with proper formatting

## Technical Details

### Dependencies
- `sale` - Core sales functionality
- `account` - Financial tracking and invoicing
- `stock` - Inventory and delivery tracking
- `purchase` - Purchase order integration

### Models

#### Sale Order Stage (`sale.order.stage`)
Custom workflow stages for sale orders with:
- Name and description
- Sequence ordering
- Fold status for kanban views
- Color coding

#### Sale Order Extension (`sale.order`)
Enhanced sale order model with:
- Custom workflow control fields
- Lock/unlock functionality
- Due amount tracking
- Warning system integration

#### Commission Report (`report.enhanced_status.commission_payout_report_template_final`)
Abstract model for generating commission reports with:
- External commission calculations
- Internal commission tracking
- Legacy commission support
- Professional PDF output

### Views

#### Sale Order Form View
Enhanced form view with:
- Simplified workflow controls
- Essential field visibility
- Lock status indicators
- Financial tracking fields

#### Sale Order Stage Views
Complete CRUD views for workflow stage management:
- Form view for stage configuration
- Tree view for stage listing
- Search view with filters
- Menu integration

#### Commission Menu
Dedicated menu structure for commission reporting:
- Commission reports menu
- Sale order commission reports action
- Easy access to commission documents

### Security

#### Access Rights (`ir.model.access.csv`)
- `sale_order_stage_user`: Read access for users
- `sale_order_stage_manager`: Full access for managers

#### Record Rules (`security.xml`)
- Stage-based access controls
- Manager override permissions
- Field-level security

### Data

#### Initial Stages (`sale_order_stage.xml`)
Pre-configured workflow stages:
- Documentation (sequence 10)
- Calculation (sequence 20)
- Approved (sequence 30)
- Completed (sequence 40)

#### Cron Jobs (`ir_cron_data.xml`)
Automated tasks for:
- Workflow progression monitoring
- Financial status updates
- Notification triggers

### Assets

#### CSS Styling
- Enhanced form view styling
- Professional report formatting
- Responsive design elements
- Color-coded status indicators

#### JavaScript
- Interactive workflow controls
- Dynamic field visibility
- Real-time status updates
- Enhanced user experience

#### XML Templates
- Commission report templates
- Workflow stage indicators
- Status badges and icons

## Installation

### Prerequisites
- Odoo 17.0
- Python 3.8+
- Required Odoo modules: `sale`, `account`, `stock`, `purchase`

### Installation Steps

1. **Copy Module Files**
   ```bash
   cp -r enhanced_status /path/to/odoo/addons/
   ```

2. **Update App List**
   - Go to Apps menu in Odoo
   - Click "Update Apps List"
   - Search for "Enhanced Status"

3. **Install Module**
   - Click "Install" on the Enhanced Status module
   - Wait for installation to complete

4. **Configure Permissions**
   - Assign users to appropriate groups
   - Configure stage-based access if needed

5. **Setup Initial Data**
   - Review default workflow stages
   - Customize stages as needed
   - Configure commission settings

## Configuration

### Workflow Stages
Navigate to Sales > Configuration > Sale Order Stages to:
- Create custom stages
- Modify existing stages
- Set stage sequences and colors
- Configure fold status for kanban views

### Commission Settings
Access commission reports via:
- Sales > Reports > Commission Reports
- Generate reports from sale orders
- Customize report templates as needed

### Security Groups
Configure user access through:
- Settings > Users & Companies > Groups
- Assign users to sales manager groups for full access
- Regular users get read-only access to stages

## Usage

### Managing Sale Orders
1. Create sale orders with enhanced workflow
2. Progress through custom stages
3. Monitor financial status automatically
4. Generate commission reports as needed

### Commission Reporting
1. Open sale order
2. Go to Print > Commission Payout Report
3. Review comprehensive commission breakdown
4. Share professional PDF with stakeholders

### Administrative Controls
1. Lock/unlock orders as needed
2. Override workflow restrictions
3. Monitor due amounts and warnings
4. Track completion status

## Support

### Documentation
- Module README (this file)
- Inline code documentation
- Odoo standard documentation

### Issues and Troubleshooting
- Check Odoo logs for errors
- Verify user permissions
- Ensure all dependencies are installed
- Contact system administrator for access issues

### Customization
This module is designed for easy customization:
- Extend models as needed
- Modify views for specific requirements
- Add new commission calculation methods
- Integrate with other OSUS modules

## License

This module is licensed under LGPL-3. See LICENSE file for details.

## Author

**OSUSAPPS**  
Website: https://www.osusapps.com  
Version: 17.0.2.0.0

---

*For technical support and customization requests, please contact the OSUSAPPS development team.*
