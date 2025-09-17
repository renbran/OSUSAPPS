#!/bin/bash

echo "=== Commission Lines Module Installation Diagnostic ==="

# Navigate to project directory
cd "/d/RUNNING APPS/ready production/latest/OSUSAPPS"

echo "1. Checking commission_lines module structure..."
if [ -d "commission_lines" ]; then
    echo "✓ commission_lines directory exists"
    ls -la commission_lines/
else
    echo "✗ commission_lines directory not found"
    exit 1
fi

echo ""
echo "2. Checking manifest file..."
if [ -f "commission_lines/__manifest__.py" ]; then
    echo "✓ __manifest__.py exists"
    echo "Module name in manifest:"
    grep "'name'" commission_lines/__manifest__.py
else
    echo "✗ __manifest__.py not found"
    exit 1
fi

echo ""
echo "3. Checking dependencies..."
echo "Dependencies in manifest:"
grep -A 10 "'depends'" commission_lines/__manifest__.py

echo ""
echo "4. Checking if commission_ax is installed..."
docker-compose exec db psql -U odoo -d odoo -c "SELECT name, state FROM ir_module_module WHERE name = 'commission_ax';"

echo ""
echo "5. Attempting to install commission_lines..."
docker-compose exec odoo odoo --init=commission_lines --stop-after-init -d odoo

echo ""
echo "6. Checking installation result..."
docker-compose exec db psql -U odoo -d odoo -c "SELECT name, state FROM ir_module_module WHERE name = 'commission_lines';"

echo ""
echo "7. Starting Odoo..."
docker-compose up -d odoo

echo "=== Diagnostic Complete ==="