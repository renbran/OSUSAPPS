# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
import json
import logging
import time

_logger = logging.getLogger(__name__)

class CustomSalesDashboardController(http.Controller):
    
    @http.route('/custom_sales/dashboard', type='http', auth='user', website=True, csrf=True)
    def dashboard_view(self, **kwargs):
        """Main dashboard view"""
        try:
            # Log dashboard access
            request.env['custom.sales.audit.log'].log_action(
                'view_dashboard',
                details='Accessed main dashboard view'
            )
            
            # Get user's dashboard configuration
            dashboard_config = request.env['custom.sales.dashboard.config'].get_user_dashboard()
            
            if not dashboard_config:
                return request.render('custom_sales.dashboard_no_config')
            
            # Get dashboard data
            dashboard_data = self._get_dashboard_data(dashboard_config)
            
            return request.render('custom_sales.dashboard_main', {
                'dashboard_config': dashboard_config,
                'dashboard_data': dashboard_data,
            })
        
        except Exception as e:
            _logger.error(f"Error rendering dashboard: {e}")
            
            # Log the error
            request.env['custom.sales.audit.log'].log_action(
                'view_dashboard',
                details=f'Dashboard view error: {str(e)}',
                success=False,
                risk_level='medium'
            )
            
            return request.render('custom_sales.dashboard_error', {
                'error_message': str(e)
            })
    
    @http.route('/custom_sales/api/dashboard_data', type='json', auth='user', methods=['POST'], csrf=True)
    def get_dashboard_data(self, dashboard_id=None, date_from=None, date_to=None, **kwargs):
        """API endpoint to get dashboard data"""
        try:
            # Validate user access
            if not request.env.user.has_group('custom_sales.group_sales_dashboard_user'):
                return {'error': 'Access denied', 'code': 403}
            
            # Input validation
            if dashboard_id:
                try:
                    dashboard_id = int(dashboard_id)
                    if dashboard_id <= 0:
                        return {'error': 'Invalid dashboard ID', 'code': 400}
                except (ValueError, TypeError):
                    return {'error': 'Dashboard ID must be a valid integer', 'code': 400}
            
            # Date validation
            if date_from:
                try:
                    from datetime import datetime
                    datetime.strptime(date_from, '%Y-%m-%d')
                except ValueError:
                    return {'error': 'Invalid date_from format. Use YYYY-MM-DD', 'code': 400}
            
            if date_to:
                try:
                    from datetime import datetime
                    datetime.strptime(date_to, '%Y-%m-%d')
                except ValueError:
                    return {'error': 'Invalid date_to format. Use YYYY-MM-DD', 'code': 400}
            
            # Get dashboard configuration
            if dashboard_id:
                dashboard_config = request.env['custom.sales.dashboard.config'].browse(dashboard_id)
                # Check if user has access to this specific dashboard
                if not dashboard_config.exists() or not self._check_dashboard_access(dashboard_config):
                    return {'error': 'Dashboard configuration not found or access denied', 'code': 404}
            else:
                dashboard_config = request.env['custom.sales.dashboard.config'].get_user_dashboard()
            
            if not dashboard_config or not dashboard_config.exists():
                return {'error': 'Dashboard configuration not found', 'code': 404}
            
            # Get dashboard data
            data = self._get_dashboard_data(dashboard_config, date_from, date_to)
            
            return {
                'success': True,
                'data': data,
                'config': {
                    'name': dashboard_config.name,
                    'refresh_interval': dashboard_config.refresh_interval,
                    'auto_refresh': dashboard_config.auto_refresh,
                    'primary_color': dashboard_config.primary_color,
                    'secondary_color': dashboard_config.secondary_color,
                    'accent_color': dashboard_config.accent_color,
                }
            }
        
        except Exception as e:
            _logger.error(f"Error getting dashboard data: {e}")
            return {'error': str(e)}
    
    @http.route('/custom_sales/api/kpis', type='json', auth='user', methods=['POST'])
    def get_kpis(self, dashboard_id=None, date_from=None, date_to=None, **kwargs):
        """Get KPI data for dashboard"""
        try:
            kpi_calculator = request.env['sales.kpi.calculator']
            kpis = kpi_calculator.get_dashboard_kpis(dashboard_id, date_from, date_to)
            
            return {
                'success': True,
                'kpis': kpis
            }
        
        except Exception as e:
            _logger.error(f"Error getting KPIs: {e}")
            return {'error': str(e)}
    
    @http.route('/custom_sales/api/charts', type='json', auth='user', methods=['POST'])
    def get_charts(self, dashboard_id=None, date_from=None, date_to=None, **kwargs):
        """Get chart data for dashboard"""
        try:
            # Get dashboard configuration
            if dashboard_id:
                dashboard_config = request.env['custom.sales.dashboard.config'].browse(dashboard_id)
            else:
                dashboard_config = request.env['custom.sales.dashboard.config'].get_user_dashboard()
            
            if not dashboard_config:
                return {'error': 'Dashboard configuration not found'}
            
            chart_generator = request.env['sales.chart.generator']
            charts = []
            
            for chart_config in dashboard_config.chart_config_ids.filtered('is_active'):
                chart_data = chart_generator.generate_chart_data(
                    chart_config, date_from, date_to
                )
                
                charts.append({
                    'id': chart_config.id,
                    'name': chart_config.name,
                    'type': chart_config.chart_type,
                    'data': chart_data,
                    'options': self._get_chart_options(chart_config),
                    'width': chart_config.width,
                    'height': chart_config.height,
                })
            
            return {
                'success': True,
                'charts': charts
            }
        
        except Exception as e:
            _logger.error(f"Error getting charts: {e}")
            return {'error': str(e)}
    
    @http.route('/custom_sales/api/sales_overview', type='json', auth='user', methods=['POST'])
    def get_sales_overview(self, date_from=None, date_to=None, **kwargs):
        """Get sales overview data"""
        try:
            domain = []
            if date_from and date_to:
                domain.extend([
                    ('create_date', '>=', date_from),
                    ('create_date', '<=', date_to)
                ])
            
            # Get sales data
            sales_orders = request.env['custom.sales.order'].search(domain)
            
            # Calculate metrics
            total_orders = len(sales_orders)
            total_revenue = sum(sales_orders.mapped('actual_revenue'))
            avg_order_value = total_revenue / total_orders if total_orders else 0
            
            # Status breakdown
            status_data = {}
            for state in sales_orders.mapped('state'):
                status_data[state] = len(sales_orders.filtered(lambda x: x.state == state))
            
            # Customer type breakdown
            customer_type_data = {}
            for customer_type in sales_orders.mapped('customer_type'):
                if customer_type:
                    customer_type_data[customer_type] = len(
                        sales_orders.filtered(lambda x: x.customer_type == customer_type)
                    )
            
            # Sales team performance
            team_data = {}
            for team in sales_orders.mapped('sales_team_id'):
                if team:
                    team_orders = sales_orders.filtered(lambda x: x.sales_team_id == team)
                    team_data[team.name] = {
                        'orders': len(team_orders),
                        'revenue': sum(team_orders.mapped('actual_revenue')),
                    }
            
            return {
                'success': True,
                'data': {
                    'total_orders': total_orders,
                    'total_revenue': total_revenue,
                    'avg_order_value': avg_order_value,
                    'status_breakdown': status_data,
                    'customer_type_breakdown': customer_type_data,
                    'team_performance': team_data,
                }
            }
        
        except Exception as e:
            _logger.error(f"Error getting sales overview: {e}")
            return {'error': str(e)}
    
    @http.route('/custom_sales/report/export', type='http', auth='user', csrf=True)
    def export_report(self, format='pdf', date_from=None, date_to=None, **kwargs):
        """Export dashboard report"""
        try:
            # Rate limiting check
            if not self._check_rate_limit():
                return request.render('custom_sales.export_error', {
                    'error_message': 'Too many export requests. Please wait before trying again.'
                })
            
            # Validate parameters
            if format not in ['pdf', 'excel', 'csv']:
                return request.not_found()
            
            # Input validation and sanitization
            if date_from:
                try:
                    from datetime import datetime
                    datetime.strptime(date_from, '%Y-%m-%d')
                except ValueError:
                    return request.render('custom_sales.export_error', {
                        'error_message': 'Invalid date_from format. Use YYYY-MM-DD'
                    })
            
            if date_to:
                try:
                    from datetime import datetime
                    datetime.strptime(date_to, '%Y-%m-%d')
                except ValueError:
                    return request.render('custom_sales.export_error', {
                        'error_message': 'Invalid date_to format. Use YYYY-MM-DD'
                    })
            
            # Check user permissions for export
            if not request.env.user.has_group('custom_sales.group_sales_dashboard_user'):
                return request.render('custom_sales.export_error', {
                    'error_message': 'You do not have permission to export reports.'
                })
            
            # Get data
            dashboard_config = request.env['custom.sales.dashboard.config'].get_user_dashboard()
            if not dashboard_config:
                return request.render('custom_sales.export_error', {
                    'error_message': 'No dashboard configuration found.'
                })
                
            dashboard_data = self._get_dashboard_data(dashboard_config, date_from, date_to)
            
            if format == 'pdf':
                return self._export_pdf_report(dashboard_data, date_from, date_to)
            elif format == 'excel':
                return self._export_excel_report(dashboard_data, date_from, date_to)
            elif format == 'csv':
                return self._export_csv_report(dashboard_data, date_from, date_to)
        
        except Exception as e:
            _logger.error(f"Error exporting report: {e}")
            return request.render('custom_sales.export_error', {
                'error_message': str(e)
            })
    
    def _get_dashboard_data(self, dashboard_config, date_from=None, date_to=None):
        """Get comprehensive dashboard data"""
        data = {}
        
        # Get KPIs
        if dashboard_config.show_kpis:
            kpi_calculator = request.env['sales.kpi.calculator']
            data['kpis'] = kpi_calculator.get_dashboard_kpis(
                dashboard_config.id, date_from, date_to
            )
        
        # Get charts
        if dashboard_config.show_charts:
            chart_generator = request.env['sales.chart.generator']
            charts = []
            
            for chart_config in dashboard_config.chart_config_ids.filtered('is_active'):
                chart_data = chart_generator.generate_chart_data(
                    chart_config, date_from, date_to
                )
                
                charts.append({
                    'id': chart_config.id,
                    'name': chart_config.name,
                    'type': chart_config.chart_type,
                    'data': chart_data,
                    'options': self._get_chart_options(chart_config),
                })
            
            data['charts'] = charts
        
        # Get summary data
        data['summary'] = self._get_summary_data(date_from, date_to)
        
        return data
    
    def _get_chart_options(self, chart_config):
        """Get chart.js options for a chart configuration"""
        options = {
            'responsive': True,
            'maintainAspectRatio': False,
            'plugins': {
                'legend': {
                    'display': chart_config.show_legend,
                    'position': 'top',
                },
                'title': {
                    'display': True,
                    'text': chart_config.name,
                }
            },
            'scales': {}
        }
        
        # Add scales for bar/line charts
        if chart_config.chart_type in ['bar', 'line']:
            options['scales']['y'] = {
                'beginAtZero': True,
                'grid': {
                    'display': True,
                }
            }
            options['scales']['x'] = {
                'grid': {
                    'display': False,
                }
            }
        
        # Add colors from theme
        dashboard_config = chart_config.dashboard_config_id
        if dashboard_config:
            # Apply theme colors
            pass
        
        return options
    
    def _get_summary_data(self, date_from=None, date_to=None):
        """Get summary data for dashboard"""
        domain = []
        if date_from and date_to:
            domain.extend([
                ('create_date', '>=', date_from),
                ('create_date', '<=', date_to)
            ])
        
        sales_orders = request.env['custom.sales.order'].search(domain)
        
        return {
            'total_orders': len(sales_orders),
            'total_revenue': sum(sales_orders.mapped('actual_revenue')),
            'pending_orders': len(sales_orders.filtered(lambda x: x.state in ['draft', 'sent'])),
            'overdue_orders': len(sales_orders.filtered('is_overdue')),
        }
    
    def _export_pdf_report(self, data, date_from, date_to):
        """Export dashboard as PDF"""
        report = request.env.ref('custom_sales.action_report_dashboard')
        
        # Create temporary record for report context
        context = {
            'dashboard_data': data,
            'date_from': date_from,
            'date_to': date_to,
        }
        
        pdf_content, _ = report._render_qweb_pdf([], data=context)
        
        return request.make_response(
            pdf_content,
            headers=[
                ('Content-Type', 'application/pdf'),
                ('Content-Disposition', 'attachment; filename=sales_dashboard.pdf')
            ]
        )
    
    def _export_excel_report(self, data, date_from, date_to):
        """Export dashboard as Excel"""
        try:
            import xlsxwriter
            import io
            
            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output)
            
            # Add worksheets
            summary_sheet = workbook.add_worksheet('Summary')
            kpi_sheet = workbook.add_worksheet('KPIs')
            
            # Format styles
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#8B0000',
                'font_color': 'white',
            })
            
            # Write summary data
            if 'summary' in data:
                summary_sheet.write('A1', 'Metric', header_format)
                summary_sheet.write('B1', 'Value', header_format)
                
                row = 1
                for key, value in data['summary'].items():
                    summary_sheet.write(row, 0, key.replace('_', ' ').title())
                    summary_sheet.write(row, 1, value)
                    row += 1
            
            # Write KPI data
            if 'kpis' in data:
                kpi_sheet.write('A1', 'KPI Name', header_format)
                kpi_sheet.write('B1', 'Value', header_format)
                kpi_sheet.write('C1', 'Format', header_format)
                
                row = 1
                for kpi in data['kpis']:
                    kpi_sheet.write(row, 0, kpi['name'])
                    kpi_sheet.write(row, 1, kpi['value'])
                    kpi_sheet.write(row, 2, kpi['format_type'])
                    row += 1
            
            workbook.close()
            output.seek(0)
            
            return request.make_response(
                output.getvalue(),
                headers=[
                    ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                    ('Content-Disposition', 'attachment; filename=sales_dashboard.xlsx')
                ]
            )
        
        except ImportError:
            return request.render('custom_sales.export_error', {
                'error_message': 'Excel export requires xlsxwriter package'
            })
    
    def _export_csv_report(self, data, date_from, date_to):
        """Export dashboard as CSV"""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Report Type', 'Sales Dashboard Export'])
        writer.writerow(['Date From', date_from or 'All time'])
        writer.writerow(['Date To', date_to or 'Now'])
        writer.writerow([])
        
        # Write KPIs
        if 'kpis' in data:
            writer.writerow(['KPI Name', 'Value', 'Format'])
            for kpi in data['kpis']:
                writer.writerow([kpi['name'], kpi['value'], kpi['format_type']])
            writer.writerow([])
        
        # Write summary
        if 'summary' in data:
            writer.writerow(['Summary Metric', 'Value'])
            for key, value in data['summary'].items():
                writer.writerow([key.replace('_', ' ').title(), value])
        
        output.seek(0)
        
        return request.make_response(
            output.getvalue(),
            headers=[
                ('Content-Type', 'text/csv'),
                ('Content-Disposition', 'attachment; filename=sales_dashboard.csv')
            ]
        )
    
    @http.route('/custom_sales/api/sales_data_paginated', type='json', auth='user', methods=['POST'], csrf=True)
    def get_sales_data_paginated(self, page=1, page_size=20, date_from=None, date_to=None, 
                                search_term=None, filters=None, **kwargs):
        """Get paginated sales data with filters"""
        try:
            # Validate user access
            if not request.env.user.has_group('custom_sales.group_sales_dashboard_user'):
                return {'error': 'Access denied', 'code': 403}
            
            # Input validation
            page = self._sanitize_input(page, 'integer') or 1
            page_size = self._sanitize_input(page_size, 'integer') or 20
            
            # Limit page size for performance
            if page_size > 100:
                page_size = 100
            
            # Validate dates
            date_from = self._sanitize_input(date_from, 'date')
            date_to = self._sanitize_input(date_to, 'date')
            search_term = self._sanitize_input(search_term, 'string')
            
            # Get paginated data
            pagination_helper = request.env['custom.sales.pagination']
            result = pagination_helper.get_paginated_sales_orders(
                page=page,
                page_size=page_size,
                date_from=date_from,
                date_to=date_to,
                search_term=search_term
            )
            
            return {
                'success': True,
                'data': result['data'],
                'pagination': result['pagination']
            }
            
        except Exception as e:
            _logger.error(f"Error getting paginated sales data: {e}")
            return {'error': str(e), 'code': 500}
    
    @http.route('/custom_sales/api/kpis_cached', type='json', auth='user', methods=['POST'], csrf=True)
    def get_kpis_cached(self, dashboard_id=None, date_from=None, date_to=None, **kwargs):
        """Get KPI data with caching"""
        try:
            # Validate user access
            if not request.env.user.has_group('custom_sales.group_sales_dashboard_user'):
                return {'error': 'Access denied', 'code': 403}
            
            # Create cache key
            cache_key = f"kpis_{dashboard_id}_{date_from}_{date_to}_{request.env.user.id}"
            
            # Get cached data
            optimizer = request.env['custom.sales.performance.optimizer']
            
            def calculate_kpis():
                kpi_calculator = request.env['sales.kpi.calculator']
                return kpi_calculator.get_dashboard_kpis(dashboard_id, date_from, date_to)
            
            kpis = optimizer.get_cached_kpi_data(cache_key, calculate_kpis)
            
            return {
                'success': True,
                'kpis': kpis,
                'cached': True
            }
        
        except Exception as e:
            _logger.error(f"Error getting cached KPIs: {e}")
            return {'error': str(e), 'code': 500}
    
    def _check_dashboard_access(self, dashboard_config):
        """Check if user has access to specific dashboard"""
        # Basic access check - can be extended with more complex rules
        if request.env.user.has_group('custom_sales.group_sales_dashboard_admin'):
            return True
        
        # Check if dashboard is public or user-specific
        if dashboard_config.is_default:
            return True
        
        # Add more specific access rules here
        return dashboard_config.create_uid == request.env.user
    
    def _check_rate_limit(self):
        """Simple rate limiting for export operations"""
        # Basic implementation - can be enhanced with Redis or database storage
        session = request.session
        current_time = time.time()
        
        # Allow 5 exports per 5 minutes
        rate_limit_key = 'export_rate_limit'
        rate_limit_data = session.get(rate_limit_key, [])
        
        # Clean old entries
        rate_limit_data = [timestamp for timestamp in rate_limit_data if current_time - timestamp < 300]
        
        if len(rate_limit_data) >= 5:
            return False
        
        rate_limit_data.append(current_time)
        session[rate_limit_key] = rate_limit_data
        
        return True
    
    def _sanitize_input(self, value, input_type='string'):
        """Sanitize user input to prevent injection attacks"""
        if not value:
            return value
        
        if input_type == 'string':
            # Remove potentially dangerous characters
            import re
            return re.sub(r'[<>&"\']', '', str(value))
        elif input_type == 'integer':
            try:
                return int(value)
            except (ValueError, TypeError):
                return None
        elif input_type == 'date':
            try:
                from datetime import datetime
                datetime.strptime(value, '%Y-%m-%d')
                return value
            except ValueError:
                return None
        
        return value
