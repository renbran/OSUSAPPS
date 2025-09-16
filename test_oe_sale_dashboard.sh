#!/bin/bash

# oe_sale_dashboard_17 Systematic Testing and Fix Script
# =====================================================

# Terminal colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Initialize log file
LOG_FILE="oe_sale_dashboard_17_test_$(date +'%Y%m%d_%H%M%S').log"
ISSUES_FOUND=0
ISSUES_FIXED=0

# Function to log messages
log() {
    local level=$1
    local message=$2
    local color=$NC
    
    case $level in
        "INFO") color=$BLUE ;;
        "SUCCESS") color=$GREEN ;;
        "WARNING") color=$YELLOW ;;
        "ERROR") color=$RED ;;
    esac
    
    echo -e "${color}[$level] $message${NC}"
    echo "[$level] $message" >> "$LOG_FILE"
}

# Function to check if Docker is running
check_docker_running() {
    log "INFO" "Checking if Docker is running..."
    if ! docker info &>/dev/null; then
        log "ERROR" "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    log "SUCCESS" "Docker is running."
}

# Function to check if containers are running
check_containers() {
    log "INFO" "Checking if Odoo and PostgreSQL containers are running..."
    
    if ! docker-compose ps | grep -q "odoo.*Up"; then
        log "WARNING" "Odoo container is not running. Starting services..."
        docker-compose up -d
        sleep 10 # Wait for services to start
        
        if ! docker-compose ps | grep -q "odoo.*Up"; then
            log "ERROR" "Failed to start Odoo container. Check docker-compose configuration."
            exit 1
        fi
    fi
    
    log "SUCCESS" "Odoo and PostgreSQL containers are running."
}

# Function to validate module structure
validate_module_structure() {
    log "INFO" "Validating module structure..."
    local missing_files=0
    
    # Check essential files
    for file in "__init__.py" "__manifest__.py" "security/ir.model.access.csv"; do
        if [ ! -f "oe_sale_dashboard_17/$file" ]; then
            log "ERROR" "Missing essential file: $file"
            ((missing_files++))
        fi
    done
    
    # Check module directories
    for dir in "models" "views" "security"; do
        if [ ! -d "oe_sale_dashboard_17/$dir" ]; then
            log "ERROR" "Missing essential directory: $dir"
            ((missing_files++))
        fi
    done
    
    if [ $missing_files -eq 0 ]; then
        log "SUCCESS" "Module structure is valid."
    else
        log "ERROR" "Module structure has issues: $missing_files missing files/directories."
        ((ISSUES_FOUND+=missing_files))
    fi
}

# Function to check manifest file
check_manifest() {
    log "INFO" "Checking manifest file..."
    local issues=0
    
    # Check if all declared files exist
    python3 - <<EOF >> "$LOG_FILE" 2>&1
import json
import os

try:
    with open('oe_sale_dashboard_17/__manifest__.py', 'r') as f:
        content = f.read()
        # Remove comments and handle the file as Python code
        manifest_dict = eval(compile(content, '__manifest__.py', 'exec'), {'__builtins__': {}}, {})
    
    missing_files = []
    
    # Check data files
    if 'data' in manifest_dict:
        for file in manifest_dict['data']:
            if not os.path.exists(os.path.join('oe_sale_dashboard_17', file)):
                missing_files.append(file)
    
    # Print results
    if missing_files:
        print(f"ERROR: {len(missing_files)} files declared in manifest but missing:")
        for file in missing_files:
            print(f"  - {file}")
        exit(1)
    else:
        print("SUCCESS: All files declared in manifest exist.")
        exit(0)
except Exception as e:
    print(f"ERROR: Failed to parse manifest file: {str(e)}")
    exit(1)
EOF

    if [ $? -ne 0 ]; then
        log "ERROR" "Issues found in manifest file."
        ((issues++))
    else
        log "SUCCESS" "Manifest file is valid."
    fi
    
    ((ISSUES_FOUND+=issues))
}

# Function to test module installation
test_module_installation() {
    log "INFO" "Testing module installation..."
    
    # Ensure module is updated in database
    docker-compose exec odoo odoo --stop-after-init -d odoo -i oe_sale_dashboard_17 --no-http >> "$LOG_FILE" 2>&1
    
    if [ $? -ne 0 ]; then
        log "ERROR" "Module installation failed. Check log for details."
        ((ISSUES_FOUND++))
        
        # Extract error message from log
        local error_msg=$(tail -n 20 "$LOG_FILE" | grep -A 5 -B 5 "ERROR\|CRITICAL" | tail -n 10)
        if [ ! -z "$error_msg" ]; then
            log "ERROR" "Installation error: $error_msg"
        fi
        
        # Try to fix common issues
        fix_common_installation_issues
    else
        log "SUCCESS" "Module installed successfully."
    fi
}

# Function to validate model fields and definitions
validate_models() {
    log "INFO" "Validating models..."
    
    # Create and run a Python script inside the container to validate models
    docker-compose exec odoo bash -c "cat > /tmp/validate_models.py << 'EOF'
import odoo
from odoo.tools import config
import sys

# Configure odoo
config['db_name'] = 'odoo'
config['without_demo'] = True
config['init'] = []
config['update'] = []

# Start odoo with the right database
odoo.cli.server.report_configuration()
odoo.service.server.start(preload=[], stop=True)

with odoo.api.Environment.manage():
    registry = odoo.modules.registry.Registry.new('odoo')
    with registry.cursor() as cr:
        env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
        
        # Check model existence and fields
        models_to_check = ['sales.dashboard', 'sales.dashboard.performer']
        
        issues = []
        for model_name in models_to_check:
            if model_name not in env:
                issues.append(f'Model {model_name} does not exist')
                continue
                
            model = env[model_name]
            # Check required fields
            required_fields = {
                'sales.dashboard': ['name', 'user_id', 'date_from', 'date_to', 'currency_id'],
                'sales.dashboard.performer': ['partner_id', 'dashboard_id', 'total_revenue']
            }
            
            for field in required_fields.get(model_name, []):
                if field not in model._fields:
                    issues.append(f'Required field {field} missing in {model_name}')
                    continue
        
        if issues:
            print('VALIDATION_ERROR: ' + '\n'.join(issues))
            sys.exit(1)
        else:
            print('VALIDATION_SUCCESS: All models and fields validated successfully')
            sys.exit(0)
EOF" >> "$LOG_FILE" 2>&1

    # Run the validation script
    output=$(docker-compose exec odoo python3 /tmp/validate_models.py 2>&1)
    echo "$output" >> "$LOG_FILE"
    
    if echo "$output" | grep -q "VALIDATION_ERROR"; then
        log "ERROR" "Model validation failed:"
        echo "$output" | grep -A 20 "VALIDATION_ERROR" | tail -n +2 | while read -r line; do
            log "ERROR" "  - $line"
            ((ISSUES_FOUND++))
        done
        
        # Try to fix model issues
        fix_model_issues
    else
        log "SUCCESS" "All models validated successfully."
    fi
}

# Function to validate security settings
validate_security() {
    log "INFO" "Validating security settings..."
    
    # Check ir.model.access.csv file
    if [ ! -f "oe_sale_dashboard_17/security/ir.model.access.csv" ]; then
        log "ERROR" "Missing security file: ir.model.access.csv"
        ((ISSUES_FOUND++))
        
        # Create basic security file
        create_security_file
        return
    fi
    
    # Count the number of access rules for each model
    local dashboard_rules=$(grep -c "model_sales_dashboard," "oe_sale_dashboard_17/security/ir.model.access.csv")
    local performer_rules=$(grep -c "model_sales_dashboard_performer," "oe_sale_dashboard_17/security/ir.model.access.csv")
    
    if [ "$dashboard_rules" -eq 0 ]; then
        log "ERROR" "No access rules defined for sales.dashboard model"
        ((ISSUES_FOUND++))
        add_security_rule "sales_dashboard"
    fi
    
    if [ "$performer_rules" -eq 0 ]; then
        log "ERROR" "No access rules defined for sales.dashboard.performer model"
        ((ISSUES_FOUND++))
        add_security_rule "sales_dashboard_performer"
    fi
    
    log "SUCCESS" "Security validation completed."
}

# Function to validate XML views
validate_views() {
    log "INFO" "Validating XML views..."
    
    # Create and run a Python script to validate views
    docker-compose exec odoo bash -c "cat > /tmp/validate_views.py << 'EOF'
import odoo
from odoo.tools import config
import sys

# Configure odoo
config['db_name'] = 'odoo'

# Start odoo with the right database
odoo.service.server.start(preload=[], stop=True)

with odoo.api.Environment.manage():
    registry = odoo.modules.registry.Registry.new('odoo')
    with registry.cursor() as cr:
        env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
        
        # Check view definitions
        View = env['ir.ui.view']
        invalid_views = View.search([
            ('model', 'in', ['sales.dashboard', 'sales.dashboard.performer']), 
            ('active', '=', True)
        ]).filtered(lambda v: not v._check_xml())
        
        if invalid_views:
            print('VALIDATION_ERROR: Invalid views found:')
            for view in invalid_views:
                print(f'- {view.name} (ID: {view.id}): XML validation failed')
            sys.exit(1)
        else:
            # Check menu items
            Menu = env['ir.ui.menu']
            dashboard_menus = Menu.search([('name', 'ilike', '%dashboard%'), ('name', 'ilike', '%sale%')])
            
            if not dashboard_menus:
                print('VALIDATION_WARNING: No menu items found for sales dashboard')
                sys.exit(2)
                
            print('VALIDATION_SUCCESS: All views validated successfully')
            sys.exit(0)
EOF" >> "$LOG_FILE" 2>&1

    # Run the validation script
    output=$(docker-compose exec odoo python3 /tmp/validate_views.py 2>&1)
    echo "$output" >> "$LOG_FILE"
    
    if echo "$output" | grep -q "VALIDATION_ERROR"; then
        log "ERROR" "View validation failed:"
        echo "$output" | grep -A 20 "VALIDATION_ERROR" | tail -n +2 | while read -r line; do
            log "ERROR" "  - $line"
            ((ISSUES_FOUND++))
        done
        
        # Try to fix view issues
        fix_view_issues
    elif echo "$output" | grep -q "VALIDATION_WARNING"; then
        log "WARNING" "View validation warnings:"
        echo "$output" | grep -A 20 "VALIDATION_WARNING" | tail -n +2 | while read -r line; do
            log "WARNING" "  - $line"
        done
    else
        log "SUCCESS" "All views validated successfully."
    fi
}

# Function to check JavaScript assets
check_js_assets() {
    log "INFO" "Checking JavaScript assets..."
    
    # First, check if files exist
    local missing_js=0
    local js_files=(
        "oe_sale_dashboard_17/static/src/js/chart.min.js"
        "oe_sale_dashboard_17/static/src/js/compatibility.js"
        "oe_sale_dashboard_17/static/src/js/field_mapping.js"
        "oe_sale_dashboard_17/static/src/js/dashboard_merged.js"
    )
    
    for file in "${js_files[@]}"; do
        if [ ! -f "$file" ]; then
            log "ERROR" "Missing JS asset: $file"
            ((missing_js++))
        fi
    done
    
    # Check for XML templates
    if [ ! -f "oe_sale_dashboard_17/static/src/xml/dashboard_merged_template.xml" ]; then
        log "ERROR" "Missing XML template: dashboard_merged_template.xml"
        ((missing_js++))
    fi
    
    # Check for CSS files
    if [ ! -f "oe_sale_dashboard_17/static/src/css/dashboard_merged.css" ]; then
        log "ERROR" "Missing CSS file: dashboard_merged.css"
        ((missing_js++))
    fi
    
    if [ $missing_js -eq 0 ]; then
        log "SUCCESS" "All JavaScript assets exist."
    else
        log "ERROR" "Missing $missing_js JavaScript assets."
        ((ISSUES_FOUND+=missing_js))
        
        # Try to fix missing asset issues
        fix_missing_assets
    fi
}

# Function to fix common installation issues
fix_common_installation_issues() {
    log "INFO" "Attempting to fix installation issues..."
    
    # Check for common dependency issues
    if grep -q "WARNING.*missing dependency" "$LOG_FILE"; then
        log "WARNING" "Detected missing dependencies. Updating manifest..."
        
        # Extract missing dependencies
        missing_deps=$(grep "WARNING.*missing dependency" "$LOG_FILE" | sed -E 's/.*missing dependency ([a-zA-Z0-9_]+).*/\1/g' | sort | uniq)
        
        for dep in $missing_deps; do
            log "INFO" "Adding missing dependency: $dep"
            
            # Update the manifest file to include the missing dependency
            sed -i "/depends': \[/a \ \ \ \ \ \ \ \ '$dep'," "oe_sale_dashboard_17/__manifest__.py"
            ((ISSUES_FIXED++))
        done
    fi
    
    # Fix potential XML syntax errors
    if grep -q "ERROR.*XML syntax error" "$LOG_FILE"; then
        log "WARNING" "Detected XML syntax errors. Running XML fixer..."
        
        # Get list of XML files
        xml_files=$(find oe_sale_dashboard_17 -name "*.xml")
        
        for file in $xml_files; do
            log "INFO" "Fixing XML syntax in $file"
            
            # Simple XML fixes: ensure proper XML declaration and fix common syntax issues
            if ! grep -q "<?xml" "$file"; then
                sed -i '1s/^/<?xml version="1.0" encoding="UTF-8"?>\n/' "$file"
            fi
            
            # Replace standalone attributes with proper XML
            sed -i 's/<field name="\([^"]*\)" required>/<field name="\1" required="1">/' "$file"
            sed -i 's/<field name="\([^"]*\)" readonly>/<field name="\1" readonly="1">/' "$file"
            
            # Fix unclosed tags
            sed -i 's/<field name="\([^"]*\)"  \/>/<field name="\1"\/>/' "$file"
            
            ((ISSUES_FIXED++))
        done
    fi
    
    # Try reinstalling the module after fixes
    log "INFO" "Reinstalling module after fixes..."
    docker-compose exec odoo odoo --stop-after-init -d odoo -i oe_sale_dashboard_17 --no-http >> "$LOG_FILE" 2>&1
    
    if [ $? -eq 0 ]; then
        log "SUCCESS" "Module reinstallation successful after fixes."
    else
        log "ERROR" "Module still has installation issues after fixes. Manual intervention required."
    fi
}

# Function to fix model issues
fix_model_issues() {
    log "INFO" "Attempting to fix model issues..."
    
    # Check for issues in model files
    python_files=("oe_sale_dashboard_17/models/sale_dashboard.py" "oe_sale_dashboard_17/models/sales_dashboard_performer.py")
    
    for file in "${python_files[@]}"; do
        log "INFO" "Checking model file: $file"
        
        # Fix common model issues
        
        # 1. Check if _name is defined
        if ! grep -q "_name =" "$file"; then
            log "ERROR" "Missing _name attribute in $file"
            # Determine the appropriate model name from filename
            model_name=$(basename "$file" .py | tr '_' '.' | sed 's/^sale/sales/')
            sed -i "/class /a \ \ \ \ _name = '$model_name'" "$file"
            log "SUCCESS" "Added _name = '$model_name' to $file"
            ((ISSUES_FIXED++))
        fi
        
        # 2. Check if _description is defined
        if ! grep -q "_description =" "$file"; then
            log "ERROR" "Missing _description attribute in $file"
            # Create a human-readable description
            description=$(basename "$file" .py | sed 's/_/ /g' | sed 's/\b\(.\)/\u\1/g')
            sed -i "/class /a \ \ \ \ _description = '$description'" "$file"
            log "SUCCESS" "Added _description to $file"
            ((ISSUES_FIXED++))
        fi
    done
    
    # Update __init__.py if needed
    if ! grep -q "sales_dashboard_performer" "oe_sale_dashboard_17/models/__init__.py"; then
        log "WARNING" "Missing import for sales_dashboard_performer in __init__.py"
        echo "from . import sales_dashboard_performer" >> "oe_sale_dashboard_17/models/__init__.py"
        log "SUCCESS" "Added import for sales_dashboard_performer"
        ((ISSUES_FIXED++))
    fi
    
    log "INFO" "Model fixes completed."
}

# Function to create security file if missing
create_security_file() {
    log "INFO" "Creating basic security file..."
    
    mkdir -p "oe_sale_dashboard_17/security"
    
    # Create basic access rights
    cat > "oe_sale_dashboard_17/security/ir.model.access.csv" << EOF
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_sales_dashboard_user,sales.dashboard.user,model_sales_dashboard,sales_team.group_sale_salesman,1,1,1,0
access_sales_dashboard_manager,sales.dashboard.manager,model_sales_dashboard,sales_team.group_sale_manager,1,1,1,1
access_sales_dashboard_performer_user,sales.dashboard.performer.user,model_sales_dashboard_performer,sales_team.group_sale_salesman,1,0,0,0
access_sales_dashboard_performer_manager,sales.dashboard.performer.manager,model_sales_dashboard_performer,sales_team.group_sale_manager,1,1,1,1
EOF

    log "SUCCESS" "Created basic security file with user and manager access rights"
    ((ISSUES_FIXED++))
    
    # Update manifest if needed
    if ! grep -q "security/ir.model.access.csv" "oe_sale_dashboard_17/__manifest__.py"; then
        sed -i "/data': \[/a \ \ \ \ \ \ \ \ 'security/ir.model.access.csv'," "oe_sale_dashboard_17/__manifest__.py"
        log "SUCCESS" "Updated manifest to include security file"
        ((ISSUES_FIXED++))
    fi
}

# Function to add security rule
add_security_rule() {
    local model=$1
    log "INFO" "Adding security rule for $model..."
    
    # Append to existing file
    echo "access_${model}_user,${model//_/.}.user,model_$model,sales_team.group_sale_salesman,1,1,1,0" >> "oe_sale_dashboard_17/security/ir.model.access.csv"
    echo "access_${model}_manager,${model//_/.}.manager,model_$model,sales_team.group_sale_manager,1,1,1,1" >> "oe_sale_dashboard_17/security/ir.model.access.csv"
    
    log "SUCCESS" "Added user and manager security rules for $model"
    ((ISSUES_FIXED+=2))
}

# Function to fix view issues
fix_view_issues() {
    log "INFO" "Attempting to fix view issues..."
    
    # List of view files
    view_files=$(find oe_sale_dashboard_17/views -name "*.xml")
    
    for file in $view_files; do
        log "INFO" "Checking view file: $file"
        
        # Fix common view issues
        
        # 1. Fix XML declaration
        if ! grep -q "<?xml" "$file"; then
            sed -i '1s/^/<?xml version="1.0" encoding="UTF-8"?>\n/' "$file"
            log "SUCCESS" "Added XML declaration to $file"
            ((ISSUES_FIXED++))
        fi
        
        # 2. Fix missing Odoo root tag
        if ! grep -q "<odoo>" "$file"; then
            content=$(cat "$file" | grep -v "<?xml")
            echo '<?xml version="1.0" encoding="UTF-8"?>' > "$file"
            echo '<odoo>' >> "$file"
            echo "$content" >> "$file"
            echo '</odoo>' >> "$file"
            log "SUCCESS" "Added <odoo> root tag to $file"
            ((ISSUES_FIXED++))
        fi
        
        # 3. Fix missing closing tags by validating XML
        if ! xmllint --noout "$file" 2>/dev/null; then
            log "WARNING" "XML validation failed for $file"
            # Backup file before attempting fixes
            cp "$file" "${file}.bak"
            
            # Simple fixes for common issues
            sed -i 's/<field name="\([^"]*\)" required>/<field name="\1" required="1">/' "$file"
            sed -i 's/<field name="\([^"]*\)" readonly>/<field name="\1" readonly="1">/' "$file"
            
            # Check if fixed
            if xmllint --noout "$file" 2>/dev/null; then
                log "SUCCESS" "Fixed XML syntax in $file"
                ((ISSUES_FIXED++))
            else
                log "ERROR" "Could not automatically fix XML in $file. Manual intervention required."
                # Restore backup if fixes failed
                mv "${file}.bak" "$file"
            fi
        fi
    done
    
    log "INFO" "View fixes completed."
}

# Function to fix missing assets
fix_missing_assets() {
    log "INFO" "Attempting to fix missing assets..."
    
    # Ensure directories exist
    mkdir -p "oe_sale_dashboard_17/static/src/js"
    mkdir -p "oe_sale_dashboard_17/static/src/css"
    mkdir -p "oe_sale_dashboard_17/static/src/xml"
    
    # Create basic placeholder files if missing
    
    # 1. Check for chart.min.js
    if [ ! -f "oe_sale_dashboard_17/static/src/js/chart.min.js" ]; then
        log "WARNING" "Creating placeholder for chart.min.js"
        echo "// Chart.js placeholder - Download from CDN in production" > "oe_sale_dashboard_17/static/src/js/chart.min.js"
        ((ISSUES_FIXED++))
    fi
    
    # 2. Check for compatibility.js
    if [ ! -f "oe_sale_dashboard_17/static/src/js/compatibility.js" ]; then
        log "WARNING" "Creating placeholder for compatibility.js"
        cat > "oe_sale_dashboard_17/static/src/js/compatibility.js" << EOF
/** @odoo-module */

// Compatibility layer for Odoo 17 JS features
export const SalesDashboardCompatibility = {
    init: function() {
        console.log("Sales Dashboard compatibility layer initialized");
    }
};

export default SalesDashboardCompatibility;
EOF
        ((ISSUES_FIXED++))
    fi
    
    # 3. Check for field_mapping.js
    if [ ! -f "oe_sale_dashboard_17/static/src/js/field_mapping.js" ]; then
        log "WARNING" "Creating placeholder for field_mapping.js"
        cat > "oe_sale_dashboard_17/static/src/js/field_mapping.js" << EOF
/** @odoo-module */

// Field mapping configuration for Sales Dashboard
export const FIELD_MAPPING = {
    // Define field mappings here
    'sales.dashboard': {
        revenue: 'total_revenue',
        orders: 'total_orders',
        average: 'avg_order_value'
    }
};

export default FIELD_MAPPING;
EOF
        ((ISSUES_FIXED++))
    fi
    
    # 4. Check for dashboard_merged.js
    if [ ! -f "oe_sale_dashboard_17/static/src/js/dashboard_merged.js" ]; then
        log "WARNING" "Creating placeholder for dashboard_merged.js"
        cat > "oe_sale_dashboard_17/static/src/js/dashboard_merged.js" << EOF
/** @odoo-module */
import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { FIELD_MAPPING } from "./field_mapping";

export class SalesDashboardController extends Component {
    static template = "oe_sale_dashboard_17.Dashboard";
    
    setup() {
        this.orm = useService("orm");
        this.state = useState({
            data: {},
            loading: true,
        });
        
        onWillStart(async () => {
            await this.loadDashboardData();
        });
    }
    
    async loadDashboardData() {
        try {
            this.state.data = await this.orm.call(
                'sales.dashboard',
                'get_dashboard_data',
                []
            );
            this.state.loading = false;
        } catch (error) {
            console.error("Failed to load dashboard data", error);
            this.state.loading = false;
        }
    }
}

registry.category("actions").add("oe_sale_dashboard_17.action_dashboard", SalesDashboardController);
EOF
        ((ISSUES_FIXED++))
    fi
    
    # 5. Check for dashboard_merged.css
    if [ ! -f "oe_sale_dashboard_17/static/src/css/dashboard_merged.css" ]; then
        log "WARNING" "Creating placeholder for dashboard_merged.css"
        cat > "oe_sale_dashboard_17/static/src/css/dashboard_merged.css" << EOF
/* Sales Dashboard CSS */
.o_sales_dashboard {
    padding: 1.5rem;
}

.o_sales_dashboard .o_dashboard_card {
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    margin-bottom: 1rem;
    padding: 1rem;
}

.o_sales_dashboard .o_dashboard_kpi {
    font-size: 24px;
    font-weight: bold;
    color: #875A7B;
}

.o_sales_dashboard .o_dashboard_title {
    font-size: 18px;
    font-weight: bold;
    margin-bottom: 1rem;
}
EOF
        ((ISSUES_FIXED++))
    fi
    
    # 6. Check for dashboard_merged_template.xml
    if [ ! -f "oe_sale_dashboard_17/static/src/xml/dashboard_merged_template.xml" ]; then
        log "WARNING" "Creating placeholder for dashboard_merged_template.xml"
        cat > "oe_sale_dashboard_17/static/src/xml/dashboard_merged_template.xml" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
    <t t-name="oe_sale_dashboard_17.Dashboard">
        <div class="o_sales_dashboard">
            <div t-if="state.loading" class="text-center py-5">
                <i class="fa fa-spinner fa-spin fa-2x"></i>
                <p>Loading dashboard data...</p>
            </div>
            <div t-else="" class="row">
                <!-- KPI Section -->
                <div class="col-12 col-md-6 col-lg-3 mb-4">
                    <div class="o_dashboard_card">
                        <div class="o_dashboard_title">Revenue</div>
                        <div class="o_dashboard_kpi">
                            <t t-esc="state.data.total_revenue || 0"></t>
                        </div>
                    </div>
                </div>
                <div class="col-12 col-md-6 col-lg-3 mb-4">
                    <div class="o_dashboard_card">
                        <div class="o_dashboard_title">Orders</div>
                        <div class="o_dashboard_kpi">
                            <t t-esc="state.data.total_orders || 0"></t>
                        </div>
                    </div>
                </div>
                <div class="col-12 col-md-6 col-lg-3 mb-4">
                    <div class="o_dashboard_card">
                        <div class="o_dashboard_title">Average Order</div>
                        <div class="o_dashboard_kpi">
                            <t t-esc="state.data.avg_order_value || 0"></t>
                        </div>
                    </div>
                </div>
                <div class="col-12 col-md-6 col-lg-3 mb-4">
                    <div class="o_dashboard_card">
                        <div class="o_dashboard_title">Conversion Rate</div>
                        <div class="o_dashboard_kpi">
                            <t t-esc="state.data.conversion_rate || 0"></t>%
                        </div>
                    </div>
                </div>
                
                <!-- Chart will be rendered here -->
                <div class="col-12 mt-4">
                    <div class="o_dashboard_card">
                        <div class="o_dashboard_title">Sales Trend</div>
                        <canvas id="salesChart" height="300"></canvas>
                    </div>
                </div>
            </div>
        </div>
    </t>
</templates>
EOF
        ((ISSUES_FIXED++))
    fi
    
    log "INFO" "Asset fixes completed."
}

# Function to generate test report
generate_report() {
    log "INFO" "Generating test report..."
    
    echo "
=======================================================
    oe_sale_dashboard_17 MODULE TEST REPORT
=======================================================

Test Date: $(date)
Issues Found: $ISSUES_FOUND
Issues Fixed: $ISSUES_FIXED

SUMMARY:
" > "oe_sale_dashboard_17_test_report.txt"
    
    # Add summary information from log
    grep -E "^\[(ERROR|WARNING|SUCCESS)\]" "$LOG_FILE" >> "oe_sale_dashboard_17_test_report.txt"
    
    echo "
RECOMMENDATIONS:
" >> "oe_sale_dashboard_17_test_report.txt"
    
    # Generate recommendations based on found issues
    if [ $ISSUES_FOUND -eq 0 ]; then
        echo "✅ Module appears to be working correctly. No issues found." >> "oe_sale_dashboard_17_test_report.txt"
    else
        if grep -q "Missing.*file\|directory" "$LOG_FILE"; then
            echo "⚠️ Fix module structure - ensure all required files and directories are present." >> "oe_sale_dashboard_17_test_report.txt"
        fi
        
        if grep -q "Missing.*dependency" "$LOG_FILE"; then
            echo "⚠️ Update module dependencies in __manifest__.py." >> "oe_sale_dashboard_17_test_report.txt"
        fi
        
        if grep -q "XML.*validation failed\|XML syntax error" "$LOG_FILE"; then
            echo "⚠️ Fix XML syntax issues in view files." >> "oe_sale_dashboard_17_test_report.txt"
        fi
        
        if grep -q "Missing.*asset" "$LOG_FILE"; then
            echo "⚠️ Add missing JavaScript/CSS assets or fix asset declarations." >> "oe_sale_dashboard_17_test_report.txt"
        fi
        
        if grep -q "security.*missing" "$LOG_FILE"; then
            echo "⚠️ Fix security access rights in ir.model.access.csv." >> "oe_sale_dashboard_17_test_report.txt"
        fi
    fi
    
    echo "
See $LOG_FILE for detailed test information.
" >> "oe_sale_dashboard_17_test_report.txt"
    
    log "SUCCESS" "Test report generated: oe_sale_dashboard_17_test_report.txt"
}

# Main execution
main() {
    log "INFO" "Starting systematic testing of oe_sale_dashboard_17 module"
    
    # Initial checks
    check_docker_running
    check_containers
    
    # Validate module structure
    validate_module_structure
    check_manifest
    
    # Test module installation
    test_module_installation
    
    # Validate models and security
    validate_models
    validate_security
    
    # Validate views and assets
    validate_views
    check_js_assets
    
    # Generate test report
    generate_report
    
    # Print summary
    log "INFO" "Testing completed!"
    log "INFO" "Found $ISSUES_FOUND issues, fixed $ISSUES_FIXED issues"
    log "INFO" "See $LOG_FILE for details and oe_sale_dashboard_17_test_report.txt for summary"
}

# Run main function
main