#!/bin/bash

echo "🔧 Testing Commission AX Module Fixes"
echo "======================================="

cd "$(dirname "$0")"

echo "📁 Current directory: $(pwd)"

echo ""
echo "🐳 Restarting Odoo container..."
docker-compose restart odoo

echo ""
echo "⏳ Waiting 10 seconds for Odoo to start..."
sleep 10

echo ""
echo "📋 Checking Odoo logs for errors..."
echo "Looking for commission-related errors:"
docker-compose logs --tail=50 odoo | grep -i commission | head -10

echo ""
echo "Looking for critical errors:"
docker-compose logs --tail=50 odoo | grep -E "(ERROR|CRITICAL|SyntaxError|AttributeError)" | head -10

echo ""
echo "Looking for successful startup messages:"
docker-compose logs --tail=30 odoo | grep -E "(ready|modules loaded|server started)" | head -5

echo ""
echo "✅ Test completed. Check above output for results."