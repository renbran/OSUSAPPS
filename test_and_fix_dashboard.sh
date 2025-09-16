#!/bin/bash

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}====== Sales Dashboard 17 Testing and Fix Script ======${NC}"

# Function to start Docker services
start_docker_services() {
    echo -e "${BLUE}Starting Docker services...${NC}"
    docker-compose down
    docker-compose up -d
    # Wait for Odoo to become available
    echo -e "${YELLOW}Waiting for Odoo to start (this may take a minute)...${NC}"
    max_retries=30
    retry_count=0
    while ! curl -s http://localhost:8090/web/database/selector > /dev/null 2>&1; do
        retry_count=$((retry_count+1))
        if [ $retry_count -ge $max_retries ]; then
            echo -e "${RED}Timed out waiting for Odoo to start${NC}"
            exit 1
        fi
        echo -n "."
        sleep 3
    done
    echo ""
    echo -e "${GREEN}Odoo is now running!${NC}"
    # Additional delay to ensure the service is fully initialized
    sleep 5
}

# Function to run test script
run_tests() {
    echo -e "${BLUE}Running module tests...${NC}"
    python test_oe_sale_dashboard.py --host localhost --port 8090 --db odoo --user admin --password admin
    test_exit=$?
    
    if [ $test_exit -eq 0 ]; then
        echo -e "${GREEN}All tests passed successfully!${NC}"
        return 0
    else
        echo -e "${YELLOW}Tests detected issues. Analyzing and fixing...${NC}"
        return 1
    fi
}

# Function to fix common module issues
fix_module_issues() {
    echo -e "${BLUE}Analyzing test results and fixing issues...${NC}"
    
    # Process test results JSON file
    if [ -f "dashboard_test_results.json" ]; then
        # Check for model-related errors
        if grep -q "Model.*does not exist" dashboard_test_log.txt; then
            echo -e "${YELLOW}Found missing model definition. Fixing...${NC}"
            # Validate models/__init__.py has correct imports
            docker-compose exec odoo bash -c "cd /mnt/extra-addons/oe_sale_dashboard_17 && cat models/__init__.py"
            
            # Check specific model files
            docker-compose exec odoo bash -c "ls -la /mnt/extra-addons/oe_sale_dashboard_17/models/"
            
            # If sales_dashboard_performer.py doesn't exist but is referenced in security, fix it
            performer_exists=$(docker-compose exec odoo bash -c "[ -f /mnt/extra-addons/oe_sale_dashboard_17/models/sales_dashboard_performer.py ] && echo 'yes' || echo 'no'")
            if [ "$performer_exists" == "no" ]; then
                echo -e "${YELLOW}Creating missing sales_dashboard_performer.py model...${NC}"
                cat > temp_model_fix.py << 'EOF'
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SalesDashboardPerformer(models.Model):
    _name = 'sales.dashboard.performer'
    _description = 'Sales Dashboard Performance Metrics'
    _order = 'score desc'

    name = fields.Char(string="Name", required=True)
    user_id = fields.Many2one('res.users', string="Salesperson")
    team_id = fields.Many2one('crm.team', string="Sales Team")
    period = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly')
    ], string="Period", default='monthly')
    
    sale_count = fields.Integer(string="Sale Count")
    revenue = fields.Float(string="Revenue")
    target = fields.Float(string="Target")
    achievement = fields.Float(string="Achievement %", compute="_compute_achievement")
    score = fields.Float(string="Performance Score", compute="_compute_score")
    
    @api.depends('revenue', 'target')
    def _compute_achievement(self):
        for rec in self:
            if rec.target and rec.target > 0:
                rec.achievement = (rec.revenue / rec.target) * 100
            else:
                rec.achievement = 0
    
    @api.depends('achievement', 'sale_count')
    def _compute_score(self):
        for rec in self:
            # Simple scoring algorithm: 70% achievement + 30% sale count (normalized)
            achievement_score = min(100, rec.achievement) * 0.7
            count_score = min(100, rec.sale_count * 2) * 0.3  # Assuming 50 is a high count
            rec.score = achievement_score + count_score
EOF
                docker-compose exec -T odoo bash -c "cat > /mnt/extra-addons/oe_sale_dashboard_17/models/sales_dashboard_performer.py" < temp_model_fix.py
                rm temp_model_fix.py
                
                # Ensure it's imported in __init__.py if not already
                init_content=$(docker-compose exec odoo bash -c "cat /mnt/extra-addons/oe_sale_dashboard_17/models/__init__.py")
                if ! echo "$init_content" | grep -q "sales_dashboard_performer"; then
                    echo -e "${YELLOW}Updating model imports in __init__.py...${NC}"
                    docker-compose exec odoo bash -c "echo 'from . import sales_dashboard_performer' >> /mnt/extra-addons/oe_sale_dashboard_17/models/__init__.py"
                fi
            fi
        fi
        
        # Check for asset loading errors
        if grep -q "Failed to load asset" dashboard_test_log.txt; then
            echo -e "${YELLOW}Found asset loading issues. Checking files...${NC}"
            
            # Check for missing JS files
            js_missing=$(docker-compose exec odoo bash -c "[ -f /mnt/extra-addons/oe_sale_dashboard_17/static/src/js/dashboard_merged.js ] && echo 'no' || echo 'yes'")
            if [ "$js_missing" == "yes" ]; then
                echo -e "${RED}dashboard_merged.js is missing. Checking for other JS files to consolidate...${NC}"
                
                # List all JS files to see what's available
                docker-compose exec odoo bash -c "find /mnt/extra-addons/oe_sale_dashboard_17/static/src/js -name '*.js'"
                
                # Check if we need to create or rename files
                original_js=$(docker-compose exec odoo bash -c "ls /mnt/extra-addons/oe_sale_dashboard_17/static/src/js/dashboard*.js 2>/dev/null || echo 'none'")
                if [ "$original_js" != "none" ]; then
                    echo -e "${YELLOW}Found source JS file, creating merged version...${NC}"
                    docker-compose exec odoo bash -c "cp /mnt/extra-addons/oe_sale_dashboard_17/static/src/js/dashboard.js /mnt/extra-addons/oe_sale_dashboard_17/static/src/js/dashboard_merged.js 2>/dev/null || echo 'Copy failed'"
                fi
            fi
            
            # Similar check for CSS files
            css_missing=$(docker-compose exec odoo bash -c "[ -f /mnt/extra-addons/oe_sale_dashboard_17/static/src/css/dashboard_merged.css ] && echo 'no' || echo 'yes'")
            if [ "$css_missing" == "yes" ]; then
                echo -e "${RED}dashboard_merged.css is missing. Checking for other CSS files...${NC}"
                
                # List all CSS files
                docker-compose exec odoo bash -c "find /mnt/extra-addons/oe_sale_dashboard_17/static/src/css -name '*.css'"
                
                # Check if we need to create or rename files
                original_css=$(docker-compose exec odoo bash -c "ls /mnt/extra-addons/oe_sale_dashboard_17/static/src/css/dashboard*.css 2>/dev/null || echo 'none'")
                if [ "$original_css" != "none" ]; then
                    echo -e "${YELLOW}Found source CSS file, creating merged version...${NC}"
                    docker-compose exec odoo bash -c "cp /mnt/extra-addons/oe_sale_dashboard_17/static/src/css/dashboard.css /mnt/extra-addons/oe_sale_dashboard_17/static/src/css/dashboard_merged.css 2>/dev/null || echo 'Copy failed'"
                fi
            fi
            
            # Ensure the chart.min.js file exists
            chart_missing=$(docker-compose exec odoo bash -c "[ -f /mnt/extra-addons/oe_sale_dashboard_17/static/src/js/chart.min.js ] && echo 'no' || echo 'yes'")
            if [ "$chart_missing" == "yes" ]; then
                echo -e "${YELLOW}chart.min.js is missing. Downloading from CDN...${NC}"
                docker-compose exec odoo bash -c "mkdir -p /mnt/extra-addons/oe_sale_dashboard_17/static/src/js/"
                docker-compose exec odoo bash -c "wget -O /mnt/extra-addons/oe_sale_dashboard_17/static/src/js/chart.min.js https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.min.js"
            fi
        fi
        
        # Check for menu-related errors
        if grep -q "Could not find Sales Analytics menu" dashboard_test_log.txt; then
            echo -e "${YELLOW}Menu items not properly created. Checking XML files...${NC}"
            
            # Check if dashboard_menu.xml exists and its content
            docker-compose exec odoo bash -c "cat /mnt/extra-addons/oe_sale_dashboard_17/views/dashboard_menu.xml"
        fi
    else
        echo -e "${RED}Test results file not found. Cannot analyze issues.${NC}"
        return 1
    fi
    
    echo -e "${BLUE}Applying fixes and updating module...${NC}"
    docker-compose exec odoo odoo -d odoo --update=oe_sale_dashboard_17 --stop-after-init
    return 0
}

# Main script
echo -e "${BLUE}Step 1: Starting Docker environment${NC}"
start_docker_services

echo -e "${BLUE}Step 2: Running initial tests${NC}"
run_tests
test_result=$?

if [ $test_result -ne 0 ]; then
    echo -e "${BLUE}Step 3: Fixing detected issues${NC}"
    fix_module_issues
    
    echo -e "${BLUE}Step 4: Running tests again to verify fixes${NC}"
    run_tests
    retest_result=$?
    
    if [ $retest_result -eq 0 ]; then
        echo -e "${GREEN}✅ All issues have been resolved successfully!${NC}"
    else
        echo -e "${RED}❌ Some issues could not be automatically fixed. Manual intervention required.${NC}"
        echo -e "${YELLOW}Please check dashboard_test_log.txt and dashboard_test_results.json for details.${NC}"
    fi
else
    echo -e "${GREEN}✅ No issues detected. Module is working correctly!${NC}"
fi

echo -e "${BLUE}=============== Testing Complete ===============${NC}"