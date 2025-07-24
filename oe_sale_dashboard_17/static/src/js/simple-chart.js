window.SimpleChart = class SimpleChart {
    constructor(ctx, config) {
        this.ctx = ctx;
        this.canvas = ctx.canvas;
        this.config = config;
        this.data = config.data;
        this.options = config.options || {};
        this.type = config.type;
        
        this.render();
    }

    render() {
        const canvas = this.canvas;
        const ctx = this.ctx;
        
        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        if (this.type === 'doughnut') {
            this.renderDoughnut();
        } else if (this.type === 'line') {
            this.renderLine();
        }
    }

    renderDoughnut() {
        const canvas = this.canvas;
        const ctx = this.ctx;
        const data = this.data.datasets[0].data;
        const labels = this.data.labels;
        const colors = this.data.datasets[0].backgroundColor;
        
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        const radius = Math.min(centerX, centerY) - 40;
        const innerRadius = radius * 0.6;
        
        let total = data.reduce((sum, value) => sum + value, 0);
        let currentAngle = -Math.PI / 2;
        
        // Draw segments
        data.forEach((value, index) => {
            if (value > 0) {
                const sliceAngle = (value / total) * 2 * Math.PI;
                
                ctx.beginPath();
                ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle);
                ctx.arc(centerX, centerY, innerRadius, currentAngle + sliceAngle, currentAngle, true);
                ctx.closePath();
                
                ctx.fillStyle = colors[index];
                ctx.fill();
                
                // Add stroke
                ctx.strokeStyle = '#fff';
                ctx.lineWidth = 2;
                ctx.stroke();
                
                currentAngle += sliceAngle;
            }
        });
        
        // Draw center text
        ctx.fillStyle = '#374151';
        ctx.font = 'bold 16px Inter';
        ctx.textAlign = 'center';
        ctx.fillText('Revenue', centerX, centerY - 5);
        ctx.font = '12px Inter';
        ctx.fillText('Distribution', centerX, centerY + 15);
    }

    renderLine() {
        const canvas = this.canvas;
        const ctx = this.ctx;
        const datasets = this.data.datasets;
        const labels = this.data.labels;
        
        const padding = 60;
        const chartWidth = canvas.width - 2 * padding;
        const chartHeight = canvas.height - 2 * padding;
        
        // Find max value
        let maxValue = 0;
        datasets.forEach(dataset => {
            maxValue = Math.max(maxValue, ...dataset.data);
        });
        
        // Draw grid
        ctx.strokeStyle = '#e5e7eb';
        ctx.lineWidth = 1;
        
        // Horizontal grid lines
        for (let i = 0; i <= 5; i++) {
            const y = padding + (chartHeight / 5) * i;
            ctx.beginPath();
            ctx.moveTo(padding, y);
            ctx.lineTo(padding + chartWidth, y);
            ctx.stroke();
        }
        
        // Vertical grid lines
        for (let i = 0; i <= labels.length - 1; i++) {
            const x = padding + (chartWidth / (labels.length - 1)) * i;
            ctx.beginPath();
            ctx.moveTo(x, padding);
            ctx.lineTo(x, padding + chartHeight);
            ctx.stroke();
        }
        
        // Draw datasets
        datasets.forEach(dataset => {
            ctx.strokeStyle = dataset.borderColor;
            ctx.fillStyle = dataset.backgroundColor;
            ctx.lineWidth = 3;
            
            // Draw line
            ctx.beginPath();
            dataset.data.forEach((value, index) => {
                const x = padding + (chartWidth / (labels.length - 1)) * index;
                const y = padding + chartHeight - (value / maxValue) * chartHeight;
                
                if (index === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            });
            ctx.stroke();
            
            // Draw points
            ctx.fillStyle = dataset.borderColor;
            dataset.data.forEach((value, index) => {
                const x = padding + (chartWidth / (labels.length - 1)) * index;
                const y = padding + chartHeight - (value / maxValue) * chartHeight;
                
                ctx.beginPath();
                ctx.arc(x, y, 4, 0, 2 * Math.PI);
                ctx.fill();
            });
        });
        
        // Draw labels
        ctx.fillStyle = '#374151';
        ctx.font = '12px Inter';
        ctx.textAlign = 'center';
        labels.forEach((label, index) => {
            const x = padding + (chartWidth / (labels.length - 1)) * index;
            ctx.fillText(label, x, canvas.height - 20);
        });
    }

    destroy() {
        // Cleanup if needed
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }
};

// Make Chart available globally for compatibility
if (typeof Chart === 'undefined') {
    window.Chart = window.SimpleChart;
}
