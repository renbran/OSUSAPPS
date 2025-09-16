#!/bin/bash

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}====== Sales Dashboard 17 Module Test & Fix ======${NC}"

# Check if docker is running
echo -e "${BLUE}1. Checking Docker environment...${NC}"
docker ps > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo -e "${RED}Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

echo -e "${YELLOW}Starting Docker containers...${NC}"
docker-compose down
docker-compose up -d
sleep 15
CONTAINER_ID=$(docker ps -qf "name=odoo")
if [ -z "$CONTAINER_ID" ]; then
    echo -e "${RED}Failed to start Odoo container.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker environment is running${NC}"

# Check if module directory is mounted
echo -e "${BLUE}2. Checking module directory...${NC}"
# Add module directory to docker-compose
echo -e "${YELLOW}Updating docker-compose.yml to add module mount...${NC}"

grep -q "oe_sale_dashboard_17:/mnt/extra-addons/oe_sale_dashboard_17" docker-compose.yml
if [ $? -ne 0 ]; then
    # Add the module volume mount
    sed -i '/enhanced_status:/a\\      - ./oe_sale_dashboard_17:/mnt/extra-addons/oe_sale_dashboard_17' docker-compose.yml
    
    echo -e "${GREEN}Updated docker-compose.yml${NC}"
    echo -e "${YELLOW}Restarting Docker containers...${NC}"
    docker-compose down
    docker-compose up -d
    sleep 15
    
    CONTAINER_ID=$(docker ps -qf "name=odoo")
    if [ -z "$CONTAINER_ID" ]; then
        echo -e "${RED}Failed to restart Odoo container.${NC}"
        exit 1
    fi
fi
echo -e "${GREEN}✓ Module directory is mounted${NC}"

# Check manifest file
echo -e "${BLUE}3. Checking manifest file...${NC}"
docker exec $CONTAINER_ID ls -la /mnt/extra-addons/oe_sale_dashboard_17/__manifest__.py > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo -e "${RED}Manifest file not found.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Manifest file exists${NC}"

# Check models
echo -e "${BLUE}4. Checking models...${NC}"
PERFORMER_EXISTS=$(docker exec $CONTAINER_ID bash -c "test -f /mnt/extra-addons/oe_sale_dashboard_17/models/sales_dashboard_performer.py && echo 'yes' || echo 'no'")
if [ "$PERFORMER_EXISTS" = "no" ]; then
    echo -e "${YELLOW}Missing sales_dashboard_performer.py model. Creating...${NC}"
    
    cat << 'EOF' > /tmp/sales_dashboard_performer.py
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
    
    docker cp /tmp/sales_dashboard_performer.py $CONTAINER_ID:/mnt/extra-addons/oe_sale_dashboard_17/models/
    
    # Update __init__.py if needed
    INIT_FILE=$(docker exec $CONTAINER_ID cat /mnt/extra-addons/oe_sale_dashboard_17/models/__init__.py)
    if [[ ! $INIT_FILE == *"sales_dashboard_performer"* ]]; then
        docker exec $CONTAINER_ID bash -c "echo 'from . import sales_dashboard_performer' >> /mnt/extra-addons/oe_sale_dashboard_17/models/__init__.py"
    fi
    
    echo -e "${GREEN}✓ Created sales_dashboard_performer.py model${NC}"
else
    echo -e "${GREEN}✓ sales_dashboard_performer.py model exists${NC}"
fi

# Check static assets
echo -e "${BLUE}5. Checking static assets...${NC}"

# Check dashboard_merged.js
JS_EXISTS=$(docker exec $CONTAINER_ID bash -c "test -f /mnt/extra-addons/oe_sale_dashboard_17/static/src/js/dashboard_merged.js && echo 'yes' || echo 'no'")
if [ "$JS_EXISTS" = "no" ]; then
    echo -e "${YELLOW}Missing dashboard_merged.js. Creating...${NC}"
    
    # Create directory if needed
    docker exec $CONTAINER_ID mkdir -p /mnt/extra-addons/oe_sale_dashboard_17/static/src/js
    
    # Create the file
    cat << 'EOF' > /tmp/dashboard_merged.js
/**
 * Merged dashboard functionality for Sales Dashboard 17
 */
odoo.define('oe_sale_dashboard_17.Dashboard', function (require) {
"use strict";

var AbstractAction = require('web.AbstractAction');
var core = require('web.core');
var QWeb = core.qweb;
var rpc = require('web.rpc');
var session = require('web.session');

var SalesDashboard = AbstractAction.extend({
    template: 'SalesDashboardTemplate',
    
    events: {
        'click .dashboard-filter-button': '_onFilterClick',
    },
    
    init: function(parent, action) {
        this._super(parent, action);
        this.actionManager = parent;
        this.date_range = 'month';
    },
    
    start: function() {
        var self = this;
        return this._super.apply(this, arguments).then(function() {
            self._loadDashboardData();
        });
    },
    
    _loadDashboardData: function() {
        var self = this;
        return this._rpc({
            model: 'sales.dashboard',
            method: 'get_dashboard_data',
            args: [this.date_range],
        }).then(function(result) {
            self._renderDashboard(result);
        });
    },
    
    _renderDashboard: function(data) {
        var self = this;
        this.$('.o_sales_dashboard').empty();
        this.$('.o_sales_dashboard').append(QWeb.render('SalesDashboardContent', {
            widget: self,
            data: data
        }));
        this._initCharts(data);
    },
    
    _initCharts: function(data) {
        // Initialize charts if Chart.js is available
        if (typeof Chart !== 'undefined') {
            this._renderSalesChart(data.sales_data);
            this._renderInvoiceChart(data.invoice_data);
        } else {
            console.error('Chart.js library not loaded');
            this.$('.dashboard-chart-container').text('Chart library not available');
        }
    },
    
    _renderSalesChart: function(data) {
        var ctx = this.$('#salesChart');
        if (ctx.length) {
            var salesChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Sales',
                        data: data.values,
                        backgroundColor: '#36A2EB'
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
    },
    
    _renderInvoiceChart: function(data) {
        var ctx = this.$('#invoiceChart');
        if (ctx.length) {
            var invoiceChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Invoices',
                        data: data.values,
                        borderColor: '#FF6384',
                        fill: false
                    }]
                },
                options: {
                    responsive: true,
                }
            });
        }
    },
    
    _onFilterClick: function(ev) {
        var $target = $(ev.currentTarget);
        this.date_range = $target.data('range');
        this.$('.dashboard-filter-button').removeClass('active');
        $target.addClass('active');
        this._loadDashboardData();
    }
});

core.action_registry.add('sales_dashboard_action', SalesDashboard);

return SalesDashboard;
});
EOF
    
    docker cp /tmp/dashboard_merged.js $CONTAINER_ID:/mnt/extra-addons/oe_sale_dashboard_17/static/src/js/
    echo -e "${GREEN}✓ Created dashboard_merged.js${NC}"
else
    echo -e "${GREEN}✓ dashboard_merged.js exists${NC}"
fi

# Check dashboard_merged.css
CSS_EXISTS=$(docker exec $CONTAINER_ID bash -c "test -f /mnt/extra-addons/oe_sale_dashboard_17/static/src/css/dashboard_merged.css && echo 'yes' || echo 'no'")
if [ "$CSS_EXISTS" = "no" ]; then
    echo -e "${YELLOW}Missing dashboard_merged.css. Creating...${NC}"
    
    # Create directory if needed
    docker exec $CONTAINER_ID mkdir -p /mnt/extra-addons/oe_sale_dashboard_17/static/src/css
    
    # Create the file
    cat << 'EOF' > /tmp/dashboard_merged.css
/* Sales Dashboard 17 CSS */
.o_sales_dashboard {
    padding: 15px;
    background-color: #f9f9f9;
}

.dashboard-card {
    background-color: #fff;
    border-radius: 5px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
    padding: 15px;
    margin-bottom: 15px;
}

.dashboard-card-title {
    font-size: 16px;
    font-weight: bold;
    color: #4c4c4c;
    margin-bottom: 10px;
}

.dashboard-value {
    font-size: 24px;
    font-weight: bold;
    color: #212529;
}

.dashboard-subtitle {
    font-size: 12px;
    color: #6c757d;
}

.dashboard-positive {
    color: #28a745;
}

.dashboard-negative {
    color: #dc3545;
}

.dashboard-chart-container {
    min-height: 250px;
    position: relative;
}

.dashboard-filter-container {
    margin-bottom: 20px;
    text-align: right;
}

.dashboard-filter-button {
    background-color: #f8f9fa;
    border: 1px solid #ddd;
    color: #495057;
    padding: 5px 10px;
    border-radius: 3px;
    margin-left: 5px;
    cursor: pointer;
}

.dashboard-filter-button.active {
    background-color: #007bff;
    color: white;
    border-color: #007bff;
}

/* Responsive styles */
@media (max-width: 768px) {
    .dashboard-value {
        font-size: 20px;
    }
    
    .dashboard-chart-container {
        min-height: 200px;
    }
}
EOF
    
    docker cp /tmp/dashboard_merged.css $CONTAINER_ID:/mnt/extra-addons/oe_sale_dashboard_17/static/src/css/
    echo -e "${GREEN}✓ Created dashboard_merged.css${NC}"
else
    echo -e "${GREEN}✓ dashboard_merged.css exists${NC}"
fi

# Check chart.min.js
CHART_EXISTS=$(docker exec $CONTAINER_ID bash -c "test -f /mnt/extra-addons/oe_sale_dashboard_17/static/src/js/chart.min.js && echo 'yes' || echo 'no'")
if [ "$CHART_EXISTS" = "no" ]; then
    echo -e "${YELLOW}Missing chart.min.js. Downloading...${NC}"
    docker exec $CONTAINER_ID bash -c "cd /mnt/extra-addons/oe_sale_dashboard_17/static/src/js && wget -O chart.min.js https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.min.js"
    echo -e "${GREEN}✓ Downloaded chart.min.js${NC}"
else
    echo -e "${GREEN}✓ chart.min.js exists${NC}"
fi

# Check dashboard_merged_template.xml
TEMPLATE_EXISTS=$(docker exec $CONTAINER_ID bash -c "test -f /mnt/extra-addons/oe_sale_dashboard_17/static/src/xml/dashboard_merged_template.xml && echo 'yes' || echo 'no'")
if [ "$TEMPLATE_EXISTS" = "no" ]; then
    echo -e "${YELLOW}Missing dashboard_merged_template.xml. Creating...${NC}"
    
    # Create directory if needed
    docker exec $CONTAINER_ID mkdir -p /mnt/extra-addons/oe_sale_dashboard_17/static/src/xml
    
    # Create the file
    cat << 'EOF' > /tmp/dashboard_merged_template.xml
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
    <t t-name="SalesDashboardTemplate">
        <div class="o_sales_dashboard">
            <div class="dashboard-filter-container">
                <button class="dashboard-filter-button active" data-range="day">Today</button>
                <button class="dashboard-filter-button" data-range="week">This Week</button>
                <button class="dashboard-filter-button" data-range="month">This Month</button>
                <button class="dashboard-filter-button" data-range="quarter">This Quarter</button>
                <button class="dashboard-filter-button" data-range="year">This Year</button>
            </div>
            <div class="row">
                <div class="col-lg-3 col-md-6 col-sm-12">
                    <div class="dashboard-card">
                        <div class="dashboard-card-title">Sales</div>
                        <div class="dashboard-value">0.00</div>
                        <div class="dashboard-subtitle">No data available</div>
                    </div>
                </div>
                <div class="col-lg-3 col-md-6 col-sm-12">
                    <div class="dashboard-card">
                        <div class="dashboard-card-title">Orders</div>
                        <div class="dashboard-value">0</div>
                        <div class="dashboard-subtitle">No data available</div>
                    </div>
                </div>
                <div class="col-lg-3 col-md-6 col-sm-12">
                    <div class="dashboard-card">
                        <div class="dashboard-card-title">Invoices</div>
                        <div class="dashboard-value">0.00</div>
                        <div class="dashboard-subtitle">No data available</div>
                    </div>
                </div>
                <div class="col-lg-3 col-md-6 col-sm-12">
                    <div class="dashboard-card">
                        <div class="dashboard-card-title">Outstanding</div>
                        <div class="dashboard-value">0.00</div>
                        <div class="dashboard-subtitle">No data available</div>
                    </div>
                </div>
            </div>
            <div class="row mt-3">
                <div class="col-lg-6 col-md-12">
                    <div class="dashboard-card">
                        <div class="dashboard-card-title">Sales Trend</div>
                        <div class="dashboard-chart-container">
                            <canvas id="salesChart"></canvas>
                        </div>
                    </div>
                </div>
                <div class="col-lg-6 col-md-12">
                    <div class="dashboard-card">
                        <div class="dashboard-card-title">Invoice Trend</div>
                        <div class="dashboard-chart-container">
                            <canvas id="invoiceChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </t>
</templates>
EOF
    
    docker cp /tmp/dashboard_merged_template.xml $CONTAINER_ID:/mnt/extra-addons/oe_sale_dashboard_17/static/src/xml/
    echo -e "${GREEN}✓ Created dashboard_merged_template.xml${NC}"
else
    echo -e "${GREEN}✓ dashboard_merged_template.xml exists${NC}"
fi

# Update/install the module
echo -e "${BLUE}6. Updating module...${NC}"
docker exec $CONTAINER_ID odoo --stop-after-init -d odoo --update=oe_sale_dashboard_17
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}Module update failed. Trying with module installation...${NC}"
    docker exec $CONTAINER_ID odoo --stop-after-init -d odoo --init=oe_sale_dashboard_17
    if [ $? -ne 0 ]; then
        echo -e "${RED}Module installation failed.${NC}"
        exit 1
    fi
fi
echo -e "${GREEN}✓ Module updated/installed successfully${NC}"

# Run module tests
echo -e "${BLUE}7. Running module tests...${NC}"
docker exec $CONTAINER_ID odoo --stop-after-init -d odoo --test-enable -i oe_sale_dashboard_17 > test_output.log 2>&1
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}Some tests failed. See test_output.log for details.${NC}"
else
    echo -e "${GREEN}✓ All tests passed successfully${NC}"
fi

# Summary
echo -e "\n${BLUE}===== Testing Summary =====${NC}"
echo -e "Module: oe_sale_dashboard_17"
echo -e "Date: $(date)"
echo -e "\n${GREEN}All tests and fixes have been completed.${NC}"
echo -e "\nYou can now access the Odoo instance at: ${BLUE}http://localhost:8090${NC}"
echo -e "Login: admin / admin"
echo -e "\nTo see the dashboard, go to Sales > ${YELLOW}Sales Analytics Hub${NC}"

# Print test results summary
if [ -f test_output.log ]; then
    echo -e "\n${BLUE}===== Test Results =====${NC}"
    grep -E "ERROR|FAIL|PASS" test_output.log | head -n 10
fi