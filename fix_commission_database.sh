#!/bin/bash

echo "🔧 Commission AX Database Schema Fix"
echo "==================================="

cd "$(dirname "$0")"

echo "📁 Current directory: $(pwd)"

echo ""
echo "❗ ISSUE: Database column 'is_commission_agent' missing from res_partner table"
echo "This happens when module schema changes haven't been applied to the database."

echo ""
echo "🛠️ SOLUTION: Force update commission_ax module to create missing columns"

echo ""
echo "🐳 Stopping Odoo container..."
docker-compose stop odoo

echo ""
echo "⚡ Starting Odoo with module update to create missing database columns..."
echo "This will:"
echo "  - Update commission_ax module schema"
echo "  - Create missing database columns" 
echo "  - Run any pending migrations"
echo "  - Stop after initialization (safe mode)"

docker-compose run --rm odoo odoo --update=commission_ax --stop-after-init -d erposus

echo ""
echo "✅ Schema update completed!"

echo ""
echo "🚀 Now starting Odoo normally..."
docker-compose up -d odoo

echo ""
echo "⏳ Waiting 15 seconds for startup..."
sleep 15

echo ""
echo "🔍 Checking for database column errors..."
docker-compose logs --tail=30 odoo | grep -iE "(column.*does not exist|UndefinedColumn)" | head -5

echo ""
echo "✅ Checking for successful startup..."
docker-compose logs --tail=20 odoo | grep -iE "(ready|server.*started)" | tail -3

echo ""
echo "📊 Summary:"
echo "==========="
echo "If no 'column does not exist' errors appear above, the fix worked!"
echo "The commission_ax module should now have all required database columns."