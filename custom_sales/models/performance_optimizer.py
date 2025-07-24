# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools
from odoo.tools import config
import logging
import time
from functools import lru_cache

_logger = logging.getLogger(__name__)

class CustomSalesPerformanceOptimizer(models.TransientModel):
    _name = 'custom.sales.performance.optimizer'
    _description = 'Performance Optimization Helper'
    
    @api.model
    def optimize_database_indexes(self):
        """Add custom database indexes for better performance"""
        cr = self.env.cr
        
        # Check and create indexes
        indexes_to_create = [
            # Custom sales order indexes
            ('idx_custom_sales_order_date', 'custom_sales_order', 'create_date'),
            ('idx_custom_sales_order_state', 'custom_sales_order', 'state'),
            ('idx_custom_sales_order_customer_type', 'custom_sales_order', 'customer_type'),
            ('idx_custom_sales_order_priority', 'custom_sales_order', 'priority'),
            ('idx_custom_sales_order_team', 'custom_sales_order', 'sales_team_id'),
            ('idx_custom_sales_order_person', 'custom_sales_order', 'sales_person_id'),
            
            # Composite indexes for common queries
            ('idx_custom_sales_order_date_state', 'custom_sales_order', 'create_date, state'),
            ('idx_custom_sales_order_date_team', 'custom_sales_order', 'create_date, sales_team_id'),
        ]
        
        for index_name, table_name, columns in indexes_to_create:
            try:
                # Check if index exists
                cr.execute("""
                    SELECT 1 FROM pg_indexes 
                    WHERE tablename = %s AND indexname = %s
                """, (table_name, index_name))
                
                if not cr.fetchone():
                    # Create index
                    cr.execute(f"""
                        CREATE INDEX CONCURRENTLY IF NOT EXISTS {index_name} 
                        ON {table_name} ({columns})
                    """)
                    _logger.info(f"Created index {index_name} on {table_name}")
                    
            except Exception as e:
                _logger.warning(f"Could not create index {index_name}: {e}")
    
    @api.model
    def get_optimized_sales_data(self, domain=None, limit=None, order=None):
        """Get sales data with optimized query"""
        if domain is None:
            domain = []
        
        # Use read() instead of browse() for better performance
        fields_to_read = [
            'name', 'create_date', 'state', 'customer_type', 'priority',
            'sales_team_id', 'sales_person_id', 'actual_revenue', 'expected_revenue'
        ]
        
        # Add limit for large datasets
        if limit is None:
            limit = 1000  # Default limit
        
        return self.env['custom.sales.order'].search_read(
            domain, fields_to_read, limit=limit, order=order or 'create_date desc'
        )
    
    @api.model
    def get_cached_kpi_data(self, cache_key, calculation_func, *args, **kwargs):
        """Get KPI data with caching"""
        if not hasattr(self, '_kpi_cache'):
            self._kpi_cache = {}
        
        # Simple memory cache - can be replaced with Redis
        if cache_key in self._kpi_cache:
            cache_time, data = self._kpi_cache[cache_key]
            
            # Cache for 5 minutes
            if time.time() - cache_time < 300:
                return data
        
        # Calculate new data
        data = calculation_func(*args, **kwargs)
        self._kpi_cache[cache_key] = (time.time(), data)
        
        return data
    
    @api.model
    def cleanup_old_data(self, days_to_keep=365):
        """Archive or delete old data to improve performance"""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        # Find old records
        old_orders = self.env['custom.sales.order'].search([
            ('create_date', '<', cutoff_date),
            ('state', 'in', ['cancelled', 'done'])
        ])
        
        if old_orders:
            _logger.info(f"Found {len(old_orders)} old orders to archive")
            
            # Instead of deleting, mark as archived
            old_orders.write({'active': False})
            
        return len(old_orders)
    
    @api.model
    def vacuum_analyze_tables(self):
        """Run VACUUM ANALYZE on custom tables"""
        if not config.get('test_enable'):  # Don't run in test mode
            cr = self.env.cr
            
            tables_to_vacuum = [
                'custom_sales_order',
                'custom_sales_dashboard_config',
                'custom_sales_kpi_config',
                'custom_sales_chart_config',
            ]
            
            for table in tables_to_vacuum:
                try:
                    cr.execute(f"VACUUM ANALYZE {table}")
                    _logger.info(f"Vacuumed and analyzed table {table}")
                except Exception as e:
                    _logger.warning(f"Could not vacuum table {table}: {e}")


class CustomSalesOrderOptimized(models.Model):
    _inherit = 'custom.sales.order'
    
    @api.model
    def get_dashboard_summary(self, date_from=None, date_to=None):
        """Optimized method to get dashboard summary data"""
        domain = []
        if date_from and date_to:
            domain.extend([
                ('create_date', '>=', date_from),
                ('create_date', '<=', date_to)
            ])
        
        # Use SQL for better performance on large datasets
        cr = self.env.cr
        
        # Build WHERE clause
        where_clause = "WHERE active = true"
        params = []
        
        if date_from and date_to:
            where_clause += " AND create_date BETWEEN %s AND %s"
            params.extend([date_from, date_to])
        
        # Single query to get all summary data
        cr.execute(f"""
            SELECT 
                COUNT(*) as total_orders,
                COALESCE(SUM(actual_revenue), 0) as total_revenue,
                COALESCE(AVG(actual_revenue), 0) as avg_order_value,
                COUNT(CASE WHEN state IN ('draft', 'sent') THEN 1 END) as pending_orders,
                COUNT(CASE WHEN is_overdue = true THEN 1 END) as overdue_orders,
                COUNT(CASE WHEN customer_type = 'new' THEN 1 END) as new_customers,
                COUNT(CASE WHEN customer_type = 'existing' THEN 1 END) as existing_customers
            FROM custom_sales_order 
            {where_clause}
        """, params)
        
        result = cr.dictfetchone()
        
        return {
            'total_orders': result['total_orders'] or 0,
            'total_revenue': float(result['total_revenue'] or 0),
            'avg_order_value': float(result['avg_order_value'] or 0),
            'pending_orders': result['pending_orders'] or 0,
            'overdue_orders': result['overdue_orders'] or 0,
            'new_customers': result['new_customers'] or 0,
            'existing_customers': result['existing_customers'] or 0,
        }
    
    @api.model
    def get_monthly_trends(self, months=12):
        """Get monthly sales trends with optimized query"""
        cr = self.env.cr
        
        cr.execute("""
            SELECT 
                DATE_TRUNC('month', create_date) as month,
                COUNT(*) as orders_count,
                COALESCE(SUM(actual_revenue), 0) as revenue
            FROM custom_sales_order 
            WHERE active = true 
                AND create_date >= CURRENT_DATE - INTERVAL '%s months'
            GROUP BY DATE_TRUNC('month', create_date)
            ORDER BY month
        """, (months,))
        
        return cr.dictfetchall()
    
    @api.model
    @tools.ormcache('date_from', 'date_to')
    def get_cached_analytics(self, date_from=None, date_to=None):
        """Cached analytics data"""
        return self.get_dashboard_summary(date_from, date_to)
