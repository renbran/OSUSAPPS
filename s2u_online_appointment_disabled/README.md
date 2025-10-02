# Videographer Resource Booking Module for Odoo 17

## 📸 Overview

A comprehensive, world-class videographer booking system for Odoo 17. This module transforms your Odoo instance into a professional videography booking platform with advanced features for managing videographers, service packages, bookings, payments, and customer reviews.

## ✨ Key Features

### 🎥 Videographer Management
- **Professional Profiles** with biography, experience, and specializations
- **Portfolio Management** with images and video links
- **Equipment Inventory** tracking
- **Service Areas** and travel fee management
- **Availability Management** with buffer times and booking limits
- **Reviews & Ratings** system
- **Social Media Integration** (Instagram, YouTube, Facebook)

### 📦 Service Packages
- **Flexible Packages** for different event types (Wedding, Corporate, Events, etc.)
- **Dynamic Pricing** with base rates and deposits
- **Package Features** and deliverables
- **Add-ons System** (extra hours, drone footage, rush delivery, etc.)
- **Videographer Assignment** per package

### 📅 Advanced Booking System
- **Booking Workflow** (Draft → Pending → Confirmed → In Progress → Completed)
- **Smart Availability** checking with conflict detection
- **Multi-day Support** with flexible scheduling
- **Location Management** with travel distance calculation
- **Custom Notes** and special requirements
- **Calendar Integration** with Odoo's native calendar

### 💰 Payment Management
- **Deposit System** with configurable percentages
- **Payment Tracking** (Unpaid, Deposit Paid, Partially Paid, Fully Paid)
- **Discount Management** with percentage-based discounts
- **Add-ons Pricing** with quantity support
- **Invoicing Ready** (integrates with Odoo's accounting)

### 📊 Analytics & Reporting
- **Booking Analytics** with pivot tables and graphs
- **Revenue Reports** by videographer
- **Performance Metrics** (bookings, ratings, revenue)
- **Calendar View** for resource planning

### 🌐 Modern Frontend
- **Responsive Design** optimized for mobile and desktop
- **Interactive Calendar** with available dates highlighted
- **Real-time Availability** checking
- **Service Package Browser** with rich descriptions
- **Customer Portal** for managing bookings

### 📧 Automated Notifications
- **Booking Confirmation** emails with details
- **Reminder Emails** (3 days before event)
- **Review Requests** after completion
- **Customizable Templates** with modern HTML design

## 🚀 Installation

### Prerequisites
- Odoo 17.0 or higher
- Python 3.10+
- PostgreSQL 12+

### Installation Steps

1. **Copy Module Files**
   ```bash
   cd /path/to/odoo/addons
   cp -r /path/to/s2u_online_appointment .
   ```

2. **Update Module List**
   - Go to Apps menu in Odoo
   - Click "Update Apps List"
   - Search for "Videographer Resource Booking"

3. **Install Module**
   - Click "Install" button
   - Wait for installation to complete

4. **Restart Odoo Service** (if needed)
   ```bash
   sudo systemctl restart odoo
   ```

## 📖 Configuration

### Initial Setup

1. **Configure Specializations**
   - Go to: Videographer Booking → Configuration → Specializations
   - Default specializations are pre-loaded (Wedding, Corporate, Event, etc.)
   - Add custom specializations as needed

2. **Set Up Equipment**
   - Navigate to: Configuration → Equipment Categories
   - Add equipment items: Configuration → Equipment
   - Organize by categories (Cameras, Drones, Lighting, etc.)

3. **Create Videographer Profiles**
   - Go to: Videographers → Videographer Profiles
   - Click "Create"
   - Fill in:
     - Basic information (name, user account, experience)
     - Biography and social media links
     - Pricing (hourly rate, minimum hours)
     - Service areas and travel fees
     - Equipment inventory
     - Availability settings

4. **Set Up Availability Slots**
   - In each videographer profile, go to "Availability Settings" tab
   - Add weekly time slots for availability
   - Configure buffer times and booking limits
   - Set advance booking requirements

5. **Create Service Packages**
   - Navigate to: Services → Service Packages
   - Create packages for different event types
   - Configure:
     - Base pricing and deposit percentage
     - Duration and resource requirements
     - Features and deliverables
     - Available add-ons
     - Assign to specific videographers (optional)

6. **Configure Package Features & Add-ons**
   - Go to: Configuration → Package Features
   - Go to: Configuration → Package Add-ons
   - Default items are pre-loaded
   - Customize as needed

## 💼 Usage

### For Administrators

#### Managing Videographers
1. Create videographer profiles with complete information
2. Upload portfolio items (images/videos)
3. Set availability schedules
4. Monitor performance metrics

#### Managing Bookings
1. View all bookings: Bookings → All Bookings
2. Use calendar view for visual scheduling
3. Filter by status, payment, videographer
4. Manually create bookings if needed
5. Track payments and mark as paid
6. Send confirmation emails

#### Analytics
1. Go to: Bookings → All Bookings
2. Switch to Pivot or Graph view
3. Analyze by videographer, package, date range
4. Export reports as needed

### For Videographers

#### Managing Your Profile
1. Access your profile from user menu
2. Update bio, portfolio, and equipment
3. Set your availability schedule
4. View your bookings and performance

#### Managing Your Bookings
1. View assigned bookings
2. Update status (Start, Complete)
3. Add internal notes
4. Communicate with clients via chatter

### For Customers (Website/Portal)

#### Browsing Videographers
1. Visit the booking page
2. Browse available videographers
3. View profiles, portfolios, and ratings
4. Check service packages

#### Making a Booking
1. Select a service package
2. Choose preferred videographer
3. Select date from interactive calendar
4. Choose available time slot
5. Add custom notes and requirements
6. Review pricing and add-ons
7. Submit booking

#### Managing Bookings
1. Login to customer portal
2. View "My Bookings"
3. See booking details
4. Cancel if needed (before event)
5. Leave review after completion

## 🎨 Customization

### Extending the Module

#### Custom Fields
Add custom fields to models by inheriting:
```python
from odoo import models, fields

class VideographerProfileCustom(models.Model):
    _inherit = 's2u.videographer.profile'

    custom_field = fields.Char(string='Custom Field')
```

#### Custom Views
Override views in your custom module:
```xml
<record id="custom_videographer_form" model="ir.ui.view">
    <field name="name">custom.videographer.form</field>
    <field name="model">s2u.videographer.profile</field>
    <field name="inherit_id" ref="s2u_online_appointment.videographer_profile_view_form"/>
    <field name="arch" type="xml">
        <!-- Your customizations here -->
    </field>
</record>
```

#### Custom Controllers
Extend controllers for custom booking logic:
```python
from odoo.addons.s2u_online_appointment.controllers.main import OnlineAppointment

class CustomAppointment(OnlineAppointment):
    def prepare_values(self, **kwargs):
        values = super().prepare_values(**kwargs)
        # Add custom logic
        return values
```

## 🔧 Technical Details

### Module Structure
```
s2u_online_appointment/
├── __init__.py
├── __manifest__.py
├── controllers/
│   ├── __init__.py
│   ├── main.py           # Main booking controller
│   └── portal.py         # Customer portal controller
├── data/
│   ├── default_data.xml      # Default specializations, equipment, features
│   ├── ir_sequence_data.xml  # Booking reference sequence
│   └── mail_template_data.xml # Email templates
├── helpers/
│   ├── __init__.py
│   └── functions.py      # Utility functions
├── models/
│   ├── __init__.py
│   ├── videographer_profile.py   # Videographer profiles
│   ├── service_package.py        # Service packages & add-ons
│   ├── appointment_registration.py # Bookings
│   ├── appointment_slot.py        # Availability slots
│   └── appointment_option.py      # Service options (legacy)
├── security/
│   └── ir.model.access.csv    # Access rights
├── static/
│   ├── src/
│   │   ├── js/
│   │   │   ├── main.js        # Frontend JavaScript
│   │   │   └── daterange.js   # Date picker
│   │   └── scss/
│   │       └── daterange.scss # Styles
│   └── description/
│       └── icon.png
└── views/
    ├── menus.xml                      # Menu structure
    ├── videographer_profile_view.xml  # Videographer views
    ├── service_package_view.xml       # Package views
    ├── booking_view.xml               # Booking views
    ├── appointment_slot_view.xml      # Slot views
    ├── appointment_option_view.xml    # Option views
    ├── appointment_template.xml       # Frontend templates
    └── appointment_portal_template.xml # Portal templates
```

### Database Models

**Main Models:**
- `s2u.videographer.profile` - Videographer profiles
- `s2u.service.package` - Service packages
- `s2u.appointment.registration` - Bookings
- `s2u.appointment.slot` - Availability slots
- `s2u.videographer.review` - Reviews & ratings
- `s2u.videographer.portfolio` - Portfolio items

**Supporting Models:**
- `s2u.videographer.specialization` - Specializations
- `s2u.videographer.equipment` - Equipment items
- `s2u.equipment.category` - Equipment categories
- `s2u.package.feature` - Package features
- `s2u.package.deliverable` - Deliverables
- `s2u.package.addon` - Add-ons
- `s2u.booking.addon` - Booking add-ons

## 🐛 Troubleshooting

### Common Issues

**Module doesn't appear in Apps list**
- Ensure module is in correct addons path
- Update apps list
- Check Odoo logs for errors

**Access Rights Issues**
- Verify user has correct groups
- Check `ir.model.access.csv`
- Clear browser cache

**Booking creation fails**
- Check sequence `s2u.booking` exists
- Verify videographer profile is complete
- Check calendar event permissions

**Frontend not working**
- Clear Odoo assets cache
- Check JavaScript console for errors
- Verify assets are properly loaded

## 📝 Support & Contribution

### Getting Help
- Check documentation in `/doc` folder
- Review Odoo logs: `/var/log/odoo/odoo-server.log`
- Contact: info@ubbels.com

### Contributing
Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Follow Odoo coding guidelines
4. Test thoroughly
5. Submit pull request

## 📄 License

**OPL-1** (Odoo Proprietary License v1.0)

See LICENSE file for details.

## 🙏 Credits

- **Author:** Ubbels.com
- **Maintainer:** Ubbels.com
- **Contributors:** Development Team

## 📊 Version History

### Version 17.0.2.0 (Current)
- Complete transformation to videographer resource booking system
- Added videographer profiles with portfolios
- Service packages with flexible pricing
- Enhanced booking workflow
- Payment tracking system
- Reviews and ratings
- Modern UI/UX
- Email notifications
- Analytics dashboard

### Version 17.0.1.3 (Legacy)
- Basic appointment booking
- Simple slot management
- Calendar integration

---

**Made with ❤️ for Odoo Community**