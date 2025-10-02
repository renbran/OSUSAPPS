# Upgrade Guide: Videographer Resource Booking Module

## 📋 Overview

This guide helps you upgrade from the basic appointment module (v1.3) to the enhanced videographer resource booking system (v2.0).

## ⚠️ Important Notes

- **Backup First:** Always backup your database before upgrading
- **Test Environment:** Test the upgrade in a staging environment first
- **Downtime:** Plan for brief downtime during upgrade
- **Data Migration:** Existing appointments will be preserved

## 🔄 Upgrade Steps

### Step 1: Backup Database

```bash
# PostgreSQL backup
pg_dump -U odoo_user -d your_database > backup_before_upgrade_$(date +%Y%m%d).sql

# Or use Odoo database manager
# Navigate to: http://your-domain/web/database/manager
```

### Step 2: Update Module Files

```bash
cd /path/to/odoo/addons/s2u_online_appointment

# Backup existing module
cp -r ../s2u_online_appointment ../s2u_online_appointment_backup

# Update module files
# Replace with new module files
```

### Step 3: Restart Odoo

```bash
sudo systemctl restart odoo
# or
sudo service odoo restart
```

### Step 4: Upgrade Module

1. **Via UI:**
   - Go to Apps menu
   - Search for "Videographer Resource Booking"
   - Click "Upgrade"

2. **Via Command Line:**
   ```bash
   odoo-bin -d your_database -u s2u_online_appointment --stop-after-init
   ```

### Step 5: Data Migration

The upgrade automatically:
- Migrates existing appointments to new booking system
- Preserves calendar events
- Maintains customer information
- Keeps existing slots and options

#### Manual Steps Required:

1. **Create Videographer Profiles**
   - Go to: Videographers → Videographer Profiles
   - Create profiles for existing users who handled appointments
   - Link them to corresponding user accounts

2. **Link Existing Appointments**
   - Go to: Bookings → All Bookings
   - Review appointments without videographer assignment
   - Assign appropriate videographer to each

3. **Set Up Service Packages** (Optional)
   - Create packages based on existing appointment options
   - Set pricing, features, and deliverables

4. **Configure Specializations & Equipment**
   - Review pre-loaded specializations
   - Add equipment inventory for each videographer

### Step 6: Update Availability Slots

The upgrade adds new fields to slots:
- `videographer_id` - Link to videographer profile
- `slot_type` - Regular/Temporary/Blocked
- `active` - Enable/disable specific slots

Update existing slots:
```sql
-- Link slots to videographer profiles
UPDATE s2u_appointment_slot
SET videographer_id = (
    SELECT id FROM s2u_videographer_profile
    WHERE user_id = s2u_appointment_slot.user_id
    LIMIT 1
)
WHERE videographer_id IS NULL;

-- Set default slot type
UPDATE s2u_appointment_slot
SET slot_type = 'regular', active = TRUE
WHERE slot_type IS NULL;
```

### Step 7: Update Website/Portal

1. **Check Frontend Templates**
   - Review booking page for new package selection
   - Test responsive layout on mobile devices

2. **Update Navigation**
   - Menu items have been reorganized
   - Update any custom website pages with links

3. **Test Booking Flow**
   - Complete test booking from frontend
   - Verify calendar integration
   - Check email notifications

### Step 8: Configure Email Templates

1. Navigate to: Settings → Technical → Email Templates
2. Review and customize:
   - Booking Confirmation Email
   - Booking Reminder Email
   - Review Request Email

### Step 9: Set User Permissions

New security groups and permissions:
- Videographer users can manage their profile
- Portal users can create and view bookings
- Managers have full access

Update user access rights:
1. Go to: Settings → Users & Companies → Users
2. For each videographer:
   - Ensure they're in "Website Designer" group
   - Link to videographer profile

## 🆕 New Features to Configure

### 1. Service Packages

```python
# Example: Create a wedding package
wedding_package = env['s2u.service.package'].create({
    'name': 'Premium Wedding Package',
    'category': 'wedding',
    'base_price': 2500.00,
    'deposit_percentage': 30.0,
    'duration_hours': 8.0,
    'is_public': True,
    'popular': True,
})
```

### 2. Add-ons System

Pre-loaded add-ons include:
- Extra Hour Coverage
- Additional Videographer
- Drone Footage
- Raw Footage
- Rush Delivery
- Social Media Edits

Customize pricing: Configuration → Package Add-ons

### 3. Payment Tracking

New payment fields on bookings:
- `deposit_amount` - Auto-calculated from percentage
- `paid_amount` - Track payments received
- `balance_due` - Remaining balance
- `payment_status` - Payment state

### 4. Reviews & Ratings

Enable customer reviews:
1. Bookings automatically show review option when completed
2. Reviews require approval before showing publicly
3. Average ratings displayed on videographer profiles

## 🔍 Post-Upgrade Checklist

- [ ] All existing appointments visible in Bookings
- [ ] Videographer profiles created and linked
- [ ] Availability slots working correctly
- [ ] Service packages configured
- [ ] Frontend booking page functional
- [ ] Calendar integration working
- [ ] Email notifications sending
- [ ] Payment tracking operational
- [ ] Portal access working for customers
- [ ] Mobile responsive design verified
- [ ] Analytics/reports functional

## 🐛 Troubleshooting

### Issue: Missing Videographer on Bookings

**Solution:**
```python
# Run in Odoo shell
bookings = env['s2u.appointment.registration'].search([('videographer_id', '=', False)])
for booking in bookings:
    # Find videographer by user
    videographer = env['s2u.videographer.profile'].search([
        ('user_id', '=', booking.event_id.user_id.id)
    ], limit=1)
    if videographer:
        booking.videographer_id = videographer.id
```

### Issue: Slots Not Showing Videographer

**Solution:**
```python
# Update slots without videographer
slots = env['s2u.appointment.slot'].search([('videographer_id', '=', False)])
for slot in slots:
    videographer = env['s2u.videographer.profile'].search([
        ('user_id', '=', slot.user_id.id)
    ], limit=1)
    if videographer:
        slot.videographer_id = videographer.id
```

### Issue: Booking Reference Not Generated

**Solution:**
```python
# Regenerate booking references
bookings = env['s2u.appointment.registration'].search([('name', 'in', ['New', False])])
for booking in bookings:
    booking.name = env['ir.sequence'].next_by_code('s2u.booking') or 'BOOK' + str(booking.id).zfill(5)
```

### Issue: Calendar Events Broken

**Solution:**
```python
# Sync calendar events for bookings
bookings = env['s2u.appointment.registration'].search([('state', '=', 'confirmed')])
for booking in bookings:
    booking._sync_calendar_event()
```

## 📊 Database Schema Changes

### New Tables
- `s2u_videographer_profile` - Videographer profiles
- `s2u_videographer_specialization` - Specializations
- `s2u_videographer_equipment` - Equipment
- `s2u_equipment_category` - Equipment categories
- `s2u_videographer_portfolio` - Portfolio items
- `s2u_videographer_review` - Reviews
- `s2u_service_package` - Service packages
- `s2u_package_feature` - Package features
- `s2u_package_deliverable` - Deliverables
- `s2u_package_addon` - Add-ons catalog
- `s2u_booking_addon` - Booking add-ons

### Modified Tables
- `s2u_appointment_registration` - New fields for pricing, payment, location
- `s2u_appointment_slot` - New fields for videographer link, type, dates

### New Sequences
- `s2u.booking` - Booking reference numbers (BOOK00001, BOOK00002, etc.)

## 🔄 Rollback Procedure

If you need to rollback:

1. **Stop Odoo**
   ```bash
   sudo systemctl stop odoo
   ```

2. **Restore Database**
   ```bash
   psql -U odoo_user -d your_database < backup_before_upgrade.sql
   ```

3. **Restore Module Files**
   ```bash
   rm -rf /path/to/odoo/addons/s2u_online_appointment
   cp -r ../s2u_online_appointment_backup ../s2u_online_appointment
   ```

4. **Restart Odoo**
   ```bash
   sudo systemctl start odoo
   ```

## 📞 Support

If you encounter issues during upgrade:
- Check Odoo logs: `/var/log/odoo/odoo-server.log`
- Review this guide's troubleshooting section
- Contact support: info@ubbels.com

## ✅ Verification Script

Run this SQL to verify upgrade success:

```sql
-- Check videographer profiles
SELECT COUNT(*) as videographer_count FROM s2u_videographer_profile WHERE active = true;

-- Check bookings with videographer
SELECT COUNT(*) as bookings_with_videographer FROM s2u_appointment_registration WHERE videographer_id IS NOT NULL;

-- Check service packages
SELECT COUNT(*) as package_count FROM s2u_service_package WHERE active = true;

-- Check slots with videographer link
SELECT COUNT(*) as linked_slots FROM s2u_appointment_slot WHERE videographer_id IS NOT NULL;

-- Check reviews
SELECT COUNT(*) as review_count FROM s2u_videographer_review;
```

Expected results:
- At least 1 videographer profile
- All bookings should have videographer assigned
- At least 1 service package (if configured)
- All slots linked to videographer
- Reviews may be 0 initially

---

**Upgrade completed successfully? Welcome to the enhanced videographer booking system! 🎉**