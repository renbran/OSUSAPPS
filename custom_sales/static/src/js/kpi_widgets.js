/** @odoo-module **/

import { Component } from "@odoo/owl";

export class KpiWidget extends Component {
    static template = "custom_sales.KpiWidgetTemplate";
    static props = {
        kpi: Object,
        className: { type: String, optional: true }
    };
    
    formatValue(value, formatType) {
        switch (formatType) {
            case 'currency':
                return new Intl.NumberFormat('en-US', {
                    style: 'currency',
                    currency: 'USD'
                }).format(value || 0);
            case 'percentage':
                return `${(value || 0).toFixed(2)}%`;
            case 'integer':
                return Math.round(value || 0).toLocaleString();
            default:
                return (value || 0).toLocaleString();
        }
    }
    
    get formattedValue() {
        return this.formatValue(this.props.kpi.value, this.props.kpi.format_type);
    }
    
    get kpiClass() {
        const baseClass = 'kpi-widget';
        const customClass = this.props.className || '';
        return `${baseClass} ${customClass}`.trim();
    }
}

export class KpiContainer extends Component {
    static template = "custom_sales.KpiContainerTemplate";
    static components = { KpiWidget };
    static props = {
        kpis: Array,
        columns: { type: Number, optional: true }
    };
    
    get gridColumns() {
        const columns = this.props.columns || 4;
        return `repeat(${columns}, 1fr)`;
    }
}
