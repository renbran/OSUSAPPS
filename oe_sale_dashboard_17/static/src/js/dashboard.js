/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class PremiumSalesDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        
        this.state = useState({
            dashboards: [],
            selectedDashboard: null,
            isLoading: false,
            chartData: null,
            filters: {
                dateFrom: new Date(new Date().getFullYear(), new Date().getMonth(), 1),
                dateTo: new Date(),
                salesTeamId: null,
                agent1PartnerId: null,
            }
        });

        onWillStart(async () => {
            await this.loadDashboards();
        });
    }

    async loadDashboards() {
        this.state.isLoading = true;
        try {
            const dashboards = await this.orm.searchRead(
                "sales.dashboard",
                [["active", "=", true]],
                [
                    "name", 
                    "total_revenue", 
                    "total_orders", 
                    "avg_order_value",
                    "total_agent1_commission",
                    "total_agent2_commission", 
                    "total_consultant_commission",
                    "avg_commission_rate",
                    "revenue_growth", 
                    "orders_growth",
                    "sales_team_id",
                    "agent1_partner_id",
                    "consultant_id",
                    "date_from",
                    "date_to",
                    "last_updated"
                ]
            );
            this.state.dashboards = dashboards;
            
            if (dashboards.length > 0) {
                this.state.selectedDashboard = dashboards[0];
                await this.loadDashboardData();
            }
        } catch (error) {
            this.notification.add("Error loading dashboards: " + error.message, {
                type: "danger",
                title: "Dashboard Error"
            });
        } finally {
            this.state.isLoading = false;
        }
    }

    async loadDashboardData() {
        if (!this.state.selectedDashboard) return;

        this.state.isLoading = true;
        try {
            // Load sales data using correct field names
            const salesData = await this.orm.call(
                "sale.order",
                "read_group",
                [],
                {
                    domain: [
                        ["date_order", ">=", this.state.filters.dateFrom],
                        ["date_order", "<=", this.state.filters.dateTo],
                        ["state", "in", ["sale", "done"]]
                    ],
                    fields: ["sale_value:sum", "amount_total:sum", "agent1_amount:sum", "agent1_partner_id"],
                    groupby: ["agent1_partner_id"]
                }
            );

            // Process chart data
            this.state.chartData = {
                salesTrend: this.processSalesTrendData(salesData),
                agentPerformance: this.processAgentPerformanceData(agentData)
            };

            // Refresh dashboard KPIs
            await this.refreshDashboardKPIs();

        } catch (error) {
            this.notification.add("Error loading dashboard data: " + error.message, {
                type: "danger",
                title: "Data Loading Error"
            });
        } finally {
            this.state.isLoading = false;
        }
    }

    processSalesTrendData(salesData) {
        return salesData.map(item => ({
            month: item.date_order,
            revenue: item.sale_value || item.amount_total || 0,
            commission: (item.agent1_amount || 0) + (item.agent2_amount || 0)
        }));
    }

    processAgentPerformanceData(agentData) {
        return agentData.map(item => ({
            agent: item.agent1_partner_id[1], // Partner name
            agentId: item.agent1_partner_id[0], // Partner ID
            totalSales: item.sale_value || item.amount_total || 0,
            commission: item.agent1_amount || 0,
            ordersCount: item.agent1_partner_id_count || 0
        })).sort((a, b) => b.totalSales - a.totalSales);
    }

    async refreshDashboardKPIs() {
        if (!this.state.selectedDashboard) return;
        
        try {
            // Trigger recomputation of KPIs
            await this.orm.call(
                "sales.dashboard", 
                "refresh_dashboard", 
                [this.state.selectedDashboard.id]
            );
            
            // Reload the dashboard data
            const updatedDashboard = await this.orm.read(
                "sales.dashboard",
                [this.state.selectedDashboard.id],
                [
                    "total_revenue", 
                    "total_orders", 
                    "avg_order_value",
                    "total_agent1_commission",
                    "total_agent2_commission",
                    "total_consultant_commission",
                    "avg_commission_rate",
                    "revenue_growth", 
                    "orders_growth",
                    "last_updated"
                ]
            );
            
            this.state.selectedDashboard = { ...this.state.selectedDashboard, ...updatedDashboard[0] };
            
            this.notification.add("Dashboard refreshed successfully", {
                type: "success",
                title: "Dashboard Updated"
            });
            
        } catch (error) {
            this.notification.add("Error refreshing dashboard: " + error.message, {
                type: "danger",
                title: "Refresh Error"
            });
        }
    }

    async applyFilters() {
        await this.loadDashboardData();
    }

    async selectDashboard(dashboardId) {
        const dashboard = this.state.dashboards.find(d => d.id === dashboardId);
        if (dashboard) {
            this.state.selectedDashboard = dashboard;
            await this.loadDashboardData();
        }
    }

    async exportDashboard() {
        if (!this.state.selectedDashboard) return;
        
        try {
            await this.orm.call(
                "sales.dashboard",
                "export_dashboard",
                [this.state.selectedDashboard.id]
            );
            
            this.notification.add("Dashboard export initiated", {
                type: "info",
                title: "Export Started"
            });
        } catch (error) {
            this.notification.add("Error exporting dashboard: " + error.message, {
                type: "danger",
                title: "Export Error"
            });
        }
    }

    async generateTestData() {
        try {
            await this.orm.call("sales.dashboard", "generate_test_data", []);
            await this.loadDashboards();
            
            this.notification.add("Test data generated successfully", {
                type: "success",
                title: "Test Data Created"
            });
        } catch (error) {
            this.notification.add("Error generating test data: " + error.message, {
                type: "danger",
                title: "Test Data Error"
            });
        }
    }

    formatCurrency(amount) {
        if (!amount) return "0.00";
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 2
        }).format(amount);
    }

    formatPercentage(value) {
        if (typeof value !== 'number') return "0.0%";
        return `${value.toFixed(1)}%`;
    }

    formatNumber(value) {
        if (!value) return "0";
        return new Intl.NumberFormat('en-US').format(value);
    }

    getPerformanceClass(growth) {
        if (growth > 0) return "kpi-change positive";
        if (growth < 0) return "kpi-change negative";
        return "kpi-change neutral";
    }

    getGrowthIcon(growth) {
        if (growth > 0) return "↗";
        if (growth < 0) return "↘";
        return "→";
    }

    // Chart rendering methods
    renderSalesTrendChart() {
        if (!this.state.chartData?.salesTrend) return;
        
        // This would integrate with Chart.js or similar charting library
        // Implementation depends on your charting preference
        console.log("Rendering sales trend chart with data:", this.state.chartData.salesTrend);
    }

    renderAgentPerformanceChart() {
        if (!this.state.chartData?.agentPerformance) return;
        
        // This would render agent performance charts
        console.log("Rendering agent performance chart with data:", this.state.chartData.agentPerformance);
    }
}

PremiumSalesDashboard.template = "premium_sales_dashboard_17.PremiumSalesDashboard";

// Widget for embedding in form views
export class SalesDashboardWidget extends Component {
    setup() {
        this.orm = useService("orm");
        this.state = useState({
            kpis: {},
            isLoading: false
        });

        onWillStart(async () => {
            await this.loadKPIs();
        });
    }

    async loadKPIs() {
        this.state.isLoading = true;
        try {
            // Load current period KPIs using correct field names
            const currentDate = new Date();
            const firstDayOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
            
            const orderData = await this.orm.call(
                "sale.order",
                "read_group",
                [],
                {
                    domain: [
                        ["date_order", ">=", firstDayOfMonth.toISOString().split('T')[0]],
                        ["date_order", "<=", currentDate.toISOString().split('T')[0]],
                        ["state", "in", ["sale", "done"]]
                    ],
                    fields: [
                        "sale_value:sum", 
                        "amount_total:sum", 
                        "agent1_amount:sum",
                        "agent2_amount:sum",
                        "salesperson_commission:sum"
                    ],
                    groupby: []
                }
            );

            if (orderData.length > 0) {
                const data = orderData[0];
                this.state.kpis = {
                    totalRevenue: data.sale_value || data.amount_total || 0,
                    totalOrders: data.__count || 0,
                    avgOrderValue: data.__count > 0 ? (data.sale_value || data.amount_total || 0) / data.__count : 0,
                    totalCommission: (data.agent1_amount || 0) + (data.agent2_amount || 0) + (data.salesperson_commission || 0)
                };
            }
        } catch (error) {
            console.error("Error loading KPIs:", error);
        } finally {
            this.state.isLoading = false;
        }
    }
}

SalesDashboardWidget.template = "premium_sales_dashboard_17.SalesDashboardWidget";

// Register components
registry.category("actions").add("premium_sales_dashboard", PremiumSalesDashboard);
registry.category("fields").add("sales_dashboard_widget", SalesDashboardWidget);

// Auto-refresh functionality
let refreshInterval;

export function startAutoRefresh(dashboard, intervalMinutes = 30) {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
    
    refreshInterval = setInterval(async () => {
        if (dashboard && dashboard.state.selectedDashboard) {
            try {
                await dashboard.refreshDashboardKPIs();
                console.log(`Dashboard auto-refreshed at ${new Date().toLocaleTimeString()}`);
            } catch (error) {
                console.error("Auto-refresh error:", error);
            }
        }
    }, intervalMinutes * 60 * 1000);
}

export function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
        refreshInterval = null;
    }
}    fields: ["sale_value:sum", "amount_total:sum", "agent1_amount:sum", "agent2_amount:sum"],
                    groupby: ["date_order:month"]
                }
            );

            // Load agent performance data
            const agentData = await this.orm.call(
                "sale.order",
                "read_group",
                [],
                {
                    domain: [
                        ["date_order", ">=", this.state.filters.dateFrom],
                        ["date_order", "<=", this.state.filters.dateTo],
                        ["state", "in", ["sale", "done"]],
                        ["agent1_partner_id", "!=", false]
                    ],