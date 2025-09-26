#!/bin/bash
# Test Commission Partner Statement Report
echo "🧪 Testing Commission Partner Statement Report"
echo "=============================================="

# First, verify tables exist
echo "1. Checking database tables..."
docker-compose exec -T db psql -U odoo -d erposus -c "
SELECT 'OK' as status, table_name 
FROM information_schema.tables 
WHERE table_name IN ('commission_line', 'commission_type', 'commission_partner_statement_wizard', 'res_partner');"

echo ""
echo "2. Checking if we have any commission data..."
docker-compose exec -T db psql -U odoo -d erposus -c "
SELECT 'Commission Lines' as type, COUNT(*) as count FROM commission_line
UNION ALL
SELECT 'Commission Types' as type, COUNT(*) as count FROM commission_type
UNION ALL
SELECT 'Commission Partners' as type, COUNT(*) as count FROM res_partner WHERE is_commission_agent = true;"

echo ""
echo "3. Creating test commission data if needed..."
docker-compose exec -T db psql -U odoo -d erposus -c "
-- Create a test commission type if none exists
INSERT INTO commission_type (name, code, sequence, active, calculation_method, default_rate)
SELECT 'Test Agent Commission', 'TEST_AGENT', 10, true, 'percentage', 5.0
WHERE NOT EXISTS (SELECT 1 FROM commission_type WHERE code = 'TEST_AGENT');

-- Update a partner to be a commission agent if none exists
UPDATE res_partner 
SET is_commission_agent = true, commission_rate = 5.0 
WHERE id = (SELECT id FROM res_partner WHERE supplier_rank > 0 LIMIT 1)
AND NOT EXISTS (SELECT 1 FROM res_partner WHERE is_commission_agent = true);
"

echo ""
echo "4. Verification - checking created data..."
docker-compose exec -T db psql -U odoo -d erposus -c "
SELECT 'Commission Partners' as type, COUNT(*) as count FROM res_partner WHERE is_commission_agent = true
UNION ALL
SELECT 'Commission Types' as type, COUNT(*) as count FROM commission_type;"

echo ""
echo "✅ Test setup complete!"
echo ""
echo "Now test the report:"
echo "1. Go to http://localhost:8090"
echo "2. Navigate to Commission Management → Reports → Partner Statement Report"
echo "3. Select date range and generate report"
echo ""
echo "If you still get RPC errors, check Odoo logs with:"
echo "docker-compose logs -f odoo"