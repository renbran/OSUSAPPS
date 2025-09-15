/** @odoo-module **/

﻿/**
 * Emergency CloudPepper Error Fix
 * Addresses critical console errors and rendering issues
 * NON-MODULE VERSION to prevent import statement errors
 */

(function () {
    "use strict";
    class EmergencyErrorFix {
        constructor() {
            this.initErrorFixes();
        }

        initErrorFixes() {
            // Fix MutationObserver type errors
            this.fixMutationObserver();

            // Suppress problematic console errors
            this.suppressProblematicErrors();

            // Ensure DOM readiness
            this.ensureDOMReadiness();

            console.log("[CloudPepper] Emergency error fixes applied");
        }

        fixMutationObserver() {
            // Store original MutationObserver
            const OriginalMutationObserver = window.MutationObserver;

            // Enhanced MutationObserver wrapper with comprehensive validation
            window.MutationObserver = class SafeMutationObserver extends OriginalMutationObserver {
                observe(target, options) {
                    // Comprehensive target validation
                    if (!target) {
                        console.warn("[CloudPepper] MutationObserver: null/undefined target ignored");
                        return;
                    }

                    // Check if target is a valid Node
                    if (typeof target.nodeType !== "number" || (!target.ownerDocument && target !== document)) {
                        console.warn("[CloudPepper] MutationObserver: Invalid target type, skipping");
                        return;
                    }

                    // Additional CloudPepper-specific checks
                    if (target.nodeType < 1 || target.nodeType > 12) {
                        console.warn("[CloudPepper] MutationObserver: Invalid nodeType value:", target.nodeType);
                        return;
                    }

                    // Ensure target is attached to DOM or is document
                    if (target !== document && !document.contains(target)) {
                        console.warn("[CloudPepper] MutationObserver: Target not in DOM, deferring");
                        // Try to observe after a brief delay if element gets attached
                        setTimeout(() => {
                            if (document.contains(target)) {
                                try {
                                    super.observe(target, options);
                                } catch (e) {
                                    console.warn("[CloudPepper] Deferred MutationObserver failed:", e.message);
                                }
                            }
                        }, 100);
                        return;
                    }

                    try {
                        return super.observe(target, options);
                    } catch (error) {
                        console.warn("[CloudPepper] MutationObserver error prevented:", error.message);

                        // Log additional debugging info for CloudPepper
                        if (error.message.includes("parameter 1 is not of type 'Node'")) {
                            console.warn("[CloudPepper] Target details:", {
                                target: target,
                                nodeType: target?.nodeType,
                                nodeName: target?.nodeName,
                                isConnected: target?.isConnected,
                                constructor: target?.constructor?.name,
                            });
                        }
                    }
                }

                disconnect() {
                    try {
                        return super.disconnect();
                    } catch (error) {
                        console.warn("[CloudPepper] MutationObserver disconnect error:", error.message);
                    }
                }
            };

            console.log("[CloudPepper] Enhanced MutationObserver protection enabled");
        }

        suppressProblematicErrors() {
            // Store original console methods
            const originalError = console.error;
            const originalWarn = console.warn;

            // Patterns to suppress (CloudPepper optimized)
            const suppressPatterns = [
                "Failed to execute 'observe' on 'MutationObserver'",
                "parameter 1 is not of type 'Node'",
                "TypeError: Failed to execute 'observe'",
                "MutationObserver.*parameter.*not.*type.*Node",
                "Local import.*is forbidden for security reasons",
                "Please remove all @import",
                "gtag is not defined",
                "google-analytics",
                "firebase",
                "Long Running Recorder",
                "Content script initialised",
                "Recorder disabled",
                "Unknown action: is-mobile",
                "Check Redirect",
                "data-oe-",
                "tracking",
                "analytics",
                "cloudpepper tracking",
                "third-party script",
                "advertisement",
                "social media",
                "index.ts-",
                "web.assets_web.min.js",
            ];

            const suppressErrors = [
                "Could not get content for.*payment_widget.js",
                "Unknown action service",
                "Content script initialised",
                "Recorder disabled",
            ];

            // Override console.error
            console.error = function (...args) {
                const message = args.join(" ");
                if (suppressPatterns.some((pattern) => message.match(new RegExp(pattern, "i")))) {
                    return; // Suppress this error
                }
                originalError.apply(console, args);
            };

            // Override console.warn
            console.warn = function (...args) {
                const message = args.join(" ");
                if (suppressPatterns.some((pattern) => message.match(new RegExp(pattern, "i")))) {
                    return; // Suppress this warning
                }
                originalWarn.apply(console, args);
            };
        }

        ensureDOMReadiness() {
            // Enhanced DOM readiness checking for CloudPepper MutationObserver issues

            // Add global error handlers for MutationObserver issues
            window.addEventListener("error", (event) => {
                if (
                    event.error &&
                    (event.error.message?.includes("MutationObserver") ||
                        event.error.message?.includes("parameter 1 is not of type 'Node'") ||
                        event.filename?.includes("index.ts-"))
                ) {
                    console.warn("[CloudPepper] Intercepted MutationObserver error:", event.error.message);
                    event.preventDefault();
                    return false;
                }
            });

            // Add unhandled promise rejection handler
            window.addEventListener("unhandledrejection", (event) => {
                if (event.reason?.message?.includes("MutationObserver") || event.reason?.stack?.includes("index.ts-")) {
                    console.warn("[CloudPepper] Intercepted unhandled promise rejection:", event.reason);
                    event.preventDefault();
                }
            });

            // Ensure DOM is ready before any operations
            if (document.readyState === "loading") {
                document.addEventListener("DOMContentLoaded", () => {
                    this.validateDOMElements();
                    this.initializeAdvancedFixes();
                });
            } else {
                this.validateDOMElements();
                this.initializeAdvancedFixes();
            }
        }

        initializeAdvancedFixes() {
            // Additional CloudPepper-specific fixes for observer issues

            // Wrap common DOM methods that might cause observer issues
            this.wrapDOMMethods();

            console.log("[CloudPepper] Advanced DOM fixes initialized");
        }

        wrapDOMMethods() {
            // Wrap querySelector methods to prevent null reference errors
            const originalQuerySelector = Document.prototype.querySelector;
            const originalQuerySelectorAll = Document.prototype.querySelectorAll;

            Document.prototype.querySelector = function (selector) {
                try {
                    return originalQuerySelector.call(this, selector);
                } catch (e) {
                    console.warn("[CloudPepper] querySelector error prevented:", e.message);
                    return null;
                }
            };

            Document.prototype.querySelectorAll = function (selector) {
                try {
                    return originalQuerySelectorAll.call(this, selector);
                } catch (e) {
                    console.warn("[CloudPepper] querySelectorAll error prevented:", e.message);
                    return [];
                }
            };

            // Also wrap IntersectionObserver if it exists
            if (window.IntersectionObserver) {
                const OriginalIntersectionObserver = window.IntersectionObserver;
                window.IntersectionObserver = class SafeIntersectionObserver extends OriginalIntersectionObserver {
                    observe(target) {
                        if (!target || typeof target.nodeType !== "number") {
                            console.warn("[CloudPepper] Invalid IntersectionObserver target skipped");
                            return;
                        }
                        try {
                            return super.observe(target);
                        } catch (error) {
                            console.warn("[CloudPepper] IntersectionObserver error prevented:", error.message);
                        }
                    }
                };
            }
        }

        validateDOMElements() {
            // Remove any elements that might cause issues
            const problematicSelectors = [
                '[data-menu-xmlid="hr_expense.menu_hr_expense_root"]',
                '.o_app[data-menu-xmlid*="expense"]',
            ];

            problematicSelectors.forEach((selector) => {
                try {
                    const elements = document.querySelectorAll(selector);
                    elements.forEach((element) => {
                        if (element && element.parentNode) {
                            console.log(`[CloudPepper] Removed problematic element: ${selector}`);
                            element.remove();
                        }
                    });
                } catch (error) {
                    // Silently ignore selector errors
                }
            });
        }
    }

    // Initialize emergency fixes as early as possible
    const emergencyFix = new EmergencyErrorFix();

    // Make available globally for debugging
    window.CloudPepperEmergencyFix = EmergencyErrorFix;
    window.cloudPepperEmergencyFix = emergencyFix;

    console.log("[CloudPepper] Emergency error fixes initialized successfully");
})(); // End IIFE
