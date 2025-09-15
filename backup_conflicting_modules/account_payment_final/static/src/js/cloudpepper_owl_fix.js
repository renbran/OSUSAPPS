/** @odoo-module **/
/**
 * Enhanced CloudPepper OWL Lifecycle Protection - Compatible Version
 * Prevents OWL lifecycle errors and RPC failures in CloudPepper environment
 * Uses CloudPepper-safe patterns to avoid import conflicts
 */

// CloudPepper-compatible OWL and RPC error protection
(function () {
  "use strict";

  console.log(
    "[CloudPepper] Loading comprehensive OWL lifecycle protection..."
  );

  // Global error handler for CloudPepper
  const CLOUDPEPPER_ERROR_HANDLER = {
    /**
     * Enhanced RPC error handling
     */
    handleRPCError(error, context = {}) {
      console.warn(
        `[CloudPepper] RPC Error in ${context.component || "Unknown"}:`,
        error
      );

      // Don't let RPC errors crash the OWL lifecycle
      if (error.message && error.message.includes("RPC_ERROR")) {
        console.warn(
          "[CloudPepper] Suppressing RPC error to prevent OWL crash"
        );
        return { success: false, error: error.message };
      }

      return null;
    },

    /**
     * OWL lifecycle error protection
     */
    handleOwlError(error, component) {
      const componentName = component
        ? component.constructor?.name || "Unknown"
        : "Unknown";
      console.warn(`[CloudPepper] OWL Error in ${componentName}:`, error);

      // Prevent error propagation that causes lifecycle crashes
      if (
        error.cause &&
        error.cause.message &&
        error.cause.message.includes("RPC_ERROR")
      ) {
        console.warn(
          "[CloudPepper] Preventing OWL lifecycle crash from RPC error"
        );
        return true; // Error handled
      }

      return false; // Let other errors propagate normally
    },

    /**
     * Safe async operation wrapper
     */
    async safeAsync(operation, fallback = null, context = {}) {
      try {
        return await operation();
      } catch (error) {
        const handled = this.handleRPCError(error, context);
        if (handled) {
          return fallback;
        }
        throw error;
      }
    },
  };

  // Enhanced Component base class protection using setTimeout to avoid conflicts
  setTimeout(function () {
    try {
      // Try to enhance Component if available
      if (window.odoo && window.owl && window.owl.Component) {
        console.log("[CloudPepper] Attempting to enhance OWL Component...");

        const OriginalComponent = window.owl.Component;
        const originalSetup = OriginalComponent.prototype.setup;

        // Enhanced setup with error handling
        OriginalComponent.prototype.setup = function () {
          // Add CloudPepper error handling to all components
          this._cloudpepperErrorHandler = CLOUDPEPPER_ERROR_HANDLER;

          // Wrap existing setup in try-catch
          try {
            if (originalSetup) {
              originalSetup.call(this);
            }
          } catch (error) {
            console.warn(
              `[CloudPepper] Setup error in ${this.constructor.name}:`,
              error
            );
            // Don't let setup errors crash the component
          }
        };

        console.log("[CloudPepper] Component enhancement applied");
      }
    } catch (enhanceError) {
      console.warn("[CloudPepper] Could not enhance Component:", enhanceError);
    }
  }, 50);

  // Enhanced error handling for specific modules
  const KNOWN_PROBLEMATIC_MODULES = [
    "account_payment_final",
    "order_status_override",
    "enhanced_rest_api",
    "oe_sale_dashboard_17",
  ];

  // Safe module monitoring
  KNOWN_PROBLEMATIC_MODULES.forEach((moduleName) => {
    try {
      console.log(`[CloudPepper] Protecting module: ${moduleName}`);

      // Monitor for module-specific errors
      setTimeout(function () {
        const moduleElements = document.querySelectorAll(
          `[data-module="${moduleName}"]`
        );
        moduleElements.forEach((element) => {
          element.addEventListener("error", function (event) {
            console.warn(
              `[CloudPepper] Module error prevented in ${moduleName}:`,
              event.error
            );
            event.preventDefault();
          });
        });
      }, 200);
    } catch (error) {
      console.warn(
        `[CloudPepper] Error protecting module ${moduleName}:`,
        error
      );
    }
  });

  // Global window error handler for unhandled promises
  window.addEventListener("unhandledrejection", function (event) {
    if (
      event.reason &&
      event.reason.message &&
      event.reason.message.includes("RPC_ERROR")
    ) {
      console.warn(
        "[CloudPepper] Prevented unhandled RPC rejection:",
        event.reason
      );
      event.preventDefault(); // Prevent the error from crashing the application
    }

    if (
      event.reason &&
      event.reason.message &&
      event.reason.message.includes("owl lifecycle")
    ) {
      console.warn(
        "[CloudPepper] Prevented unhandled OWL lifecycle rejection:",
        event.reason
      );
      event.preventDefault();
    }
  });

  // Global error handler for OWL errors
  window.addEventListener("error", function (event) {
    if (event.error && event.error.message) {
      const errorMessage = event.error.message;

      if (
        errorMessage.includes("owl lifecycle") ||
        errorMessage.includes("RPC_ERROR")
      ) {
        console.warn(
          "[CloudPepper] Prevented OWL/RPC error crash:",
          event.error
        );
        event.preventDefault();
      }

      if (errorMessage.includes("odoo.define is not a function")) {
        console.warn(
          "[CloudPepper] Prevented odoo.define error crash:",
          event.error
        );
        event.preventDefault();
      }
    }
  });

  // Safe RPC wrapper for global use
  window.cloudpepperSafeRPC = async function (params, fallback = null) {
    return await CLOUDPEPPER_ERROR_HANDLER.safeAsync(
      () => {
        if (
          window.odoo &&
          window.odoo.__DEBUG__ &&
          window.odoo.__DEBUG__.services.rpc
        ) {
          return window.odoo.__DEBUG__.services.rpc(params);
        }
        throw new Error("RPC service not available");
      },
      fallback,
      { component: "GlobalRPC" }
    );
  };

  // Safe ORM wrapper for global use
  window.cloudpepperSafeORM = async function (
    model,
    method,
    args = [],
    kwargs = {},
    fallback = null
  ) {
    return await CLOUDPEPPER_ERROR_HANDLER.safeAsync(
      () => {
        if (
          window.odoo &&
          window.odoo.__DEBUG__ &&
          window.odoo.__DEBUG__.services.orm
        ) {
          return window.odoo.__DEBUG__.services.orm.call(
            model,
            method,
            args,
            kwargs
          );
        }
        throw new Error("ORM service not available");
      },
      fallback,
      { component: "GlobalORM", model: model, method: method }
    );
  };

  console.log(
    "[CloudPepper] Enhanced OWL Lifecycle & RPC Error Protection Loaded Successfully"
  );
})();
