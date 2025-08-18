/** @odoo-module **/

import { Component, useState, onMounted, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

// OSUS Properties Brand Colors
const brandColors = {
    primary: '#800020',
    gold: '#FFD700',
    lightGold: '#FFF8DC',
    darkGold: '#B8860B',
    white: '#FFFFFF',
    accent: '#A0522D'
};

export class PaymentDashboardView extends Component {
    static template = "account_payment_final.Dashboard";
    static props = ["*"];
    
    setup() {
        this.orm = useService("orm");
        this.actionService = useService("action");
        this.notification = useService("notification");
        
        this.state = useState({
            isLoading: true,
            paymentData: {},
            error: null
        });
        
        onMounted(async () => {
            await this.loadPaymentData();
        });
        
        onWillUnmount(() => {
            this.cleanupResources();
        });
    }
    
    async loadPaymentData() {
        try {
            this.state.isLoading = true;
            const data = await this.orm.call("account.payment", "get_dashboard_data", []);
            this.state.paymentData = data;
            this.state.error = null;
        } catch (error) {
            console.error("Payment dashboard error:", error);
            this.state.error = error.message;
            this.notification.add(_t("Failed to load payment data"), { type: "danger" });
        } finally {
            this.state.isLoading = false;
        }
    }
    
    async onCreatePayment() {
        try {
            const action = await this.orm.call("account.payment", "action_create_payment", []);
            this.actionService.doAction(action);
        } catch (error) {
            this.notification.add(_t("Error creating payment"), { type: "danger" });
        }
    }
    
    cleanupResources() {
        // Cleanup any resources, event listeners, etc.
        console.log("Payment dashboard cleanup");
    }
}

registry.category("views").add("payment_dashboard", PaymentDashboardView);
