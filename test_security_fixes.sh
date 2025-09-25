#!/bin/bash

echo "🛠️ Testing Commission AX Security Fixes"
echo "========================================"

cd "$(dirname "$0")"

echo "📁 Current directory: $(pwd)"

echo ""
echo "🐳 Restarting Odoo container to apply security fixes..."
docker-compose restart odoo

echo ""
echo "⏳ Waiting 15 seconds for Odoo to initialize..."
sleep 15

echo ""
echo "🔍 Checking for CRITICAL errors in Odoo logs..."
echo "================================================"
docker-compose logs --tail=50 odoo | grep -E "(CRITICAL|ERROR|Failed to initialize)" | tail -10

echo ""
echo "🔍 Checking for security-related errors..."
echo "==========================================="
docker-compose logs --tail=50 odoo | grep -iE "(security|access|permission|model.*not found)" | tail -10

echo ""
echo "🔍 Checking for commission_ax module loading..."
echo "==============================================="
docker-compose logs --tail=50 odoo | grep -iE "(commission_ax|commission.*wizard)" | tail -10

echo ""
echo "✅ Looking for successful startup messages..."
echo "============================================="
docker-compose logs --tail=30 odoo | grep -iE "(ready|server.*started|modules.*loaded|registry.*loaded)" | tail -5

echo ""
echo "📊 Summary: Check above output for errors"
echo "If no CRITICAL errors appear, the fixes were successful!"