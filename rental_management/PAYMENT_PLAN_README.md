# Payment Plan Feature - User Guide

## Overview
The Payment Plan feature has been successfully added to the Odoo 17 Rental Management module. This feature allows you to define flexible payment schedules for property sales with support for DLD fees, admin fees, and various payment milestones.

## Features Added

### 1. **Payment Plan Templates**
Create reusable payment plan templates that can be applied to multiple properties.

**Location:** Properties → Configurations → Payment Plans

**Key Features:**
- Define percentage-based payment terms
- Support for different payment types (Booking, Construction, Handover, Post-Handover, etc.)
- Installment support with flexible frequencies (Monthly, Quarterly, Half-Yearly, Yearly)
- Validation to ensure total percentage equals 100%

### 2. **Property Payment Plan Integration**
Each property can now have a custom payment plan with additional fees.

**Location:** Property Form → Payment Plan Tab (visible only for Sale properties)

**Fields Added:**
- **Has Payment Plan:** Enable/disable payment plan for the property
- **Payment Plan Template:** Select from pre-defined templates
- **DLD Fee (%):** Dubai Land Department fee (default: 4%)
- **Admin Fee:** Administrative fee (default: 2100)
- **Custom Payment Plan Lines:** Customize the payment schedule
- **Total with Fees:** Automatically calculated total including all fees

### 3. **Payment Plan Types**
- **Booking:** Initial booking payment
- **Days After Booking:** Payment due after specified days
- **Construction Milestone:** Payment linked to construction progress
- **Handover:** Payment on property handover
- **Post Handover:** Payments after handover (supports installments)
- **Other:** Custom payment types

### 4. **Reports**

#### Payment Plan Report
Automatically included in property reports when a payment plan is defined.

**Features:**
- Price summary with DLD and admin fees
- Detailed payment schedule with installment information
- Terms and conditions
- Professional formatting

#### Enhanced Sales Offer Report (2-Page Brochure)
A beautifully formatted 2-page report for property marketing.

**Page 1:**
- Property image with overlay
- Key features prominently displayed at the top
- Amenities grid with icons
- Specifications
- Nearby landmarks
- Gallery images
- Location and contact information

**Page 2:**
- Floor plans (up to 2)
- Unit information table
- Payment plan breakdown (for sale properties)
- Professional footer

**Access:** Properties → Select Property → Print → Sales Offer

## Sample Payment Plans Included

### 1. **60% Post Handover - 4 Years (Standard)**
- 10% Booking
- 10% After 30 days
- 15% On construction
- 5% On handover
- 60% Post handover (8 installments over 4 years, half-yearly)

### 2. **Quick Payment - 20% Down**
- 20% Down payment at booking
- 80% Balance on handover

### 3. **Flexible 30-70 Split**
- 10% Booking
- 20% Construction phase
- 70% Post handover (4 installments over 2 years, half-yearly)

## Usage Instructions

### Creating a Payment Plan Template

1. Go to **Properties → Configurations → Payment Plans**
2. Click **Create**
3. Fill in:
   - **Plan Name:** e.g., "60% Post Handover - 4 Years"
   - **Description:** Optional description
4. Add **Payment Terms** lines:
   - **Description:** Payment description
   - **Payment Type:** Select type
   - **Percentage:** Payment percentage (must total 100%)
   - **Days After:** For "Days After Booking" type
   - **Installments:** Number of installments (for post-handover)
   - **Frequency:** Installment frequency
5. Click **Save**

### Applying Payment Plan to Property

1. Open a property (must be "For Sale")
2. Go to **Payment Plan** tab
3. Check **Has Payment Plan**
4. Select a **Payment Plan Template** (optional)
5. Adjust **DLD Fee %** and **Admin Fee** if needed
6. Customize **Custom Payment Plan** lines if required
7. Verify **Total Percentage** = 100%
8. **Save**

### Viewing Payment Calculations

The system automatically calculates:
- Individual payment amounts based on percentages
- DLD fee amount (percentage of sale price)
- Total amount including all fees
- Real-time validation of payment plan totals

### Generating Reports

#### Payment Plan Report
1. Open property with payment plan
2. Click **Print**
3. Select **Property Brochure** or any property report
4. Payment plan section automatically included

#### Sales Offer Report
1. Open property
2. Click **Print**
3. Select **Sales Offer**
4. Professional 2-page brochure generated

## Technical Details

### Models Created

1. **property.payment.plan**
   - Payment plan templates
   - Reusable across multiple properties

2. **property.payment.plan.line**
   - Template payment terms
   - Defines payment structure

3. **property.custom.payment.plan.line**
   - Property-specific payment lines
   - Allows customization per property
   - Auto-calculates amounts

### Fields Added to Property Model

- `is_payment_plan` - Boolean flag
- `payment_plan_id` - Link to template
- `custom_payment_plan_line_ids` - Custom payment lines
- `dld_fee_percentage` - DLD fee percentage
- `dld_fee_amount` - Calculated DLD amount
- `admin_fee` - Admin fee amount
- `total_with_fees` - Total including all fees
- `payment_plan_total` - Sum of payment percentages

### Files Created/Modified

**New Files:**
- `models/property_payment_plan.py`
- `views/property_payment_plan_view.xml`
- `views/property_payment_plan_inherit_view.xml`
- `report/property_payment_plan_report.xml`
- `report/property_brochure_enhanced_report.xml`
- `data/payment_plan_template_data.xml`

**Modified Files:**
- `models/__init__.py`
- `__manifest__.py`
- `security/ir.model.access.csv`
- `views/menus.xml`

## Example: Creating Your Payment Plan

Based on your requirement (10% booking, 10% after 30 days, 15% construction, 5% handover, 60% post handover - 4 years, 6 months):

```xml
Name: "Standard Payment Plan"

Lines:
1. Booking Payment - 10% - Booking - 1 installment
2. After 30 Days - 10% - Days After Booking (30 days) - 1 installment
3. Construction Phase - 15% - Construction - 1 installment
4. Handover Payment - 5% - Handover - 1 installment
5. Post Handover - 60% - Post Handover - 8 installments - Half-Yearly
```

## Validation Rules

1. Total payment plan percentage must equal 100%
2. Individual percentages must be between 0 and 100
3. Payment plans only available for "For Sale" properties
4. System warns if payment plan total ≠ 100%

## Tips

1. **Create Templates First:** Set up common payment plans as templates for quick reuse
2. **Customize Per Property:** Use templates as starting points, then customize as needed
3. **Verify Totals:** Always check that payment plan total shows 100% before saving
4. **Use Installments:** For post-handover payments, use installment features for automatic calculation
5. **Print Sales Offers:** Use the enhanced report for professional property presentations

## Support

For issues or questions:
1. Check that all files are properly loaded in the module
2. Verify security access rights
3. Ensure property is set to "For Sale" to see payment plan tab
4. Check that payment plan total equals 100%

## Future Enhancements

Potential future additions:
- Payment schedule generation with due dates
- Integration with invoicing
- Payment reminders
- Multiple payment plan versions per property
- Payment plan comparison reports

---

**Version:** 1.0
**Module:** rental_management
**Odoo Version:** 17.0
**Date:** 2025
