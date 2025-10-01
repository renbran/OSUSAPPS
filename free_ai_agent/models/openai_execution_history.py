# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class OpenAIExecutionHistory(models.Model):
    _name = 'openai.execution.history'
    _description = 'OpenAI Business Intelligence Execution History'
    _order = 'id desc'
    _rec_name = 'display_name'

    agent_id = fields.Many2one('openai.business.agent', string='AI Agent', required=True, ondelete='cascade')
    
    # Execution details
    execution_type = fields.Selection([
        ('manual', 'Manual Execution'),
        ('scheduled', 'Scheduled Analysis'),
        ('triggered', 'Event Triggered'),
        ('test', 'Test Run'),
    ], string='Execution Type', required=True)
    
    status = fields.Selection([
        ('draft', 'Draft'),
        ('running', 'Running Analysis'),
        ('completed', 'Analysis Completed'),
        ('failed', 'Analysis Failed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft')
    
    # Timing information
    started_at = fields.Datetime('Started At', required=True, default=fields.Datetime.now)
    completed_at = fields.Datetime('Completed At')
    duration = fields.Float('Duration (seconds)', compute='_compute_duration', store=True)
    
    # AI Response data
    response_content = fields.Html('Intelligence Analysis')
    raw_response = fields.Text('Raw OpenAI Response')
    tokens_used = fields.Integer('Tokens Used', default=0)
    ai_model = fields.Char('AI Model Used')
    estimated_cost = fields.Float('Estimated Cost ($)', compute='_compute_estimated_cost', store=True)
    
    # Analysis metadata
    business_data_summary = fields.Text('Business Data Summary')
    analysis_focus = fields.Char('Analysis Focus')
    urgency_level = fields.Char('Urgency Level')
    
    # Error handling
    error_message = fields.Text('Error Details')
    retry_count = fields.Integer('Retry Count', default=0)
    
    # User information
    user_id = fields.Many2one('res.users', string='Executed By', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    
    # Display name
    display_name = fields.Char('Display Name', compute='_compute_display_name', store=True)
    
    # Quality metrics
    response_quality = fields.Selection([
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('average', 'Average'),
        ('poor', 'Poor'),
    ], string='Response Quality')
    
    user_feedback = fields.Text('User Feedback')
    usefulness_rating = fields.Selection([
        ('5', 'Very Useful'),
        ('4', 'Useful'),
        ('3', 'Somewhat Useful'),
        ('2', 'Not Very Useful'),
        ('1', 'Not Useful'),
    ], string='Usefulness Rating')
    
    @api.depends('started_at', 'completed_at')
    def _compute_duration(self):
        for record in self:
            if record.started_at and record.completed_at:
                delta = record.completed_at - record.started_at
                record.duration = delta.total_seconds()
            else:
                record.duration = 0.0
    
    @api.depends('tokens_used', 'ai_model')
    def _compute_estimated_cost(self):
        # OpenAI pricing (approximate, as of 2024)
        pricing_map = {
            'gpt-4o': 0.000015,  # $15 per 1M tokens
            'gpt-4o-mini': 0.00000015,  # $0.15 per 1M tokens
            'gpt-4-turbo': 0.00001,  # $10 per 1M tokens
            'gpt-4': 0.00003,  # $30 per 1M tokens
            'gpt-3.5-turbo': 0.000002,  # $2 per 1M tokens
        }
        
        for record in self:
            if record.tokens_used and record.ai_model:
                rate = pricing_map.get(record.ai_model, 0.000002)  # Default to GPT-3.5 rate
                record.estimated_cost = record.tokens_used * rate
            else:
                record.estimated_cost = 0.0
    
    @api.depends('agent_id', 'started_at', 'execution_type')
    def _compute_display_name(self):
        for record in self:
            agent_name = record.agent_id.name if record.agent_id else 'Unknown Agent'
            date_str = record.started_at.strftime('%Y-%m-%d %H:%M') if record.started_at else 'Unknown Date'
            record.display_name = f"{agent_name} - {record.execution_type} - {date_str}"
    
    def action_view_full_analysis(self):
        """Open the full analysis in a detailed view"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Intelligence Analysis Results',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': {'dialog_size': 'large'},
        }
    
    def action_retry_analysis(self):
        """Retry the analysis execution"""
        if self.status not in ['failed', 'completed']:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'warning',
                    'message': _('Can only retry failed or completed analyses'),
                }
            }
        
        self.retry_count += 1
        return self.agent_id.execute_intelligence_analysis()
    
    def action_provide_feedback(self):
        """Open feedback form"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Provide Feedback',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'views': [[self.env.ref('free_ai_agent.view_openai_execution_history_feedback_form').id, 'form']],
        }
    
    def action_share_analysis(self):
        """Share analysis with team members"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Share Analysis',
            'res_model': 'mail.compose.message',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_model': self._name,
                'default_res_id': self.id,
                'default_subject': f'AI Analysis: {self.agent_id.name}',
                'default_body': f"""
                    <p>Sharing AI analysis results from {self.agent_id.name}:</p>
                    <blockquote>{self.response_content[:500]}...</blockquote>
                    <p><a href="/web#id={self.id}&model={self._name}&view_type=form">View Full Analysis</a></p>
                """,
            }
        }
    
    @api.model
    def get_execution_statistics(self, days=30):
        """Get execution statistics for dashboard"""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        domain = [('started_at', '>=', cutoff_date)]
        
        executions = self.search(domain)
        
        return {
            'total_executions': len(executions),
            'successful_executions': len(executions.filtered(lambda r: r.status == 'completed')),
            'failed_executions': len(executions.filtered(lambda r: r.status == 'failed')),
            'total_tokens_used': sum(executions.mapped('tokens_used')),
            'total_estimated_cost': sum(executions.mapped('estimated_cost')),
            'average_duration': sum(executions.mapped('duration')) / max(len(executions), 1),
            'most_active_agents': executions.mapped('agent_id').mapped('name')[:5],
        }
    
    @api.model
    def cleanup_old_executions(self, days_to_keep=90):
        """Cleanup old execution history records"""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        old_executions = self.search([('started_at', '<', cutoff_date)])
        
        count = len(old_executions)
        old_executions.unlink()
        
        _logger.info("Cleaned up %d old execution history records", count)
        return count