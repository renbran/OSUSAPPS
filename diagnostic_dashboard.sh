#!/bin/bash

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Log file
LOG_FILE="dashboard_diagnostic_$(date +"%Y%m%d_%H%M%S").log"
REPORT_FILE="dashboard_diagnostic_report.txt"

# Function to log messages
log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

log "${BLUE}========== OE SALE DASHBOARD 17 DETAILED DIAGNOSTICS ==========${NC}"
log "Started at $(date)"
log ""

# Check Docker is running
log "${YELLOW}Checking Docker environment...${NC}"
if ! docker info > /dev/null 2>&1; then
    log "${RED}ERROR: Docker is not running.${NC}"
    exit 1
fi

# Check containers are running
log "${YELLOW}Checking container status...${NC}"
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
log "${GREEN}Docker environment is ready${NC}"

# DIAGNOSTIC 1: Check module structure
log "\n${BLUE}[DIAGNOSTIC 1] Checking module structure...${NC}"

# Check __init__.py files
log "${YELLOW}Checking __init__.py files...${NC}"
docker exec $CONTAINER_ID bash -c "cat /mnt/extra-addons/oe_sale_dashboard_17/__init__.py" > /tmp/init_main.txt
docker exec $CONTAINER_ID bash -c "cat /mnt/extra-addons/oe_sale_dashboard_17/models/__init__.py" > /tmp/init_models.txt

log "Main __init__.py:"
cat /tmp/init_main.txt | tee -a "$LOG_FILE"
log "\nModels __init__.py:"
cat /tmp/init_models.txt | tee -a "$LOG_FILE"

# Check if directories exist
log "\n${YELLOW}Checking directory structure...${NC}"
for dir in "models" "views" "security" "static" "static/src/js" "static/src/css" "static/src/xml"; do
    if docker exec $CONTAINER_ID bash -c "[ -d /mnt/extra-addons/oe_sale_dashboard_17/$dir ]"; then
        log "${GREEN}Directory $dir exists${NC}"
    else
        log "${RED}Directory $dir does not exist${NC}"
    fi
done

# DIAGNOSTIC 2: Detailed installation test with error capture
log "\n${BLUE}[DIAGNOSTIC 2] Detailed installation test...${NC}"

# Reset database to ensure clean state
log "${YELLOW}Resetting database for clean test...${NC}"
docker-compose exec db psql -U odoo -d postgres -c "DROP DATABASE odoo WITH (FORCE)"
docker-compose exec db psql -U odoo -d postgres -c "CREATE DATABASE odoo OWNER odoo"
sleep 5

# Try module installation with detailed error logging
log "${YELLOW}Installing module with debug logging...${NC}"
docker-compose exec odoo odoo -d odoo -i base,web --no-http --stop-after-init > /dev/null 2>&1
INSTALL_OUTPUT=$(docker-compose exec odoo odoo -d odoo -i oe_sale_dashboard_17 --no-http --stop-after-init --log-level=debug 2>&1)

echo "$INSTALL_OUTPUT" > /tmp/install_full.log
log "Saved full installation log to /tmp/install_full.log"

# Extract errors and warnings
grep -iE 'error|warning|traceback|exception' /tmp/install_full.log > /tmp/install_errors.log

# Log errors
if [ -s /tmp/install_errors.log ]; then
    log "${RED}Installation errors found:${NC}"
    cat /tmp/install_errors.log | tee -a "$LOG_FILE"
else
    log "${GREEN}No installation errors found${NC}"
fi

# DIAGNOSTIC 3: Check model definitions
log "\n${BLUE}[DIAGNOSTIC 3] Checking model definitions...${NC}"

# Create script to check model definitions
cat > /tmp/check_models.py << 'EOF'
import odoo
from odoo import api, fields, models, SUPERUSER_ID
from contextlib import closing
import sys
import json
import traceback

def check_models():
    errors = []
    warnings = []
    info = []
    
    try:
        odoo.tools.config['db_name'] = 'odoo'
        with odoo.api.Environment.manage():
            registry = odoo.modules.registry.Registry.new('odoo')
            with closing(registry.cursor()) as cr:
                env = odoo.api.Environment(cr, SUPERUSER_ID, {})
                
                # Check if module is installed
                module = env['ir.module.module'].search([('name', '=', 'oe_sale_dashboard_17')])
                if not module:
                    errors.append("Module oe_sale_dashboard_17 not found in ir.module.module")
                    return {"errors": errors, "warnings": warnings, "info": info}
                
                info.append(f"Module state: {module.state}")
                
                # Check expected models
                expected_models = [
                    'sales.dashboard',
                    'sales.dashboard.performer',
                    'sales.dashboard.analytics'
                ]
                
                for model_name in expected_models:
                    if model_name in env:
                        model_obj = env[model_name]
                        info.append(f"Model {model_name} exists")
                        
                        # Check fields
                        try:
                            fields_info = {}
                            for field_name, field in model_obj._fields.items():
                                field_type = field.type
                                fields_info[field_name] = field_type
                            info.append(f"Fields for {model_name}: {json.dumps(fields_info)}")
                        except Exception as e:
                            errors.append(f"Error checking fields for {model_name}: {str(e)}")
                    else:
                        errors.append(f"Model {model_name} not found")
                
                # Check views
                View = env['ir.ui.view']
                for model_name in expected_models:
                    views = View.search([('model', '=', model_name)])
                    if views:
                        info.append(f"Found {len(views)} views for {model_name}")
                        for view in views:
                            info.append(f"View: {view.name} (type: {view.type}, id: {view.id})")
                    else:
                        warnings.append(f"No views found for model {model_name}")
                
                # Check menu items
                Menu = env['ir.ui.menu']
                dashboard_menus = Menu.search([('name', 'ilike', '%dashboard%'), ('name', 'ilike', '%sale%')])
                if dashboard_menus:
                    info.append(f"Found {len(dashboard_menus)} dashboard menu items")
                    for menu in dashboard_menus:
                        info.append(f"Menu: {menu.name} (id: {menu.id}, parent: {menu.parent_id.name if menu.parent_id else 'None'})")
                else:
                    warnings.append("No dashboard menu items found")
                
                # Check JavaScript assets
                IrAsset = env['ir.asset']
                js_assets = IrAsset.search([('path', 'like', 'oe_sale_dashboard_17'), ('path', 'like', '.js')])
                if js_assets:
                    info.append(f"Found {len(js_assets)} JavaScript assets")
                    for asset in js_assets:
                        info.append(f"Asset: {asset.path} (target: {asset.target})")
                else:
                    warnings.append("No JavaScript assets found for module")
                    
    except Exception as e:
        errors.append(f"Unexpected error: {str(e)}")
        errors.append(traceback.format_exc())
        
    return {"errors": errors, "warnings": warnings, "info": info}

if __name__ == '__main__':
    result = check_models()
    print(json.dumps(result))
EOF

# Run the model check script
log "${YELLOW}Checking model definitions...${NC}"
docker cp /tmp/check_models.py $CONTAINER_ID:/tmp/
MODEL_CHECK=$(docker-compose exec odoo python3 /tmp/check_models.py)

# Parse and display results
if [ $? -eq 0 ]; then
    # Save raw output
    echo "$MODEL_CHECK" > /tmp/model_check_raw.json
    
    # Parse and display errors
    ERROR_COUNT=$(echo "$MODEL_CHECK" | grep -o '"errors":\s*\[[^]]*\]' | grep -o '"' | wc -l)
    WARN_COUNT=$(echo "$MODEL_CHECK" | grep -o '"warnings":\s*\[[^]]*\]' | grep -o '"' | wc -l)
    
    if [ $ERROR_COUNT -gt 1 ]; then
        log "${RED}Model definition errors found:${NC}"
        echo "$MODEL_CHECK" | grep -o '"errors":\s*\[[^]]*\]' | sed 's/"errors": \[\|\]//g' | tr -d ',' | sed 's/"//g' | tee -a "$LOG_FILE"
    else
        log "${GREEN}No model definition errors${NC}"
    fi
    
    if [ $WARN_COUNT -gt 1 ]; then
        log "${YELLOW}Model definition warnings:${NC}"
        echo "$MODEL_CHECK" | grep -o '"warnings":\s*\[[^]]*\]' | sed 's/"warnings": \[\|\]//g' | tr -d ',' | sed 's/"//g' | tee -a "$LOG_FILE"
    else
        log "${GREEN}No model definition warnings${NC}"
    fi
    
    # Display info
    log "${CYAN}Model information:${NC}"
    echo "$MODEL_CHECK" | grep -o '"info":\s*\[[^]]*\]' | sed 's/"info": \[\|\]//g' | tr -d ',' | sed 's/"//g' | tee -a "$LOG_FILE"
else
    log "${RED}Failed to run model check script${NC}"
fi

# DIAGNOSTIC 4: Check JavaScript files
log "\n${BLUE}[DIAGNOSTIC 4] Checking JavaScript files...${NC}"

# List all JS files
log "${YELLOW}Listing JavaScript files...${NC}"
JS_FILES=$(docker exec $CONTAINER_ID bash -c "find /mnt/extra-addons/oe_sale_dashboard_17/static -name '*.js' | sort")

if [ -z "$JS_FILES" ]; then
    log "${RED}No JavaScript files found${NC}"
else
    log "${GREEN}Found JavaScript files:${NC}"
    echo "$JS_FILES" | tee -a "$LOG_FILE"
    
    # Check content of key JS files
    log "\n${YELLOW}Checking key JavaScript file content...${NC}"
    CHART_FILE=$(echo "$JS_FILES" | grep "chart.min.js" || echo "")
    if [ -n "$CHART_FILE" ]; then
        JS_SIZE=$(docker exec $CONTAINER_ID bash -c "wc -l $CHART_FILE | awk '{print \$1}'")
        log "${CYAN}chart.min.js has $JS_SIZE lines${NC}"
        
        # Check if it's a proper Chart.js file
        CHART_CHECK=$(docker exec $CONTAINER_ID bash -c "grep -l 'Chart' $CHART_FILE")
        if [ -n "$CHART_CHECK" ]; then
            log "${GREEN}chart.min.js appears to be valid${NC}"
        else
            log "${RED}chart.min.js does not appear to be a valid Chart.js file${NC}"
        fi
    fi
    
    # Check main dashboard JS
    DASHBOARD_JS=$(echo "$JS_FILES" | grep "dashboard_merged.js" || echo "")
    if [ -n "$DASHBOARD_JS" ]; then
        JS_SIZE=$(docker exec $CONTAINER_ID bash -c "wc -l $DASHBOARD_JS | awk '{print \$1}'")
        log "${CYAN}dashboard_merged.js has $JS_SIZE lines${NC}"
        
        # Check for essential functions
        ESSENTIAL_FUNCTIONS=("renderChart" "updateDashboard" "fetchData")
        for func in "${ESSENTIAL_FUNCTIONS[@]}"; do
            FUNC_CHECK=$(docker exec $CONTAINER_ID bash -c "grep -l '$func' $DASHBOARD_JS")
            if [ -n "$FUNC_CHECK" ]; then
                log "${GREEN}Found function: $func${NC}"
            else
                log "${RED}Missing function: $func${NC}"
            fi
        done
    fi
fi

# DIAGNOSTIC 5: Check XML templates
log "\n${BLUE}[DIAGNOSTIC 5] Checking XML templates...${NC}"

# List all XML files
log "${YELLOW}Listing XML files...${NC}"
XML_FILES=$(docker exec $CONTAINER_ID bash -c "find /mnt/extra-addons/oe_sale_dashboard_17/static -name '*.xml' | sort")

if [ -z "$XML_FILES" ]; then
    log "${RED}No XML template files found in static directory${NC}"
else
    log "${GREEN}Found XML template files:${NC}"
    echo "$XML_FILES" | tee -a "$LOG_FILE"
    
    # Check for QWeb templates
    for xml_file in $XML_FILES; do
        TEMPLATES=$(docker exec $CONTAINER_ID bash -c "grep -c '<templates' $xml_file")
        if [ "$TEMPLATES" -gt 0 ]; then
            log "${GREEN}Found QWeb template in $xml_file${NC}"
            # Count template definitions
            T_COUNT=$(docker exec $CONTAINER_ID bash -c "grep -c '<t t-name=' $xml_file")
            log "${CYAN}File contains $T_COUNT template definitions${NC}"
        else
            log "${RED}No QWeb template found in $xml_file${NC}"
        fi
    done
fi

# DIAGNOSTIC 6: Check manifest for issues
log "\n${BLUE}[DIAGNOSTIC 6] Checking manifest for issues...${NC}"

# Get manifest content
log "${YELLOW}Analyzing manifest content...${NC}"
MANIFEST=$(docker exec $CONTAINER_ID bash -c "cat /mnt/extra-addons/oe_sale_dashboard_17/__manifest__.py")
echo "$MANIFEST" > /tmp/manifest.py

# Check for common manifest issues
ASSET_CHECK=$(grep -c "assets" /tmp/manifest.py)
if [ $ASSET_CHECK -gt 0 ]; then
    log "${GREEN}Found 'assets' section in manifest${NC}"
else
    log "${RED}Missing 'assets' section in manifest${NC}"
fi

# Check assets syntax
ASSET_SYNTAX=$(grep -A 20 "assets" /tmp/manifest.py)
log "${CYAN}Assets section:${NC}"
echo "$ASSET_SYNTAX" | tee -a "$LOG_FILE"

# Check external URLs
EXTERNAL_URLS=$(grep -c "https://" /tmp/manifest.py)
if [ $EXTERNAL_URLS -gt 0 ]; then
    log "${YELLOW}Found $EXTERNAL_URLS external URLs in manifest - these can cause issues${NC}"
    grep "https://" /tmp/manifest.py | tee -a "$LOG_FILE"
fi

# Generate final diagnostic report
log "\n${BLUE}========== DIAGNOSTIC SUMMARY ==========${NC}"

# Create summary report
cat > "$REPORT_FILE" << EOF
OE SALE DASHBOARD 17 - DIAGNOSTIC REPORT
========================================
Date: $(date)

STRUCTURE CHECK:
- Directory structure: $(if docker exec $CONTAINER_ID bash -c "[ -d /mnt/extra-addons/oe_sale_dashboard_17/models ] && [ -d /mnt/extra-addons/oe_sale_dashboard_17/views ] && [ -d /mnt/extra-addons/oe_sale_dashboard_17/security ]"; then echo "PASS"; else echo "FAIL"; fi)
- __init__.py files: $(if docker exec $CONTAINER_ID bash -c "[ -f /mnt/extra-addons/oe_sale_dashboard_17/__init__.py ] && [ -f /mnt/extra-addons/oe_sale_dashboard_17/models/__init__.py ]"; then echo "PASS"; else echo "FAIL"; fi)
- Security files: $(if docker exec $CONTAINER_ID bash -c "[ -f /mnt/extra-addons/oe_sale_dashboard_17/security/ir.model.access.csv ]"; then echo "PASS"; else echo "FAIL"; fi)

INSTALLATION CHECK:
- Installation errors: $(if [ -s /tmp/install_errors.log ]; then echo "FAIL"; else echo "PASS"; fi)
- External URLs in manifest: $(if [ $EXTERNAL_URLS -gt 0 ]; then echo "WARNING"; else echo "PASS"; fi)

JAVASCRIPT ASSETS:
- JS files present: $(if [ -z "$JS_FILES" ]; then echo "FAIL"; else echo "PASS"; fi)
- chart.min.js: $(if echo "$JS_FILES" | grep -q "chart.min.js"; then echo "PASS"; else echo "FAIL"; fi)
- dashboard_merged.js: $(if echo "$JS_FILES" | grep -q "dashboard_merged.js"; then echo "PASS"; else echo "FAIL"; fi)

XML TEMPLATES:
- XML files present: $(if [ -z "$XML_FILES" ]; then echo "FAIL"; else echo "PASS"; fi)
- QWeb templates found: $(if docker exec $CONTAINER_ID bash -c "grep -q '<templates' \$(find /mnt/extra-addons/oe_sale_dashboard_17/static -name '*.xml')"; then echo "PASS"; else echo "FAIL"; fi)

IDENTIFIED ISSUES:
EOF

# Add issues from diagnostics
if [ -s /tmp/install_errors.log ]; then
    echo "1. Installation errors found - see diagnostic log" >> "$REPORT_FILE"
    head -n 3 /tmp/install_errors.log >> "$REPORT_FILE"
    echo "..." >> "$REPORT_FILE"
fi

if [ $EXTERNAL_URLS -gt 0 ]; then
    echo "2. External URLs in manifest can cause issues with asset loading" >> "$REPORT_FILE"
    grep "https://" /tmp/manifest.py >> "$REPORT_FILE"
fi

if [ -z "$JS_FILES" ]; then
    echo "3. Missing JavaScript files" >> "$REPORT_FILE"
fi

if [ -z "$XML_FILES" ]; then
    echo "4. Missing XML template files" >> "$REPORT_FILE"
fi

# Conclude report
echo -e "\nRECOMMENDED FIXES:" >> "$REPORT_FILE"
if [ $EXTERNAL_URLS -gt 0 ]; then
    echo "- Replace external URLs with local assets" >> "$REPORT_FILE"
fi
if [ -s /tmp/install_errors.log ]; then
    echo "- Address installation errors shown in diagnostics" >> "$REPORT_FILE"
fi

log "${GREEN}Diagnostic report saved to $REPORT_FILE${NC}"
log "${YELLOW}See $LOG_FILE for detailed logs${NC}"
log "${BLUE}Diagnostics completed at $(date)${NC}"