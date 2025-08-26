/** @odoo-module **/
import { ListController } from "@web/views/list/list_controller";
import { patch } from "@web/core/utils/patch";

patch(ListController.prototype, {
    setup() {
        super.setup();
    },
    async onCustomAction() {
        const selectedRecords = await this.getSelectedResIds();
        if (!selectedRecords.length) {
            this.notification.add(_t("Please select at least one record"), {
                type: "warning",
            });
            return;
        }
        await this.orm.call(
            this.props.resModel,
            "custom_bulk_action",
            [selectedRecords]
        );
        await this.model.load();
    },
});
