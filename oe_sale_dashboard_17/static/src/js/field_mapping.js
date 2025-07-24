/**
 * Field Mapping and Validation for Dashboard
 * 
 * This module ensures the dashboard can work with or without the custom fields
 * from the osus_invoice_report and le_sale_type modules by providing fallbacks
 * for missing fields.
 * 
 * @version 1.0.0
 * @since Odoo 17.0.0.2.0
 */

odoo.define('oe_sale_dashboard_17.field_mapping', function (require) {
    'use strict';
    
    var fieldMapping = {
        // Default mappings
        booking_date: 'date_order',
        sale_value: 'amount_total',
        
        // Track which fields are available
        _available: {}
    };
    
    /**
     * Initialize field mapping based on available fields
     * @param {Object} orm - The ORM service
     * @returns {Promise} - Resolves when mapping is initialized
     */
    async function initFieldMapping(orm) {
        if (!orm) {
            console.error('ORM service not available for field mapping');
            return;
        }
        
        try {
            // Check which fields exist in sale.order model
            const fields = await orm.call(
                'sale.order', 
                'fields_get', 
                [['booking_date', 'sale_value', 'date_order', 'amount_total', 'sale_type_id']]
            );
            
            // Update available fields
            fieldMapping._available = {
                booking_date: !!fields.booking_date,
                sale_value: !!fields.sale_value,
                sale_type_id: !!fields.sale_type_id,
                date_order: !!fields.date_order,
                amount_total: !!fields.amount_total
            };
            
            // Log available fields
            console.log('Dashboard field availability:', fieldMapping._available);
            
            // Update mappings based on available fields
            if (fieldMapping._available.booking_date) {
                fieldMapping.booking_date = 'booking_date';
            } else {
                fieldMapping.booking_date = 'date_order';
                console.warn('booking_date field not found, using date_order as fallback');
            }
            
            if (fieldMapping._available.sale_value) {
                fieldMapping.sale_value = 'sale_value';
            } else {
                fieldMapping.sale_value = 'amount_total';
                console.warn('sale_value field not found, using amount_total as fallback');
            }
            
            return fieldMapping;
        } catch (error) {
            console.error('Error initializing field mapping:', error);
            return fieldMapping;
        }
    }
    
    /**
     * Get the appropriate field name to use in a query
     * @param {string} fieldName - The logical field name
     * @returns {string} - The actual field name to use
     */
    function getFieldName(fieldName) {
        return fieldMapping[fieldName] || fieldName;
    }
    
    /**
     * Build a domain for date range filtering using the appropriate date field
     * @param {string} startDate - The start date (YYYY-MM-DD)
     * @param {string} endDate - The end date (YYYY-MM-DD)
     * @returns {Array} - The domain array for filtering
     */
    function buildDateDomain(startDate, endDate) {
        const dateField = getFieldName('booking_date');
        return [
            [dateField, '>=', startDate],
            [dateField, '<=', endDate]
        ];
    }
    
    /**
     * Build a domain for sale type filtering
     * @param {integer} saleTypeId - The sale type ID to filter by
     * @returns {Array} - The domain array for filtering, or empty if sale_type_id is not available
     */
    function buildSaleTypeDomain(saleTypeId) {
        if (saleTypeId && fieldMapping._available.sale_type_id) {
            return [['sale_type_id', '=', saleTypeId]];
        }
        return [];
    }
    
    /**
     * Build a field list for amount calculations
     * @returns {Array} - Field list to include in read_group
     */
    function getAmountFields() {
        const fields = ['amount_total'];
        
        if (fieldMapping._available.sale_value) {
            fields.push('sale_value');
        }
        
        return fields;
    }
    
    return {
        initFieldMapping: initFieldMapping,
        getFieldName: getFieldName,
        buildDateDomain: buildDateDomain,
        buildSaleTypeDomain: buildSaleTypeDomain,
        getAmountFields: getAmountFields,
        isFieldAvailable: function(fieldName) {
            return !!fieldMapping._available[fieldName];
        }
    };
});
