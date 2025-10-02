# Property Sales Offer Report - Quick Installation Guide

## Installation Steps

### 1. Files Created
The following files have been added to the `rental_management` module:

```
rental_management/
├── report/
│   └── property_sales_offer_report.xml    (NEW - Main report template)
├── __manifest__.py                         (UPDATED - Added report reference)
└── PROPERTY_SALES_OFFER_REPORT.md         (NEW - Documentation)
```

### 2. Module Update Required

After adding these files, you need to update the module:

#### Option A: Using Odoo UI (Recommended for Production)
1. Go to **Apps** menu
2. Remove the "Apps" filter to show all modules
3. Search for "rental_management" or "Property Sale & Rental Management"
4. Click the **Upgrade** button
5. Wait for the upgrade to complete

#### Option B: Using Command Line (Development)
```bash
# Navigate to your Odoo directory
cd /path/to/odoo

# Update the module
./odoo-bin -c odoo.conf -u rental_management -d your_database_name --stop-after-init

# Restart Odoo service
sudo systemctl restart odoo
```

#### Option C: Using Docker (Current Setup)
```bash
# From the project root directory
docker-compose exec odoo odoo --update=rental_management --stop-after-init -d odoo

# Restart the container
docker-compose restart odoo
```

### 3. Verify Installation

1. Open Odoo and navigate to **Property Management**
2. Open any property record that is marked "For Sale"
3. Click on the **Print** dropdown button
4. You should see a new option: **Property Sales Offer**
5. Click it to generate the PDF report

### 4. Testing the Report

#### Test with a Sample Property:

1. **Create/Open a Property**:
   - Name: "Luxury Villa with Sea View"
   - Type: Residential
   - Property For: Sale
   - Price: 1,500,000 (or your currency)

2. **Fill Required Fields**:
   - Address (Street, City, State, Country)
   - Total Area: 2500 sq_ft
   - Rooms: 4
   - Bathrooms: 3
   - Parking: 2

3. **Add Images**:
   - Upload at least one main image
   - Add 3-4 property images to gallery

4. **Enable Payment Plan** (Optional):
   - Enable "Payment Plan" checkbox
   - Add payment plan lines totaling 100%

5. **Generate Report**:
   - Click Print → Property Sales Offer
   - Check all sections render correctly

### 5. Troubleshooting

#### Report Not Appearing in Print Menu
**Solution**: 
- Clear Odoo cache: Settings → Technical → Cache → Clear Cache
- Update module again
- Restart Odoo service

#### Images Not Displaying
**Solution**:
- Ensure images are uploaded in binary format
- Check file size (should be under 10MB per image)
- Verify image field names match the template

#### Payment Plan Section Empty
**Solution**:
- Ensure property is marked "For Sale"
- Enable "Payment Plan" checkbox on property form
- Add payment plan lines with percentages totaling 100%

#### Layout Issues
**Solution**:
- Check browser compatibility (Chrome/Firefox recommended)
- Clear browser cache
- Verify Bootstrap CSS is loading

### 6. Customization

#### Changing Brand Colors
Edit the report template and replace `#800020` with your brand color:
```bash
# Find and replace in the file
sed -i 's/#800020/#YOUR_COLOR/g' rental_management/report/property_sales_offer_report.xml
```

#### Adding Company Logo
The report uses `web.external_layout` which automatically includes your company logo from:
- Settings → General Settings → Companies → Company Logo

#### Modifying Sections
Edit `rental_management/report/property_sales_offer_report.xml` and:
- Comment out unwanted sections with `<!-- -->`
- Add new sections following the existing pattern
- Update module after changes

### 7. Performance Optimization

For large property databases:

1. **Optimize Images**:
   - Compress images before upload (recommended: 1920x1080, under 500KB)
   - Use JPEG format for photos

2. **Limit Gallery Images**:
   - Recommend 8-10 images maximum per property
   - Use floor plans sparingly (2-3 max)

3. **Database Indexing**:
   ```sql
   CREATE INDEX idx_property_sale ON property_details(sale_lease);
   CREATE INDEX idx_property_plan ON property_details(is_payment_plan);
   ```

### 8. Multi-Language Support

The report supports translations. To add translations:

1. Go to Settings → Translations → Import/Export → Export Translations
2. Select `rental_management` module
3. Export PO file
4. Translate strings in the PO file
5. Import translated PO file back

### 9. User Permissions

Ensure users have proper permissions:

```xml
<!-- Add to security/security.xml if needed -->
<record id="property_sales_offer_report_access" model="ir.model.access">
    <field name="name">property.sales.offer.report.access</field>
    <field name="model_id" ref="model_property_details"/>
    <field name="group_id" ref="rental_management.group_property_user"/>
    <field name="perm_read" eval="1"/>
    <field name="perm_write" eval="0"/>
    <field name="perm_create" eval="0"/>
    <field name="perm_unlink" eval="0"/>
</record>
```

### 10. Production Deployment Checklist

- [ ] Files committed to version control
- [ ] Module updated on all environments (dev, staging, prod)
- [ ] Test report generation with sample data
- [ ] Verify payment plan calculations
- [ ] Check image rendering quality
- [ ] Test with different property types
- [ ] Verify multi-page layout
- [ ] Test on different browsers
- [ ] Review with sales team
- [ ] Train users on new report

## Quick Command Reference

```bash
# Docker-based setup (recommended for this project)
docker-compose exec odoo odoo -u rental_management --stop-after-init -d odoo
docker-compose restart odoo
docker-compose logs -f odoo

# Check module status
docker-compose exec odoo odoo shell -d odoo
>>> self.env['ir.module.module'].search([('name', '=', 'rental_management')])

# Clear cache
docker-compose exec odoo odoo --dev=all -d odoo
```

## Support

For issues or questions:
1. Check the comprehensive documentation: `PROPERTY_SALES_OFFER_REPORT.md`
2. Review Odoo logs: `docker-compose logs -f odoo`
3. Contact development team

---

**Status**: Ready for Installation
**Version**: 1.0.0
**Last Updated**: October 2025
