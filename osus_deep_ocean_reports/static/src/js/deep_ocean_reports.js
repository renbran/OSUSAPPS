/** @odoo-module */

// Deep Ocean Reports JavaScript Module
// Professional navy and azure theme enhancements

import { Component } from "@odoo/owl";

export class DeepOceanReports {
    constructor() {
        this.colors = {
            deepNavy: '#1e3a8a',
            oceanBlue: '#3b82f6',
            skyBlue: '#0ea5e9',
            iceWhite: '#f8fafc'
        };
        
        this.init();
    }

    init() {
        // Initialize Deep Ocean report enhancements
        this.addAnimations();
        this.enhanceInteractivity();
        this.optimizeForPrint();
    }

    addAnimations() {
        // Add smooth animations for report elements
        document.addEventListener('DOMContentLoaded', () => {
            const reportElements = document.querySelectorAll('.deep-ocean-report *');
            reportElements.forEach((element, index) => {
                element.style.animationDelay = `${index * 0.05}s`;
                element.classList.add('deep-ocean-fade-in');
            });
        });
    }

    enhanceInteractivity() {
        // Add hover effects and interactive elements
        document.addEventListener('DOMContentLoaded', () => {
            // Table row hover effects
            const tableRows = document.querySelectorAll('.deep-ocean-table tbody tr');
            tableRows.forEach(row => {
                row.addEventListener('mouseenter', () => {
                    row.style.transform = 'translateY(-2px)';
                    row.style.boxShadow = '0 4px 15px rgba(30, 58, 138, 0.15)';
                });
                
                row.addEventListener('mouseleave', () => {
                    row.style.transform = 'translateY(0)';
                    row.style.boxShadow = 'none';
                });
            });

            // QR Code interaction
            const qrCodes = document.querySelectorAll('.deep-ocean-qr-code img');
            qrCodes.forEach(qr => {
                qr.addEventListener('click', () => {
                    qr.style.transform = 'scale(1.1)';
                    setTimeout(() => {
                        qr.style.transform = 'scale(1)';
                    }, 300);
                });
            });
        });
    }

    optimizeForPrint() {
        // Optimize report for printing
        const printStyles = `
            @media print {
                .deep-ocean-report {
                    -webkit-print-color-adjust: exact;
                    color-adjust: exact;
                }
                
                .deep-ocean-header::before {
                    display: none !important;
                }
                
                .deep-ocean-table tbody tr:hover {
                    transform: none !important;
                    box-shadow: none !important;
                }
                
                .deep-ocean-fade-in {
                    animation: none !important;
                }
            }
        `;
        
        const styleSheet = document.createElement('style');
        styleSheet.textContent = printStyles;
        document.head.appendChild(styleSheet);
    }

    // Utility functions for report enhancement
    static formatCurrency(amount, currency = 'AED') {
        return new Intl.NumberFormat('en-AE', {
            style: 'currency',
            currency: currency,
            minimumFractionDigits: 2
        }).format(amount);
    }

    static formatDate(date, locale = 'en-GB') {
        return new Intl.DateTimeFormat(locale, {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        }).format(new Date(date));
    }

    static generateAnalyticsReference() {
        const timestamp = Date.now();
        const random = Math.random().toString(36).substring(2, 8);
        return `DO-${timestamp}-${random}`.toUpperCase();
    }
}

// Initialize Deep Ocean Reports when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new DeepOceanReports();
});

// Export for use in other modules
export default DeepOceanReports;