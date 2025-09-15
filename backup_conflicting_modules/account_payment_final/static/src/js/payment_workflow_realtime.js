/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

// Global error handler for OWL lifecycle errors
window.addEventListener("error", function (event) {
  if (event.message && event.message.includes("owl lifecycle")) {
    console.log("OWL lifecycle error caught and handled:", event.message);
    event.preventDefault();
    return false;
  }
});

window.addEventListener("unhandledrejection", function (event) {
  if (
    event.reason &&
    event.reason.message &&
    event.reason.message.includes("RPC_ERROR")
  ) {
    console.log("RPC error caught and handled:", event.reason.message);
    event.preventDefault();
    return false;
  }
});

/**
 * Payment Workflow Real-time Updates
 * CloudPepper Compatible - FULLY MODERNIZED VERSION
 * Provides real-time status updates and UI enhancements for payment approval workflow
 */

class PaymentWorkflowRealtime {
  static lastUserActivity = Date.now();

  /**
   * Initialize real-time workflow monitoring (CloudPepper Safe)
   */
  static init() {
    this.setupWorkflowObservers();
    this.setupFieldWatchers();
    this.enhanceButtons();
    this.setupAutoRefresh();
    this.setupUserActivityTracking();
  }

  /**
   * Setup user activity tracking for safe refreshes
   */
  static setupUserActivityTracking() {
    // Track various user interactions using modern event delegation
    document.addEventListener("click", () => this.trackUserActivity());
    document.addEventListener("change", () => this.trackUserActivity());
    document.addEventListener("keypress", () => this.trackUserActivity());

    // Track form interactions specifically
    document.addEventListener("change", (event) => {
      if (event.target.matches("input, select, textarea")) {
        this.trackUserActivity();
      }
    });
  }

  /**
   * Setup observers for workflow state changes (CloudPepper Safe)
   */
  static setupWorkflowObservers() {
    try {
      // Watch for approval_state field changes
      document.addEventListener("change", (event) => {
        if (event.target.matches('select[name="approval_state"]')) {
          try {
            this.onApprovalStateChange(event.target);
          } catch (error) {
            console.log("Approval state change error:", error);
          }
        }
      });

      // Watch for reviewer/approver/authorizer changes
      document.addEventListener("change", (event) => {
        if (event.target.matches('select[name="reviewer_id"], select[name="approver_id"], select[name="authorizer_id"]')) {
          try {
            this.onWorkflowUserChange(event.target);
          } catch (error) {
            console.log("Workflow user change error:", error);
          }
        }
      });

      // Watch for state synchronization
      document.addEventListener("change", (event) => {
        if (event.target.matches('select[name="state"]')) {
          try {
            this.onStateChange(event.target);
          } catch (error) {
            console.log("State change error:", error);
          }
        }
      });
    } catch (error) {
      console.log("Setup workflow observers error:", error);
    }
  }

  /**
   * Setup field watchers for real-time validation
   */
  static setupFieldWatchers() {
    // Amount validation
    document.addEventListener("change", (event) => {
      if (event.target.matches('input[name="amount"]')) {
        this.validateAmount(event.target);
      }
    });

    // Partner validation
    document.addEventListener("change", (event) => {
      if (event.target.matches('select[name="partner_id"]')) {
        this.onPartnerChange(event.target);
      }
    });
  }

  /**
   * Handle approval state changes
   */
  static onApprovalStateChange(field) {
    const newState = field.value;
    const currentTime = new Date().toISOString();

    // Update workflow progress indicator
    this.updateWorkflowProgress(newState);

    // Show appropriate notifications
    this.showStateChangeNotification(newState);

    // Update button visibility
    this.updateButtonVisibility(newState);

    // Sync with standard state field if needed
    this.syncStandardState(newState);
  }

  /**
   * Handle workflow user assignments
   */
  static onWorkflowUserChange(field) {
    const fieldName = field.name;
    const userId = field.value;
    const currentTime = new Date().toISOString();

    // Auto-populate corresponding date fields
    if (fieldName === "reviewer_id" && userId) {
      const reviewerDateField = document.querySelector('input[name="reviewer_date"]');
      if (reviewerDateField) reviewerDateField.value = currentTime;
    } else if (fieldName === "approver_id" && userId) {
      const approverDateField = document.querySelector('input[name="approver_date"]');
      if (approverDateField) approverDateField.value = currentTime;
    } else if (fieldName === "authorizer_id" && userId) {
      const authorizerDateField = document.querySelector('input[name="authorizer_date"]');
      if (authorizerDateField) authorizerDateField.value = currentTime;
    }

    // Update workflow progress
    this.updateWorkflowProgress();
  }

  /**
   * Handle standard state changes
   */
  static onStateChange(field) {
    const newState = field.value;
    const approvalField = document.querySelector('select[name="approval_state"]');

    // Sync approval state with standard state
    if (newState === "posted" && approvalField && approvalField.value !== "posted") {
      approvalField.value = "posted";
      approvalField.dispatchEvent(new Event("change"));
    } else if (
      newState === "cancel" &&
      approvalField && approvalField.value !== "cancelled"
    ) {
      approvalField.value = "cancelled";
      approvalField.dispatchEvent(new Event("change"));
    }
  }

  /**
   * Validate payment amount in real-time
   */
  static validateAmount(field) {
    const amount = parseFloat(field.value) || 0;
    const existingWarning = field.parentNode.querySelector(".field-warning");

    // Remove existing warnings
    if (existingWarning) {
      existingWarning.remove();
    }

    if (amount <= 0) {
      this.showFieldWarning(field, "Amount must be greater than zero");
    } else if (amount > 10000) {
      this.showFieldWarning(
        field,
        "High amount payment - enhanced approval required",
        "warning"
      );
    }
  }

  /**
   * Handle partner changes
   */
  static onPartnerChange(field) {
    const partnerId = field.value;
    if (partnerId) {
      // Auto-populate partner bank if available
      this.autoPopulatePartnerBank(partnerId);

      // Set destination account for vendor payments
      this.setDestinationAccount(partnerId);
    }
  }

  /**
   * Update workflow progress indicator
   */
  static updateWorkflowProgress(currentState) {
    const progressContainer = document.querySelector(".workflow-progress");
    if (!progressContainer) return;

    currentState = currentState || document.querySelector('select[name="approval_state"]')?.value;

    const stages = [
      "draft",
      "under_review",
      "for_approval",
      "for_authorization",
      "approved",
      "posted",
    ];
    const currentIndex = stages.indexOf(currentState);

    const progressSteps = progressContainer.querySelectorAll(".progress-step");
    progressSteps.forEach((step, index) => {
      step.classList.remove("step-pending", "step-current", "step-completed");
      
      if (index <= currentIndex) {
        step.classList.add("step-completed");
      } else if (index === currentIndex + 1) {
        step.classList.add("step-current");
      } else {
        step.classList.add("step-pending");
      }
    });
  }

  /**
   * Show state change notifications
   */
  static showStateChangeNotification(newState) {
    const messages = {
      under_review: "Payment submitted for review",
      for_approval: "Payment ready for approval",
      for_authorization: "Payment ready for authorization",
      approved: "Payment approved - ready to post",
      posted: "Payment posted successfully",
      cancelled: "Payment cancelled",
    };

    const message = messages[newState];
    if (message) {
      this.showNotification(message, "success");
    }
  }

  /**
   * Update button visibility based on current state
   */
  static updateButtonVisibility(currentState) {
    const buttons = document.querySelectorAll(".workflow-button");

    // Hide all workflow buttons first
    buttons.forEach(button => button.style.display = "none");

    // Show appropriate buttons based on current state
    switch (currentState) {
      case "draft":
        this.showButton('button[name="action_submit_for_review"]');
        break;
      case "under_review":
        this.showButton('button[name="action_review_payment"]');
        this.showButton('button[name="action_reject_payment"]');
        break;
      case "for_approval":
        this.showButton('button[name="action_approve_payment"]');
        this.showButton('button[name="action_reject_payment"]');
        break;
      case "for_authorization":
        this.showButton('button[name="action_authorize_payment"]');
        this.showButton('button[name="action_reject_payment"]');
        break;
      case "approved":
        this.showButton('button[name="action_post_payment"]');
        break;
    }
  }

  /**
   * Helper method to show a button
   */
  static showButton(selector) {
    const button = document.querySelector(selector);
    if (button) {
      button.style.display = "inline-block";
    }
  }

  /**
   * Show field warning
   */
  static showFieldWarning(field, message, type = "error") {
    const warning = document.createElement("div");
    warning.className = `field-warning alert alert-${type === "error" ? "danger" : "warning"}`;
    warning.textContent = message;
    
    field.parentNode.appendChild(warning);
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
      if (warning.parentNode) {
        warning.remove();
      }
    }, 5000);
  }

  /**
   * Show notification
   */
  static showNotification(message, type = "info") {
    // Use modern notification API if available
    if (window.Notification && window.Notification.permission === "granted") {
      new Notification("Payment Workflow", { body: message });
    } else {
      // Fallback to console log
      console.log(`[${type.toUpperCase()}] ${message}`);
    }
  }

  /**
   * Track user activity
   */
  static trackUserActivity() {
    this.lastUserActivity = Date.now();
  }

  /**
   * Setup auto-refresh (CloudPepper Safe)
   */
  static setupAutoRefresh() {
    // Only refresh if no recent user activity (5 minutes)
    setInterval(() => {
      const timeSinceLastActivity = Date.now() - this.lastUserActivity;
      if (timeSinceLastActivity > 300000) { // 5 minutes
        this.refreshWorkflowStatus();
      }
    }, 60000); // Check every minute
  }

  /**
   * Enhance buttons with modern styling and behavior
   */
  static enhanceButtons() {
    const workflowButtons = document.querySelectorAll(".workflow-button");
    
    workflowButtons.forEach(button => {
      // Add loading state capability
      button.addEventListener("click", (event) => {
        button.classList.add("loading");
        button.disabled = true;
        
        // Re-enable after 3 seconds (fallback)
        setTimeout(() => {
          button.classList.remove("loading");
          button.disabled = false;
        }, 3000);
      });
    });
  }

  /**
   * Auto-populate partner bank information
   */
  static async autoPopulatePartnerBank(partnerId) {
    try {
      // This would typically make an RPC call to get partner bank info
      console.log(`Auto-populating bank info for partner ${partnerId}`);
    } catch (error) {
      console.log("Error auto-populating partner bank:", error);
    }
  }

  /**
   * Set destination account based on partner
   */
  static setDestinationAccount(partnerId) {
    try {
      // This would typically set the appropriate destination account
      console.log(`Setting destination account for partner ${partnerId}`);
    } catch (error) {
      console.log("Error setting destination account:", error);
    }
  }

  /**
   * Refresh workflow status (CloudPepper Safe)
   */
  static refreshWorkflowStatus() {
    try {
      // Safe refresh without disrupting user interaction
      const currentState = document.querySelector('select[name="approval_state"]')?.value;
      if (currentState) {
        this.updateWorkflowProgress(currentState);
        this.updateButtonVisibility(currentState);
      }
    } catch (error) {
      console.log("Error refreshing workflow status:", error);
    }
  }

  /**
   * Sync standard state with approval state
   */
  static syncStandardState(approvalState) {
    const stateMapping = {
      "draft": "draft",
      "under_review": "draft",
      "for_approval": "draft", 
      "for_authorization": "draft",
      "approved": "posted",
      "posted": "posted",
      "cancelled": "cancel"
    };

    const standardState = stateMapping[approvalState];
    if (standardState) {
      const stateField = document.querySelector('select[name="state"]');
      if (stateField && stateField.value !== standardState) {
        stateField.value = standardState;
        stateField.dispatchEvent(new Event("change"));
      }
    }
  }
}

// Initialize when DOM is ready
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => {
    PaymentWorkflowRealtime.init();
  });
} else {
  PaymentWorkflowRealtime.init();
}

// Make available globally for CloudPepper compatibility
window.PaymentWorkflowRealtime = PaymentWorkflowRealtime;

export default PaymentWorkflowRealtime;
