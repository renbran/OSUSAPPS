from odoo import models, api, fields
from datetime import datetime, timedelta
from collections import defaultdict
import logging

_logger = logging.getLogger(__name__)


class SaleDashboard(models.Model):
    _inherit = 'sale.order'

    @api.model
    def get_monthly_fluctuation_data(self, start_date, end_date, sales_type_ids=None):
        """
        Get monthly fluctuation data for deal analysis
        Returns data grouped by month for quotations, sales orders, and invoiced sales
        """
        try:
            # Parse dates
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            
            # Generate monthly buckets
            monthly_data = defaultdict(lambda: {
                'quotations': {'count': 0, 'amount': 0},
                'sales_orders': {'count': 0, 'amount': 0},
                'invoiced_sales': {'count': 0, 'amount': 0}
            })
            
            # Generate month labels
            current_dt = start_dt.replace(day=1)
            month_labels = []
            
            while current_dt <= end_dt:
                month_key = current_dt.strftime('%Y-%m')
                month_label = current_dt.strftime('%b %Y')
                month_labels.append(month_label)
                monthly_data[month_key]  # Initialize if not exists
                current_dt = current_dt.replace(day=28) + timedelta(days=4)
                current_dt = current_dt.replace(day=1)
            
            # Use create_date as fallback if booking_date doesn't exist
            date_field = 'booking_date' if 'booking_date' in self.env['sale.order']._fields else 'create_date'
            
            # Base domain for filtering
            base_domain = [
                (date_field, '>=', start_date),
                (date_field, '<=', end_date),
                ('state', '!=', 'cancel')  # Exclude cancelled orders
            ]
            
            # Check if sale_order_type_id exists before using it
            if sales_type_ids and 'sale_order_type_id' in self.env['sale.order']._fields:
                base_domain.append(('sale_order_type_id', 'in', sales_type_ids))
            
            # Get all orders
            orders = self.search_read(base_domain, [
                'state', 'invoice_status', 'amount_total', date_field, 'name'
            ])
            
            # Process each order
            for order in orders:
                order_date = order[date_field]
                if isinstance(order_date, str):
                    order_dt = datetime.strptime(order_date, '%Y-%m-%d')
                else:
                    order_dt = order_date
                
                month_key = order_dt.strftime('%Y-%m')
                amount = order.get('amount_total', 0)
                
                # Categorize order based on state
                if order['state'] == 'draft':
                    monthly_data[month_key]['quotations']['count'] += 1
                    monthly_data[month_key]['quotations']['amount'] += amount
                elif order['state'] == 'sale' and order['invoice_status'] != 'invoiced':
                    monthly_data[month_key]['sales_orders']['count'] += 1
                    monthly_data[month_key]['sales_orders']['amount'] += amount
                elif order['state'] == 'sale' and order['invoice_status'] == 'invoiced':
                    monthly_data[month_key]['invoiced_sales']['count'] += 1
                    monthly_data[month_key]['invoiced_sales']['amount'] += amount
            
            # Convert to lists for Chart.js
            quotations_data = []
            sales_orders_data = []
            invoiced_sales_data = []
            
            for label in month_labels:
                month_key = datetime.strptime(label, '%b %Y').strftime('%Y-%m')
                quotations_data.append(monthly_data[month_key]['quotations'])
                sales_orders_data.append(monthly_data[month_key]['sales_orders'])
                invoiced_sales_data.append(monthly_data[month_key]['invoiced_sales'])
            
            return {
                'labels': month_labels,
                'quotations': quotations_data,
                'sales_orders': sales_orders_data,
                'invoiced_sales': invoiced_sales_data
            }
            
        except Exception as e:
            _logger.error(f"Error in get_monthly_fluctuation_data: {str(e)}")
            return {
                'labels': [],
                'quotations': [],
                'sales_orders': [],
                'invoiced_sales': []
            }

    @api.model
    def get_sales_type_distribution(self, start_date, end_date):
        """
        Get sales type distribution data for pie charts
        Returns count and amount distribution by sales type
        """
        try:
            # Use create_date as fallback if booking_date doesn't exist
            date_field = 'booking_date' if 'booking_date' in self.env['sale.order']._fields else 'create_date'
            
            # Base domain excluding cancelled orders
            base_domain = [
                (date_field, '>=', start_date),
                (date_field, '<=', end_date),
                ('state', '!=', 'cancel')
            ]
            
            count_distribution = {}
            amount_distribution = {}
            
            # Check if sale order type exists
            if 'sale_order_type_id' in self.env['sale.order']._fields:
                # Get all sales types
                sales_types = self.env['sale.order.type'].search([])
                
                for sales_type in sales_types:
                    type_domain = base_domain + [('sale_order_type_id', '=', sales_type.id)]
                    
                    # Get all orders for this type
                    orders = self.search_read(type_domain, ['state', 'invoice_status', 'amount_total', 'name'])
                    
                    total_count = len(orders)
                    total_amount = sum(order.get('amount_total', 0) for order in orders)
                    
                    if total_count > 0:  # Only include types with data
                        count_distribution[sales_type.name] = total_count
                        amount_distribution[sales_type.name] = total_amount
            else:
                # Fallback: just use all orders as one type
                orders = self.search_read(base_domain, ['amount_total'])
                total_count = len(orders)
                total_amount = sum(order.get('amount_total', 0) for order in orders)
                
                if total_count > 0:
                    count_distribution['All Sales'] = total_count
                    amount_distribution['All Sales'] = total_amount
            
            return {
                'count_distribution': count_distribution,
                'amount_distribution': amount_distribution
            }
            
        except Exception as e:
            _logger.error(f"Error in get_sales_type_distribution: {str(e)}")
            return {
                'count_distribution': {},
                'amount_distribution': {}
            }

    @api.model 
    def get_top_performers_data(self, start_date, end_date, performer_type='agent', limit=10):
        """
        Get top performing agents or agencies based on sales performance
        Args:
            start_date: Start date for filtering
            end_date: End date for filtering  
            performer_type: 'agent' for agents, 'agency' for agencies
            limit: Number of top performers to return (default 10)
        Returns:
            List of top performers with their metrics
        """
        try:
            # Use create_date as fallback if booking_date doesn't exist
            date_field = 'booking_date' if 'booking_date' in self.env['sale.order']._fields else 'create_date'
            
            # Determine field names based on performer type and availability
            if performer_type == 'agent':
                partner_field = 'agent1_partner_id' if 'agent1_partner_id' in self.env['sale.order']._fields else None
                amount_field = 'agent1_amount' if 'agent1_amount' in self.env['sale.order']._fields else None
            elif performer_type == 'agency':
                partner_field = 'broker_partner_id' if 'broker_partner_id' in self.env['sale.order']._fields else None
                amount_field = 'broker_amount' if 'broker_amount' in self.env['sale.order']._fields else None
            else:
                return []

            # If required fields don't exist, return empty list
            if not partner_field:
                _logger.warning(f"Partner field for {performer_type} not found in sale.order model")
                return []

            # Base domain for filtering
            base_domain = [
                (date_field, '>=', start_date),
                (date_field, '<=', end_date),
                ('state', '!=', 'cancel'),  # Exclude cancelled orders
                (partner_field, '!=', False)  # Must have agent/broker assigned
            ]

            # Fields to read
            fields_to_read = [
                partner_field, 'amount_total', 'state', 'invoice_status', 'name', date_field
            ]
            
            # Add sale_value if it exists
            if 'sale_value' in self.env['sale.order']._fields:
                fields_to_read.append('sale_value')
                
            # Add commission field if it exists
            if amount_field and amount_field in self.env['sale.order']._fields:
                fields_to_read.append(amount_field)

            # Get all orders with the specified criteria  
            orders = self.search_read(base_domain, fields_to_read)
            
            _logger.info(f"Found {len(orders)} orders for {performer_type} ranking")
            
            # Group data by partner
            partner_data = {}
            
            for order in orders:
                partner_id = order.get(partner_field)
                if not partner_id:
                    continue
                    
                # Handle both tuple format (id, name) and plain id
                if isinstance(partner_id, tuple) and len(partner_id) == 2:
                    partner_key = partner_id[0]
                    partner_name = partner_id[1]
                elif isinstance(partner_id, (int, list)):
                    partner_key = partner_id[0] if isinstance(partner_id, list) else partner_id
                    # Get partner name from res.partner model
                    partner_rec = self.env['res.partner'].browse(partner_key)
                    partner_name = partner_rec.name if partner_rec.exists() else f"Partner {partner_key}"
                else:
                    continue
                
                if partner_key not in partner_data:
                    partner_data[partner_key] = {
                        'partner_id': partner_key,
                        'partner_name': partner_name,
                        'count': 0,
                        'total_sales_value': 0.0,
                        'total_commission': 0.0,
                        'invoiced_count': 0,
                        'invoiced_sales_value': 0.0,
                        'invoiced_commission': 0.0
                    }
                
                # Get values with proper fallbacks and validation
                sales_value = float(order.get('sale_value') or order.get('amount_total') or 0.0)
                commission_value = float(order.get(amount_field) or 0.0) if amount_field else 0.0
                
                # Add to totals
                partner_data[partner_key]['count'] += 1
                partner_data[partner_key]['total_sales_value'] += sales_value
                partner_data[partner_key]['total_commission'] += commission_value
                
                # If invoiced, add to invoiced totals
                if order.get('state') == 'sale' and order.get('invoice_status') == 'invoiced':
                    partner_data[partner_key]['invoiced_count'] += 1
                    partner_data[partner_key]['invoiced_sales_value'] += sales_value
                    partner_data[partner_key]['invoiced_commission'] += commission_value

            # Convert to list and sort by total sales value (descending), then by commission
            performers_list = list(partner_data.values())
            
            # Sort by multiple criteria for better ranking
            performers_list.sort(key=lambda x: (
                -float(x.get('total_sales_value', 0)),      # Primary: Total sales value (descending)
                -float(x.get('total_commission', 0)),       # Secondary: Total commission (descending) 
                -int(x.get('count', 0))                     # Tertiary: Number of sales (descending)
            ))
            
            # Return top performers limited to the specified count
            top_performers = performers_list[:limit]
            _logger.info(f"Returning top {len(top_performers)} {performer_type}s")
            return top_performers
            
        except Exception as e:
            # Log the error for debugging
            _logger.error(f"Error in get_top_performers_data: {str(e)}")
            _logger.error(f"Parameters: start_date={start_date}, end_date={end_date}, performer_type={performer_type}, limit={limit}")
            
            # Return empty list instead of error dict for frontend compatibility
            return []

    def _get_actual_invoiced_amount(self, order_name):
        """
        Helper method to get actual invoiced amount from account.move
        """
        try:
            # This is a placeholder - implement based on your invoice structure
            return 0.0
        except:
            return 0.0
