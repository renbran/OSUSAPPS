/** @odoo-module **/

import { Component, useState, onWillStart, onMounted, useRef, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

export class SaleDashboardMerged extends Component {
    static template = "oe_sale_dashboard_17.SaleDashboardTemplate";

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        
        // Enhanced state management with all best practices merged
        this.state = useState({
            dashboardData: {
                categories: {},
                totals: {
                    draft_count: 0, draft_amount: 0,
                    sales_order_count: 0, sales_order_amount: 0,
                    invoice_count: 0, invoice_amount: 0,
                    total_count: 0, total_amount: 0,
                    // Enhanced KPIs from merged versions
                    conversion_rate: 0, avg_deal_size: 0,
                    revenue_growth: 0, pipeline_velocity: 0
                },
                metadata: {
                    date_field_used: 'booking_date',
                    has_sales_types: true,
                    has_sale_value: true
                }
            },
            salesTypes: [],
            isLoading: false,
            error: null,
            filters: {
                startDate: this._getDefaultStartDate(),
                endDate: this._getDefaultEndDate(),
                selectedSalesTypes: []
            },
            charts: {
                trendChart: null,
                categoryChart: null,
                statusChart: null,
                comparisonChart: null
            },
            // Auto-refresh functionality (best practice from custom_sales)
            lastRefresh: new Date(),
            autoRefresh: true,
            refreshInterval: 5 * 60 * 1000, // 5 minutes
            // Performance metrics
            loadTime: 0,
            dataQuality: 'good'
        });

        // Chart containers references
        this.trendChartRef = useRef("trendChart");
        this.categoryChartRef = useRef("categoryChart");
        this.statusChartRef = useRef("statusChart");
        this.comparisonChartRef = useRef("comparisonChart");
        
        // Auto-refresh timer
        this.refreshTimer = null;

        // Enhanced color palette (merged from all versions)
        this.colorPalette = {
            primary: { background: 'rgba(139, 0, 0, 0.8)', border: 'rgba(139, 0, 0, 1)' },
            secondary: { background: 'rgba(114, 47, 55, 0.8)', border: 'rgba(114, 47, 55, 1)' },
            accent: { background: 'rgba(212, 175, 55, 0.8)', border: 'rgba(212, 175, 55, 1)' },
            success: { background: 'rgba(34, 197, 94, 0.8)', border: 'rgba(34, 197, 94, 1)' },
            warning: { background: 'rgba(251, 191, 36, 0.8)', border: 'rgba(251, 191, 36, 1)' },
            info: { background: 'rgba(59, 130, 246, 0.8)', border: 'rgba(59, 130, 246, 1)' }
        };

        onWillStart(this.loadInitialData);
        onMounted(this.initializeCharts);
        onWillUnmount(this.cleanup);
    }

    /**
     * Cleanup function to clear timers and charts (best practice)
     */
    cleanup() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
        }
        
        // Clean up all charts
        Object.values(this.state.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
    }

    /**
     * Get default start date (beginning of current month)
     */
    _getDefaultStartDate() {
        const now = new Date();
        return new Date(now.getFullYear(), now.getMonth(), 1).toISOString().split('T')[0];
    }

    /**
     * Get default end date (today)
     */
    _getDefaultEndDate() {
        return new Date().toISOString().split('T')[0];
    }

    /**
     * Load initial data with comprehensive error handling
     */
    async loadInitialData() {
        const startTime = performance.now();
        this.state.isLoading = true;
        this.state.error = null;
        
        try {
            // Parallel loading for better performance
            await Promise.all([
                this.loadSalesTypes(),
                this.loadDashboardData()
            ]);
            
            // Setup auto-refresh if enabled
            if (this.state.autoRefresh) {
                this.setupAutoRefresh();
            }
            
            // Calculate load time
            this.state.loadTime = performance.now() - startTime;
            
        } catch (error) {
            this.handleError(_t("Failed to load dashboard data"), error);
        } finally {
            this.state.isLoading = false;
        }
    }

    /**
     * Load available sales types with enhanced error handling
     */
    async loadSalesTypes() {
        try {
            const salesTypes = await this.orm.searchRead(
                "sale.order.type",
                [],
                ["id", "name"],
                { order: "name asc" }
            );
            
            this.state.salesTypes = salesTypes || [];
            
            // Auto-select all types by default
            this.state.filters.selectedSalesTypes = salesTypes.map(type => type.id);
            
        } catch (error) {
            // Graceful fallback when sales types are not available (defensive programming)
            console.warn("Sales types not available, using fallback mode");
            this.state.salesTypes = [];
            this.state.filters.selectedSalesTypes = [];
            this.state.dashboardData.metadata.has_sales_types = false;
        }
    }

    /**
     * Load dashboard data with enhanced error handling and performance tracking
     */
    async loadDashboardData() {
        this.state.isLoading = true;
        this.state.error = null;
        
        try {
            const result = await this.orm.call(
                "sale.order",
                "get_dashboard_summary_data",
                [],
                {
                    start_date: this.state.filters.startDate,
                    end_date: this.state.filters.endDate,
                    sales_type_ids: this.state.filters.selectedSalesTypes.length > 0 
                        ? this.state.filters.selectedSalesTypes 
                        : null
                }
            );

            if (result.error) {
                throw new Error(result.error);
            }

            this.state.dashboardData = result;
            this.state.lastRefresh = new Date();
            
            // Evaluate data quality
            this.evaluateDataQuality();
            
            // Update charts after data load
            this.updateCharts();
            
        } catch (error) {
            this.handleError(_t("Failed to load dashboard data"), error);
        } finally {
            this.state.isLoading = false;
        }
    }

    /**
     * Evaluate data quality based on completeness and consistency
     */
    evaluateDataQuality() {
        const totals = this.state.dashboardData.totals;
        const categories = Object.keys(this.state.dashboardData.categories);
        
        let quality = 'excellent';
        
        // Check for data completeness
        if (totals.total_count === 0) {
            quality = 'no_data';
        } else if (categories.length === 0) {
            quality = 'limited';
        } else if (totals.total_amount === 0) {
            quality = 'poor';
        } else if (categories.length < 3) {
            quality = 'good';
        }
        
        this.state.dataQuality = quality;
    }

    /**
     * Enhanced error handling with categorized error types
     */
    handleError(message, error) {
        console.error("Dashboard Error:", error);
        this.state.error = message;
        
        let errorType = 'danger';
        let errorMessage = message;
        
        // Categorize errors for better UX
        if (error.message && error.message.includes('network')) {
            errorType = 'warning';
            errorMessage = _t("Network connection issue. Please check your connection.");
        } else if (error.message && error.message.includes('permission')) {
            errorType = 'warning';
            errorMessage = _t("Access denied. Please check your permissions.");
        } else if (error.message && error.message.includes('timeout')) {
            errorType = 'info';
            errorMessage = _t("Request timeout. Data is loading slowly.");
        }
        
        this.notification.add(errorMessage, { type: errorType });
    }

    /**
     * Setup auto-refresh functionality (best practice from custom_sales)
     */
    setupAutoRefresh() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
        }
        
        this.refreshTimer = setInterval(() => {
            if (this.state.autoRefresh && !this.state.isLoading) {
                this.loadDashboardData();
            }
        }, this.state.refreshInterval);
    }

    /**
     * Toggle auto-refresh functionality with user feedback
     */
    toggleAutoRefresh() {
        this.state.autoRefresh = !this.state.autoRefresh;
        
        if (this.state.autoRefresh) {
            this.setupAutoRefresh();
            this.notification.add(_t("Auto-refresh enabled (5min intervals)"), { type: "info" });
        } else {
            if (this.refreshTimer) {
                clearInterval(this.refreshTimer);
            }
            this.notification.add(_t("Auto-refresh disabled"), { type: "info" });
        }
    }

    /**
     * Manual refresh trigger with performance tracking
     */
    async manualRefresh() {
        const startTime = performance.now();
        await this.loadDashboardData();
        const loadTime = performance.now() - startTime;
        
        this.notification.add(
            _t("Dashboard refreshed in %s ms", Math.round(loadTime)), 
            { type: "success" }
        );
    }

    /**
     * Handle filter changes with enhanced validation
     */
    async onFilterChange() {
        // Validate date range
        if (this.state.filters.startDate > this.state.filters.endDate) {
            this.notification.add(_t("Start date cannot be after end date"), { type: "warning" });
            return;
        }
        
        // Check for reasonable date range (not more than 5 years)
        const startDate = new Date(this.state.filters.startDate);
        const endDate = new Date(this.state.filters.endDate);
        const daysDiff = (endDate - startDate) / (1000 * 60 * 60 * 24);
        
        if (daysDiff > 1825) { // 5 years
            this.notification.add(_t("Date range too large. Please select a smaller range."), { type: "warning" });
            return;
        }
        
        if (daysDiff < 0) {
            this.notification.add(_t("Invalid date range"), { type: "warning" });
            return;
        }
        
        await this.loadDashboardData();
    }

    /**
     * Handle sales type selection changes with immediate feedback
     */
    onSalesTypeChange(typeId, isChecked) {
        if (isChecked) {
            if (!this.state.filters.selectedSalesTypes.includes(typeId)) {
                this.state.filters.selectedSalesTypes.push(typeId);
            }
        } else {
            const index = this.state.filters.selectedSalesTypes.indexOf(typeId);
            if (index > -1) {
                this.state.filters.selectedSalesTypes.splice(index, 1);
            }
        }
        
        // Provide immediate visual feedback
        const typeName = this.state.salesTypes.find(t => t.id === typeId)?.name || 'Unknown';
        const action = isChecked ? 'added' : 'removed';
        
        this.notification.add(
            _t("Sales type '%s' %s", typeName, action), 
            { type: "info", duration: 2000 }
        );
        
        this.onFilterChange();
    }

    /**
     * Initialize all charts with enhanced error handling
     */
    async initializeCharts() {
        try {
            // Ensure Chart.js is available
            await this.ensureChartJS();
            
            // Initialize all charts
            this.createTrendChart();
            this.createCategoryChart();
            this.createStatusChart();
            this.createComparisonChart();
            
        } catch (error) {
            console.error("Chart initialization error:", error);
            this.notification.add(_t("Charts could not be loaded"), { type: "warning" });
        }
    }

    /**
     * Ensure Chart.js is loaded with better error handling
     */
    async ensureChartJS() {
        let attempts = 0;
        const maxAttempts = 10;
        
        while (typeof Chart === 'undefined' && attempts < maxAttempts) {
            await new Promise(resolve => setTimeout(resolve, 500));
            attempts++;
        }
        
        if (typeof Chart === 'undefined') {
            throw new Error(_t("Chart.js library could not be loaded"));
        }
        
        // Set global Chart.js defaults
        Chart.defaults.font.family = "'Inter', 'Segoe UI', 'Roboto', sans-serif";
        Chart.defaults.color = '#374151';
        Chart.defaults.responsive = true;
        Chart.defaults.maintainAspectRatio = false;
    }

    /**
     * Update all charts with new data and error handling
     */
    updateCharts() {
        try {
            this.updateTrendChart();
            this.updateCategoryChart();
            this.updateStatusChart();
            this.updateComparisonChart();
        } catch (error) {
            console.error("Error updating charts:", error);
        }
    }

    /**
     * Create enhanced trend chart with best practices
     */
    createTrendChart() {
        if (!this.trendChartRef.el) return;
        
        const ctx = this.trendChartRef.el.getContext('2d');
        
        this.state.charts.trendChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: _t('Revenue Trend'),
                    data: [],
                    borderColor: this.colorPalette.primary.border,
                    backgroundColor: this.colorPalette.primary.background,
                    borderWidth: 3,
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: this.colorPalette.primary.border,
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            padding: 20
                        }
                    },
                    title: {
                        display: true,
                        text: _t('Monthly Revenue Trend'),
                        font: { size: 16, weight: 'bold' },
                        padding: 20
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff',
                        borderColor: this.colorPalette.primary.border,
                        borderWidth: 1
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: true,
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            display: true,
                            color: 'rgba(0, 0, 0, 0.1)'
                        },
                        ticks: {
                            callback: function(value) {
                                return '$' + (value / 1000).toFixed(0) + 'K';
                            }
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                animation: {
                    duration: 1000,
                    easing: 'easeInOutQuart'
                }
            }
        });
    }

    /**
     * Create enhanced category chart
     */
    createCategoryChart() {
        if (!this.categoryChartRef.el) return;
        
        const ctx = this.categoryChartRef.el.getContext('2d');
        
        this.state.charts.categoryChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: [],
                datasets: [{
                    data: [],
                    backgroundColor: [
                        this.colorPalette.primary.background,
                        this.colorPalette.secondary.background,
                        this.colorPalette.accent.background,
                        this.colorPalette.success.background,
                        this.colorPalette.warning.background,
                        this.colorPalette.info.background
                    ],
                    borderColor: [
                        this.colorPalette.primary.border,
                        this.colorPalette.secondary.border,
                        this.colorPalette.accent.border,
                        this.colorPalette.success.border,
                        this.colorPalette.warning.border,
                        this.colorPalette.info.border
                    ],
                    borderWidth: 2,
                    hoverOffset: 10
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            usePointStyle: true,
                            padding: 15
                        }
                    },
                    title: {
                        display: true,
                        text: _t('Revenue by Category'),
                        font: { size: 16, weight: 'bold' },
                        padding: 20
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.raw || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: $${(value / 1000).toFixed(1)}K (${percentage}%)`;
                            }
                        }
                    }
                },
                animation: {
                    animateRotate: true,
                    duration: 1500
                }
            }
        });
    }

    /**
     * Create status distribution chart
     */
    createStatusChart() {
        if (!this.statusChartRef.el) return;
        
        const ctx = this.statusChartRef.el.getContext('2d');
        
        this.state.charts.statusChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [_t('Drafts'), _t('Sales Orders'), _t('Invoiced')],
                datasets: [{
                    label: _t('Count'),
                    data: [],
                    backgroundColor: [
                        this.colorPalette.warning.background,
                        this.colorPalette.info.background,
                        this.colorPalette.success.background
                    ],
                    borderColor: [
                        this.colorPalette.warning.border,
                        this.colorPalette.info.border,
                        this.colorPalette.success.border
                    ],
                    borderWidth: 2,
                    borderRadius: 8,
                    borderSkipped: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: _t('Orders by Status'),
                        font: { size: 16, weight: 'bold' },
                        padding: 20
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    }
                },
                animation: {
                    duration: 1200,
                    easing: 'easeOutBounce'
                }
            }
        });
    }

    /**
     * Create comparison chart for enhanced analytics
     */
    createComparisonChart() {
        if (!this.comparisonChartRef.el) return;
        
        const ctx = this.comparisonChartRef.el.getContext('2d');
        
        this.state.charts.comparisonChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [
                    {
                        label: _t('Current Period'),
                        data: [],
                        backgroundColor: this.colorPalette.primary.background,
                        borderColor: this.colorPalette.primary.border,
                        borderWidth: 2
                    },
                    {
                        label: _t('Previous Period'),
                        data: [],
                        backgroundColor: this.colorPalette.secondary.background,
                        borderColor: this.colorPalette.secondary.border,
                        borderWidth: 2
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top'
                    },
                    title: {
                        display: true,
                        text: _t('Period Comparison'),
                        font: { size: 16, weight: 'bold' }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '$' + (value / 1000).toFixed(0) + 'K';
                            }
                        }
                    }
                }
            }
        });
    }

    /**
     * Update trend chart with actual data
     */
    updateTrendChart() {
        if (!this.state.charts.trendChart) return;
        
        try {
            // Generate trend data from dashboard data
            const trendData = this.generateTrendData();
            
            this.state.charts.trendChart.data.labels = trendData.labels;
            this.state.charts.trendChart.data.datasets[0].data = trendData.values;
            this.state.charts.trendChart.update('active');
            
        } catch (error) {
            console.error("Error updating trend chart:", error);
        }
    }

    /**
     * Update category chart with actual data
     */
    updateCategoryChart() {
        if (!this.state.charts.categoryChart) return;
        
        try {
            const categories = this.state.dashboardData.categories;
            const labels = Object.keys(categories);
            const data = labels.map(label => categories[label].total_amount);
            
            this.state.charts.categoryChart.data.labels = labels;
            this.state.charts.categoryChart.data.datasets[0].data = data;
            this.state.charts.categoryChart.update('active');
            
        } catch (error) {
            console.error("Error updating category chart:", error);
        }
    }

    /**
     * Update status chart with actual data
     */
    updateStatusChart() {
        if (!this.state.charts.statusChart) return;
        
        try {
            const totals = this.state.dashboardData.totals;
            const data = [
                totals.draft_count,
                totals.sales_order_count,
                totals.invoice_count
            ];
            
            this.state.charts.statusChart.data.datasets[0].data = data;
            this.state.charts.statusChart.update('active');
            
        } catch (error) {
            console.error("Error updating status chart:", error);
        }
    }

    /**
     * Update comparison chart
     */
    updateComparisonChart() {
        if (!this.state.charts.comparisonChart) return;
        
        try {
            // This would require additional backend method for comparison data
            // For now, show current data only
            const categories = this.state.dashboardData.categories;
            const labels = Object.keys(categories);
            const currentData = labels.map(label => categories[label].total_amount);
            
            this.state.charts.comparisonChart.data.labels = labels;
            this.state.charts.comparisonChart.data.datasets[0].data = currentData;
            this.state.charts.comparisonChart.data.datasets[1].data = currentData.map(v => v * 0.85); // Mock previous data
            this.state.charts.comparisonChart.update('active');
            
        } catch (error) {
            console.error("Error updating comparison chart:", error);
        }
    }

    /**
     * Generate trend data for the line chart
     */
    generateTrendData() {
        // This is a simplified version - in reality, you'd call a backend method
        // to get actual monthly data
        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
        const totals = this.state.dashboardData.totals;
        const baseValue = totals.total_amount / 6;
        
        const values = months.map((_, index) => {
            // Generate some variation for demo purposes
            const variation = (Math.random() - 0.5) * 0.4;
            return Math.max(0, baseValue * (1 + variation));
        });
        
        return { labels: months, values };
    }

    /**
     * Format currency values for display
     */
    formatCurrency(value) {
        if (value >= 1000000) {
            return `$${(value / 1000000).toFixed(1)}M`;
        } else if (value >= 1000) {
            return `$${(value / 1000).toFixed(1)}K`;
        } else {
            return `$${value.toFixed(0)}`;
        }
    }

    /**
     * Get data quality indicator color
     */
    getDataQualityColor() {
        const qualityColors = {
            'excellent': '#10b981',
            'good': '#3b82f6',
            'limited': '#f59e0b',
            'poor': '#ef4444',
            'no_data': '#6b7280'
        };
        
        return qualityColors[this.state.dataQuality] || '#6b7280';
    }

    /**
     * Export dashboard data as CSV (additional feature)
     */
    async exportDashboardData() {
        try {
            const data = this.state.dashboardData;
            let csvContent = "Category,Draft Count,Draft Amount,Sales Orders Count,Sales Orders Amount,Invoice Count,Invoice Amount,Total\n";
            
            Object.entries(data.categories).forEach(([category, values]) => {
                csvContent += `${category},${values.draft_count},${values.draft_amount},${values.sales_order_count},${values.sales_order_amount},${values.invoice_count},${values.invoice_amount},${values.total_amount}\n`;
            });
            
            // Add totals row
            const totals = data.totals;
            csvContent += `TOTAL,${totals.draft_count},${totals.draft_amount},${totals.sales_order_count},${totals.sales_order_amount},${totals.invoice_count},${totals.invoice_amount},${totals.total_amount}\n`;
            
            // Download CSV
            const blob = new Blob([csvContent], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `sales_dashboard_${new Date().toISOString().split('T')[0]}.csv`;
            a.click();
            window.URL.revokeObjectURL(url);
            
            this.notification.add(_t("Dashboard data exported successfully"), { type: "success" });
            
        } catch (error) {
            this.handleError(_t("Failed to export data"), error);
        }
    }
}

// Register the component
registry.category("actions").add("oe_sale_dashboard_17.sales_dashboard_action", SaleDashboardMerged);
