/** @odoo-module **/
import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

export class LeadCaptureWidget extends Component {
    static template = "auto_lead_capture.LeadCaptureWidgetTemplate";
    static props = {
        record: Object,
        readonly: { type: Boolean, optional: true },
    };

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.state = useState({
            isLoading: false,
            data: null,
        });
        onWillStart(this.loadData);
    }

    async loadData() {
        this.state.isLoading = true;
        try {
            const data = await this.orm.call(
                "auto.lead.capture",
                "get_lead_data",
                [this.props.record.resId]
            );
            this.state.data = data;
        } catch (error) {
            this.notification.add(
                _t("Failed to load lead data: %s", error.message),
                { type: "danger" }
            );
        } finally {
            this.state.isLoading = false;
        }
    }

    async onAssignLead() {
        if (this.props.readonly) return;
        try {
            await this.orm.call(
                "auto.lead.capture",
                "assign_lead",
                [this.props.record.resId]
            );
            this.notification.add(_t("Lead assigned successfully"), {
                type: "success",
            });
        } catch (error) {
            this.notification.add(
                _t("Assignment failed: %s", error.message),
                { type: "danger" }
            );
        }
    }
}

registry.category("fields").add("lead_capture_widget", LeadCaptureWidget);
