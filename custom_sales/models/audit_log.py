# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class CustomSalesAuditLog(models.Model):
    _name = 'custom.sales.audit.log'
    _description = 'Sales Module Audit Log'
    _order = 'create_date desc'
    _rec_name = 'action_type'
    
    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=True,
        index=True,
        default=lambda self: self.env.user
    )
    
    action_type = fields.Selection([
        ('view_dashboard', 'View Dashboard'),
        ('export_report', 'Export Report'),
        ('create_order', 'Create Sales Order'),
        ('update_order', 'Update Sales Order'),
        ('delete_order', 'Delete Sales Order'),
        ('config_dashboard', 'Configure Dashboard'),
        ('access_denied', 'Access Denied'),
        ('security_violation', 'Security Violation'),
        ('data_export', 'Data Export'),
        ('login_attempt', 'Login Attempt'),
    ], string='Action Type', required=True, index=True)
    
    resource_model = fields.Char(
        string='Resource Model',
        help='Model name that was accessed'
    )
    
    resource_id = fields.Integer(
        string='Resource ID',
        help='ID of the record that was accessed'
    )
    
    ip_address = fields.Char(
        string='IP Address',
        help='Client IP address'
    )
    
    user_agent = fields.Text(
        string='User Agent',
        help='Browser user agent string'
    )
    
    request_data = fields.Text(
        string='Request Data',
        help='JSON data of the request parameters'
    )
    
    response_status = fields.Char(
        string='Response Status',
        help='HTTP response status'
    )
    
    details = fields.Text(
        string='Details',
        help='Additional details about the action'
    )
    
    session_id = fields.Char(
        string='Session ID',
        help='User session identifier'
    )
    
    success = fields.Boolean(
        string='Success',
        default=True,
        help='Whether the action was successful'
    )
    
    risk_level = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ], string='Risk Level', default='low', index=True)
    
    @api.model
    def log_action(self, action_type, resource_model=None, resource_id=None, 
                   details=None, success=True, risk_level='low', **kwargs):
        """Log an audit action"""
        try:
            # Get request information
            from odoo.http import request
            
            data = {
                'action_type': action_type,
                'resource_model': resource_model,
                'resource_id': resource_id,
                'details': details,
                'success': success,
                'risk_level': risk_level,
            }
            
            if request:
                data.update({
                    'ip_address': request.httprequest.environ.get('REMOTE_ADDR'),
                    'user_agent': request.httprequest.environ.get('HTTP_USER_AGENT'),
                    'session_id': request.session.sid if hasattr(request.session, 'sid') else None,
                })
                
                # Add request data (sanitized)
                if hasattr(request, 'jsonrequest') and request.jsonrequest:
                    import json
                    # Remove sensitive data
                    safe_data = {k: v for k, v in request.jsonrequest.items() 
                               if k not in ['password', 'token', 'session']}
                    data['request_data'] = json.dumps(safe_data)
            
            # Create audit log
            self.create(data)
            
        except Exception as e:
            # Don't let audit logging break the main functionality
            _logger.error(f"Failed to create audit log: {e}")
    
    @api.model
    def get_security_summary(self, days=30):
        """Get security summary for the last N days"""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        domain = [('create_date', '>=', cutoff_date)]
        
        # Count by action type
        action_counts = {}
        logs = self.search(domain)
        
        for log in logs:
            action_type = log.action_type
            if action_type not in action_counts:
                action_counts[action_type] = {'total': 0, 'failed': 0, 'high_risk': 0}
            
            action_counts[action_type]['total'] += 1
            
            if not log.success:
                action_counts[action_type]['failed'] += 1
            
            if log.risk_level in ['high', 'critical']:
                action_counts[action_type]['high_risk'] += 1
        
        # Get top users by activity
        user_activity = {}
        for log in logs:
            user_name = log.user_id.name
            if user_name not in user_activity:
                user_activity[user_name] = 0
            user_activity[user_name] += 1
        
        # Sort by activity
        top_users = sorted(user_activity.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'total_actions': len(logs),
            'failed_actions': len(logs.filtered(lambda x: not x.success)),
            'high_risk_actions': len(logs.filtered(lambda x: x.risk_level in ['high', 'critical'])),
            'action_breakdown': action_counts,
            'top_users': top_users,
            'period_days': days,
        }
    
    @api.model
    def cleanup_old_logs(self, days_to_keep=90):
        """Clean up old audit logs"""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        old_logs = self.search([('create_date', '<', cutoff_date)])
        
        if old_logs:
            count = len(old_logs)
            old_logs.unlink()
            _logger.info(f"Cleaned up {count} old audit logs")
            return count
        
        return 0


class CustomSalesOrderAudit(models.Model):
    _inherit = 'custom.sales.order'
    
    @api.model
    def create(self, vals):
        """Override create to add audit logging"""
        result = super().create(vals)
        
        # Log the creation
        self.env['custom.sales.audit.log'].log_action(
            'create_order',
            resource_model=self._name,
            resource_id=result.id,
            details=f"Created sales order: {result.name}",
            risk_level='low'
        )
        
        return result
    
    def write(self, vals):
        """Override write to add audit logging"""
        # Log sensitive field changes
        sensitive_fields = ['state', 'actual_revenue', 'sales_person_id']
        
        for record in self:
            old_values = {field: getattr(record, field) for field in sensitive_fields if field in vals}
            
            result = super(CustomSalesOrderAudit, record).write(vals)
            
            if any(field in vals for field in sensitive_fields):
                details = f"Updated sales order: {record.name}. Changed fields: {list(vals.keys())}"
                
                self.env['custom.sales.audit.log'].log_action(
                    'update_order',
                    resource_model=self._name,
                    resource_id=record.id,
                    details=details,
                    risk_level='medium' if 'actual_revenue' in vals else 'low'
                )
        
        return super().write(vals)
    
    def unlink(self):
        """Override unlink to add audit logging"""
        for record in self:
            self.env['custom.sales.audit.log'].log_action(
                'delete_order',
                resource_model=self._name,
                resource_id=record.id,
                details=f"Deleted sales order: {record.name}",
                risk_level='high'
            )
        
        return super().unlink()
