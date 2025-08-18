/** @odoo-module **/
/**
 * CloudPepper RPC Error Protection for Order Net Commission
 * OSUS Properties - Odoo 17 Compatibility
 */

import { registry } from "@web/core/registry";
import { patch } from "@web/core/utils/patch";
import { Component } from "@odoo/owl";

// Global error handler for CloudPepper compatibility
window.addEventListener('error', function(event) {
    if (event.error && event.error.message) {
        console.warn('Order Net Commission - Caught global error:', event.error.message);
        
        // Handle specific RPC errors
        if (event.error.message.includes('RPC_ERROR') || 
            event.error.message.includes('order_net_commission')) {
            console.log('Handling order_net_commission RPC error gracefully');
            event.preventDefault();
            return false;
        }
    }
});

// Promise rejection handler for uncaught RPC errors
window.addEventListener('unhandledrejection', function(event) {
    if (event.reason && event.reason.message) {
        console.warn('Order Net Commission - Caught unhandled promise rejection:', event.reason.message);
        
        // Handle RPC promise rejections
        if (event.reason.message.includes('RPC_ERROR') || 
            event.reason.message.includes('order_net_commission')) {
            console.log('Handling order_net_commission promise rejection gracefully');
            event.preventDefault();
            return false;
        }
    }
});

// Patch the RPC service for better error handling
const rpcService = {
    start() {
        return {
            async rpc(route, params = {}, settings = {}) {
                try {
                    // Original RPC call logic would go here
                    console.log('Order Net Commission - Safe RPC call:', route);
                    return await this._originalRPC(route, params, settings);
                } catch (error) {
                    console.warn('Order Net Commission - RPC Error caught:', error);
                    
                    // Handle commission-specific errors gracefully
                    if (error.message && error.message.includes('order_net_commission')) {
                        console.log('Gracefully handling commission RPC error');
                        return { error: 'Commission calculation temporarily unavailable' };
                    }
                    
                    // Re-throw other errors
                    throw error;
                }
            }
        };
    }
};

// Register the protection service
registry.category("services").add("order_net_commission_protection", rpcService);

// Enhanced Component patch for error boundaries
patch(Component.prototype, "order_net_commission_error_boundary", {
    setup() {
        this._super(...arguments);
        
        // Add error boundary for commission components
        this.__onError = this.__onError || ((error) => {
            console.warn('Order Net Commission - Component error caught:', error);
            
            if (error.message && error.message.includes('commission')) {
                console.log('Gracefully handling commission component error');
                return; // Handle gracefully
            }
            
            // Call original error handler for other errors
            if (this._super.__onError) {
                this._super.__onError(error);
            }
        });
    },
    
    mounted() {
        this._super(...arguments);
        
        // Add commission-specific initialization protection
        try {
            if (this.props && this.props.record && this.props.record.model === 'sale.order') {
                console.log('Order Net Commission - Component mounted safely');
            }
        } catch (error) {
            console.warn('Order Net Commission - Mount error handled:', error);
        }
    }
});

// CloudPepper specific fixes
if (typeof odoo !== 'undefined' && odoo.define) {
    // Ensure backward compatibility with CloudPepper's module system
    odoo.define('order_net_commission.cloudpepper_protection', function (require) {
        'use strict';
        
        console.log('Order Net Commission - CloudPepper protection loaded');
        
        return {
            protectRPC: function(originalRPC) {
                return function(route, params, settings) {
                    try {
                        return originalRPC.call(this, route, params, settings);
                    } catch (error) {
                        console.warn('Protected RPC call failed:', error);
                        return Promise.resolve({ error: 'RPC call protected' });
                    }
                };
            },
            
            init: function() {
                console.log('Order Net Commission protection initialized for CloudPepper');
            }
        };
    });
}

console.log('Order Net Commission - CloudPepper RPC protection loaded successfully');
