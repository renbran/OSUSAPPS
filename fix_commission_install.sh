#!/bin/bash

echo "=== Commission Lines Installation Fix ==="
cd "/d/RUNNING APPS/ready production/latest/OSUSAPPS"

echo "1. Checking current module status..."
docker-compose exec db psql -U odoo -d odoo -c "SELECT name, state FROM ir_module_module WHERE name LIKE '%commission%' ORDER BY name;"

echo ""
echo "2. Attempting to install commission_lines directly..."

# Try to install with better error handling
if docker-compose exec odoo odoo --init=commission_lines --stop-after-init -d odoo --log-level=error 2>&1 | tee install_log.txt; then
    echo "Installation command completed"
else
    echo "Installation command failed"
fi

echo ""
echo "3. Checking installation result..."
docker-compose exec db psql -U odoo -d odoo -c "SELECT name, state FROM ir_module_module WHERE name = 'commission_lines';"

echo ""
echo "4. Checking commission_line table..."
docker-compose exec db psql -U odoo -d odoo -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'commission_line';" 

echo ""
echo "5. Starting Odoo..."
docker-compose up -d odoo

echo "=== Fix Complete ==="