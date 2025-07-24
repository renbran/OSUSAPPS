/** @odoo-module **/

import { Component, useState, onMounted, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

class CustomSalesDashboard extends Component {
    static template = "custom_sales.DashboardTemplate";
    
    setup() {
        this.orm = useService("orm");
        this.rpc = useService("rpc");
        this.notification = useService("notification");
        
        this.state = useState({
            kpis: [],
            charts: [],
            loading: true,
            error: null,
            filters: {
                date_from: null,
                date_to: null,
                dashboard_id: null
            }
        });
        
        this.refreshInterval = null;
        
        onMounted(() => {
            this.loadDashboardData();
            this.setupAutoRefresh();
        });
        
        onWillUnmount(() => {
            if (this.refreshInterval) {
                clearInterval(this.refreshInterval);
            }
        });
    }
    
    async loadDashboardData() {
        try {
            this.state.loading = true;
            this.state.error = null;
            
            const result = await this.rpc("/custom_sales/api/dashboard_data", {
                dashboard_id: this.state.filters.dashboard_id,
                date_from: this.state.filters.date_from,
                date_to: this.state.filters.date_to
            } catch (error) { console.error('Caught error:', error); });
            
            if (result.error) {
                throw new Error(result.error);
            }
            
            this.state.kpis = result.data.kpis || [];
            this.state.charts = result.data.charts || [];
            
            this.$nextTick(() => {
                this.renderCharts();
            });
            
        } catch (error) {
            console.error("Dashboard loading error:", error);
            this.state.error = error.message;
            this.notification.add(error.message, { type: "danger" });
        } finally {
            this.state.loading = false;
        }
    }
    
    async refreshData() {
        await this.loadDashboardData();
    }
    
    setupAutoRefresh() {
        // Refresh every 5 minutes
        this.refreshInterval = setInterval(() => {
            this.loadDashboardData();
        }, 300000);
    }
    
    renderCharts() {
        this.state.charts.forEach(chart => {
            const canvas = document.getElementById(`chart_${chart.id}`);
            if (canvas && window.Chart) {
                new window.Chart(canvas, {
                    type: chart.type,
                    data: chart.data,
                    options: chart.options || {}
                });
            }
        });
    }
    
    onDateFilterChange() {
        this.loadDashboardData();
    }
    
    async exportReport(format) {
        try {
            const url = `/custom_sales/report/export?format=${format} catch (error) { console.error('Caught error:', error); }&date_from=${this.state.filters.date_from || ''}&date_to=${this.state.filters.date_to || ''}`;
            window.open(url, '_blank');
            
            this.notification.add(`Report exported as ${format.toUpperCase()}`, { type: "success" });
        } catch (error) {
            this.notification.add(`Export failed: ${error.message}`, { type: "danger" });
        }
    }
    
    formatKpiValue(kpi) {
        const value = kpi.value || 0;
        
        switch (kpi.format_type) {
            case 'currency':
                return new Intl.NumberFormat('en-US', {
                    style: 'currency',
                    currency: 'USD'
                }).format(value);
            case 'percentage':
                return `${value.toFixed(2)}%`;
            case 'integer':
                return Math.round(value).toLocaleString();
            default:
                return value.toLocaleString();
        }
    }
}

CustomSalesDashboard.props = {};

registry.category("actions").add("custom_sales_dashboard", CustomSalesDashboard);
