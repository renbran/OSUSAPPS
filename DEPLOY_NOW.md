# 🚀 DEPLOY NOW - 30 Second Guide

## ⚡ Super Quick Deployment

### Copy & Paste This Command

**Replace `YOUR_SERVER_IP` with your actual server IP:**

```bash
ssh root@YOUR_SERVER_IP << 'DEPLOY'
cd /var/odoo/properties/extra-addons/odoo17_final.git-6880b7fcd4844/commission_ax/views
mkdir -p /tmp/backup_$(date +%Y%m%d_%H%M%S)
cp *.xml /tmp/backup_$(date +%Y%m%d_%H%M%S)/
sed -i 's/parent="commission_ax\.menu_commission_reports"/parent="menu_commission_reports"/g' commission_profit_analysis_wizard_views.xml commission_partner_statement_wizard_views.xml
sed -i 's/action="commission_ax\.action_commission_profit_analysis_wizard"/action="action_commission_profit_analysis_wizard"/g' commission_profit_analysis_wizard_views.xml
sed -i 's/action="commission_ax\.action_commission_partner_statement_wizard"/action="action_commission_partner_statement_wizard"/g' commission_partner_statement_wizard_views.xml
sed -i 's/parent="commission_ax\.commission_menu"/parent="commission_menu"/g' commission_type_views.xml
sed -i 's/action="commission_ax\.action_commission_type"/action="action_commission_type"/g' commission_type_views.xml
su - odoo -c '/var/odoo/properties/src/odoo-bin -c /etc/odoo/odoo.conf -d properties -u commission_ax --stop-after-init'
systemctl restart odoo
echo "✅ DEPLOYMENT COMPLETE!"
DEPLOY
```

---

## ✅ Verify It Worked

```bash
# Check for errors (should be none)
ssh root@YOUR_SERVER_IP "journalctl -u odoo --since '2 minutes ago' | grep -i parseerror"

# Check service (should be running)
ssh root@YOUR_SERVER_IP "systemctl status odoo"
```

---

## 🎯 That's It!

- ✅ Files fixed
- ✅ Module updated
- ✅ Service restarted
- ✅ Backup created

**Test**: Go to Sales → Commissions in your Odoo web interface

---

## 📚 Need More Info?

- **Quick Guide**: `QUICK_START_PRODUCTION.md`
- **Full Guide**: `PRODUCTION_DEPLOYMENT_GUIDE.md`
- **Automated Script**: `fix_commission_ax_production.sh`
- **Complete Package**: `DEPLOYMENT_PACKAGE_README.md`

---

## 🔄 Rollback (if needed)

```bash
ssh root@YOUR_SERVER_IP << 'ROLLBACK'
cd /var/odoo/properties/extra-addons/odoo17_final.git-6880b7fcd4844/commission_ax/views
cp /tmp/backup_*/commission_*.xml .
systemctl restart odoo
ROLLBACK
```

---

🎉 **Deploy in 30 seconds!**