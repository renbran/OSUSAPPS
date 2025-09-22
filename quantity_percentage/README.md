# Quantity Percentage Display Module

## Overview

This module modifies quantity fields across Odoo 17 sales orders and invoices to display as percentages with precise decimal handling, preventing rounding and providing a uniform interface throughout the system.

## Features

- **Uniform Percentage Display**: Converts quantity values to percentage format across all modules
- **Sales Integration**: Works with Sales Orders, Quotations, and Order Lines
- **Accounting Integration**: Works with Customer Invoices, Supplier Bills, and Move Lines
- **High Precision**: Maintains up to 6 decimal places for exact calculations
- **No Rounding**: Preserves exact decimal values without rounding
- **Clean UI**: Uses Odoo's built-in percentage widget for consistent display
- **Complete Integration**: Seamless workflow from quotation to invoice

## Supported Modules

### Sales
- **Sales Orders**: Order line quantities display as percentages
- **Quotations**: Quote line quantities display as percentages  
- **Sales Order Lines**: Tree and form views with percentage display

### Accounting
- **Customer Invoices**: Invoice line quantities display as percentages
- **Supplier Bills**: Bill line quantities display as percentages
- **Account Move Lines**: All accounting entries with percentage display

## Technical Implementation

### Model Extension
- Extends `account.move.line` model
- Adds `quantity_percentage` computed field
- Uses inverse function to maintain data integrity
- Configurable decimal precision (default: 6 places)

### View Modifications
- Replaces quantity field in invoice forms
- Updates tree views for consistency
- Includes search functionality
- Applies to both customer invoices and supplier bills

### Security
- Proper access rights for different user groups
- Respects existing accounting permissions
- Read/write access based on user roles

## Installation

1. **Copy the module** to your Odoo addons directory:
   ```bash
   cp -r quantity_percentage /var/odoo/your_instance/addons/
   ```

2. **Update the apps list** in Odoo:
   - Go to Apps menu
   - Click "Update Apps List"

3. **Install the module**:
   - Search for "Quantity Percentage Display"
   - Click Install

4. **Alternative installation via command line**:
   ```bash
   docker-compose run --rm odoo odoo -d your_db -i quantity_percentage --stop-after-init
   ```

## Usage

After installation, all quantity fields in invoice lines will automatically display as percentages:

- **Input**: Enter values as decimals (e.g., 0.036)
- **Display**: Shows as percentage (3.6%)
- **Storage**: Maintains exact decimal precision
- **Calculations**: All tax and total calculations remain accurate

## Example
- Original value: 0.036000
- Display: 3.6%
- No rounding applied
- Full precision maintained in calculations

## Compatibility
- **Odoo Version**: 17.0
- **Dependencies**: account (base accounting module)
- **License**: LGPL-3

## Support
For issues or customizations, contact the OSUSAPPS development team.

## Technical Notes
- Uses computed fields with inverse functions
- Leverages Odoo's percentage widget
- Maintains backward compatibility
- Preserves all existing accounting functionality