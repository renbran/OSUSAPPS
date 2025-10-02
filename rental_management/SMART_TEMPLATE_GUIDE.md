# Smart Template System - Dynamic Field Handling Guide

## Overview

This guide explains how to create **intelligent PDF reports** that automatically:
- ✅ Hide empty/null fields
- ✅ Reorganize layout to fill available space
- ✅ Adjust grid columns dynamically
- ✅ Show/hide entire sections based on data availability
- ✅ Maintain professional appearance with any data combination

---

## Core Principles

### 1. **Conditional Rendering**
Only show fields that have values:
```xml
<!-- ❌ BAD: Always shows label even if field is empty -->
<div>
    <label>Property Owner:</label>
    <span t-field="doc.landlord_id"/>
</div>

<!-- ✅ GOOD: Only shows if field has value -->
<t t-if="doc.landlord_id">
    <div>
        <label>Property Owner:</label>
        <span t-field="doc.landlord_id"/>
    </div>
</t>
```

### 2. **Dynamic Grid Layouts**
Adjust column widths based on content:
```xml
<!-- Dynamic column sizing -->
<t t-set="available_fields" t-value="0"/>
<t t-if="doc.bed">
    <t t-set="available_fields" t-value="available_fields + 1"/>
</t>
<t t-if="doc.bathroom">
    <t t-set="available_fields" t-value="available_fields + 1"/>
</t>

<!-- Calculate column width -->
<t t-set="col_width" t-value="12 // max(available_fields, 1)"/>

<!-- Apply dynamic width -->
<t t-if="doc.bed">
    <div t-attf-class="col-{{col_width}}">
        <span t-field="doc.bed"/> Bedrooms
    </div>
</t>
```

### 3. **Smart Sections**
Hide entire sections if no data exists:
```xml
<!-- ❌ BAD: Shows section even if no amenities -->
<div class="amenities-section">
    <h3>Amenities</h3>
    <t t-foreach="doc.amenities_ids" t-as="amenity">
        <span t-field="amenity.name"/>
    </t>
</div>

<!-- ✅ GOOD: Only shows if amenities exist -->
<t t-if="doc.amenities_ids and len(doc.amenities_ids) > 0">
    <div class="amenities-section">
        <h3>Amenities</h3>
        <t t-foreach="doc.amenities_ids" t-as="amenity">
            <span t-field="amenity.name"/>
        </t>
    </div>
</t>
```

---

## Implementation Patterns

### Pattern 1: Flexible Table Rows

**Problem:** Tables with empty fields create gaps

**Solution:**
```xml
<table class="table">
    <tbody>
        <!-- Only show rows with data -->
        <t t-if="doc.region_id">
            <tr>
                <td>Region</td>
                <td><span t-field="doc.region_id"/></td>
            </tr>
        </t>
        <t t-if="doc.city_id">
            <tr>
                <td>City</td>
                <td><span t-field="doc.city_id"/></td>
            </tr>
        </t>
        <t t-if="doc.street">
            <tr>
                <td>Street</td>
                <td><span t-field="doc.street"/></td>
            </tr>
        </t>
    </tbody>
</table>
```

### Pattern 2: Dynamic Grid Columns

**Problem:** Fixed grid leaves empty spaces

**Solution:**
```xml
<!-- Count available fields -->
<t t-set="field_count" t-value="0"/>
<t t-set="has_bed" t-value="doc.bed and doc.bed > 0"/>
<t t-set="has_bathroom" t-value="doc.bathroom and doc.bathroom > 0"/>
<t t-set="has_parking" t-value="doc.parking and doc.parking > 0"/>
<t t-set="has_area" t-value="doc.total_area and doc.total_area > 0"/>

<t t-if="has_bed"><t t-set="field_count" t-value="field_count + 1"/></t>
<t t-if="has_bathroom"><t t-set="field_count" t-value="field_count + 1"/></t>
<t t-if="has_parking"><t t-set="field_count" t-value="field_count + 1"/></t>
<t t-if="has_area"><t t-set="field_count" t-value="field_count + 1"/></t>

<!-- Calculate responsive column class -->
<t t-set="col_class" t-value="'col-' + str(12 // max(field_count, 1))"/>

<div class="row">
    <t t-if="has_bed">
        <div t-att-class="col_class">
            <strong><span t-field="doc.bed"/></strong> Bedrooms
        </div>
    </t>
    <t t-if="has_bathroom">
        <div t-att-class="col_class">
            <strong><span t-field="doc.bathroom"/></strong> Bathrooms
        </div>
    </t>
    <t t-if="has_parking">
        <div t-att-class="col_class">
            <strong><span t-field="doc.parking"/></strong> Parking
        </div>
    </t>
    <t t-if="has_area">
        <div t-att-class="col_class">
            <strong><span t-field="doc.total_area"/></strong> <span t-field="doc.measure_unit"/>
        </div>
    </t>
</div>
```

### Pattern 3: Inline Grouping

**Problem:** Multiple related optional fields

**Solution:**
```xml
<!-- Group related fields inline -->
<div>
    <span t-field="doc.type"/>
    <t t-if="doc.property_subtype_id">
        - <span t-field="doc.property_subtype_id"/>
    </t>
    <t t-if="doc.furnishing_id">
        | <span t-field="doc.furnishing_id"/>
    </t>
    <t t-if="doc.property_status">
        | Status: <span t-field="doc.property_status"/>
    </t>
</div>
```

### Pattern 4: Smart Pagination

**Problem:** Page breaks with no content following

**Solution:**
```xml
<!-- Only add page break if next section has content -->
<t t-set="has_next_section" t-value="doc.property_images_ids or doc.floreplan_ids"/>
<t t-if="has_next_section">
    <p style="page-break-before: always;"/>
</t>
```

### Pattern 5: Fallback Content

**Problem:** Completely empty sections look unprofessional

**Solution:**
```xml
<t t-if="doc.description">
    <p><span t-field="doc.description"/></p>
</t>
<t t-else="">
    <p style="color: #999; font-style: italic;">
        Description not available. Contact us for more details.
    </p>
</t>
```

---

## Advanced Techniques

### Technique 1: Field Value Checking

```xml
<!-- Check different types of empty values -->
<t t-set="has_value" t-value="doc.field_name and doc.field_name != False and doc.field_name != 0 and doc.field_name != ''"/>

<!-- For Many2one fields -->
<t t-if="doc.partner_id and doc.partner_id.id">
    <span t-field="doc.partner_id"/>
</t>

<!-- For One2many/Many2many fields -->
<t t-if="doc.line_ids and len(doc.line_ids) > 0">
    <t t-foreach="doc.line_ids" t-as="line">
        ...
    </t>
</t>

<!-- For Boolean fields -->
<t t-if="doc.is_active == True">
    Active Property
</t>

<!-- For Monetary fields -->
<t t-if="doc.price and doc.price > 0">
    <span t-field="doc.price" t-options='{"widget": "monetary"}'/>
</t>
```

### Technique 2: Dynamic Style Classes

```xml
<!-- Add CSS classes based on data availability -->
<t t-set="section_class" t-value="'full-width' if not doc.sidebar_content else 'with-sidebar'"/>

<div t-att-class="section_class">
    <!-- Content adjusts based on class -->
</div>
```

### Technique 3: Computed Variables

```xml
<!-- Pre-compute boolean checks for cleaner code -->
<t t-set="show_payment_plan" t-value="doc.sale_lease == 'for_sale' and doc.is_payment_plan and doc.custom_payment_plan_line_ids and len(doc.custom_payment_plan_line_ids) > 0"/>

<t t-if="show_payment_plan">
    <!-- Payment plan section -->
</t>
```

### Technique 4: Smart Column Distribution

```xml
<!-- Distribute fields evenly across available space -->
<t t-set="fields_to_show" t-value="[]"/>
<t t-if="doc.field1"><t t-set="fields_to_show" t-value="fields_to_show + ['field1']"/></t>
<t t-if="doc.field2"><t t-set="fields_to_show" t-value="fields_to_show + ['field2']"/></t>
<t t-if="doc.field3"><t t-set="fields_to_show" t-value="fields_to_show + ['field3']"/></t>

<t t-set="total_fields" t-value="len(fields_to_show)"/>
<t t-set="fields_per_row" t-value="min(total_fields, 4)"/>
<t t-set="col_size" t-value="12 // fields_per_row"/>

<div class="row">
    <t t-foreach="fields_to_show" t-as="field_name">
        <div t-attf-class="col-{{col_size}}">
            <!-- Dynamic field rendering -->
        </div>
    </t>
</div>
```

---

## Complete Example: Smart Key Highlights Section

```xml
<!-- Smart Key Highlights with Dynamic Layout -->
<t t-set="has_highlights" t-value="doc.type or doc.price or doc.bed or doc.bathroom or doc.parking or doc.total_area"/>

<t t-if="has_highlights">
    <div class="mb-4">
        <h3>Key Highlights</h3>
        <div style="border: 3px solid #800020; padding: 20px; background-color: #f8f9fa; border-radius: 8px;">
            <div class="row">
                <!-- Property Type & Price (always full width if present) -->
                <t t-if="doc.type">
                    <div class="col-6 mb-3">
                        <div style="background: white; padding: 15px; border-radius: 6px;">
                            <div style="color: #666; font-size: 0.9rem;">Property Type</div>
                            <div style="font-weight: bold; font-size: 1.2rem; color: #800020;">
                                <span t-field="doc.type"/>
                                <t t-if="doc.property_subtype_id"> - <span t-field="doc.property_subtype_id"/></t>
                            </div>
                        </div>
                    </div>
                </t>
                
                <t t-if="doc.price and doc.price > 0">
                    <div class="col-6 mb-3">
                        <div style="background: white; padding: 15px; border-radius: 6px;">
                            <div style="color: #666; font-size: 0.9rem;">Sale Price</div>
                            <div style="font-weight: bold; font-size: 1.5rem; color: #28a745;">
                                <span t-field="doc.price" t-options='{"widget": "monetary", "display_currency": doc.currency_id}'/>
                            </div>
                        </div>
                    </div>
                </t>
            </div>
            
            <!-- Dynamic grid for specs -->
            <t t-set="spec_count" t-value="0"/>
            <t t-if="doc.bed and doc.bed > 0"><t t-set="spec_count" t-value="spec_count + 1"/></t>
            <t t-if="doc.bathroom and doc.bathroom > 0"><t t-set="spec_count" t-value="spec_count + 1"/></t>
            <t t-if="doc.parking and doc.parking > 0"><t t-set="spec_count" t-value="spec_count + 1"/></t>
            <t t-if="doc.total_area and doc.total_area > 0"><t t-set="spec_count" t-value="spec_count + 1"/></t>
            
            <t t-if="spec_count > 0">
                <!-- Calculate column size: 12 columns / number of specs -->
                <t t-set="spec_col_size" t-value="12 // spec_count if spec_count > 0 else 12"/>
                
                <div class="row">
                    <t t-if="doc.bed and doc.bed > 0">
                        <div t-attf-class="col-{{spec_col_size}} mb-3">
                            <div style="background: white; padding: 15px; border-radius: 6px; text-align: center;">
                                <div style="font-size: 2rem; color: #800020; font-weight: bold;">
                                    <span t-field="doc.bed"/>
                                </div>
                                <div style="color: #666; font-size: 0.9rem;">Bedrooms</div>
                            </div>
                        </div>
                    </t>
                    
                    <t t-if="doc.bathroom and doc.bathroom > 0">
                        <div t-attf-class="col-{{spec_col_size}} mb-3">
                            <div style="background: white; padding: 15px; border-radius: 6px; text-align: center;">
                                <div style="font-size: 2rem; color: #800020; font-weight: bold;">
                                    <span t-field="doc.bathroom"/>
                                </div>
                                <div style="color: #666; font-size: 0.9rem;">Bathrooms</div>
                            </div>
                        </div>
                    </t>
                    
                    <t t-if="doc.parking and doc.parking > 0">
                        <div t-attf-class="col-{{spec_col_size}} mb-3">
                            <div style="background: white; padding: 15px; border-radius: 6px; text-align: center;">
                                <div style="font-size: 2rem; color: #800020; font-weight: bold;">
                                    <span t-field="doc.parking"/>
                                </div>
                                <div style="color: #666; font-size: 0.9rem;">Parking Spaces</div>
                            </div>
                        </div>
                    </t>
                    
                    <t t-if="doc.total_area and doc.total_area > 0">
                        <div t-attf-class="col-{{spec_col_size}} mb-3">
                            <div style="background: white; padding: 15px; border-radius: 6px; text-align: center;">
                                <div style="font-size: 1.5rem; color: #800020; font-weight: bold;">
                                    <span t-field="doc.total_area"/> <span t-field="doc.measure_unit"/>
                                </div>
                                <div style="color: #666; font-size: 0.9rem;">Total Area</div>
                            </div>
                        </div>
                    </t>
                </div>
            </t>
        </div>
    </div>
</t>
```

---

## Best Practices

### ✅ DO:
1. **Always check for null/empty values** before rendering
2. **Group related optional fields** inline when possible
3. **Calculate grid columns dynamically** based on available data
4. **Hide entire sections** if no data exists
5. **Use t-set to pre-compute** complex conditions
6. **Add fallback content** for critical sections
7. **Test with minimal data** to ensure layout adapts

### ❌ DON'T:
1. **Don't use fixed grid sizes** when content varies
2. **Don't show empty labels** without values
3. **Don't create page breaks** before empty sections
4. **Don't assume all fields** will have values
5. **Don't use nested conditions** excessively (use t-set)
6. **Don't forget Many2one ID checks** (doc.field_id.id)
7. **Don't hardcode column counts** for optional fields

---

## Testing Checklist

Test your smart template with:
- [ ] Fully populated record (all fields)
- [ ] Minimally populated record (required fields only)
- [ ] Record with no images
- [ ] Record with no amenities
- [ ] Record with no payment plan
- [ ] Record with only 1-2 specs (not 4)
- [ ] Record with no description
- [ ] Record with no connectivity data

**Expected Result:** Report looks professional in ALL scenarios with no empty sections or wasted space.

---

## Performance Considerations

### Optimize t-set Usage
```xml
<!-- ❌ BAD: Recalculating same value multiple times -->
<t t-if="doc.field1 and doc.field2 and doc.field3">...</t>
<t t-if="doc.field1 and doc.field2 and doc.field3">...</t>

<!-- ✅ GOOD: Calculate once, reuse -->
<t t-set="show_section" t-value="doc.field1 and doc.field2 and doc.field3"/>
<t t-if="show_section">...</t>
<t t-if="show_section">...</t>
```

### Minimize Nested Loops
```xml
<!-- ❌ BAD: Nested loops with conditions -->
<t t-foreach="doc.lines" t-as="line">
    <t t-foreach="line.items" t-as="item">
        <t t-if="item.active">...</t>
    </t>
</t>

<!-- ✅ GOOD: Filter first, then loop -->
<t t-set="active_lines" t-value="doc.lines.filtered(lambda l: l.items)"/>
<t t-foreach="active_lines" t-as="line">
    ...
</t>
```

---

## Reusable Helper Patterns

### Pattern: Has Any Value
```xml
<t t-set="has_any_value" t-value="doc.field1 or doc.field2 or doc.field3 or doc.field4"/>
```

### Pattern: Count Non-Empty Fields
```xml
<t t-set="field_count" t-value="(1 if doc.field1 else 0) + (1 if doc.field2 else 0) + (1 if doc.field3 else 0)"/>
```

### Pattern: Format Optional Field
```xml
<t t-if="doc.field">
    <span t-field="doc.field"/>
</t>
<t t-else="">
    <span style="color: #999;">N/A</span>
</t>
```

---

## Migration Strategy

### Converting Existing Static Template

1. **Identify all optional fields**
2. **Wrap each in t-if condition**
3. **Group related fields**
4. **Calculate dynamic columns**
5. **Add section-level conditions**
6. **Test with varied data**
7. **Optimize performance**

---

**Result:** A professional, adaptive report that works perfectly regardless of which fields are populated! 🎯
