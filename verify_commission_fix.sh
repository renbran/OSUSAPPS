#!/bin/bash
# Verify Commission Module Status After Assignment Views Fix
echo "🔍 Verifying Commission Module Status"
echo "======================================"

# Check if all required tables exist
echo "1. Database tables status:"
docker-compose exec -T db psql -U odoo -d erposus -c "
SELECT 
    'commission_type' as table_name,
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'commission_type') 
         THEN '✅ EXISTS' ELSE '❌ MISSING' END as status
UNION ALL
SELECT 
    'commission_line' as table_name,
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'commission_line') 
         THEN '✅ EXISTS' ELSE '❌ MISSING' END as status
UNION ALL
SELECT 
    'commission_partner_statement_wizard' as table_name,
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'commission_partner_statement_wizard') 
         THEN '✅ EXISTS' ELSE '❌ MISSING' END as status
UNION ALL
SELECT 
    'res_partner (is_commission_agent)' as table_name,
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'res_partner' AND column_name = 'is_commission_agent') 
         THEN '✅ EXISTS' ELSE '❌ MISSING' END as status;
"

echo ""
echo "2. Commission data status:"
docker-compose exec -T db psql -U odoo -d erposus -c "
SELECT 'Commission Types' as item, COUNT(*) as count FROM commission_type
UNION ALL
SELECT 'Commission Lines' as item, COUNT(*) as count FROM commission_line
UNION ALL
SELECT 'Commission Partners' as item, COUNT(*) as count FROM res_partner WHERE is_commission_agent = true;
"

echo ""
echo "3. Module files status:"
echo "Commission assignment views: $([ -f 'commission_ax/views/commission_assignment_views.xml.disabled' ] && echo '✅ DISABLED' || echo '❌ NOT FOUND')"
echo "Commission wizard views: $([ -f 'commission_ax/views/commission_partner_statement_wizard_views.xml' ] && echo '✅ EXISTS' || echo '❌ MISSING')"
echo "Wizard model file: $([ -f 'commission_ax/wizards/commission_partner_statement_wizard.py' ] && echo '✅ EXISTS' || echo '❌ MISSING')"

echo ""
echo "✅ Verification Complete!"
echo ""
echo "🧪 Test the Commission Partner Statement Report:"
echo "1. Go to: http://localhost:8090"
echo "2. Navigate to Commission Management → Reports → Partner Statement Report"
echo "3. Generate a report to confirm functionality"
echo ""
echo "📋 Expected behavior:"
echo "- No RPC errors"
echo "- Report wizard opens successfully" 
echo "- PDF and Excel reports generate without errors"