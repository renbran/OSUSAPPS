#!/bin/bash
# Commission AX Module Fix Script
# This script fixes the purchase_order_count field issue in commission_ax module

echo "🔧 Commission AX Module Fix Script"
echo "=================================="

COMMISSION_AX_PATH="../commission_ax/models/sale_order.py"

if [ -f "$COMMISSION_AX_PATH" ]; then
    echo "✅ Found commission_ax module"
    
    # Create backup
    cp "$COMMISSION_AX_PATH" "$COMMISSION_AX_PATH.backup"
    echo "✅ Created backup: sale_order.py.backup"
    
    # Fix the field definition
    sed -i 's/purchase_order_count = fields\.Integer(string="PO Count", compute="_compute_purchase_order_count")/purchase_order_count = fields.Integer(string="PO Count", compute="_compute_purchase_order_count", store=False, default=0)/g' "$COMMISSION_AX_PATH"
    
    echo "✅ Fixed purchase_order_count field definition"
    echo "✅ Added store=False and default=0 parameters"
    
    echo ""
    echo "🔄 Next steps:"
    echo "1. Restart Odoo: docker-compose restart"
    echo "2. Update commission_ax: docker-compose exec odoo odoo --stop-after-init --update=commission_ax -d odoo"
    echo "3. Install Deep Ocean Reports: docker-compose exec odoo odoo --stop-after-init --install=osus_deep_ocean_reports -d odoo"
    
else
    echo "ℹ️  Commission AX module not found at $COMMISSION_AX_PATH"
    echo "   This is normal if commission_ax is not installed"
fi

echo ""
echo "✅ Deep Ocean Reports should now work without errors!"