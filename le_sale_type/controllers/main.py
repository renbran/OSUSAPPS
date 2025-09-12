from odoo import http
from odoo.http import request
import json


class SaleOrderTypeController(http.Controller):

    @http.route('/sale_order_type/get_dynamic_filters', type='json', auth='user')
    def get_dynamic_filters(self):
        """
        Returns dynamic filters for sale order types
        """
        try:
            sale_types = request.env['sale.order.type'].search([('active', '=', True)])
            filters = []
            
            for sale_type in sale_types:
                filter_data = {
                    'id': f'dynamic_sale_type_{sale_type.id}',
                    'name': f'{sale_type.name}_orders',
                    'string': f'{sale_type.name} Orders',
                    'domain': [('sale_order_type_id', '=', sale_type.id)],
                    'context': {},
                    'group_id': 'sale_type_filters',
                    'sequence': sale_type.id,
                }
                filters.append(filter_data)
            
            return {
                'success': True,
                'filters': filters
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @http.route('/sale_order_type/get_sale_orders_by_type', type='json', auth='user')
    def get_sale_orders_by_type(self, sale_type_id=None):
        """
        Returns sale orders filtered by type
        """
        try:
            domain = []
            if sale_type_id:
                domain = [('sale_order_type_id', '=', sale_type_id)]
            
            orders = request.env['sale.order'].search_read(
                domain,
                ['name', 'partner_id', 'amount_total', 'state', 'sale_order_type_id']
            )
            
            return {
                'success': True,
                'orders': orders
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
