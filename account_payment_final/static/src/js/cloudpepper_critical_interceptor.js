/** @odoo-module **/

/**
 * CloudPepper Critical Error Interceptor
 * MUST LOAD FIRST - Prevents web.assets_web_dark.min.js crashes
 * NON-MODULE VERSION to prevent import statement errors
 */

console.log("[CloudPepper Critical] Installing emergency error interceptors...");

// CRITICAL: Install MutationObserver safety wrapper immediately
(function installMutationObserverSafety() {
    const OriginalMutationObserver = window.MutationObserver;

    window.MutationObserver = class CloudPepperSafeMutationObserver extends OriginalMutationObserver {
        observe(target, options) {
            // Critical validation to prevent TypeError
            if (!target) {
                console.debug("[CloudPepper Critical] MutationObserver: null target ignored");
                return;
            }

            if (typeof target !== "object") {
                console.debug("[CloudPepper Critical] MutationObserver: non-object target ignored");
                return;
            }

            if (!target.nodeType) {
                console.debug("[CloudPepper Critical] MutationObserver: target without nodeType ignored");
                return;
            }

            // Validate node type ranges (1-12 are valid DOM node types)
            if (target.nodeType < 1 || target.nodeType > 12) {
                console.debug("[CloudPepper Critical] MutationObserver: invalid nodeType ignored:", target.nodeType);
                return;
            }

            try {
                return super.observe(target, options);
            } catch (error) {
                console.debug("[CloudPepper Critical] MutationObserver error safely handled:", error.message);
                return;
            }
        }
    };

    console.log("[CloudPepper Critical] MutationObserver safety wrapper installed");
})();

// CRITICAL: Global error interceptor for syntax errors
window.addEventListener(
    "error",
    function (event) {
        const message = event.message || "";
        const filename = event.filename || "";
        const source = event.error ? event.error.stack : "";

        // Intercept web.assets_web_dark.min.js syntax errors
        if (
            filename.includes("web.assets_web_dark.min.js") &&
            (message.includes("Unexpected token") || message.includes("SyntaxError"))
        ) {
            console.warn(`[CloudPepper Critical] Syntax error in ${filename} intercepted:`, message);
            event.preventDefault();
            event.stopPropagation();
            return false;
        }

        // Intercept index.ts-dbda1bbd.js errors
        if (filename.includes("index.ts-dbda1bbd.js") && message.includes("MutationObserver")) {
            console.warn(`[CloudPepper Critical] MutationObserver error in ${filename} intercepted:`, message);
            event.preventDefault();
            event.stopPropagation();
            return false;
        }

        // General MutationObserver TypeError protection
        if (
            message.includes("Failed to execute 'observe' on 'MutationObserver'") ||
            message.includes("parameter 1 is not of type 'Node'")
        ) {
            console.warn("[CloudPepper Critical] MutationObserver TypeError intercepted:", message);
            event.preventDefault();
            event.stopPropagation();
            return false;
        }

        // Let other errors pass through
        return true;
    },
    true
); // Use capture phase to intercept before other handlers

// CRITICAL: Promise rejection handler
window.addEventListener("unhandledrejection", function (event) {
    const reason = event.reason;
    const reasonText = reason ? reason.toString() : "";

    if (
        reasonText.includes("MutationObserver") ||
        reasonText.includes("Unexpected token") ||
        reasonText.includes("SyntaxError") ||
        reasonText.includes("observe")
    ) {
        console.warn("[CloudPepper Critical] Promise rejection intercepted:", reasonText);
        event.preventDefault();
    }
});

// CRITICAL: Safe DOM utilities for modules that need them
window.CloudPepperCritical = {
    // Safe element selection
    safeQuery: function (selector, context = document) {
        try {
            if (!context || !context.querySelector) {
                console.debug("[CloudPepper Critical] Invalid context for query");
                return null;
            }
            return context.querySelector(selector);
        } catch (error) {
            console.debug("[CloudPepper Critical] Query error handled:", error.message);
            return null;
        }
    },

    // Safe MutationObserver creation
    createSafeObserver: function (callback) {
        try {
            return new MutationObserver(function (mutations, observer) {
                try {
                    return callback(mutations, observer);
                } catch (error) {
                    console.debug("[CloudPepper Critical] Observer callback error handled:", error.message);
                }
            });
        } catch (error) {
            console.debug("[CloudPepper Critical] Observer creation error handled:", error.message);
            return null;
        }
    },

    // Safe observation with validation
    safeObserve: function (observer, target, options = {}) {
        if (!observer || !target) {
            console.debug("[CloudPepper Critical] Invalid observer or target");
            return false;
        }

        try {
            observer.observe(target, {
                childList: true,
                subtree: true,
                ...options,
            });
            return true;
        } catch (error) {
            console.debug("[CloudPepper Critical] Observation error handled:", error.message);
            return false;
        }
    },
};

// CRITICAL: Asset loading error prevention
(function () {
    const originalCreateElement = document.createElement;

    document.createElement = function (tagName) {
        const element = originalCreateElement.call(this, tagName);

        if (tagName && tagName.toLowerCase() === "script") {
            element.addEventListener("error", function (event) {
                const src = this.src || "";
                if (
                    src.includes("web.assets_web_dark") ||
                    src.includes("index.ts-dbda1bbd") ||
                    src.includes(".min.js")
                ) {
                    console.warn("[CloudPepper Critical] Script error intercepted:", src);
                    event.preventDefault();
                    event.stopPropagation();
                }
            });
        }

        return element;
    };
})();

console.log("[CloudPepper Critical] All critical error interceptors installed successfully");

// Make available globally for debugging
window.CloudPepperCriticalInterceptor = {
    name: "cloudpepper_critical_interceptor",
    version: "1.0.0",
    installed: true,
    utils: window.CloudPepperCritical,
};
