#!/bin/bash
# oe_sale_dashboard_17_fix.sh
# Comprehensive fix for OE Sale Dashboard 17
# Created on: September 16, 2025

echo "========== OE SALE DASHBOARD 17 FIX SCRIPT =========="
echo "Started at $(date)"

# Ensure we're in the right directory
cd "$(dirname "$0")" || exit 1
SCRIPT_DIR=$(pwd)

# Check if Docker is running
echo "Checking Docker environment..."
if ! docker ps &>/dev/null; then
    echo "ERROR: Docker is not running or not accessible"
    exit 1
fi

# Get container name
CONTAINER_NAME=$(docker ps --filter name=odoo --format "{{.Names}}")
if [ -z "$CONTAINER_NAME" ]; then
    echo "ERROR: Odoo container not found"
    exit 1
fi

echo "Using container: $CONTAINER_NAME"

# 1. Fix Template and Component Registration Mismatch
echo "[FIX 1] Fixing template and component registration mismatch..."

# Fix the dashboard_merged.js file - update component registration
echo "Updating component registration in dashboard_merged.js..."
docker exec $CONTAINER_NAME bash -c "cat > /tmp/fix_component_registration.js << 'EOF'
/** @odoo-module **/

import { Component, useState, onWillStart, onMounted, useRef, onWillUnmount } from \"@odoo/owl\";
import { registry } from \"@web/core/registry\";
import { useService } from \"@web/core/utils/hooks\";
import { _t } from \"@web/core/l10n/translation\";

export class SaleDashboardMerged extends Component {
    static template = \"oe_sale_dashboard_17.SaleDashboardTemplate\";

    // Rest of the file remains unchanged
EOF"

# Create necessary missing functions
echo "Adding missing functions (renderChart, updateDashboard, fetchData)..."
docker exec $CONTAINER_NAME bash -c "cat > /tmp/missing_functions.js << 'EOF'
    /**
     * Render chart based on provided data and options
     * @param {string} chartRef - Reference to chart canvas
     * @param {string} type - Type of chart (line, bar, pie, etc.)
     * @param {Object} data - Chart data object
     * @param {Object} options - Chart configuration options
     * @returns {Chart} - Chart instance
     */
    renderChart(chartRef, type, data, options) {
        try {
            // Clean up existing chart instance if it exists
            if (this.state.charts[chartRef] && typeof this.state.charts[chartRef].destroy === 'function') {
                this.state.charts[chartRef].destroy();
            }
            
            // Get the canvas context
            const canvas = this[chartRef].el;
            if (!canvas) {
                console.error(`Canvas element not found for ${chartRef}`);
                return null;
            }
            
            const ctx = canvas.getContext('2d');
            
            // Create and store new chart instance
            const chart = new Chart(ctx, {
                type,
                data,
                options
            });
            
            // Update state with new chart instance
            this.state.charts[chartRef] = chart;
            
            return chart;
        } catch (error) {
            this.handleError(\`Failed to render chart (${chartRef})\`, error);
            return null;
        }
    }
    
    /**
     * Update dashboard with new data
     * @param {boolean} showLoading - Whether to show loading indicator
     */
    async updateDashboard(showLoading = true) {
        try {
            // Avoid concurrent updates
            if (this.state.isLoading) return;
            
            // Show loading state if requested
            if (showLoading) {
                this.state.isLoading = true;
            }
            
            const startTime = performance.now();
            
            // Fetch the data
            const data = await this.fetchData();
            
            // Update state with new data
            this.state.dashboardData = data;
            this.state.lastRefresh = new Date();
            this.state.loadTime = performance.now() - startTime;
            
            // Update data quality indicator based on load time
            if (this.state.loadTime < 1000) {
                this.state.dataQuality = 'excellent';
            } else if (this.state.loadTime < 3000) {
                this.state.dataQuality = 'good';
            } else {
                this.state.dataQuality = 'degraded';
            }
            
            // Update all charts with new data
            this.updateAllCharts();
            
            // Show success message
            if (showLoading) {
                this.notification.add(_t("Dashboard updated successfully"), { type: "success" });
            }
        } catch (error) {
            this.handleError(_t("Failed to update dashboard"), error);
        } finally {
            // Hide loading state
            this.state.isLoading = false;
        }
    }
    
    /**
     * Fetch data from the server
     * @returns {Promise<Object>} - Dashboard data
     */
    async fetchData() {
        try {
            // Prepare the parameters
            const params = {
                start_date: this.state.filters.startDate,
                end_date: this.state.filters.endDate,
                sales_types: this.state.filters.selectedSalesTypes,
            };
            
            // Call the ORM method to fetch dashboard data
            const result = await this.orm.call(
                'sale.order',
                'get_dashboard_data',
                [],
                { params }
            );
            
            // Process and return the data
            return this.processServerData(result);
        } catch (error) {
            throw new Error(\`Data fetch error: ${error.message || error}\`);
        }
    }
    
    /**
     * Process raw server data into dashboard-ready format
     * @param {Object} rawData - Raw data from server
     * @returns {Object} - Processed dashboard data
     */
    processServerData(rawData) {
        // Default structure in case of empty data
        const defaultData = {
            categories: {},
            totals: {
                draft_count: 0, draft_amount: 0,
                sales_order_count: 0, sales_order_amount: 0,
                invoice_count: 0, invoice_amount: 0,
                total_count: 0, total_amount: 0,
                conversion_rate: 0, avg_deal_size: 0,
                revenue_growth: 0, pipeline_velocity: 0
            },
            metadata: {
                date_field_used: 'booking_date',
                has_sales_types: true,
                has_sale_value: true
            }
        };
        
        // If no data returned, use defaults
        if (!rawData) {
            return defaultData;
        }
        
        // Process and enhance the data
        try {
            // Enhanced KPIs calculations
            if (rawData.totals) {
                // Calculate conversion rate if possible
                if (rawData.totals.draft_count > 0) {
                    rawData.totals.conversion_rate = ((rawData.totals.sales_order_count / 
                        (rawData.totals.draft_count + rawData.totals.sales_order_count)) * 100).toFixed(2);
                }
                
                // Calculate average deal size
                if (rawData.totals.sales_order_count > 0) {
                    rawData.totals.avg_deal_size = (rawData.totals.sales_order_amount / 
                        rawData.totals.sales_order_count).toFixed(2);
                }
            }
            
            return { ...defaultData, ...rawData };
        } catch (error) {
            console.error("Error processing server data:", error);
            return defaultData;
        }
    }
EOF"

# Fix component registration at end of file
echo "Fixing component registration at end of file..."
docker exec $CONTAINER_NAME bash -c "cat > /tmp/fix_registry.js << 'EOF'
}

// Register the component with the correct registry that matches dashboard_views.xml
registry.category(\"actions\").add(\"oe_sale_dashboard_17_action\", SaleDashboardMerged);
EOF"

# Apply the fixes to the dashboard_merged.js file
echo "Applying fixes to dashboard_merged.js..."
docker exec $CONTAINER_NAME bash -c "cd /mnt/extra-addons/oe_sale_dashboard_17/static/src/js/ && \
    head -n 8 dashboard_merged.js > dashboard_merged.js.new && \
    cat /tmp/fix_component_registration.js >> dashboard_merged.js.new && \
    tail -n +12 dashboard_merged.js | head -n 830 >> dashboard_merged.js.new && \
    cat /tmp/missing_functions.js >> dashboard_merged.js.new && \
    cat /tmp/fix_registry.js >> dashboard_merged.js.new && \
    cp dashboard_merged.js dashboard_merged.js.bak && \
    mv dashboard_merged.js.new dashboard_merged.js"

# 2. Fix manifest dependencies and assets
echo "[FIX 2] Updating manifest and assets section..."
docker exec $CONTAINER_NAME bash -c "cat > /tmp/fix_manifest.py << 'EOF'
import json
import os

# Path to the manifest file
manifest_path = '/mnt/extra-addons/oe_sale_dashboard_17/__manifest__.py'

# Read the current manifest
with open(manifest_path, 'r') as f:
    content = f.read()

# Extract the relevant part (everything between { and })
start = content.find('{')
end = content.rfind('}') + 1
manifest_dict_str = content[start:end]

# Convert tabs to spaces and handle multi-line strings for proper eval
manifest_dict_str = manifest_dict_str.replace('\t', '    ')
manifest_dict = eval(manifest_dict_str)

# Fix the assets section - replace the CDN URL with local chart.js
if 'assets' in manifest_dict:
    assets_backend = manifest_dict['assets'].get('web.assets_backend', [])
    
    # Remove CDN URL if present
    cdn_url = 'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js'
    if cdn_url in assets_backend:
        assets_backend.remove(cdn_url)
    
    # Ensure local chart.min.js is included
    chart_js = 'oe_sale_dashboard_17/static/src/js/chart.min.js'
    if chart_js not in assets_backend:
        assets_backend.insert(1, chart_js)
    
    # Update the manifest dictionary
    manifest_dict['assets']['web.assets_backend'] = assets_backend

# Save the updated manifest
with open(manifest_path, 'w') as f:
    f.write(content[:start])
    f.write(json.dumps(manifest_dict, indent=4))
    f.write(content[end:])

print("Manifest updated successfully")
EOF"

# Execute the Python script to fix the manifest
echo "Executing manifest fix script..."
docker exec $CONTAINER_NAME python3 /tmp/fix_manifest.py

# 3. Restart Odoo to apply fixes
echo "[FIX 3] Restarting Odoo to apply changes..."
docker restart $CONTAINER_NAME

# Wait for Odoo to start
echo "Waiting for Odoo to restart..."
sleep 10

# 4. Update the module
echo "[FIX 4] Updating the OE Sale Dashboard 17 module..."
docker exec $CONTAINER_NAME odoo --update=oe_sale_dashboard_17 --stop-after-init

echo "Fix script completed at $(date)"
echo "Please verify the dashboard functionality in Odoo"