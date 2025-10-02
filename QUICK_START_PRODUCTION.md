# 🚀 QUICK START - Production Deployment

## 📋 3-Minute Deployment

### Option A: Automated Script (Recommended) ⭐

**Step 1: Copy script to server**
```bash
# From your local machine
scp fix_commission_ax_production.sh root@your-server-ip:/tmp/

# OR manually create on server
ssh root@your-server-ip
cat > /tmp/fix_commission_ax.sh << 'EOF'
[paste the script content from fix_commission_ax_production.sh]
EOF
chmod +x /tmp/fix_commission_ax.sh
```

**Step 2: Run the script**
```bash
# SSH to server
ssh root@your-server-ip

# Run script
/tmp/fix_commission_ax.sh
```

**Step 3: Press Enter when prompted**

The script will automatically:
- ✅ Backup files
- ✅ Fix all 3 XML files
- ✅ Update module
- ✅ Restart Odoo
- ✅ Verify deployment

---

### Option B: One-Line Command 🚀

Copy and paste this entire command (replace `your-server-ip` with actual IP):

```bash
ssh root@your-server-ip 'bash -s' << 'ENDSSH'
cd /var/odoo/properties/extra-addons/odoo17_final.git-6880b7fcd4844/commission_ax/views &&
mkdir -p /tmp/backup_$(date +%Y%m%d_%H%M%S) &&
cp *.xml /tmp/backup_$(date +%Y%m%d_%H%M%S)/ &&
sed -i "s/parent=\"commission_ax\.menu_commission_reports\"/parent=\"menu_commission_reports\"/g" commission_profit_analysis_wizard_views.xml &&
sed -i "s/action=\"commission_ax\.action_commission_profit_analysis_wizard\"/action=\"action_commission_profit_analysis_wizard\"/g" commission_profit_analysis_wizard_views.xml &&
sed -i "s/parent=\"commission_ax\.menu_commission_reports\"/parent=\"menu_commission_reports\"/g" commission_partner_statement_wizard_views.xml &&
sed -i "s/action=\"commission_ax\.action_commission_partner_statement_wizard\"/action=\"action_commission_partner_statement_wizard\"/g" commission_partner_statement_wizard_views.xml &&
sed -i "s/parent=\"commission_ax\.commission_menu\"/parent=\"commission_menu\"/g" commission_type_views.xml &&
sed -i "s/action=\"commission_ax\.action_commission_type\"/action=\"action_commission_type\"/g" commission_type_views.xml &&
echo "Files fixed!" &&
su - odoo -c "/var/odoo/properties/src/odoo-bin -c /etc/odoo/odoo.conf -d properties -u commission_ax --stop-after-init" &&
systemctl restart odoo &&
echo "✅ Deployment complete!"
ENDSSH
```

---

### Option C: Manual (5 minutes)

```bash
# 1. SSH to server
ssh root@your-server-ip

# 2. Navigate to views folder
cd /var/odoo/properties/extra-addons/odoo17_final.git-6880b7fcd4844/commission_ax/views

# 3. Backup
cp commission_profit_analysis_wizard_views.xml{,.bak}
cp commission_partner_statement_wizard_views.xml{,.bak}
cp commission_type_views.xml{,.bak}

# 4. Fix files
sed -i 's/parent="commission_ax\.menu_commission_reports"/parent="menu_commission_reports"/g' commission_profit_analysis_wizard_views.xml
sed -i 's/action="commission_ax\.action_commission_profit_analysis_wizard"/action="action_commission_profit_analysis_wizard"/g' commission_profit_analysis_wizard_views.xml

sed -i 's/parent="commission_ax\.menu_commission_reports"/parent="menu_commission_reports"/g' commission_partner_statement_wizard_views.xml
sed -i 's/action="commission_ax\.action_commission_partner_statement_wizard"/action="action_commission_partner_statement_wizard"/g' commission_partner_statement_wizard_views.xml

sed -i 's/parent="commission_ax\.commission_menu"/parent="commission_menu"/g' commission_type_views.xml
sed -i 's/action="commission_ax\.action_commission_type"/action="action_commission_type"/g' commission_type_views.xml

# 5. Update module
su - odoo -c '/var/odoo/properties/src/odoo-bin -c /etc/odoo/odoo.conf -d properties -u commission_ax --stop-after-init'

# 6. Restart
systemctl restart odoo

# 7. Check logs
journalctl -u odoo -f
```

---

## ✅ Quick Verification

```bash
# Check for errors
journalctl -u odoo --since "2 minutes ago" | grep -i "parseerror"

# Should return nothing (no errors)

# Check service
systemctl status odoo

# Should show "active (running)"
```

---

## 🔄 Rollback (if needed)

```bash
# Restore from backup
cd /var/odoo/properties/extra-addons/odoo17_final.git-6880b7fcd4844/commission_ax/views
cp commission_profit_analysis_wizard_views.xml.bak commission_profit_analysis_wizard_views.xml
cp commission_partner_statement_wizard_views.xml.bak commission_partner_statement_wizard_views.xml
cp commission_type_views.xml.bak commission_type_views.xml

# Restart
systemctl restart odoo
```

---

## 📞 Need Help?

**Check logs:**
```bash
journalctl -u odoo -n 100
```

**Check service:**
```bash
systemctl status odoo
```

**Restart service:**
```bash
systemctl restart odoo
```

---

## 📄 Full Documentation

See `PRODUCTION_DEPLOYMENT_GUIDE.md` for:
- Detailed explanations
- Troubleshooting guide
- Verification steps
- Rollback procedures

---

**Deployment Time**: ~3 minutes  
**Downtime**: ~10 seconds (service restart)  
**Risk**: Low (backups created automatically)

🎉 **Choose your method and deploy!**