#!/bin/bash

echo "🛠️ Testing Commission AX Data Loading Fix"
echo "==========================================="

cd "$(dirname "$0")"

echo "📁 Current directory: $(pwd)"

echo ""
echo "🐳 Restarting Odoo container to test data loading..."
docker-compose restart odoo

echo ""
echo "⏳ Waiting 20 seconds for Odoo to fully initialize..."
sleep 20

echo ""
echo "🔍 Checking for commission_category ValueError..."
echo "================================================"
docker-compose logs --tail=50 odoo | grep -iE "(wrong value.*commission_category|valueerror.*external|valueerror.*internal)" | head -5

echo ""
echo "🔍 Checking for data loading errors..."
echo "======================================"
docker-compose logs --tail=50 odoo | grep -iE "(ERROR|CRITICAL|ParseError|Failed to initialize)" | head -10

echo ""
echo "🔍 Checking for commission_types_data.xml loading..."
echo "=================================================="
docker-compose logs --tail=50 odoo | grep -iE "(commission_types_data|commission\.type)" | head -5

echo ""
echo "✅ Looking for successful startup messages..."
echo "============================================="
docker-compose logs --tail=30 odoo | grep -iE "(ready|server.*started|modules.*loaded|registry.*loaded)" | tail -5

echo ""
echo "📊 Summary:"
echo "==========="
echo "✅ If no ValueError for commission_category appears above, the fix worked!"
echo "✅ If you see 'ready' or 'server started' messages, Odoo is running successfully!"