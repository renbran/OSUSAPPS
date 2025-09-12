from odoo import models, fields, api
from odoo.osv import expression


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sale_order_type_id = fields.Many2one('sale.order.type', string="Sale Type")

    @api.model
    def create(self, vals):
        # Check if sale_order_type_id is provided in vals
        if vals.get('sale_order_type_id'):
            sale_type = self.env['sale.order.type'].browse(vals['sale_order_type_id'])
            # Ensure that sale_type has a valid sequence
            if sale_type.sequence_id:
                # Generate the next sequence number for the sale order name
                vals['name'] = sale_type.sequence_id.next_by_id()
            else:
                # Raise an exception if no sequence is associated with the sale type
                raise ValueError("The selected Sale Order Type does not have a sequence associated with it.")
        return super(SaleOrder, self).create(vals)

    @api.model
    def get_dynamic_sale_type_filters(self):
        """
        Generate dynamic search filters for all active sale order types
        Returns a list of filter dictionaries for use in search views
        """
        filters = []
        sale_types = self.env['sale.order.type'].search([('active', '=', True)])
        
        for sale_type in sale_types:
            filter_data = {
                'name': f"filter_sale_type_{sale_type.id}",
                'string': f"{sale_type.name} Orders",
                'domain': [('sale_order_type_id', '=', sale_type.id)],
                'context': {'group_by': 'sale_order_type_id'},
            }
            filters.append(filter_data)
        
        return filters

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        """
        Override search_read to handle dynamic filtering context
        """
        # Check if we have a specific sale type filter in context
        if self._context.get('search_default_sale_type_filter'):
            sale_type_id = self._context.get('search_default_sale_type_filter')
            if domain is None:
                domain = []
            domain = expression.AND([domain, [('sale_order_type_id', '=', sale_type_id)]])
        
        return super().search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)
