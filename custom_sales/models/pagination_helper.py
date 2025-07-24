# -*- coding: utf-8 -*-

from odoo import models, fields, api
import math
import logging

_logger = logging.getLogger(__name__)

class CustomSalesPagination(models.TransientModel):
    _name = 'custom.sales.pagination'
    _description = 'Pagination Helper for Large Datasets'
    
    @api.model
    def paginate_records(self, model_name, domain=None, page=1, page_size=50, order=None):
        """Generic pagination method for any model"""
        if domain is None:
            domain = []
        
        if page < 1:
            page = 1
        
        if page_size < 1 or page_size > 1000:  # Limit maximum page size
            page_size = 50
        
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Get model
        model = self.env[model_name]
        
        # Get total count
        total_count = model.search_count(domain)
        
        # Calculate pagination info
        total_pages = math.ceil(total_count / page_size) if total_count > 0 else 1
        has_previous = page > 1
        has_next = page < total_pages
        
        # Get records for current page
        records = model.search(
            domain, 
            limit=page_size, 
            offset=offset,
            order=order or 'create_date desc'
        )
        
        return {
            'records': records,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_count': total_count,
                'total_pages': total_pages,
                'has_previous': has_previous,
                'has_next': has_next,
                'start_index': offset + 1 if total_count > 0 else 0,
                'end_index': min(offset + page_size, total_count),
            }
        }
    
    @api.model
    def get_paginated_sales_orders(self, domain=None, page=1, page_size=20, 
                                  date_from=None, date_to=None, search_term=None):
        """Get paginated sales orders with filters"""
        if domain is None:
            domain = []
        
        # Add date filters
        if date_from and date_to:
            domain.extend([
                ('create_date', '>=', date_from),
                ('create_date', '<=', date_to)
            ])
        
        # Add search filter
        if search_term:
            domain.extend([
                '|', '|', '|',
                ('name', 'ilike', search_term),
                ('custom_field_1', 'ilike', search_term),
                ('custom_field_3.name', 'ilike', search_term),
                ('sales_person_id.name', 'ilike', search_term)
            ])
        
        return self.paginate_records(
            'custom.sales.order',
            domain=domain,
            page=page,
            page_size=page_size,
            order='create_date desc'
        )
    
    @api.model
    def get_paginated_dashboard_data(self, dashboard_config, page=1, page_size=10):
        """Get paginated dashboard data for tables"""
        domain = []
        
        # Apply dashboard filters if any
        if hasattr(dashboard_config, 'default_date_filter'):
            # Add default date filters based on config
            pass
        
        result = self.get_paginated_sales_orders(domain, page, page_size)
        
        # Convert records to dict for JSON response
        records_data = []
        for record in result['records']:
            records_data.append({
                'id': record.id,
                'name': record.name,
                'create_date': record.create_date.strftime('%Y-%m-%d %H:%M:%S') if record.create_date else '',
                'state': record.state,
                'customer_name': record.custom_field_3.name if record.custom_field_3 else '',
                'sales_person': record.sales_person_id.name if record.sales_person_id else '',
                'actual_revenue': record.actual_revenue or 0,
                'customer_type': record.customer_type or '',
                'priority': record.priority or '1',
            })
        
        return {
            'data': records_data,
            'pagination': result['pagination']
        }
