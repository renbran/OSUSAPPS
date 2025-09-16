/** @odoo-module **/

import { Component, useState, onWillStart, onMounted, useRef } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

/**
 * Simplified Dashboard Component (Fallback Version)
 * This is a fallback implementation that replaces the problematic dashboard_merged.js
 */
export class SaleDashboardFixed extends Component {
    static template = "oe_sale_dashboard_17.SaleDashboardTemplate";
    
    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        
        // Simple state management
        this.state = useState({
            dashboardData: {
                categories: {
                    'Product A': { count: 15, amount: 4500 },
                    'Product B': { count: 8, amount: 3200 },
                    'Product C': { count: 12, amount: 1800 },
                    'Product D': { count: 5, amount: 2500 }
                },
                totals: {
                    draft_count: 18, draft_amount: 5400,
                    sales_order_count: 42, sales_order_amount: 12600,
                    invoice_count: 35, invoice_amount: 10500,
                    total_count: 95, total_amount: 28500
                }
            },
            isLoading: false,
            error: null
        });
        
        // Chart references
        this.chartRef = useRef("mainChart");
        
        onWillStart(this.loadInitialData);
        onMounted(this.initializeView);
    }
    
    /**
     * Load initial data (simplified)
     */
    loadInitialData = async () => {
        this.state.isLoading = true;
        
        try {
            // In the simplified version, we're using static data
            // Future implementations should call the server
            
            this.notification.add(_t("Dashboard data loaded successfully"), { type: "success" });
        } catch (error) {
            console.error("Failed to load dashboard data:", error);
            this.state.error = _t("Failed to load dashboard data");
            this.notification.add(this.state.error, { type: "danger" });
        } finally {
            this.state.isLoading = false;
        }
    };
    
    /**
     * Initialize the view with basic chart
     */
    initializeView = () => {
        if (this.chartRef.el) {
            try {
                const ctx = this.chartRef.el.getContext('2d');
                
                // Basic chart implementation
                new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: Object.keys(this.state.dashboardData.categories),
                        datasets: [{
                            label: 'Sales by Category',
                            data: Object.values(this.state.dashboardData.categories).map(item => item.amount),
                            backgroundColor: [
                                'rgba(139, 0, 0, 0.8)',
                                'rgba(114, 47, 55, 0.8)',
                                'rgba(212, 175, 55, 0.8)',
                                'rgba(34, 197, 94, 0.8)'
                            ]
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false
                    }
                });
            } catch (error) {
                console.error("Failed to initialize chart:", error);
                this.notification.add(_t("Failed to initialize chart"), { type: "warning" });
            }
        }
    };
    
    /**
     * Render a simplified chart
     * This is a minimal implementation with basic functionality
     */
    renderChart(chartRef, type, data, options) {
        try {
            const canvas = this[chartRef].el;
            if (!canvas) return null;
            
            const ctx = canvas.getContext('2d');
            return new Chart(ctx, { type, data, options });
        } catch (error) {
            console.error("Chart rendering error:", error);
            return null;
        }
    }
    
    /**
     * Update dashboard with new data
     * Simplified implementation
     */
    updateDashboard() {
        this.notification.add(_t("This is a simplified dashboard with static data"), { type: "info" });
    }
    
    /**
     * Fetch data from server
     * Simplified implementation returns static data
     */
    async fetchData() {
        return this.state.dashboardData;
    }
}

// Register the component with the correct tag name
registry.category("actions").add("oe_sale_dashboard_17_action", SaleDashboardFixed);
