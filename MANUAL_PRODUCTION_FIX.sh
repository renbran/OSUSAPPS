#!/bin/bash
# PRODUCTION FIX: rental_management Field Error + commission_ax Menu Fix
# Run this on your production server: 139.84.163.11

echo "================================================"
echo "🔧 PRODUCTION SERVER FIX - Step by Step"
echo "================================================"
echo ""

# Step 1: Connect to your server
echo "Step 1: Connect to your server"
echo "Run: ssh root@139.84.163.11"
echo "Enter your password when prompted"
echo ""
read -p "Press Enter after you've connected to the server..."

# Step 2: Fix rental_management module
echo ""
echo "Step 2: Fix rental_management module"
echo "This will reinstall the module to fix the is_extra_service field error"
echo ""
echo "Run this command:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cat << 'CMD1'
su - odoo -c '/var/odoo/properties/src/odoo-bin -c /etc/odoo/odoo.conf -d properties -u rental_management --stop-after-init'
CMD1
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⏳ This may take 2-5 minutes. Wait for it to complete."
echo ""
read -p "Press Enter after the command completes..."

# Step 3: Fix commission_ax XML files
echo ""
echo "Step 3: Fix commission_ax XML files"
echo "Navigate to the commission_ax views directory:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cat << 'CMD2'
cd /var/odoo/properties/extra-addons/odoo17_final.git-6880b7fcd4844/commission_ax/views
CMD2
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
read -p "Press Enter after navigating to the directory..."

# Step 4: Create backup
echo ""
echo "Step 4: Create backup of XML files"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cat << 'CMD3'
mkdir -p /tmp/backup_$(date +%Y%m%d_%H%M%S)
cp *.xml /tmp/backup_$(date +%Y%m%d_%H%M%S)/
CMD3
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
read -p "Press Enter after creating backup..."

# Step 5: Fix XML files
echo ""
echo "Step 5: Fix XML files (remove commission_ax. prefix)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cat << 'CMD4'
sed -i 's/parent="commission_ax\.menu_commission_reports"/parent="menu_commission_reports"/g' commission_profit_analysis_wizard_views.xml commission_partner_statement_wizard_views.xml

sed -i 's/action="commission_ax\.action_commission_profit_analysis_wizard"/action="action_commission_profit_analysis_wizard"/g' commission_profit_analysis_wizard_views.xml

sed -i 's/action="commission_ax\.action_commission_partner_statement_wizard"/action="action_commission_partner_statement_wizard"/g' commission_partner_statement_wizard_views.xml

sed -i 's/parent="commission_ax\.commission_menu"/parent="commission_menu"/g' commission_type_views.xml

sed -i 's/action="commission_ax\.action_commission_type"/action="action_commission_type"/g' commission_type_views.xml
CMD4
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
read -p "Press Enter after fixing XML files..."

# Step 6: Verify changes
echo ""
echo "Step 6: Verify the changes"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cat << 'CMD5'
grep 'parent="menu_commission_reports"' commission_profit_analysis_wizard_views.xml
grep 'parent="commission_menu"' commission_type_views.xml
CMD5
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "You should see lines WITHOUT 'commission_ax.' prefix"
echo ""
read -p "Press Enter after verifying..."

# Step 7: Update commission_ax module
echo ""
echo "Step 7: Update commission_ax module"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cat << 'CMD6'
su - odoo -c '/var/odoo/properties/src/odoo-bin -c /etc/odoo/odoo.conf -d properties -u commission_ax --stop-after-init'
CMD6
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⏳ This may take 1-3 minutes. Wait for it to complete."
echo ""
read -p "Press Enter after the command completes..."

# Step 8: Restart Odoo
echo ""
echo "Step 8: Restart Odoo service"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cat << 'CMD7'
systemctl restart odoo
CMD7
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⏳ Waiting for Odoo to start..."
sleep 10

# Step 9: Check status
echo ""
echo "Step 9: Check Odoo status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cat << 'CMD8'
systemctl status odoo --no-pager -l
CMD8
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
read -p "Press Enter after checking status..."

# Step 10: Check logs
echo ""
echo "Step 10: Check logs for errors"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cat << 'CMD9'
tail -100 /var/log/odoo/odoo-server.log | grep -E "ERROR|CRITICAL|commission_ax|rental_management"
CMD9
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Look for any ERROR or CRITICAL messages"
echo ""

echo ""
echo "================================================"
echo "✅ DEPLOYMENT COMPLETE!"
echo "================================================"
echo ""
echo "Next Steps:"
echo "1. Log into your Odoo web interface"
echo "2. Go to Sales → Commissions"
echo "3. Verify all menus are working"
echo "4. Test the commission wizards"
echo ""
echo "If you see any errors, run:"
echo "tail -f /var/log/odoo/odoo-server.log"
echo ""
