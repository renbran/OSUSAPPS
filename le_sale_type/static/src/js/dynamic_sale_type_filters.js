/** @odoo-module **/

import { SearchModel } from "@web/search/search_model";
import { patch } from "@web/core/utils/patch";

patch(SearchModel.prototype, "le_sale_type.dynamic_filters", {
    /**
     * Override _importFilters to add dynamic sale type filters
     */
    async _importFilters(filters, groupBys) {
        await super._importFilters(filters, groupBys);
        
        if (this.resModel === 'sale.order') {
            await this._addDynamicSaleTypeFilters();
        }
    },

    /**
     * Add dynamic filters for each active sale order type
     */
    async _addDynamicSaleTypeFilters() {
        try {
            const saleTypes = await this.orm.searchRead(
                'sale.order.type',
                [['active', '=', true]],
                ['id', 'name']
            );

            saleTypes.forEach(saleType => {
                const filterId = `dynamic_sale_type_${saleType.id}`;
                
                // Check if filter already exists to avoid duplicates
                if (!this.filters.find(f => f.id === filterId)) {
                    const dynamicFilter = {
                        id: filterId,
                        type: "filter",
                        description: `${saleType.name} Orders`,
                        domain: [['sale_order_type_id', '=', saleType.id]],
                        context: {},
                        groupId: "sale_type_filters",
                        isDefault: false,
                    };
                    
                    this.filters.push(dynamicFilter);
                }
            });

            // Trigger re-render
            this.trigger('update');
        } catch (error) {
            console.warn('Failed to load dynamic sale type filters:', error);
        }
    },
});
