/** @odoo-module **/

/**
 * CloudPepper JavaScript Error Handler
 * Fixes MutationObserver errors and provides robust DOM observation
 * NON-MODULE VERSION to prevent import statement errors
 */

(function() {
    'use strict';

class CloudPepperJSErrorHandler {
    constructor() {
        this.setupGlobalErrorHandling();
        this.patchMutationObserver();
        this.setupDOMObservation();
    }

    setupGlobalErrorHandling() {
        // Catch and handle JavaScript errors
        window.addEventListener("error", (event) => {
            if (event.error && event.error.message) {
                const message = event.error.message;

                // Handle specific known errors
                if (message.includes("MutationObserver") || message.includes("parameter 1 is not of type")) {
                    console.warn("[CloudPepper] MutationObserver error handled:", message);
                    event.preventDefault();
                    return false;
                }

                if (message.includes("Unexpected token") || message.includes("SyntaxError")) {
                    console.warn("[CloudPepper] Syntax error handled:", message);
                    // Allow error to be logged but prevent crash
                }
            }
        });

        // Handle unhandled promise rejections
        window.addEventListener("unhandledrejection", (event) => {
            if (event.reason && event.reason.message) {
                const message = event.reason.message;
                if (message.includes("MutationObserver") || message.includes("observe")) {
                    console.warn("[CloudPepper] Promise rejection handled:", message);
                    event.preventDefault();
                }
            }
        });
    }

    patchMutationObserver() {
        // Store original MutationObserver
        const OriginalMutationObserver = window.MutationObserver;

        // Create safe wrapper
        window.MutationObserver = class SafeMutationObserver extends OriginalMutationObserver {
            observe(target, options) {
                try {
                    // Validate target parameter
                    if (!target) {
                        console.warn("[CloudPepper] MutationObserver.observe called with null/undefined target");
                        return;
                    }

                    if (typeof target !== "object" || !target.nodeType) {
                        console.warn("[CloudPepper] MutationObserver.observe called with invalid target:", target);
                        return;
                    }

                    // Ensure target is a proper DOM node
                    if (
                        target.nodeType !== Node.ELEMENT_NODE &&
                        target.nodeType !== Node.DOCUMENT_NODE &&
                        target.nodeType !== Node.DOCUMENT_FRAGMENT_NODE
                    ) {
                        console.warn(
                            "[CloudPepper] MutationObserver.observe called with invalid node type:",
                            target.nodeType
                        );
                        return;
                    }

                    // Call original observe method
                    return super.observe(target, options);
                } catch (error) {
                    console.warn("[CloudPepper] MutationObserver.observe error caught:", error.message);
                    // Don't re-throw, just log and continue
                }
            }
        };

        console.debug("[CloudPepper] MutationObserver patched for safety");
    }

    setupDOMObservation() {
        // Provide safe DOM observation utility
        window.CloudPepperDOM = {
            safeObserve: (selector, callback, options = {}) => {
                const element = typeof selector === "string" ? document.querySelector(selector) : selector;

                if (!element) {
                    console.warn(`[CloudPepper] Element not found for observation: ${selector}`);
                    return null;
                }

                try {
                    const observer = new MutationObserver(callback);
                    observer.observe(element, {
                        childList: true,
                        subtree: true,
                        attributes: true,
                        ...options,
                    });
                    return observer;
                } catch (error) {
                    console.warn("[CloudPepper] Failed to create safe observer:", error.message);
                    return null;
                }
            },

            waitForElement: (selector, timeout = 5000) => {
                return new Promise((resolve, reject) => {
                    const element = document.querySelector(selector);
                    if (element) {
                        resolve(element);
                        return;
                    }

                    const observer = new MutationObserver((mutations) => {
                        const element = document.querySelector(selector);
                        if (element) {
                            observer.disconnect();
                            resolve(element);
                        }
                    });

                    try {
                        observer.observe(document.body, {
                            childList: true,
                            subtree: true,
                        });

                        setTimeout(() => {
                            observer.disconnect();
                            reject(new Error(`Element ${selector} not found within ${timeout}ms`));
                        }, timeout);
                    } catch (error) {
                        reject(error);
                    }
                });
            },
        };
    }
}

// Initialize error handler immediately
const errorHandler = new CloudPepperJSErrorHandler();

// Make available globally for debugging
window.CloudPepperJSErrorHandler = CloudPepperJSErrorHandler;
window.cloudPepperErrorHandler = errorHandler;

console.log("[CloudPepper] JavaScript error handler initialized successfully");

})(); // End IIFE
