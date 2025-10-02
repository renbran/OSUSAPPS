# 🚀 PRODUCTION DEPLOYMENT GUIDE - commission_ax Fix

## 📋 Overview

**Issue**: Production server has old code with incorrect module prefix  
**Location**: `/var/odoo/properties/` on Vultr server  
**Database**: `properties`  
**Status**: ✅ Fix ready for deployment

---

## 🎯 What Needs to be Fixed

### Files to Update
1. `commission_profit_analysis_wizard_views.xml` (line 52)
2. `commission_partner_statement_wizard_views.xml` (line 64)
3. `commission_type_views.xml` (line 78)

### Changes Required
Remove `commission_ax.` prefix from internal menu/action references:
- `commission_ax.menu_commission_reports` → `menu_commission_reports`
- `commission_ax.action_*` → `action_*`
- `commission_ax.commission_menu` → `commission_menu`

---

## 🔧 Deployment Methods

### Method 1: Automated Script (RECOMMENDED) ⭐

This is the fastest and safest method.

#### Step 1: Create the Fix Script on Production

```bash
# SSH to production server
ssh root@your-vultr-server-ip

# Create deployment script
cat > /tmp/fix_commission_ax.sh << 'EOF'
#!/bin/bash
set -e

echo "🚀 Starting commission_ax deployment fix..."

# Configuration
MODULE_PATH="/var/odoo/properties/extra-addons/odoo17_final.git-6880b7fcd4844/commission_ax"
VIEWS_PATH="${MODULE_PATH}/views"
BACKUP_DIR="/tmp/commission_ax_backup_$(date +%Y%m%d_%H%M%S)"

# Create backup
echo "📦 Creating backup..."
mkdir -p "${BACKUP_DIR}"
cp -r "${VIEWS_PATH}" "${BACKUP_DIR}/"
echo "✅ Backup created at: ${BACKUP_DIR}"

# Navigate to views directory
cd "${VIEWS_PATH}"

# Fix commission_profit_analysis_wizard_views.xml
echo "🔧 Fixing commission_profit_analysis_wizard_views.xml..."
sed -i 's/parent="commission_ax\.menu_commission_reports"/parent="menu_commission_reports"/g' commission_profit_analysis_wizard_views.xml
sed -i 's/action="commission_ax\.action_commission_profit_analysis_wizard"/action="action_commission_profit_analysis_wizard"/g' commission_profit_analysis_wizard_views.xml

# Fix commission_partner_statement_wizard_views.xml
echo "🔧 Fixing commission_partner_statement_wizard_views.xml..."
sed -i 's/parent="commission_ax\.menu_commission_reports"/parent="menu_commission_reports"/g' commission_partner_statement_wizard_views.xml
sed -i 's/action="commission_ax\.action_commission_partner_statement_wizard"/action="action_commission_partner_statement_wizard"/g' commission_partner_statement_wizard_views.xml

# Fix commission_type_views.xml
echo "🔧 Fixing commission_type_views.xml..."
sed -i 's/parent="commission_ax\.commission_menu"/parent="commission_menu"/g' commission_type_views.xml
sed -i 's/action="commission_ax\.action_commission_type"/action="action_commission_type"/g' commission_type_views.xml

# Verify changes
echo ""
echo "📋 Verifying changes..."
echo "Checking for remaining 'commission_ax.' prefixes in views:"
if grep -r "commission_ax\." *.xml | grep -E "(parent=|action=)" ; then
    echo "⚠️  Warning: Some commission_ax prefixes still found!"
else
    echo "✅ No commission_ax prefixes found - files are clean!"
fi

echo ""
echo "✅ Files updated successfully!"
echo ""
echo "📁 Backup location: ${BACKUP_DIR}"
echo ""
echo "🔄 Next steps:"
echo "1. Update the module: su - odoo -c '/var/odoo/properties/src/odoo-bin -c /etc/odoo/odoo.conf -d properties -u commission_ax --stop-after-init'"
echo "2. Restart Odoo: systemctl restart odoo"
echo "3. Check logs: journalctl -u odoo -f"
EOF

# Make script executable
chmod +x /tmp/fix_commission_ax.sh

# Run the script
/tmp/fix_commission_ax.sh
```

#### Step 2: Update the Module

```bash
# Switch to odoo user and update module
su - odoo
/var/odoo/properties/src/odoo-bin -c /etc/odoo/odoo.conf -d properties -u commission_ax --stop-after-init

# Exit back to root
exit
```

#### Step 3: Restart Odoo Service

```bash
# Restart Odoo
systemctl restart odoo

# Monitor logs for errors
journalctl -u odoo -f
```

Press `Ctrl+C` when you see no errors and service is running.

---

### Method 2: Manual File Editing

If you prefer to edit files manually:

#### Step 1: Backup Files

```bash
ssh root@your-vultr-server-ip

# Create backup
cd /var/odoo/properties/extra-addons/odoo17_final.git-6880b7fcd4844/commission_ax/views
cp commission_profit_analysis_wizard_views.xml commission_profit_analysis_wizard_views.xml.bak
cp commission_partner_statement_wizard_views.xml commission_partner_statement_wizard_views.xml.bak
cp commission_type_views.xml commission_type_views.xml.bak
```

#### Step 2: Edit Files

**File 1: commission_profit_analysis_wizard_views.xml (Line 52)**

```bash
nano commission_profit_analysis_wizard_views.xml
```

Find line 52 and change:
```xml
<!-- BEFORE -->
<menuitem id="menu_commission_profit_analysis" name="Profit Analysis Report" parent="commission_ax.menu_commission_reports" action="commission_ax.action_commission_profit_analysis_wizard" sequence="20"/>

<!-- AFTER -->
<menuitem id="menu_commission_profit_analysis" name="Profit Analysis Report" parent="menu_commission_reports" action="action_commission_profit_analysis_wizard" sequence="20"/>
```

**File 2: commission_partner_statement_wizard_views.xml (Line 64)**

```bash
nano commission_partner_statement_wizard_views.xml
```

Find line 64 and change:
```xml
<!-- BEFORE -->
<menuitem id="menu_commission_partner_statement_wizard" name="Partner Statement Report" parent="commission_ax.menu_commission_reports" action="commission_ax.action_commission_partner_statement_wizard" sequence="20"/>

<!-- AFTER -->
<menuitem id="menu_commission_partner_statement_wizard" name="Partner Statement Report" parent="menu_commission_reports" action="action_commission_partner_statement_wizard" sequence="20"/>
```

**File 3: commission_type_views.xml (Line 78)**

```bash
nano commission_type_views.xml
```

Find line 78 and change:
```xml
<!-- BEFORE -->
<menuitem id="menu_commission_type" name="Commission Types" parent="commission_ax.commission_menu" action="commission_ax.action_commission_type" sequence="10"/>

<!-- AFTER -->
<menuitem id="menu_commission_type" name="Commission Types" parent="commission_menu" action="action_commission_type" sequence="10"/>
```

#### Step 3: Update and Restart

Same as Method 1 Steps 2-3.

---

### Method 3: Git Deployment

If your production pulls from Git:

#### Step 1: Commit Changes to Git (Local)

```bash
# On your local Windows machine
cd "d:/GitHub/osus_main/cleanup osus/OSUSAPPS"

# Stage changes
git add commission_ax/views/commission_profit_analysis_wizard_views.xml
git add commission_ax/views/commission_partner_statement_wizard_views.xml
git add commission_ax/views/commission_type_views.xml

# Commit
git commit -m "Fix: Remove incorrect module prefix from commission_ax internal menu references

- Remove commission_ax. prefix from menu_commission_reports parent
- Remove commission_ax. prefix from action references
- Fix commission_menu parent reference
- Resolves ParseError: External ID not found"

# Push to repository
git push origin main
```

#### Step 2: Pull on Production Server

```bash
# SSH to production
ssh root@your-vultr-server-ip

# Navigate to module directory
cd /var/odoo/properties/extra-addons/odoo17_final.git-6880b7fcd4844

# Backup current state
git stash

# Pull latest changes
git pull origin main

# Update module
su - odoo -c '/var/odoo/properties/src/odoo-bin -c /etc/odoo/odoo.conf -d properties -u commission_ax --stop-after-init'

# Restart Odoo
systemctl restart odoo

# Monitor logs
journalctl -u odoo -f
```

---

## ✅ Verification Steps

### 1. Check File Changes

```bash
cd /var/odoo/properties/extra-addons/odoo17_final.git-6880b7fcd4844/commission_ax/views

# Verify no commission_ax prefix in parent/action attributes
grep -n "commission_ax\." commission_profit_analysis_wizard_views.xml | grep -E "(parent=|action=)"
grep -n "commission_ax\." commission_partner_statement_wizard_views.xml | grep -E "(parent=|action=)"
grep -n "commission_ax\." commission_type_views.xml | grep -E "(parent=|action=)"
```

**Expected**: No output (no matches found)

### 2. Check Odoo Logs

```bash
# Check for ParseError
journalctl -u odoo --since "5 minutes ago" | grep -i "parseerror"

# Check for External ID error
journalctl -u odoo --since "5 minutes ago" | grep -i "external id not found"

# Check module loading
journalctl -u odoo --since "5 minutes ago" | grep "commission_ax"
```

**Expected**: 
- No ParseError
- No "External ID not found"
- Module loads successfully

### 3. Check Odoo Service Status

```bash
systemctl status odoo
```

**Expected**: Active (running) status

### 4. Test in Odoo Web Interface

1. Open browser to your production URL
2. Login as admin
3. Navigate to **Sales → Commissions**
4. Verify menu structure:
   - ✅ Commission Lines menu visible
   - ✅ Configuration → Commission Types accessible
   - ✅ Commission Reports → Profit Analysis Report accessible
   - ✅ Commission Reports → Partner Statement Report accessible
5. Open each wizard to confirm no errors

---

## 🔄 Rollback Procedure

If something goes wrong:

### Method 1: Restore from Backup

```bash
# Find your backup
ls -la /tmp/commission_ax_backup_*

# Restore files
cp -r /tmp/commission_ax_backup_YYYYMMDD_HHMMSS/views/* /var/odoo/properties/extra-addons/odoo17_final.git-6880b7fcd4844/commission_ax/views/

# Restart Odoo
systemctl restart odoo
```

### Method 2: Git Revert (if using Git)

```bash
cd /var/odoo/properties/extra-addons/odoo17_final.git-6880b7fcd4844

# Revert to previous commit
git revert HEAD

# Update module
su - odoo -c '/var/odoo/properties/src/odoo-bin -c /etc/odoo/odoo.conf -d properties -u commission_ax --stop-after-init'

# Restart
systemctl restart odoo
```

---

## 📊 Expected Results

### Before Fix
```
❌ ParseError: External ID not found: commission_ax.commission_menu_reports
❌ Database initialization fails
❌ Commission menus not accessible
```

### After Fix
```
✅ No ParseError
✅ Module loads successfully
✅ All commission menus accessible
✅ Wizards open without errors
✅ Database initializes properly
```

---

## 🚨 Troubleshooting

### Issue: "Permission denied" when editing files

**Solution**:
```bash
# Ensure you're root or use sudo
sudo su -
```

### Issue: Module update fails

**Solution**:
```bash
# Check Odoo is not running
systemctl stop odoo

# Run update again
su - odoo -c '/var/odoo/properties/src/odoo-bin -c /etc/odoo/odoo.conf -d properties -u commission_ax --stop-after-init'

# Start Odoo
systemctl start odoo
```

### Issue: Changes not taking effect

**Solution**:
```bash
# Clear Odoo cache
rm -rf /var/odoo/properties/.local/share/Odoo/sessions/*

# Update module with init
su - odoo -c '/var/odoo/properties/src/odoo-bin -c /etc/odoo/odoo.conf -d properties -i commission_ax --stop-after-init'

# Restart
systemctl restart odoo
```

### Issue: Database still shows old menus

**Solution**:
```bash
# Update module list from Odoo shell
su - odoo
/var/odoo/properties/src/odoo-bin shell -c /etc/odoo/odoo.conf -d properties

# In Odoo shell:
>>> env['ir.module.module'].update_list()
>>> env.cr.commit()
>>> exit()

# Restart
exit
systemctl restart odoo
```

---

## 📝 Deployment Checklist

- [ ] **Pre-deployment**
  - [ ] Backup production database
  - [ ] Backup module files
  - [ ] Notify users of maintenance window
  - [ ] Check current Odoo status

- [ ] **Deployment**
  - [ ] SSH to production server
  - [ ] Run fix script or manual edits
  - [ ] Verify file changes
  - [ ] Update commission_ax module
  - [ ] Restart Odoo service

- [ ] **Post-deployment**
  - [ ] Check Odoo service status
  - [ ] Review logs for errors
  - [ ] Test commission menus
  - [ ] Test wizards functionality
  - [ ] Verify no ParseError in logs
  - [ ] Notify users maintenance complete

- [ ] **Documentation**
  - [ ] Document deployment time
  - [ ] Note any issues encountered
  - [ ] Update change log
  - [ ] Archive backup location

---

## 📞 Support Commands

### Check Odoo Version
```bash
/var/odoo/properties/src/odoo-bin --version
```

### Check Module Status
```bash
# From Odoo shell
su - odoo
/var/odoo/properties/src/odoo-bin shell -c /etc/odoo/odoo.conf -d properties
>>> env['ir.module.module'].search([('name','=','commission_ax')]).state
>>> exit()
```

### View Recent Errors
```bash
journalctl -u odoo --since "1 hour ago" -p err
```

### Check Database Connection
```bash
su - odoo
psql -U odoo -d properties -c "SELECT count(*) FROM ir_module_module WHERE name='commission_ax';"
```

---

## 🎯 Quick Commands Summary

```bash
# Full deployment in one go
ssh root@your-vultr-server-ip << 'ENDSSH'
cd /var/odoo/properties/extra-addons/odoo17_final.git-6880b7fcd4844/commission_ax/views
cp commission_profit_analysis_wizard_views.xml{,.bak}
cp commission_partner_statement_wizard_views.xml{,.bak}
cp commission_type_views.xml{,.bak}
sed -i 's/parent="commission_ax\.menu_commission_reports"/parent="menu_commission_reports"/g' commission_profit_analysis_wizard_views.xml
sed -i 's/action="commission_ax\.action_commission_profit_analysis_wizard"/action="action_commission_profit_analysis_wizard"/g' commission_profit_analysis_wizard_views.xml
sed -i 's/parent="commission_ax\.menu_commission_reports"/parent="menu_commission_reports"/g' commission_partner_statement_wizard_views.xml
sed -i 's/action="commission_ax\.action_commission_partner_statement_wizard"/action="action_commission_partner_statement_wizard"/g' commission_partner_statement_wizard_views.xml
sed -i 's/parent="commission_ax\.commission_menu"/parent="commission_menu"/g' commission_type_views.xml
sed -i 's/action="commission_ax\.action_commission_type"/action="action_commission_type"/g' commission_type_views.xml
su - odoo -c '/var/odoo/properties/src/odoo-bin -c /etc/odoo/odoo.conf -d properties -u commission_ax --stop-after-init'
systemctl restart odoo
ENDSSH
```

---

**Deployment Guide Version**: 1.0  
**Last Updated**: October 2, 2025  
**Related Docs**: `COMMISSION_AX_MENU_FIX_FINAL.md`, `ODOO_MODULE_PREFIX_QUICK_REF.md`

🎉 **Good luck with your deployment!**