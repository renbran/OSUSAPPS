/** @odoo-module */

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

/**
 * Enhanced Sale Order Form Widget
 * Adds interactive features to the tabbed sale order form
 */
export class SaleOrderFormEnhanced extends Component {
  static template = "enhanced_status.SaleOrderFormEnhanced";

  setup() {
    this.orm = useService("orm");
    this.notification = useService("notification");

    this.state = useState({
      activeTab: "order_details",
      completionProgress: 0,
      financialSummary: {
        invoiced: 0,
        paid: 0,
        balance: 0,
      },
    });

    onWillStart(async () => {
      await this.loadFinancialData();
    });
  }

  /**
   * Switch between tabs with visual feedback
   */
  switchTab(tabName) {
    this.state.activeTab = tabName;
    this.highlightTabContent();
  }

  /**
   * Add visual feedback when switching tabs
   */
  highlightTabContent() {
    const tabContent = document.querySelector(
      `[name="${this.state.activeTab}"]`
    );
    if (tabContent) {
      tabContent.classList.add("tab-switching");
      setTimeout(() => {
        tabContent.classList.remove("tab-switching");
      }, 300);
    }
  }

  /**
   * Load financial data for the current order
   */
  async loadFinancialData() {
    if (this.props.resId) {
      try {
        const orderData = await this.orm.read(
          "sale.order",
          [this.props.resId],
          [
            "invoiced_amount",
            "paid_amount",
            "balance_amount",
            "completion_criteria_met",
          ]
        );

        if (orderData.length > 0) {
          const order = orderData[0];
          this.state.financialSummary = {
            invoiced: order.invoiced_amount,
            paid: order.paid_amount,
            balance: order.balance_amount,
          };

          // Calculate completion progress
          this.calculateCompletionProgress(order);
        }
      } catch (error) {
        console.error("Error loading financial data:", error);
      }
    }
  }

  /**
   * Calculate completion progress based on various criteria
   */
  calculateCompletionProgress(order) {
    let progress = 0;

    // Check if order has lines
    if (order.order_line && order.order_line.length > 0) progress += 25;

    // Check invoicing status
    if (order.invoiced_amount > 0) progress += 25;

    // Check payment status
    if (order.paid_amount > 0) progress += 25;

    // Check if criteria met
    if (order.completion_criteria_met) progress += 25;

    this.state.completionProgress = progress;
  }

  /**
   * Show workflow help dialog
   */
  showWorkflowHelp() {
    this.notification.add(
      `
            <div class="workflow-help">
                <h4>Workflow Stages Guide:</h4>
                <ul>
                    <li><strong>Documentation:</strong> Gather requirements and specifications</li>
                    <li><strong>Calculation:</strong> Perform pricing and technical calculations</li>
                    <li><strong>Approved:</strong> Final approval before execution</li>
                    <li><strong>Completed:</strong> Order fulfilled and locked</li>
                </ul>
            </div>
            `,
      { type: "info", title: "Workflow Help", sticky: false }
    );
  }

  /**
   * Validate tab before switching
   */
  validateBeforeSwitch(targetTab) {
    // Add validation logic here if needed
    // For example, ensure required fields are filled before moving to next tab
    return true;
  }

  /**
   * Auto-save functionality when switching tabs
   */
  async autoSave() {
    if (this.props.resId) {
      try {
        // Trigger form save
        this.trigger("save");
        this.notification.add("Changes auto-saved", { type: "success" });
      } catch (error) {
        this.notification.add("Auto-save failed", { type: "danger" });
      }
    }
  }
}

// Register the component
registry
  .category("form_widgets")
  .add("sale_order_enhanced", SaleOrderFormEnhanced);

/**
 * Tab Progress Indicator Component
 */
export class TabProgressIndicator extends Component {
  static template = "enhanced_status.TabProgressIndicator";
  static props = ["progress", "stage"];

  get progressBarStyle() {
    return `width: ${this.props.progress}%`;
  }

  get progressColor() {
    if (this.props.progress < 25) return "bg-danger";
    if (this.props.progress < 50) return "bg-warning";
    if (this.props.progress < 75) return "bg-info";
    return "bg-success";
  }
}

registry
  .category("form_widgets")
  .add("tab_progress_indicator", TabProgressIndicator);

/**
 * Financial Status Widget
 */
export class FinancialStatusWidget extends Component {
  static template = "enhanced_status.FinancialStatusWidget";
  static props = ["invoiced", "paid", "balance", "total"];

  get invoicedPercentage() {
    return this.props.total > 0
      ? Math.round((this.props.invoiced / this.props.total) * 100)
      : 0;
  }

  get paidPercentage() {
    return this.props.total > 0
      ? Math.round((this.props.paid / this.props.total) * 100)
      : 0;
  }

  get balancePercentage() {
    return this.props.total > 0
      ? Math.round((this.props.balance / this.props.total) * 100)
      : 0;
  }
}

registry
  .category("form_widgets")
  .add("financial_status_widget", FinancialStatusWidget);

// Auto-initialize when DOM is ready
document.addEventListener("DOMContentLoaded", function () {
  // Add smooth transitions to tab switching
  const style = document.createElement("style");
  style.textContent = `
        .tab-switching {
            opacity: 0.7;
            transform: translateY(-5px);
            transition: all 0.3s ease;
        }
        
        .workflow-help ul {
            margin: 10px 0;
            padding-left: 20px;
        }
        
        .workflow-help li {
            margin-bottom: 5px;
        }
    `;
  document.head.appendChild(style);
});
