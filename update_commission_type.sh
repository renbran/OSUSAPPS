#!/bin/bash

# Commission Type Model Update Script
# This script ensures the commission.type model is properly installed and accessible

echo "=== Commission Type Model Update Script ==="
echo "Date: $(date)"
echo ""

# Function to check if we're in the right directory
check_odoo_environment() {
    if [ ! -f "docker-compose.yml" ]; then
        echo "Error: docker-compose.yml not found. Please run this script from the OSUSAPPS directory."
        exit 1
    fi
    
    if [ ! -d "commission_ax" ]; then
        echo "Error: commission_ax module not found."
        exit 1
    fi
}

# Function to check Docker containers
check_docker_status() {
    echo "Checking Docker containers..."
    docker-compose ps
    echo ""
}

# Function to update commission_ax module
update_commission_module() {
    echo "Updating commission_ax module..."
    echo "This will install the new commission.type model..."
    
    # Update the specific module
    docker-compose exec odoo odoo --update=commission_ax --stop-after-init -d odoo
    
    if [ $? -eq 0 ]; then
        echo "✅ commission_ax module updated successfully"
    else
        echo "❌ Failed to update commission_ax module"
        return 1
    fi
}

# Function to restart Odoo service
restart_odoo() {
    echo "Restarting Odoo service..."
    docker-compose restart odoo
    
    if [ $? -eq 0 ]; then
        echo "✅ Odoo service restarted successfully"
    else
        echo "❌ Failed to restart Odoo service"
        return 1
    fi
}

# Function to check if commission.type model is available
verify_commission_type_model() {
    echo "Waiting for Odoo to start..."
    sleep 10
    
    echo "Verifying commission.type model is available..."
    
    # Try to access the model through Python
    docker-compose exec odoo python3 -c "
import odoo
from odoo import registry, SUPERUSER_ID
from odoo.api import Environment

try:
    reg = registry('odoo')
    with reg.cursor() as cr:
        env = Environment(cr, SUPERUSER_ID, {})
        commission_type_model = env['commission.type']
        count = commission_type_model.search_count([])
        print(f'✅ commission.type model found with {count} records')
        
        # List existing commission types
        types = commission_type_model.search([])
        for commission_type in types:
            print(f'   - {commission_type.name} ({commission_type.code})')
            
except Exception as e:
    print(f'❌ Error accessing commission.type model: {e}')
    exit(1)
"
}

# Main execution
main() {
    echo "Starting commission type model update process..."
    echo ""
    
    # Check environment
    check_odoo_environment
    
    # Check Docker status
    check_docker_status
    
    # Update module
    echo "Step 1: Updating commission_ax module..."
    update_commission_module
    if [ $? -ne 0 ]; then
        echo "Update failed. Exiting."
        exit 1
    fi
    echo ""
    
    # Restart Odoo
    echo "Step 2: Restarting Odoo service..."
    restart_odoo
    if [ $? -ne 0 ]; then
        echo "Restart failed. Exiting."
        exit 1
    fi
    echo ""
    
    # Verify model
    echo "Step 3: Verifying commission.type model..."
    verify_commission_type_model
    echo ""
    
    echo "=== Update Process Complete ==="
    echo ""
    echo "The commission.type model should now be available."
    echo "External modules like 'commission_lines' should now be able to reference it."
    echo ""
    echo "If you're still getting RPC errors, ensure that:"
    echo "1. The external module (commission_lines) is updated/restarted"
    echo "2. Both modules are installed in the same database"
    echo "3. The commission_ax module has higher priority or is listed as a dependency"
    echo ""
}

# Execute main function
main "$@"