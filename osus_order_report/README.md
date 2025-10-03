# OSUS Professional Order Report

## Overview
This module provides a professional, modern sales order report for Odoo 17 with a clean design, clear layout, and company branding.

## Features

### 🎨 Modern Design
- Clean, professional layout
- Gradient header with brand colors
- Responsive design for all screen sizes
- Print-optimized formatting

### 📋 Comprehensive Information
- **Header Section**
  - Document type (Quotation/Sales Order)
  - Order number and status badge
  - Order date and validity date
  
- **Customer & Delivery Information**
  - Customer details with full address
  - Separate delivery address section
  - Contact information (phone, email)
  - Tax ID display

- **Order Details Table**
  - Line numbers for easy reference
  - Product name and internal reference
  - Quantity and unit of measure
  - Unit price and taxes
  - Subtotal per line
  - Product codes displayed

- **Additional Information**
  - Salesperson name
  - Customer reference
  - Payment terms
  - Order notes

- **Financial Summary**
  - Subtotal amount
  - Tax breakdown by group
  - Total amount with currency
  
- **Legal & Compliance**
  - Terms and conditions section
  - Signature section (Customer + Authorized)
  - Computer-generated disclaimer

## Installation

1. Copy the `osus_order_report` folder to your Odoo addons directory
2. Restart Odoo service
3. Update Apps List
4. Search for "OSUS Professional Order Report"
5. Click Install

## Usage

### Print Reports

1. Navigate to **Sales → Orders**
2. Open any sales order
3. Click **Print → Professional Sales Order**
4. The PDF will be generated with filename: `Order - SO00XXX.pdf`

### Customization

#### Colors
Edit the CSS file to change brand colors:
```css
/* File: static/src/css/order_report_style.css */

.osus-doc-title {
    color: #1a5490;  /* Change main title color */
}

.osus-table-header {
    background: linear-gradient(135deg, #1a5490 0%, #2874a6 100%);  /* Change table header gradient */
}
```

#### Layout
Edit the QWeb template:
```xml
<!-- File: views/report_sale_order_template.xml -->
```

#### Paper Format
Change paper format in report definition:
```xml
<!-- File: report/sale_order_report.xml -->
<field name="paperformat_id" ref="base.paperformat_euro"/>  <!-- or base.paperformat_us -->
```

## Design Elements

### Color Palette
- **Primary Blue**: `#1a5490` - Headers, titles
- **Secondary Blue**: `#3498db` - Accents, dividers
- **Dark Text**: `#2c3e50` - Main content
- **Light Gray**: `#f8f9fa` - Background boxes
- **Muted Text**: `#7f8c8d` - Secondary information

### Typography
- **Font Family**: Segoe UI, Tahoma, Geneva, Verdana, sans-serif
- **Headers**: Bold (700 weight)
- **Body**: Regular (400 weight)
- **Line Height**: 1.6 for readability

### Layout Structure
```
┌─────────────────────────────────────────┐
│ Header: Title, Number, Status, Date    │
├─────────────────────────────────────────┤
│ Customer Info    │ Delivery Address    │
├─────────────────────────────────────────┤
│ Order Lines Table (Products)           │
├─────────────────────────────────────────┤
│ Notes           │ Totals              │
├─────────────────────────────────────────┤
│ Terms & Conditions                      │
├─────────────────────────────────────────┤
│ Signatures (Customer | Authorized)      │
└─────────────────────────────────────────┘
```

## Technical Details

### Module Structure
```
osus_order_report/
├── __init__.py
├── __manifest__.py
├── README.md
├── report/
│   └── sale_order_report.xml          # Report definition
├── views/
│   └── report_sale_order_template.xml # QWeb template
└── static/
    └── src/
        └── css/
            └── order_report_style.css  # Styling
```

### Dependencies
- `sale` - Sales Management
- `web` - Web Framework

### Compatibility
- Odoo Version: 17.0
- License: LGPL-3

## Support & Customization

For custom modifications or support:
- Check the inline comments in template files
- Refer to Odoo QWeb documentation
- Test changes in a development environment first

## Screenshots

### Document Header
- Shows order type (Quotation/Sales Order)
- Status badge with color coding
- Order reference and dates

### Customer Section
- Complete address information
- Contact details
- Delivery address (if different)

### Order Lines
- Professional table layout
- Clear product information
- Price and tax breakdown

### Totals
- Subtotal calculation
- Tax breakdown by group
- Bold total amount

### Signatures
- Space for customer signature
- Space for authorized signature
- Date fields

## Best Practices

1. **Before Printing**
   - Verify all order information is correct
   - Check customer address details
   - Confirm pricing and taxes

2. **Customization**
   - Always backup files before editing
   - Test in development environment
   - Use CSS variables for easy color changes

3. **Performance**
   - Report generates quickly for orders with up to 100 lines
   - For large orders, consider pagination

## Troubleshooting

### Report Not Showing
- Clear browser cache
- Restart Odoo service
- Update the module

### Styling Not Applied
- Check asset bundle is loaded
- Clear Odoo assets cache
- Verify CSS file path in manifest

### Missing Information
- Check field permissions
- Verify data exists on order
- Check QWeb template field names

## Changelog

### Version 17.0.1.0.0
- Initial release
- Professional layout design
- Comprehensive order information
- Mobile responsive
- Print optimized
- Signature section
- Terms and conditions support

## License
LGPL-3 - See LICENSE file for details

## Credits
Developed by OSUSAPPS Team
