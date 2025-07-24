# Automated Employee Announcements

## Description
This module provides comprehensive automated email notifications for employee events and sales activities. It includes:

- **Employee birthday announcements** with beautiful HTML templates
- **Work anniversary celebrations** with years of service tracking  
- **Sales order notifications** to agents for invoicing, payments, and reminders
- **Flexible rule-based system** for customizable automation
- **Integration with HR and Sales modules** for seamless workflow

## Key Features

### 🎉 Employee Celebrations
- Automated birthday announcements with customizable templates
- Work anniversary notifications with service year calculations
- Option to send to individual employees or company-wide
- Manual send options from employee records
- Beautiful, responsive HTML email templates

### 📊 Sales Automation
- Invoice creation notifications to sales agents
- Payment confirmation alerts
- Deal status reminders for overdue quotations (30+ days)
- Rich HTML templates with company branding

### ⚙️ Advanced Configuration
- Rule-based automation system
- Customizable days-before notifications
- Template management and customization
- Cron job scheduling and monitoring
- Comprehensive logging and tracking

## Installation

1. **Prerequisites**: Ensure the following modules are installed:
   - `hr` (Human Resources)
   - `sale_management` (Sales Management)
   - `mail` (Messaging)
   - `account` (Accounting)

2. **Install Module**:
   ```bash
   # Copy module to addons directory
   cp -r automated_employee_announce /path/to/odoo/addons/
   
   # Restart Odoo and update apps list
   # Install from Apps menu
   ```

3. **Configure Mail Server**: Ensure outgoing mail server is properly configured in Settings > Technical > Email

## Configuration

### Employee Setup
1. Navigate to **HR > Employees**
2. Ensure each employee has:
   - Valid work email address
   - Birthday date (for birthday announcements)
   - Joining date (for anniversary announcements)

### Mail Rules Configuration
1. Go to **HR > Employee Announcements > Mail Rules**
2. Configure or create new rules:
   - **Rule Type**: Birthday or Work Anniversary
   - **Template**: Select appropriate mail template
   - **Send to All**: Choose individual or company-wide notifications
   - **Days Before**: Set advance notification (0 = on the day)
   - **Active**: Enable/disable rule

### Sales Agent Configuration
For sales notifications, ensure sale orders have:
- `agent1_partner_id` field populated
- Valid partner, buyer, project, and unit information
- Proper booking dates

## Usage

### Automated Operations
- **Daily Cron Jobs**: Automatically run at scheduled times
- **Event Triggers**: Sales notifications sent on invoice/payment events
- **Rule Execution**: All active rules processed daily

### Manual Operations
- **Test Rules**: Use "Test Rule" button in rule configuration
- **Manual Wishes**: Send birthday/anniversary wishes from employee record
- **Immediate Execution**: Run specific rules on demand

### Monitoring
- **Rule Statistics**: Track emails sent and execution history
- **Chatter Integration**: All activities logged in relevant records
- **Error Handling**: Comprehensive logging and error reporting

## Technical Details

### Models
- `automated.mail.rule`: Core automation rules
- `hr.employee`: Extended with anniversary fields and actions
- `sale.order`: Enhanced with agent notification triggers
- `account.move`: Payment notification integration

### Scheduled Actions
- `Automated Mail Rules`: Daily execution of all active rules
- `Birthday Announcements`: Employee birthday notifications
- `Anniversary Announcements`: Work anniversary notifications  
- `Deal Status Reminders`: Overdue quotation follow-ups

### Security
- Role-based access control
- HR User permissions for rule viewing
- HR Manager permissions for rule management
- Automatic user assignment for cron jobs

## Customization

### Email Templates
Templates can be customized in **Settings > Technical > Email Templates**:
- `Employee Birthday Announcement`
- `Employee Work Anniversary Announcement`
- `Sale Order Invoiced - Agent Notification`
- `Sale Order Deal Status Reminder`
- `Sale Order Payment Initiated`

### Rule Types
Extend the system by adding new rule types in the model:
```python
rule_type = fields.Selection([
    ('birthday', 'Birthday'),
    ('work_anniversary', 'Work Anniversary'),
    ('custom_event', 'Custom Event'),  # Add your type
], ...)
```

## Troubleshooting

### Common Issues
1. **Emails not sending**:
   - Check mail server configuration
   - Verify employee email addresses
   - Review cron job execution logs

2. **Missing notifications**:
   - Ensure rules are active
   - Check date fields on employee records
   - Verify template assignments

3. **Sales notifications not working**:
   - Confirm `agent1_partner_id` is set
   - Check partner email addresses
   - Review sale order states

### Debugging
- Enable developer mode for detailed logging
- Check **Settings > Technical > Scheduled Actions** for cron status
- Review mail logs in **Settings > Technical > Email > Emails**

## Testing

Run comprehensive tests:
```bash
# Run all tests
odoo --test-enable -i automated_employee_announce --stop-after-init

# Run specific test
python -m pytest tests/test_automated_mails.py -v
```

## Support & Maintenance

### Performance Optimization
- Rules execute efficiently with optimized queries
- Email sending uses Odoo's queue system
- Minimal database overhead with smart caching

### Version Compatibility
- Designed for Odoo 17.0
- Backward compatible with minor version updates
- Migration guides available for major upgrades

## License
LGPL-3 - See LICENSE file for details

## Credits
Developed for enhanced employee engagement and sales process automation.
