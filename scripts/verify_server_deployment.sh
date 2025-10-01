#!/bin/bash

# Server Deployment Verification Script
# This script helps verify that the server has the latest code changes

echo "🚀 Server Deployment Verification for Commission App Fixes"
echo "=========================================================="

echo ""
echo "📋 Expected Fixes in commission_period_views.xml:"
echo "   • date_from should be changed to date_start"
echo "   • date_to should be changed to date_end"
echo ""

echo "🔍 Checking local repository status:"
echo -n "   Local git HEAD: "
git rev-parse --short HEAD
echo -n "   Origin HEAD: "  
git rev-parse --short origin/HEAD 2>/dev/null || echo "Cannot determine"

echo ""
echo "✅ Local file verification:"
if grep -q "date_start" commission_app/views/commission_period_views.xml && grep -q "date_end" commission_app/views/commission_period_views.xml; then
    if ! grep -q "date_from" commission_app/views/commission_period_views.xml && ! grep -q "date_to" commission_app/views/commission_period_views.xml; then
        echo "   ✅ Local file is CORRECT (uses date_start/date_end)"
    else
        echo "   ⚠️  Local file has MIXED field names"
    fi
else
    echo "   ❌ Local file still has INCORRECT field names"
fi

echo ""
echo "📊 Field name analysis in commission_period_views.xml:"
echo -n "   date_start occurrences: "
grep -o "date_start" commission_app/views/commission_period_views.xml | wc -l
echo -n "   date_end occurrences: "
grep -o "date_end" commission_app/views/commission_period_views.xml | wc -l
echo -n "   date_from occurrences: "
grep -o "date_from" commission_app/views/commission_period_views.xml | wc -l
echo -n "   date_to occurrences: "
grep -o "date_to" commission_app/views/commission_period_views.xml | wc -l

echo ""
echo "🎯 Server Update Instructions:"
echo "   1. On the server, navigate to the commission_app directory"
echo "   2. Run: git pull origin main"
echo "   3. Verify the fix with: grep 'date_start\|date_end' commission_app/views/commission_period_views.xml"
echo "   4. Restart Odoo server: docker-compose restart odoo (or equivalent)"
echo "   5. Clear Odoo cache if needed"

echo ""
echo "🔧 Manual server fix (if git pull doesn't work):"
echo "   Replace all 'date_from' with 'date_start'"
echo "   Replace all 'date_to' with 'date_end'"
echo "   In file: commission_app/views/commission_period_views.xml"

echo ""
echo "💡 Commit with the fix: eecfd3eae (Fix: Correct field name mismatches)"
echo "📅 This script generated on: $(date)"