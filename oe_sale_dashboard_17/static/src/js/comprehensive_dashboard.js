/** @odoo-module **/

import { Component, onWillStart, onMounted, useRef, useState } from "@odoo/owl";
import { KanbanRenderer } from "@web/views/kanban/kanban_renderer";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

export class DashboardKanban extends KanbanRenderer {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.action = useService("action");
        this.chartRef = useRef("chartContainer");
        
        this.state = useState({
            chartData: null,
            loading: false,
            activeView: 'overview'
        });
        
        onMounted(() => {
            this.loadChartData();
            this.initializeAnimations();
        });
    }

    async loadChartData() {
        this.state.loading = true;
        try {
            // Load chart data from the dashboard model
            const records = this.props.list.records;
            if (records.length > 0) {
                const record = records[0];
                const chartData = await this.orm.call(
                    'sales.dashboard',
                    'get_sales_trend_data',
                    [record.resId]
                );
                this.state.chartData = chartData;
                if (this.chartRef.el) {
                    this.renderChart();
                }
            }
        } catch (error) {
            console.error('Error loading chart data:', error);
        } finally {
            this.state.loading = false;
        }
    }

    renderChart() {
        if (!this.chartRef.el || !this.state.chartData) return;

        // Clear existing chart
        this.chartRef.el.innerHTML = '';

        // Create chart container
        const chartContainer = document.createElement('div');
        chartContainer.className = 'o_dashboard_chart_container';
        chartContainer.innerHTML = `
            <h4 class="o_chart_title">Sales Trend</h4>
            <canvas id="salesTrendChart" width="400" height="200"></canvas>
        `;
        this.chartRef.el.appendChild(chartContainer);

        // Render chart using Chart.js or simple canvas
        this.renderSalesTrendChart();
    }

    renderSalesTrendChart() {
        const canvas = document.getElementById('salesTrendChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const data = this.state.chartData;
        
        // Simple line chart implementation
        const dates = Object.keys(data);
        const values = Object.values(data);
        const maxValue = Math.max(...values);
        const minValue = Math.min(...values);
        
        const width = canvas.width;
        const height = canvas.height;
        const padding = 40;
        
        // Clear canvas
        ctx.clearRect(0, 0, width, height);
        
        // Draw grid
        ctx.strokeStyle = '#e0e0e0';
        ctx.lineWidth = 1;
        
        // Vertical grid lines
        for (let i = 0; i <= 10; i++) {
            const x = padding + (i * (width - 2 * padding)) / 10;
            ctx.beginPath();
            ctx.moveTo(x, padding);
            ctx.lineTo(x, height - padding);
            ctx.stroke();
        }
        
        // Horizontal grid lines
        for (let i = 0; i <= 5; i++) {
            const y = padding + (i * (height - 2 * padding)) / 5;
            ctx.beginPath();
            ctx.moveTo(padding, y);
            ctx.lineTo(width - padding, y);
            ctx.stroke();
        }
        
        // Draw line chart
        if (values.length > 1) {
            ctx.strokeStyle = '#667eea';
            ctx.lineWidth = 3;
            ctx.beginPath();
            
            values.forEach((value, index) => {
                const x = padding + (index * (width - 2 * padding)) / (values.length - 1);
                const y = height - padding - ((value - minValue) / (maxValue - minValue)) * (height - 2 * padding);
                
                if (index === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            });
            
            ctx.stroke();
            
            // Draw points
            ctx.fillStyle = '#667eea';
            values.forEach((value, index) => {
                const x = padding + (index * (width - 2 * padding)) / (values.length - 1);
                const y = height - padding - ((value - minValue) / (maxValue - minValue)) * (height - 2 * padding);
                
                ctx.beginPath();
                ctx.arc(x, y, 4, 0, 2 * Math.PI);
                ctx.fill();
            });
        }
        
        // Add labels
        ctx.fillStyle = '#666';
        ctx.font = '12px Arial';
        ctx.textAlign = 'center';
        
        // X-axis labels (simplified)
        dates.forEach((date, index) => {
            if (index % Math.ceil(dates.length / 5) === 0) {
                const x = padding + (index * (width - 2 * padding)) / (dates.length - 1);
                const shortDate = new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
                ctx.fillText(shortDate, x, height - 10);
            }
        });
    }

    initializeAnimations() {
        // Add fade-in animation to dashboard cards
        const cards = document.querySelectorAll('.o_dashboard_card');
        cards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                card.style.transition = 'all 0.6s ease';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 100);
        });
    }

    async onActionViewSalesDetails(record) {
        const action = await this.orm.call(
            'sales.dashboard',
            'action_view_sales_details',
            [record.resId]
        );
        this.action.doAction(action);
    }

    async onActionViewTopPerformers(record) {
        const action = await this.orm.call(
            'sales.dashboard',
            'action_view_top_performers',
            [record.resId]
        );
        this.action.doAction(action);
    }

    async onActionViewInvoiceDetails(record) {
        const action = await this.orm.call(
            'sales.dashboard',
            'action_view_invoice_details',
            [record.resId]
        );
        this.action.doAction(action);
    }

    async onActionViewPaymentDetails(record) {
        const action = await this.orm.call(
            'sales.dashboard',
            'action_view_payment_details',
            [record.resId]
        );
        this.action.doAction(action);
    }

    async onActionViewReceivables(record) {
        const action = await this.orm.call(
            'sales.dashboard',
            'action_view_receivables',
            [record.resId]
        );
        this.action.doAction(action);
    }

    async onActionViewOverdue(record) {
        const action = await this.orm.call(
            'sales.dashboard',
            'action_view_overdue',
            [record.resId]
        );
        this.action.doAction(action);
    }
}

// Enhanced Chart Utility Functions
export class DashboardCharts {
    static createPieChart(canvas, data, colors) {
        const ctx = canvas.getContext('2d');
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        const radius = Math.min(centerX, centerY) - 20;
        
        let total = data.reduce((sum, value) => sum + value, 0);
        let currentAngle = -Math.PI / 2;
        
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        data.forEach((value, index) => {
            const sliceAngle = (value / total) * 2 * Math.PI;
            
            // Draw slice
            ctx.beginPath();
            ctx.moveTo(centerX, centerY);
            ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle);
            ctx.closePath();
            ctx.fillStyle = colors[index % colors.length];
            ctx.fill();
            
            // Draw border
            ctx.strokeStyle = '#fff';
            ctx.lineWidth = 2;
            ctx.stroke();
            
            currentAngle += sliceAngle;
        });
    }

    static createBarChart(canvas, data, labels, color) {
        const ctx = canvas.getContext('2d');
        const width = canvas.width;
        const height = canvas.height;
        const padding = 40;
        const barWidth = (width - 2 * padding) / data.length;
        const maxValue = Math.max(...data);
        
        ctx.clearRect(0, 0, width, height);
        
        // Draw bars
        data.forEach((value, index) => {
            const barHeight = (value / maxValue) * (height - 2 * padding);
            const x = padding + index * barWidth;
            const y = height - padding - barHeight;
            
            // Create gradient
            const gradient = ctx.createLinearGradient(0, y, 0, y + barHeight);
            gradient.addColorStop(0, color);
            gradient.addColorStop(1, color + '80');
            
            ctx.fillStyle = gradient;
            ctx.fillRect(x + 5, y, barWidth - 10, barHeight);
            
            // Add value labels
            ctx.fillStyle = '#333';
            ctx.font = '12px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(value.toLocaleString(), x + barWidth / 2, y - 5);
            
            // Add category labels
            if (labels && labels[index]) {
                ctx.save();
                ctx.translate(x + barWidth / 2, height - 10);
                ctx.rotate(-Math.PI / 6);
                ctx.textAlign = 'right';
                ctx.fillText(labels[index], 0, 0);
                ctx.restore();
            }
        });
    }

    static createDonutChart(canvas, data, colors, centerText) {
        const ctx = canvas.getContext('2d');
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        const outerRadius = Math.min(centerX, centerY) - 20;
        const innerRadius = outerRadius * 0.6;
        
        let total = data.reduce((sum, value) => sum + value, 0);
        let currentAngle = -Math.PI / 2;
        
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        data.forEach((value, index) => {
            const sliceAngle = (value / total) * 2 * Math.PI;
            
            // Draw slice
            ctx.beginPath();
            ctx.arc(centerX, centerY, outerRadius, currentAngle, currentAngle + sliceAngle);
            ctx.arc(centerX, centerY, innerRadius, currentAngle + sliceAngle, currentAngle, true);
            ctx.closePath();
            ctx.fillStyle = colors[index % colors.length];
            ctx.fill();
            
            // Draw border
            ctx.strokeStyle = '#fff';
            ctx.lineWidth = 2;
            ctx.stroke();
            
            currentAngle += sliceAngle;
        });
        
        // Draw center text
        if (centerText) {
            ctx.fillStyle = '#333';
            ctx.font = 'bold 16px Arial';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(centerText, centerX, centerY);
        }
    }
}

// Dashboard Utility Functions
export class DashboardUtils {
    static formatCurrency(amount, currency = 'USD') {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency
        }).format(amount);
    }

    static formatPercentage(value, decimals = 1) {
        return value.toFixed(decimals) + '%';
    }

    static getGrowthIcon(value) {
        if (value > 0) return '↗';
        if (value < 0) return '↘';
        return '→';
    }

    static getGrowthClass(value) {
        if (value > 0) return 'text-success';
        if (value < 0) return 'text-danger';
        return 'text-muted';
    }

    static animateNumber(element, target, duration = 1000) {
        const start = 0;
        const startTime = Date.now();
        
        const updateNumber = () => {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const current = start + (target - start) * this.easeOutQuart(progress);
            
            element.textContent = Math.round(current).toLocaleString();
            
            if (progress < 1) {
                requestAnimationFrame(updateNumber);
            }
        };
        
        requestAnimationFrame(updateNumber);
    }

    static easeOutQuart(t) {
        return 1 - Math.pow(1 - t, 4);
    }

    static debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Export for use in other components
export { DashboardKanban, DashboardCharts, DashboardUtils };

// Register components
registry.category("views").add("dashboard_kanban", DashboardKanban);