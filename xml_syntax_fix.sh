#!/bin/bash
# Fix XML syntax errors in executive views

echo "🔧 XML SYNTAX ERROR FIX FOR EXECUTIVE VIEWS"
echo "=" * 50

echo ""
echo "Step 1: Validate XML syntax locally..."

cat << 'EOF'
# Test XML syntax with xmllint (if available)
xmllint --noout payment_account_enhanced/views/executive_views.xml
xmllint --noout payment_account_enhanced/views/account_payment_views.xml

# Expected: No output means valid XML
EOF

echo ""
echo "Step 2: Update module with fixed XML..."

cat << 'EOF'
cd /var/odoo/staging-erposus.com && sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf --no-http --stop-after-init --update payment_account_enhanced

# Expected: Successful module update without XML errors
EOF

echo ""
echo "Step 3: Test basic module loading..."

cat << 'EOF'
cd /var/odoo/staging-erposus.com && sudo -u odoo venv/bin/python3 src/odoo-bin shell -c odoo.conf << 'TEST_EOF'

print("🔍 TESTING MODULE AFTER XML FIX")
print("=" * 30)

# Check if module loaded successfully
try:
    payment_module = env['ir.module.module'].search([('name', '=', 'payment_account_enhanced')])
    if payment_module:
        print(f"✅ Module state: {payment_module.state}")
    else:
        print("❌ Module not found")
except Exception as e:
    print(f"❌ Module check error: {e}")

# Test if views were created
try:
    executive_views = env['ir.ui.view'].search([('key', 'like', 'payment_account_enhanced.%executive%')])
    print(f"✅ Executive views found: {len(executive_views)}")
    for view in executive_views:
        print(f"  - {view.key}")
except Exception as e:
    print(f"❌ View check error: {e}")

# Test if actions were created
try:
    executive_actions = env['ir.actions.act_window'].search([('name', 'like', '%Executive%')])
    print(f"✅ Executive actions found: {len(executive_actions)}")
    for action in executive_actions:
        print(f"  - {action.name}")
except Exception as e:
    print(f"❌ Action check error: {e}")

TEST_EOF
EOF

echo ""
echo "📋 WHAT WAS FIXED:"
echo "1. Escaped all >= operators as &gt;= in XML attributes"
echo "2. Escaped all < operators as &lt; in XML attributes"  
echo "3. Simplified complex datetime expressions in domain filters"
echo "4. Fixed XML parsing issues in executive_views.xml and account_payment_views.xml"
echo ""
echo "Run the commands above to verify the fix worked!"
