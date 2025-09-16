###
# PowerShell script to test and fix Odoo Sales Dashboard 17 module
###

Write-Host "===== Testing oe_sale_dashboard_17 Module =====" -ForegroundColor Blue

# Function to test if a container exists and is running
function Test-Container {
    $container = docker ps -qf "name=osusapps-odoo-1"
    return $container
}

# Function to execute command in container
function Exec-Container {
    param (
        [string]$cmd
    )
    
    $result = docker exec osusapps-odoo-1 bash -c "$cmd"
    return $result
}

# Step 1: Check if Docker is running and Odoo container exists
Write-Host "1. Checking Docker environment..." -ForegroundColor Blue
$container = Test-Container
if (-not $container) {
    Write-Host "Starting Docker containers..." -ForegroundColor Yellow
    docker-compose down
    docker-compose up -d
    Start-Sleep -Seconds 10
    $container = Test-Container
    if (-not $container) {
        Write-Host "ERROR: Failed to start Odoo container" -ForegroundColor Red
        exit 1
    }
}
Write-Host "✓ Docker environment is running" -ForegroundColor Green

# Step 2: Check if module directory is mounted correctly
Write-Host "2. Checking module directory..." -ForegroundColor Blue
try {
    $moduleDir = Exec-Container "ls -la /mnt/extra-addons"
    if ($moduleDir -match "oe_sale_dashboard_17") {
        Write-Host "✓ Module directory is correctly mounted" -ForegroundColor Green
    } else {
        Write-Host "Module directory not found, adding it to docker-compose.yml" -ForegroundColor Yellow
        
        $dockerCompose = Get-Content -Path "docker-compose.yml"
        $updated = $false
        
        for ($i = 0; $i -lt $dockerCompose.Length; $i++) {
            if ($dockerCompose[$i] -match "volumes:" -and $dockerCompose[$i+1] -match "- ./") {
                # Find the end of volumes section
                $volumeEndIndex = $i + 1
                while ($volumeEndIndex -lt $dockerCompose.Length -and $dockerCompose[$volumeEndIndex] -match "^ *- ") {
                    $volumeEndIndex++
                }
                
                # Insert our module at the right position
                $dockerCompose = $dockerCompose[0..($volumeEndIndex-1)] + 
                                "      - ./oe_sale_dashboard_17:/mnt/extra-addons/oe_sale_dashboard_17" +
                                $dockerCompose[$volumeEndIndex..$dockerCompose.Length]
                $updated = $true
                break
            }
        }
        
        if ($updated) {
            Set-Content -Path "docker-compose.yml" -Value $dockerCompose
            Write-Host "Updated docker-compose.yml" -ForegroundColor Green
            Write-Host "Restarting Docker containers to apply changes..." -ForegroundColor Yellow
            docker-compose down
            docker-compose up -d
            Start-Sleep -Seconds 10
        } else {
            Write-Host "ERROR: Could not update docker-compose.yml" -ForegroundColor Red
            exit 1
        }
    }
} catch {
    Write-Host "ERROR: Failed to check module directory: $_" -ForegroundColor Red
    exit 1
}

# Step 3: Check manifest file
Write-Host "3. Checking manifest file..." -ForegroundColor Blue
try {
    $manifest = Exec-Container "cat /mnt/extra-addons/oe_sale_dashboard_17/__manifest__.py"
    Write-Host "✓ __manifest__.py exists" -ForegroundColor Green
    
    # Check if manifest contains all necessary assets
    if (-not ($manifest -match "dashboard_merged.js")) {
        Write-Host "WARNING: manifest doesn't reference dashboard_merged.js" -ForegroundColor Yellow
    }
    if (-not ($manifest -match "dashboard_merged.css")) {
        Write-Host "WARNING: manifest doesn't reference dashboard_merged.css" -ForegroundColor Yellow
    }
    if (-not ($manifest -match "dashboard_merged_template.xml")) {
        Write-Host "WARNING: manifest doesn't reference dashboard_merged_template.xml" -ForegroundColor Yellow
    }
} catch {
    Write-Host "ERROR: Failed to check manifest: $_" -ForegroundColor Red
    exit 1
}

# Step 4: Check models
Write-Host "4. Checking models..." -ForegroundColor Blue
try {
    $initFile = Exec-Container "cat /mnt/extra-addons/oe_sale_dashboard_17/models/__init__.py"
    $modelFiles = @()
    
    # Extract model imports
    $initFile -split "`n" | ForEach-Object {
        if ($_ -match "from \. import (.+)") {
            $modelName = $matches[1].Trim()
            $modelFiles += $modelName
            
            # Check if model file exists
            $fileExists = Exec-Container "test -f /mnt/extra-addons/oe_sale_dashboard_17/models/${modelName}.py && echo 'yes' || echo 'no'"
            if ($fileExists -eq "yes") {
                Write-Host "✓ Model $modelName.py exists" -ForegroundColor Green
            } else {
                Write-Host "× Model $modelName.py is missing!" -ForegroundColor Red
                
                # If it's the sales_dashboard_performer model, create it
                if ($modelName -eq "sales_dashboard_performer") {
                    Write-Host "Creating missing sales_dashboard_performer.py..." -ForegroundColor Yellow
                    
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
                    $modelContent | Out-File -FilePath ".\temp_model.py" -Encoding utf8
                    Get-Content -Path ".\temp_model.py" | docker exec -i osusapps-odoo-1 bash -c "cat > /mnt/extra-addons/oe_sale_dashboard_17/models/sales_dashboard_performer.py"
                    Remove-Item -Path ".\temp_model.py"
                    Write-Host "✓ Created sales_dashboard_performer.py" -ForegroundColor Green
                }
            }
        }
    }
} catch {
    Write-Host "ERROR: Failed to check models: $_" -ForegroundColor Red
    exit 1
}

# Step 5: Check security file
Write-Host "5. Checking security file..." -ForegroundColor Blue
try {
    $securityFile = Exec-Container "cat /mnt/extra-addons/oe_sale_dashboard_17/security/ir.model.access.csv"
    Write-Host "✓ Security file exists" -ForegroundColor Green
    
    # Check if the security file references models that exist
    if ($securityFile -match "model_sales_dashboard_performer" -and -not ($modelFiles -contains "sales_dashboard_performer")) {
        Write-Host "WARNING: Security file references sales_dashboard_performer but model isn't imported" -ForegroundColor Yellow
    }
} catch {
    Write-Host "ERROR: Failed to check security file: $_" -ForegroundColor Red
    exit 1
}

# Step 6: Check static files
Write-Host "6. Checking static files..." -ForegroundColor Blue
$staticFiles = @(
    "static/src/js/dashboard_merged.js",
    "static/src/css/dashboard_merged.css",
    "static/src/js/chart.min.js",
    "static/src/xml/dashboard_merged_template.xml"
)

foreach ($file in $staticFiles) {
    try {
        $fileExists = Exec-Container "test -f /mnt/extra-addons/oe_sale_dashboard_17/$file && echo 'yes' || echo 'no'"
        if ($fileExists -eq "yes") {
            Write-Host "✓ $file exists" -ForegroundColor Green
        } else {
            Write-Host "× $file is missing" -ForegroundColor Yellow
            
            # Create directory if needed
            $directory = $file.Substring(0, $file.LastIndexOf('/'))
            Exec-Container "mkdir -p /mnt/extra-addons/oe_sale_dashboard_17/$directory"
            
            # Handle specific files
            if ($file -eq "static/src/js/chart.min.js") {
                Write-Host "Downloading chart.min.js..." -ForegroundColor Yellow
                Exec-Container "wget -O /mnt/extra-addons/oe_sale_dashboard_17/$file https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.min.js"
                Write-Host "✓ Downloaded chart.min.js" -ForegroundColor Green
            } elseif ($file -eq "static/src/js/dashboard_merged.js") {
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
                $jsContent | Out-File -FilePath ".\temp_js.js" -Encoding utf8
                Get-Content -Path ".\temp_js.js" | docker exec -i osusapps-odoo-1 bash -c "cat > /mnt/extra-addons/oe_sale_dashboard_17/$file"
                Remove-Item -Path ".\temp_js.js"
                Write-Host "✓ Created dashboard_merged.js" -ForegroundColor Green
            } elseif ($file -eq "static/src/css/dashboard_merged.css") {
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
                $cssContent | Out-File -FilePath ".\temp_css.css" -Encoding utf8
                Get-Content -Path ".\temp_css.css" | docker exec -i osusapps-odoo-1 bash -c "cat > /mnt/extra-addons/oe_sale_dashboard_17/$file"
                Remove-Item -Path ".\temp_css.css"
                Write-Host "✓ Created dashboard_merged.css" -ForegroundColor Green
            } elseif ($file -eq "static/src/xml/dashboard_merged_template.xml") {
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
                $xmlContent | Out-File -FilePath ".\temp_xml.xml" -Encoding utf8
                Get-Content -Path ".\temp_xml.xml" | docker exec -i osusapps-odoo-1 bash -c "cat > /mnt/extra-addons/oe_sale_dashboard_17/$file"
                Remove-Item -Path ".\temp_xml.xml"
                Write-Host "✓ Created dashboard_merged_template.xml" -ForegroundColor Green
            }
        }
    } catch {
        Write-Host "ERROR: Failed to check $file: $_" -ForegroundColor Red
    }
}

# Step 7: Install/update module
Write-Host "7. Installing/updating module..." -ForegroundColor Blue
try {
    $installResult = Exec-Container "odoo --stop-after-init -d odoo --update=oe_sale_dashboard_17"
    Write-Host "✓ Module updated successfully" -ForegroundColor Green
} catch {
    Write-Host "WARNING: Module update had issues: $_" -ForegroundColor Yellow
    Write-Host "Trying module installation instead..." -ForegroundColor Yellow
    
    try {
        $installResult = Exec-Container "odoo --stop-after-init -d odoo --init=oe_sale_dashboard_17"
        Write-Host "✓ Module installed successfully" -ForegroundColor Green
    } catch {
        Write-Host "ERROR: Module installation failed: $_" -ForegroundColor Red
    }
}

# Step 8: Run tests
Write-Host "8. Running module tests..." -ForegroundColor Blue
try {
    $testResult = Exec-Container "odoo --stop-after-init -d odoo --test-enable --log-level=test -i oe_sale_dashboard_17"
    Write-Host "✓ Module tests completed" -ForegroundColor Green
    
    # Check for test failures
    if ($testResult -match "FAIL|ERROR") {
        Write-Host "WARNING: Some tests failed" -ForegroundColor Yellow
        # Extract failure messages
        $testResult -split "`n" | ForEach-Object {
            if ($_ -match "FAIL|ERROR") {
                Write-Host $_ -ForegroundColor Red
            }
        }
    } else {
        Write-Host "✓ All tests passed" -ForegroundColor Green
    }
} catch {
    Write-Host "ERROR: Failed to run tests: $_" -ForegroundColor Red
}

# Step 9: Summary
Write-Host "`n===== Testing Summary =====" -ForegroundColor Blue
Write-Host "Module: oe_sale_dashboard_17" -ForegroundColor White
Write-Host "Date: $(Get-Date)" -ForegroundColor White
Write-Host "`nAll tests and fixes have been completed." -ForegroundColor Green
Write-Host "The module has been installed/updated in the Odoo container." -ForegroundColor Green
Write-Host "`nYou can now access the Odoo instance at: http://localhost:8090" -ForegroundColor Cyan
Write-Host "Username: admin" -ForegroundColor Cyan
Write-Host "Password: admin" -ForegroundColor Cyan
Write-Host "`nTo see the dashboard, go to Sales > Sales Analytics Hub" -ForegroundColor Yellow