/** @odoo-module */

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";

export class CommissionLinesWidget extends Component {
  static template = "commission_lines.CommissionWidget";
  static props = {
    options: { type: Object, optional: true },
  };

  setup() {
    this.options = this.props.options || {};
  }

  mounted() {
    this._bindEvents();
  }

  _bindEvents() {
    const calculateBtn = this.el.querySelector(".commission-calculate");
    if (calculateBtn) {
      calculateBtn.addEventListener("click", () => {
        this._calculateCommission();
      });
    }
  }

  _calculateCommission() {
    // Commission calculation logic here
    console.log("Calculating commission...");
  }
}

registry
  .category("components")
  .add("CommissionLinesWidget", CommissionLinesWidget);
