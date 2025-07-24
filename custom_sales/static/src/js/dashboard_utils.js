/** @odoo-module **/

export const DashboardUtils = {
    
    formatCurrency(value, currency = 'USD') {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency
        }).format(value || 0);
    },
    
    formatNumber(value, decimals = 0) {
        return new Intl.NumberFormat('en-US', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        }).format(value || 0);
    },
    
    formatPercentage(value, decimals = 2) {
        return `${(value || 0).toFixed(decimals)}%`;
    },
    
    formatDate(date, format = 'short') {
        if (!date) return '';
        
        const options = {
            short: { year: 'numeric', month: 'short', day: 'numeric' },
            long: { year: 'numeric', month: 'long', day: 'numeric' },
            time: { 
                year: 'numeric', 
                month: 'short', 
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            }
        };
        
        return new Intl.DateTimeFormat('en-US', options[format] || options.short).format(new Date(date));
    },
    
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    downloadFile(data, filename, type = 'text/plain') {
        const blob = new Blob([data], { type });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
    },
    
    getRandomColor() {
        const colors = [
            '#8B0000', // Burgundy
            '#FFD700', // Gold
            '#F5DEB3', // Light Gold
            '#A0522D', // Sienna
            '#CD853F', // Peru
            '#DEB887', // Burlywood
        ];
        return colors[Math.floor(Math.random() * colors.length)];
    },
    
    generateColorPalette(count) {
        const baseColors = ['#8B0000', '#FFD700', '#F5DEB3', '#A0522D'];
        const palette = [];
        
        for (let i = 0; i < count; i++) {
            palette.push(baseColors[i % baseColors.length]);
        }
        
        return palette;
    },
    
    calculatePercentageChange(current, previous) {
        if (!previous || previous === 0) return 0;
        return ((current - previous) / previous) * 100;
    },
    
    groupBy(array, key) {
        return array.reduce((groups, item) => {
            const group = item[key];
            if (!groups[group]) {
                groups[group] = [];
            }
            groups[group].push(item);
            return groups;
        }, {});
    },
    
    sumBy(array, key) {
        return array.reduce((sum, item) => sum + (item[key] || 0), 0);
    },
    
    avgBy(array, key) {
        if (array.length === 0) return 0;
        return this.sumBy(array, key) / array.length;
    },
    
    maxBy(array, key) {
        if (array.length === 0) return null;
        return Math.max(...array.map(item => item[key] || 0));
    },
    
    minBy(array, key) {
        if (array.length === 0) return null;
        return Math.min(...array.map(item => item[key] || 0));
    }
};
