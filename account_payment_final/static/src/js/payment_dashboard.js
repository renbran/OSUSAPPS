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
            this.state.error = null;
            
            // Safe RPC call with fallback
            const data = await this.orm.call("account.payment", "get_dashboard_data", []).catch(() => {
                // Fallback data if method doesn't exist
                return {
                    pending: 0,
                    approved: 0,
                    total_amount: '0.00',
                    recent_payments: []
                };
            });
            
            this.state.paymentData = data;
        } catch (error) {
            console.error("Payment dashboard error:", error);
            this.state.error = error.message || "Unknown error occurred";
            this.notification.add(_t("Failed to load payment data"), { type: "danger" });
        } finally {
            this.state.isLoading = false;
        }
    }
    
    async onCreatePayment() {
        try {
            // Use standard Odoo action instead of custom method
            const action = {
                type: 'ir.actions.act_window',
                name: _t('Create Payment'),
                res_model: 'account.payment',
                view_mode: 'form',
                views: [[false, 'form']],
                target: 'current',
                context: {
                    default_payment_type: 'outbound'
                }
            };
            this.actionService.doAction(action);
        } catch (error) {
            console.error("Error creating payment:", error);
            this.notification.add(_t("Error creating payment"), { type: "danger" });
        }
    }
    
    cleanupResources() {
        // Clean up any subscriptions or intervals
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
    }
}

// Register the component properly
registry.category("fields").add("payment_dashboard", PaymentDashboardView);
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
