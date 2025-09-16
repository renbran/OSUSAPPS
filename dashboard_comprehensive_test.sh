#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Start with clear screen
clear

echo -e "${BLUE}=== OE SALES DASHBOARD 17 COMPREHENSIVE TEST ===${NC}"
echo -e "${BLUE}This test will validate all aspects of the module${NC}"
echo

# Create log file
LOG_FILE="dashboard_test_$(date +"%Y%m%d_%H%M%S").log"
echo "OE SALES DASHBOARD 17 TEST LOG - $(date)" > "$LOG_FILE"

# Function to log message
log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

# Check if Docker is running
log "${YELLOW}Step 1: Checking Docker environment...${NC}"
if ! docker info > /dev/null 2>&1; then
    log "${RED}ERROR: Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Check if containers are running
if ! docker-compose ps | grep -q "odoo.*Up"; then
    log "${YELLOW}Starting Docker containers...${NC}"
    docker-compose up -d
    log "${YELLOW}Waiting for containers to start...${NC}"
    sleep 15
fi

CONTAINER_ID=$(docker-compose ps -q odoo)
if [ -z "$CONTAINER_ID" ]; then
    log "${RED}ERROR: Failed to get Odoo container ID.${NC}"
    exit 1
fi
log "${GREEN}✓ Docker environment is ready${NC}"
echo

# Test module structure
log "${YELLOW}Step 2: Testing module structure...${NC}"
MODULE_ERRORS=0

# Check manifest
if [ ! -f "oe_sale_dashboard_17/__manifest__.py" ]; then
    log "${RED}ERROR: Manifest file not found.${NC}"
    ((MODULE_ERRORS++))
else
    log "${GREEN}✓ Manifest file exists${NC}"
fi

# Check models directory
if [ ! -d "oe_sale_dashboard_17/models" ] || [ ! -f "oe_sale_dashboard_17/models/__init__.py" ]; then
    log "${RED}ERROR: Models directory or __init__.py file missing.${NC}"
    ((MODULE_ERRORS++))
else
    log "${GREEN}✓ Models directory structure is valid${NC}"
fi

# Check security directory
if [ ! -d "oe_sale_dashboard_17/security" ] || [ ! -f "oe_sale_dashboard_17/security/ir.model.access.csv" ]; then
    log "${RED}ERROR: Security directory or ir.model.access.csv file missing.${NC}"
    ((MODULE_ERRORS++))
else
    log "${GREEN}✓ Security directory structure is valid${NC}"
fi

# Check views directory
if [ ! -d "oe_sale_dashboard_17/views" ]; then
    log "${RED}ERROR: Views directory missing.${NC}"
    ((MODULE_ERRORS++))
else
    log "${GREEN}✓ Views directory exists${NC}"
    
    # List expected view files from manifest
    VIEW_FILES=$(grep -o "'views/[^']*'" oe_sale_dashboard_17/__manifest__.py | tr -d "'")
    MISSING_VIEWS=0
    
    for file in $VIEW_FILES; do
        if [ ! -f "oe_sale_dashboard_17/$file" ]; then
            log "${RED}ERROR: View file missing: $file${NC}"
            ((MISSING_VIEWS++))
        else
            log "${GREEN}✓ View file exists: $file${NC}"
        fi
    done
    
    if [ $MISSING_VIEWS -gt 0 ]; then
        ((MODULE_ERRORS++))
    fi
fi

if [ $MODULE_ERRORS -eq 0 ]; then
    log "${GREEN}✓ Module structure validation passed${NC}"
else
    log "${RED}✗ Module structure validation failed with $MODULE_ERRORS errors${NC}"
fi
echo

# Install the module
log "${YELLOW}Step 3: Installing module...${NC}"
docker-compose exec odoo odoo -d odoo -i oe_sale_dashboard_17 --stop-after-init > /tmp/install_output.txt 2>&1
INSTALL_STATUS=$?

cat /tmp/install_output.txt >> "$LOG_FILE"

if [ $INSTALL_STATUS -ne 0 ] || grep -qi "ERROR\|CRITICAL" /tmp/install_output.txt; then
    log "${RED}✗ Module installation failed${NC}"
    grep -i "ERROR\|CRITICAL" /tmp/install_output.txt | while read -r line; do
        log "${RED}$line${NC}"
    done
else
    log "${GREEN}✓ Module installed successfully${NC}"
fi
echo

# Test model creation
log "${YELLOW}Step 4: Testing model creation...${NC}"
# Create a Python script to test model creation
cat > /tmp/test_model_creation.py << 'EOF'
import sys
import odoo
from odoo import api, fields, models, SUPERUSER_ID
from contextlib import closing

def test_model_creation():
    odoo.tools.config['db_name'] = 'odoo'
    with odoo.api.Environment.manage():
        registry = odoo.modules.registry.Registry.new('odoo')
        with closing(registry.cursor()) as cr:
            env = odoo.api.Environment(cr, SUPERUSER_ID, {})
            
            # Test dashboard model
            Dashboard = env['sales.dashboard']
            if not Dashboard:
                print("ERROR: sales.dashboard model does not exist")
                return 1
                
            # Test creating a dashboard
            try:
                dashboard = Dashboard.create({
                    'name': 'Test Dashboard',
                    'date_from': '2023-01-01',
                    'date_to': '2023-12-31',
                })
                print(f"SUCCESS: Created dashboard with ID {dashboard.id}")
            except Exception as e:
                print(f"ERROR: Failed to create dashboard: {str(e)}")
                return 1
                
            # Test performer model
            Performer = env['sales.dashboard.performer']
            if not Performer:
                print("ERROR: sales.dashboard.performer model does not exist")
                return 1
                
            # Test creating a performer record
            try:
                performer = Performer.create({
                    'name': 'Test Performer',
                    'dashboard_id': dashboard.id,
                    'total_orders': 10,
                    'total_revenue': 1000.0,
                })
                print(f"SUCCESS: Created performer with ID {performer.id}")
            except Exception as e:
                print(f"ERROR: Failed to create performer: {str(e)}")
                return 1
                
            return 0

if __name__ == '__main__':
    sys.exit(test_model_creation())
EOF

# Run the test script
docker cp /tmp/test_model_creation.py "$CONTAINER_ID":/tmp/
MODEL_TEST_RESULT=$(docker-compose exec odoo python3 /tmp/test_model_creation.py)
MODEL_TEST_STATUS=$?

log "$MODEL_TEST_RESULT"

if [ $MODEL_TEST_STATUS -eq 0 ] && echo "$MODEL_TEST_RESULT" | grep -q "SUCCESS"; then
    log "${GREEN}✓ Model creation test passed${NC}"
else
    log "${RED}✗ Model creation test failed${NC}"
fi
echo

# Test views
log "${YELLOW}Step 5: Testing view loading...${NC}"
# Create a Python script to test view loading
cat > /tmp/test_views.py << 'EOF'
import sys
import odoo
from odoo import api, fields, models, SUPERUSER_ID
from contextlib import closing

def test_views():
    odoo.tools.config['db_name'] = 'odoo'
    with odoo.api.Environment.manage():
        registry = odoo.modules.registry.Registry.new('odoo')
        with closing(registry.cursor()) as cr:
            env = odoo.api.Environment(cr, SUPERUSER_ID, {})
            
            # Test views for sales.dashboard model
            model = 'sales.dashboard'
            View = env['ir.ui.view']
            
            # Check for form view
            form_view = View.search([('model', '=', model), ('type', '=', 'form')], limit=1)
            if not form_view:
                print(f"ERROR: No form view found for {model}")
                return 1
            print(f"SUCCESS: Found form view for {model}: {form_view.name}")
                
            # Check for tree/list view
            tree_view = View.search([('model', '=', model), ('type', '=', 'tree')], limit=1)
            if not tree_view:
                print(f"ERROR: No tree view found for {model}")
                return 1
            print(f"SUCCESS: Found tree view for {model}: {tree_view.name}")
            
            # Check for search view
            search_view = View.search([('model', '=', model), ('type', '=', 'search')], limit=1)
            if not search_view:
                print(f"WARNING: No search view found for {model}")
            else:
                print(f"SUCCESS: Found search view for {model}: {search_view.name}")
                
            # Check menu items
            Menu = env['ir.ui.menu']
            dashboard_menu = Menu.search([('name', 'ilike', '%dashboard%'), ('name', 'ilike', '%sale%')], limit=1)
            if not dashboard_menu:
                print("ERROR: No dashboard menu item found")
                return 1
            print(f"SUCCESS: Found dashboard menu: {dashboard_menu.name}")
            
            return 0

if __name__ == '__main__':
    sys.exit(test_views())
EOF

# Run the test script
docker cp /tmp/test_views.py "$CONTAINER_ID":/tmp/
VIEW_TEST_RESULT=$(docker-compose exec odoo python3 /tmp/test_views.py)
VIEW_TEST_STATUS=$?

log "$VIEW_TEST_RESULT"

if [ $VIEW_TEST_STATUS -eq 0 ] && echo "$VIEW_TEST_RESULT" | grep -q "SUCCESS"; then
    log "${GREEN}✓ View loading test passed${NC}"
else
    log "${RED}✗ View loading test failed${NC}"
fi
echo

# Test JavaScript assets
log "${YELLOW}Step 6: Testing JavaScript assets...${NC}"
# Create a Python script to test asset loading
cat > /tmp/test_assets.py << 'EOF'
import sys
import os
import odoo
from odoo import api, fields, models, SUPERUSER_ID
from contextlib import closing

def test_assets():
    odoo.tools.config['db_name'] = 'odoo'
    with odoo.api.Environment.manage():
        registry = odoo.modules.registry.Registry.new('odoo')
        with closing(registry.cursor()) as cr:
            env = odoo.api.Environment(cr, SUPERUSER_ID, {})
            
            # Check if assets are registered
            IrAsset = env['ir.asset']
            assets = IrAsset.search([('path', 'like', 'oe_sale_dashboard_17')])
            
            if not assets:
                print("WARNING: No assets found for oe_sale_dashboard_17")
            else:
                print(f"SUCCESS: Found {len(assets)} assets for oe_sale_dashboard_17")
                
            # Check if JS files exist
            module_path = '/mnt/extra-addons/oe_sale_dashboard_17'
            js_dir = os.path.join(module_path, 'static', 'src', 'js')
            
            if not os.path.exists(js_dir):
                print(f"ERROR: JS directory not found at {js_dir}")
                return 1
                
            js_files = [f for f in os.listdir(js_dir) if f.endswith('.js')]
            if not js_files:
                print("ERROR: No JS files found in static/src/js directory")
                return 1
                
            print(f"SUCCESS: Found {len(js_files)} JS files: {', '.join(js_files)}")
            
            return 0

if __name__ == '__main__':
    sys.exit(test_assets())
EOF

# Run the test script
docker cp /tmp/test_assets.py "$CONTAINER_ID":/tmp/
ASSET_TEST_RESULT=$(docker-compose exec odoo python3 /tmp/test_assets.py)
ASSET_TEST_STATUS=$?

log "$ASSET_TEST_RESULT"

if [ $ASSET_TEST_STATUS -eq 0 ] && echo "$ASSET_TEST_RESULT" | grep -q "SUCCESS"; then
    log "${GREEN}✓ Asset loading test passed${NC}"
else
    log "${RED}✗ Asset loading test failed${NC}"
fi
echo

# Final summary
log "${BLUE}=== TEST SUMMARY ===${NC}"
log "Module Structure: $([ $MODULE_ERRORS -eq 0 ] && echo "${GREEN}PASSED${NC}" || echo "${RED}FAILED${NC}")"
log "Module Installation: $([ $INSTALL_STATUS -eq 0 ] && echo "${GREEN}PASSED${NC}" || echo "${RED}FAILED${NC}")"
log "Model Creation: $([ $MODEL_TEST_STATUS -eq 0 ] && echo "${GREEN}PASSED${NC}" || echo "${RED}FAILED${NC}")"
log "View Loading: $([ $VIEW_TEST_STATUS -eq 0 ] && echo "${GREEN}PASSED${NC}" || echo "${RED}FAILED${NC}")"
log "Asset Loading: $([ $ASSET_TEST_STATUS -eq 0 ] && echo "${GREEN}PASSED${NC}" || echo "${RED}FAILED${NC}")"

if [ $MODULE_ERRORS -eq 0 ] && [ $INSTALL_STATUS -eq 0 ] && [ $MODEL_TEST_STATUS -eq 0 ] && [ $VIEW_TEST_STATUS -eq 0 ] && [ $ASSET_TEST_STATUS -eq 0 ]; then
    log "${GREEN}All tests passed successfully!${NC}"
    FINAL_RESULT="PASSED"
else
    log "${RED}Some tests failed. Check the logs for details.${NC}"
    FINAL_RESULT="FAILED"
fi

log "Detailed logs available in: $LOG_FILE"
echo

# Create a summary report file
cat > "dashboard_test_summary.txt" << EOF
OE SALES DASHBOARD 17 TEST SUMMARY
==================================
Test Date: $(date)
Final Result: $FINAL_RESULT

Test Steps:
- Module Structure: $([ $MODULE_ERRORS -eq 0 ] && echo "PASSED" || echo "FAILED")
- Module Installation: $([ $INSTALL_STATUS -eq 0 ] && echo "PASSED" || echo "FAILED")
- Model Creation: $([ $MODEL_TEST_STATUS -eq 0 ] && echo "PASSED" || echo "FAILED")
- View Loading: $([ $VIEW_TEST_STATUS -eq 0 ] && echo "PASSED" || echo "FAILED")
- Asset Loading: $([ $ASSET_TEST_STATUS -eq 0 ] && echo "PASSED" || echo "FAILED")

For detailed information, see: $LOG_FILE
EOF

log "${YELLOW}Test summary written to dashboard_test_summary.txt${NC}"
echo

log "${BLUE}Test completed at $(date)${NC}"