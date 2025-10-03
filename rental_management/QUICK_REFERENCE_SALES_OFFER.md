# Sales Offer Report - Quick Reference

## 🎯 What Changed?

### Visual Design
- **Color Scheme:** Maroon → Bronze/Gold (Biltmore Sufouh style)
- **Layout:** 2 columns → 3 columns (Page 1)
- **Header Image:** 320px → 220px height
- **New Banner:** Validity notice at top

### Content Updates
- **"Landlord" → "Developer"** (all instances)
- **Added Bank Details** section
- **Added Registration Fees** breakdown
- **Added Booking Amount** section
- **Enhanced Payment Plan** table

---

## 📋 Report Structure

### Page 1: Property Overview
```
┌─────────────────────────────────────────┐
│    ⏰ Valid for 1 day (Validity Banner) │
├─────────────────────────────────────────┤
│       Property Image with Overlay       │
├──────────┬──────────┬───────────────────┤
│ LEFT 38% │ MID 30%  │ RIGHT 30%         │
│          │          │                   │
│ Property │ Amenities│ Gallery           │
│ Details  │          │                   │
│          │ Specs    │                   │
│ Location │          │                   │
│          │ Nearby   │                   │
│ Contact  │          │                   │
│Developer │          │                   │
│          │          │                   │
│ Bank     │          │                   │
│ Details  │          │                   │
└──────────┴──────────┴───────────────────┘
```

### Page 2: Payment Details
```
┌─────────────────────────────────────────┐
│    ⏰ Valid for 1 day (Validity Banner) │
├─────────────────────────────────────────┤
│           Property Name - Details        │
├──────────────────┬──────────────────────┤
│ LEFT 48%         │ RIGHT 48%            │
│                  │                      │
│ Floor Plans      │ Plan of Installments │
│                  │                      │
│ (1 plan shown)   │ (Full breakdown)     │
│                  │                      │
│ Disclaimer       │ Registration Fees    │
│                  │                      │
│                  │ Booking Amount       │
└──────────────────┴──────────────────────┘
```

---

## 🎨 Color Codes

| Element | Color | Hex Code |
|---------|-------|----------|
| Primary | Bronze | #C5A572 |
| Secondary | Dark Bronze | #8B7355 |
| Text | Dark Gray | #333 |
| Background | Light Gray | #f9f9f9 |
| Accent | Light Beige | #fff8f0 |

---

## 📊 Payment Plan Format

The payment plan table displays:

| Column | Content | Format |
|--------|---------|--------|
| **Installment** | Description (e.g., "On Booking") | Left-aligned, 7pt |
| **% of Price** | Percentage | Centered, bold, 1 decimal |
| **Amount AED** | Amount in AED | Right-aligned, 2 decimals, comma-separated |

Example row:
```
On Booking            10.0 %       325,600.00 AED
```

---

## 💰 Registration Fees

Two items displayed:
1. **4% DLD Fees + AED 40** → Calculated from property price
2. **Oqood Registration Fee inc. VAT** → Fixed at AED 2,100.00

---

## 📝 Key Fields

### Developer Information (formerly Landlord)
- **Field Name:** `landlord_id`
- **Display Label:** "Developer"
- **Related Fields:** `landlord_phone`, `landlord_email`

### Payment Plan Fields
- **Model:** `custom_payment_plan_line_ids`
- **Fields Used:**
  - `name` → Installment description
  - `percentage` → Percentage of total price
  - `amount` → Amount in AED

### Registration Fees
- **DLD Fee:** `dld_fee_amount` (4% + 40 AED)
- **Oqood Fee:** Fixed value (2,100 AED)

---

## 🔄 How to Update Module

### Windows:
```batch
cd "d:\RUNNING APPS\ready production\latest\OSUSAPPS\rental_management"
update_sales_offer_report.bat
```

### Linux/Mac:
```bash
cd "/path/to/OSUSAPPS/rental_management"
./update_sales_offer_report.sh
```

### Manual Update:
```bash
docker-compose exec odoo odoo --update=rental_management --stop-after-init
docker-compose restart odoo
```

---

## 🧪 Testing Checklist

- [ ] Property with payment plan displays correctly
- [ ] All installments shown with correct percentages
- [ ] Registration fees section appears
- [ ] Booking amount shows first installment
- [ ] Developer label (not Landlord) is displayed
- [ ] Bank details appear on Page 1
- [ ] Floor plans display on Page 2
- [ ] Colors match Biltmore Sufouh branding
- [ ] PDF prints correctly
- [ ] Three-column layout renders properly

---

## 📁 Files Modified

| File | Status | Location |
|------|--------|----------|
| `property_brochure_enhanced_report.xml` | ✅ Updated | `report/` |
| `property_brochure_enhanced_report.xml.backup` | 📦 Backup | `report/` |
| `SALES_OFFER_ENHANCEMENT_SUMMARY.md` | 📄 New | Root |
| `update_sales_offer_report.bat` | 🔧 New | Root |
| `update_sales_offer_report.sh` | 🔧 New | Root |
| `QUICK_REFERENCE_SALES_OFFER.md` | 📋 This file | Root |

---

## 🐛 Troubleshooting

### Report doesn't update?
1. Clear browser cache (Ctrl+Shift+R)
2. Restart Odoo: `docker-compose restart odoo`
3. Update module again
4. Check Odoo logs: `docker-compose logs -f odoo`

### Colors look wrong?
- Check if browser is in dark mode
- Verify PDF render (not just preview)
- Print to PDF to see final output

### Payment plan not showing?
- Verify property has `sale_lease = 'for_sale'`
- Check `is_payment_plan = True`
- Ensure `custom_payment_plan_line_ids` has records

### Developer label still shows Landlord?
- Clear Odoo assets cache
- Hard refresh browser
- Verify template file was updated

---

## 📞 Support

For issues or questions:
1. Check `SALES_OFFER_ENHANCEMENT_SUMMARY.md`
2. Review Odoo logs: `docker-compose logs -f odoo`
3. Verify XML syntax is correct
4. Test with different property records

---

## 🎓 Reference Data (from Biltmore Sufouh Example)

### Sample Property:
- **Name:** Biltmore Sufouh
- **Floor:** 26
- **Unit:** 2612
- **Size:** 1,097.27 sqft
- **Price:** 3,256,000 AED
- **Registration:** 130,280 AED

### Sample Payment Plan:
| Installment | % | Amount (AED) |
|-------------|---|--------------|
| On Booking | 10% | 325,600 |
| After 30 days | 10% | 325,600 |
| After 3 months | 5% | 162,800 |
| After 6 months | 5% | 162,800 |
| On Handover | 10% | 325,600 |
| After 6 months of Handover | 7.5% | 244,200 |
| (... continues for full payment schedule)

---

**Last Updated:** October 3, 2025  
**Module Version:** 17.0.3.2.8  
**Status:** ✅ Production Ready
