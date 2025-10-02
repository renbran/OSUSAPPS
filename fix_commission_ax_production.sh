#!/bin/bash
#
# Commission AX Production Fix Script
# Purpose: Fix module prefix errors in commission_ax views
# Date: October 2, 2025
# 

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Commission AX Production Fix Script          ║${NC}"
echo -e "${BLUE}║  Removing incorrect module prefixes           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
echo ""

# Configuration
MODULE_PATH="/var/odoo/properties/extra-addons/odoo17_final.git-6880b7fcd4844/commission_ax"
VIEWS_PATH="${MODULE_PATH}/views"
BACKUP_DIR="/tmp/commission_ax_backup_$(date +%Y%m%d_%H%M%S)"
ODOO_BIN="/var/odoo/properties/src/odoo-bin"
ODOO_CONF="/etc/odoo/odoo.conf"
DB_NAME="properties"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}✗ This script must be run as root${NC}"
    echo "Please run: sudo $0"
    exit 1
fi

# Check if module path exists
if [ ! -d "$MODULE_PATH" ]; then
    echo -e "${RED}✗ Module path not found: $MODULE_PATH${NC}"
    echo "Please update MODULE_PATH variable in this script"
    exit 1
fi

echo -e "${YELLOW}📋 Pre-flight checks...${NC}"
echo "   Module path: $MODULE_PATH"
echo "   Views path: $VIEWS_PATH"
echo "   Database: $DB_NAME"
echo ""

# Create backup
echo -e "${YELLOW}📦 Creating backup...${NC}"
mkdir -p "${BACKUP_DIR}"
cp -r "${VIEWS_PATH}" "${BACKUP_DIR}/"
echo -e "${GREEN}✓ Backup created: ${BACKUP_DIR}${NC}"
echo ""

# Navigate to views directory
cd "${VIEWS_PATH}"

# Fix commission_profit_analysis_wizard_views.xml
echo -e "${YELLOW}🔧 Fixing commission_profit_analysis_wizard_views.xml...${NC}"
if [ -f "commission_profit_analysis_wizard_views.xml" ]; then
    sed -i.bak \
        -e 's/parent="commission_ax\.menu_commission_reports"/parent="menu_commission_reports"/g' \
        -e 's/action="commission_ax\.action_commission_profit_analysis_wizard"/action="action_commission_profit_analysis_wizard"/g' \
        commission_profit_analysis_wizard_views.xml
    echo -e "${GREEN}✓ Fixed commission_profit_analysis_wizard_views.xml${NC}"
else
    echo -e "${RED}✗ File not found: commission_profit_analysis_wizard_views.xml${NC}"
fi

# Fix commission_partner_statement_wizard_views.xml
echo -e "${YELLOW}🔧 Fixing commission_partner_statement_wizard_views.xml...${NC}"
if [ -f "commission_partner_statement_wizard_views.xml" ]; then
    sed -i.bak \
        -e 's/parent="commission_ax\.menu_commission_reports"/parent="menu_commission_reports"/g' \
        -e 's/action="commission_ax\.action_commission_partner_statement_wizard"/action="action_commission_partner_statement_wizard"/g' \
        commission_partner_statement_wizard_views.xml
    echo -e "${GREEN}✓ Fixed commission_partner_statement_wizard_views.xml${NC}"
else
    echo -e "${RED}✗ File not found: commission_partner_statement_wizard_views.xml${NC}"
fi

# Fix commission_type_views.xml
echo -e "${YELLOW}🔧 Fixing commission_type_views.xml...${NC}"
if [ -f "commission_type_views.xml" ]; then
    sed -i.bak \
        -e 's/parent="commission_ax\.commission_menu"/parent="commission_menu"/g' \
        -e 's/action="commission_ax\.action_commission_type"/action="action_commission_type"/g' \
        commission_type_views.xml
    echo -e "${GREEN}✓ Fixed commission_type_views.xml${NC}"
else
    echo -e "${RED}✗ File not found: commission_type_views.xml${NC}"
fi

echo ""
echo -e "${YELLOW}📋 Verifying changes...${NC}"
echo ""

# Check for remaining commission_ax prefixes in parent/action attributes
FOUND_ISSUES=0
for file in commission_profit_analysis_wizard_views.xml commission_partner_statement_wizard_views.xml commission_type_views.xml; do
    if [ -f "$file" ]; then
        if grep -q 'parent="commission_ax\.' "$file" || grep -q 'action="commission_ax\.' "$file"; then
            echo -e "${RED}✗ Still found commission_ax prefix in: $file${NC}"
            grep -n 'commission_ax\.' "$file" | grep -E '(parent=|action=)' || true
            FOUND_ISSUES=1
        else
            echo -e "${GREEN}✓ Clean: $file${NC}"
        fi
    fi
done

echo ""

if [ $FOUND_ISSUES -eq 0 ]; then
    echo -e "${GREEN}✅ All files fixed successfully!${NC}"
else
    echo -e "${YELLOW}⚠️  Some files still have issues - please review manually${NC}"
fi

echo ""
echo -e "${YELLOW}📁 Backup location: ${BACKUP_DIR}${NC}"
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Next Steps                                    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}1. Update the module:${NC}"
echo "   su - odoo -c '$ODOO_BIN -c $ODOO_CONF -d $DB_NAME -u commission_ax --stop-after-init'"
echo ""
echo -e "${YELLOW}2. Restart Odoo service:${NC}"
echo "   systemctl restart odoo"
echo ""
echo -e "${YELLOW}3. Monitor logs:${NC}"
echo "   journalctl -u odoo -f"
echo ""
echo -e "${GREEN}Press Enter to update module and restart Odoo automatically...${NC}"
echo -e "${YELLOW}Or press Ctrl+C to exit and run steps manually${NC}"
read

# Update module
echo ""
echo -e "${YELLOW}🔄 Updating commission_ax module...${NC}"
su - odoo -c "$ODOO_BIN -c $ODOO_CONF -d $DB_NAME -u commission_ax --stop-after-init"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Module updated successfully${NC}"
else
    echo -e "${RED}✗ Module update failed - check logs${NC}"
    exit 1
fi

# Restart Odoo
echo ""
echo -e "${YELLOW}🔄 Restarting Odoo service...${NC}"
systemctl restart odoo

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Odoo restarted successfully${NC}"
else
    echo -e "${RED}✗ Odoo restart failed${NC}"
    exit 1
fi

# Check service status
sleep 3
if systemctl is-active --quiet odoo; then
    echo -e "${GREEN}✓ Odoo service is running${NC}"
else
    echo -e "${RED}✗ Odoo service is not running${NC}"
    echo "Check status with: systemctl status odoo"
    exit 1
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ Deployment Complete!                       ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}📊 Final verification:${NC}"
echo "   1. Check logs: journalctl -u odoo --since '2 minutes ago'"
echo "   2. Test commission menus in Odoo web interface"
echo "   3. Verify no ParseError in logs"
echo ""
echo -e "${YELLOW}🔄 To rollback if needed:${NC}"
echo "   cp -r ${BACKUP_DIR}/views/* ${VIEWS_PATH}/"
echo "   systemctl restart odoo"
echo ""
echo -e "${GREEN}🎉 Done!${NC}"
