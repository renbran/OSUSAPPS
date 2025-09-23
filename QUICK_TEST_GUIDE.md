# 🚀 Quick Installation Test Guide

## Step 1: Verify Module is Ready
```bash
cd "d:\GitHub\osus_main\cleanup osus\OSUSAPPS"
ls -la custom_calendar_invitations/
```
**Expected**: You should see all module files listed.

## Step 2: Start Odoo (if not running)
```bash
docker-compose up -d
```
**Wait**: 2-3 minutes for containers to start.

## Step 3: Check Odoo is Running
```bash
docker-compose ps
```
**Expected**: Odoo and database containers should be "Up".

## Step 4: Install Module via Command Line
```bash
# Quick install test
docker-compose exec odoo odoo -i custom_calendar_invitations --stop-after-init -d odoo

# Or with test mode for more validation
docker-compose exec odoo odoo -i custom_calendar_invitations --test-enable --stop-after-init -d odoo --log-level=info
```

## Step 5: Check Installation Success
```bash
# Check logs for errors
docker-compose logs odoo | grep -i "custom_calendar"

# Or check all recent logs
docker-compose logs --tail=50 odoo
```

## Step 6: Access Odoo Web Interface
1. Open browser: http://localhost:8069
2. Login with admin credentials
3. Go to **Apps** menu
4. Search for "Custom Calendar"
5. Should show as "Installed" ✅

## Step 7: Test Email Template
1. Go to **Settings > Technical > Email Templates**
2. Search for "Calendar: Meeting Invitation"
3. Should see "Calendar: Meeting Invitation (Enhanced)"
4. Preview the template ✅

## Step 8: Create Test Event
1. Go to **Calendar** app
2. Create new event with:
   - Title: "Test Meeting"
   - Date/Time: Any future date
   - Add an attendee (your email)
3. Click "Send Invitations"
4. Check your email for the enhanced template ✅

## ✅ Success Indicators:
- No error messages in logs
- Module shows as "Installed" in Apps
- Enhanced email template exists
- Test invitation email uses new design
- Google Calendar button works

## ❌ Troubleshooting:
- **Container errors**: Check `docker-compose logs`
- **Module not found**: Verify files in `/mnt/extra-addons/`
- **Template issues**: Restart Odoo after installation
- **Permission errors**: Check security settings

---
**Quick Test**: The module is ready for installation testing!