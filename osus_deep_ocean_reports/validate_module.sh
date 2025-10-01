#!/bin/bash
# Deep Ocean Reports - Module Validation Script
# This script validates that the Deep Ocean Reports module is correctly configured

echo "🌊 Deep Ocean Reports - Module Validation"
echo "=========================================="

MODULE_PATH="."
MANIFEST_FILE="$MODULE_PATH/__manifest__.py"

# Function to check file exists
check_file() {
    if [ -f "$1" ]; then
        echo "✅ $2"
        return 0
    else
        echo "❌ $2"
        return 1
    fi
}

# Function to check dependency
check_dependency() {
    if grep -q "'$1'" "$MANIFEST_FILE"; then
        if [ "$2" = "should_exist" ]; then
            echo "✅ Dependency '$1' found"
            return 0
        else
            echo "⚠️  Dependency '$1' found (may cause conflicts)"
            return 1
        fi
    else
        if [ "$2" = "should_exist" ]; then
            echo "❌ Dependency '$1' missing"
            return 1
        else
            echo "✅ Dependency '$1' not found (good)"
            return 0
        fi
    fi
}

echo ""
echo "📁 File Structure Validation:"
echo "-----------------------------"

files_ok=0
check_file "$MODULE_PATH/__manifest__.py" "Manifest file" && ((files_ok++))
check_file "$MODULE_PATH/models/deep_ocean_invoice.py" "Model file" && ((files_ok++))
check_file "$MODULE_PATH/views/account_move_views.xml" "Views file" && ((files_ok++))
check_file "$MODULE_PATH/reports/deep_ocean_invoice_report.xml" "Invoice report" && ((files_ok++))
check_file "$MODULE_PATH/reports/deep_ocean_receipt_report.xml" "Receipt report" && ((files_ok++))
check_file "$MODULE_PATH/static/src/css/deep_ocean_reports.css" "CSS file" && ((files_ok++))
check_file "$MODULE_PATH/static/src/js/deep_ocean_reports.js" "JavaScript file" && ((files_ok++))
check_file "$MODULE_PATH/security/ir.model.access.csv" "Security file" && ((files_ok++))

echo ""
echo "🔗 Dependency Validation:"
echo "-------------------------"

deps_ok=0
check_dependency "account" "should_exist" && ((deps_ok++))
check_dependency "base" "should_exist" && ((deps_ok++))
check_dependency "portal" "should_exist" && ((deps_ok++))
check_dependency "sale" "should_not_exist" && ((deps_ok++))

echo ""
echo "🔍 XML Validation:"
echo "------------------"

xml_ok=0

# Check views file for common issues
if [ -f "$MODULE_PATH/views/account_move_views.xml" ]; then
    if grep -q 'purchase_order_count' "$MODULE_PATH/views/account_move_views.xml"; then
        echo "❌ Views contain purchase_order_count reference"
    else
        echo "✅ Views don't reference purchase_order_count"
        ((xml_ok++))
    fi
    
    if grep -q 'Deep Ocean Theme' "$MODULE_PATH/views/account_move_views.xml"; then
        echo "✅ Deep Ocean Theme tab found in views"
        ((xml_ok++))
    else
        echo "❌ Deep Ocean Theme tab missing"
    fi
else
    echo "❌ Views file not found"
fi

# Check reports
if [ -f "$MODULE_PATH/reports/deep_ocean_invoice_report.xml" ]; then
    if grep -q 'deep_ocean_invoice_report' "$MODULE_PATH/reports/deep_ocean_invoice_report.xml"; then
        echo "✅ Invoice report template found"
        ((xml_ok++))
    else
        echo "⚠️  Invoice report template ID may be incorrect"
    fi
fi

echo ""
echo "📊 Validation Summary:"
echo "----------------------"

total_checks=11
passed_checks=$((files_ok + deps_ok + xml_ok))

echo "Files: $files_ok/8 ✅"
echo "Dependencies: $deps_ok/4 ✅"  
echo "XML Structure: $xml_ok/3 ✅"
echo ""
echo "Overall: $passed_checks/$total_checks checks passed"

if [ $passed_checks -eq $total_checks ]; then
    echo ""
    echo "🎉 ALL VALIDATIONS PASSED!"
    echo "✅ Deep Ocean Reports module is ready for installation"
    echo ""
    echo "🚀 Installation Commands:"
    echo "docker-compose exec odoo odoo --stop-after-init --install=osus_deep_ocean_reports -d odoo"
elif [ $passed_checks -gt 8 ]; then
    echo ""
    echo "✅ MOSTLY READY - Minor issues detected"
    echo "📝 Review warnings above and proceed with installation"
else
    echo ""
    echo "❌ CRITICAL ISSUES DETECTED"
    echo "🔧 Fix the errors above before installation"
fi

echo ""
echo "📚 Usage Instructions:"
echo "1. Install: Update Apps List > Search 'Deep Ocean' > Install"
echo "2. Use: Go to Customer Invoice > Deep Ocean Theme tab"
echo "3. Enable: Toggle 'Use Deep Ocean Theme'"
echo "4. Print: Use 'Print Deep Ocean Invoice/Receipt' buttons"