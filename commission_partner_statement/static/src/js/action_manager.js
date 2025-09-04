/** @odoo-module **/

import { registry } from "@web/core/registry";
import { download } from "@web/core/network/download";

// Handle Excel report download
export function downloadCommissionExcel(action, options, env) {
  if (action.url) {
    download({
      url: action.url,
      data: {},
      complete: () => false,
      error: (error) => {
        env.services.notification.add(
          env._t("Error downloading commission statement: ") + error.message,
          { type: "danger" }
        );
      },
    });
  }
  return Promise.resolve(true);
}

registry
  .category("ir.actions.report handlers")
  .add("commission_excel_handler", downloadCommissionExcel);
