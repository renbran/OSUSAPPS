#!/bin/bash

# Simple Commission AX Module Validation Script
# This script validates the module structure and syntax before Docker testing

echo "========================================"
echo "Commission AX Module Validation"
echo "========================================"

# Function to check file existence
check_file_exists() {
    local file="$1"
    if [ -f "$file" ]; then
        echo "✅ $file exists"
        return 0
    else
        echo "❌ $file missing"
        return 1
    fi
}

# Function to validate Python syntax
validate_python_syntax() {
    local file="$1"
    if python -m py_compile "$file" 2>/dev/null; then
        echo "✅ $file syntax valid"
        return 0
    else
        echo "❌ $file syntax error"
        python -m py_compile "$file"
        return 1
    fi
}

# Function to validate XML syntax
validate_xml_syntax() {
    local file="$1"
    if xmllint --noout "$file" 2>/dev/null; then
        echo "✅ $file XML valid"
        return 0
    else
        echo "❌ $file XML error"
        xmllint --noout "$file"
        return 1
    fi
}

echo "1. Checking module structure..."
echo "================================"

# Check main module files
check_file_exists "commission_ax/__manifest__.py"
check_file_exists "commission_ax/__init__.py"

# Check new wizard files
check_file_exists "commission_ax/wizards/deals_commission_report_wizard.py"
check_file_exists "commission_ax/views/deals_commission_report_wizard_views.xml"
check_file_exists "commission_ax/reports/deals_commission_report.xml"

# Check security files
check_file_exists "commission_ax/security/ir.model.access.csv"

echo ""
echo "2. Validating Python syntax..."
echo "================================"

# Validate Python files
validate_python_syntax "commission_ax/wizards/deals_commission_report_wizard.py"
validate_python_syntax "commission_ax/__manifest__.py"

echo ""
echo "3. Validating XML syntax..."
echo "================================"

# Validate XML files
validate_xml_syntax "commission_ax/views/deals_commission_report_wizard_views.xml"
validate_xml_syntax "commission_ax/reports/deals_commission_report.xml"

echo ""
echo "4. Checking manifest data section..."
echo "====================================="

# Check if our new files are in the manifest
if grep -q "deals_commission_report_wizard_views.xml" commission_ax/__manifest__.py; then
    echo "✅ Wizard views in manifest"
else
    echo "❌ Wizard views missing from manifest"
fi

if grep -q "deals_commission_report.xml" commission_ax/__manifest__.py; then
    echo "✅ Report template in manifest"
else
    echo "❌ Report template missing from manifest"
fi

echo ""
echo "5. Checking model imports..."
echo "============================"

# Check if wizard is imported
if grep -q "deals_commission_report_wizard" commission_ax/wizards/__init__.py; then
    echo "✅ Wizard imported in __init__.py"
else
    echo "❌ Wizard not imported in __init__.py"
fi

echo ""
echo "6. Checking security access..."
echo "=============================="

# Check if security access is defined
if grep -q "deals.commission.report.wizard" commission_ax/security/ir.model.access.csv; then
    echo "✅ Security access defined"
else
    echo "❌ Security access missing"
fi

echo ""
echo "========================================"
echo "Module Validation Completed!"
echo "========================================"

# Summary
echo ""
echo "Summary:"
echo "--------"
if [ -f "commission_ax/wizards/deals_commission_report_wizard.py" ] && \
   [ -f "commission_ax/views/deals_commission_report_wizard_views.xml" ] && \
   [ -f "commission_ax/reports/deals_commission_report.xml" ]; then
    echo "✅ All required files are present"
    echo "✅ Module structure is complete"
    echo ""
    echo "Ready for Docker testing!"
    echo "Run: ./test_commission_deals_report.sh"
else
    echo "❌ Some files are missing"
    echo "Please check the file structure before testing"
fi
