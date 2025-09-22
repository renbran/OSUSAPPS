# Quantity Percentage Display Module

## Overview

This module enhances Odoo 17 sales orders and invoices with intelligent percentage quantity handling. When users input "5", the system automatically converts it to 0.05 (representing 5%) and defaults to percentage Unit of Measure.

## Key Features

### Smart Percentage Input Conversion
- **Input "5"** → System stores **0.05** and displays **"5%"**
- **Input "0.5"** → System stores **0.005** and displays **"0.5%"**
- **Input "10"** → System stores **0.10** and displays **"10%"**

### Automatic UoM Management
- **Default UoM**: Automatically sets Unit of Measure to % for new lines
- **Flexible**: Users can still change UoM if needed for specific cases
- **Consistent**: Percentage UoM is created if it doesn't exist

### High Precision Display
- **Uniform Percentage Display**: Converts quantity values to percentage format across all modules
- **High Precision**: Maintains up to 6 decimal places for exact calculations
- **No Rounding**: Preserves exact decimal values without rounding
- **Clean UI**: Uses Odoo's built-in percentage widget for consistent display

## Supported Modules

### Sales
- **Sales Orders**: Order line quantities with smart percentage input
- **Quotations**: Quote line quantities with percentage conversion  
- **Sales Order Lines**: Tree and form views with percentage display

### Accounting
- **Customer Invoices**: Invoice line quantities with percentage logic
- **Supplier Bills**: Bill line quantities with percentage conversion
- **Account Move Lines**: All accounting entries with percentage display

## Usage Examples

### Example 1: Commission Percentage
```
User Input: 5
System Storage: 0.05
Display: 5%
Calculation: If sale amount is $1000, commission = $1000 × 0.05 = $50
```

### Example 2: Tax Rate
```
User Input: 7.5
System Storage: 0.075
Display: 7.5%
Calculation: If taxable amount is $200, tax = $200 × 0.075 = $15
```

### Example 3: Discount Rate
```
User Input: 15
System Storage: 0.15
Display: 15%
Calculation: If product price is $100, discount = $100 × 0.15 = $15
```

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