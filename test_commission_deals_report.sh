#!/bin/bash

# Commission AX Module Test Script for Docker
# This script tests the deals commission report functionality

echo "========================================"
echo "Commission AX Module Test Script"
echo "========================================"

# Function to wait for Odoo to be ready
wait_for_odoo() {
    echo "Waiting for Odoo to be ready..."
    until curl -s http://localhost:8090/web/health > /dev/null 2>&1; do
        echo "Waiting for Odoo..."
        sleep 5
    done
    echo "Odoo is ready!"
}

# Function to check if module is installed
check_module_installation() {
    echo "Checking commission_ax module installation..."
    docker-compose exec odoo odoo shell -c /etc/odoo/odoo.conf -d odoo << 'EOF'
import logging
_logger = logging.getLogger(__name__)

try:
    # Check if commission_ax module is installed
    module = env['ir.module.module'].search([('name', '=', 'commission_ax')])
    if module:
        print(f"Commission AX module status: {module.state}")
        if module.state == 'installed':
            print("✅ Commission AX module is installed!")
            
            # Check if our new model exists
            if env['ir.model'].search([('model', '=', 'deals.commission.report.wizard')]):
                print("✅ Deals Commission Report Wizard model exists!")
            else:
                print("❌ Deals Commission Report Wizard model not found!")
                
            # Check if menu items exist
            menu = env['ir.ui.menu'].search([('name', '=', 'Comprehensive Deals Report')])
            if menu:
                print("✅ Deals Commission Report menu exists!")
            else:
                print("❌ Deals Commission Report menu not found!")
                
        else:
            print(f"❌ Commission AX module is not installed (status: {module.state})")
    else:
        print("❌ Commission AX module not found!")
        
except Exception as e:
    print(f"❌ Error checking module: {e}")
    
env.cr.commit()
EOF
}

# Function to install/upgrade the module
install_upgrade_module() {
    echo "Installing/Upgrading commission_ax module..."
    docker-compose exec odoo odoo -c /etc/odoo/odoo.conf -d odoo -i commission_ax --stop-after-init
}

# Function to test the deals commission report wizard
test_deals_report_wizard() {
    echo "Testing Deals Commission Report Wizard..."
    docker-compose exec odoo odoo shell -c /etc/odoo/odoo.conf -d odoo << 'EOF'
import logging
from datetime import date, timedelta

_logger = logging.getLogger(__name__)

try:
    # Create a test wizard instance
    wizard_model = env['deals.commission.report.wizard']
    print(f"✅ Deals Commission Report Wizard model accessible: {wizard_model}")
    
    # Test wizard creation
    wizard = wizard_model.create({
        'date_from': date.today() - timedelta(days=30),
        'date_to': date.today(),
        'include_zero_commissions': True,
        'include_draft_orders': True,
        'group_by_project': True,
        'show_payment_details': True,
        'commission_status_filter': 'all'
    })
    print(f"✅ Test wizard created successfully: ID {wizard.id}")
    
    # Test data retrieval method
    deals_data = wizard._get_deals_data()
    print(f"✅ Data retrieval method works, found {len(deals_data)} deals")
    
    # Test if we have any sale orders to work with
    sale_orders = env['sale.order'].search([], limit=5)
    print(f"Available sale orders for testing: {len(sale_orders)}")
    
    if sale_orders:
        for order in sale_orders:
            print(f"  - Order: {order.name}, Customer: {order.partner_id.name}, State: {order.state}")
            if hasattr(order, 'consultant_id') and order.consultant_id:
                print(f"    Consultant: {order.consultant_id.name}")
            if hasattr(order, 'manager_id') and order.manager_id:
                print(f"    Manager: {order.manager_id.name}")
            if hasattr(order, 'project_id') and order.project_id:
                print(f"    Project: {order.project_id.name}")
    
    print("✅ Deals Commission Report Wizard test completed successfully!")
    
except Exception as e:
    print(f"❌ Error testing wizard: {e}")
    import traceback
    traceback.print_exc()

env.cr.commit()
EOF
}

# Function to test report generation
test_report_generation() {
    echo "Testing report generation..."
    docker-compose exec odoo odoo shell -c /etc/odoo/odoo.conf -d odoo << 'EOF'
import logging
from datetime import date, timedelta

_logger = logging.getLogger(__name__)

try:
    # Create wizard and test PDF generation
    wizard = env['deals.commission.report.wizard'].create({
        'date_from': date.today() - timedelta(days=30),
        'date_to': date.today(),
    })
    
    # Test data preparation
    deals_data = wizard._get_deals_data()
    print(f"Found {len(deals_data)} deals for report")
    
    if deals_data:
        print("Sample deal data:")
        sample = deals_data[0]
        for key, value in sample.items():
            print(f"  {key}: {value}")
            
    # Check if report action exists
    report_action = env.ref('commission_ax.action_report_deals_commission', raise_if_not_found=False)
    if report_action:
        print("✅ PDF Report action exists!")
    else:
        print("❌ PDF Report action not found!")
    
    print("✅ Report generation test completed!")
    
except Exception as e:
    print(f"❌ Error testing report generation: {e}")
    import traceback
    traceback.print_exc()

env.cr.commit()
EOF
}

# Function to create test data
create_test_data() {
    echo "Creating test data for commission testing..."
    docker-compose exec odoo odoo shell -c /etc/odoo/odoo.conf -d odoo << 'EOF'
import logging
from datetime import date

_logger = logging.getLogger(__name__)

try:
    # Create test partners for commission
    partner_model = env['res.partner']
    
    # Create consultant
    consultant = partner_model.create({
        'name': 'Test Consultant',
        'is_company': False,
        'supplier_rank': 1,
    })
    print(f"✅ Created test consultant: {consultant.name} (ID: {consultant.id})")
    
    # Create manager
    manager = partner_model.create({
        'name': 'Test Manager',
        'is_company': False,
        'supplier_rank': 1,
    })
    print(f"✅ Created test manager: {manager.name} (ID: {manager.id})")
    
    # Create customer
    customer = partner_model.create({
        'name': 'Test Customer',
        'is_company': True,
        'customer_rank': 1,
    })
    print(f"✅ Created test customer: {customer.name} (ID: {customer.id})")
    
    # Create project if project module is available
    project = None
    if 'project.project' in env:
        project = env['project.project'].create({
            'name': 'Test Real Estate Project',
            'partner_id': customer.id,
        })
        print(f"✅ Created test project: {project.name} (ID: {project.id})")
    
    # Create test product
    product = env['product.product'].create({
        'name': 'Test Property Unit',
        'default_code': 'UNIT-001',
        'type': 'service',
        'list_price': 500000.00,
    })
    print(f"✅ Created test product: {product.name} (ID: {product.id})")
    
    # Create test sale order with commission data
    sale_order_data = {
        'partner_id': customer.id,
        'date_order': date.today(),
        'consultant_id': consultant.id,
        'consultant_commission_type': 'percent_untaxed_total',
        'consultant_comm_percentage': 2.5,
        'manager_id': manager.id,
        'manager_legacy_commission_type': 'percent_untaxed_total',
        'manager_comm_percentage': 1.5,
        'order_line': [(0, 0, {
            'product_id': product.id,
            'product_uom_qty': 1,
            'price_unit': 500000.00,
        })],
    }
    
    if project:
        sale_order_data['project_id'] = project.id
        
    sale_order = env['sale.order'].create(sale_order_data)
    print(f"✅ Created test sale order: {sale_order.name} (ID: {sale_order.id})")
    print(f"   Customer: {sale_order.partner_id.name}")
    print(f"   Amount: {sale_order.amount_total}")
    print(f"   Consultant: {sale_order.consultant_id.name if sale_order.consultant_id else 'None'}")
    print(f"   Manager: {sale_order.manager_id.name if sale_order.manager_id else 'None'}")
    if project:
        print(f"   Project: {sale_order.project_id.name}")
    
    # Confirm the sale order
    sale_order.action_confirm()
    print(f"✅ Sale order confirmed, state: {sale_order.state}")
    
    print("✅ Test data creation completed!")
    
except Exception as e:
    print(f"❌ Error creating test data: {e}")
    import traceback
    traceback.print_exc()

env.cr.commit()
EOF
}

# Main test execution
main() {
    echo "Starting commission_ax module test..."
    
    # Check if Docker containers are running
    if ! docker-compose ps | grep -q "Up"; then
        echo "Starting Docker containers..."
        docker-compose up -d
        sleep 30
    fi
    
    # Wait for Odoo to be ready
    wait_for_odoo
    
    # Install/upgrade module
    install_upgrade_module
    
    # Wait a bit after installation
    sleep 10
    
    # Check module installation
    check_module_installation
    
    # Create test data
    create_test_data
    
    # Test the wizard functionality
    test_deals_report_wizard
    
    # Test report generation
    test_report_generation
    
    echo "========================================"
    echo "Commission AX Module Test Completed!"
    echo "========================================"
    echo ""
    echo "Next steps:"
    echo "1. Access Odoo at http://localhost:8090"
    echo "2. Login with admin/admin"
    echo "3. Go to Sales > Commission Reports > Comprehensive Deals Report"
    echo "4. Test the report with the created test data"
    echo ""
}

# Run main function
main
