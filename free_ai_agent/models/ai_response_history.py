# -*- coding: utf-8 -*-

import logging
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class AIResponseHistory(models.Model):
    _name = 'free.ai.response.history'
    _description = 'AI Response History'
    _order = 'id desc'
    _rec_name = 'display_name'

    agent_id = fields.Many2one('free.ai.agent', string='AI Agent', required=True, ondelete='cascade')
    
    # Execution details
    execution_type = fields.Selection([
        ('manual', 'Manual'),
        ('scheduled', 'Scheduled'),
        ('triggered', 'Triggered'),
    ], string='Execution Type', required=True)
    
    status = fields.Selection([
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], string='Status', default='draft')
    
    # Timing
    started_at = fields.Datetime('Started At', required=True, default=fields.Datetime.now)
    completed_at = fields.Datetime('Completed At')
    duration = fields.Float('Duration (seconds)', compute='_compute_duration', store=True)
    
    # AI Response
    response_content = fields.Html('Response Content')
    raw_response = fields.Text('Raw Response')
    tokens_used = fields.Integer('Tokens Used', default=0)
    ai_model = fields.Char('AI Model')
    
    # Error handling
    error_message = fields.Text('Error Message')
    
    # Metadata
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    display_name = fields.Char('Display Name', compute='_compute_display_name', store=True)
    
    @api.depends('started_at', 'completed_at')
    def _compute_duration(self):
        for record in self:
            if record.started_at and record.completed_at:
                delta = record.completed_at - record.started_at
                record.duration = delta.total_seconds()
            else:
                record.duration = 0.0
    
    @api.depends('agent_id', 'started_at', 'execution_type')
    def _compute_display_name(self):
        for record in self:
            agent_name = record.agent_id.name if record.agent_id else 'Unknown Agent'
            date_str = record.started_at.strftime('%Y-%m-%d %H:%M') if record.started_at else 'Unknown Date'
            record.display_name = f"{agent_name} - {record.execution_type} - {date_str}"
    
    def view_response_details(self):
        """Open response details in a larger view"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Response Details',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
    
    def retry_execution(self):
        """Retry the agent execution"""
        if self.status not in ['failed', 'completed']:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'warning',
                    'message': _('Can only retry failed or completed executions'),
                }
            }
        
        return self.agent_id.execute_agent()
    
    @api.model
    def cleanup_old_records(self, days_to_keep=30):
        """Cleanup old response history records"""
        cutoff_date = fields.Datetime.now() - relativedelta(days=days_to_keep)
        old_records = self.search([('started_at', '<', cutoff_date)])
        
        count = len(old_records)
        old_records.unlink()
        
        _logger.info("Cleaned up %d old response history records", count)
        return count