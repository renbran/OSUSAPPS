# Commission Partner Statement Module

This module extends the partner management system to provide comprehensive commission statement reporting capabilities based on sale order commissions.

## Features

- **Commission Statement Generation**: Generate detailed PDF and Excel reports
- **Partner Integration**: Seamlessly integrates with existing partner records
- **Commission Extraction**: Extracts commission data from all commission types (External, Internal, Legacy)
- **Automated Reporting**: Monthly automated statement generation
- **Professional Templates**: Professional report layouts with detailed breakdowns

## Installation

1. Copy the module to your Odoo addons directory
2. Restart Odoo server
3. Update the app list in Odoo
4. Install the module from Apps menu

## Dependencies

- base
- sale
- contacts
- commission_ax
- enhanced_status

## Usage

1. Navigate to Contacts
2. Open a partner record
3. Check the "Commission Statement" tab
4. Use the action buttons to generate reports

## Configuration

- Set user permissions in Settings → Users & Companies → Groups
- Configure automatic statement generation in partner records
- Customize email templates if needed

## Technical Details

- Extends `res.partner` model with commission statement capabilities
- Provides PDF and Excel export functionality
- Includes automated cron job for monthly statements
- Professional email templates for sharing statements
