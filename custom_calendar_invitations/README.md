# Custom Calendar Invitations for Odoo 17

## Overview

This module enhances Odoo's default calendar invitation emails with professional branding, improved Google Calendar integration, and a better user experience. It completely overrides the standard calendar invitation template with a modern, responsive design that includes one-click calendar integration.

## Features

### 🎨 **Professional Design**
- Modern, responsive email template
- Custom OSUS branding (#722F37 color scheme)
- Visual calendar widget showing event date
- Clean, mobile-friendly layout

### 📅 **Enhanced Google Calendar Integration**
- Properly encoded URLs for special characters
- Complete event data population (title, description, location, organizer)
- Automatic timezone handling
- Video call links included in calendar events

### 🔗 **Multiple Calendar Options**
- One-click "Add to Google Calendar" button
- ICS file download for other calendar applications
- Proper event metadata for calendar apps

### 📧 **Improved User Experience**
- RSVP buttons (Accept/Decline/Maybe) directly in email
- Location with Google Maps integration
- Video call links prominently displayed
- Organizer information and signatures
- Event duration and recurrence details

### 🛠️ **Technical Enhancements**
- Proper URL encoding for international characters
- Error handling and logging
- Multi-language support
- Timezone-aware formatting
- HTML email compatibility

## Installation

### Method 1: Through Odoo Apps (Recommended)

1. **Copy Module**: Place the `custom_calendar_invitations` folder in your Odoo addons directory:
   ```
   /mnt/extra-addons/custom_calendar_invitations/
   ```

2. **Update Apps List**: In Odoo, go to Apps > Update Apps List

3. **Install Module**: Search for "Custom Calendar Invitations" and click Install

### Method 2: Command Line Installation

```bash
# Update module list
docker-compose exec odoo odoo --update=all --stop-after-init

# Or install specific module
docker-compose exec odoo odoo -i custom_calendar_invitations --stop-after-init
```

## Usage

Once installed, the module automatically enhances all calendar invitations:

### Creating Enhanced Invitations

1. **Create Calendar Event**: Use the standard Odoo Calendar app
2. **Add Event Details**:
   - Title and description
   - Date/time and timezone
   - Location (will link to Google Maps)
   - Video call URL (if applicable)
   - Attendees

3. **Send Invitations**: Click the "Send Invitations" button
4. **Recipients Receive**: Professional emails with enhanced integration

### What Recipients See

Recipients will receive emails with:
- Professional branded header
- Visual calendar widget with event date
- One-click "Add to Google Calendar" button
- ICS file download option
- Event details clearly formatted
- RSVP buttons for quick responses
- Location with map link
- Video call access (if provided)

## Configuration

### Customizing the Template

To modify the email template design:

1. Go to **Settings > Technical > Email Templates**
2. Find "Calendar: Meeting Invitation (Enhanced)"
3. Modify the HTML content as needed
4. Save changes

### Changing Brand Colors

To customize the color scheme, edit the template and replace:
- `#722F37` (primary brand color)
- `#8B1538` (darker variant)
- `#5a1f2a` (darkest variant)

### Adding Company Logo

Add your company logo by modifying the header section in the template:
```html
<img src="/web/image/res.company/1/logo" alt="Company Logo" style="max-height: 50px;">
```

## Technical Details

### Files Structure
```
custom_calendar_invitations/
├── __init__.py                    # Module initialization
├── __manifest__.py               # Module definition
├── models/
│   ├── __init__.py              # Models initialization
│   └── calendar_event.py        # Enhanced calendar event model
├── data/
│   └── calendar_templates.xml   # Email template definitions
├── security/
│   └── ir.model.access.csv      # Access rights
└── README.md                    # This documentation
```

### Key Components

#### 1. Enhanced Calendar Event Model (`models/calendar_event.py`)
- Extends `calendar.event` with Google Calendar URL generation
- Improves invitation sending with proper error handling
- Adds timezone support and ICS file enhancements

#### 2. Custom Email Template (`data/calendar_templates.xml`)
- Professional HTML email template
- Responsive design for mobile and desktop
- Dynamic content population with proper escaping

#### 3. Google Calendar URL Generation
Generates properly formatted URLs like:
```
https://calendar.google.com/calendar/render?
action=TEMPLATE&
text=Meeting%20Title&
dates=20250504T110000Z/20250504T113000Z&
location=Meeting%20Location&
details=Meeting%20description...
```

### Dependencies
- `base`: Core Odoo functionality
- `calendar`: Calendar event management
- `mail`: Email template system

## Troubleshooting

### Common Issues

#### 1. Template Not Loading
**Problem**: Custom template doesn't appear
**Solution**: 
- Check module installation
- Verify data files are loaded
- Update module if needed

#### 2. Google Calendar Link Not Working
**Problem**: "Add to Google Calendar" button doesn't work
**Solution**:
- Check URL encoding in template
- Verify event data is properly populated
- Test with simple event first

#### 3. Timezone Issues
**Problem**: Times showing incorrectly in emails
**Solution**:
- Check user timezone settings
- Verify event timezone configuration
- Ensure proper timezone context in template

#### 4. RSVP Buttons Not Working
**Problem**: Accept/Decline buttons don't respond
**Solution**:
- Verify access tokens are generated
- Check calendar app configuration
- Ensure proper URL generation

### Debug Steps

1. **Check Email Templates**:
   ```
   Settings > Technical > Email Templates
   Search: "Calendar: Meeting Invitation"
   ```

2. **Test Template**:
   - Create simple test event
   - Add yourself as attendee
   - Send invitation and check email

3. **Check Logs**:
   ```bash
   docker-compose logs -f odoo | grep calendar
   ```

4. **Verify Module Installation**:
   ```
   Apps > Custom Calendar Invitations
   Should show "Installed"
   ```

## Advanced Customization

### Adding Custom Fields

To include custom event fields in emails:

1. **Extend the Model**:
```python
class CalendarEvent(models.Model):
    _inherit = 'calendar.event'
    
    custom_field = fields.Char('Custom Field')
```

2. **Update Template**:
```xml
<t t-if="object.custom_field">
    <div>Custom: <t t-out="object.custom_field"/></div>
</t>
```

### Multiple Template Support

To create different templates for different event types:

1. **Create Additional Templates** in `data/calendar_templates.xml`
2. **Add Selection Logic** in the model to choose templates
3. **Implement Conditional Logic** based on event properties

### Integration with Other Modules

The module can be extended to integrate with:
- CRM (include lead/opportunity information)
- Project (add project context to meetings)
- HR (employee-specific meeting templates)
- Website (public event invitations)

## Support and Maintenance

### Updating the Module

To update after making changes:
```bash
docker-compose exec odoo odoo -u custom_calendar_invitations --stop-after-init
```

### Backup Considerations

The module modifies core calendar functionality, so ensure:
- Regular database backups
- Test changes in development environment
- Document any customizations

## License

This module is licensed under LGPL-3, compatible with Odoo's licensing requirements.

## Contributing

To contribute improvements:
1. Test changes thoroughly
2. Follow Odoo development guidelines
3. Document any modifications
4. Consider backward compatibility

## Version History

- **v17.0.1.0.0**: Initial release
  - Professional email template
  - Enhanced Google Calendar integration
  - RSVP functionality
  - Mobile-responsive design
  - Multi-language support

---

**Need Help?** Contact the OSUS Development Team for support with customization or troubleshooting.