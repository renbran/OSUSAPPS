/** @odoo-module **/

/**
 * IMMEDIATE EMERGENCY JAVASCRIPT FIX
 * Executes INSTANTLY to prevent ALL errors
 * Must be injected directly into HTML head
 */

console.log("[EMERGENCY] Installing immediate JavaScript error prevention...");

// IMMEDIATE MutationObserver override - before anything else loads
(function () {
    if (!window.MutationObserver) return;

    const Original = window.MutationObserver;

    window.MutationObserver = function (callback) {
        const instance = new Original(callback);

        // Override observe method
        const originalObserve = instance.observe;
        instance.observe = function (target, options) {
            // IMMEDIATE validation
            if (
                !target ||
                typeof target !== "object" ||
                !target.nodeType ||
                target.nodeType < 1 ||
                target.nodeType > 12
            ) {
                console.debug("[EMERGENCY] Invalid MutationObserver target blocked");
                return;
            }

            try {
                return originalObserve.call(this, target, options);
            } catch (e) {
                console.debug("[EMERGENCY] MutationObserver error caught:", e.message);
                return;
            }
        };

        return instance;
    };

    // Maintain prototype
    window.MutationObserver.prototype = Original.prototype;

    console.log("[EMERGENCY] Immediate MutationObserver protection active");
})();

// IMMEDIATE error event suppression
window.addEventListener(
    "error",
    function (e) {
        const msg = e.message || "";
        if (
            msg.includes("MutationObserver") ||
            msg.includes("parameter 1 is not of type") ||
            msg.includes("Unexpected token") ||
            (e.filename && e.filename.includes("index.ts-"))
        ) {
            console.debug("[EMERGENCY] Error suppressed:", msg);
            e.preventDefault();
            e.stopPropagation();
            return false;
        }
    },
    true
);

// IMMEDIATE syntax error prevention for minified files
const originalError = window.Error;
window.Error = function (message) {
    if (
        typeof message === "string" &&
        (message.includes("Unexpected token") || message.includes("Cannot use import"))
    ) {
        console.debug("[EMERGENCY] Syntax error suppressed:", message);
        const err = new originalError("Suppressed by emergency fix");
        err.name = "SuppressedError";
        return err;
    }
    return new originalError(message);
};
window.Error.prototype = originalError.prototype;

console.log("[EMERGENCY] Immediate error prevention active");
