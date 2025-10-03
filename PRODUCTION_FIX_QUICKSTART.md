# 🚀 PRODUCTION SERVER FIX GUIDE
**Server:** 139.84.163.11  
**Issues:** rental_management field error + commission_ax menu references

---

## 📋 Overview

You have **TWO issues** to fix:
1. **rental_management**: `is_extra_service` field error (blocking Odoo startup)
2. **commission_ax**: Menu reference errors (External ID not found)

**Time Required:** ~10-15 minutes  
**Risk Level:** Low (we'll create backups)

---

## ⚡ QUICK FIX (Copy & Paste)

### Connect to your server:
```bash
ssh root@139.84.163.11
```
*Enter your password when prompted*

---

### Then copy/paste this ENTIRE block:

```bash
echo "🔧 Starting Production Fix..."
echo ""

# Fix 1: Reinstall rental_management
echo "📦 Step 1: Fixing rental_management module..."
su - odoo -c '/var/odoo/properties/src/odoo-bin -c /etc/odoo/odoo.conf -d properties -u rental_management --stop-after-init' 2>&1 | tail -20
echo "✅ rental_management fixed!"
echo ""

# Fix 2: Navigate to commission_ax
echo "📁 Step 2: Navigating to commission_ax views..."
cd /var/odoo/properties/extra-addons/odoo17_final.git-6880b7fcd4844/commission_ax/views
pwd
echo ""

# Create backup
echo "💾 Step 3: Creating backup..."
BACKUP_DIR="/tmp/backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR
cp *.xml $BACKUP_DIR/
echo "Backup created at: $BACKUP_DIR"
ls -lh $BACKUP_DIR/
echo ""

# Fix XML files
echo "✏️  Step 4: Fixing XML files..."
sed -i 's/parent="commission_ax\.menu_commission_reports"/parent="menu_commission_reports"/g' commission_profit_analysis_wizard_views.xml commission_partner_statement_wizard_views.xml
sed -i 's/action="commission_ax\.action_commission_profit_analysis_wizard"/action="action_commission_profit_analysis_wizard"/g' commission_profit_analysis_wizard_views.xml
sed -i 's/action="commission_ax\.action_commission_partner_statement_wizard"/action="action_commission_partner_statement_wizard"/g' commission_partner_statement_wizard_views.xml
sed -i 's/parent="commission_ax\.commission_menu"/parent="commission_menu"/g' commission_type_views.xml
sed -i 's/action="commission_ax\.action_commission_type"/action="action_commission_type"/g' commission_type_views.xml
echo "✅ XML files fixed!"
echo ""

# Verify changes
echo "🔍 Step 5: Verifying changes..."
echo "Found correct references:"
grep -n 'parent="menu_commission_reports"' commission_profit_analysis_wizard_views.xml || echo "None"
grep -n 'parent="commission_menu"' commission_type_views.xml || echo "None"
echo ""

# Update commission_ax
echo "📦 Step 6: Updating commission_ax module..."
su - odoo -c '/var/odoo/properties/src/odoo-bin -c /etc/odoo/odoo.conf -d properties -u commission_ax --stop-after-init' 2>&1 | tail -20
echo "✅ commission_ax updated!"
echo ""

# Restart Odoo
echo "🔄 Step 7: Restarting Odoo service..."
systemctl restart odoo
sleep 10
echo ""

# Check status
echo "📊 Step 8: Checking Odoo status..."
systemctl status odoo --no-pager -l | head -20
echo ""

# Check for errors
echo "🔍 Step 9: Checking logs for errors..."
echo "Recent errors (if any):"
tail -50 /var/log/odoo/odoo-server.log | grep -E "ERROR|CRITICAL" | tail -10 || echo "No recent errors found!"
echo ""

echo "================================================"
echo "✅ PRODUCTION FIX COMPLETE!"
echo "================================================"
echo ""
echo "Backup location: $BACKUP_DIR"
echo ""
echo "Next steps:"
echo "1. Open your Odoo web interface"
echo "2. Go to Sales → Commissions"
echo "3. Test the commission menus and wizards"
echo ""
```

---

## 🔄 If Something Goes Wrong

### Restore from backup:
```bash
cd /var/odoo/properties/extra-addons/odoo17_final.git-6880b7fcd4844/commission_ax/views
cp /tmp/backup_YYYYMMDD_HHMMSS/*.xml .
systemctl restart odoo
```

### View live logs:
```bash
tail -f /var/log/odoo/odoo-server.log
```
Press `Ctrl+C` to stop

### Restart Odoo if needed:
```bash
systemctl restart odoo
systemctl status odoo
```

---

## 📝 What This Script Does

1. **Fixes rental_management**: Reinstalls the module to properly load all field definitions
2. **Creates backup**: Saves all XML files to `/tmp/backup_TIMESTAMP/`
3. **Fixes commission_ax XMLs**: Removes incorrect `commission_ax.` prefixes from menu references
4. **Updates module**: Applies the XML changes to Odoo database
5. **Restarts Odoo**: Reloads all modules with the fixes
6. **Verifies**: Checks status and logs for any remaining errors

---

## ✅ Success Indicators

After running the script, you should see:
- ✅ "rental_management fixed!"
- ✅ "commission_ax updated!"
- ✅ Odoo status shows "active (running)"
- ✅ No "ERROR" or "CRITICAL" in recent logs
- ✅ Commission menus work in web interface

---

## 🆘 Need Help?

If you see errors after running the script, share:
1. The output from the script
2. Last 50 lines from logs: `tail -50 /var/log/odoo/odoo-server.log`

---

**Ready?** Just copy the big block above and paste it into your SSH session! 🚀
