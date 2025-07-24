/**
 * Chart.js Fallback Script
 * 
 * This script provides a fallback mechanism for Chart.js when the CDN fails to load.
 * It will attempt to dynamically load Chart.js from alternative CDNs if the primary one fails.
 * 
 * @version 1.1.0
 * @since Odoo 17.0
 */

(function() {
    window.chartJsFallbackStatus = {
        loaded: false,
        loading: false,
        error: null,
        source: null
    };
    
    // Don't run if Chart is already defined
    if (typeof Chart !== 'undefined') {
        console.log('Chart.js already loaded, skipping fallback');
        window.chartJsFallbackStatus.loaded = true;
        window.chartJsFallbackStatus.source = 'primary';
        return;
    }
    
    console.log('Chart.js fallback mechanism activated');
    
    // List of alternative CDNs to try in order
    const alternativeSources = [
        'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.js',
        'https://unpkg.com/chart.js@4.4.0/dist/chart.umd.js',
        // Add more fallback sources if needed
    ];
    
    /**
     * Attempt to load Chart.js from a given URL
     * @param {string} url - The URL to load Chart.js from
     * @returns {Promise} - Resolves when loaded, rejects on error
     */
    function loadScript(url) {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = url;
            script.async = true;
            
            script.onload = () => {
                console.log(`Successfully loaded Chart.js from ${url}`);
                resolve();
            };
            
            script.onerror = () => {
                console.warn(`Failed to load Chart.js from ${url}`);
                reject();
            };
            
            document.head.appendChild(script);
        });
    }
    
    /**
     * Try loading Chart.js from alternative sources
     */
    async function tryAlternativeSources() {
        for (const source of alternativeSources) {
            try {
                await loadScript(source);
                // If we reach here, the script loaded successfully
                return;
            } catch (error) {
                // This source failed, try the next one
                continue;
            }
        }
        
        // All sources failed
        console.error('All Chart.js fallback sources failed to load');
        
        // Add a custom notification to the DOM
        const container = document.querySelector('.o_oe_sale_dashboard_17_container');
        if (container) {
            const alert = document.createElement('div');
            alert.className = 'alert alert-warning';
            alert.textContent = 'Failed to load Chart.js library. Some visualizations may not be available.';
            container.prepend(alert);
        }
    }
    
    /**
     * Public function to check if Chart.js is available
     * @returns {Promise} - Resolves when Chart.js is available, rejects after timeout
     */
    window.ensureChartJsAvailable = function() {
        return new Promise((resolve, reject) => {
            // If already loaded, resolve immediately
            if (typeof Chart !== 'undefined') {
                window.chartJsFallbackStatus.loaded = true;
                resolve(true);
                return;
            }
            
            // If already trying to load, wait for it
            if (window.chartJsFallbackStatus.loading) {
                const maxWaitTime = 10000; // 10 seconds
                let waitTime = 0;
                const interval = setInterval(() => {
                    waitTime += 100;
                    
                    if (typeof Chart !== 'undefined') {
                        clearInterval(interval);
                        resolve(true);
                        return;
                    }
                    
                    if (waitTime >= maxWaitTime) {
                        clearInterval(interval);
                        reject(new Error('Timeout waiting for Chart.js to load'));
                        return;
                    }
                }, 100);
                return;
            }
            
            // Start loading process
            window.chartJsFallbackStatus.loading = true;
            
            // Wait a bit to see if the primary CDN loads Chart.js
            setTimeout(async () => {
                if (typeof Chart === 'undefined') {
                    // Primary CDN failed, try alternatives
                    try {
                        await tryAlternativeSources();
                        
                        if (typeof Chart !== 'undefined') {
                            window.chartJsFallbackStatus.loaded = true;
                            resolve(true);
                        } else {
                            window.chartJsFallbackStatus.error = 'All CDNs failed';
                            reject(new Error('Failed to load Chart.js from any source'));
                        }
                    } catch (error) {
                        window.chartJsFallbackStatus.error = error.message;
                        reject(error);
                    }
                } else {
                    window.chartJsFallbackStatus.loaded = true;
                    window.chartJsFallbackStatus.source = 'primary-delayed';
                    resolve(true);
                }
                
                window.chartJsFallbackStatus.loading = false;
            }, 2000);
        });
    };
    
    // Auto-initialize the fallback mechanism
    setTimeout(() => {
        if (typeof Chart === 'undefined') {
            // Primary CDN failed, try alternatives
            tryAlternativeSources();
        }
    }, 2000);
})();
