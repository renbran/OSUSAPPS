/** @odoo-module */

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class CommissionDashboard extends Component {
    static template = "CommissionDashboard";
    static props = {};

    setup() {
        this.rpc = useService("rpc");
        this.commission_data = {};
        this.dashboards_templates = ['CommissionDashboard'];
    }

    async mounted() {
        await this.fetch_data();
        this.render_dashboard();
        
        const refreshBtn = this.el.querySelector('.commission_refresh');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', async () => {
                await this.fetch_data();
                this.render_dashboard();
            });
        }
    }

    async fetch_data() {
        try {
            this.commission_data = await this.rpc("/web/dataset/call_kw", {
                model: 'commission.line',
                method: 'get_dashboard_data',
                args: [],
                kwargs: {},
            });
        } catch (error) {
            console.error('Error fetching commission data:', error);
            this.commission_data = {};
        }
    }

    render_dashboard() {
        const contentEl = this.el.querySelector('.commission_dashboard_content');
        if (contentEl) {
            // For now, just display basic data
            // In a full implementation, you'd use a proper template
            contentEl.innerHTML = `
                <div class="commission-summary">
                    <h3>Commission Dashboard</h3>
                    <p>Data loaded: ${JSON.stringify(this.commission_data)}</p>
                </div>
            `;
        }
    }
}

registry.category("actions").add("commission_dashboard", CommissionDashboard);