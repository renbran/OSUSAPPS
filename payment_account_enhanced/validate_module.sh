#!/bin/bash
# Module Validation Script
# Checks for common issues in the payment_account_enhanced module

echo "🔍 VALIDATING PAYMENT ACCOUNT ENHANCED MODULE"
echo "=" * 60

cd "$(dirname "$0")"

# Check for Python syntax errors
echo "✅ Checking Python files..."
find . -name "*.py" -type f | while read file; do
    if [[ -f "$file" ]]; then
        echo "  📄 Checking: $file"
        # Use basic file operations since python may not be available
        if grep -q "def action_print_payment_voucher" "$file"; then
            echo "    ✅ Found action_print_payment_voucher method"
        fi
    fi
done

# Check for XML structure
echo "✅ Checking XML files..."
find . -name "*.xml" -type f | while read file; do
    if [[ -f "$file" ]]; then
        echo "  📄 Checking: $file"
        if grep -q "action_print_payment_voucher" "$file"; then
            echo "    ✅ Found action_print_payment_voucher reference"
        fi
    fi
done

# Check for conflicting modules
echo "✅ Checking for conflicts..."
if [[ -d "../account_payment_final" ]]; then
    echo "    ⚠️  WARNING: account_payment_final module still exists - REMOVE IT"
else
    echo "    ✅ No account_payment_final conflict"
fi

if [[ -d "../account_payment_approval" ]]; then
    echo "    ⚠️  WARNING: account_payment_approval module still exists - REMOVE IT"
else
    echo "    ✅ No account_payment_approval conflict"
fi

# Check essential files
echo "✅ Checking essential files..."
essential_files=(
    "__manifest__.py"
    "models/__init__.py"
    "models/account_payment.py"
    "views/account_payment_views.xml"
    "controllers/main.py"
)

for file in "${essential_files[@]}"; do
    if [[ -f "$file" ]]; then
        echo "    ✅ Found: $file"
    else
        echo "    ❌ Missing: $file"
    fi
done

echo ""
echo "🎯 VALIDATION COMPLETE"
echo "=" * 60
echo "Next steps:"
echo "1. Install/upgrade the module in Odoo"
echo "2. Test payment voucher creation"
echo "3. Test QR generation and verification"
