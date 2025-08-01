/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onMounted, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

const actionRegistry = registry.category("actions");

class OeSaleDashboard extends Component {
    static template = "oe_sale_dashboard_17.yearly_sales_dashboard_template";
    
    setup() {
        super.setup();
        
        // Initialize state with enhanced filtering
        const today = new Date().toISOString().split('T')[0];
        const thirtyDaysAgo = new Date();
        thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
        const startDate = thirtyDaysAgo.toISOString().split('T')[0];
        
        this.state = useState({
            startDate: startDate,
            endDate: today,
            selectedSalesTypes: [],
            salesTypes: [],
            // Enhanced dashboard data
            summaryData: {},
            trendsData: {},
            rankingData: [],
            distributionData: {},
            isLoading: false,
            // KPI values
            totalPipelineValue: 0,
            realizedRevenue: 0,
            averageDealSize: 0,
            overallConversionRate: 0,
        });

        // Chart instances for cleanup
        this.charts = {
            trendsLine: null,
            comparisonBar: null,
            enhancedPie: null
        };

        // Services
        this.orm = useService("orm");
        this.notification = useService("notification");

        // Color palette for charts
        this.colorPalette = {
            primary: { background: 'rgba(128, 0, 32, 0.8)', border: 'rgba(128, 0, 32, 1)' },
            secondary: { background: 'rgba(114, 47, 55, 0.8)', border: 'rgba(114, 47, 55, 1)' },
            accent: { background: 'rgba(212, 175, 55, 0.8)', border: 'rgba(212, 175, 55, 1)' },
            success: { background: 'rgba(212, 175, 55, 0.6)', border: 'rgba(212, 175, 55, 0.8)' },
            info: { background: 'rgba(244, 228, 188, 0.8)', border: 'rgba(244, 228, 188, 1)' }
        };

        this.chartColors = {
            backgrounds: [
                this.colorPalette.primary.background,
                this.colorPalette.secondary.background,
                this.colorPalette.accent.background,
                this.colorPalette.success.background,
                this.colorPalette.info.background,
                'rgba(156, 163, 175, 0.8)'
            ],
            borders: [
                this.colorPalette.primary.border,
                this.colorPalette.secondary.border,
                this.colorPalette.accent.border,
                this.colorPalette.success.border,
                this.colorPalette.info.border,
                'rgba(156, 163, 175, 1)'
            ]
        };

        // Currency formatter
        this.currencyFormatter = new Intl.NumberFormat('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
            useGrouping: true
        });

        // Initialize dashboard on mount
        onMounted(async () => {
            console.log("Enhanced Sales Dashboard Loading...");
            try {
                await this._initializeEnhancedDashboard();
                this._addScrollToTopButton();
            } catch (error) {
                console.error('Dashboard initialization error:', error);
                this.notification.add(_t("Dashboard loading failed"), { type: 'danger' });
            }
        });
    }

    /**
     * Format large numbers for dashboard display
     */
    formatDashboardValue(value) {
        if (!value || value === 0) return "0";
        
        const absValue = Math.abs(value);
        if (absValue >= 1_000_000_000) {
            return `${(value / 1_000_000_000).toFixed(1)} B`;
        } else if (absValue >= 1_000_000) {
            return `${(value / 1_000_000).toFixed(1)} M`;
        } else if (absValue >= 1_000) {
            return `${(value / 1_000).toFixed(0)} K`;
        } else {
            return `${Math.round(value)}`;
        }
    }

    /**
     * Handle date change events
     */
    onStartDateChange(ev) {
        this.state.startDate = ev.target.value;
        this._loadEnhancedDashboardData();
    }

    onEndDateChange(ev) {
        this.state.endDate = ev.target.value;
        this._loadEnhancedDashboardData();
    }

    /**
     * Handle sales type filter change
     */
    onSalesTypeFilterChange(ev) {
        const selectedOptions = Array.from(ev.target.selectedOptions).map(option => parseInt(option.value));
        this.state.selectedSalesTypes = selectedOptions;
        this._loadEnhancedDashboardData();
    }

    /**
     * Initialize enhanced dashboard
     */
    async _initializeEnhancedDashboard() {
        await this._loadSalesTypes();
        await this._loadEnhancedDashboardData();
    }

    /**
     * Load available sales types
     */
    async _loadSalesTypes() {
        try {
            const salesTypes = await this.orm.searchRead("sale.order.type", [], ['id', 'name']);
            this.state.salesTypes = salesTypes;
            this.state.selectedSalesTypes = salesTypes.map(st => st.id);
        } catch (error) {
            console.error("Error loading sales types:", error);
            this.state.salesTypes = [];
            this.state.selectedSalesTypes = [];
        }
    }

    /**
     * Load enhanced dashboard data
     */
    async _loadEnhancedDashboardData() {
        this.state.isLoading = true;
        try {
            // Validate date range
            if (this.state.startDate > this.state.endDate) {
                this.notification.add(_t("Start date cannot be later than end date"), { type: 'warning' });
                this.state.isLoading = false;
                return;
            }

            const salesTypeIds = this.state.selectedSalesTypes.length > 0 ? this.state.selectedSalesTypes : null;

            // Load all data in parallel
            const [summaryData, trendsData, rankingData, distributionData] = await Promise.all([
                this.orm.call("sale.order", "get_dashboard_summary_data", [
                    this.state.startDate, 
                    this.state.endDate, 
                    salesTypeIds
                ]),
                this.orm.call("sale.order", "get_monthly_fluctuation_data", [
                    this.state.startDate, 
                    this.state.endDate, 
                    salesTypeIds
                ]),
                this.orm.call("sale.order", "get_sales_type_ranking_data", [
                    this.state.startDate, 
                    this.state.endDate, 
                    salesTypeIds
                ]),
                this.orm.call("sale.order", "get_sales_type_distribution", [
                    this.state.startDate, 
                    this.state.endDate
                ])
            ]);

            // Update state
            this.state.summaryData = summaryData;
            this.state.trendsData = trendsData;
            this.state.rankingData = rankingData;
            this.state.distributionData = distributionData;

            // Update KPIs
            this._updateKPIs(summaryData);

            // Wait for DOM and create charts
            await this._waitForDOM();
            this._createEnhancedCharts();

            this.notification.add(_t(`Dashboard updated: ${this.state.startDate} to ${this.state.endDate}`), { type: 'success' });

        } catch (error) {
            console.error("Error loading enhanced dashboard data:", error);
            this.notification.add(_t("Error loading dashboard data"), { type: 'danger' });
        } finally {
            this.state.isLoading = false;
        }
    }

    /**
     * Update KPI values
     */
    _updateKPIs(summaryData) {
        if (summaryData && summaryData.totals) {
            const totals = summaryData.totals;
            this.state.totalPipelineValue = totals.draft_amount + totals.sales_order_amount;
            this.state.realizedRevenue = totals.invoice_amount;
            this.state.averageDealSize = totals.total_count > 0 ? totals.total_amount / totals.total_count : 0;
            this.state.overallConversionRate = totals.total_count > 0 ? 
                ((totals.invoice_count / totals.total_count) * 100).toFixed(1) : 0;
        }
    }

    /**
     * Wait for DOM elements to be ready
     */
    async _waitForDOM() {
        return new Promise(resolve => {
            const checkDOM = () => {
                if (document.getElementById('trendsLineChart') && 
                    document.getElementById('comparisonBarChart') && 
                    document.getElementById('enhancedPieChart')) {
                    resolve();
                } else {
                    setTimeout(checkDOM, 100);
                }
            };
            checkDOM();
        });
    }

    /**
     * Create enhanced charts
     */
    _createEnhancedCharts() {
        // Wait for Chart.js to be available
        if (typeof Chart === 'undefined') {
            console.warn('Chart.js not loaded, waiting...');
            setTimeout(() => this._createEnhancedCharts(), 500);
            return;
        }

        try {
            this._createTrendsLineChart();
            this._createComparisonBarChart();
            this._createEnhancedPieChart();
        } catch (error) {
            console.error("Error creating charts:", error);
        }
    }

    /**
     * Create trends line chart
     */
    _createTrendsLineChart() {
        const ctx = document.getElementById('trendsLineChart');
        if (!ctx || !this.state.trendsData) return;

        if (this.charts.trendsLine) {
            this.charts.trendsLine.destroy();
        }

        const trendsData = this.state.trendsData;
        
        this.charts.trendsLine = new Chart(ctx, {
            type: 'line',
            data: {
                labels: trendsData.labels || [],
                datasets: [
                    {
                        label: 'Quotations',
                        data: trendsData.quotations || [],
                        borderColor: this.colorPalette.primary.border,
                        backgroundColor: this.colorPalette.primary.background,
                        tension: 0.4,
                        fill: false
                    },
                    {
                        label: 'Sales Orders',
                        data: trendsData.sales_orders || [],
                        borderColor: this.colorPalette.secondary.border,
                        backgroundColor: this.colorPalette.secondary.background,
                        tension: 0.4,
                        fill: false
                    },
                    {
                        label: 'Invoiced Sales',
                        data: trendsData.invoiced_sales || [],
                        borderColor: this.colorPalette.success.border,
                        backgroundColor: this.colorPalette.success.background,
                        tension: 0.4,
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Sales Trends Over Time'
                    },
                    legend: {
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: (value) => this.formatDashboardValue(value)
                        }
                    }
                }
            }
        });
    }

    /**
     * Create comparison bar chart
     */
    _createComparisonBarChart() {
        const ctx = document.getElementById('comparisonBarChart');
        if (!ctx || !this.state.rankingData) return;

        if (this.charts.comparisonBar) {
            this.charts.comparisonBar.destroy();
        }

        const rankingData = this.state.rankingData;
        const labels = rankingData.map(item => item.sales_type_name || 'Unknown');
        const salesValues = rankingData.map(item => item.total_sales_value || 0);
        const invoicedValues = rankingData.map(item => item.invoiced_amount || 0);

        this.charts.comparisonBar = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Total Sales Value',
                        data: salesValues,
                        backgroundColor: this.colorPalette.primary.background,
                        borderColor: this.colorPalette.primary.border,
                        borderWidth: 1
                    },
                    {
                        label: 'Invoiced Amount',
                        data: invoicedValues,
                        backgroundColor: this.colorPalette.success.background,
                        borderColor: this.colorPalette.success.border,
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Sales Type Comparison'
                    },
                    legend: {
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: (value) => this.formatDashboardValue(value)
                        }
                    }
                }
            }
        });
    }

    /**
     * Create enhanced pie chart
     */
    _createEnhancedPieChart() {
        const ctx = document.getElementById('enhancedPieChart');
        if (!ctx || !this.state.distributionData) return;

        if (this.charts.enhancedPie) {
            this.charts.enhancedPie.destroy();
        }

        const distributionData = this.state.distributionData;
        const amountDistribution = distributionData.amount_distribution || {};
        const labels = Object.keys(amountDistribution);
        const data = Object.values(amountDistribution);

        if (labels.length === 0) return;

        this.charts.enhancedPie = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: this.chartColors.backgrounds.slice(0, labels.length),
                    borderColor: this.chartColors.borders.slice(0, labels.length),
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Sales Distribution by Type'
                    },
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const value = context.parsed;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${context.label}: ${this.formatDashboardValue(value)} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    /**
     * Add scroll to top button
     */
    _addScrollToTopButton() {
        try {
            const scrollBtn = document.getElementById('scroll-to-top-btn');
            if (!scrollBtn) return;

            const container = document.querySelector('.o_oe_sale_dashboard_17_container');
            if (!container) return;

            container.addEventListener('scroll', () => {
                if (container.scrollTop > 300) {
                    scrollBtn.style.display = 'block';
                } else {
                    scrollBtn.style.display = 'none';
                }
            });

            scrollBtn.addEventListener('click', () => {
                container.scrollTo({ top: 0, behavior: 'smooth' });
            });
        } catch (error) {
            console.warn('Scroll to top functionality not available:', error);
        }
    }

    /**
     * Cleanup method
     */
    willUnmount() {
        // Destroy charts
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.destroy();
        });
    }
}

// Register the component
OeSaleDashboard.template = "oe_sale_dashboard_17.yearly_sales_dashboard_template";
actionRegistry.add("oe_sale_dashboard_17_tag", OeSaleDashboard);
