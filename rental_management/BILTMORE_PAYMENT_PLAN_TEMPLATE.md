# Biltmore Sufouh Payment Plan - Default Template

## Overview
A new default payment plan template has been added to the system based on the Biltmore Sufouh property payment structure. This template will be available for all properties and can be applied with a single click.

---

## Payment Structure

### Total: 100% over 12 Installments

| # | Installment Description | % of Price | Payment Type |
|---|------------------------|------------|--------------|
| 1 | On Booking | 10.0% | Booking |
| 2 | Installment after 30 days from booking | 10.0% | Days After Booking (30 days) |
| 3 | Installment after 3 months from booking | 5.0% | Days After Booking (90 days) |
| 4 | Installment after 6 months from booking | 5.0% | Days After Booking (180 days) |
| 5 | On Handover | 10.0% | Handover |
| 6 | Installment after 6 months of Handover | 7.5% | Post Handover |
| 7 | Installment after 12 months of Handover | 7.5% | Post Handover |
| 8 | Installment after 18 months of Handover | 7.5% | Post Handover |
| 9 | Installment after 24 months of Handover | 7.5% | Post Handover |
| 10 | Installment after 30 months of Handover | 7.5% | Post Handover |
| 11 | Installment after 36 months of Handover | 7.5% | Post Handover |
| 12 | Installment after 42 months of Handover | 7.5% | Post Handover |
| 13 | Installment after 48 months of Handover | 7.5% | Post Handover |

**Pre-Handover Total:** 40%
**Post-Handover Total:** 60% (8 installments over 4 years, half-yearly)

---

## Template Details

**Template Name:** "Biltmore Sufouh Plan (Default)"
**Template ID:** `payment_plan_template_biltmore`
**Sequence:** 1 (appears first in the list)
**Status:** Active

---

## How to Use

### For New Properties:

1. **Go to:** Properties → Properties → Create
2. **Set:** Sale/Lease = "For Sale"
3. **Enable:** "Has Payment Plan" checkbox
4. **Select:** "Biltmore Sufouh Plan (Default)" from Payment Plan Template dropdown
5. **System will automatically:**
   - Load all 12 installment lines
   - Calculate amounts based on property price
   - Set correct payment types and dates
   - Validate that total equals 100%

### For Existing Properties:

1. **Open:** Property record
2. **Go to:** "Payment Plan" tab
3. **Check:** "Has Payment Plan"
4. **Select:** "Biltmore Sufouh Plan (Default)"
5. **Customize if needed:** Edit individual lines (descriptions, percentages, etc.)
6. **Save:** Property record

---

## Example Calculation

For a property priced at **AED 3,256,000** (like Biltmore Sufouh):

| Installment | % | Amount (AED) |
|-------------|---|--------------|
| On Booking | 10.0% | 325,600.00 |
| After 30 days | 10.0% | 325,600.00 |
| After 3 months | 5.0% | 162,800.00 |
| After 6 months | 5.0% | 162,800.00 |
| On Handover | 10.0% | 325,600.00 |
| After 6 months of Handover | 7.5% | 244,200.00 |
| After 12 months of Handover | 7.5% | 244,200.00 |
| After 18 months of Handover | 7.5% | 244,200.00 |
| After 24 months of Handover | 7.5% | 244,200.00 |
| After 30 months of Handover | 7.5% | 244,200.00 |
| After 36 months of Handover | 7.5% | 244,200.00 |
| After 42 months of Handover | 7.5% | 244,200.00 |
| After 48 months of Handover | 7.5% | 244,200.00 |
| **Total** | **100%** | **3,256,000.00** |

---

## Additional Fees (Automatic)

The system will automatically add:

1. **DLD Registration Fee:** 4% + AED 40
   - For AED 3,256,000: **AED 130,280**
   
2. **Oqood Registration Fee inc. VAT:** **AED 2,100**

**Total Registration Fees:** AED 132,380

---

## Report Generation

When you print the **Sales Offer Report**, it will show:

✅ All 12 installment lines in a professional table
✅ Percentages formatted to 1 decimal place
✅ Amounts formatted with commas and AED suffix
✅ Registration fees breakdown
✅ Booking amount section
✅ Bronze/gold Biltmore branding
✅ Validity notice ("This offer is valid for 1 day")

---

## Customization Options

You can modify any template line:
- **Description:** Change text (e.g., "After 3 months" → "Q1 Payment")
- **Percentage:** Adjust % (system validates total = 100%)
- **Payment Type:** Change type if needed
- **Days/Months:** Modify timing
- **Notes:** Add additional information

---

## Technical Details

**File Modified:** `data/payment_plan_template_data.xml`

**New Records Created:**
- 1 Payment Plan Template (`property.payment.plan`)
- 13 Payment Plan Lines (`property.payment.plan.line`)

**Database Tables:**
- `property_payment_plan` - Template header
- `property_payment_plan_line` - Template lines
- `property_custom_payment_plan_line` - Property-specific lines (copied from template)

---

## Deployment

To activate this template:

```bash
# Update the rental_management module
docker-compose exec odoo odoo --update=rental_management --stop-after-init
docker-compose restart odoo
```

Or use the update script:
```bash
cd rental_management
./update_sales_offer_report.sh   # Linux/Mac
update_sales_offer_report.bat    # Windows
```

---

## Verification

After deployment, verify:
1. ✅ Template appears in dropdown: Properties → Configuration → Payment Plans
2. ✅ Template is named "Biltmore Sufouh Plan (Default)"
3. ✅ Template has 13 lines totaling 100%
4. ✅ Template can be applied to properties
5. ✅ Sales Offer report displays all installments correctly

---

## Benefits

✅ **One-Click Application:** No manual entry of 12+ lines
✅ **Consistent Branding:** Matches Biltmore Sufouh standards
✅ **Error Prevention:** Pre-validated to total 100%
✅ **Time Saving:** Apply standard payment plan in seconds
✅ **Professional Reports:** Automatically formatted in sales offers
✅ **Easy Customization:** Use as template and adjust per property

---

## Support

For questions or issues:
1. Check that module is updated
2. Verify template appears in Configuration → Payment Plans
3. Ensure property is set to "For Sale"
4. Check that total percentage = 100%

---

**Created:** October 3, 2025
**Module:** rental_management
**Version:** 17.0.3.2.8
**Status:** ✅ Ready for Production
