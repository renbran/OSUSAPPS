# OSUS Global Report Template

## 🎯 Overview
**Universal report template that overrides ALL Odoo reports** with a consistent, professional design. One installation applies your branding to every document in your system.

## ✨ What This Module Does

This module **globally overrides** the external layout template used by ALL Odoo reports, providing:

### 🎨 Professional Design Applied To:
- ✅ **Invoices & Bills** (Customer & Vendor)
- ✅ **Sales Orders & Quotations**
- ✅ **Purchase Orders & RFQs**
- ✅ **Delivery Orders & Receipts**
- ✅ **Manufacturing Orders**
- ✅ **Payment Receipts & Vouchers**
- ✅ **Inventory Reports**
- ✅ **Packing Slips**
- ✅ **Credit Notes**
- ✅ **And ALL other Odoo reports!**

### 🏢 Global Features:
1. **Professional Header**
   - Company logo (automatically styled)
   - Company information
   - Contact details
   - Tax ID
   - Blue gradient background

2. **Consistent Styling**
   - Modern typography
   - Professional color scheme (Deep Ocean Blue)
   - Styled tables with hover effects
   - Clean information boxes
   - Status badges

3. **Professional Footer**
   - Company contact information
   - Page numbers
   - Website and email
   - Disclaimer text

4. **Print Optimized**
   - Colors preserved in print
   - Proper page breaks
   - Clean, professional output

## 🚀 Installation

### Step 1: Install the Module
```bash
# 1. Restart Odoo
cd "d:/GitHub/osus_main/cleanup osus/OSUSAPPS"
docker-compose restart odoo

# 2. In Odoo Web Interface:
# - Go to Apps
# - Update Apps List
# - Search: "OSUS Global Report Template"
# - Click Install
```

### Step 2: Verify Installation
1. Open any sales order
2. Click Print → Quotation/Order
3. You should see the new professional design

### Step 3: Update Company Information
Go to **Settings → Companies → Your Company** and ensure:
- Company logo is uploaded
- Address is complete
- Phone and email are filled
- Website is set
- Tax ID is entered

## 📐 Design System

### Color Palette
```scss
Primary Blue:   #1a5490  // Headers, titles, borders
Secondary Blue: #3498db  // Accents, highlights
Accent Blue:    #2874a6  // Gradients
Dark Text:      #2c3e50  // Main content
Light Gray:     #f8f9fa  // Backgrounds
Success Green:  #27ae60  // Positive status
Warning Orange: #f39c12  // Warnings, notes
Danger Red:     #e74c3c  // Errors, overdue
```

### Typography
- **Font Family**: Segoe UI, Tahoma, Geneva, Verdana, sans-serif
- **Header Sizes**: 
  - H1: 32px (Document titles)
  - H2: 24px (Section titles)
  - H3: 18px (Subsections)
  - H4: 16px (Minor sections)
- **Body Text**: 13px
- **Footer**: 11px

### Layout Structure
```
┌─────────────────────────────────────────────┐
│  HEADER (Blue Gradient)                    │
│  Logo    │  Company Info                   │
│          │  Address, Phone, Email          │
│  ─────────────────────────────────────────  │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│  DOCUMENT BODY                              │
│  (Your specific report content)             │
│                                             │
│  Tables, addresses, totals, etc.           │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│  ─────────────────────────────────────────  │
│  FOOTER                                     │
│  Company Info  │  Page X of Y               │
│                │  Disclaimer                │
└─────────────────────────────────────────────┘
```

## 🎨 Customization Guide

### Change Brand Colors

Edit: `static/src/scss/global_report_style.scss`

```scss
// Line 13-24: Change these variables
$primary-color: #1a5490;        // Your main brand color
$secondary-color: #3498db;      // Your accent color
$accent-color: #2874a6;         // Your gradient color
```

After changing colors:
```bash
# Clear Odoo assets cache
# In Odoo: Settings → Technical → Regenerate Assets Bundles
# Or restart Odoo with assets cache clear
```

### Modify Header Layout

Edit: `views/external_layout_template.xml`

Example - Remove company logo:
```xml
<!-- Comment out or remove lines 12-16 -->
<!--
<div class="col-4 osus-logo-section">
    <img t-if="company.logo" ... />
</div>
-->
```

Example - Add company slogan:
```xml
<!-- Add after line 28 (company name) -->
<div class="osus-company-slogan">
    <em>Your trusted partner since 2020</em>
</div>
```

### Modify Footer Content

Edit: `views/external_layout_template.xml` (lines 75-110)

Example - Add social media:
```xml
<!-- Add before page numbers -->
<div class="osus-social-media">
    <i class="fa fa-facebook"/> /yourcompany
    <i class="fa fa-linkedin"/> /company/yourcompany
</div>
```

### Change Table Styles

Edit: `static/src/scss/global_report_style.scss` (lines 184-241)

Example - Change header background:
```scss
.article table thead {
    background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); // Red gradient
    color: white;
}
```

Example - Remove hover effect:
```scss
.article table tbody tr:hover {
    background-color: transparent; // No hover
}
```

## 📋 Module Structure

```
osus_global_report_template/
├── __init__.py
├── __manifest__.py
├── README.md
├── views/
│   ├── external_layout_template.xml    # Main layout override
│   └── report_assets.xml               # Asset registration
└── static/
    └── src/
        └── scss/
            └── global_report_style.scss # Master stylesheet
```

## 🔧 Technical Details

### How It Works

1. **Template Inheritance**: Overrides `web.external_layout` with priority 99
2. **Asset Injection**: Injects SCSS into `web.report_assets_common`
3. **Global Application**: ALL reports use external_layout, so changes apply everywhere
4. **Layout Variants**: Overrides all layout types (standard, clean, boxed, bold, striped)

### Template Priority

```xml
priority="99"  <!-- High priority ensures our template wins -->
```

### Dependencies

```python
'depends': ['web', 'base']  # Minimal dependencies
```

### Asset Bundle

```python
'web.report_assets_common': [
    'osus_global_report_template/static/src/scss/global_report_style.scss',
]
```

## 🎯 Best Practices

### 1. Company Setup
Always fill in company information completely:
- **Logo**: High-quality, transparent background PNG
- **Address**: Complete street, city, state, zip, country
- **Contact**: Phone, email, website
- **Tax ID**: For legal compliance

### 2. Testing
Test the template with:
- Sales order (quotation and confirmed)
- Invoice (draft and posted)
- Purchase order
- Delivery order
- Payment receipt

### 3. Customization
- Make small changes incrementally
- Test after each change
- Keep backups of modified files
- Clear cache after CSS changes

### 4. Print Settings
Ensure proper print settings:
- **Paper Format**: A4 or US Letter
- **Margins**: 10mm all sides (default)
- **DPI**: 90 for reports (Odoo default)

## 🐛 Troubleshooting

### Issue: Changes Not Appearing

**Solution:**
```bash
# Method 1: Clear assets cache
# Settings → Technical → Regenerate Assets Bundles

# Method 2: Restart with cache clear
docker-compose restart odoo

# Method 3: Update module
# Apps → OSUS Global Report Template → Upgrade
```

### Issue: Logo Not Showing

**Solution:**
1. Check company logo is uploaded: Settings → Companies
2. Verify file size < 1MB
3. Use PNG format with transparent background
4. Clear browser cache

### Issue: Colors Not Printing

**Solution:**
Browser print settings:
- Enable "Background graphics"
- Enable "Print colors"
- Use "Save as PDF" instead of direct print

### Issue: Layout Broken

**Solution:**
1. Check for XML syntax errors
2. Verify all divs are properly closed
3. Review browser console for errors
4. Restore from backup if needed

## 📊 Affected Reports List

This template applies to:

### Sales
- Quotations
- Sales Orders
- Delivery Orders
- Invoices
- Credit Notes
- Pro Forma Invoices

### Purchases
- RFQs (Request for Quotations)
- Purchase Orders
- Receipts
- Vendor Bills

### Inventory
- Packing Operations
- Stock Moves
- Internal Transfers
- Product Labels

### Accounting
- Invoices
- Bills
- Payment Receipts
- Credit Notes
- Bank Statements

### HR & Payroll
- Employee Contracts
- Payslips
- Expense Reports

### Manufacturing
- Manufacturing Orders
- Work Orders
- Bill of Materials

### Custom Modules
- Any custom report using external_layout

## 🔒 Compatibility

- **Odoo Version**: 17.0
- **License**: LGPL-3
- **Dependencies**: web, base (standard Odoo modules)
- **Conflicts**: May override other report template modules (last installed wins)

## 📚 Additional Resources

### Odoo QWeb Documentation
- [Official QWeb Guide](https://www.odoo.com/documentation/17.0/developer/reference/frontend/qweb.html)
- [Report Development](https://www.odoo.com/documentation/17.0/developer/reference/backend/reports.html)

### CSS Resources
- [SCSS Documentation](https://sass-lang.com/documentation)
- [Flexbox Guide](https://css-tricks.com/snippets/css/a-guide-to-flexbox/)
- [Print CSS Guide](https://www.smashingmagazine.com/2015/01/designing-for-print-with-css/)

## 💡 Pro Tips

1. **Logo Best Practices**:
   - Use SVG for scalability
   - Or PNG with 300 DPI
   - Transparent background
   - Max size: 800px × 200px

2. **Color Selection**:
   - Use your brand colors
   - Ensure sufficient contrast (4.5:1 ratio)
   - Test in color and grayscale

3. **Typography**:
   - Stick to web-safe fonts
   - Or include custom fonts in assets
   - Maintain readable font sizes (min 11px)

4. **Testing**:
   - Test with real data
   - Print preview before actual printing
   - Test on different browsers
   - Verify PDF output quality

## 📝 Changelog

### Version 17.0.1.0.0
- Initial release
- Global external_layout override
- Professional header and footer
- Comprehensive SCSS styling
- All layout variants covered
- Print optimization
- Responsive design
- Complete documentation

## 🤝 Support

For issues or customization help:
1. Check this README first
2. Review inline code comments
3. Test in development environment
4. Check Odoo logs for errors

## 📄 License

LGPL-3 - See LICENSE file for full details

---

**Developed by OSUSAPPS Team**  
*Professional Odoo Solutions*

🌐 Website: https://www.osusapps.com  
📧 Email: support@osusapps.com  
📞 Phone: +1 (XXX) XXX-XXXX

---

## 🎉 Quick Start Summary

1. **Install** the module from Apps
2. **Upload** your company logo
3. **Fill** company information
4. **Print** any report
5. **Enjoy** professional documents!

That's it! All your reports now have a consistent, professional design. 🚀
