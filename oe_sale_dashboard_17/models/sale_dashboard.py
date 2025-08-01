from odoo import models, api, fields
from datetime import datetime, timedelta
from collections import defaultdict
import logging

_logger = logging.getLogger(__name__)


class SaleDashboard(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _check_field_exists(self, field_name):
        """Check if a field exists in the current model to ensure compatibility"""
        return field_name in self.env['sale.order']._fields

    @api.model
    def _get_safe_date_field(self):
        """Get the appropriate date field - booking_date if available, otherwise create_date"""
        return 'booking_date' if self._check_field_exists('booking_date') else 'create_date'

    @api.model
    def _get_safe_amount_field(self, record):
        """Get the best available amount field value"""
        if self._check_field_exists('sale_value') and record.get('sale_value'):
            return record['sale_value']
        return record.get('amount_total', 0)

    @api.model
    def format_dashboard_value(self, value):
        """
        Format large numbers for dashboard display with K/M/B suffixes
        Enhanced with better rounding and formatting
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
    def get_dashboard_summary_data(self, start_date, end_date, sales_type_ids=None):
        """
        Get comprehensive dashboard summary data filtered by date and sales type
        Enhanced with field validation and better error handling
        """
        try:
            date_field = self._get_safe_date_field()
            
            # Base domain for filtering with safe field checking
            base_domain = [
                (date_field, '>=', start_date),
                (date_field, '<=', end_date),
                ('state', '!=', 'cancel')  # Exclude cancelled orders
            ]
            
            # Only add sales type filter if the field exists
            if sales_type_ids and self._check_field_exists('sale_order_type_id'):
                base_domain.append(('sale_order_type_id', 'in', sales_type_ids))
            
            # Get sales types safely
            summary_data = {}
            total_summary = {
                'draft_count': 0, 'draft_amount': 0,
                'sales_order_count': 0, 'sales_order_amount': 0,
                'invoice_count': 0, 'invoice_amount': 0,
                'total_count': 0, 'total_amount': 0,
                # Enhanced KPIs
                'conversion_rate': 0,
                'avg_deal_size': 0,
                'revenue_growth': 0,
                'pipeline_velocity': 0
            }
            
            if self._check_field_exists('sale_order_type_id'):
                sales_types_domain = []
                if sales_type_ids:
                    sales_types_domain = [('id', 'in', sales_type_ids)]
                
                sales_types = self.env['sale.order.type'].search(sales_types_domain)
                
                for sales_type in sales_types:
                    type_domain = base_domain + [('sale_order_type_id', '=', sales_type.id)]
                    category_data = self._process_category_data(type_domain, sales_type.name)
                    summary_data[sales_type.name] = category_data
                    
                    # Add to totals
                    for key in ['draft_count', 'draft_amount', 'sales_order_count', 
                               'sales_order_amount', 'invoice_count', 'invoice_amount']:
                        total_summary[key] += category_data.get(key, 0)
            else:
                # Fallback when no sales types available
                category_data = self._process_category_data(base_domain, 'All Sales')
                summary_data['All Sales'] = category_data
                
                for key in ['draft_count', 'draft_amount', 'sales_order_count', 
                           'sales_order_amount', 'invoice_count', 'invoice_amount']:
                    total_summary[key] += category_data.get(key, 0)
            
            # Calculate enhanced KPIs
            total_summary['total_count'] = (total_summary['draft_count'] + 
                                          total_summary['sales_order_count'] + 
                                          total_summary['invoice_count'])
            total_summary['total_amount'] = (total_summary['draft_amount'] + 
                                           total_summary['sales_order_amount'] + 
                                           total_summary['invoice_amount'])
            
            # Enhanced KPI calculations
            if total_summary['draft_count'] > 0:
                total_summary['conversion_rate'] = (total_summary['invoice_count'] / total_summary['draft_count']) * 100
            
            if total_summary['total_count'] > 0:
                total_summary['avg_deal_size'] = total_summary['total_amount'] / total_summary['total_count']
            
            # Calculate revenue growth (comparison with previous period)
            total_summary['revenue_growth'] = self._calculate_revenue_growth(start_date, end_date, sales_type_ids)
            
            # Calculate pipeline velocity
            total_summary['pipeline_velocity'] = self._calculate_pipeline_velocity(start_date, end_date, sales_type_ids)
            
            return {
                'categories': summary_data,
                'totals': total_summary,
                'metadata': {
                    'date_field_used': date_field,
                    'has_sales_types': self._check_field_exists('sale_order_type_id'),
                    'has_sale_value': self._check_field_exists('sale_value')
                }
            }
            
        except Exception as e:
            _logger.error(f"Error in get_dashboard_summary_data: {str(e)}")
            return {
                'categories': {},
                'totals': {
                    'draft_count': 0, 'draft_amount': 0,
                    'sales_order_count': 0, 'sales_order_amount': 0,
                    'invoice_count': 0, 'invoice_amount': 0,
                    'total_count': 0, 'total_amount': 0,
                    'conversion_rate': 0, 'avg_deal_size': 0,
                    'revenue_growth': 0, 'pipeline_velocity': 0
                },
                'error': str(e)
            }

    def _process_category_data(self, base_domain, category_name):
        """Process data for a specific category with enhanced error handling"""
        try:
            # Fields to read with safe checking
            fields_to_read = ['state', 'invoice_status', 'amount_total', 'name']
            if self._check_field_exists('sale_value'):
                fields_to_read.append('sale_value')
            
            # Draft orders (quotations)
            draft_domain = base_domain + [('state', 'in', ['draft', 'sent'])]
            draft_orders = self.search_read(draft_domain, fields_to_read)
            draft_count = len(draft_orders)
            draft_amount = sum(self._get_safe_amount_field(order) for order in draft_orders)
            
            # Confirmed sales orders (not yet invoiced)
            so_domain = base_domain + [('state', '=', 'sale'), ('invoice_status', 'in', ['to invoice', 'no', 'upselling'])]
            so_orders = self.search_read(so_domain, fields_to_read)
            so_count = len(so_orders)
            so_amount = sum(self._get_safe_amount_field(order) for order in so_orders)
            
            # Invoiced sales orders
            invoice_domain = base_domain + [('state', '=', 'sale'), ('invoice_status', '=', 'invoiced')]
            invoice_orders = self.search_read(invoice_domain, fields_to_read)
            invoice_count = len(invoice_orders)
            invoice_amount = 0
            
            for order in invoice_orders:
                actual_amount = self._get_actual_invoiced_amount(order['name'])
                invoice_amount += actual_amount or self._get_safe_amount_field(order)
            
            # Calculate category totals
            category_total = draft_amount + so_amount + invoice_amount
            
            return {
                'draft_count': draft_count,
                'draft_amount': draft_amount,
                'sales_order_count': so_count,
                'sales_order_amount': so_amount,
                'invoice_count': invoice_count,
                'invoice_amount': invoice_amount,
                'total_count': draft_count + so_count + invoice_count,
                'total_amount': category_total,
                'category_name': category_name
            }
            
        except Exception as e:
            _logger.error(f"Error processing category {category_name}: {str(e)}")
            return {
                'draft_count': 0, 'draft_amount': 0,
                'sales_order_count': 0, 'sales_order_amount': 0,
                'invoice_count': 0, 'invoice_amount': 0,
                'total_count': 0, 'total_amount': 0,
                'category_name': category_name
            }

    def _calculate_revenue_growth(self, start_date, end_date, sales_type_ids=None):
        """Calculate revenue growth compared to previous period"""
        try:
            # Current period revenue
            current_revenue = self._get_period_revenue(start_date, end_date, sales_type_ids)
            
            # Calculate previous period dates
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            period_length = (end_dt - start_dt).days
            
            prev_end_dt = start_dt - timedelta(days=1)
            prev_start_dt = prev_end_dt - timedelta(days=period_length)
            
            # Previous period revenue
            prev_revenue = self._get_period_revenue(
                prev_start_dt.strftime('%Y-%m-%d'), 
                prev_end_dt.strftime('%Y-%m-%d'), 
                sales_type_ids
            )
            
            if prev_revenue > 0:
                growth = ((current_revenue - prev_revenue) / prev_revenue) * 100
                return round(growth, 2)
            
            return 0.0
            
        except Exception as e:
            _logger.error(f"Error calculating revenue growth: {str(e)}")
            return 0.0

    def _get_period_revenue(self, start_date, end_date, sales_type_ids=None):
        """Get total revenue for a specific period"""
        try:
            date_field = self._get_safe_date_field()
            domain = [
                (date_field, '>=', start_date),
                (date_field, '<=', end_date),
                ('state', '=', 'sale'),
                ('invoice_status', '=', 'invoiced')
            ]
            
            if sales_type_ids and self._check_field_exists('sale_order_type_id'):
                domain.append(('sale_order_type_id', 'in', sales_type_ids))
            
            fields_to_read = ['amount_total', 'name']
            if self._check_field_exists('sale_value'):
                fields_to_read.append('sale_value')
                
            orders = self.search_read(domain, fields_to_read)
            
            total_revenue = 0
            for order in orders:
                actual_amount = self._get_actual_invoiced_amount(order['name'])
                total_revenue += actual_amount or self._get_safe_amount_field(order)
                
            return total_revenue
            
        except Exception as e:
            _logger.error(f"Error getting period revenue: {str(e)}")
            return 0.0

    def _calculate_pipeline_velocity(self, start_date, end_date, sales_type_ids=None):
        """Calculate average time from quotation to invoice"""
        try:
            date_field = self._get_safe_date_field()
            domain = [
                (date_field, '>=', start_date),
                (date_field, '<=', end_date),
                ('state', '=', 'sale'),
                ('invoice_status', '=', 'invoiced')
            ]
            
            if sales_type_ids and self._check_field_exists('sale_order_type_id'):
                domain.append(('sale_order_type_id', 'in', sales_type_ids))
            
            fields_to_read = [date_field, 'date_order', 'confirmation_date']
            orders = self.search_read(domain, fields_to_read)
            
            if not orders:
                return 0.0
            
            total_days = 0
            valid_orders = 0
            
            for order in orders:
                order_date = order.get('confirmation_date') or order.get('date_order')
                invoice_date = order.get(date_field)
                
                if order_date and invoice_date:
                    if isinstance(order_date, str):
                        order_dt = datetime.strptime(order_date[:10], '%Y-%m-%d')
                    else:
                        order_dt = order_date
                    
                    if isinstance(invoice_date, str):
                        invoice_dt = datetime.strptime(invoice_date[:10], '%Y-%m-%d')
                    else:
                        invoice_dt = invoice_date
                    
                    days_diff = (invoice_dt - order_dt).days
                    if days_diff >= 0:  # Valid progression
                        total_days += days_diff
                        valid_orders += 1
            
            return round(total_days / valid_orders, 1) if valid_orders > 0 else 0.0
            
        except Exception as e:
            _logger.error(f"Error calculating pipeline velocity: {str(e)}")
            return 0.0

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

    @api.model
    def get_sales_type_ranking_data(self, start_date, end_date, sales_type_ids=None):
        """
        Get ranking data for sales types based on count, sales value, and total
        Returns a list sorted by performance metrics
        """
        try:
            # Base domain
            base_domain = [
                ('booking_date', '>=', start_date),
                ('booking_date', '<=', end_date),
                ('state', '!=', 'cancel')
            ]
            
            if sales_type_ids:
                base_domain.append(('sale_order_type_id', 'in', sales_type_ids))
            
            # Get sales types to rank
            sales_types_domain = []
            if sales_type_ids:
                sales_types_domain = [('id', 'in', sales_type_ids)]
            
            sales_types = self.env['sale.order.type'].search(sales_types_domain)
            
            ranking_data = []
            
            for sales_type in sales_types:
                type_domain = base_domain + [('sale_order_type_id', '=', sales_type.id)]
                
                # Get all orders for this type
                orders = self.search_read(type_domain, ['state', 'invoice_status', 'sale_value', 'amount_total', 'name'])
                
                total_count = len(orders)
                total_sales_value = 0.0
                total_amount = 0.0
                invoiced_count = 0
                invoiced_amount = 0.0
                
                for order in orders:
                    sales_value = order['sale_value'] or order['amount_total'] or 0
                    total_sales_value += sales_value
                    total_amount += order['amount_total'] or 0
                    
                    # Calculate invoiced amounts
                    if order['state'] == 'sale' and order['invoice_status'] == 'invoiced':
                        invoiced_count += 1
                        actual_invoiced = self._get_actual_invoiced_amount(order['name'])
                        invoiced_amount += actual_invoiced or sales_value
                
                # Calculate performance metrics
                avg_deal_size = total_sales_value / total_count if total_count > 0 else 0
                invoiced_rate = (invoiced_count / total_count * 100) if total_count > 0 else 0
                
                ranking_data.append({
                    'sales_type_name': sales_type.name,
                    'total_count': total_count,
                    'total_sales_value': total_sales_value,
                    'total_amount': total_amount,
                    'invoiced_count': invoiced_count,
                    'invoiced_amount': invoiced_amount,
                    'avg_deal_size': avg_deal_size,
                    'invoiced_rate': invoiced_rate,
                    'performance_score': total_sales_value * 0.4 + invoiced_amount * 0.4 + total_count * 0.2
                })
            
            # Sort by performance score (descending)
            ranking_data.sort(key=lambda x: x['performance_score'], reverse=True)
            
            return ranking_data
            
        except Exception as e:
            _logger.error(f"Error in get_sales_type_ranking_data: {str(e)}")
            return []
