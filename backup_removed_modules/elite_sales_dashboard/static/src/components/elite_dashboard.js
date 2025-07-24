odoo.define('elite_sales_dashboard.EliteDashboardComponent', function (require) {
    "use strict";

    const { Component, hooks } = owl;
    const { useState, useRef, onMounted, onWillUnmount } = hooks;
    const { xml } = owl.tags;
    const rpc = require('web.rpc');
    
    class EliteDashboardComponent extends Component {
        constructor() {
            super(...arguments);
            this.state = useState({
                currentView: 'internal',
                dashboardData: null,
                settings: null,
                isLoading: true,
                lastUpdated: new Date(),
            });
            this.chartRef = useRef('annualTrendChart');
            this.refreshTimer = null;
        }
        
        async willStart() {
            await this.loadData();
        }
        
        async mounted() {
            this.renderChart();
            this.startAutoRefresh();
        }
        
        willUnmount() {
            if (this.refreshTimer) {
                clearInterval(this.refreshTimer);
            }
        }
        
        async loadData() {
            this.state.isLoading = true;
            
            try {
                // Load settings
                const settings = await rpc.query({
                    route: '/elite_dashboard/settings',
                    params: {},
                });
                this.state.settings = settings;
                
                // Load dashboard data
                const data = await rpc.query({
                    route: '/elite_dashboard/data',
                    params: {
                        agent_type: this.state.currentView,
                    },
                });
                this.state.dashboardData = data;
                this.state.lastUpdated = new Date();
            } catch (error) {
                console.error('Failed to load dashboard data:', error);
            } finally {
                this.state.isLoading = false;
            }
        }
        
        startAutoRefresh() {
            const interval = this.state.settings?.refresh_interval || 5;
            this.refreshTimer = setInterval(async () => {
                await this.loadData();
                this.renderChart();
            }, interval * 1000);
        }
        
        renderChart() {
            if (!this.chartRef.el || !this.state.dashboardData) return;
            
            const ctx = this.chartRef.el.getContext('2d');
            const trend = this.state.dashboardData.annual_trend;
            
            if (!trend) return;
            
            const labels = Object.keys(trend);
            const data = Object.values(trend);
            
            if (this.chart) {
                this.chart.destroy();
            }
            
            this.chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Monthly Sales',
                        data: data,
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 2,
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return '$' + (value / 1000000).toFixed(1) + 'M';
                                }
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const value = context.parsed.y;
                                    return '$' + value.toLocaleString();
                                }
                            }
                        }
                    }
                }
            });
        }
        
        async toggleView(view) {
            if (view !== this.state.currentView) {
                this.state.currentView = view;
                await this.loadData();
                this.renderChart();
            }
        }
        
        formatCurrency(amount) {
            if (amount >= 1000000) {
                return '$' + (amount / 1000000).toFixed(1) + 'M';
            } else if (amount >= 1000) {
                return '$' + (amount / 1000).toFixed(1) + 'K';
            } else {
                return '$' + amount.toFixed(0);
            }
        }
        
        formatTime(date) {
            return date.toLocaleTimeString();
        }
    }
    
    EliteDashboardComponent.template = xml`
        <div class="elite_dashboard_container">
            <div class="elite_dashboard_header">
                <h1>Elite Sales Dashboard</h1>
                <div class="elite_dashboard_controls">
                    <button class="btn btn-primary" t-att-class="{'btn-primary': state.currentView === 'internal', 'btn-secondary': state.currentView !== 'internal'}" t-on-click="toggleView('internal')">Internal Agents</button>
                    <button class="btn btn-secondary" t-att-class="{'btn-primary': state.currentView === 'external', 'btn-secondary': state.currentView !== 'external'}" t-on-click="toggleView('external')">External Partners</button>
                    <button class="btn btn-secondary" t-on-click="loadData">Refresh</button>
                </div>
            </div>
            
            <div t-if="state.isLoading" class="alert alert-info">
                Loading dashboard data...
            </div>
            
            <div t-if="!state.isLoading and state.dashboardData" class="elite_dashboard_content">
                <!-- Summary Cards -->
                <div class="elite_dashboard_summary">
                    <!-- Total Earnings -->
                    <div class="elite_dashboard_card">
                        <div class="elite_dashboard_card_title">Total Earnings</div>
                        <div class="elite_dashboard_card_value">
                            <t t-esc="formatCurrency(state.dashboardData.total_earnings)"/>
                        </div>
                        <div t-if="state.dashboardData.mom_change" t-attf-class="elite_dashboard_card_change {{state.dashboardData.mom_change >= 0 ? 'positive' : 'negative'}}">
                            <t t-if="state.dashboardData.mom_change >= 0">↑</t>
                            <t t-else="">↓</t>
                            <t t-esc="Math.abs(state.dashboardData.mom_change).toFixed(1)"/>% from last month
                        </div>
                    </div>
                    
                    <!-- Completed Deals -->
                    <div class="elite_dashboard_card">
                        <div class="elite_dashboard_card_title">Completed Deals</div>
                        <div class="elite_dashboard_card_value">
                            <t t-esc="state.dashboardData.completed_deals"/>
                        </div>
                        <div class="elite_dashboard_card_subtitle">
                            <t t-esc="state.dashboardData.avg_per_agent.toFixed(1)"/> avg per agent
                        </div>
                    </div>
                    
                    <!-- In Progress Value -->
                    <div class="elite_dashboard_card">
                        <div class="elite_dashboard_card_title">In Progress Value</div>
                        <div class="elite_dashboard_card_value">
                            <t t-esc="formatCurrency(state.dashboardData.in_progress_value)"/>
                        </div>
                        <div class="elite_dashboard_card_subtitle">
                            <t t-esc="state.dashboardData.in_progress_deals"/> deals in progress
                        </div>
                    </div>
                    
                    <!-- Active Agents -->
                    <div class="elite_dashboard_card">
                        <div class="elite_dashboard_card_title">Active Agents</div>
                        <div class="elite_dashboard_card_value">
                            <t t-esc="state.dashboardData.agents_count"/>
                        </div>
                        <div class="elite_dashboard_card_subtitle">
                            <t t-esc="state.dashboardData.in_progress_deals"/> deals in progress
                        </div>
                    </div>
                </div>
                
                <!-- Charts and Leaderboard -->
                <div class="elite_dashboard_charts">
                    <!-- Annual Trend Chart -->
                    <div class="elite_dashboard_chart">
                        <div class="elite_dashboard_chart_title">Annual Sales Trend</div>
                        <canvas t-ref="annualTrendChart" height="300"></canvas>
                    </div>
                    
                    <!-- Leaderboard -->
                    <div class="elite_dashboard_leaderboard">
                        <div class="elite_dashboard_chart_title">Sales Leaderboard</div>
                        <div class="elite_dashboard_leaderboard_table">
                            <!-- Header -->
                            <div class="elite_dashboard_leaderboard_header">
                                <div class="elite_dashboard_leaderboard_rank">#</div>
                                <div class="elite_dashboard_leaderboard_agent">Agent</div>
                                <div class="elite_dashboard_leaderboard_stats">Stats</div>
                                <div class="elite_dashboard_leaderboard_sales">Sales</div>
                            </div>
                            
                            <!-- Rows -->
                            <t t-foreach="state.dashboardData.leaderboard" t-as="agent">
                                <div class="elite_dashboard_leaderboard_row">
                                    <div class="elite_dashboard_leaderboard_rank">
                                        <t t-esc="agent.rank"/>
                                    </div>
                                    <div class="elite_dashboard_leaderboard_agent">
                                        <div class="elite_dashboard_leaderboard_avatar">
                                            <t t-esc="agent.name.charAt(0)"/>
                                        </div>
                                        <div class="elite_dashboard_leaderboard_name">
                                            <t t-esc="agent.name"/>
                                        </div>
                                    </div>
                                    <div class="elite_dashboard_leaderboard_stats">
                                        <div class="elite_dashboard_leaderboard_deals">
                                            <t t-esc="agent.deals_count"/> deals • <t t-esc="agent.in_progress_count"/> in progress
                                        </div>
                                    </div>
                                    <div class="elite_dashboard_leaderboard_sales">
                                        <div class="elite_dashboard_leaderboard_amount">
                                            <t t-esc="formatCurrency(agent.total_sales)"/>
                                        </div>
                                        <div class="elite_dashboard_leaderboard_pending">
                                            <t t-esc="formatCurrency(agent.pending_value)"/> pending
                                        </div>
                                        <t t-if="state.settings.show_rank_changes && agent.rank_change !== 0">
                                            <div t-attf-class="elite_dashboard_rank_change {{agent.rank_change > 0 ? 'positive' : 'negative'}}">
                                                <t t-if="agent.rank_change > 0">↑</t>
                                                <t t-else="">↓</t>
                                            </div>
                                        </t>
                                    </div>
                                </div>
                            </t>
                        </div>
                    </div>
                </div>
                
                <!-- Footer -->
                <div class="elite_dashboard_footer">
                    <div class="elite_dashboard_update_info">
                        Live updates every <t t-esc="state.settings.refresh_interval"/> seconds • Last updated: <t t-esc="formatTime(state.lastUpdated)"/>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    return EliteDashboardComponent;
});