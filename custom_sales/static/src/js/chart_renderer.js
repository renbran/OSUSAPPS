/** @odoo-module **/

export class ChartRenderer {
    constructor() {
        this.charts = new Map();
    }
    
    renderChart(canvasId, chartConfig) {
        if (!window.Chart) {
            console.error("Chart.js not loaded");
            return;
        }
        
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas ${canvasId} not found`);
            return;
        }
        
        // Destroy existing chart if any
        if (this.charts.has(canvasId)) {
            this.charts.get(canvasId).destroy();
        }
        
        const chart = new window.Chart(canvas, {
            type: chartConfig.type,
            data: chartConfig.data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                ...chartConfig.options
            }
        });
        
        this.charts.set(canvasId, chart);
        return chart;
    }
    
    updateChart(canvasId, newData) {
        const chart = this.charts.get(canvasId);
        if (chart) {
            chart.data = newData;
            chart.update();
        }
    }
    
    destroyChart(canvasId) {
        const chart = this.charts.get(canvasId);
        if (chart) {
            chart.destroy();
            this.charts.delete(canvasId);
        }
    }
    
    destroyAllCharts() {
        this.charts.forEach((chart, canvasId) => {
            chart.destroy();
        });
        this.charts.clear();
    }
}
