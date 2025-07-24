/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, useState, onWillStart } from "@odoo/owl";

export class EliteDashboard extends Component {
    static template = "elite_sales_dashboard.Dashboard";
    
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.currentView = useState({ value: "internal" });
        this.dashboardData = useState({});
        this.settings = useState({});
        
        onWillStart(async () => {
            await this.loadDashboardData();
        });
    }

    async loadDashboardData() {
        try {
            const [settings, data] = await Promise.all([
                this.orm.call("elite.dashboard.settings", "get_settings"),
                this.orm.call("elite.agent.dashboard", "get_dashboard_data", [], {
                    agent_type: this.currentView.value
                })
            ]);
            this.settings.value = settings;
            this.dashboardData.value = data;
        } catch (error) {
            console.error("Dashboard loading error:", error);
        }
    }

    async onToggleView(ev) {
        const view = ev.currentTarget.dataset.view;
        if (view !== this.currentView.value) {
            this.currentView.value = view;
            await this.loadDashboardData();
        }
    }
}

// Proper action registration
registry.category("actions").add("elite_dashboard", EliteDashboard);