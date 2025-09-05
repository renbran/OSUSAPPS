# SCHOLARIX Deal Report - User Guide

## 📋 Overview

The **SCHOLARIX Deal Report** is a comprehensive, professionally branded report that provides detailed analysis of real estate deals with complete commission breakdowns. This report is integrated into the Sales module and provides a beautiful, print-ready document for deal analysis and commission tracking.

## 🎯 Key Features

### 🏢 Professional SCHOLARIX Branding
- Custom SCHOLARIX header with branded colors (#722F37)
- Professional layout with property deal focus
- Print-ready PDF format with consistent styling
- Company logo and signature sections

### 💰 Complete Commission Analysis
- **External Commissions**: Broker, Referrer, Cashback, and Other External partners
- **Internal Team Commissions**: Agent 1, Agent 2, Manager, and Director
- **Legacy Commission Structure**: Consultant, Manager, Second Agent, and Director (legacy)
- **Financial Summary**: Total commissions and net company share

### 📊 Deal Information
- Property reference and deal dates
- Deal agent and status tracking
- Property details with units, prices, and taxes
- Deal value summary with tax calculations

## 🚀 How to Access the Report

### Method 1: From Sale Order Form
1. Navigate to **Sales → Orders → Sale Orders**
2. Open any sale order
3. Click the **Print** dropdown button
4. Select **"SCHOLARIX Deal Report"**
5. Report will generate as PDF

### Method 2: From List View
1. Go to **Sales → Orders → Sale Orders**
2. Select one or more sale orders (checkboxes)
3. Click **Print** button in the toolbar
4. Select **"SCHOLARIX Deal Report"**
5. Multiple reports will be generated

## 📄 Report Sections

### 1. Header Section
- **SCHOLARIX** branding with professional styling
- **Deal number** and status (Draft, Confirmed, Done)
- **Property reference** and key dates
- **Deal agent** information

### 2. Property Details Table
- Property descriptions with full specifications
- Units, pricing, and discount information
- Tax calculations and total values
- Section subtotals for multi-property deals

### 3. Commission Analysis (3 Categories)

#### 🌐 External Commissions
- **Broker commissions** with rates and amounts
- **Referrer bonuses** with calculation methods
- **Cashback payments** to clients
- **Other external partners** and their fees

#### 🏢 Internal Team Commissions
- **Agent 1 & Agent 2** primary sales agents
- **Manager commissions** for team leadership
- **Director override** commissions
- Rate types: Fixed, % Unit Price, % Total Value

#### 📋 Legacy Commission Structure
- **Consultant** (legacy field mapping)
- **Manager** (legacy system compatibility)
- **Second Agent** (historical deals)
- **Director** (legacy override structure)

### 4. Financial Summary
- **Total External Commissions**
- **Total Internal Commissions**
- **Total All Commissions**
- **🏢 SCHOLARIX Net Company Share** (highlighted)

### 5. Deal Status & Notes
- Current deal status with visual indicators
- Success celebration for closed deals (🎉)
- Completion confirmation for delivered deals (✅)

### 6. Signature & Terms
- Authorized signature section
- Payment terms and conditions
- Fiscal position remarks
- Official SCHOLARIX footer with timestamp

## 🎨 Visual Design Features

### Color Scheme
- **Primary Color**: #722F37 (Professional burgundy)
- **Headers**: White text on burgundy background
- **Borders**: Consistent burgundy borders throughout
- **Highlights**: Gold accents for important totals

### Typography
- **Headers**: Bold, professional fonts
- **Tables**: Clear, readable data presentation
- **Status**: Color-coded deal status indicators
- **Money Values**: Prominent financial display

### Layout
- **Responsive Design**: Works on all screen sizes
- **Print Optimization**: Perfect for physical printing
- **Mobile Friendly**: Accessible on tablets and phones
- **Professional Margins**: Clean, business-appropriate spacing

## 📈 Commission Calculation Display

### Rate Types Shown
- **Fixed Amount**: Shows "Fixed" instead of percentage
- **% Unit Price**: Percentage of individual unit prices
- **% Total Value**: Percentage of untaxed total deal value

### Amount Display
- All amounts shown in deal currency
- Formatted with proper currency symbols
- Bold highlighting for commission totals
- Color coding for different commission categories

## 🔍 When to Use This Report

### For Sales Teams
- Deal closure documentation
- Commission calculation verification
- Client presentation materials
- Internal deal analysis

### For Management
- Commission approval workflows
- Deal profitability analysis
- Team performance evaluation
- Financial planning and forecasting

### For Accounting
- Commission payment processing
- Deal revenue recognition
- Tax calculation verification
- Audit trail documentation

## 📋 Requirements

### System Requirements
- Odoo 17.0 or higher
- `custom_sales` module installed
- `commission_ax` module for commission data
- PDF generation capability

### Data Requirements
- Sale order with confirmed status
- Commission partners assigned
- Commission rates and types configured
- Property/product information complete

## 🛠️ Customization Options

The report template can be customized by modifying:
- `custom_sales/reports/scholarix_deal_report.xml`
- CSS styling for colors and layout
- Additional fields or sections
- Company branding elements

## 🎯 Best Practices

### For Optimal Results
1. **Complete Commission Setup**: Ensure all commission partners and rates are configured
2. **Accurate Property Data**: Fill in complete product/property descriptions
3. **Proper Deal Status**: Confirm deals before generating reports
4. **Regular Updates**: Keep commission structures current

### Report Generation Tips
1. **Single Deal Reports**: Generate individually for detailed analysis
2. **Batch Processing**: Use list view selection for multiple deals
3. **Print Settings**: Use landscape orientation for best layout
4. **Digital Distribution**: PDF format perfect for email sharing

## 📞 Support

For questions about the SCHOLARIX Deal Report:
- Check sale order commission data completeness
- Verify module installation and updates
- Review commission partner configurations
- Contact system administrator for customizations

---

**© SCHOLARIX - Professional Real Estate Commission Management System**

*This report is part of the Custom Sales Dashboard Pro module for Odoo 17*
