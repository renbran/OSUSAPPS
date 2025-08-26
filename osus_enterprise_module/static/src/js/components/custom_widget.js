/** @odoo-module **/
import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

export class CustomWidget extends Component {
  static template = "osus_enterprise_module.CustomWidgetTemplate";
  static props = {
    record: Object,
    name: String,
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
      const data = await this.orm.call("osus.main.model", "get_custom_data", [
        this.props.record.resId,
      ]);
      this.state.data = data;
    } catch (error) {
      this.notification.add(_t("Failed to load data: %s", error.message), {
        type: "danger",
      });
    } finally {
      this.state.isLoading = false;
    }
  }

  async onSaveData() {
    if (this.props.readonly) return;
    try {
      await this.orm.call("osus.main.model", "save_custom_data", [
        this.props.record.resId,
        this.state.data,
      ]);
      this.notification.add(_t("Data saved successfully"), {
        type: "success",
      });
    } catch (error) {
      this.notification.add(_t("Save failed: %s", error.message), {
        type: "danger",
      });
    }
  }
}

registry.category("fields").add("custom_widget", CustomWidget);
