# Property Sales Offer Report - Comprehensive Documentation

## Overview
The **Property Sales Offer Report** is a professional, client-facing PDF document designed to present complete property information to prospective buyers. This report provides a comprehensive overview of property details, pricing, payment plans, amenities, and visual assets.

## Report Location
- **File**: `rental_management/report/property_sales_offer_report.xml`
- **Model**: `property.details`
- **Report Type**: PDF (QWeb)
- **Report Name**: `Property Sales Offer`

## Key Features

### 1. **Professional Design**
- Modern, gradient-styled headers with brand colors (#800020)
- Responsive layout with proper spacing and visual hierarchy
- High-quality typography and consistent styling
- Box shadows and rounded corners for premium appearance

### 2. **Comprehensive Property Information**

#### Cover Page
- Eye-catching header with report title
- Main property image (high-resolution, cover-fit display)
- Property name and code prominently displayed
- Project information (if applicable)

#### Key Highlights Section
- Property Type & Subtype
- Sale Price (monetary format with currency)
- Number of Rooms, Bathrooms, Parking
- Total Area with measurement units
- Visual cards with icons for quick reference

#### Location Details
- Complete address breakdown
- Region, Project, and Sub-project information
- GPS coordinates (if available)
- Formatted for easy readability

#### Property Specifications
- Total and usable area measurements
- BHK type (for residential properties)
- Furnishing details
- Floor information
- Facing direction
- Current status badge

#### Room-wise Area Breakdown
- Detailed table of all rooms/sections
- Measurements: Length, Width, Height (if applicable)
- Individual and total area calculations
- Supports both 2D and 3D measurements (sq_ft, sq_m, cu_ft, cu_m)

### 3. **Flexible Payment Plan Section**
(Only displayed for sale properties with payment plans enabled)

#### Price Breakdown
- Base sale price
- DLD Registration Fee (with percentage)
- Administrative Fee
- **Total Amount** including all fees
- Clear visual separation with gradient backgrounds

#### Payment Schedule Table
- Sequential numbering of payment milestones
- Detailed description of each payment
- Payment type badges (Booking, Construction, Handover, etc.)
- Days after booking (for time-based payments)
- Installment information (number and frequency)
- Percentage and calculated amount for each milestone
- Visual indicators for payment terms
- Footer showing 100% total verification

#### Payment Plan Benefits
- Information box highlighting advantages
- Flexible scheduling
- Transparent pricing
- Installment options
- Secure processing

### 4. **Property Features & Amenities**

#### Premium Amenities
- Grid layout of all available amenities
- Check-mark icons for visual confirmation
- Gradient background cards
- Left-border accent in brand color

#### Property Specifications
- Technical features and installations
- Similar visual style to amenities
- Different accent color (#17a2b8) for distinction

#### Nearby Connectivity
- Table format with location, type, and distance
- Badge styling for location types
- Distance with unit of measurement
- Map marker icons for visual reference

### 5. **Visual Assets**

#### Property Gallery
- Multi-image display in responsive grid (2 columns)
- High-quality image rendering (300px height)
- Image captions (if provided)
- Border styling with shadow effects
- Separate page for better presentation

#### Floor Plans
- Full-width display of floor plans
- Individual titles for each plan
- Optimized for print quality
- Maximum height constraint for consistency
- Separate page from other content

### 6. **Contact Information**
- Landlord/Owner name
- Phone number with icon
- Email address with icon
- Website link with icon
- Centered, prominent display
- Gradient background box

### 7. **Footer & Legal**
- Validity note
- Accuracy disclaimer
- Contact encouragement
- Property reference code
- Professional formatting

## Fields Extracted from Property Module

### Basic Information
- `name` - Property Name
- `property_seq` - Property Code
- `type` - Property Type (Land, Residential, Commercial, Industrial)
- `property_subtype_id` - Property Subtype
- `sale_lease` - Property For (Sale/Rent)
- `stage` - Current Status
- `description` - Property Description

### Location Data
- `region_id` - Region
- `property_project_id` - Project
- `subproject_id` - Sub Project
- `street`, `street2` - Address Lines
- `city_id` - City
- `zip` - Postal Code
- `state_id` - State/Province
- `country_id` - Country
- `latitude`, `longitude` - GPS Coordinates

### Pricing Information
- `price` - Sale/Rent Price
- `currency_id` - Currency
- `pricing_type` - Fixed or Area-wise
- `price_per_area` - Price per unit area
- `dld_fee_percentage` - DLD Fee Percentage
- `dld_fee_amount` - DLD Fee Amount
- `admin_fee` - Administrative Fee
- `total_with_fees` - Total Amount with Fees

### Measurements
- `total_area` - Total Area
- `usable_area` - Usable Area
- `measure_unit` - Unit of Measurement
- `room_measurement_ids` - Room-wise Measurements
  - `section_id.name` - Room/Section Name
  - `no_of_unit` - Number of Units
  - `length`, `width`, `height` - Dimensions
  - `carpet_area` - Calculated Area

### Property Details
- `bed` - Number of Bedrooms/Rooms
- `bathroom` - Number of Bathrooms
- `parking` - Parking Spaces
- `unit_type` - BHK Type
- `furnishing_id` - Furnishing Type
- `total_floor` - Total Floors
- `floor` - Floor Number
- `facing` - Facing Direction

### Payment Plan
- `is_payment_plan` - Payment Plan Enabled
- `custom_payment_plan_line_ids` - Payment Plan Lines
  - `name` - Milestone Description
  - `payment_type` - Type of Payment
  - `days_after` - Days After Booking
  - `installments` - Number of Installments
  - `installment_frequency` - Installment Frequency
  - `percentage` - Payment Percentage
  - `amount` - Payment Amount
  - `note` - Additional Notes

### Features & Amenities
- `amenities` - Amenities Available Flag
- `amenities_ids` - List of Amenities
- `is_facilities` - Specifications Available Flag
- `property_specification_ids` - List of Specifications
- `nearby_connectivity` - Connectivity Available Flag
- `connectivity_ids` - List of Nearby Locations
  - `connectivity_id.name` - Location Name
  - `connectivity_id.type` - Location Type
  - `distance` - Distance Value
  - `uom_id` - Unit of Measurement

### Visual Assets
- `image` - Main Property Image
- `is_images` - Images Available Flag
- `property_images_ids` - Property Image Gallery
  - `image` - Image Data
  - `name` - Image Caption
- `is_floor_plan` - Floor Plans Available Flag
- `floreplan_ids` - Floor Plan Images
  - `name` - Floor Plan Title
  - `image` - Floor Plan Image

### Owner Information
- `landlord_id` - Landlord/Owner
- `landlord_phone` - Contact Phone
- `landlord_email` - Contact Email
- `website` - Website URL

## Usage Instructions

### For Users:
1. Navigate to Property Management
2. Open any property record marked for sale
3. Click on **Print** → **Property Sales Offer**
4. The comprehensive PDF will be generated
5. Save or print the document for client presentation

### For Developers:

#### Accessing the Report
```python
# Programmatic report generation
property = self.env['property.details'].browse(property_id)
report = self.env.ref('rental_management.action_property_sales_offer_report')
pdf_content, _ = report._render_qweb_pdf([property.id])
```

#### Customization Points
1. **Colors**: Update the brand color (#800020) throughout the template
2. **Logo**: Modify `web.external_layout` to include company logo
3. **Additional Fields**: Add more fields from `property.details` model
4. **Sections**: Comment out or add new sections as needed
5. **Layout**: Adjust column widths, padding, and spacing

#### Adding New Sections
```xml
<div class="mb-4">
    <h3 style="background-color: #800020; color: white; padding: 15px;">
        <i class="fa fa-icon-name"></i>Section Title
    </h3>
    <div style="border: 3px solid #800020; padding: 20px;">
        <!-- Section content -->
    </div>
</div>
```

## Report Structure

### Page Layout
1. **Page 1**: Cover, Key Highlights, Location, Specifications, Room Breakdown
2. **Page 2**: Payment Plan (if applicable)
3. **Page 3**: Amenities, Features, Connectivity
4. **Page 4+**: Photo Gallery
5. **Page 5+**: Floor Plans
6. **Last Page**: Contact Information & Footer

### Conditional Rendering
- Payment plan section only shows for sale properties with plans enabled
- Room measurements only show when `is_section_measurement` is true
- Amenities section only shows when amenities are available
- Image gallery only shows when images are uploaded
- Floor plans only shows when plans are available

## Best Practices

### For Property Data Entry:
1. Always upload a high-quality main image
2. Fill in complete address details
3. Add detailed property description
4. Upload multiple property images (minimum 4-6)
5. Include floor plans for better visualization
6. Set up payment plan for sale properties
7. Add all relevant amenities and specifications
8. Fill in nearby connectivity information

### For Report Generation:
1. Ensure all required fields are populated
2. Verify payment plan calculations (should total 100%)
3. Check image quality before generation
4. Review the PDF before sharing with clients
5. Update property status to "available" before sharing

## Technical Specifications

### Dependencies
- Odoo 17 Web Module
- QWeb Reporting Engine
- Font Awesome Icons
- Bootstrap CSS Framework

### Performance
- Report generation: ~3-5 seconds
- PDF size: ~2-5 MB (depending on image count)
- Page count: 5-15 pages (depending on content)

### Compatibility
- Works with all property types
- Supports multiple currencies
- Multi-language support (translation-ready)
- Responsive to data availability

## Troubleshooting

### Common Issues:

1. **Images not displaying**
   - Ensure images are properly uploaded in binary format
   - Check `image_data_uri()` function is available

2. **Payment plan not showing**
   - Verify `sale_lease` is set to 'for_sale'
   - Check `is_payment_plan` is enabled
   - Ensure payment plan lines exist

3. **Layout issues**
   - Check browser compatibility
   - Verify Bootstrap CSS is loaded
   - Review inline styles

4. **Missing sections**
   - Verify conditional flags are enabled
   - Check related records exist
   - Review field permissions

## Future Enhancements

### Planned Features:
- [ ] QR code for property verification
- [ ] Interactive map with property location
- [ ] Comparison with similar properties
- [ ] Virtual tour integration
- [ ] Investment ROI calculator
- [ ] Multilingual support
- [ ] Custom branding per landlord
- [ ] Digital signature section

## Support & Maintenance

### Module Information:
- **Module**: rental_management (v3.2.8)
- **Report**: property_sales_offer_report.xml
- **Author**: TechKhedut Inc.
- **License**: OPL-1

### Contact:
For customization requests, bug reports, or feature suggestions, please contact the development team.

---

**Last Updated**: October 2025
**Version**: 1.0.0
**Status**: Production Ready
