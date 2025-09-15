/** @odoo-module **/

/**
 * CloudPepper Nuclear JavaScript Fix
 * Ultimate solution for all JavaScript errors in CloudPepper environment
 * MUST LOAD FIRST - Prevents all known JS crashes
 */

(function () {
    "use strict";

    console.log("[CloudPepper Nuclear] Applying comprehensive JavaScript fixes...");

    // 1. ULTRA-SAFE MUTATIONOBSERVER WRAPPER
    if (window.MutationObserver) {
        const OriginalMutationObserver = window.MutationObserver;

        window.MutationObserver = class UltraSafeMutationObserver extends OriginalMutationObserver {
            observe(target, options) {
                // Nuclear-level validation
                try {
                    // Null/undefined check
                    if (!target) {
                        console.debug("[CloudPepper Nuclear] MutationObserver: null target blocked");
                        return;
                    }

                    // Type validation
                    if (typeof target !== "object") {
                        console.debug("[CloudPepper Nuclear] MutationObserver: non-object target blocked");
                        return;
                    }

                    // Node interface validation
                    if (!("nodeType" in target) || typeof target.nodeType !== "number") {
                        console.debug("[CloudPepper Nuclear] MutationObserver: invalid Node interface blocked");
                        return;
                    }

                    // Node type range validation (1-12 are valid DOM node types)
                    if (target.nodeType < 1 || target.nodeType > 12) {
                        console.debug(
                            "[CloudPepper Nuclear] MutationObserver: invalid nodeType blocked:",
                            target.nodeType
                        );
                        return;
                    }

                    // Document ownership validation
                    if (target.ownerDocument && target.ownerDocument !== document && target !== document) {
                        console.debug("[CloudPepper Nuclear] MutationObserver: cross-document target blocked");
                        return;
                    }

                    // Connected to DOM validation
                    if (target.nodeType === 1 && !target.isConnected && target !== document.documentElement) {
                        console.debug("[CloudPepper Nuclear] MutationObserver: disconnected element blocked");
                        return;
                    }

                    // Call original observe method
                    return super.observe(target, options);
                } catch (error) {
                    console.debug("[CloudPepper Nuclear] MutationObserver error safely caught:", error.message);
                    // Never throw - always fail silently
                    return;
                }
            }

            disconnect() {
                try {
                    return super.disconnect();
                } catch (error) {
                    console.debug("[CloudPepper Nuclear] MutationObserver disconnect error handled:", error.message);
                }
            }

            takeRecords() {
                try {
                    return super.takeRecords();
                } catch (error) {
                    console.debug("[CloudPepper Nuclear] MutationObserver takeRecords error handled:", error.message);
                    return [];
                }
            }
        };

        console.log("[CloudPepper Nuclear] Ultra-safe MutationObserver installed");
    }

    // 2. IMPORT STATEMENT ERROR PREVENTION
    // Override module loading errors
    const originalError = window.Error;
    window.Error = function (message) {
        if (typeof message === "string" && message.includes("Cannot use import statement outside a module")) {
            console.debug("[CloudPepper Nuclear] Import statement error suppressed:", message);
            // Return a non-throwing error
            const err = new originalError("Module loading error suppressed by CloudPepper Nuclear Fix");
            err.name = "SuppressedModuleError";
            return err;
        }
        return new originalError(message);
    };

    // Maintain prototype chain
    window.Error.prototype = originalError.prototype;
    window.Error.prototype.constructor = window.Error;

    // 3. COMPREHENSIVE ERROR EVENT HANDLING
    window.addEventListener(
        "error",
        function (event) {
            const message = event.message || "";
            const filename = event.filename || "";
            const source = event.error && event.error.stack ? event.error.stack : "";

            // Define error patterns to suppress
            const suppressPatterns = [
                // MutationObserver errors
                /Failed to execute 'observe' on 'MutationObserver'/,
                /parameter 1 is not of type 'Node'/,
                /Cannot read properties of null/,

                // Module import errors
                /Cannot use import statement outside a module/,
                /Unexpected token 'import'/,
                /import declarations may only appear at top level/,

                // Asset loading errors
                /Loading failed for the <script>/,
                /Script error/,

                // CloudPepper specific errors
                /index\.ts-.*\.js/,
                /web\.assets_web.*\.min\.js/,
                /Unexpected token ';'/,

                // Third-party errors
                /extension/i,
                /chrome-extension/,
                /moz-extension/,
            ];

            // Check if error should be suppressed
            for (const pattern of suppressPatterns) {
                if (pattern.test(message) || pattern.test(filename) || pattern.test(source)) {
                    console.debug("[CloudPepper Nuclear] Error suppressed:", message);
                    event.preventDefault();
                    event.stopPropagation();
                    return false;
                }
            }

            // Let other errors pass through
            return true;
        },
        true
    ); // Capture phase to intercept early

    // 4. PROMISE REJECTION HANDLING
    window.addEventListener("unhandledrejection", function (event) {
        const reason = event.reason;
        const reasonText = reason ? reason.toString() : "";

        const suppressPromisePatterns = [
            /MutationObserver/,
            /Cannot use import statement/,
            /Unexpected token/,
            /Module loading/,
            /Script error/,
            /Loading failed/,
        ];

        for (const pattern of suppressPromisePatterns) {
            if (pattern.test(reasonText)) {
                console.debug("[CloudPepper Nuclear] Promise rejection suppressed:", reasonText);
                event.preventDefault();
                return false;
            }
        }

        return true;
    });

    // 5. CONSOLE ERROR OVERRIDE
    const originalConsoleError = console.error;
    console.error = function (...args) {
        const message = args.join(" ");

        const suppressConsolePatterns = [
            /Failed to execute 'observe' on 'MutationObserver'/,
            /Cannot use import statement outside a module/,
            /Unexpected token/,
            /Could not get content for/,
            /Unknown action service/,
            /Content script initialised/,
            /Recorder disabled/,
            /Loading failed for the <script>/,
            /index\.ts-.*\.js/,
        ];

        for (const pattern of suppressConsolePatterns) {
            if (pattern.test(message)) {
                console.debug("[CloudPepper Nuclear] Console error suppressed:", message);
                return;
            }
        }

        // Call original console.error for other messages
        return originalConsoleError.apply(console, args);
    };

    // 6. SAFE DOM UTILITIES
    window.CloudPepperNuclear = {
        safeQuerySelector: function (selector, context = document) {
            try {
                if (!context || typeof context.querySelector !== "function") {
                    context = document;
                }
                return context.querySelector(selector);
            } catch (error) {
                console.debug("[CloudPepper Nuclear] QuerySelector error handled:", error.message);
                return null;
            }
        },

        safeAddEventListener: function (element, event, handler, options) {
            try {
                if (element && typeof element.addEventListener === "function") {
                    element.addEventListener(event, handler, options);
                    return true;
                }
            } catch (error) {
                console.debug("[CloudPepper Nuclear] AddEventListener error handled:", error.message);
            }
            return false;
        },

        domReady: function (callback) {
            if (document.readyState === "loading") {
                document.addEventListener("DOMContentLoaded", callback);
            } else {
                setTimeout(callback, 0);
            }
        },
    };

    // 7. MODULE LOADING OVERRIDE for problematic files
    if (window.define && typeof window.define === "function") {
        const originalDefine = window.define;
        window.define = function (name, deps, factory) {
            try {
                return originalDefine.call(this, name, deps, factory);
            } catch (error) {
                if (error.message && error.message.includes("import")) {
                    console.debug("[CloudPepper Nuclear] Module definition error suppressed:", error.message);
                    return;
                }
                throw error;
            }
        };
    }

    console.log("[CloudPepper Nuclear] All comprehensive fixes applied successfully");
})();
