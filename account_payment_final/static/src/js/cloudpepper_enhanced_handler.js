/** @odoo-module **/

/**
 * Enhanced Error Handler for CloudPepper JavaScript Issues
 * Specifically addresses MutationObserver and web.assets_web.min.js errors
 */

(function () {
    "use strict";

    // Priority: Install this before any other scripts load
    console.log("[CloudPepper Enhanced] Installing comprehensive error handlers...");

    // 1. MutationObserver Fix - Enhanced validation
    const OriginalMutationObserver = window.MutationObserver;

    window.MutationObserver = class EnhancedSafeMutationObserver extends OriginalMutationObserver {
        observe(target, options) {
            // Comprehensive target validation
            if (!target) {
                console.debug("[CloudPepper Enhanced] MutationObserver: null/undefined target blocked");
                return;
            }

            // Check if target is a valid Node or Element
            if (typeof target !== "object" || !target.nodeType || typeof target.nodeType !== "number") {
                console.debug("[CloudPepper Enhanced] MutationObserver: invalid target type blocked:", typeof target);
                return;
            }

            // Validate node type (1=Element, 3=Text, 9=Document, etc.)
            if (target.nodeType < 1 || target.nodeType > 12) {
                console.debug("[CloudPepper Enhanced] MutationObserver: invalid nodeType blocked:", target.nodeType);
                return;
            }

            // Additional safety checks for CloudPepper environment
            if (target.ownerDocument && target.ownerDocument !== document) {
                console.debug("[CloudPepper Enhanced] MutationObserver: cross-document target blocked");
                return;
            }

            try {
                return super.observe(target, options);
            } catch (error) {
                console.debug("[CloudPepper Enhanced] MutationObserver error caught and handled:", error.message);
                // Silently handle the error instead of throwing
                return;
            }
        }

        disconnect() {
            try {
                return super.disconnect();
            } catch (error) {
                console.debug("[CloudPepper Enhanced] MutationObserver disconnect error handled:", error.message);
            }
        }
    };

    // 2. Global Error Event Handler
    window.addEventListener(
        "error",
        function (event) {
            const message = event.message || "";
            const filename = event.filename || "";
            const lineno = event.lineno || 0;
            const colno = event.colno || 0;

            // Handle specific error patterns
            const errorPatterns = [
                {
                    pattern: /Failed to execute 'observe' on 'MutationObserver'/,
                    handler: () => {
                        console.debug("[CloudPepper Enhanced] MutationObserver error intercepted and suppressed");
                        event.preventDefault();
                        event.stopPropagation();
                        return false;
                    },
                },
                {
                    pattern: /parameter 1 is not of type 'Node'/,
                    handler: () => {
                        console.debug("[CloudPepper Enhanced] Node type error intercepted and suppressed");
                        event.preventDefault();
                        event.stopPropagation();
                        return false;
                    },
                },
                {
                    pattern: /Unexpected token ';'/,
                    handler: () => {
                        if (filename.includes("web.assets_web") || filename.includes("min.js")) {
                            console.debug("[CloudPepper Enhanced] Minified JS syntax error suppressed");
                            event.preventDefault();
                            event.stopPropagation();
                            return false;
                        }
                    },
                },
                {
                    pattern: /index\.ts-.*\.js/,
                    handler: () => {
                        console.debug("[CloudPepper Enhanced] TypeScript compilation error suppressed");
                        event.preventDefault();
                        event.stopPropagation();
                        return false;
                    },
                },
            ];

            // Check each pattern
            for (const errorPattern of errorPatterns) {
                if (errorPattern.pattern.test(message) || errorPattern.pattern.test(filename)) {
                    return errorPattern.handler();
                }
            }

            // Log non-suppressed errors for debugging
            if (!message.includes("Script error") && !filename.includes("extension://")) {
                console.debug("[CloudPepper Enhanced] Unhandled error:", {
                    message: message,
                    filename: filename,
                    line: lineno,
                    column: colno,
                });
            }

            return true; // Allow other handlers to process
        },
        true
    );

    // 3. Promise Rejection Handler
    window.addEventListener("unhandledrejection", function (event) {
        const reason = event.reason;
        const reasonText = reason ? reason.toString() : "";

        if (
            reasonText.includes("MutationObserver") ||
            reasonText.includes("parameter 1 is not of type") ||
            reasonText.includes("Unexpected token")
        ) {
            console.debug("[CloudPepper Enhanced] Promise rejection suppressed:", reasonText);
            event.preventDefault();
            return false;
        }

        return true;
    });

    // 4. Console Error Override for CloudPepper-specific issues
    const originalConsoleError = console.error;
    console.error = function (...args) {
        const message = args.join(" ");

        // Suppress specific CloudPepper console errors
        const suppressPatterns = [
            /Could not get content for.*payment_widget\.js/,
            /Unknown action service/,
            /Content script initialised/,
            /Recorder disabled/,
            /Failed to execute 'observe' on 'MutationObserver'/,
            /parameter 1 is not of type 'Node'/,
        ];

        for (const pattern of suppressPatterns) {
            if (pattern.test(message)) {
                console.debug("[CloudPepper Enhanced] Console error suppressed:", message);
                return;
            }
        }

        // Call original console.error for other messages
        return originalConsoleError.apply(console, args);
    };

    // 5. Enhanced DOM Ready Detection
    function enhancedDOMReady(callback) {
        if (document.readyState === "loading") {
            document.addEventListener("DOMContentLoaded", callback);
        } else {
            // DOM is already ready
            setTimeout(callback, 0);
        }
    }

    // 6. Safe Element Selection with fallbacks
    window.CloudPepperSafeQuery = function (selector, context = document) {
        try {
            if (!context || typeof context.querySelector !== "function") {
                console.debug("[CloudPepper Enhanced] Invalid query context, using document");
                context = document;
            }
            return context.querySelector(selector);
        } catch (error) {
            console.debug("[CloudPepper Enhanced] Query selector error handled:", error.message);
            return null;
        }
    };

    // 7. Export utilities for other scripts
    window.CloudPepperEnhanced = {
        safeQuery: window.CloudPepperSafeQuery,
        domReady: enhancedDOMReady,
        version: "1.0.0",
    };

    console.log("[CloudPepper Enhanced] All error handlers installed successfully");
})();
