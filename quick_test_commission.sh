#!/bin/bash

# Quick Docker Test for Commission AX Module
echo "========================================"
echo "Quick Commission AX Docker Test"
echo "========================================"

echo "Step 1: Starting Docker containers..."
docker-compose up -d

echo "Step 2: Waiting for containers to be ready..."
sleep 30

echo "Step 3: Checking container status..."
docker-compose ps

echo "Step 4: Installing commission_ax module..."
docker-compose exec odoo odoo -c /etc/odoo/odoo.conf -d odoo -i commission_ax --stop-after-init

echo "Step 5: Testing module installation..."
docker-compose exec odoo odoo shell -c /etc/odoo/odoo.conf -d odoo -c "
module = env['ir.module.module'].search([('name', '=', 'commission_ax')])
print(f'Commission AX module status: {module.state if module else \"not found\"}')

# Test if our new model exists
wizard_model = env.get('deals.commission.report.wizard')
if wizard_model:
    print('✅ Deals Commission Report Wizard model exists!')
    
    # Try to create a test wizard
    wizard = wizard_model.create({
        'date_from': '2025-01-01',
        'date_to': '2025-12-31',
    })
    print(f'✅ Test wizard created successfully: ID {wizard.id}')
else:
    print('❌ Deals Commission Report Wizard model not found!')

env.cr.commit()
"

echo "Step 6: Starting Odoo web server..."
docker-compose up odoo

echo "========================================"
echo "Test completed!"
echo "Access Odoo at: http://localhost:8090"
echo "Login: admin/admin"
echo "Navigate to: Sales > Commission Reports > Comprehensive Deals Report"
echo "========================================"
