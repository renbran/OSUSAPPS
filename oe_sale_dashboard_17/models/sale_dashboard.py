# -*- coding: utf-8 -*-
from odoo import models, api, fields, _
from datetime import datetime, timedelta
from collections import defaultdict
import logging

_logger = logging.getLogger(__name__)


<<<<<<< Updated upstream
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
=======
class SaleDashboardSimple(models.TransientModel):
    _name = 'sale.dashboard'
    _description = 'Sales Dashboard'

    @api.model
    def format_dashboard_value(self, value):
        """Format large numbers for dashboard display with K/M/B suffixes"""
>>>>>>> Stashed changes
        if not value or value == 0:
            return "0"
        
        abs_value = abs(value)
        
        if abs_value >= 1_000_000_000:
            formatted = round(value / 1_000_000_000, 2)
            return f"{formatted}B"
        elif abs_value >= 1_000_000:
            formatted = round(value / 1_000_000, 2)
            return f"{formatted}M"
        elif abs_value >= 1_000:
            formatted = round(value / 1_000)
            return f"{formatted:.0f}K"
        else:
            return f"{round(value):.0f}"

    @api.model
<<<<<<< Updated upstream
=======
    def get_sales_performance_data(self, start_date, end_date, sale_type_ids=None):
        """Get sales performance data with optional sale type filtering"""
        try:
            _logger.info(f"Getting performance data from {start_date} to {end_date}")
            
            sale_order = self.env['sale.order']
            
            # Use booking_date field if available, fallback to date_order
            date_field = 'booking_date' if hasattr(sale_order, 'booking_date') else 'date_order'
            
            # Base domain
            base_domain = [
                (date_field, '>=', start_date),
                (date_field, '<=', end_date),
                ('state', '!=', 'cancel')
            ]
            
            # Add sale type filter if provided
            if sale_type_ids and hasattr(sale_order, 'sale_order_type_id'):
                base_domain.append(('sale_order_type_id', 'in', sale_type_ids))
            
            # Count quotations (draft, sent)
            quotation_count = sale_order.search_count(base_domain + [('state', 'in', ['draft', 'sent'])])
            
            # Count sales orders (sale, done)
            sales_order_count = sale_order.search_count(base_domain + [('state', 'in', ['sale', 'done'])])
            
            # Count invoiced sales
            invoice_count = sale_order.search_count(base_domain + [('invoice_status', 'in', ['invoiced', 'to invoice'])])
            
            # Get total amount
            orders = sale_order.search(base_domain)
            total_amount = sum(order.amount_total for order in orders)
            
            result = {
                'total_quotations': quotation_count,
                'total_orders': sales_order_count,
                'total_invoiced': invoice_count,
                'total_amount': total_amount,
                'quotation_count': quotation_count,
                'sales_order_count': sales_order_count,
                'invoice_count': invoice_count
            }
            
            _logger.info(f"Performance data result: {result}")
            return result
            
        except Exception as e:
            _logger.error(f"Error getting performance data: {e}")
            return {
                'total_quotations': 0,
                'total_orders': 0,
                'total_invoiced': 0,
                'total_amount': 0,
                'quotation_count': 0,
                'sales_order_count': 0,
                'invoice_count': 0
            }

    @api.model
>>>>>>> Stashed changes
    def get_monthly_fluctuation_data(self, start_date, end_date, sales_type_ids=None):
        """Get monthly fluctuation data with booking_date support"""
        try:
            _logger.info(f"Getting monthly data from {start_date} to {end_date}")
            
            sale_order = self.env['sale.order']
            date_field = 'booking_date' if hasattr(sale_order, 'booking_date') else 'date_order'
            
            # Parse dates
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            
            # Generate monthly buckets
            result = []
            current_dt = start_dt.replace(day=1)
            
            while current_dt <= end_dt:
                month_start = current_dt.strftime('%Y-%m-%d')
                
                # Calculate month end
                if current_dt.month == 12:
                    next_month = current_dt.replace(year=current_dt.year + 1, month=1, day=1)
                else:
                    next_month = current_dt.replace(month=current_dt.month + 1, day=1)
                month_end = (next_month - timedelta(days=1)).strftime('%Y-%m-%d')
                
                # Get orders for this month
                month_domain = [
                    (date_field, '>=', month_start),
                    (date_field, '<=', month_end),
                    ('state', '!=', 'cancel')
                ]
                
                # Add sale type filter if provided
                if sales_type_ids and hasattr(sale_order, 'sale_order_type_id'):
                    month_domain.append(('sale_order_type_id', 'in', sales_type_ids))
                
                orders = sale_order.search(month_domain)
                total_amount = sum(order.amount_total for order in orders)
                
                result.append({
                    'month': current_dt.strftime('%b %Y'),
                    'amount': total_amount,
                    'count': len(orders)
                })
                
                # Move to next month
                if current_dt.month == 12:
                    current_dt = current_dt.replace(year=current_dt.year + 1, month=1)
                else:
                    current_dt = current_dt.replace(month=current_dt.month + 1)
            
            _logger.info(f"Monthly data result: {len(result)} months")
            return result
            
        except Exception as e:
            _logger.error(f"Error getting monthly data: {e}")
            return []
<<<<<<< Updated upstream
=======

    @api.model
    def get_sales_by_state_data(self, start_date, end_date, sale_type_ids=None):
        """Get sales by state data with booking_date support"""
        try:
            _logger.info(f"Getting state data from {start_date} to {end_date}")
            
            sale_order = self.env['sale.order']
            date_field = 'booking_date' if hasattr(sale_order, 'booking_date') else 'date_order'
            
            # Base domain
            base_domain = [
                (date_field, '>=', start_date),
                (date_field, '<=', end_date),
                ('state', '!=', 'cancel')
            ]
            
            # Add sale type filter if provided
            if sale_type_ids and hasattr(sale_order, 'sale_order_type_id'):
                base_domain.append(('sale_order_type_id', 'in', sale_type_ids))
            
            # Count by state
            draft_count = sale_order.search_count(base_domain + [('state', 'in', ['draft', 'sent'])])
            sale_count = sale_order.search_count(base_domain + [('state', '=', 'sale')])
            done_count = sale_order.search_count(base_domain + [('state', '=', 'done')])
            
            result = {
                'labels': ['Draft', 'Sale', 'Done'],
                'counts': [draft_count, sale_count, done_count]
            }
            
            _logger.info(f"State data result: {result}")
            return result
            
        except Exception as e:
            _logger.error(f"Error getting state data: {e}")
            return {
                'labels': ['Draft', 'Sale', 'Done'],
                'counts': [0, 0, 0]
            }

    @api.model
    def get_top_customers_data(self, start_date, end_date, sale_type_ids=None, limit=10):
        """Get top customers data with booking_date and sale type support"""
        try:
            _logger.info(f"Getting customers data from {start_date} to {end_date}")
            
            sale_order = self.env['sale.order']
            date_field = 'booking_date' if hasattr(sale_order, 'booking_date') else 'date_order'
            
            # Base domain
            base_domain = [
                (date_field, '>=', start_date),
                (date_field, '<=', end_date),
                ('state', '!=', 'cancel'),
                ('partner_id', '!=', False)
            ]
            
            # Add sale type filter if provided
            if sale_type_ids and hasattr(sale_order, 'sale_order_type_id'):
                base_domain.append(('sale_order_type_id', 'in', sale_type_ids))
            
            orders = sale_order.search(base_domain)
            
            # Group by customer
            customer_totals = defaultdict(float)
            for order in orders:
                customer_totals[order.partner_id.name] += order.amount_total
            
            # Sort and limit
            sorted_customers = sorted(customer_totals.items(), key=lambda x: x[1], reverse=True)[:limit]
            
            result = {
                'labels': [customer[0] for customer in sorted_customers],
                'amounts': [customer[1] for customer in sorted_customers]
            }
            
            _logger.info(f"Customers data result: {len(result['labels'])} customers")
            return result
            
        except Exception as e:
            _logger.error(f"Error getting customers data: {e}")
            return {
                'labels': [],
                'amounts': []
            }

    @api.model
    def get_sales_team_performance(self, start_date, end_date, sale_type_ids=None):
        """Get sales team performance data with booking_date and sale type support"""
        try:
            _logger.info(f"Getting team data from {start_date} to {end_date}")
            
            sale_order = self.env['sale.order']
            date_field = 'booking_date' if hasattr(sale_order, 'booking_date') else 'date_order'
            
            # Base domain
            base_domain = [
                (date_field, '>=', start_date),
                (date_field, '<=', end_date),
                ('state', '!=', 'cancel')
            ]
            
            # Add sale type filter if provided
            if sale_type_ids and hasattr(sale_order, 'sale_order_type_id'):
                base_domain.append(('sale_order_type_id', 'in', sale_type_ids))
            
            orders = sale_order.search(base_domain)
            
            # Group by team or user
            team_totals = defaultdict(float)
            for order in orders:
                team_name = 'Unassigned'
                if hasattr(order, 'team_id') and order.team_id:
                    team_name = order.team_id.name
                elif order.user_id:
                    team_name = order.user_id.name
                    
                team_totals[team_name] += order.amount_total
            
            # Sort by performance
            sorted_teams = sorted(team_totals.items(), key=lambda x: x[1], reverse=True)
            
            result = {
                'labels': [team[0] for team in sorted_teams],
                'amounts': [team[1] for team in sorted_teams]
            }
            
            _logger.info(f"Team data result: {len(result['labels'])} teams")
            return result
            
        except Exception as e:
            _logger.error(f"Error getting team data: {e}")
            return {
                'labels': ['Unassigned'],
                'amounts': [0]
            }

    @api.model
    def get_predefined_date_ranges(self):
        """Get predefined date ranges for quick filtering"""
        today = datetime.now().date()
        
        # Last 30 days
        last_30_start = today - timedelta(days=30)
        last_30_end = today
        
        # Last 90 days
        last_90_start = today - timedelta(days=90)
        last_90_end = today
        
        # Last year (current year)
        last_year_start = today.replace(month=1, day=1)
        last_year_end = today
        
        # Current quarter
        current_quarter = (today.month - 1) // 3 + 1
        quarter_start_month = (current_quarter - 1) * 3 + 1
        current_quarter_start = today.replace(month=quarter_start_month, day=1)
        current_quarter_end = today
        
        # Previous quarter
        if current_quarter == 1:
            prev_quarter_start = today.replace(year=today.year-1, month=10, day=1)
            prev_quarter_end = today.replace(year=today.year-1, month=12, day=31)
        else:
            prev_quarter_month = (current_quarter - 2) * 3 + 1
            prev_quarter_start = today.replace(month=prev_quarter_month, day=1)
            if current_quarter == 2:
                prev_quarter_end = today.replace(month=3, day=31)
            elif current_quarter == 3:
                prev_quarter_end = today.replace(month=6, day=30)
            else:
                prev_quarter_end = today.replace(month=9, day=30)
        
        return {
            'last_30_days': {
                'name': 'Last 30 Days',
                'start_date': last_30_start.strftime('%Y-%m-%d'),
                'end_date': last_30_end.strftime('%Y-%m-%d')
            },
            'last_90_days': {
                'name': 'Last 90 Days', 
                'start_date': last_90_start.strftime('%Y-%m-%d'),
                'end_date': last_90_end.strftime('%Y-%m-%d')
            },
            'last_year': {
                'name': 'This Year',
                'start_date': last_year_start.strftime('%Y-%m-%d'),
                'end_date': last_year_end.strftime('%Y-%m-%d')
            },
            'current_quarter': {
                'name': f'Q{current_quarter} {today.year}',
                'start_date': current_quarter_start.strftime('%Y-%m-%d'),
                'end_date': current_quarter_end.strftime('%Y-%m-%d')
            },
            'previous_quarter': {
                'name': f'Q{current_quarter-1 if current_quarter > 1 else 4} {today.year if current_quarter > 1 else today.year-1}',
                'start_date': prev_quarter_start.strftime('%Y-%m-%d'),
                'end_date': prev_quarter_end.strftime('%Y-%m-%d')
            }
        }

    @api.model
    def get_comprehensive_dashboard_data(self, start_date, end_date, sale_type_ids=None):
        """Get comprehensive dashboard data with all charts and metrics"""
        try:
            _logger.info(f"Getting comprehensive dashboard data from {start_date} to {end_date}")
            
            # Get all individual data components
            performance_data = self.get_sales_performance_data(start_date, end_date, sale_type_ids)
            monthly_data = self.get_monthly_fluctuation_data(start_date, end_date, sale_type_ids)
            state_data = self.get_sales_by_state_data(start_date, end_date, sale_type_ids)
            customers_data = self.get_top_customers_data(start_date, end_date, sale_type_ids)
            team_data = self.get_sales_team_performance(start_date, end_date, sale_type_ids)
            agent_data = self.get_agent_ranking_data(start_date, end_date, sale_type_ids)
            broker_data = self.get_broker_ranking_data(start_date, end_date, sale_type_ids)
            recent_orders = self.get_recent_orders_data(start_date, end_date, sale_type_ids)
            sale_type_options = self.get_sale_type_options()
            predefined_ranges = self.get_predefined_date_ranges()
            
            result = {
                'performance': performance_data,
                'monthly_trend': monthly_data,
                'sales_by_state': state_data,
                'top_customers': customers_data,
                'team_performance': team_data,
                'agent_ranking': agent_data,
                'broker_ranking': broker_data,
                'recent_orders': recent_orders,
                'sale_type_options': sale_type_options,
                'predefined_ranges': predefined_ranges,
                'date_range': {
                    'start_date': start_date,
                    'end_date': end_date
                }
            }
            
            _logger.info(f"Comprehensive dashboard data compiled successfully")
            return result
            
        except Exception as e:
            _logger.error(f"Error getting comprehensive dashboard data: {e}")
            return {
                'performance': {},
                'monthly_trend': [],
                'sales_by_state': {},
                'top_customers': {},
                'team_performance': {},
                'agent_ranking': {},
                'broker_ranking': {},
                'recent_orders': [],
                'sale_type_options': [],
                'predefined_ranges': {},
                'date_range': {'start_date': start_date, 'end_date': end_date}
            }

    @api.model
    def get_agent_ranking_data(self, start_date, end_date, sale_type_ids=None, limit=10):
        """Get agent1_partner_id ranking based on deal count, price_unit and amount_total"""
        try:
            _logger.info(f"Getting agent ranking from {start_date} to {end_date}")
            
            sale_order = self.env['sale.order']
            date_field = 'booking_date' if hasattr(sale_order, 'booking_date') else 'date_order'
            
            # Base domain
            base_domain = [
                (date_field, '>=', start_date),
                (date_field, '<=', end_date),
                ('state', '!=', 'cancel'),
                ('agent1_partner_id', '!=', False)
            ]
            
            # Add sale type filter if provided
            if sale_type_ids and hasattr(sale_order, 'sale_order_type_id'):
                base_domain.append(('sale_order_type_id', 'in', sale_type_ids))
            
            orders = sale_order.search(base_domain)
            
            # Group by agent
            agent_stats = defaultdict(lambda: {
                'deal_count': 0,
                'total_amount': 0,
                'avg_price_unit': 0,
                'name': 'Unknown Agent'
            })
            
            for order in orders:
                agent = order.agent1_partner_id
                agent_id = agent.id
                agent_stats[agent_id]['name'] = agent.name
                agent_stats[agent_id]['deal_count'] += 1
                agent_stats[agent_id]['total_amount'] += order.amount_total
                
                # Calculate average price unit from order lines
                if order.order_line:
                    total_price_unit = sum(line.price_unit for line in order.order_line)
                    avg_price = total_price_unit / len(order.order_line) if order.order_line else 0
                    current_avg = agent_stats[agent_id]['avg_price_unit']
                    deal_count = agent_stats[agent_id]['deal_count']
                    agent_stats[agent_id]['avg_price_unit'] = ((current_avg * (deal_count - 1)) + avg_price) / deal_count
            
            # Sort by total amount (primary), then deal count
            sorted_agents = sorted(
                agent_stats.items(), 
                key=lambda x: (x[1]['total_amount'], x[1]['deal_count']), 
                reverse=True
            )[:limit]
            
            result = {
                'agents': [],
                'deal_counts': [],
                'total_amounts': [],
                'avg_price_units': []
            }
            
            for agent_id, stats in sorted_agents:
                result['agents'].append(stats['name'])
                result['deal_counts'].append(stats['deal_count'])
                result['total_amounts'].append(stats['total_amount'])
                result['avg_price_units'].append(stats['avg_price_unit'])
            
            _logger.info(f"Agent ranking result: {len(result['agents'])} agents")
            return result
            
        except Exception as e:
            _logger.error(f"Error getting agent ranking: {e}")
            return {
                'agents': [],
                'deal_counts': [],
                'total_amounts': [],
                'avg_price_units': []
            }

    @api.model
    def get_broker_ranking_data(self, start_date, end_date, sale_type_ids=None, limit=10):
        """Get broker_partner_id ranking based on deal count, price_unit and amount_total"""
        try:
            _logger.info(f"Getting broker ranking from {start_date} to {end_date}")
            
            sale_order = self.env['sale.order']
            date_field = 'booking_date' if hasattr(sale_order, 'booking_date') else 'date_order'
            
            # Base domain
            base_domain = [
                (date_field, '>=', start_date),
                (date_field, '<=', end_date),
                ('state', '!=', 'cancel'),
                ('broker_partner_id', '!=', False)
            ]
            
            # Add sale type filter if provided
            if sale_type_ids and hasattr(sale_order, 'sale_order_type_id'):
                base_domain.append(('sale_order_type_id', 'in', sale_type_ids))
            
            orders = sale_order.search(base_domain)
            
            # Group by broker
            broker_stats = defaultdict(lambda: {
                'deal_count': 0,
                'total_amount': 0,
                'avg_price_unit': 0,
                'name': 'Unknown Broker'
            })
            
            for order in orders:
                broker = order.broker_partner_id
                broker_id = broker.id
                broker_stats[broker_id]['name'] = broker.name
                broker_stats[broker_id]['deal_count'] += 1
                broker_stats[broker_id]['total_amount'] += order.amount_total
                
                # Calculate average price unit from order lines
                if order.order_line:
                    total_price_unit = sum(line.price_unit for line in order.order_line)
                    avg_price = total_price_unit / len(order.order_line) if order.order_line else 0
                    current_avg = broker_stats[broker_id]['avg_price_unit']
                    deal_count = broker_stats[broker_id]['deal_count']
                    broker_stats[broker_id]['avg_price_unit'] = ((current_avg * (deal_count - 1)) + avg_price) / deal_count
            
            # Sort by total amount (primary), then deal count
            sorted_brokers = sorted(
                broker_stats.items(), 
                key=lambda x: (x[1]['total_amount'], x[1]['deal_count']), 
                reverse=True
            )[:limit]
            
            result = {
                'brokers': [],
                'deal_counts': [],
                'total_amounts': [],
                'avg_price_units': []
            }
            
            for broker_id, stats in sorted_brokers:
                result['brokers'].append(stats['name'])
                result['deal_counts'].append(stats['deal_count'])
                result['total_amounts'].append(stats['total_amount'])
                result['avg_price_units'].append(stats['avg_price_unit'])
            
            _logger.info(f"Broker ranking result: {len(result['brokers'])} brokers")
            return result
            
        except Exception as e:
            _logger.error(f"Error getting broker ranking: {e}")
            return {
                'brokers': [],
                'deal_counts': [],
                'total_amounts': [],
                'avg_price_units': []
            }

    @api.model
    def get_recent_orders_data(self, start_date, end_date, sale_type_ids=None, limit=20):
        """Get recent orders with booking date, agent, broker and sale type information"""
        try:
            _logger.info(f"Getting recent orders from {start_date} to {end_date}")
            
            sale_order = self.env['sale.order']
            date_field = 'booking_date' if hasattr(sale_order, 'booking_date') else 'date_order'
            
            # Base domain
            base_domain = [
                (date_field, '>=', start_date),
                (date_field, '<=', end_date),
                ('state', '!=', 'cancel')
            ]
            
            # Add sale type filter if provided
            if sale_type_ids and hasattr(sale_order, 'sale_order_type_id'):
                base_domain.append(('sale_order_type_id', 'in', sale_type_ids))
            
            orders = sale_order.search(base_domain, order=f'{date_field} desc', limit=limit)
            
            result = []
            for order in orders:
                order_data = {
                    'name': order.name,
                    'partner_name': order.partner_id.name if order.partner_id else 'N/A',
                    'booking_date': getattr(order, date_field).strftime('%Y-%m-%d') if getattr(order, date_field) else 'N/A',
                    'amount_total': order.amount_total,
                    'state': order.state,
                    'agent_name': order.agent1_partner_id.name if hasattr(order, 'agent1_partner_id') and order.agent1_partner_id else 'N/A',
                    'broker_name': order.broker_partner_id.name if hasattr(order, 'broker_partner_id') and order.broker_partner_id else 'N/A',
                    'sale_type': order.sale_order_type_id.name if hasattr(order, 'sale_order_type_id') and order.sale_order_type_id else 'N/A'
                }
                result.append(order_data)
            
            _logger.info(f"Recent orders result: {len(result)} orders")
            return result
            
        except Exception as e:
            _logger.error(f"Error getting recent orders: {e}")
            return []
>>>>>>> Stashed changes
