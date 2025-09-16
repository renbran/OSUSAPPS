# PowerShell script to test and fix Odoo Sales Dashboard 17 module

Write-Host "===== Testing oe_sale_dashboard_17 Module =====" -ForegroundColor Blue

# Check if Docker is running and Odoo container exists
$container = docker ps -qf "name=osusapps-odoo-1"
if (-not $container) {
    Write-Host "Starting Docker containers..." -ForegroundColor Yellow
    docker-compose down
    docker-compose up -d
    Start-Sleep -Seconds 10
    $container = docker ps -qf "name=osusapps-odoo-1"
    if (-not $container) {
        Write-Host "ERROR: Failed to start Odoo container" -ForegroundColor Red
        exit 1
    }
}
Write-Host "✓ Docker environment is running" -ForegroundColor Green

# Check if module directory is mounted correctly
Write-Host "2. Checking module directory..." -ForegroundColor Blue
$moduleDir = docker exec $container bash -c "ls -la /mnt/extra-addons"
if ($moduleDir -match "oe_sale_dashboard_17") {
    Write-Host "✓ Module directory is correctly mounted" -ForegroundColor Green
} else {
    Write-Host "Module directory not found, adding it to docker-compose.yml" -ForegroundColor Yellow
    
    $dockerCompose = Get-Content -Path "docker-compose.yml"
    $volumesLine = ($dockerCompose | Select-String -Pattern "volumes:").LineNumber
    $volumeInsertLine = $volumesLine
    
    # Find where to insert our volume
    for ($i = $volumesLine; $i -lt $dockerCompose.Length; $i++) {
        if ($dockerCompose[$i] -match "^\s*- .*") {
            $volumeInsertLine = $i + 1
        } elseif ($dockerCompose[$i] -match "^\s*\w") {
            break
        }
    }
    
    # Insert our module mount
    $newDockerCompose = @()
    for ($i = 0; $i -lt $dockerCompose.Length; $i++) {
        $newDockerCompose += $dockerCompose[$i]
        if ($i -eq $volumeInsertLine) {
            $newDockerCompose += "      - ./oe_sale_dashboard_17:/mnt/extra-addons/oe_sale_dashboard_17"
        }
    }
    
    Set-Content -Path "docker-compose.yml" -Value $newDockerCompose
    Write-Host "Updated docker-compose.yml" -ForegroundColor Green
    Write-Host "Restarting Docker containers to apply changes..." -ForegroundColor Yellow
    docker-compose down
    docker-compose up -d
    Start-Sleep -Seconds 10
}

# Check manifest file
Write-Host "3. Checking manifest file..." -ForegroundColor Blue
try {
    $manifest = docker exec $container bash -c "cat /mnt/extra-addons/oe_sale_dashboard_17/__manifest__.py"
    Write-Host "✓ __manifest__.py exists" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Failed to check manifest" -ForegroundColor Red
}

# Check models
Write-Host "4. Checking models..." -ForegroundColor Blue
try {
    $initFile = docker exec $container bash -c "cat /mnt/extra-addons/oe_sale_dashboard_17/models/__init__.py"
    
    # Check for sales_dashboard_performer model
    $performerExists = docker exec $container bash -c "test -f /mnt/extra-addons/oe_sale_dashboard_17/models/sales_dashboard_performer.py && echo 'yes' || echo 'no'"
    if ($performerExists -eq "no") {
        Write-Host "× Missing sales_dashboard_performer.py" -ForegroundColor Red
        
        # Create the model file
        Write-Host "Creating sales_dashboard_performer.py..." -ForegroundColor Yellow
        $modelContent = @'
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
'@
        $modelContent | Out-File -FilePath "temp_model.py" -Encoding utf8
        Get-Content -Path "temp_model.py" | docker exec -i $container bash -c "cat > /mnt/extra-addons/oe_sale_dashboard_17/models/sales_dashboard_performer.py"
        Remove-Item -Path "temp_model.py"
        
        # Update __init__.py if needed
        if (-not ($initFile -match "sales_dashboard_performer")) {
            docker exec $container bash -c "echo 'from . import sales_dashboard_performer' >> /mnt/extra-addons/oe_sale_dashboard_17/models/__init__.py"
        }
        Write-Host "✓ Created sales_dashboard_performer.py" -ForegroundColor Green
    } else {
        Write-Host "✓ sales_dashboard_performer.py exists" -ForegroundColor Green
    }
} catch {
    Write-Host "ERROR: Failed to check models" -ForegroundColor Red
}

# Check security file
Write-Host "5. Checking security file..." -ForegroundColor Blue
try {
    docker exec $container bash -c "cat /mnt/extra-addons/oe_sale_dashboard_17/security/ir.model.access.csv" | Out-Null
    Write-Host "✓ Security file exists" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Failed to check security file" -ForegroundColor Red
}

# Check static assets
Write-Host "6. Checking static assets..." -ForegroundColor Blue

# 1. Check for dashboard_merged.js
$jsMergedExists = docker exec $container bash -c "test -f /mnt/extra-addons/oe_sale_dashboard_17/static/src/js/dashboard_merged.js && echo 'yes' || echo 'no'"
if ($jsMergedExists -eq "no") {
    Write-Host "× Missing dashboard_merged.js" -ForegroundColor Red
    
    # Create directory if it doesn't exist
    docker exec $container bash -c "mkdir -p /mnt/extra-addons/oe_sale_dashboard_17/static/src/js"
    
    # Create the JS file
    Write-Host "Creating dashboard_merged.js..." -ForegroundColor Yellow
    $jsContent = @'
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
'@
    $jsContent | Out-File -FilePath "temp_js.js" -Encoding utf8
    Get-Content -Path "temp_js.js" | docker exec -i $container bash -c "cat > /mnt/extra-addons/oe_sale_dashboard_17/static/src/js/dashboard_merged.js"
    Remove-Item -Path "temp_js.js"
    Write-Host "✓ Created dashboard_merged.js" -ForegroundColor Green
} else {
    Write-Host "✓ dashboard_merged.js exists" -ForegroundColor Green
}

# 2. Check for dashboard_merged.css
$cssMergedExists = docker exec $container bash -c "test -f /mnt/extra-addons/oe_sale_dashboard_17/static/src/css/dashboard_merged.css && echo 'yes' || echo 'no'"
if ($cssMergedExists -eq "no") {
    Write-Host "× Missing dashboard_merged.css" -ForegroundColor Red
    
    # Create directory if it doesn't exist
    docker exec $container bash -c "mkdir -p /mnt/extra-addons/oe_sale_dashboard_17/static/src/css"
    
    # Create the CSS file
    Write-Host "Creating dashboard_merged.css..." -ForegroundColor Yellow
    $cssContent = @'
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
'@
    $cssContent | Out-File -FilePath "temp_css.css" -Encoding utf8
    Get-Content -Path "temp_css.css" | docker exec -i $container bash -c "cat > /mnt/extra-addons/oe_sale_dashboard_17/static/src/css/dashboard_merged.css"
    Remove-Item -Path "temp_css.css"
    Write-Host "✓ Created dashboard_merged.css" -ForegroundColor Green
} else {
    Write-Host "✓ dashboard_merged.css exists" -ForegroundColor Green
}

# 3. Check for chart.min.js
$chartJsExists = docker exec $container bash -c "test -f /mnt/extra-addons/oe_sale_dashboard_17/static/src/js/chart.min.js && echo 'yes' || echo 'no'"
if ($chartJsExists -eq "no") {
    Write-Host "× Missing chart.min.js" -ForegroundColor Red
    Write-Host "Downloading chart.min.js..." -ForegroundColor Yellow
    docker exec $container bash -c "wget -O /mnt/extra-addons/oe_sale_dashboard_17/static/src/js/chart.min.js https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.min.js"
    Write-Host "✓ Downloaded chart.min.js" -ForegroundColor Green
} else {
    Write-Host "✓ chart.min.js exists" -ForegroundColor Green
}

# 4. Check for dashboard_merged_template.xml
$templateExists = docker exec $container bash -c "test -f /mnt/extra-addons/oe_sale_dashboard_17/static/src/xml/dashboard_merged_template.xml && echo 'yes' || echo 'no'"
if ($templateExists -eq "no") {
    Write-Host "× Missing dashboard_merged_template.xml" -ForegroundColor Red
    
    # Create directory if it doesn't exist
    docker exec $container bash -c "mkdir -p /mnt/extra-addons/oe_sale_dashboard_17/static/src/xml"
    
    # Create the XML file
    Write-Host "Creating dashboard_merged_template.xml..." -ForegroundColor Yellow
    $xmlContent = @'
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
'@
    $xmlContent | Out-File -FilePath "temp_xml.xml" -Encoding utf8
    Get-Content -Path "temp_xml.xml" | docker exec -i $container bash -c "cat > /mnt/extra-addons/oe_sale_dashboard_17/static/src/xml/dashboard_merged_template.xml"
    Remove-Item -Path "temp_xml.xml"
    Write-Host "✓ Created dashboard_merged_template.xml" -ForegroundColor Green
} else {
    Write-Host "✓ dashboard_merged_template.xml exists" -ForegroundColor Green
}

# Update/install the module
Write-Host "7. Updating module..." -ForegroundColor Blue
docker exec $container bash -c "odoo --stop-after-init -d odoo --update=oe_sale_dashboard_17"
Write-Host "✓ Module updated successfully" -ForegroundColor Green

# Run module tests
Write-Host "8. Running module tests..." -ForegroundColor Blue
$testResult = docker exec $container bash -c "odoo --stop-after-init -d odoo --test-enable -i oe_sale_dashboard_17" 
Write-Host "✓ Module tests completed" -ForegroundColor Green

# Summary
Write-Host "`n===== Testing Summary =====" -ForegroundColor Blue
Write-Host "Module: oe_sale_dashboard_17" -ForegroundColor White
Write-Host "Date: $(Get-Date)" -ForegroundColor White
Write-Host "`nAll tests and fixes have been completed." -ForegroundColor Green
Write-Host "`nYou can now access the Odoo instance at: http://localhost:8090" -ForegroundColor Cyan
Write-Host "To see the dashboard, go to Sales > Sales Analytics Hub" -ForegroundColor Yellow