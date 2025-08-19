/** @odoo-module **/

import { Component, onMounted, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

/**
 * Report Font Enhancement Service
 * Dynamically adjusts font contrast and transparency based on background
 */
export class ReportFontEnhancementService extends Component {
    
    setup() {
        this.rpc = useService("rpc");
        onMounted(this.onMounted);
        onWillUnmount(this.onWillUnmount);
    }

    onMounted() {
        this.initializeEnhancements();
        this.setupEventListeners();
    }

    onWillUnmount() {
        this.removeEventListeners();
    }

    /**
     * Initialize font enhancements for all reports
     */
    async initializeEnhancements() {
        // Add enhancement classes to existing reports
        this.enhanceExistingReports();
        
        // Setup mutation observer for dynamically loaded content
        this.setupMutationObserver();
        
        // Apply adaptive contrast
        this.applyAdaptiveContrast();
        
        console.log('Report Font Enhancement: Initialized');
    }

    /**
     * Enhance existing reports on the page
     */
    enhanceExistingReports() {
        const reportSelectors = [
            '.o_report_layout_standard',
            '.o_report_layout_boxed', 
            '.o_report_layout_clean',
            '.o_content[data-report-margin-top]',
            '.invoice-report',
            '.financial-report'
        ];

        reportSelectors.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(element => {
                this.enhanceReportElement(element);
            });
        });
    }

    /**
     * Enhance a single report element
     */
    enhanceReportElement(element) {
        if (!element || element.classList.contains('font-enhanced')) {
            return;
        }

        // Add enhancement class
        element.classList.add('font-enhanced', 'report-enhanced');
        
        // Calculate and apply optimal contrast
        this.calculateOptimalContrast(element);
        
        // Enhance tables within the report
        this.enhanceTablesInReport(element);
        
        // Apply transparency based on background
        this.applyAdaptiveTransparency(element);
    }

    /**
     * Calculate optimal contrast for text based on background
     */
    calculateOptimalContrast(element) {
        const computedStyle = window.getComputedStyle(element);
        const backgroundColor = computedStyle.backgroundColor;
        
        // Convert background color to luminance
        const luminance = this.calculateLuminance(backgroundColor);
        
        // Set text color based on luminance
        const textColor = luminance > 0.5 ? '#212529' : '#f8f9fa';
        const shadowColor = luminance > 0.5 ? 
            'rgba(255, 255, 255, 0.8)' : 
            'rgba(0, 0, 0, 0.8)';
        
        // Apply calculated colors
        element.style.setProperty('--dynamic-text-color', textColor);
        element.style.setProperty('--dynamic-shadow-color', shadowColor);
        element.style.color = textColor;
        element.style.textShadow = `0 1px 2px ${shadowColor}`;
    }

    /**
     * Calculate luminance from color string
     */
    calculateLuminance(colorStr) {
        // Handle rgb/rgba values
        const rgbMatch = colorStr.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
        if (!rgbMatch) {
            // Default to medium luminance if can't parse
            return 0.5;
        }
        
        const [, r, g, b] = rgbMatch.map(Number);
        
        // Normalize and calculate relative luminance
        const [rNorm, gNorm, bNorm] = [r, g, b].map(val => {
            const normalized = val / 255;
            return normalized <= 0.03928 
                ? normalized / 12.92 
                : Math.pow((normalized + 0.055) / 1.055, 2.4);
        });
        
        return 0.2126 * rNorm + 0.7152 * gNorm + 0.0722 * bNorm;
    }

    /**
     * Enhance tables within reports
     */
    enhanceTablesInReport(reportElement) {
        const tables = reportElement.querySelectorAll('table');
        
        tables.forEach(table => {
            if (table.classList.contains('table-enhanced')) {
                return;
            }
            
            table.classList.add('table-enhanced', 'report-table-enhanced');
            
            // Enhance headers
            const headers = table.querySelectorAll('th');
            headers.forEach(th => {
                th.style.fontWeight = '600';
                th.style.textShadow = '0 1px 2px rgba(0,0,0,0.3)';
            });
            
            // Enhance amount columns
            const amountCells = table.querySelectorAll('.amount, .monetary, .text-right');
            amountCells.forEach(cell => {
                cell.classList.add('report-amount-enhanced');
                cell.style.fontVariantNumeric = 'tabular-nums';
                cell.style.fontWeight = '500';
            });
        });
    }

    /**
     * Apply adaptive transparency based on content and background
     */
    applyAdaptiveTransparency(element) {
        const hasBackgroundImage = window.getComputedStyle(element).backgroundImage !== 'none';
        
        if (hasBackgroundImage) {
            // Increase opacity for better readability over images
            element.style.backgroundColor = 'rgba(255, 255, 255, 0.95)';
        } else {
            // Use lighter transparency for solid backgrounds
            element.style.backgroundColor = 'rgba(255, 255, 255, 0.9)';
        }
    }

    /**
     * Apply adaptive contrast to all report elements
     */
    applyAdaptiveContrast() {
        // Check system preference for dark mode
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        const prefersHighContrast = window.matchMedia('(prefers-contrast: high)').matches;
        
        if (prefersDark) {
            document.documentElement.style.setProperty('--report-text-color', '#f8f9fa');
            document.documentElement.style.setProperty('--report-background-color', '#212529');
        }
        
        if (prefersHighContrast) {
            document.documentElement.style.setProperty('--report-text-color', '#000000');
            document.documentElement.style.setProperty('--report-background-color', '#ffffff');
            document.documentElement.style.setProperty('--report-border-color', '#000000');
        }
    }

    /**
     * Setup mutation observer for dynamic content
     */
    setupMutationObserver() {
        this.observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList') {
                    mutation.addedNodes.forEach((node) => {
                        if (node.nodeType === Node.ELEMENT_NODE) {
                            // Check if new node is a report or contains reports
                            if (this.isReportElement(node)) {
                                this.enhanceReportElement(node);
                            } else {
                                // Check for report elements within the new node
                                const reportElements = node.querySelectorAll?.(
                                    '.o_report_layout_standard, .o_report_layout_boxed, .o_report_layout_clean'
                                );
                                reportElements?.forEach(element => {
                                    this.enhanceReportElement(element);
                                });
                            }
                        }
                    });
                }
            });
        });

        this.observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    /**
     * Check if element is a report element
     */
    isReportElement(element) {
        const reportClasses = [
            'o_report_layout_standard',
            'o_report_layout_boxed', 
            'o_report_layout_clean',
            'invoice-report',
            'financial-report'
        ];
        
        return reportClasses.some(className => element.classList?.contains(className));
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Listen for color scheme changes
        this.colorSchemeQuery = window.matchMedia('(prefers-color-scheme: dark)');
        this.colorSchemeHandler = () => this.applyAdaptiveContrast();
        this.colorSchemeQuery.addEventListener('change', this.colorSchemeHandler);

        // Listen for high contrast changes
        this.contrastQuery = window.matchMedia('(prefers-contrast: high)');
        this.contrastHandler = () => this.applyAdaptiveContrast();
        this.contrastQuery.addEventListener('change', this.contrastHandler);

        // Listen for print events
        this.beforePrintHandler = () => this.preparePrintMode();
        this.afterPrintHandler = () => this.restoreNormalMode();
        window.addEventListener('beforeprint', this.beforePrintHandler);
        window.addEventListener('afterprint', this.afterPrintHandler);
    }

    /**
     * Remove event listeners
     */
    removeEventListeners() {
        if (this.observer) {
            this.observer.disconnect();
        }
        
        if (this.colorSchemeQuery && this.colorSchemeHandler) {
            this.colorSchemeQuery.removeEventListener('change', this.colorSchemeHandler);
        }
        
        if (this.contrastQuery && this.contrastHandler) {
            this.contrastQuery.removeEventListener('change', this.contrastHandler);
        }
        
        window.removeEventListener('beforeprint', this.beforePrintHandler);
        window.removeEventListener('afterprint', this.afterPrintHandler);
    }

    /**
     * Prepare for print mode
     */
    preparePrintMode() {
        document.body.classList.add('print-mode-font-enhanced');
        
        // Force high contrast for printing
        const reportElements = document.querySelectorAll('.font-enhanced');
        reportElements.forEach(element => {
            element.style.color = '#000000';
            element.style.backgroundColor = '#ffffff';
            element.style.textShadow = 'none';
        });
    }

    /**
     * Restore normal mode after printing
     */
    restoreNormalMode() {
        document.body.classList.remove('print-mode-font-enhanced');
        
        // Restore original styling
        setTimeout(() => {
            this.applyAdaptiveContrast();
            this.enhanceExistingReports();
        }, 100);
    }
}

// Register the service
registry.category("services").add("reportFontEnhancement", {
    dependencies: ["rpc"],
    start(env, { rpc }) {
        const service = new ReportFontEnhancementService();
        service.rpc = rpc;
        service.initializeEnhancements();
        return service;
    },
});

// Also initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const enhancementService = new ReportFontEnhancementService();
    enhancementService.initializeEnhancements();
});

// Export for use in other modules
export { ReportFontEnhancementService };
