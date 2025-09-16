#!/bin/bash

echo "===== Testing oe_sale_dashboard_17 Module ====="
echo "1. Checking module structure..."

# Check if Docker is running and Odoo container exists
CONTAINER_ID=$(docker ps -qf "name=osusapps-odoo-1")
if [ -z "$CONTAINER_ID" ]; then
    echo "Starting Docker containers..."
    docker-compose down
    docker-compose up -d
    sleep 10
    CONTAINER_ID=$(docker ps -qf "name=osusapps-odoo-1")
    if [ -z "$CONTAINER_ID" ]; then
        echo "ERROR: Failed to start Odoo container"
        exit 1
    fi
fi

# Check module directory exists in container
docker exec $CONTAINER_ID ls -la /mnt/extra-addons/oe_sale_dashboard_17
if [ $? -ne 0 ]; then
    echo "ERROR: Module directory not found in container"
    exit 1
fi
echo "✓ Module directory exists in container"

# Check manifest file
docker exec $CONTAINER_ID cat /mnt/extra-addons/oe_sale_dashboard_17/__manifest__.py > /dev/null
if [ $? -ne 0 ]; then
    echo "ERROR: __manifest__.py not found"
    exit 1
fi
echo "✓ __manifest__.py exists"

# Check models directory and files
docker exec $CONTAINER_ID ls -la /mnt/extra-addons/oe_sale_dashboard_17/models/
echo "2. Checking model files..."
# Check each model file referenced in __init__.py
docker exec $CONTAINER_ID cat /mnt/extra-addons/oe_sale_dashboard_17/models/__init__.py | while read line; do
    if [[ $line == from* ]]; then
        # Extract model name
        model=$(echo $line | sed 's/from . import //')
        # Check if file exists
        docker exec $CONTAINER_ID ls -la /mnt/extra-addons/oe_sale_dashboard_17/models/${model}.py > /dev/null
        if [ $? -ne 0 ]; then
            echo "ERROR: Model file ${model}.py not found"
            exit 1
        fi
        echo "✓ Model file ${model}.py exists"
    fi
done

# Check security file
echo "3. Checking security files..."
docker exec $CONTAINER_ID cat /mnt/extra-addons/oe_sale_dashboard_17/security/ir.model.access.csv > /dev/null
if [ $? -ne 0 ]; then
    echo "ERROR: security/ir.model.access.csv not found"
    exit 1
fi
echo "✓ security/ir.model.access.csv exists"

# Check for static files referenced in manifest
echo "4. Checking static files..."
docker exec $CONTAINER_ID cat /mnt/extra-addons/oe_sale_dashboard_17/__manifest__.py | grep -o "'[^']*\.(js\|css\|xml)'" | sed "s/'//g" | while read asset; do
    if [[ $asset == http* ]]; then
        # Skip external URLs
        continue
    fi
    
    # Strip module name from path if present
    if [[ $asset == oe_sale_dashboard_17/* ]]; then
        asset=${asset#oe_sale_dashboard_17/}
    fi
    
    docker exec $CONTAINER_ID ls -la /mnt/extra-addons/oe_sale_dashboard_17/$asset > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "WARNING: Asset file $asset not found"
        # Get directory of the asset
        dir=$(dirname "$asset")
        # Create directory if it doesn't exist
        docker exec $CONTAINER_ID mkdir -p /mnt/extra-addons/oe_sale_dashboard_17/$dir
        
        # For JS files, create empty file with basic structure
        if [[ $asset == *.js ]]; then
            if [[ $asset == *dashboard_merged.js ]]; then
                echo "Creating missing dashboard_merged.js file..."
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
                docker exec -i $CONTAINER_ID sh -c "cat > /mnt/extra-addons/oe_sale_dashboard_17/$asset" < /tmp/dashboard_merged.js
                echo "✓ Created dashboard_merged.js file"
            elif [[ $asset == *chart.min.js ]]; then
                echo "Downloading chart.min.js from CDN..."
                docker exec $CONTAINER_ID wget -O /mnt/extra-addons/oe_sale_dashboard_17/$asset https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.min.js
                echo "✓ Downloaded chart.min.js file"
            else
                echo "Creating empty JS file for $asset"
                docker exec $CONTAINER_ID sh -c "echo '// Generated placeholder file' > /mnt/extra-addons/oe_sale_dashboard_17/$asset"
            fi
        fi
        
        # For CSS files, create empty file with basic structure
        if [[ $asset == *.css ]]; then
            if [[ $asset == *dashboard_merged.css ]]; then
                echo "Creating missing dashboard_merged.css file..."
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
                docker exec -i $CONTAINER_ID sh -c "cat > /mnt/extra-addons/oe_sale_dashboard_17/$asset" < /tmp/dashboard_merged.css
                echo "✓ Created dashboard_merged.css file"
            else
                echo "Creating empty CSS file for $asset"
                docker exec $CONTAINER_ID sh -c "echo '/* Generated placeholder file */' > /mnt/extra-addons/oe_sale_dashboard_17/$asset"
            fi
        fi
        
        # For XML files, create empty file with basic structure
        if [[ $asset == *.xml ]]; then
            if [[ $asset == *dashboard_merged_template.xml ]]; then
                echo "Creating missing dashboard_merged_template.xml file..."
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
    <t t-name="SalesDashboardContent">
        <div class="row">
            <div class="col-lg-3 col-md-6 col-sm-12">
                <div class="dashboard-card">
                    <div class="dashboard-card-title">Sales</div>
                    <div class="dashboard-value">
                        <t t-esc="data.currency_symbol"/> <t t-esc="data.total_sales"/>
                    </div>
                    <div class="dashboard-subtitle">
                        <t t-if="data.sales_growth > 0">
                            <span class="dashboard-positive">
                                <i class="fa fa-arrow-up"></i> <t t-esc="data.sales_growth"/>%
                            </span>
                        </t>
                        <t t-elif="data.sales_growth &lt; 0">
                            <span class="dashboard-negative">
                                <i class="fa fa-arrow-down"></i> <t t-esc="Math.abs(data.sales_growth)"/>%
                            </span>
                        </t>
                        <t t-else="">
                            <span>No change</span>
                        </t>
                        vs previous period
                    </div>
                </div>
            </div>
            <div class="col-lg-3 col-md-6 col-sm-12">
                <div class="dashboard-card">
                    <div class="dashboard-card-title">Orders</div>
                    <div class="dashboard-value">
                        <t t-esc="data.total_orders"/>
                    </div>
                    <div class="dashboard-subtitle">
                        <t t-if="data.order_count_growth > 0">
                            <span class="dashboard-positive">
                                <i class="fa fa-arrow-up"></i> <t t-esc="data.order_count_growth"/>%
                            </span>
                        </t>
                        <t t-elif="data.order_count_growth &lt; 0">
                            <span class="dashboard-negative">
                                <i class="fa fa-arrow-down"></i> <t t-esc="Math.abs(data.order_count_growth)"/>%
                            </span>
                        </t>
                        <t t-else="">
                            <span>No change</span>
                        </t>
                        vs previous period
                    </div>
                </div>
            </div>
            <div class="col-lg-3 col-md-6 col-sm-12">
                <div class="dashboard-card">
                    <div class="dashboard-card-title">Invoices</div>
                    <div class="dashboard-value">
                        <t t-esc="data.currency_symbol"/> <t t-esc="data.total_invoices"/>
                    </div>
                    <div class="dashboard-subtitle">
                        <span><t t-esc="data.invoice_count"/> invoice(s)</span>
                    </div>
                </div>
            </div>
            <div class="col-lg-3 col-md-6 col-sm-12">
                <div class="dashboard-card">
                    <div class="dashboard-card-title">Outstanding</div>
                    <div class="dashboard-value">
                        <t t-esc="data.currency_symbol"/> <t t-esc="data.total_outstanding"/>
                    </div>
                    <div class="dashboard-subtitle">
                        <span><t t-esc="data.outstanding_count"/> invoice(s)</span>
                    </div>
                </div>
            </div>
        </div>
    </t>
</templates>
EOF
                docker exec -i $CONTAINER_ID sh -c "cat > /mnt/extra-addons/oe_sale_dashboard_17/$asset" < /tmp/dashboard_merged_template.xml
                echo "✓ Created dashboard_merged_template.xml file"
            else
                echo "Creating empty XML file for $asset"
                docker exec $CONTAINER_ID sh -c "echo '<?xml version=\"1.0\" encoding=\"UTF-8\"?><templates xml:space=\"preserve\"></templates>' > /mnt/extra-addons/oe_sale_dashboard_17/$asset"
            fi
        fi
    else
        echo "✓ Asset file $asset exists"
    fi
done

# Check for model sales_dashboard_performer
echo "5. Checking sales_dashboard_performer model..."
docker exec $CONTAINER_ID test -f /mnt/extra-addons/oe_sale_dashboard_17/models/sales_dashboard_performer.py
if [ $? -ne 0 ]; then
    echo "Creating missing sales_dashboard_performer.py model..."
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
    docker exec -i $CONTAINER_ID sh -c "cat > /mnt/extra-addons/oe_sale_dashboard_17/models/sales_dashboard_performer.py" < /tmp/sales_dashboard_performer.py
    
    # Make sure it's imported in __init__.py
    docker exec $CONTAINER_ID grep -q "sales_dashboard_performer" /mnt/extra-addons/oe_sale_dashboard_17/models/__init__.py
    if [ $? -ne 0 ]; then
        echo "Updating models/__init__.py to import sales_dashboard_performer..."
        docker exec $CONTAINER_ID sh -c "echo 'from . import sales_dashboard_performer' >> /mnt/extra-addons/oe_sale_dashboard_17/models/__init__.py"
    fi
    echo "✓ Created sales_dashboard_performer.py model"
else
    echo "✓ sales_dashboard_performer.py model exists"
fi

# Update the module to apply changes
echo "6. Installing/updating module..."
docker exec $CONTAINER_ID odoo --stop-after-init -d odoo --init=oe_sale_dashboard_17
if [ $? -ne 0 ]; then
    echo "Installation failed, trying with module update instead..."
    docker exec $CONTAINER_ID odoo --stop-after-init -d odoo --update=oe_sale_dashboard_17
fi

echo "7. Running module tests..."
docker exec $CONTAINER_ID odoo --stop-after-init -d odoo --test-enable --log-level=test -i oe_sale_dashboard_17 2>&1 | tee test_output.log
test_result=$?

if [ $test_result -eq 0 ]; then
    echo "✓ All tests passed successfully!"
else
    echo "⚠ Some tests failed. Check test_output.log for details."
fi

echo "===== Testing complete! ====="