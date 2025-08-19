from odoo import models, api, fields
from datetime import datetime, timedelta
from collections import defaultdict
import logging

_logger = logging.getLogger(__name__)


class SaleDashboard(models.Model):
    _inherit = 'sale.order'

    @api.model
    def format_dashboard_value(self, value):
        """
        Format large numbers for dashboard display with K/M/B suffixes
        Args:
            value (float/int): The numerical value to format
        Returns:
            str: Formatted string with appropriate suffix
        """
        if not value or value == 0:
            return "0"
        
        abs_value = abs(value)
        
        if abs_value >= 1_000_000_000:
            formatted = round(value / 1_000_000_000, 2)
            return f"{formatted} B"
        elif abs_value >= 1_000_000:
            formatted = round(value / 1_000_000, 2)
            return f"{formatted} M"
        elif abs_value >= 1_000:
            formatted = round(value / 1_000)
            return f"{formatted:.0f} K"
        else:
            return f"{round(value):.0f}"

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
            
            # Base domain for filtering
            base_domain = [
                ('booking_date', '>=', start_date),
                ('booking_date', '<=', end_date),
                ('state', '!=', 'cancel')  # Exclude cancelled orders
            ]
            
            if sales_type_ids:
                base_domain.append(('sale_order_type_id', 'in', sales_type_ids))
            
            # Get quotations (draft, sent)
            quotation_domain = base_domain + [('state', 'in', ['draft', 'sent'])]
            quotations = self.search_read(quotation_domain, ['booking_date', 'amount_total', 'sale_value'])
            
            for quote in quotations:
                if quote['booking_date']:
                    month_key = quote['booking_date'].strftime('%Y-%m')
                    if month_key in monthly_data:
                        monthly_data[month_key]['quotations']['count'] += 1
                        monthly_data[month_key]['quotations']['amount'] += quote['sale_value'] or quote['amount_total'] or 0
            
            # Get sales orders (confirmed but not invoiced)
            sales_order_domain = base_domain + [
                ('state', '=', 'sale'),
                ('invoice_status', 'in', ['to invoice', 'no', 'upselling'])
            ]
            sales_orders = self.search_read(sales_order_domain, ['booking_date', 'amount_total', 'sale_value'])
            
            for order in sales_orders:
                if order['booking_date']:
                    month_key = order['booking_date'].strftime('%Y-%m')
                    if month_key in monthly_data:
                        monthly_data[month_key]['sales_orders']['count'] += 1
                        monthly_data[month_key]['sales_orders']['amount'] += order['sale_value'] or order['amount_total'] or 0
            
            # Get invoiced sales
            invoiced_domain = base_domain + [
                ('state', '=', 'sale'),
                ('invoice_status', '=', 'invoiced')
            ]
            invoiced_orders = self.search_read(invoiced_domain, ['booking_date', 'amount_total', 'sale_value', 'name'])
            
            # Get actual invoiced amounts
            for order in invoiced_orders:
                if order['booking_date']:
                    month_key = order['booking_date'].strftime('%Y-%m')
                    if month_key in monthly_data:
                        monthly_data[month_key]['invoiced_sales']['count'] += 1
                        
                        # Try to get actual invoiced amount
                        invoiced_amount = self._get_actual_invoiced_amount(order['name'])
                        amount = invoiced_amount or order['sale_value'] or order['amount_total'] or 0
                        monthly_data[month_key]['invoiced_sales']['amount'] += amount
            
            # Convert to chart format
            result = {
                'labels': month_labels,
                'quotations': [],
                'sales_orders': [],
                'invoiced_sales': []
            }
            
            for label in month_labels:
                # Find the corresponding month data
                month_key = None
                for key in monthly_data.keys():
                    if datetime.strptime(key, '%Y-%m').strftime('%b %Y') == label:
                        month_key = key
                        break
                
                if month_key and month_key in monthly_data:
                    result['quotations'].append(monthly_data[month_key]['quotations']['amount'])
                    result['sales_orders'].append(monthly_data[month_key]['sales_orders']['amount'])
                    result['invoiced_sales'].append(monthly_data[month_key]['invoiced_sales']['amount'])
                else:
                    result['quotations'].append(0)
                    result['sales_orders'].append(0)
                    result['invoiced_sales'].append(0)
            
            return result
            
        except Exception as e:
            # Return default data structure on error
            return {
                'labels': ['Current Period'],
                'quotations': [0],
                'sales_orders': [0],
                'invoiced_sales': [0],
                'error': str(e)
            }
    
    def _get_actual_invoiced_amount(self, order_name):
        """Get actual invoiced amount from account.move records"""
        try:
            invoices = self.env['account.move'].search([
                ('invoice_origin', '=', order_name),
                ('move_type', 'in', ['out_invoice', 'out_refund']),
                ('state', '=', 'posted')
            ])
            
            total_amount = 0.0
            for invoice in invoices:
                if invoice.move_type == 'out_invoice':
                    total_amount += invoice.amount_total
                elif invoice.move_type == 'out_refund':
                    total_amount -= invoice.amount_total
            
            return total_amount
        except:
            return 0.0

    @api.model
    def get_sales_type_distribution(self, start_date, end_date):
        """
        Get sales type distribution data for pie charts
        Returns count and amount distribution by sales type
        """
        try:
            # Base domain excluding cancelled orders
            base_domain = [
                ('booking_date', '>=', start_date),
                ('booking_date', '<=', end_date),
                ('state', '!=', 'cancel')
            ]
            
            # Get all sales types
            sales_types = self.env['sale.order.type'].search([])
            
            count_distribution = {}
            amount_distribution = {}
            
            for sales_type in sales_types:
                type_domain = base_domain + [('sale_order_type_id', '=', sales_type.id)]
                
                # Get all orders for this type
                orders = self.search_read(type_domain, ['state', 'invoice_status', 'amount_total', 'sale_value', 'name'])
                
                total_count = len(orders)
                total_amount = 0.0
                
                for order in orders:
                    # For invoiced orders, try to get actual invoiced amount
                    if order['state'] == 'sale' and order['invoice_status'] == 'invoiced':
                        invoiced_amount = self._get_actual_invoiced_amount(order['name'])
                        amount = invoiced_amount or order['sale_value'] or order['amount_total'] or 0
                    else:
                        amount = order['sale_value'] or order['amount_total'] or 0
                    
                    total_amount += amount
                
                if total_count > 0:  # Only include types with data
                    count_distribution[sales_type.name] = total_count
                    amount_distribution[sales_type.name] = total_amount
            
            return {
                'count_distribution': count_distribution,
                'amount_distribution': amount_distribution
            }
            
        except Exception as e:
            return {
                'count_distribution': {},
                'amount_distribution': {},
                'error': str(e)
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
            # Determine field names based on performer type
            if performer_type == 'agent':
                partner_field = 'agent1_partner_id'
                amount_field = 'agent1_amount'
            elif performer_type == 'agency':
                partner_field = 'broker_partner_id'
                amount_field = 'broker_amount'
            else:
                return []

            # Base domain for filtering
            base_domain = [
                ('booking_date', '>=', start_date),
                ('booking_date', '<=', end_date),
                ('state', '!=', 'cancel'),  # Exclude cancelled orders
                (partner_field, '!=', False)  # Must have agent/broker assigned
            ]

            # Get all orders with the specified criteria  
            # Include all necessary fields for comprehensive ranking
            orders = self.search_read(base_domain, [
                partner_field, 'amount_total', 'sale_value', amount_field, 
                'state', 'invoice_status', 'name', 'booking_date'
            ])
            
            # Debug logging
            import logging
            _logger = logging.getLogger(__name__)
            _logger.info(f"Found {len(orders)} orders for {performer_type} ranking")
            if orders:
                _logger.info(f"Sample order fields: {list(orders[0].keys())}")
                _logger.info(f"Sample order data: {orders[0]}")
                _logger.info(f"Looking for partner field: {partner_field}, amount field: {amount_field}")

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
                commission_value = float(order.get(amount_field) or 0.0)
                
                # Debug logging for first few records
                if len(partner_data) < 3:
                    _logger.info(f"Processing order {order.get('name')}: sales_value={sales_value}, commission={commission_value}, partner={partner_name}")
                
                # Add to totals
                partner_data[partner_key]['count'] += 1
                partner_data[partner_key]['total_sales_value'] += sales_value
                partner_data[partner_key]['total_commission'] += commission_value
                
                # If invoiced, add to invoiced totals
                if order.get('state') == 'sale' and order.get('invoice_status') == 'invoiced':
                    partner_data[partner_key]['invoiced_count'] += 1
                    
                    # Try to get actual invoiced amount
                    order_name = order.get('name', '')
                    invoiced_amount = self._get_actual_invoiced_amount(order_name)
                    final_sales_value = invoiced_amount or sales_value
                    
                    partner_data[partner_key]['invoiced_sales_value'] += final_sales_value
                    partner_data[partner_key]['invoiced_commission'] += commission_value

            # Convert to list and sort by total sales value (descending), then by commission
            performers_list = list(partner_data.values())
            
            # Sort by multiple criteria for better ranking
            performers_list.sort(key=lambda x: (
                -float(x.get('total_sales_value', 0)),      # Primary: Total sales value (descending)
                -float(x.get('total_commission', 0)),       # Secondary: Total commission (descending) 
                -int(x.get('count', 0))                     # Tertiary: Number of sales (descending)
            ))
            
            # Debug logging
            _logger.info(f"Sorted {len(performers_list)} {performer_type}s. Top 3:")
            for i, performer in enumerate(performers_list[:3]):
                _logger.info(f"  {i+1}. {performer.get('partner_name')} - Sales: {performer.get('total_sales_value')}, Commission: {performer.get('total_commission')}")
            
            # Return top performers limited to the specified count
            top_performers = performers_list[:limit]
            _logger.info(f"Returning top {len(top_performers)} {performer_type}s")
            return top_performers
            
        except Exception as e:
            # Log the error for debugging
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error(f"Error in get_top_performers_data: {str(e)}")
            _logger.error(f"Parameters: start_date={start_date}, end_date={end_date}, performer_type={performer_type}, limit={limit}")
            
            # Return empty list instead of error dict for frontend compatibility
            return []
